try:
    from typing import List
    from typing_extensions import Literal
    # XXX Gravity interface may change this - right now CircuitPython specific
    from busio import I2C
except ImportError:
    pass

import adafruit_bmp3xx
import adafruit_sht4x
import adafruit_veml7700

from . import devices

class MeterInterface(devices.DeviceInterface):
    def __init__(self, i2c: I2C):
        self._i2c_bus = i2c

    def bus_id(self) -> int:
        r = 0
        if 'channel_switch' in self._i2c_bus.__dict__:
            n = int.from_bytes(self._i2c_bus.channel_switch, 'little')
            while n > 1:
                n = n >> 1
                r = r + 1
        return r

    def measure(self):
        pass

    def board(self) -> int:
        pass

    def measurement(self) -> int:
        pass

#
# BMP390 based measurements
class Bmp390(MeterInterface):
    def __init__(self, i2c: I2C):
        super().__init__(i2c)

    def board(self) -> int:
        return devices.BMP390

class Bmp390Temperature(Bmp390):
    def __init__(self, i2c: I2C):
        super().__init__(i2c)
        self._bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

    def measure(self) -> float:
        return self._bmp.temperature

    def measurement(self) -> int:
        return devices.TEMPERATURE

class Bmp390Pressure(Bmp390):
    def __init__(self, i2c: I2C):
        super().__init__(i2c)
        self._bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

    def measure(self) -> float:
        return self._bmp.pressure

    def measurement(self) -> int:
        return devices.PRESSURE

class Bmp390Altitude(Bmp390):
    def __init__(self, i2c: I2C):
        super().__init__(i2c)
        self._bmp = adafruit_bmp3xx.BMP3XX_I2C(i2c)

    def measure(self) -> float:
        return self._bmp.altitude

    def measurement(self) -> int:
        return devices.ALTITUDE

    def set_sea_level_pressure(self, msl: float):
        self._bmp.sea_level_pressure = msl
# END BMP390

#
# SHT41 (SHT4x) measurements
class Sht41(MeterInterface):
    def __init__(self, i2c: I2C):
        super().__init__(i2c)

    def board(self) -> int:
        return devices.SHT41

class Sht41Temperature(Sht41):
    def __init__(self, i2c: I2C):
        super().__init__(i2c)
        self._sht = adafruit_sht4x.SHT4x(i2c)

    def measure(self) -> float:
        temp, _ =  self._sht.measurements
        return temp

    def measurement(self) -> int:
        return devices.TEMPERATURE

class Sht41RelativeHumidity(Sht41):
    def __init__(self, i2c: I2C):
        super().__init__(i2c)
        self._sht = adafruit_sht4x.SHT4x(i2c)

    def measure(self) -> float:
        _, rh = self._sht.measurements
        return rh

    def measurement(self) -> int:
        return devices.RELATIVE_HUMIDITY
# END SHT41 (SHT4x)

#
# VEML7700 measurements
class Veml7700(MeterInterface):
    def __init__(self, i2c: I2C):
        super().__init__(i2c)

    def board(self) -> int:
        return devices.VEML7700

class Veml7700AmbientLight(Veml7700):
    def __init__(self, i2c: I2C):
        super().__init__(i2c)
        self._veml7700 = adafruit_veml7700.VEML7700(i2c)

    def measure(self) -> float:
        l = self._veml7700.light
        return l

    def measurement(self) -> int:
        return devices.AMBIENT_LIGHT

class Veml7700Lux(Veml7700):
    def __init__(self, i2c: I2C):
        super().__init__(i2c)
        self._veml7700 = adafruit_veml7700.VEML7700(i2c)

    def measure(self) -> float:
        l = self._veml7700.lux
        return l

    def measurement(self) -> int:
        return devices.LUX
# END VEML7700

class MeterFactory:
    def __init__(self):
        self._boards = {}

    def register_method(self, board, measurement: int, ctor):
        try:
            dev_board = self._boards[board]
            dev_board[measurement] = ctor
        except KeyError as e:
            self._boards[board] = dict()
            self._boards[board][measurement] = ctor

    def get_meter(self, board, measurement: int, i2c: I2C) -> MeterInterface:
        dev_board = self._boards.get(board)
        ctor = dev_board.get(measurement)
        if not ctor:
            raise ValueError('{}:{}'.format(board, measurement))

        return ctor(i2c)

meter_factory = MeterFactory()
meter_factory.register_method(devices.BMP390, devices.TEMPERATURE, Bmp390Temperature)
meter_factory.register_method(devices.BMP390, devices.PRESSURE, Bmp390Pressure)
meter_factory.register_method(devices.BMP390, devices.ALTITUDE, Bmp390Altitude)
meter_factory.register_method(devices.SHT41, devices.TEMPERATURE, Sht41Temperature)
meter_factory.register_method(devices.SHT41, devices.RELATIVE_HUMIDITY, Sht41RelativeHumidity)
meter_factory.register_method(devices.VEML7700, devices.AMBIENT_LIGHT, Veml7700AmbientLight)
meter_factory.register_method(devices.VEML7700, devices.LUX, Veml7700Lux)
