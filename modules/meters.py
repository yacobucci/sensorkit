try:
    from typing import List
    from typing_extensions import Literal
    # XXX Gravity interface may change this - right now CircuitPython specific
    from busio import I2C
except ImportError:
    pass

from . import devices

class MeterInterface:
    def measure(self):
        pass

class Temperature:
    def __init__(self):
        pass

    def measure(self):
        return 10

class MeterFactory:
    def __init__(self):
        self._ctors = {}

    def register_method(self, board, ctor):
        self._ctors[board] = ctor

    def get_meter(self, board, i2c: I2C) -> MeterInterface:
        ctor = self._ctors.get(board)
        if not ctor:
            raise ValueError(board)

        return ctor(i2c)

meter_factory = MeterFactory()
meter_factory.register_method(devices.BMP390, Temperature)
