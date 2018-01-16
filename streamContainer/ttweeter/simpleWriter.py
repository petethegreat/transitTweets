#!/usr/bin/env python3
''' Stream twitter data related to toronto transit.
Take data from twitter and create messages which are published to kafka'''

from __future__ import print_function
import signal
import sys
import re
import datetime
import tweepy
import sqlite3
from collections import deque
import time
from multiprocessing import Process, Queue, Value
# handle to logfile
LOGFILE = None

# follow tweets from (or mentioning?) these users
FOLLOW = [
    'TTCnotices',
    'TTChelps',
    'bradTTC',
    ]

# # a big box containing the torontoish area
LOCATIONBOX = [
    -79.63,
    43.61,
    -79.297,
    43.76
    ]
    
# Wellington
# LOCATIONBOX = [
#     174.75,
#     -41.356,
#     174.95,
#     -41.2
#     ]

# terms to track
TRACK = ['ttc,ridetherocket']



#############################################################

def writeLog(s):
    global LOGFILE
    if LOGFILE:
        LOGFILE.write('{time} {s}\n'.format(time=datetime.datetime.now(), s=s))
    else:
        print('Error, could not write to log')
#############################################################

class myStreamer(tweepy.StreamListener):
    ''' StreamListener class for tweepy. Print statuses to stdout'''
    #########################################################

    def __init__(self, dbFile,printmessage=True):
        super(myStreamer, self).__init__()
        self.printmessage = printmessage
        self._dbcon = None
        # self._dbcur = None
        self._dbfile = dbFile
        self._statusList = None
        self._queryStr = None
        self.record = None
        # self.writeInterval = 4.0
    #########################################################
    # Properties

    ## DB connection
    # @property
    # def dbcon(self):
    #     ''' connection to sqlite database for raw tweet data'''
    #     return self._dbcon
    # @dbcon.setter
    # def dbcon(self, conn):
    #     self._dbcon = conn
    # @dbcon.deleter
    # def dbcon(self):
    #     del self._dbcon
    
    ## DB filename
    @property
    def dbfile(self):
        '''database filename'''
        return self._dbfile

    @dbfile.setter
    def dbfile(self,file):
        self._dbfile = file

    @dbfile.deleter
    def dbfile(self):
        del self._dbfile

    ## StatusLise
    @property
    def statusList(self):
        ''' list of status data to be written to db '''
        return self._statusList
    @statusList.setter
    def statusList(self,slist):
        self._statusList = slist
    @statusList.deleter
    def statusList(self):
        del self._statusList
    #########################################################
    def initialiseConnection(self):
        self._dbcon = sqlite3.connect(self._dbfile)
        self._queryStr = 'INSERT INTO rawTweets (' \
                    'tweet_id_str, ' \
                    'author, ' \
                    'author_id_str, ' \
                    'status, ' \
                    'geo_latt, ' \
                    'geo_long, ' \
                    'datetime_utc) ' \
                    ' VALUES (?,?,?,?,?,?,?)'

    def on_status(self, status):
        ''' carried out when a status is recieved through stream '''
        # get a db cursor, if we don't already have one
        # if not self._dbcur:
        #     self._dbcon  = sqlite3.connect(self._dbfile)
        #     self._dbcur = self.dbcon.cursor()

        # tweet id
        tweet_id_str = status.id_str

        # author info
        author_name = status.author.screen_name
        author_id_str = status.author.id_str

        # datetime (in utc)
        datetime_utc = status.created_at

        # coordinates
        lon = None
        lat = None
        if status.coordinates:
            # print(status.coordinates[u'coordinates'])
            lon = status.coordinates[u'coordinates'][0]
            lat = status.coordinates[u'coordinates'][1]

        # write to db
        # this could hammer the disk.
        # Might be better to store tweets in a list
        # write the list if it exceeds X tweets or Y seconds since last write
        tweetinfo = (tweet_id_str, author_name, author_id_str, status.text, lat, lon, datetime_utc)
        
        curr = self._dbcon.cursor()
        curr.execute(self._queryStr, tweetinfo)
        self._dbcon.commit()

        if self.printmessage:
            print('\n{aname:20s} :'.format(
                aname=author_name))
            print(status.text)

    #########################################################

    def on_error(self, status):
        ''' print status on error'''
        print(status)
    def disconnect(self):
        self._dbcon.disconnect()
        super(myStreamer, self).disconnect()
