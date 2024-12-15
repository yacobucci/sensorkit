from apscheduler.schedulers.background import BackgroundScheduler
import argparse
import asyncio
from contextlib import asynccontextmanager
import logging
import sys

import board
from busio import I2C
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
import uvicorn

from api import metrics
from sensorkit.config import Config
from sensorkit import controls
from sensorkit import datastructures
from sensorkit import devices
from sensorkit import devicetree
from sensorkit import meters
from tools.getters import OpenMeteoGetter

logger = logging.getLogger(__name__)

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

scheduler = BackgroundScheduler()
state = None

location = 'https://api.open-meteo.com/v1/forecast?'
params = {
    'latitude': 39.7592537,
    'longitude': -105.1230315,
    'current': 'pressure_msl'
}

def main():
    parser = argparse.ArgumentParser(description='monitor.py: I2C sensor monitor')
    parser.add_argument(
        '--config-file',
        help='Global configuration file',
        default='${HOME}/.config/sensorkit-monitor/config.yaml'
    )
    parser.add_argument(
        '--test',
        help='Temp argument for development',
        default=False
    )
    args = parser.parse_args()

    config = Config(args.config_file)

    try:
        dest = config.log_destination
        is_stream = False
        level = config.log_level
        fmt = config.log_format
    except AttributeError as e:
        print('disabling custom logging, using defaults - {}'.format(e), file=sys.stderr)
        dest = sys.stdout
        is_stream = True
        fmt = '%(levelname)s %(asctime)s : %(message)s'
        level = 'debug'
    finally:
        if is_stream:
            logging.basicConfig(stream=dest, encoding='utf-8', format=fmt)
        else:
            logging.basicConfig(filename=dest, encoding='utf-8', format=fmt)
        set_log_level(level, logger)

    app = Starlette(debug=True)
    state = datastructures.State(app.state)

    tree = devicetree.DeviceTree(board.I2C(), state)
    state.tree = tree

    try:
        interval = config.altimeter_calibration_interval

        logger.debug('getting mean sea level pressure for altimeter calibration')

        handler = OpenMeteoGetter(state)
        handler.url_get(location, params)
        logger.debug('calibration pressure stored: %s', state.altimeter_calibration)

        logger.debug('adding calibration job to scheduler')

        #XXX make objects so can configure with data from config
        scheduler.add_job(handler.url_get, 'interval', seconds=interval, kwargs = {
            'url': location,
            'params': params
        })
    except AttributeError as e:
        logger.info('disabling altimeter calibration - %s', e)

    try:
        encoding = config.metrics_encoding
        labels = config.metrics_labels
        endpoint = config.metrics_endpoint

        exporter = metrics.metrics_factory.get_exporter(encoding, labels)
        app.add_route(endpoint, exporter.export)
    except AttributeError as e:
        logger.info('disabling metrics exporting - %s', e)

    scheduler.start()

    host = config.host
    port = config.port
    config = uvicorn.Config(app, host=host, port=port, log_level='debug')
    server = uvicorn.Server(config)

    if args.test is False:
        server.run()

if __name__ == '__main__':
    main()
