import logging

from prometheus_client import Counter, Gauge, generate_latest
from starlette.responses import Response

from sensorkit import devices
from sensorkit import devicetree

logger = logging.getLogger(__name__)

# XXX pull in set from configuration
prometheus_labels = [ 'board_name', 'board', 'bus_id', 'address', 'units' ]

dynamic_gauges = {}

class MetricsInterface:
    def export():
        pass

class PrometheusExporter(MetricsInterface):
    def __init__(self):
        super().__init__()

    async def export(self, request) -> Response:
        tree = request.app.state.tree
        for meter in tree.meters():
            if meter.measurement not in dynamic_gauges:
                dimension = devices.to_capability_strings[meter.measurement]
                dynamic_gauges[meter.measurement] = \
                    Gauge(dimension,
                          'Sensor measurement - {}'.format(dimension),
                          prometheus_labels)
            gauge = dynamic_gauges[meter.measurement]
            gauge.labels(meter.name,
                         meter.board,
                         meter.bus_id,
                         meter.address,
                         meter.units).set(meter.measure)

        response = Response(generate_latest(), media_type='text/plain; charset=utf-8')
        return response

class MetricsFactory:
    def __init__(self):
        self._ctors = {}

    def register_method(self, encoding, ctor):
        self._ctors[encoding] = ctor

    def get_exporter(self, encoding):
        ctor = self._ctors.get(encoding)
        if not ctor:
            raise ValueError(encoding)

        return ctor()

metrics_factory = MetricsFactory()
metrics_factory.register_method('prometheus', PrometheusExporter)