#############################################################

def GetCredentials(credFile):
    '''read tokens and secrets from config file'''
    cred_dict = {}
    writeLog('reading from {fn}'.format(fn=credFile))
    try:
        with open(credFile, 'r') as cfile:
            for line in cfile.readlines():
                if len(line) < 2:
                    continue
                words = line.strip().split(' ')
                cred_dict[words[0]] = words[1]
    except IOError:
        writeLog('could not read from file {fn}'.format(fn=credFile))
        sys.exit()
    return cred_dict
#############################################################

# def GetUserIDs(api, names):
#     '''Look up a list of names, get a list of user ids '''
#     users = api.lookup_users(screen_names=names)
#     ids = [user.id_str for user in users]
#     return ids
#############################################################



def setupDB(dbFile, dropRaw=False):
    '''
    set up the database for storing tweet info
    create db if file does not exist
    create table rawTweets if it does not exist
    '''
    print('setting up DB')
    conn = sqlite3.connect(dbFile)
    cur = conn.cursor()

    if dropRaw:
        cur.execute('DROP TABLE IF EXISTS rawTweets')

    # check if table exists
    cur.execute("SELECT count(*) from sqlite_master WHERE type = 'table' AND name = 'rawTweets'")
    count = cur.fetchone()[0]
    writeLog('there are {row} tables named rawTweets in the database'.format(row=count))


    if count > 0:
        writeLog('rawtweets exists')
    else:
        writeLog('creating rawtweets table')
        cur.execute(
            'CREATE TABLE rawTweets('
            'id INTEGER PRIMARY KEY, '
            'tweet_id_str TEXT, '
            'author TEXT, '
            'author_id_str TEXT, '
            'status TEXT, '
            'geo_latt REAL, '
            'geo_long REAL, '
            'datetime_utc TEXT'
            ');'
            )

    # close cursor
    cur.close()

#############################################################

def sgetTweets(credFile, DBfile, logfile):
    ''' main function. Do stuff.'''

    # setup log file
    global LOGFILE
    LOGFILE = logfile

    writeLog('writing tweets - \n')

    cd = GetCredentials(credFile)

    # setup db
    # create the table if it does not exist
    setupDB(DBfile)

    # authenticate
    print('authenticating')
    auth = tweepy.OAuthHandler(cd['Consumer_Key'], cd['Consumer_Secret'])
    auth.set_access_token(cd['Access_Token'], cd['Access_Secret'])

    # handle on tweepy api object
    tweeper = tweepy.API(auth)

    # # initialise the stream
    print('initialising twitter stream')
    theStreamListener = myStreamer(DBfile)
    theStreamListener.initialiseConnection()


    # pass db connection to stream listener
    # theStreamListener.dbcon = conn

    # start streaming
    stream = tweepy.Stream(auth=tweeper.auth, listener=theStreamListener)


    # print('streaming')
    # Async, this is done in a new thread
    # stream.filter(locations=LOCATIONBOX, follow=ids, track=TRACK, async=True)

    # start writing
    # do this in a new thread also
    # theQueue = Queue()
    # # self.Queue = theQueue
    # record = Value('i',1)
    # theStreamListener.Queue = theQueue
    # P = Process(target=theStreamListener.writeStatusesSQlite,args=(theQueue,record))
    # P.start()

    stream.filter(locations=LOCATIONBOX, async=False)

    
    # theStreamListener.writeStatuses()


    # stream until interrupt signal received
    # def handler(signal, frame):
    #     print('signal caught, exiting')
    #     stream.disconnect()
    #     # record.value = -1
    #     # P.join(5)



    # signal.signal(signal.SIGINT, handler)
    # print('Press Ctrl+C to exit')
    # signal.pause()


    # q = ''
    # while not re.match(r'^[qQ]', q):
    #     q = input('enter "q" to exit > ')
    #     # print('received input: {q}'.format(q=q))
    #     stream.disconnect()
    #     record.value = -1
    #     P.join()



# if __name__ == '__main__':
#     main()

