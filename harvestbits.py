import time,pigpio
import numpy as np

# This needs to change to geigerRandCache
fo=open("geigerbits","wb+")
timeStamps = []
bitarray = []
def mycb(x,y,z):
    t=time.time()
    timeStamps.append(t)
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
        #fo.write(bitpackedArray)
        fo.write((bitpackedArray))
        fo.flush()
        del bitarray[:]


pin=pigpio.pi()
cb=pin.callback(23,pigpio.FALLING_EDGE,mycb)

while True:

    time.sleep(3)
