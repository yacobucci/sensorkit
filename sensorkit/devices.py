import abc
from collections.abc import Iterator
import logging
from typing import Any

import adafruit_bmp3xx
import adafruit_scd4x
import adafruit_sht4x
import adafruit_tsl2591
import adafruit_veml7700
from busio import I2C

from . import constants
from . import profiles
from .tools.mixins import RunnableMixin

logger = logging.getLogger(__name__)

class DeviceInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'address') and
                callable(subclass.address) and
                hasattr(subclass, 'board') and
                callable(subclass.board) and
                hasattr(subclass, 'name') and
                callable(subclass.name) and
                hasattr(subclass, 'capabilities') and
                callable(subclass.capabilities) and
                hasattr(subclass, 'capabilities_gen') and
                callable(subclass.capabilities_gen) and
                hasattr(subclass, 'bus') and
                callable(subclass.bus) and
                hasattr(subclass, 'bus_id') and
                callable(subclass.bus_id) and
                hasattr(subclass, 'real_device') and
                callable(subclass.real_device) or
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
    def capabilities(self) -> list[int]:
        raise NotImplementedError

    @abc.abstractmethod
    def capabilities_gen(self) -> Iterator[int]:
        raise NotImplementedError

    @abc.abstractmethod
    def bus(self) -> I2C:
        raise NotImplementedError

    @abc.abstractmethod
    def bus_id(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def real_device(self):
        raise NotImplementedError

class Device(DeviceInterface):
    def __init__(self, bus: I2C | None, name: str, board: int, capabilities: list[int],
                 address: int, env: dict[str, Any] | None = None):
        self._bus = bus
        self._name = name
        self._board = board
        self._caps = capabilities
        self._address = address

    @property
    def address(self) -> int | str:
        return self._address

    @property
    def board(self) -> int:
        return self._board

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> list[int]:
        return self._caps

    def capabilities_gen(self) -> Iterator[int]:
        for cap in self._caps:
            yield cap

    @property
    def bus(self) -> I2C:
        return self._bus

    @property
    def bus_id(self) -> int:
        r = 0
        if self._bus is not None and 'channel_switch' in self._bus.__dict__:
            n = int.from_bytes(self._bus.channel_switch, 'little')
            while n > 1:
                n = n >> 1
                r = r + 1
        return r

class VirtualDevice(Device):
    def __init__(self, name: str, board: int, capabilities: list[int],
                 address: int = constants.VIRTUAL_ADDR, env: dict[str, Any] | None = None):
        super().__init__(None, name, board, capabilities, address)
    
    @property
    def real_device(self):
        return None

class Bmp390(Device):
    def __init__(self, bus: I2C, name: str, board: int, capabilities: list[int],
                 address: int = 119, env: dict[str, Any] | None = None):
        super().__init__(bus, name, board, capabilities, address)
        self._dev = adafruit_bmp3xx.BMP3XX_I2C(bus, address)

    @property
    def real_device(self):
        return self._dev

class Sht41(Device):
    def __init__(self, bus: I2C, name: str, board: int, capabilities: list[int],
                 address: int = 68, env: dict[str, Any] | None = None):
        super().__init__(bus, name, board, capabilities, address)
        self._dev = adafruit_sht4x.SHT4x(bus, address)

    @property
    def real_device(self):
        return self._dev

class Veml7700(Device):
    def __init__(self, bus: I2C, name: str, board: int, capabilities: list[int],
                 address: int = 16, env: dict[str, Any] | None = None):
        super().__init__(bus, name, board, capabilities, address)
        self._dev = adafruit_veml7700.VEML7700(bus, address)

    @property
    def real_device(self):
        return self._dev

class Scd41(Device, RunnableMixin):
    def __init__(self, bus: I2C, name: str, board: int, capabilities: list[int],
                 address: int = 98, env: dict[str, Any] | None = None):
        super().__init__(bus, name, board, capabilities, address)
        self._dev = adafruit_scd4x.SCD4X(bus, address)
        self._dev.reinit()

        self._env = env

    @property
    def real_device(self):
        return self._dev

    def run(self):
        if 'indoors' in self._env:
            enable = not self._env['indoors']
            self._dev.self_calibration_enabled = enable

        self._dev.start_periodic_measurement()

    def stop(self):
        self._dev.stop_periodic_measurement()

class Tsl2591(Device):
    def __init__(self, bus: I2C, name: str, board: int, capabilities: list[int],
                 address: int = 41, env: dict[str, Any] | None = None):
        super().__init__(bus, name, board, capabilities, address)
        self._dev = adafruit_tsl2591.TSL2591(bus, address)

    @property
    def real_device(self):
        return self._dev

class DeviceFactory:
    def __init__(self):
        self._ctors = {}

    def register_device(self, board, ctor):
        self._ctors[board] = ctor

    def get_device(self, bus: I2C, name: str, board: int, capabilities: list[int],
                   address: int, env: dict[str, Any] | None = None) -> DeviceInterface:
        ctor = self._ctors.get(board)
        if not ctor:
            raise ValueError(board)

        return ctor(bus, name, board, capabilities, address, env)

device_factory = DeviceFactory()
device_factory.register_device(constants.BMP390, Bmp390)
device_factory.register_device(constants.SHT41, Sht41)
device_factory.register_device(constants.VEML7700, Veml7700)
device_factory.register_device(constants.SCD41, Scd41)
device_factory.register_device(constants.TSL2591, Tsl2591)
