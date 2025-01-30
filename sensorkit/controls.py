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
from .tools.mixins import NodeMixin

class ChannelProxy(NodeMixin):
    def __init__(self, index: int, channel):
        super().__init__()
        self._index = index
        self._channel = channel

    @property
    def channel_id(self) -> int:
        return self._index

    def __getattr__(self, attr):
        return getattr(self._channel, attr)

class MuxInterface(metaclass=abc.ABCMeta):
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

class PCA9546A(NodeMixin, devices.Device, MuxInterface):
    def __init__(self, bus: I2C, name: str, device_id: int, capabilities: list[int],
                 address: int | str = 112):
        super().__init__(bus, name, device_id, capabilities, address)
        self._mux = adafruit_tca9548a.PCA9546A(bus, address)
        self._channels = [None] * 4

        for i in range(len(self._mux)):
            self._channels[i] = ChannelProxy(i, self._mux[i])

    def __len__(self) -> Literal[4]:
        return len(self._mux)

    @property
    def real_device(self):
        return self._mux

    def channels(self) -> Iterator[int]:
        for c in self._channels:
            yield c

class MuxFactory:
    def __init__(self):
        self._ctors = {}

    def register_mux(self, device_id, ctor):
        self._ctors[device_id] = ctor

    def get_mux(self, bus: I2C, name: str, device_id: int, capabilities: list[int],
                address: int | str) -> MuxInterface:
        ctor = self._ctors.get(device_id)
        if not ctor:
            raise ValueError(device_id)

        return ctor(bus, name, device_id, capabilities, address)

mux_factory = MuxFactory()
mux_factory.register_mux(constants.PCA9546A, PCA9546A)
