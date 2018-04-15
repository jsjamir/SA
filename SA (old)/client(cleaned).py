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
    "Gets the arguments of the command line statement in dictionary form (p)"
    p = {'id':None, 'temp':[None,None], 'humid':[None,None], 'batt':[None,None]}


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
        p['temp'] = [float(x) for x in args.temp.split(',')]
        if p['temp'][0] >= p['temp'][1]:
            print "ERROR: temperature first argument should be less than second argument"
            quit()

    if args.humid:
        if not template_i.match(args.humid):
            print "ERROR: humidity must be in INT,INT"
            quit()
        p['humid'] = [int(x) for x in args.humid.split(',')]
        if p['humid'][0] >= p['humid'][1]:
            print "ERROR: humidity first argument should be less than second argument"
            quit()
        if p['humid'][0] < 0 or p['humid'][1] > 65535:
            print "ERROR: humidity must be between 0 and 65536"
            quit()

    if args.batt:
        if not template_f.match(args.batt):
            print "ERROR: battery voltage must be in FLOAT,FLOAT"
            quit()
        p['batt'] = [float(x) for x in args.batt.split(',')]
        if p['batt'][0] >= p['batt'][1]:
            print "ERROR: battery first argument should be less than second argument"
            quit()

    return p #{ id:<id>, temp}
def get_random_data(p):
    data = {}
    data['id'] = p['id']
    if p['temp'][0] is not None:
        data['temp'] = uniform(p['temp'][0], p['temp'][1])
    if p['humid'][0] is not None:
        data['humid'] = randrange(p['humid'][0], p['humid'][1]+1)
    if p['batt'][0] is not None:
        data['batt'] = uniform(p['batt'][0], p['batt'][1])
    return data
def sort_data(data, p):
    list_data = [ data['id'] ]
    for i in data:
        if i == 'temp':
            list_data.append(1)
            temp_int = float_to_int16(data['temp'], p['temp'])
            list_data.append(temp_int)
        if i == 'humid':
            list_data.append(2)
            list_data.append(data['humid'])
        if i == 'batt':
            list_data.append(3)
            batt_int = float_to_int16(data['batt'], p['batt'])
            list_data.append(batt_int)

    sorted_data = []
    for i in range(1, len(list_data), 2):
        sorted_data.append(list_data[i+1])

    for i in range(1, len(list_data), 2):
        sorted_data.append(list_data[i])

    sorted_data.append(list_data[0])
    return sorted_data
def get_pack_format(sorted_data):
    length = len(sorted_data)/2
    pack_format = 'H' * length + 'B' * (length+1)
    return pack_format
def encode_data(data, parameters):
    sorted_data = sort_data(data, parameters)
    pack_format = get_pack_format(sorted_data)
    encoded_data = pack(pack_format, *sorted_data)
    return encoded_data
def float_to_int16(data, (minval, maxval)):
    int16 = float((data - minval)) / (maxval-minval)
    int16 = int16 * 2**16
    return int(int16)
def gcl_append_init():
    gdp.gdp_init()
    gcl_input = 'ph.edu.upd.pcari.jasper.data'
    pem_input = '_data.pem'

    gcl_name = gdp.GDP_NAME(gcl_input)
    skey = gdp.EP_CRYPTO_KEY(filename=pem_input,
           keyform=gdp.EP_CRYPTO_KEYFORM_PEM, flags=gdp.EP_CRYPTO_F_SECRET)

    gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA, {"skey":skey})
    return gcl_handle

def main():
    gcl_handle = gcl_append_init()
    parameters = arguments()
    gcl_handle.append({"data": json.dumps(parameters)})
    print "sent: ", json.dumps(parameters)

    while True:
        time.sleep(2)
        data = get_random_data(parameters)
        encoded_data = encode_data(data, parameters)
        gcl_handle.append({"data": encoded_data})
        print "sent: [%s]" % encoded_data
        print "data: [%r]" % encoded_data
        print "data: [%s]" % data
    exit()

if __name__ == "__main__":
    main()
