#!/usr/bin/env python
import tweepy
import sys
import re

def GetCredentials(filename='myCredentials.txt'):
    '''read tokens and secrets from config file'''
    cred_dict = {}
    print('reading from {fn}'.format(fn=filename))
    try:
        with open(filename,'r') as credfile:
            for line in credfile.readlines():
                if len(line) < 2:
                    continue
                words = line.strip().split(' ')
                cred_dict[words[0]] = words[1]
    except IOError:
        print('could not read from file {fn}'.format(fn=filename))
        sys.exit()
    return(cred_dict)




class myStreamer(tweepy.StreamListener):
    ''' StreamListener class. Print statuses to stdout'''
    def __init__(self):
        super(myStreamer, self).__init__()

    def on_status(self, status):
        print('{aname:20s} ({aid}):'.format(aname=status.author.screen_name,aid=status.author.id))
        print(status.text)
        print(
            'geo: {geo}, coord: {coord}, location: {loc}\n' \
            .format(geo=status.geo,coord=status.coordinates,loc=status.user.location)
            )



    def on_error(self,status):
        print(status)





def main():
    cd = GetCredentials()

    # authenticate
    print('authenticating')
    auth = tweepy.OAuthHandler(cd['Consumer_Key'], cd['Consumer_Secret'])
    auth.set_access_token(cd['Access_Token'], cd['Access_Secret'])


    tweeper = tweepy.API(auth)

    # initialise the stream
    print('initialising twitter stream')
    theStreamListener = myStreamer()
    stream = tweepy.Stream(auth = tweeper.auth,listener=theStreamListener)
    # ttc mentions
    # stream.filter(track=['ttc'])
    # everything in Toronto (ish)
    # stream.filter(locations=[43.76,-79.63,43.61,-79.297])
    bboxTO = [43.61,-79.63,43.76,-79.297] # big, Torontoish
    bboxHood = [43.652107, -79.379787, 43.665000, -79.367897] # close to me

    print('streaming')
    stream.filter(locations=bboxTO,track=['ttc'],async=True)


    q = ''
    while not re.match(r'^[qQ]',q):
        q = raw_input('enter "q" to exit > ')
        # print('received input: {q}'.format(q=q))
        stream.disconnect()

    




    

    # raw_input('hit enter to exit:')






    


if __name__ == '__main__':
    main()

