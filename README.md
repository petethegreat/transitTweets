# transitTweets
stream tweets related to toronto Transit


## Introduction

The aim of this project is to display information related to toronto transit harvested from twitter. The intended workflow is 

    * Use python/tweepy to stream tweets (statuses)
    * Pass the streamed tweets as messages to a kafka topic
    * Have spark consume messages from kafka, and process the data via spark streaming
    * Pass results back to kafka via a different topic
    * Use a Restful Flask microservice to respond with current (realtime-ish) results when queried
    * Visualise results on a web page using D3.js, querying our Flask service to get current data

## Notes

At present, I'm focussing on getting the data from twitter. I have a python script that will stream tweets to stdout. Will expand this so that it instead writes raw tweets to an sqlite3 database. Will use this database as a standin for the spark/kafka machinery for now, then sort that out once other parts are working as intended.
