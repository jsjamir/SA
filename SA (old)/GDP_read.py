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
record = gcl_handle.read(18)
print "received:", record['data']
exit()
