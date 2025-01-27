import abc
from collections.abc import Iterator
import logging
import typing

from busio import I2C

from . import datastructures
from . import devices
from .constants import *

logger = logging.getLogger(__name__)

class MeterInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'address') and
                callable(subclass.address) and
                hasattr(subclass, 'board') and
                callable(subclass.board) and
                hasattr(subclass, 'name') and
                callable(subclass.name) and
                hasattr(subclass, 'bus_id') and
                callable(subclass.bus_id) and
                hasattr(subclass, 'measure') and
                callable(subclass.measure) and
                hasattr(subclass, 'measurement') and
                callable(subclass.measurement) and
                hasattr(subclass, 'units') and
                callable(subclass.units) or
                NotImplemented)

    @abc.abstractmethod
    def address(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def board(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def bus_id(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def measure(self) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    def measurement(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def units(self) -> str:
        raise NotImplementedError

class Meter(MeterInterface):
    def __init__(self, device, measurement: int):
        self._device = device
        self._measurement = measurement

    @property
    def address(self) -> int:
        return self._device.address

    @property
    def board(self) -> int:
        return self._device.board

    @property
    def name(self) -> str:
        return self._device.name

    @property
    def bus_id(self) -> int:
        return self._device.bus_id

    @property
    def measure(self) -> float:
        return self._device.read_capability(self._measurement)

    @property
    def measurement(self) -> int:
        return self._measurement

    @property
    def units(self) -> str:
        return self._device.capability_units(self._measurement)
