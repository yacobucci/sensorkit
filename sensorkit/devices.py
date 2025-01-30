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
from .tools.mixins import (
        NodeMixin,
        RunnableInterface,
)

logger = logging.getLogger(__name__)

class DeviceCapabilityError(Exception):
    """Raised when Device cannot read requested capability."""

class DeviceInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'address') and
                callable(subclass.address) and
                hasattr(subclass, 'device_id') and
                callable(subclass.device_id) and
                hasattr(subclass, 'name') and
                callable(subclass.name) and
                hasattr(subclass, 'channel_id') and
                callable(subclass.channel_id) and
                hasattr(subclass, 'real_device') and
                callable(subclass.real_device) and
                hasattr(subclass, 'capabilities') and
                callable(subclass.capabilities) and
                hasattr(subclass, 'capabilities_gen') and
                callable(subclass.capabilities_gen) and
                hasattr(subclass, 'read_capability') and
                callable(subclass.read_capability) and
                hasattr(subclass, 'capability_units') and
                callable(subclass.capability_units) or
                NotImplemented)

    @abc.abstractmethod
    def address(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def device_id(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def channel_id(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def real_device(self):
        raise NotImplementedError

    @abc.abstractmethod
    def capabilities(self) -> list[int]:
        raise NotImplementedError

    @abc.abstractmethod
    def capabilities_gen(self) -> Iterator[int]:
        raise NotImplementedError

    @abc.abstractmethod
    def read_capability(self, capability: int) -> [ int | float ]:
        raise NotImplementedError

    @abc.abstractmethod
    def capability_units(self, capability: int) -> str:
        raise NotImplementedError

class Device(DeviceInterface):
    def __init__(self, bus: I2C | None, name: str, device_id: int, capabilities: list[int],
                 address: int, env: dict[str, Any] | None = None):
        self._bus = bus
        self._name = name
        self._device_id = device_id
        self._caps = capabilities
        self._dev = None
        self._property_map = dict()
        self._capability_units = dict()

        self._address = address
        self._has_channel = False
        self._channel_id = 0
        if self._bus is not None and hasattr(self._bus, 'channel_switch'):
            n = int.from_bytes(self._bus.channel_switch, 'little')
            r = 0
            while n > 1:
                n = n >> 1
                r = r + 1
            self._channel_id = r
            self._has_channel = True

    @property
    def address(self) -> int:
        return self._address

    @property
    def device_id(self) -> int:
        return self._device_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def capabilities(self) -> list[int]:
        return self._caps

    def capabilities_gen(self) -> Iterator[int]:
        for cap in self._caps:
            yield cap

    def read_capability(self, capability: int) -> [ int | float ]:
        try:
            prop = self._property_map[capability]
        except KeyError:
            raise DeviceCapabilityError('capability ({}) is unsupported by device ({})'.format(
                capability, self._device_id))

        if self._dev is None:
            msg = 'device initialized without real device ({})'.format(self._device_id)
            raise DeviceCapabilityError(msg)

        return getattr(self._dev, prop)

    def capability_units(self, capability: int) -> str:
        try:
            units = self._capability_units[capability]
            return units
        except KeyError:
            msg = 'capability ({}) has no associated units for device ({})'.format(capability,
                                                                                   self._device_id)
            raise DeviceCapabilityError(msg)

    @property
    def channel_id(self) -> [ int | None ]:
        if self._has_channel is True:
            return self._channel_id
        return None

class Bmp390(NodeMixin, Device):
    def __init__(self, bus: I2C, name: str, device_id: int,
                 address: int = 119, env: dict[str, Any] | None = None):
        super().__init__(bus, name, device_id,
                         [ constants.TEMPERATURE, constants.PRESSURE, constants.ALTITUDE ],
                         address)
        self._dev = adafruit_bmp3xx.BMP3XX_I2C(bus, address)
        self._property_map[constants.TEMPERATURE] = 'temperature'
        self._capability_units[constants.TEMPERATURE] = constants.CELSIUS_UNITS
        self._property_map[constants.PRESSURE] = 'pressure'
        self._capability_units[constants.PRESSURE] = constants.HECTOPASCAL_UNITS
        self._property_map[constants.ALTITUDE] = 'altitude'
        self._capability_units[constants.ALTITUDE] = constants.METER_UNITS

    @property
    def real_device(self):
        return self._dev

class Sht41(NodeMixin, Device):
    def __init__(self, bus: I2C, name: str, device_id: int,
                 address: int = 68, env: dict[str, Any] | None = None):
        super().__init__(bus, name, device_id,
                         [ constants.RELATIVE_HUMIDITY, constants.TEMPERATURE ],
                         address)
        self._dev = adafruit_sht4x.SHT4x(bus, address)
        self._property_map[constants.RELATIVE_HUMIDITY] = 'relative_humidity'
        self._capability_units[constants.RELATIVE_HUMIDITY] = constants.PERC_RELATIVE_HUMIDITY_UNITS
        self._property_map[constants.TEMPERATURE] = 'temperature'
        self._capability_units[constants.TEMPERATURE] = constants.CELSIUS_UNITS

    @property
    def real_device(self):
        return self._dev

class Veml7700(NodeMixin, Device):
    def __init__(self, bus: I2C, name: str, device_id: int,
                 address: int = 16, env: dict[str, Any] | None = None):
        super().__init__(bus, name, device_id, [ constants.LUX, constants.AMBIENT_LIGHT ], address)
        self._dev = adafruit_veml7700.VEML7700(bus, address)
        self._property_map[constants.LUX] = 'lux'
        self._capability_units[constants.LUX] = constants.LUX_UNITS
        self._property_map[constants.AMBIENT_LIGHT] = 'light'
        self._capability_units[constants.AMBIENT_LIGHT] = constants.AMBIENT_LIGHT_UNITS

    @property
    def real_device(self):
        return self._dev

class Scd41(NodeMixin, Device, RunnableInterface):
    def __init__(self, bus: I2C, name: str, device_id: int,
                 address: int = 98, env: dict[str, Any] | None = None):
        super().__init__(bus, name, device_id,
                         [ constants.TEMPERATURE, constants.RELATIVE_HUMIDITY, constants.CO2 ],
                         address)
        self._dev = adafruit_scd4x.SCD4X(bus, address)
        self._property_map[constants.TEMPERATURE] = 'temperature'
        self._capability_units[constants.TEMPERATURE] = constants.CELSIUS_UNITS
        self._property_map[constants.RELATIVE_HUMIDITY] = 'relative_humidity'
        self._capability_units[constants.RELATIVE_HUMIDITY] = constants.PERC_RELATIVE_HUMIDITY_UNITS
        self._property_map[constants.CO2] = 'CO2'
        self._capability_units[constants.CO2] = constants.PPM_UNITS

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

class Tsl2591(NodeMixin, Device):
    def __init__(self, bus: I2C, name: str, device_id: int,
                 address: int = 41, env: dict[str, Any] | None = None):
        super().__init__(bus, name, device_id,
                         [ constants.LUX, constants.INFRARED, constants.VISIBLE,
                           constants.FULL_SPECTRUM ],
                         address)
        self._dev = adafruit_tsl2591.TSL2591(bus, address)
        self._property_map[constants.LUX] = 'lux'
        self._capability_units[constants.LUX] = constants.LUX_UNITS
        self._property_map[constants.INFRARED] = 'infrared'
        self._capability_units[constants.INFRARED] = constants.AMBIENT_LIGHT_UNITS
        self._property_map[constants.VISIBLE] = 'visible'
        self._capability_units[constants.INFRARED] = constants.AMBIENT_LIGHT_UNITS
        self._property_map[constants.FULL_SPECTRUM] = 'full_spectrum'
        self._capability_units[constants.FULL_SPECTRUM] = constants.AMBIENT_LIGHT_UNITS

    @property
    def real_device(self):
        return self._dev

class DeviceFactory:
    def __init__(self):
        self._ctors = {}

    def register_device(self, device_id, ctor):
        self._ctors[device_id] = ctor

    def get_device(self, bus: I2C, name: str, device_id: int,
                   address: int, env: dict[str, Any] | None = None) -> DeviceInterface:
        ctor = self._ctors.get(device_id)
        if not ctor:
            raise ValueError(device_id)

        return ctor(bus, name, device_id, address, env)

device_factory = DeviceFactory()
device_factory.register_device(constants.BMP390, Bmp390)
device_factory.register_device(constants.SHT41, Sht41)
device_factory.register_device(constants.VEML7700, Veml7700)
device_factory.register_device(constants.SCD41, Scd41)
device_factory.register_device(constants.TSL2591, Tsl2591)
