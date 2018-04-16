import socket
import struct
import numpy as np
import json
import gdp
import time
import threading, os, sys
import re
from threading import Thread
from struct import *
from copy import deepcopy
from Queue import Queue
from time import sleep, ctime

UDP_IP_ADDRESS = "127.0.0.1"
UDP_PORT_NO = 6789

def control_center(q):
  #q.put("stop 123 1")
  #sleep(2)
  #q.put("start 123 1")
  while True:
    template = re.compile(r'^(status clients|status sensors( +\d+)?|stop \d+( +\d+)?|start \d+( +\d+)?)$')
    command = raw_input().rstrip('\n')
    if not template.match(command):
        print 'invalid command!'
    else:
        q.put(command)
def control_center_init():
    q = Queue(maxsize=0)
    control = Thread(target=control_center, args=(q,))
    control.setDaemon(True)
    control.start()
    return q
def do_commands(q):
    while not q.empty():
        command = q.get()
        #print "[%r]" % command
        command = command.split(' ')
        command_ = command[0] + ' ' + command[1]
        if command_ == 'status clients':
            print "********************"
            print "***Status Clients***"
            print "********************"
            for i in sensor_id_status:
                print "client_id: %3d | timestamp: %d" % (i, sensor_id_status[i]['timestamp'])

        if command_ == 'status sensors':
            if len(command) == 2:
                print "************************"
                print "***Status Sensors All***"
                print "************************"
                for i in sensor_id_status:
                    print "client_id:", i
                    if 1 in sensor_id_status[i]:
                        print "   temp ON"
                    else:
                        print "   temp OFF"
                    if 2 in sensor_id_status[i]:
                        print "   humid ON"
                    else:
                        print "   humid OFF"
                    if 3 in sensor_id_status[i]:
                        print "   batt ON"
                    else:
                        print "   batt OFF"
                    print "********************"
            else:
                    print "************************"
                    print "***Status Sensors One***"
                    print "************************"
                    i = int(command[2])
                    if i in sensor_ids:
                        print "client_id:", int(command[2])
                        if 1 in sensor_id_status[i]:
                            print "   temp ON"
                        else:
                            print "   temp OFF"
                        if 2 in sensor_id_status[i]:
                            print "   humid ON"
                        else:
                            print "   humid OFF"
                        if 3 in sensor_id_status[i]:
                            print "   batt ON"
                        else:
                            print "   batt OFF"
                        print "********************"

        if command[0] == 'start':
            if int(command[1]) in sensor_ids:
                if len(command) == 2:
                    print "************************"
                    print "***Start Sensors All****"
                    print "************************"
                    for i in range(1,4):
                        text = command[0] + ' ' + command[1] + ' ' + str(i)
                        q.put(text)
                else:
                    print "************************"
                    print "***Start Sensors One***"
                    print "************************"
                    print "client_id:", int(command[1])
                    if int(command[2]) in sensor_id_boundaries[int(command[1])]:
                        sensor_id_status[ int(command[1])][int(command[2]) ] =  sensor_id_boundaries[ int(command[1]) ][ int(command[2]) ]
                    #print sensor_id_status[int(command[1])]
            else:
                print "Invalid client ID!"

        if command[0] == 'stop':
            if int(command[1]) in sensor_ids:
                if len(command) == 2:
                    print "************************"
                    print "***Stop Sensors All****"
                    print "************************"
                    for i in range(1,4):
                        if i in sensor_id_status[int(command[1])]:
                            text = command[0] + ' ' + command[1] + ' ' + str(i)
                            q.put(text)
                        #print text
                    #print "client_id:", int(command[1])
                    #for i in sensor_id_status[int(command[1])].keys():
                    #    if i is not 'timestamp':
                    #        del sensor_id_status[int(command[1])][i]
                else:
                    print "************************"
                    print "***Stop Sensors One***"
                    print "************************"
                    print "client_id:", int(command[1])
                    if int(command[2]) in sensor_id_status[int(command[1])]:
                        del sensor_id_status[int(command[1])][int(command[2])]
            else:
                print "Invalid client ID!"
        q.task_done()
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
    gcl_handle_temp = gcl_append_init('ph.edu.upd.pcari.jasper.temp', '_temp.pem')
    gcl_handle_humid = gcl_append_init('ph.edu.upd.pcari.jasper.humid', '_humid.pem')
    gcl_handle_batt = gcl_append_init('ph.edu.upd.pcari.jasper.batt', '_batt.pem')
    time.sleep(0.5)
    print "Sensor_id:", sensor_id, "created."
    r = os.fdopen(readpipe,'r',0)
    while True:
        time.sleep(0.3)
        message = r.readline().rstrip('\n')
        if  message == 'kill':
            break;
        if len(message) >= 4:
            message = message.split(',')
            encoded_data = message[0]
            epoch = message[1]
            message = message[3:]
            for i in range(0, len(message), 2):
                data = epoch + encoded_data[-1] + encoded_data[i:i+2]
                if message[i] == '1':
                    gcl_handle_temp.append({"data": data})
                    print "%d >>> temp: [%s] == %s" % ( int(sensor_id), data, message[i+1] )
                if message[i] == '2':
                    gcl_handle_humid.append({"data": data})
                    print "%d >>> humid: [%s] == %s" % ( int(sensor_id), data, message[i+1] )
                if message[i] == '3':
                    gcl_handle_batt.append({"data": data})
                    print "%d >>> batt: [%s] == %s" % ( int(sensor_id), data, message[i+1] )
    print "Sensor_id:", sensor_id, "exited."
    while True:
        pass
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
def gcl_append_init(gcl_input, pem_input):
    gdp.gdp_init()
    gcl_name = gdp.GDP_NAME(gcl_input)
    skey = gdp.EP_CRYPTO_KEY(filename=pem_input,
           keyform=gdp.EP_CRYPTO_KEYFORM_PEM, flags=gdp.EP_CRYPTO_F_SECRET)

    gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA, {"skey":skey})
    return gcl_handle


