# -*- coding: utf-8 -*-
import gdp
from random import *
def write_config(filename):
    r = open(filename, 'r')
    gcl_input = r.readline().rstrip('\n')
    pem_input = r.readline().rstrip('\n')
    r.close
    return gcl_input, pem_input

gdp.gdp_init()
random_int =  randint(1,100)
gcl_input = write_config("inputs.txt")[0]
print "gcl: [%r]" % gcl_input

gcl_name = gdp.GDP_NAME(gcl_input)
gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RO)

#GDP Reading
gcl_handle.multiread(-5,4)

while True:
    event = gcl_handle.get_next_event(None)
    if event['type'] == gdp.GDP_EVENT_EOS:
        break
    print event['datum']['data']

exit()
