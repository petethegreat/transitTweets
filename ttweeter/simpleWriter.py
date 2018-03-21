#!/usr/bin/env python3
''' Stream twitter data related to toronto transit.
Take data from twitter and create messages which are published to kafka'''

from __future__ import print_function
import sys
import re
import datetime
import tweepy
import sqlite3
import time

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
    -79.544,
    43.567,
    -79.197,
    43.898
    ]

# LOCATIONBOX = [
#     -79.63,
#     43.61,
#     -79.297,
#     43.76
#     ]
    
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
        ''' initialise object'''
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

    # DB connection
    @property
    def dbcon(self):
        ''' connection to sqlite database for raw tweet data'''
        return self._dbcon
    @dbcon.setter
    def dbcon(self, conn):
        self._dbcon = conn
    @dbcon.deleter
    def dbcon(self):
        del self._dbcon

    ## DB filename
    @property
    def dbfile(self):
        '''database filename'''
        return self._dbfile

    @dbfile.setter
    def dbfile(self, file):
        self._dbfile = file

    @dbfile.deleter
    def dbfile(self):
        del self._dbfile
    #########################################################

    def initialiseConnection(self):
        ''' set up a db connection, store an insert query'''
        self.dbcon = sqlite3.connect(self._dbfile)
        self._queryStr = 'INSERT INTO rawTweets (' \
                    'tweet_id_str, ' \
                    'author, ' \
                    'author_id_str, ' \
                    'status, ' \
                    'geo_latt, ' \
                    'geo_long, ' \
                    'datetime_utc) ' \
                    ' VALUES (?,?,?,?,?,?,?)'
    #########################################################

    def closeConnection(self):
        ''' close the database connection'''
        self.dbcon.commit()
        self.dbcon.close()
    #########################################################

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
        else:
            return
        # check that tweet is actually within our location box
        # (getting some stuff from new york state)

        if lat < LOCATIONBOX[1] or lon > LOCATIONBOX[2]:
            return
        



        text = status.text

        if hasattr(status,'extended_tweet'):
            text = status.extended_tweet['full_text']



        # write to db
        # this could hammer the disk.
        # Might be better to store tweets in a list
        # write the list if it exceeds X tweets or Y seconds since last write
        tweetinfo = (tweet_id_str, author_name, author_id_str, text, lat, lon, datetime_utc)
        
        #quick/dumb check for relevance
        # isttc = text.find('ttc')
        # if isttc >= 0:
            
        curr = self.dbcon.cursor()
        curr.execute(self._queryStr, tweetinfo)
        self.dbcon.commit()
        writeLog('stored tweet {s}'.format(s=tweet_id_str))

        if self.printmessage:
            print('\n{aname:20s} :'.format(
                aname=author_name))
            print(text)

    #########################################################

    def on_error(self, status_code):
        ''' print status on error'''
        writeLog('Error retrieving status, disconnecting {s}'.format(s=status_code))
        self.dbcon.commit()
        self.dbcon.close()

        # returning false will disconnect (and exit)
        return False

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
    theStreamListener = myStreamer(DBfile,printmessage=False)
    theStreamListener.initialiseConnection()


    # pass db connection to stream listener
    # theStreamListener.dbcon = conn

    # start streaming
    stream = tweepy.Stream(auth=tweeper.auth, listener=theStreamListener)
    stream.filter(locations=LOCATIONBOX, async=False)

    # try: 
    #     stream.filter(locations=LOCATIONBOX, async=False)
    # # exit gracefully
    # except Exception as e:
    #     writeLog('exception: {e}\n'.format(e=e))
    #     writeLog('closing db\n')
    #     theStreamListener.closeConnection()
    #     stream.disconnect()




    # print('closing db connection')
    # theStreamListener.closeConnection()
