import gdp
import pexpect
import os
import time

GDPLOGD_SERVER = "ph.edu.upd.pcari.gdplogd"
GCL_KEY = "pass27word"

def open_gcl_write(gcl_complete_name_str):
	print "opening for writing: %s" % gcl_complete_name_str
	skey = gdp.EP_CRYPTO_KEY(filename=gcl_complete_name_str+".pem",
			keyform=gdp.EP_CRYPTO_KEYFORM_PEM,
			flags=gdp.EP_CRYPTO_F_SECRET)
	gcl_name = gdp.GDP_NAME(gcl_complete_name_str)
	return gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_AO, open_info={'skey':skey})

def open_gcl_read(gcl_complete_name_str, timeout=0):
	print "opening for reading: %s" % gcl_complete_name_str
	start = time.time()
	handler = []
	while time.time() - start <= timeout + 1:
		try:
			gcl_name = gdp.GDP_NAME(gcl_complete_name_str)
			handler = gdp.GDP_GCL(gcl_name, gdp.GDP_MODE_RO)
			break
		except:
			pass
		if timeout == 0:
			break
	del gcl_name
	return handler

def create_gcl(gcl_complete_name_str):
	print "creatin gcl: %s" % gcl_complete_name_str
	command = "gcl-create %s %s" % (GDPLOGD_SERVER, gcl_complete_name_str)
	child = pexpect.spawn(command)
	#fout = file("LOG.TXT","w")
	#child.setlog(fout)
	child.expect("pass")
	child.sendline(GCL_KEY)
	child.expect("erify")
	child.sendline(GCL_KEY)
	child.expect("new GCL ")
	child.expect(pexpect.EOF)
	gcl_file = child.before
	gcl_file = gcl_file.split()[0]
	print gcl_file
	os.system("mv ./%s.pem ./%s.pem" % (gcl_file, gcl_complete_name_str))
	time.sleep(0.5)
	command = "openssl ec -in ./%s.pem -out ./%s.new.pem -outform PEM" % \
			(gcl_complete_name_str, gcl_complete_name_str)
	child = pexpect.spawn(command)
	child.expect("pass")
	child.sendline(GCL_KEY)
	time.sleep(0.5)
	os.system("mv ./%s.pem ./%s.old.pem" % (gcl_complete_name_str, \
			gcl_complete_name_str))
	time.sleep(0.5)
	os.system("mv ./%s.new.pem ./%s.pem" % (gcl_complete_name_str, \
			gcl_complete_name_str))
	time.sleep(0.5)


def pack_datum(datum):
	return {"data": datum}
