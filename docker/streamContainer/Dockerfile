FROM ubuntu:latest

# apt-get install python3, pip3
# pip3 install requirements.txt

# build with docker build -t containername:latest
# add a volume for data, put the sqlite file there, and the twitter credentials


RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential

COPY TransitTweeter.py appDir/
COPY ttweeter/ appDir/ttweeter/
COPY requirements.txt appDir/

WORKDIR /appDir




RUN pip3 install -r requirements.txt

RUN mkdir /logfiles

# run the app

#CMD  ls -alh
CMD ./TransitTweeter.py --credFile /data/myCredentials.txt --sqlitedb /data/rawTweets.db --writerLog /logfiles/writer.log 


# need to run the app with the volume mounted
# docker run --name tweetwriterTest --mount source=test,target=/data imagename


# add a docker volume
# pass logfile and dbfile locations (on docker volume) to the run command

# docker build -t twtest .
# docker run -d --name twtestcontainer --mount source=test,target=/data twtest:latest
