import board
import adafruit_tca9548a

i2c = board.I2C()
mux = adafruit_tca9548a.PCA9546A(i2c)

for channel in range(len(mux)):
    if mux[channel].try_lock():
        print('Channel {}:'.format(channel), end='')
        addresses = mux[channel].scan()
        print([hex(address) for address in addresses if address != 0x70])
        mux[channel].unlock()
