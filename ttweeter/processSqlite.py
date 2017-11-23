'''
Process raw tweets from sqlite db
'''
import sqlite3
import pandas as pd
import sys

class tweetProcessor(object):
    def __init__(self,rawTweetFile='tweetdb.sqlite'):
        self._rawTweetFile = rawTweetFile

        
    def processRawTweets(self):
        ''' 
        read tweets from sqlite3
        '''
        try:
            conn = sqlite3.connect(self._rawTweetFile)
        except Exception:
            print('Error, could not connect to {fn}'.format(self._rawTweetFile))
            sys.exit()
        # cur = conn.cursor()
        self.df = pd.read_sql('SELECT * from rawTweets;',conn)
        print(self.df.head())

        first, check that status contains ttc

        from these, get lat and lon, and compute age, store this in a df or dict or something

        get list of routes, look for names or for route numbers XX or 5XX

        
















