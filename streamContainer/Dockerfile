FROM ubuntu:latest

# apt-get install python3, pip3
# pip3 install requirements.txt

# build with docker build -t containername:latest
# add a volume for data, put the sqlite file there, and the twitter credentials


RUN apt-get update -y
RUN apt-get install -y python3-pip python3-dev build-essential
COPY TransitTweeter.py .
COPY ttweeter .


