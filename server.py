import socket
import struct
import numpy as np
import json
import gdp

from time import sleep, ctime
import time
import threading, os, sys
from struct import *

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789

def initialize_socket():
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSock.bind((UDP_IP_ADDRESS, UDP_PORT_NO))
    return serverSock
def new_writerthread_withpipe(sensor_id ):
    new_r, new_w = os.pipe() #create new new_pipe
    new_w = os.fdopen(new_w,'w',0) #make file object
    new_thread = threading.Thread(
    target = writer, args=(sensor_id, new_r)) #create new thread
    new_thread.setDaemon(True)
    new_thread.start()
    return new_w
def writer(sensor_id, readpipe):
    time.sleep(0.5)
    print "Sensor_id:", sensor_id, "created."
    r = os.fdopen(readpipe,'r',0)
    while True:
        message = r.readline().rstrip('\n')
        message = message.split(',')
        encoded_data = message[0]
        epoch = message[1]
        message = message[3:]
        for i in range(0, len(message), 2):
            data = epoch + encoded_data[-1] + encoded_data[i:i+2]
            if message[i] == '1':
                print "%d >>> temp: [%r] == %s" % ( int(sensor_id), data, message[i+1] )
            if message[i] == '2':
                print "%d >>> humid: [%r] == %s" % ( int(sensor_id), data, message[i+1] )
            if message[i] == '3':
                print "%d >>> batt: [%r] == %s" % ( int(sensor_id), data, message[i+1] )
    print "Sensor_id:", sensor_id, "exited."
def file_write(filename, message):
    f = open(filename, 'a')
    f.write(message)
    f.write('\n')
    f.close()
def get_pack_format(length):
    length = (length-1)/3
    pack_format = 'H' * length + 'B' * (length+1)
    return pack_format
def unsort_data(sorted_data):
    unsorted_data = [sorted_data[-1]]
    offset = len(sorted_data)/2
    for i in range(offset):
        unsorted_data.append(sorted_data[offset+i])
        unsorted_data.append(sorted_data[i])
    return unsorted_data
def int16_to_float(data, (minval, maxval)):
    data = float(data) / 2**16 * (maxval-minval) + minval
    return data
def int16_to_float_list(sorted_data, boundaries):
    offset = len(sorted_data)/2
    for i in range(offset):
        if sorted_data[i + offset] != 2:
            sorted_data[i] = int16_to_float(
            sorted_data[i], boundaries[sorted_data[i+offset]] )
    return sorted_data
def decode_data(packed_data, boundaries):
    pack_format = get_pack_format(len(packed_data))
    unpacked_data = list(unpack(pack_format, packed_data))
    received_data = int16_to_float_list(unpacked_data, boundaries)
    unsorted_data = unsort_data(received_data)
    return unsorted_data
def get_boundaries(parameters):
    boundaries = {}
    for i in range(1, len(parameters), 2):
        boundaries[parameters[i]] = parameters[i+1]
    return boundaries
def csvdata(data):
    message = ""
    for i in data[1:]:
        message = message + str(i) + ','
    return message.rstrip(',')
def write_config(filename):
    r = open(filename, 'r')
    gcl_input = r.readline().rstrip('\n')
    pem_input = r.readline().rstrip('\n')
    r.close
    return gcl_input, pem_input
def gcl_subscription_init():
    gdp.gdp_init()
    gcl_input = "ph.edu.upd.pcari.jasper.data"
    print "gcl: [%r]" % gcl_input
    gcl_name = gdp.GDP_NAME(gcl_input)
    gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RO)
    return gcl_handle

def main():
    #initialize gcl
    gcl_handle = gcl_subscription_init()
    gcl_handle.subscribe(0, 0, None)
    sensor_id_boundaries = {}
    sensor_id_writepipe = {}
    sensor_ids = [] #sensor_id:write_pipe dictionary
    while True:
        event = gcl_handle.get_next_event(None)
        time = event['datum']['ts']['tv_sec']
        time = pack('Q', time)
        data = event['datum']['data']

        if len(data) > 20: #it is a first time sensor
            parameters = json.loads(data)
            boundaries = get_boundaries(parameters)
            sensor_id = parameters[0]
            sensor_ids.append(int(sensor_id))
            if sensor_id in sensor_id_boundaries:
                pass
            else:
                print "New Sensor! ID:", sensor_id
                sensor_id_boundaries[sensor_id] = boundaries
                sensor_id_writepipe[sensor_id] = new_writerthread_withpipe(str(sensor_id))
            print sensor_id_boundaries
            print sensor_ids
        else:
            unpack_format = len(data) * 'B'
            parse_id = unpack(unpack_format, data)
            sensor_id = parse_id[-1]
            if sensor_id in sensor_ids:
                message = decode_data(data, sensor_id_boundaries[sensor_id])
                message = csvdata(message)
                message = data + ',' + time + ',' + str(sensor_id) + ',' + message
                print >>sensor_id_writepipe[sensor_id], message




if __name__ == '__main__':
    main()
