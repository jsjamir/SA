import argparse
import re
import numpy as np
import binascii
import sys
import socket
import time
import json
import gdp
from random import *
from struct import *

def arguments():
    argument_debug = 0;
    p = {'id':None, 1:[None,None], 2:[None,None], 3:[None,None]}

    "Gets the arguments of the command line statement"
    template_f = re.compile(r'^(\d+(\.\d+)?)(,\d+(\.\d+)?)$') #used for float parsing must must be two comma-separated float values
    template_i = re.compile(r'^(\d+,\d+)$') #used for int parsing must be two comma-separated float values
    parser = argparse.ArgumentParser()
    parser.add_argument("sensor_id", type=int, help="8 bit unique sensor id (0-255)")
    parser.add_argument("-t", "--temp", help="temperature in float. use format -t min,max.")
    parser.add_argument("-u", "--humid", help="temperature in float. use format -t min,max.")
    parser.add_argument("-b", "--batt", help="battery voltage in float. use format -b min,max.")
    args = parser.parse_args()

    p['id'] = args.sensor_id

    if not 0 <= p['id'] <= 255:
        print "ERROR: sensor_id must be INT between 0 and 255"
        quit()

    if args.temp:
        if not template_f.match(args.temp):
            print "ERROR: temperature must be in FLOAT,FLOAT"
            quit()
        p[1] = [float(x) for x in args.temp.split(',')]
        if p[1][0] >= p[1][1]:
            print "ERROR: temperature first argument should be less than second argument"
            quit()

    if args.humid:
        if not template_i.match(args.humid):
            print "ERROR: humidity must be in INT,INT"
            quit()
        p[2] = [int(x) for x in args.humid.split(',')]
        if p[2][0] >= p[2][1]:
            print "ERROR: humidity first argument should be less than second argument"
            quit()
        if p[2][0] < 0 or p[2][1] > 65535:
            print "ERROR: humidity must be between 0 and 65536"
            quit()

    if args.batt:
        if not template_f.match(args.batt):
            print "ERROR: battery voltage must be in FLOAT,FLOAT"
            quit()
        p[3] = [float(x) for x in args.batt.split(',')]
        if p[3][0] >= p[3][1]:
            print "ERROR: battery first argument should be less than second argument"
            quit()

    return p

parameters = arguments()
print "parameters", parameters
