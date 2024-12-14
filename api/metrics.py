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
    def __init__(self, labels: dict[str, str] = {}):
        super().__init__()

        self._labels = prometheus_labels + list(labels.keys())
        self._config = labels

    async def export(self, request) -> Response:
        tree = request.app.state.tree
        for meter in tree.meters():
            if meter.measurement not in dynamic_gauges:
                dimension = devices.to_capability_strings[meter.measurement]

                g = Gauge(dimension,
                          'Sensor measurement - {}'.format(dimension),
                          self._labels)
                dynamic_gauges[meter.measurement] = g

            gauge = dynamic_gauges[meter.measurement]
            d = dict()
            d[prometheus_labels[0]] = meter.name
            d[prometheus_labels[1]] = meter.board
            d[prometheus_labels[2]] = meter.bus_id
            d[prometheus_labels[3]] = meter.address
            d[prometheus_labels[4]] = meter.units
            for k in self._config:
                d[k] = self._config[k]

            gauge.labels(**d).set(meter.measure)

        response = Response(generate_latest(), media_type='text/plain; charset=utf-8')
        return response

class MetricsFactory:
    def __init__(self):
        self._ctors = {}

    def register_method(self, encoding, ctor):
        self._ctors[encoding] = ctor

    def get_exporter(self, encoding, labels: dict[str, str] = {}):
        ctor = self._ctors.get(encoding)
        if not ctor:
            raise ValueError(encoding)

        return ctor(labels)

metrics_factory = MetricsFactory()
metrics_factory.register_method('prometheus', PrometheusExporter)
