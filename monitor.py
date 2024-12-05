import asyncio
import logging

import board
from busio import I2C
from quart import Quart, current_app

from modules import devices
from modules import controls
from modules import meters

app = Quart(__name__)
app.logger.setLevel(logging.DEBUG)

#params = {
#    'latitude': 39.7592537,
#    'longitude': -105.1230315,
#    'current': 'pressure_msl'
#}

def create_meters(i2c: I2C, ignore_set: set) -> list[meters.MeterInterface]:
    objects = []
    if i2c.try_lock():
        addresses = i2c.scan()
        i2c.unlock()

        app.logger.info('device scan %s, ignore set %s',
                        [hex(n) for n in addresses],
                        [hex(n) for n in ignore_set])

        for a in addresses:
            if a in ignore_set:
                app.logger.debug('ignoring addr %s, filtered by ignore_set argument', hex(a))
                continue

            app.logger.debug('setting up device address %s', hex(a))

            dev = devices.device_types[a]
            app.logger.debug('found device: %s', dev)

            for cap in dev['capabilities']:
                try:
                    m = meters.meter_factory.get_meter(dev['id'], cap, i2c)
                    objects.append(m)
                except ValueError as e:
                    app.logger.warning('name %s, board %s, capability %s - no associated ctor',
                                       dev['name'], dev['id'], cap)
    return objects

def setup_bus_devices() -> list[meters.MeterInterface]:
    all_meters = []
    i2c = board.I2C()

    bus_devices = i2c.scan()
    app.logger.debug('initial scan results: %s', [hex(n) for n in bus_devices])

    if len(bus_devices) == 1:
        app.logger.info('single device bus, checking for multiplexer presence')

        addr = bus_devices[0]
        d = devices.device_types[addr]
        if d['type'] == devices.CONTROL and d['subtype'] == devices.MUX:
            app.logger.info('multiplexer %s found at addr %s, setting up multiple channels',
                            d['name'], hex(addr))

            mux = controls.mux_factory.get_mux(d['id'], i2c)
            app.logger.info('multiplexer supported channels: %s', len(mux))

            for virtual_i2c in mux.channels():
                ignore_set = set([ mux.address() ])
                objects = create_meters(virtual_i2c, ignore_set)
                app.logger.info('meters %s', meters)
                all_meters.extend(objects)
        else:
            app.logger.info('single device on bus, setting up meters')
            all_meters = create_meters(virtual_i2c, {})
    else:
        app.logger.info('multiple devices on bus, setting up meters')
        all_meters = create_meters(virtual_i2c, {})

    return all_meters

def main():
    all_meters = setup_bus_devices()
    app.logger.debug('all devices available: %s', all_meters)

#                                b = m.board()
#                                metric = m.measurement()
#                                bus_id = m.bus_id()
#
#                                if metric == devices.ALTITUDE:
#                                    # XXX just for testing
#                                    import json
#                                    import urllib.request
#                                    location = 'https://api.open-meteo.com/v1/forecast?latitude=39.7592537&longitude=-105.1230315&current=pressure_msl'
#                                    contents = urllib.request.urlopen(location)
#                                    if contents.status == 200:
#                                        data = contents.read()
#                                        obj = json.loads(data)
#                                        msl = obj['current']['pressure_msl']
#                                        m.set_sea_level_pressure(msl)
#
#                                value = m.measure()
#
#                                print('Board {} Measurement {} Value {} on Bus {}'.format(b, metric, value, bus_id))

if __name__ == '__main__':
    main()
