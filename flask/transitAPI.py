#!/usr/bin/env python3
'''
Flask Rest API
Has a few endpoints for different results
fetch results from db tables
'''

# Adding data to fake sqlite db. 
# on request, pull rows from geoData table, send JSON response

from datetime import datetime, timedelta
from flask import Flask, jsonify, request, Response, json
from flask_restful import Resource, Api
import sqlite3

app = Flask(__name__)
api = Api(app)


## Move this stuff, get rid of globals
## put all this into the geoData object
## define an init
geoDataCache = []
interval = 5

timelast = datetime.utcnow()
dbfile = 'fake.sqlite'

def updateGeoData():
    ''' update the cached data, if needed '''
    global geoDataCache, timelast
    if (not geoDataCache) or ((datetime.utcnow() - timelast).seconds > interval):
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




        # if request contains a callback, wrap the json in the callback function
        # else just return the json
        
    # move updateGeoData function, and cached data into this class.

    # move updateGeoData function, and cached data into this class.


api.add_resource(geoData, '/geoData')

if __name__ == '__main__':
    app.run(debug=True)