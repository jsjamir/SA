from Queue import Queue
from threading import Thread
from time import sleep
import re
from copy import deepcopy

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
def do_commands():
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


sensor_id_boundaries = {123: {0: [0, 0], 1: [100.0, 10000.0], 2: [123, 545], 'timestamp': 1523840751}, 22: {0: [0, 0], 1: [100.0, 10000.0], 2: [123, 545], 'timestamp': 1523840743}}
sensor_id_status = deepcopy(sensor_id_boundaries)
sensor_ids = [123, 22]

q = control_center_init()
while True:
    do_commands()
    sleep(1)
    print "doing something!"
