# -*- coding: utf-8 -*-
import gdp
from random import *
def write_config(filename):
    r = open(filename, 'r')
    gcl_input = r.readline().rstrip('\n')
    pem_input = r.readline().rstrip('\n')
    r.close
    return gcl_input, pem_input

def gcl_append_init(config_file):
    gdp.gdp_init()
    gcl_input, pem_input = write_config(config_file)
    print "gcl: [%r]" % gcl_input
    print "pem: [%r]" % pem_input

    gcl_name = gdp.GDP_NAME(gcl_input)
    skey = gdp.EP_CRYPTO_KEY(filename=pem_input,
           keyform=gdp.EP_CRYPTO_KEYFORM_PEM, flags=gdp.EP_CRYPTO_F_SECRET)

    gcl_handle = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RA, {"skey":skey})
    return gcl_handle

#GDP Writing
gcl_handle = gcl_append_init("inputs.txt")
data =  randint(1,100)
gcl_handle.append({"data": str(data)})
print "sent:", data
exit()
