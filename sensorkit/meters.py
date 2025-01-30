import abc
from collections.abc import Iterator
import logging
import typing

from busio import I2C

from . import datastructures
from . import devices
from .constants import *
from .tools.mixins import NodeMixin

logger = logging.getLogger(__name__)

class MeterInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'measure') and
                callable(subclass.measure) and
                hasattr(subclass, 'measurement') and
                callable(subclass.measurement) and
                hasattr(subclass, 'units') and
                callable(subclass.units) and
                hasattr(subclass, 'address') and
                callable(subclass.address) and
                hasattr(subclass, 'device_id') and
                callable(subclass.device_id) and
                hasattr(subclass, 'name') and
                callable(subclass.name) and
                hasattr(subclass, 'channel_id') and
                callable(subclass.channel_id) or
                NotImplemented)

    @abc.abstractmethod
    def measure(self) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    def measurement(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def units(self) -> str:
        raise NotImplementedError

    @property
    def address(self) -> int:
        raise NotImplementedError

    @property
    def device_id(self) -> int:
        raise NotImplementedError

    @property
    def name(self) -> str:
        raise NotImplementedError

    @property
    def channel_id(self) -> int:
        raise NotImplementedError

class Meter(NodeMixin, MeterInterface):
    def __init__(self, device, measurement: int):
        super().__init__()
        self._device = device
        self._measurement = measurement

    @property
    def address(self) -> int:
        return self._device._address

    @property
    def device_id(self) -> int:
        return self._device._device_id

    @property
    def name(self) -> str:
        return self._device._name

    @property
    def channel_id(self) -> int:
        return self._device._channel_id

    @property
    def measure(self) -> float:
        return self._device.read_capability(self._measurement)

    @property
    def measurement(self) -> int:
        return self._measurement

    @property
    def units(self) -> str:
        return self._device.capability_units(self._measurement)
