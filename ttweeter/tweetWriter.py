#!/usr/bin/env python3
''' Stream twitter data related to toronto transit.
Take data from twitter and create messages which are published to kafka'''

from __future__ import print_function
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
        self.record = None
        self.writeInterval = 4.0
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
    def writeStatusesSQlite(self,theQueue,record):
        '''write statuses to db file'''
        # self.record = True
        print('\x1b[31mWriting Statuses to DB\x1b[0m')
        try:
            with open('statusRecorder.log','w',encoding='utf-8') as thislog:
                thislog.write('\x1b[31mWriting Statuses to DB\x1b[0m\n')
                conn = sqlite3.connect(self._dbfile)
                cur = conn.cursor()
                thislog.write('writeStatuses - recording\n')

                # the tuples in self._statusList are organised in this way
                query = 'INSERT INTO rawTweets (' \
                    'tweet_id_str, ' \
                    'author, ' \
                    'author_id_str, ' \
                    'status, ' \
                    'geo_latt, ' \
                    'geo_long, ' \
                    'datetime_utc) ' \
                    ' VALUES (?,?,?,?,?,?,?)'

                thislog.write('Query: ' + query + '\n')

                while record.value == 1 :
                    if not self.Queue.empty():
                        # write status from deque
                        # statusTuple = self._statusList.popleft()
                        while not self.Queue.empty():
                            statusTuple = self.Queue.get()
                            cur.execute(query,statusTuple)
                            thislog.write('wrote tweet {tid} to DB\n'.format(tid=statusTuple[0]))
                            thislog.write('inserted rows: {rc}\n'.format(rc=cur.rowcount))
                        conn.commit()

                    else:
                        # deque empty, wait a while
                        time.sleep(self.writeInterval)
                        thislog.write('sleeping\n')
                thislog.write('writeStatuses - done writing tweets to DB\n')

                # when we get here, self.record has been set to False
                conn.close()
        except IOError:
            print('Error, could not open statusRecorder.log for writing')

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
        self.Queue.put(tweetinfo)
        # print('put a tweet')

        # self._dbcur.execute(
        #     'INSERT INTO rawTweets('
        #     'tweet_id_str, '
        #     'author, '
        #     'author_id_str, '
        #     'status, '
        #     'geo_latt, '
        #     'geo_long, '
        #     'datetime_utc) '
        #     ' VALUES (?,?,?,?,?,?,?)',
        #     tweetinfo
        #     )
        writeLog('appended tweet {tid} created at {cat} to list'.format(tid=tweet_id_str, cat=datetime_utc))

        if self.printmessage:
            print('\n{aname:20s} :'.format(
                aname=author_name))
            print(status.text)
            # coordinates.coordinates are long,lat
            # geo.coordinates are lat, long

            # if status.coordinates:
                # print('\033[31mcoordinates: \033[0m{lat},{lon}'.format(lat=lat, lon=lon))
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

def GetUserIDs(api, names):
    '''Look up a list of names, get a list of user ids '''
    users = api.lookup_users(screen_names=names)
    ids = [user.id_str for user in users]
    return ids
#############################################################



def setupDB(dbFile, dropRaw=False):
    '''
    set up the database for storing tweet info
    create db if file does not exist
    create table rawTweets if it does not exist
    '''
    writeLog('setting up DB')
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

def getTweets(credFile, DBfile, logfile):
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


    # pass db connection to stream listener
    # theStreamListener.dbcon = conn

    # start streaming
    stream = tweepy.Stream(auth=tweeper.auth, listener=theStreamListener)

    # print('streaming')
    # Async, this is done in a new thread
    # stream.filter(locations=LOCATIONBOX, follow=ids, track=TRACK, async=True)

    # start writing
    # do this in a new thread also
    theQueue = Queue()
    # self.Queue = theQueue
    record = Value('i',1)
    theStreamListener.Queue = theQueue
    P = Process(target=theStreamListener.writeStatusesSQlite,args=(theQueue,record))
    P.start()

    stream.filter(locations=LOCATIONBOX, async=True)

    
    # theStreamListener.writeStatuses()


    # stream until users enters [qQ].*
    q = ''
    while not re.match(r'^[qQ]', q):
        q = input('enter "q" to exit > ')
        # print('received input: {q}'.format(q=q))
        stream.disconnect()
        record.value = -1
        P.join()



# if __name__ == '__main__':
#     main()

