from os import urandom

lengthReq = 99
geiger = open("geiger")

output = geiger.read(lengthReq).strip()

lengthRead = len(output)
lengthRemaining = lengthReq - lengthRead
extraOutput = 0

#if lengthRead < lengthReq :
#    #devrand = open("/dev/random")
#    #extraOutput = devrand.read(lengthRemaining)
#    #devrand.close()
#    extraOutput = urandom(lengthRemaining)

geiger.close()

print
print "Output from geiger: " + str(output)
print "length requested: " + str(lengthReq)
print "length actually read: " + str(lengthRead)
#print "extra from os.urandom: " + str(extraOutput)
print

#import os
#
#stats = os.stat('../geigerRandCache')
#print "size: " + str(stats.st_size)
