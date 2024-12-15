import abc

try:
    import typing
    from typing import List
    from typing_extensions import Literal
    # XXX Gravity interface may change this - right now CircuitPython specific
    from busio import I2C
except ImportError:
    pass

from . import datastructures
from . import devices

class MeterInterface(devices.DeviceInterface, metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'measure') and
                callable(subclass.measure) and
                hasattr(subclass, measurement) and
                callable(subclass.measurement) and
                hasattr(subclass, 'units') and
                callable(subclass.units) or
                NotImplemented)

    def __init__(self, device, i2c: I2C,
                 state: datastructures.State | None = None):
        super().__init__(device.profile)
        self._device = device
        self._i2c_bus = i2c
        self._state = state

    @property
    def bus_id(self) -> int:
        r = 0
        if 'channel_switch' in self._i2c_bus.__dict__:
            n = int.from_bytes(self._i2c_bus.channel_switch, 'little')
            while n > 1:
                n = n >> 1
                r = r + 1
        return r

    @property
    def real_device(self):
        return self._device.real_device

    @abc.abstractmethod
    def measure(self) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    def measurement(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def units(self) -> str:
        raise NotImplementedError

#
# BMP390 based measurements
class Bmp390Temperature(MeterInterface):
    def __init__(self, device, i2c: I2C,
                 state: datastructures.State | None = None):
        super().__init__(device, i2c, state)

    @property
    def measure(self) -> float:
        bmp = self._device.real_device
        return bmp.temperature

    @property
    def measurement(self) -> int:
        return devices.TEMPERATURE

    @property
    def units(self) -> str:
        return 'Celsius (C)'

class Bmp390Pressure(MeterInterface):
    def __init__(self, device, i2c: I2C,
                 state: datastructures.State | None = None):
        super().__init__(device, i2c, state)

    @property
    def measure(self) -> float:
        bmp = self._device.real_device
        return bmp.pressure

    @property
    def measurement(self) -> int:
        return devices.PRESSURE

    @property
    def units(self) -> str:
        return 'Hectopascal (hPa)'

class Bmp390Altitude(MeterInterface):
    def __init__(self, device, i2c: I2C,
                 state: datastructures.State | None = None):
        super().__init__(device, i2c, state)

        # XXX for now use the real_device...must improve
        bmp = self._device.real_device
        self._default = bmp.sea_level_pressure
        self._key = 'altimeter_calibration'

        self._state.add_key_listener(self._key, self.state_callback)

    @property
    def measure(self) -> float:
        bmp = self._device.real_device
        return bmp.altitude

    @property
    def measurement(self) -> int:
        return devices.ALTITUDE

    @property
    def units(self) -> str:
        return 'Meter (M)'

    @property
    def sea_level_pressure(self):
        bmp = self._device.real_device
        return bmp.sea_level_pressure

    @sea_level_pressure.setter
    def sea_level_pressure(self, msl: float):
        bmp = self._device.real_device
        bmp.sea_level_pressure = msl

    def state_callback(self, key: str, value: typing.Any) -> None:
        if key != 'altimeter_calibration':
            return

        bmp = self._device.real_device
        if value != bmp.sea_level_pressure:
            if value is None:
                bmp.sea_level_pressure = self._default
            else:
                bmp.sea_level_pressure = value
# END BMP390

#
# SHT41 (SHT4x) measurements
class Sht41Temperature(MeterInterface):
    def __init__(self, device, i2c: I2C,
                 state: datastructures.State | None = None):
        super().__init__(device, i2c, state)

    @property
    def measure(self) -> float:
        sht = self._device.real_device
        temp, _ =  sht.measurements
        return temp

    @property
    def measurement(self) -> int:
        return devices.TEMPERATURE

    @property
    def units(self) -> str:
        return 'Celsius (C)'

class Sht41RelativeHumidity(MeterInterface):
    def __init__(self, device, i2c: I2C,
                 state: datastructures.State | None = None):
        super().__init__(device, i2c, state)

    @property
    def measure(self) -> float:
        sht = self._device.real_device
        _, rh = sht.measurements
        return rh

    @property
    def measurement(self) -> int:
        return devices.RELATIVE_HUMIDITY

    @property
    def units(self) -> str:
        return 'Percent Relative Humidity (% rH)'
# END SHT41 (SHT4x)

#
# VEML7700 measurements
class Veml7700AmbientLight(MeterInterface):
    def __init__(self, device, i2c: I2C,
                 state: datastructures.State | None = None):
        super().__init__(device, i2c, state)

    @property
    def measure(self) -> float:
        veml7700 = self._device.real_device
        l = veml7700.light
        return l

    @property
    def measurement(self) -> int:
        return devices.AMBIENT_LIGHT

    @property
    def units(self) -> str:
        return 'Ambient Light Data'

class Veml7700Lux(MeterInterface):
    def __init__(self, device, i2c: I2C,
                 state: datastructures.State | None = None):
        super().__init__(device, i2c, state)

    @property
    def measure(self) -> float:
        veml7700 = self._device.real_device
        l = veml7700.lux
        return l

    @property
    def measurement(self) -> int:
        return devices.LUX

    @property
    def units(self) -> str:
        return 'Lux (Lx)'
# END VEML7700

#
# SCD41 (SCD4x) measurements
class Scd41Temperature(MeterInterface):
    def __init__(self, device, i2c: I2C,
                 state: datastructures.State | None = None):
        super().__init__(device, i2c, state)

    @property
    def measure(self) -> float:
        scd = self._device.real_device
        temp = scd.temperature
        return temp

    @property
    def measurement(self) -> int:
        return devices.TEMPERATURE

    @property
    def units(self) -> str:
        return 'Celsius (C)'

class Scd41RelativeHumidity(MeterInterface):
    def __init__(self, device, i2c: I2C,
                 state: datastructures.State | None = None):
        super().__init__(device, i2c, state)

    @property
    def measure(self) -> float:
        scd = self._device.real_device
        rh = scd.relative_humidity
        return rh

    @property
    def measurement(self) -> int:
        return devices.RELATIVE_HUMIDITY

    @property
    def units(self) -> str:
        return 'Percent Relative Humidity (% rH)'

class Scd41CO2(MeterInterface):
    def __init__(self, device, i2c: I2C,
                 state: datastructures.State | None = None):
        super().__init__(device, i2c, state)

    @property
    def measure(self) -> int:
        scd = self._device.real_device
        co2 = scd.CO2
        return co2

    @property
    def measurement(self) -> int:
        return devices.CO2

    @property
    def units(self) -> str:
        return 'Parts per Million (PPM)'
# END SCD41 (SCD4x)

class MeterFactory:
    def __init__(self):
        self._boards = {}

    def register_board(self, board, ctor):
        try:
            dev_board = self._boards[board]
            dev_board['ctor'] = ctor
        except KeyError as e:
            self._board[board] = dict()
            self._board[board]['ctor'] = ctor

    def register_meter(self, board, measurement: int, ctor):
        try:
            dev_board = self._boards[board]
            dev_board[measurement] = ctor
        except KeyError as e:
            self._boards[board] = dict()
            self._boards[board][measurement] = ctor

    def get_meter(self, device, board: int, measurement: int, i2c: I2C,
                  state: datastructures.State | None = None) -> MeterInterface:
        dev_board = self._boards.get(board)
        ctor = dev_board.get(measurement)
        if not ctor:
            raise ValueError('{}:{}'.format(board, measurement))

        return ctor(device, i2c, state)

meter_factory = MeterFactory()
meter_factory.register_meter(devices.BMP390, devices.TEMPERATURE, Bmp390Temperature)
meter_factory.register_meter(devices.BMP390, devices.PRESSURE, Bmp390Pressure)
meter_factory.register_meter(devices.BMP390, devices.ALTITUDE, Bmp390Altitude)
meter_factory.register_meter(devices.SHT41, devices.TEMPERATURE, Sht41Temperature)
meter_factory.register_meter(devices.SHT41, devices.RELATIVE_HUMIDITY, Sht41RelativeHumidity)
meter_factory.register_meter(devices.VEML7700, devices.AMBIENT_LIGHT, Veml7700AmbientLight)
meter_factory.register_meter(devices.VEML7700, devices.LUX, Veml7700Lux)
meter_factory.register_meter(devices.SCD41, devices.TEMPERATURE, Scd41Temperature)
meter_factory.register_meter(devices.SCD41, devices.RELATIVE_HUMIDITY, Scd41RelativeHumidity)
meter_factory.register_meter(devices.SCD41, devices.CO2, Scd41CO2)
