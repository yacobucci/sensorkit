import adafruit_bmp3xx
import adafruit_scd4x
import adafruit_sht4x
import adafruit_veml7700
from busio import I2C

NONE = 0x00

# Interfaces
ADAFRUIT = 0x0001
DFROBOT  = 0x0002

# Device interfaces
adafruit = 'adafruit'
dfrobot  = 'dfrobot'

to_interface = dict({
    adafruit: ADAFRUIT,
    dfrobot: DFROBOT
})

# Device Types
PHYSICAL_BUS  = 0x0001
PSUEDO_DEVICE = 0x0002
MUX           = 0x0004
CHANNEL       = 0x0008
DEVICE        = 0x0010
METER         = 0x0020
DETECTOR      = 0x0040

# Type strings
mux      = 'mux'
meter    = 'meter'
detector = 'detector'

to_device_type = dict({
    mux: MUX,
    meter: METER,
    detector: DETECTOR
})

# Capabilities
FOUR_CHANNEL      = 0x0001
EIGHT_CHANNEL     = 0x0002
PRESSURE          = 0x0004
TEMPERATURE       = 0x0008
ALTITUDE          = 0x0010
RELATIVE_HUMIDITY = 0x0020
AMBIENT_LIGHT     = 0x0040
LUX               = 0x0080
CO2               = 0x0100

# Capability Strings
four_channel      = 'four_channel'
eight_channel     = 'eight_channel'
pressure          = 'pressure'
temperature       = 'temperature'
altitude          = 'altitude'
relative_humidity = 'relative_humidity'
ambient_light     = 'ambient_light'
lux               = 'lux'
co2               = 'CO2'

to_capability_strings = dict([
    (FOUR_CHANNEL, four_channel),
    (EIGHT_CHANNEL, eight_channel),
    (PRESSURE, pressure),
    (TEMPERATURE, temperature),
    (ALTITUDE, altitude),
    (RELATIVE_HUMIDITY, relative_humidity),
    (AMBIENT_LIGHT, ambient_light),
    (LUX, lux),
    (CO2, co2)
])

to_capabilities = dict({
    four_channel: FOUR_CHANNEL,
    eight_channel: EIGHT_CHANNEL,
    pressure: PRESSURE,
    temperature: TEMPERATURE,
    altitude: ALTITUDE,
    relative_humidity: RELATIVE_HUMIDITY,
    ambient_light: AMBIENT_LIGHT,
    lux: LUX,
    co2: CO2
})

# Breakout boards
PCA9546A = 0x0001
PCA9548A = 0x0002
TCA9548A = PCA9548A
BMP390   = 0x0003
SHT41    = 0x0004
VEML7700 = 0x0005
SCD41    = 0x0006

to_device_ids = dict({
    'pca9546a': PCA9546A,
    'pca9548a': PCA9548A,
    'tca9548a': TCA9548A,
    'bmp390': BMP390,
    'sht41': SHT41,
    'veml7700': VEML7700,
    'scd41': SCD41
})

# XXX making this a builder eventually make defaults easier and to handle
# conversions between config and settings
#class ProfileBuilder:
#    def __init__(self):
#        pass
#
#    def with_id(self, dev_id: str) -> ProfileBuilder:
#        try:
#            self._name = dev_id.upper()
#            self._device_id = to_device_ids[self._name.lower()]
#        except KeyError as e:
#            raise AttributeError('unsupported device - {}'.format(dev_id))
#        return self
#
#    def with_address(self, addr: int) -> ProfileBuilder:
#        if addr is None or 0 >= addr >= 0x5F:
#            raise AttributeError('unsupported address value - {}'.format(addr))
#
#        self._addr = addr
#        return self
#
#    def with_interface(self, interface: str) -> ProfileBuilder:
#        try:
#            self._interface = to_interface[interface]
#        except KeyError as e:
#            raise AttributeError('unsupported interface - {}'.format(interface))
#        return self
#
#    def with_type(self, typ: str) -> ProfileBuilder:
#        try:
#            self._type = to_device_type[typ.lower()]
#        except KeyError as e:
#            raise AttributeError('unsupported device type - {}'.format(typ))
#        return self
#
#    def with_capabilities(self, caps: list[str]) -> ProfileBuiler:
#        try:
#            self._capabilities = [ to_capabilities[cap] for cap in caps ]
#        except KeyError as e:
#            raise AttributeError('unsupported capability - {}'.format(e))
#        return self
#
#    def build(self) -> DeviceProfile:
#        return DeviceProfile(self._name, self._address, self._device_id, self._capabilities,
#                             self._type, self._interface)

# Device profiles
# XXX can capabilities be AND and OR at some point?
class DeviceProfile:
    def __init__(self, name: str, address: int, device_id: int, capabilities: list[int],
                 typ: int, interface: int = ADAFRUIT):
        self._name = name
        self._address = address
        self._dev_id = device_id
        self._caps = capabilities
        self._type = typ

    
    @property
    def address(self) -> int:
        return self._address

    @property
    def capabilities(self) -> list[int]:
        return self._caps

    def capabilities_gen(self) -> int:
        for cap in self._caps:
            yield cap

    @property
    def name(self) -> str:
        return self._name

    @property
    def device_id(self) -> int:
        return self._dev_id

    @property
    def typ(self) -> int:
        return self._type

    def is_mux(self) -> bool:
        return True if self._type == MUX else False

    def is_meter(self) -> bool:
        return True if self._type == METER else False

    def is_detector(self) -> bool:
        return True if self._type == DETECTOR else False

    def has_capability(self, cap: int) -> bool:
        return True if cap in self._caps else False

pca9546a = DeviceProfile('PCA9546A', 0x70, PCA9546A, [ FOUR_CHANNEL ], MUX)
tca9548a = DeviceProfile('TCA9548A', 0x70, TCA9548A, [ EIGHT_CHANNEL ], MUX)
bmp390 = DeviceProfile('BMP390', 0x77, BMP390, [ PRESSURE, TEMPERATURE, ALTITUDE ], METER)
sht41 = DeviceProfile('SHT41', 0x44, SHT41, [ TEMPERATURE, RELATIVE_HUMIDITY ], METER)
veml7700 = DeviceProfile('VEML7700', 0x10, VEML7700, [ AMBIENT_LIGHT, LUX ], METER)
scd41 = DeviceProfile('SCD41', 0x62, SCD41, [ CO2, RELATIVE_HUMIDITY, TEMPERATURE ], METER)

profiles = dict([
    (0x70, pca9546a),
    (0x77, bmp390),
    (0x44, sht41),
    (0x10, veml7700),
    (0x62, scd41)
])

class DeviceInterface:
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

    def real_device(self):
        pass

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
