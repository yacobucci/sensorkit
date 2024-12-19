from apscheduler.schedulers.background import BackgroundScheduler
import argparse
import logging
import sys

import board
from starlette.applications import Starlette
import uvicorn

from api import metrics
from config import Config, load_config
from sensorkit import SensorKit

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

    data = load_config(args.config_file)
    config = Config(data)

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

    kit = SensorKit(board.I2C(), data['sensorkit'], scheduler, app.state)

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
