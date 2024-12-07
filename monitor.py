import argparse
import asyncio
import logging
import sys

import board
from busio import I2C
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

from modules import devices
from modules import controls
from modules import meters

logger = logging.getLogger(__name__)

#params = {
#    'latitude': 39.7592537,
#    'longitude': -105.1230315,
#    'current': 'pressure_msl'
#}

def create_meters(i2c: I2C, ignore_addr_set: set) -> list[meters.MeterInterface]:
    objects = []
    if i2c.try_lock():
        addresses = i2c.scan()
        i2c.unlock()

        logger.info('device scan %s, ignore set %s',
                        [hex(n) for n in addresses],
                        [hex(n) for n in ignore_addr_set])

        for a in addresses:
            if a in ignore_addr_set:
                logger.debug('ignoring addr %s, filtered by ignore_addr_set argument', hex(a))
                continue

            logger.debug('setting up device address %s', hex(a))

            dev = devices.device_types[a]
            logger.debug('found device: %s', dev)

            for cap in dev['capabilities']:
                try:
                    m = meters.meter_factory.get_meter(dev['id'], cap, i2c)
                    objects.append(m)
                except ValueError as e:
                    logger.warning('name %s, board %s, capability %s - no associated ctor',
                                       dev['name'], dev['id'], cap)
    return objects

def setup_bus_devices() -> list[meters.MeterInterface]:
    all_meters = []
    i2c = board.I2C()

    bus_devices = i2c.scan()
    logger.debug('initial scan results: %s', [hex(n) for n in bus_devices])

    if len(bus_devices) == 1:
        logger.info('single device bus, checking for multiplexer presence')

        addr = bus_devices[0]
        d = devices.device_types[addr]
        if d['type'] == devices.CONTROL and d['subtype'] == devices.MUX:
            logger.info('multiplexer %s found at addr %s, setting up multiple channels',
                            d['name'], hex(addr))

            mux = controls.mux_factory.get_mux(d['id'], i2c)
            logger.info('multiplexer supported channels: %s', len(mux))

            for virtual_i2c in mux.channels():
                ignore_addr_set = set([ mux.address() ])
                objects = create_meters(virtual_i2c, ignore_addr_set)
                logger.info('meters %s', meters)
                all_meters.extend(objects)
        else:
            logger.info('single device on bus, setting up meters')
            all_meters = create_meters(virtual_i2c, {})
    else:
        logger.info('multiple devices on bus, setting up meters')
        all_meters = create_meters(virtual_i2c, {})

    return all_meters

def set_log_level(level: str, logger: logging.Logger):
    if level == 'debug':
        logger.setLevel(logging.DEBUG)
    elif level == 'info':
        logger.setLevel(logging.INFO)
    elif level == 'warning':
        logger.setLevel(logging.WARNING)
    elif level == 'error':
        logger.setLevel(logging.ERROR)
    elif level == 'crit':
        logger.setLevel(logging.CRITICAL)
    else:
        raise ValueError(level)

async def metrics(request):
    return JSONResponse({'metrics': {'temp': 55, 'relh': 35}})

def main():
    parser = argparse.ArgumentParser(description='monitor.py: I2C sensor monitor')
    parser.add_argument(
        '--log',
        help='Log file'
    )
    parser.add_argument(
        '--log-level',
        help='Log Level',
        default='debug'
    )
    parser.add_argument(
        '--prometheus',
        help='Setup a prometheus metrics endpoint',
        action=argparse.BooleanOptionalAction,
        default=False
    )
    args = parser.parse_args()

    if args.log is not None and len(args.log) > 0:
        logging.basicConfig(filename=args.log, encoding='utf-8',
                            format='%(levelname)s %(asctime)s : %(message)s')
    else:
        h = logging.StreamHandler(sys.stdout)
        f = logging.Formatter('%(levelname)s %(asctime)s : %(message)s')
        h.setFormatter(f)
        logger.addHandler(h)

    set_log_level(args.log_level, logger)

    all_meters = setup_bus_devices()
    logger.debug('all devices available: %s', all_meters)

    app = Starlette(debug=True)

    if args.prometheus is True:
        app.add_route('/metrics', metrics)

    config = uvicorn.Config(app, port=8000, log_level=args.log_level)
    server = uvicorn.Server(config)
    server.run()
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
