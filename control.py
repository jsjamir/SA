from Queue import Queue
from threading import Thread
from time import sleep
import re

def control_center(q):
  while True:
    template = re.compile(r'^(status clients|status sensors( +\d+)?|stop \d+( +\d+)?|start \d+( +\d+)?)$')
    command = raw_input().rstrip('\n')
    if not template.match(command):
        print "invalid command!"
    else:
        command = command.split(' ')
        
        print command
        print "valid!"



q = Queue(maxsize=0)
control = Thread(target=control_center, args=(q,))
control.setDaemon(True)
control.start()

while True:
    sleep(10)
    if not q.empty():
        command = q.get()
        q.task_done()
        print "command", command
    print "doing my tasks"


q.join()
