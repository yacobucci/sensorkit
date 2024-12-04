#import board
#import adafruit_tca9548a

#import adafruit_sht4x
 
#import adafruit_bmp3xx

#i2c = board.I2C()

#mux = adafruit_tca9548a.PCA9546A(i2c)

#for channel in range(4):
#    if mux[channel].try_lock():
#        print('Channel {}:'.format(channel), end='')
#        addresses = mux[channel].scan()
#        print([hex(address) for address in addresses])
#        mux[channel].unlock()

#sht = adafruit_sht4x.SHT4x(mux[0])
#bmp = adafruit_bmp3xx.BMP3XX_I2C(mux[0])

#print(sht.measurements)
#print('{} {} {}'.format(bmp.pressure, bmp.altitude, bmp.temperature))

#sht = adafruit_sht4x.SHT4x(mux[1])
#bmp = adafruit_bmp3xx.BMP3XX_I2C(mux[1])

#print(sht.measurements)
#print('{} {} {}'.format(bmp.pressure, bmp.altitude, bmp.temperature))

import adafruit_tca9548a as mux
import board

from modules.devices import *

def main():
    # arg parsing
    i2c = board.I2C()

    bus_devices = i2c.scan()
    print(bus_devices)

    chains = None

    if len(bus_devices) == 1:
        addr = bus_devices[0]

        d = devices[addr]
        if d['type'] == CONTROL and d['subtype'] == MUX:
            print('single device is a multiplexer')
        else:
            try:
                _ = devices[addr]
            except KeyError as _:
                print('single device unsupported: {}'.format(hex(addr)))
        #XXX make this the mux control
        chains = [i2c]
    else:
        print('single bus chain')
        chains = [i2c]

    for channel in range(len(chains)):
        if chains[channel].try_lock():
            print('channel {}:'.format(channel), end='')
            addresses = chains[channel].scan()
            print([hex(address) for address in addresses])
            chains[channel].unlock()

if __name__ == '__main__':
    main()
