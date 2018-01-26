#!/usr/bin/env python3
'''
Flask Rest API
Has a few endpoints for different results
fetch results from db tables
'''

# Adding data to fake sqlite db. 
# on request, pull rows from geoData table, send JSON response

from geojson import Feature, Point, FeatureCollection
import geojson

from datetime import datetime, timedelta
from flask import Flask, jsonify, request, Response, json
from flask_restful import Resource, Api
import sqlite3
import uwsgi

app = Flask(__name__)
api = Api(app)


## Move this stuff, get rid of globals
## put all this into the geoData object
## define an init
geoDataCache = None
interval = 5


timelast = datetime.utcnow()

dbfile = 'fake.sqlite'



def updateGeoData():
    ''' update the cached data, if needed '''
    global geoDataCache, timelast, geoJsonCache
    if (
            (not geoDataCache) or
            ((datetime.utcnow() - timelast).seconds > interval)
        ):
        timelast = datetime.utcnow()
        conn = sqlite3.connect(dbfile)
        cur = conn.cursor()
        cur.execute('select * from geoData;')
        colnames = [col[0] for col in cur.description ]
        geoDataCache = [ dict(zip(colnames,row)) for row in cur]
        # geoDataCache = list(cur.fetchall())
        conn.close()
        print('updating cached geoData')



class geoData(Resource):
    ''' class for handling geoData requests '''
    def get(self):
        ''' on get request '''
        updateGeoData()
        data = json.dumps(geoDataCache)
        callback = request.args.get('callback',False)
        mtype = 'application/json'
        resp = data
        if callback:
            # resp = u'{cb}({json})'.format(cb=str(callback),json=data.data)
            resp = str(callback) + '(' + data + ')'
            mtype = 'application/javascript'
            
            # return data
        return  Response(resp,mimetype=mtype)




class geojsonData(Resource):
    ''' return data in a geoJson format'''
    def __init__(self):
        self.timelast = datetime.utcnow()
        self.interval = 5.0
        self.geoJsonCache = None
        self.dbfile = 'fake.sqlite'

    def updateGeoJsonCache(self):
        ''' update cached geoJson data '''
        if (
                (not self.geoJsonCache) or
                ((datetime.utcnow() - self.timelast).seconds > self.interval)
        ):
            conn = sqlite3.connect(self.dbfile)
            cur = conn.cursor()
            # fake "GeoData" table used for testing
            # cur.execute(
            #     "select * from geoData where "
            #     "datetime(datetime_utc,'utc') > datetime('now','utc','-1 day');")

            # same info from rawTweets
            # only select records where latt and long are not null
            cur.execute(
                "SELECT id, geo_latt, geo_long, datetime_utc, tweet_id_str FROM geoData WHERE "
                "datetime(datetime_utc,'utc') > datetime('now','utc','-1 day') "
                "AND geo_latt IS NOT NULL AND geo_long IS NOT NULL;")


            colnames = [col[0] for col in cur.description]
            # create a featurecollection, one (point) feature from each row
            # additional info is included in properties metadata
            self.geoJsonCache = FeatureCollection([
                Feature(
                    geometry=Point((row[2], row[1])),
                    properties={
                        'id':row[0],
                        'datetime_utc':row[3],
                        'tweet_id_str':row[4]}
                    )
                for row in cur])
            # for row in cur:
            #     print('lat: {lat}, lon: {lon}'.format(lat=row[1],lon=row[2]))
            #     print(Point((row[1],row[2])))
            conn.close()
            print('updating cached geoData')

    def get(self):
        self.updateGeoJsonCache()
        data = geojson.dumps(self.geoJsonCache)
        callback = request.args.get('callback',False)
        mtype = 'application/json'
        resp = data
        if callback:
            # resp = u'{cb}({json})'.format(cb=str(callback),json=data.data)
            resp = str(callback) + '(' + data + ')'
            mtype = 'application/javascript'
            
            # return data
        return  Response(resp,mimetype=mtype)


        # if request contains a callback, wrap the json in the callback function
        # else just return the json
        
    # move updateGeoData function, and cached data into this class.

    # move updateGeoData function, and cached data into this class.


# api.add_resource(geoData, '/geoData')
api.add_resource(geojsonData,'/geojsonData')

if __name__ == '__main__':
    app.run(debug=True)
else:
    # if we're running through uwsgi, then get the dbfile from there
    # dbfile is a placeholder set in uwsgi config (.ini)
    if 'dbfile' in uwsgi.opts:
        dbfile = uwsgi.opts['dbfile']
