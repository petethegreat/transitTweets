#!/usr/bin/env python3
'''
Run all the pieces
'''

from __future__ import print_function

import argparse
import ttweeter
import sys
import codecs

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--credFile',
        default='myCredentials.txt',
        help='text file containing twitter credentials')
    parser.add_argument(
        '--sqlitedb',
        default='tweetdb.sqlite',
        help='sqlite3 database containing twitter data')
    parser.add_argument(
        '--writerLog',
        default='writer.log',
        help='logfile for tweet writer')

    args = parser.parse_args()
    credFile = args.credFile
    DBfile = args.sqlitedb
    # print('reading credentials from {cf}'.format(cf=credFile))
    # print('writing tweet data to {dbf}'.format(dbf=DBfile))

    try:
        with codecs.open(args.writerLog,'w',encoding='utf8') as writerLog:
            print('opening {wl} for tweetWriter logging\n'.format(wl=args.writerLog))
            ttweeter.writeTweets(credFile,DBfile,writerLog)
    except IOError: 
        print('Error: could not open {wf} for writing\n')
        sys.exit()
    print('done writing tweets, exiting')









