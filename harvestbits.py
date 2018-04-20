import time,pigpio
import numpy as np

timeStamps = []
runningCpm = []
bitarray = []

def mycb(x,y,z):
    t = time.time()

    timeStamps.append(t)

    # when we receive a new timestamp, update our counts per minute
    if len(timeStamps) >= 2:
        t0 = timeStamps[-2]
        t1 = timeStamps[-1]
        runningCpm.append(60 / (t1 - t0))
        cpm = sum(runningCpm) / float(len(runningCpm))
        cpmfile = open("geigercpm","w+")
        cpmfile.write(str(cpm))
        cpmfile.close()
        #t0 = t1
        if len(runningCpm) >= 30:
            runningCpm.pop(0)
        print ("counts per minute:", cpm)

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
        # This needs to change to geigerRandCache
        fo = open("geigerRandCache","ab+")
        #fo.write(bitpackedArray)
        fo.write((bitpackedArray))
        fo.flush()
        fo.close()
        del bitarray[:]


pin=pigpio.pi()
cb=pin.callback(23,pigpio.FALLING_EDGE,mycb)

while True:

    time.sleep(3)
