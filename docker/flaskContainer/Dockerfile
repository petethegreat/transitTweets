FROM ubuntu:latest

# start from ubuntu:latest and install nginx in addition to other stuff.
# starting from nginx will not run nginx, we will need to start it in addition to uswgi using supervisor

# https://docs.docker.com/engine/admin/multi-service_container/

# to start, just get supervisor running, doing a couple of dumb things (test scripts or something)
# make sure logging works as expected, have logs go to /data 

# then get nginx installed and running as one of the processes under supervisor
# make sure that we can see the hello-world webpage when the container is running

# then add flask and uwsgi/flask
# will need to have nginx, uwsgi and supervisor conf files 

# python stuff, and nginx

########################
### apt-get packages ### 
########################
# install python framework, as well as supervisor and nginx

RUN apt-get update -y && apt-get install -y python3-pip python3-dev build-essential nginx supervisor

################
### logfiles ###
################
# create a directory for logfiles. This will keep logs container specific
# our supervisord config redirects stdout and stderr to this location

RUN mkdir /logfiles

###################
#### Supervisor ###
###################
# install our config file as the default
# this config tells supervisor to run nginx (daemon off)

COPY supervisor.conf /etc/supervisor/supervisord.conf

#############
### nginx ###
#############
# RUN which nginx

# expose the port to allow incoming traffic
EXPOSE 80

# create directory to hold the socket
RUN mkdir /nginx_uwsgi_socket

# nothing else needs to be done here as yet.
# we can replace/install our own nginx config file once we have uwsgi sorted

####################
### Flask webapp ###
####################
# copy flask files, and nginx_config

COPY flask/ flaskdir/flask
COPY requirements.txt flaskdir/
COPY fc_nginx.conf flaskdir/

## move to flask app working directory
WORKDIR /flaskdir

## install required python modules 
RUN pip3 install -r requirements.txt

#########################
### Start supervisord ###
#########################
# run supervisor, which will run nginx
# this should use the config file copied to /etc/supervisor/supervisord.conf
# specify this explicitly (security/good practice)
# which should run supervisor in the foreground and start nginx

CMD supervisord -c /etc/supervisor/supervisord.conf

#################
### old stuff ###
#################


#CMD nginx -g "daemon off;"

# run nginx in foreground

# this works, so our nginx setup is good.
# look into multistage builds, get python and build essential on top of base ubuntu
# this image should be nginx + flask + uswgi + supervisor





