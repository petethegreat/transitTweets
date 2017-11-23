#!/usr/bin/env python
''' Stream twitter data related to toronto transit.
Take data from twitter and create messages which are published to kafka'''

from __future__ import print_function
import sys
import re

import tweepy


# follow tweets from (or mentioning?) these users
FOLLOW = [
    'TTCnotices',
    'TTChelps',
    'bradTTC',
    ]

# a big box containing the torontoish area
# LOCATIONBOX = [
#     -79.63,
#     43.61,
#     -79.297,
#     43.76
#     ]

# Wellington
LOCATIONBOX = [
    174.75,
    -41.356,
    174.95,
    -41.2
    ]
# terms to track
TRACK = ['metlink']
#############################################################

def GetCredentials(filename='myCredentials.txt'):
    '''read tokens and secrets from config file'''
    cred_dict = {}
    print('reading from {fn}'.format(fn=filename))
    try:
        with open(filename, 'r') as credfile:
            for line in credfile.readlines():
                if len(line) < 2:
                    continue
                words = line.strip().split(' ')
                cred_dict[words[0]] = words[1]
    except IOError:
        print('could not read from file {fn}'.format(fn=filename))
        sys.exit()
    return cred_dict
#############################################################

def GetUserIDs(api, names):
    '''Look up a list of names, get a list of user ids '''
    users = api.lookup_users(screen_names=names)
    ids = [user.id_str for user in users]
    return ids
#############################################################

class myStreamer(tweepy.StreamListener):
    ''' StreamListener class for tweepy. Print statuses to stdout'''
    #########################################################

    def __init__(self,printmessage=True):
        super(myStreamer, self).__init__()
        self.printmessage = printmessage
    #########################################################

    def on_status(self, status):
        # kafka stuff

        if self.printmessage:
            print('\n{aname:20s} ({aid}):'.format(
                aname=status.author.screen_name, aid=status.author.id))
            print(status.text)
            # note that coordinates are formatted as [long,lat]
            # coordinates.coordinates are long,lat
            # geo.coordinates are lat long
            coords = None
            if status.coordinates:
                # print(status.coordinates[u'coordinates'])
                lon = status.coordinates[u'coordinates'][0]
                lat = status.coordinates[u'coordinates'][1]
                coords = [lat, lon]
            if coords:
                print('\033[31mcoordinates: \033[0m{lat},{lon}'.format(lat=coords[0], lon=coords[1]))
    #########################################################

    def on_error(self, status):
        ''' print status on error'''
        print(status)
#############################################################

def main():
    ''' main function. Do stuff.'''
    cd = GetCredentials()

    # authenticate
    print('authenticating')
    auth = tweepy.OAuthHandler(cd['Consumer_Key'], cd['Consumer_Secret'])
    auth.set_access_token(cd['Access_Token'], cd['Access_Secret'])

    # handle on tweepy api object
    tweeper = tweepy.API(auth)

    # look up ids
    ids = GetUserIDs(tweeper, FOLLOW)
    print('followed ids:')
    for theid in ids:
        print(theid)

    # initialise the stream
    print('initialising twitter stream')
    theStreamListener = myStreamer()
    stream = tweepy.Stream(auth=tweeper.auth, listener=theStreamListener)

    print('streaming')
    # stream.filter(locations=LOCATIONBOX, follow=ids, track=TRACK, async=True)
    stream.filter(locations=LOCATIONBOX, async=True)



    # stream until users enters [qQ].*
    q = ''
    while not re.match(r'^[qQ]', q):
        q = raw_input('enter "q" to exit > ')
        # print('received input: {q}'.format(q=q))
        stream.disconnect()

if __name__ == '__main__':
    main()

