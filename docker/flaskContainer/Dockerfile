FROM ubuntu:latest

# either
# start from an nginx image
# install pip, build tools
# have a start script that runs supervisor (or something) for both nginx and uwsgi (uwsgi will run our flask app)

# or
# start from ubuntu:latest and install nginx in addition to other stuff.
# starting from nginx will not run nginx, we will need to start it in addition to uswgi

# https://docs.docker.com/engine/admin/multi-service_container/


#RUN apt-get update -y && apt-get install -y python3-pip python3-dev build-essential supervisor nginx
# just build-essential and nginx for now. This downloads a bunch. look into multi-stage builds, or a common root image, don't need all our images to install python 3.5 independantly.
RUN apt-get update -y && apt-get install -y build-essential nginx


# to start, just get supervisor running, doing a couple of dumb things (test scripts or something)
# make sure logging works as expected, have logs go to /data 

# then get nginx installed and running as one of the processes under supervisor
# make sure that we can see the hello-world webpage when the container is running

# then add flask and uwsgi/flask
# will need to have nginx, uwsgi and supervisor conf files 


## copy flask files 
COPY flask/ flaskdir/flask
COPY requirements.txt flaskdir/

## move to flask app working directory
WORKDIR /flaskdir

## install required python modules
# RUN pip install -r requirements.txt

RUN which nginx

EXPOSE 80

#CMD service nginx start

CMD nginx -g "daemon off;"
# run nginx in foreground

# this works, so our nginx setup is good.
# look into multistage builds, get python and build essential on top of base ubuntu
# this image should be nginx + flask + uswgi + supervisor





