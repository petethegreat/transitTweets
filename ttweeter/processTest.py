#!/usr/bin/env python3
'''
Run all the pieces
'''
from multiprocessing import Process, Queue
from random import randint
import time

counts = 10

def dostuff1(queue):
    count=0
    while count < counts:
        if not queue.empty():
            moose = queue.get()
            print('dostuff1: moose = {m}'.format(m=moose))
            count += 1
        else:
            print('dostuff1 - queue empty')
            time.sleep(3)


def dostuff2(queue):
    count=0
    while count < counts:
            theint = randint(0,10)
            queue.put(theint)
            print('dostuff2: theint = {m}'.format(m=theint))
            count += 1
            time.sleep(2)
            
   


def doAllTheThings():
    q = Queue()
    P = Process(target=dostuff1,args=(q,))
    R = Process(target=dostuff2,args=(q,))

    P.start()
    R.start()
    P.join()
    R.join()

    print('all done')


if __name__ == '__main__':
    doAllTheThings()
