# transitTweets
stream tweets related to toronto Transit


## Introduction

The aim of this project is to display information related to toronto transit harvested from twitter. The intended workflow is 

  - Use python/tweepy to stream tweets (statuses)
  - Pass the streamed tweets as messages to a kafka topic
  - Have spark consume messages from kafka, and process the data via spark streaming
  - Pass results back to kafka via a different topic
  - Use a Restful Flask microservice to respond with current (realtime-ish) results when queried
  - Visualise results on a web page using D3.js and leaflet, querying our Flask service to get current data.

## Status

- Tweepy works. Can stream tweets from twitter and store them in an sqlite database.
- Flask works. Can set up a flask webapp (using flask's debug webserver) that will retrieve/cache data from sqlite and return it as geoJson when requested.
- Javascript works. Can plot lat/long info using d3.js. Plot transitions with new data. Also have a leaflet map that places a marker for each tweet.

Right now, there are a few different pieces that all seem to work. Focus now is to get all the pieces working together nicely under Docker, and then install it on AWS. Have created a docker branch to do this. 


## Kafka
Ran into some out-of-memory errors when trying to work with Kafka on the raspberry pi. Will come back to this. At present want to get something running. Will use an sqlite database to store tweets and processed data for now. This isn't scalable and won't teach me anything about kafka, but should be sufficient to get a map that displays twitter data in realtime(ish). Javascript/d3.js/Docker are all fairly new to me, and I'd like to get something up and running in the near future. Will aim to get the map up and running, with the html hosted on github pages and the tweepy/python/flask backend on AWS. Once this is working, I'll tackle kafka, and do some more advanced processing/machine learning in spark.



