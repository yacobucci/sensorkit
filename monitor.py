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

import board

from modules import devices
from modules import controls
from modules import meters

def main():
    # arg parsing
    i2c = board.I2C()

    bus_devices = i2c.scan()
    print(bus_devices)

    if len(bus_devices) == 1:
        addr = bus_devices[0]

        d = devices.device_types[addr]
        if d['type'] == devices.CONTROL and d['subtype'] == devices.MUX:
            print('single device is a multiplexer')

            mux = controls.mux_factory.get_mux(d['id'], i2c)
            print('channels: {}'.format(len(mux)))

            for c in mux.channels():
                if c.try_lock():
                    addresses = c.scan()
                    # XXX debug log
                    #print('unlocking channel {}'.format(c.channel_switch))
                    c.unlock()
                    print([hex(address) for address in addresses])

                    for a in addresses:
                        if a == mux.address():
                            continue

                        dev = devices.device_types[a]
                        print(dev)

                        for cap in dev['capabilities']:
                            try:
                                m = meters.meter_factory.get_meter(dev['id'], cap, c)
                                b = m.board()
                                metric = m.measurement()
                                bus_id = m.bus_id()

                                if metric == devices.ALTITUDE:
                                    # XXX just for testing
                                    import json
                                    import urllib.request
                                    location = 'https://api.open-meteo.com/v1/forecast?latitude=39.7592537&longitude=-105.1230315&current=pressure_msl'
                                    contents = urllib.request.urlopen(location)
                                    if contents.status == 200:
                                        data = contents.read()
                                        obj = json.loads(data)
                                        msl = obj['current']['pressure_msl']
                                        m.set_sea_level_pressure(msl)

                                value = m.measure()

                                print('Board {} Measurement {} Value {} on Bus {}'.format(b, metric, value, bus_id))
                            except ValueError as e:
                                print(e)
    else:
        print('single bus chain')

if __name__ == '__main__':
    main()
