data = "1,443.384963989,2,1077,3,4234"
data = data.split(',')
print data
for i in range(len(data)):
    if data[i] == '1':
        print "temperature: %s" % data[i+1]
    if data[i] == '2':
        print "humidity: %s" % data[i+1]
    if data[i] == '3':
        print "battery: %s" % data[i+1]
