# -*- coding: utf-8 -*-
import gdp
from random import *
def write_config(filename):
    r = open(filename, 'r')
    gcl_input = r.readline().rstrip('\n')
    pem_input = r.readline().rstrip('\n')
    r.close
    return gcl_input, pem_input

def gcl_subscription_init(config_file):
    gdp.gdp_init()
    gcl_input = write_config("inputs.txt")[0]
    print "gcl: [%r]" % gcl_input
    gcl_name = gdp.GDP_NAME(gcl_input)
    gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RO)
    return gcl_handle

#GDP Reading
gcl_handle = gcl_subscription_init("inputs.txt")
gcl_handle.subscribe(0, 0, None)

while True:
    event = gcl_handle.get_next_event(None)
    print event['datum']['data']

exit()
