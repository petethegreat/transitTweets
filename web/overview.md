# Toronto Tweets

## Introduction
This started as a small project to do something involving twitter data with visualisation in D3.js (intent was to detect ttc delays/anomolies from twitter data). Data is streamed using Tweepy, a python module for interacting with the twitter api, and stored in a small sqlite database. A flask microservice retrieves data from the db, and sends it as a json response when an http request is received. The frontend consists of some html and javascript hosted on github pages, which, at present, uses leaflet to plot recent tweets on a map. The backend (tweepy and flask) are wrapped in docker containers running on an AWS t2 micro instance. Initially I had intended to use spark/kafka to handle data streaming and processing, but this a) seems like overkill for the small amount of data manipulation needed, and b) may take up too many resources on a t2 micro.

All the code for the frontend and backend, as well as dockerfiles (and a build script) for the docker images are contained in [github](https://github.com/petethegreat/transitTweets)


## Frontend

The html/javascript used on the frontend is contained in the repository's web directory, and is hosted on [github pages](http://www.peterthompson.ml/transitTweets/web/TorontoTweets.html). A map of Toronto is drawn using leaflet. 

