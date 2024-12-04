try:
    from typing import List
    from typing_extensions import Literal
    # XXX Gravity interface may change this - right now CircuitPython specific
    from busio import I2C
except ImportError:
    pass

import board
import adafruit_tca9548a

from . import devices

class MuxInterface:
    def channels(self):
        pass

    def __len__(self):
        pass

class PCA9546A:
    def __init__(self, i2c: I2C):
        self._mux = adafruit_tca9548a.PCA9546A(i2c)
        pass

    def __len__(self) -> Literal[4]:
        return len(self._mux)

    def channels(self):
        for c in range(len(self._mux)):
            yield self._mux[c]

class MuxFactory:
    def __init__(self):
        self._ctors = {}

    def register_method(self, board, ctor):
        self._ctors[board] = ctor

    def get_mux(self, board, i2c: I2C) -> MuxInterface:
        ctor = self._ctors.get(board)
        if not ctor:
            raise ValueError(board)

        return ctor(i2c)

mux_factory = MuxFactory()
mux_factory.register_method(devices.PCA9546A, PCA9546A)