def main():
    #initialize gcl
    gcl_handle = gcl_subscription_init()
    q = control_center_init()
    gcl_handle.subscribe(0, 0, None)
    sensor_id_boundaries = {}
    sensor_id_writepipe = {}
    sensor_id_status = {}
    sensor_ids = [] #sensor_id:write_pipe dictionary
    while True:
        do_commands(q)
        event = gcl_handle.get_next_event(None)
        time_ = event['datum']['ts']['tv_sec']
        time = pack('Q', time_)
        data = event['datum']['data']

        if len(data) > 20: #it is a first time sensor
            parameters = json.loads(data)
            boundaries = get_boundaries(parameters)
            sensor_id = parameters[0]
            if sensor_id in sensor_ids: #update sensor
                print >>sensor_id_writepipe[sensor_id], 'kill'
                print "Updated! ID:", sensor_id
                sensor_id_boundaries[sensor_id] = boundaries
                sensor_id_status[sensor_id] = boundaries
                #print sensor_id_boundaries
                sensor_id_writepipe[sensor_id] = new_writerthread_withpipe(str(sensor_id))
            else: #first time sensor
                print "New Sensor! ID:", sensor_id
                sensor_id_boundaries[sensor_id] = boundaries
                sensor_id_status[sensor_id] = boundaries
                sensor_id_boundaries[sensor_id]['timestamp'] = -1
                sensor_id_status[sensor_id]['timestamp'] = -1
                sensor_id_writepipe[sensor_id] = new_writerthread_withpipe(str(sensor_id))
                sensor_ids.append(int(sensor_id))
            sleep(0.5)
            #print sensor_id_boundaries
            #print sensor_id_writepipe
            #print sensor_ids
        else: #continuous message
            unpack_format = len(data) * 'B'
            parse_id = unpack(unpack_format, data)
            sensor_id = parse_id[-1]
            if sensor_id in sensor_ids:
                sensor_id_boundaries[sensor_id]['timestamp'] = time_
                sensor_id_status[sensor_id]['timestamp'] = time_
                message = decode_data(data, sensor_id_boundaries[sensor_id])
                message = csvdata(message)
                message = data + ',' + time + ',' + str(sensor_id) + ',' + message
                print >>sensor_id_writepipe[sensor_id], message
                #print sensor_id_boundaries




if __name__ == '__main__':
    main()
