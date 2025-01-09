import abc
from collections.abc import Iterator
import logging
from typing import Literal

logger = logging.getLogger(__name__)

import board
from busio import I2C
import adafruit_tca9548a

from . import constants
from . import devices

class MuxInterface(devices.DeviceInterface, metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'address') and
                callable(subclass.address) and
                hasattr(subclass, 'channels') and
                callable(subclass.channels) and
                hasattr(subclass, '__len__') and
                callable(subclass.__len__) or
                NotImplemented)

    @abc.abstractmethod
    def channels(self) -> Iterator[int]:
        raise NotImplementedError

    @abc.abstractmethod
    def __len__(self):
        raise NotImplementedError

class PCA9546A(devices.Device, MuxInterface):
    def __init__(self, bus: I2C, name: str, board: int, capabilities: list[int],
                 address: int | str = 112):
        super().__init__(bus, name, board, capabilities, address)
        self._mux = adafruit_tca9548a.PCA9546A(bus, address)
        pass

    def __len__(self) -> Literal[4]:
        return len(self._mux)

    @property
    def real_device(self):
        return self._mux

    def channels(self) -> Iterator[int]:
        for c in range(len(self._mux)):
            yield self._mux[c]

class MuxFactory:
    def __init__(self):
        self._ctors = {}

    def register_mux(self, board, ctor):
        self._ctors[board] = ctor

    def get_mux(self, bus: I2C, name: str, board: int, capabilities: list[int],
                address: int | str) -> MuxInterface:
        ctor = self._ctors.get(board)
        if not ctor:
            raise ValueError(board)

        return ctor(bus, name, board, capabilities, address)

mux_factory = MuxFactory()
mux_factory.register_mux(constants.PCA9546A, PCA9546A)
