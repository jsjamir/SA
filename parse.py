# -*- coding: utf-8 -*-
from struct import *

def send_messages(message):
    message = message.split(',')
    encoded_data = message[0]
    time = message[1]
    message = message[3:]

    for i in range(0, len(message), 2):
        data = time + encoded_data[-1] + encoded_data[i:i+2]
        if message[i] == '1':
            print "print to temp: [%r]" % data
        if message[i] == '2':
            print "print to humid: [%r]" % data
        if message[i] == '3':
            print "print to batt: [%r]" % data
    return data
