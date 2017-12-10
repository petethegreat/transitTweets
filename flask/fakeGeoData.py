#!/usr/bin/env python3
''' 
populate test db with some geo data
add a new (random) point every few seconds
'''
from __future__ import print_function

import argparse
import sys
from datetime import datetime, timedelta
import sqlite3
import random

tweet_id_str = '939887719920160768'
class dataFaker(object):
    def __init__(self,dbFile):
        self.dbFile = dbFile
        self.updateInterval = 7
        self.lats = [43.656839,43.665152]
        self.lons = [-79.411510,-79.356219]
        self.cur = None
        self.conn = None


    def setup(self):
        ''' set up the fake data tables '''
        self.cur.execute('DROP TABLE IF EXISTS geoData')

        self.cur.execute(
                'CREATE TABLE geoData('
                'id INTEGER PRIMARY KEY, '
                'geo_latt REAL, '
                'geo_long REAL, '
                'datetime_utc TEXT,'
                'tweet_id_str TEXT'
                ');'
                )
    def update(self):
        ''' insert some random (Toronto) lat/lon values into table '''
        lat = random.uniform(self.lats[0],self.lats[1])
        lon = random.uniform(self.lons[0],self.lons[1])
        timenow = datetime.utcnow()

        self.cur.execute('INSERT INTO geoData(geo_latt,geo_long,datetime_utc,tweet_id_str) VALUES(?,?,?,?);',(lat,lon, timenow,tweet_id_str))
        self.conn.commit()
        # cur.commit()
        print('added point ({lat},{lon}), {tn}'.format(lat=lat,lon=lon,tn=timenow))


    def DoStuff(self):

        self.conn = sqlite3.connect(self.dbFile)
        self.cur = self.conn.cursor()

        self.setup()
        self.update()

        timelast = datetime.now()
        while True:
            timeSinceUpdate = datetime.now() - timelast
            if timeSinceUpdate.seconds > self.updateInterval:
                self.update()
                timelast = datetime.now()

def GenerateResults(dbFile):
    faker = dataFaker(dbFile)
    faker.DoStuff()


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
   
    parser.add_argument(
        '--fakeDB',
        default='fake.sqlite',
        help='sqlite3 database containing fake processed data')
    args = parser.parse_args()
    dbFile = args.fakeDB
    GenerateResults(dbFile)

