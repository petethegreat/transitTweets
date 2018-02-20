# transitTweets
stream tweets related to toronto Transit


## Introduction

The aim of this project is to display information related to toronto transit harvested from twitter. The intended workflow is (well, initially was)

  - Use python/tweepy to stream tweets (statuses)
  - Pass the streamed tweets as messages to a kafka topic
  - Have spark consume messages from kafka, and process the data via spark streaming
  - Pass results back to kafka via a different topic
  - Use a Restful Flask microservice to respond with current (realtime-ish) results when queried
  - Visualise results on a web page using D3.js and leaflet, querying our Flask service to get current data.

Backend is running in a t2.micro on aws. This is a pretty small space for both spark and kafka to be running in addition to tweepy and flask. For now, I'm avoiding the big data tools in favour of a simple sqlite database:
  - python/tweepy to stream twitter statuses
  - write tweets to sqlite db table
  - Flask reads from the db periodically
  - html/javascript hosted on gh-pages requests data from flask, plots it using leaflet/d3


## Status

Things are running. The tweepy and flask components are housed within docker containers. Dockerfiles are in this repo, as well as a script to build the images. Deplyment is via "docker save | gzip > image.tar.gz" locally, followed by scp and then "gunzip -c image.tar.gz | docker load" on aws. A docker volume is used to hold the sqlite db file, so that both containers can access it.

Map works well, want to do a few more things with the data, so I'll be working on that.

## SSL/https
Needed our server to repond to https requests (github pages serve site over https, which requires that our javascript gets over https). Have obtained certificates through letsencrypt, and domains through freenom. https now works accordingly, although as our gh-pages site is now associated with a custom domain (peterthompson.ml), https is no longer enforced.


