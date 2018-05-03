import time,pigpio
import numpy as np

timeStamps = []
#runningCpm = []
cpmStamps = []
bitarray = []

def mycb(x,y,z):
    t = time.time()

    timeStamps.append(t)
    cpmStamps.append(t)

    # when we receive a new timestamp, update our counts per minute
    # this method is deprecated in favor of the method below
    #if len(timeStamps) >= 2:
        #t0 = timeStamps[-2]
        #t1 = timeStamps[-1]
        #runningCpm.append(60 / (t1 - t0))
        #cpm = sum(runningCpm) / float(len(runningCpm))
        #cpmfile = open("geigercpm","a+")
        #cpmfile.write("running: " + str(cpm) + "\n")
        #cpmfile.close()
        #if len(runningCpm) >= 30:
        #    runningCpm.pop(0)
        #print ("running average counts per minute:", cpm)

    # when we receive a new timestamp, update our counts per minute
    if len(cpmStamps) >= 2:
        intervalMinutes = (cpmStamps[-1] - cpmStamps[0]) / 60
        intervalCpm = float(len(cpmStamps)) / intervalMinutes
        cpmfile = open("geigercpm","a+")
        cpmfile.write("interval: " + str(intervalCpm) + "\n")
        cpmfile.close()
        if len(cpmStamps) >= 30:
            cpmStamps.pop(0)
        print ("interval average counts per minute:", intervalCpm)

    # Keeping track of 3 timestamps, once we have three compare for a bit
    if ( len(timeStamps) == 3):
        time1 = timeStamps[0] - timeStamps[1]
        time2 = timeStamps[1] - timeStamps[2]
        randr = time1 > time2
        bitarray.append(int(randr))
        timeStamps.pop(0)
        print randr

    # If we have all 8 bits for a byte, pack them and flush to file
    print len(bitarray)
    if (len(bitarray) == 8):
        bitpackedArray = np.packbits(bitarray)
        fo = open("geigerRandCache","ab+")
        fo.write((bitpackedArray))
        fo.flush()
        fo.close()
        del bitarray[:]


pin=pigpio.pi()
cb=pin.callback(23,pigpio.FALLING_EDGE,mycb)

while True:

    time.sleep(3)
