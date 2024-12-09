import logging

from prometheus_client import Counter, Gauge, generate_latest
from starlette.responses import Response

from . import devices

logger = logging.getLogger(__name__)

temperature = Gauge(
    'temperature',
    'temperature celsius',
    ['board', 'bus']
)

# Async route functions
async def metrics(request):
#                                b = m.board()
#                                metric = m.measurement()
#                                bus_id = m.bus_id()
#
#                                if metric == devices.ALTITUDE:
#                                    # XXX just for testing
#
#                                value = m.measure()
#
#                                print('Board {} Measurement {} Value {} on Bus {}'.format(b, metric, value, bus_id))
    logger.debug('all devices available: %s', request.app.state.meters)
    
    meters = request.app.state.meters
    for meter in meters:
        if meter.board == devices.SHT41 and meter.measurement == devices.TEMPERATURE:
            temperature.labels(meter.board, meter.bus_id).set(meter.measure)

    response = Response(generate_latest(), media_type='text/plain; charset=utf-8')
    return response
