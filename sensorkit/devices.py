import abc

import adafruit_bmp3xx
import adafruit_scd4x
import adafruit_sht4x
import adafruit_veml7700
from busio import I2C

from .constants import *
from .profiles import *

class DeviceInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'real_device') and
                callable(subclass.real_device) or
                NotImplemented)

    def __init__(self, profile: DeviceProfile):
        self._device_profile = profile

    @property
    def profile(self) -> DeviceProfile:
        return self._device_profile

    @property
    def address(self) -> int:
        return hex(self._device_profile.address)

    @property
    def board(self) -> int:
        return self._device_profile.device_id

    @property
    def name(self) -> str:
        return self._device_profile.name

    @abc.abstractmethod
    def real_device(self):
        raise NotImplementedError

class Bmp390(DeviceInterface):
    def __init__(self, profile: DeviceProfile, i2c: I2C):
        super().__init__(profile)
        self._bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

    @property
    def real_device(self):
        return self._bmp

class Sht41(DeviceInterface):
    def __init__(self, profile: DeviceProfile, i2c: I2C):
        super().__init__(profile)
        self._sht = adafruit_sht4x.SHT4x(i2c)

    @property
    def real_device(self):
        return self._sht

class Veml7700(DeviceInterface):
    def __init__(self, profile: DeviceProfile, i2c: I2C):
        super().__init__(profile)
        self._veml7700 = adafruit_veml7700.VEML7700(i2c)

    @property
    def real_device(self):
        return self._veml7700

class Scd41(DeviceInterface):
    def __init__(self, profile: DeviceProfile, i2c: I2C):
        super().__init__(profile)
        self._scd = adafruit_scd4x.SCD4X(i2c)

    @property
    def real_device(self):
        return self._scd

class DeviceFactory:
    def __init__(self):
        self._ctors = {}

    def register_device(self, board, ctor):
        self._ctors[board] = ctor

    def get_device(self, board: int, profile: DeviceProfile, i2c: I2C) -> DeviceInterface:
        ctor = self._ctors.get(board)
        if not ctor:
            raise ValueError(board)

        return ctor(profile, i2c)

device_factory = DeviceFactory()
device_factory.register_device(BMP390, Bmp390)
device_factory.register_device(SHT41, Sht41)
device_factory.register_device(VEML7700, Veml7700)
device_factory.register_device(SCD41, Scd41)
