NONE = 0x00

# Device Types
SENSOR  = (0x0001 << 32)
CONTROL = (0x0002 << 32)

# SubTypes
MUX      = 0x0001
METER    = 0x0002
DETECTOR = 0x0004

# Multiplexer capacities
FOUR_CHANNEL  = 0x01
EIGHT_CHANNEL = 0x02

# Meters
PRESSURE          = 0x0001
TEMPERATURE       = 0x0002
ALTITUDE          = 0x0004
RELATIVE_HUMIDITY = 0x0008
AMBIENT_LIGHT     = 0x0010
LUX               = 0x0020
CO2               = 0x0040

measurements = dict([
    (PRESSURE, 'pressure'),
    (TEMPERATURE, 'temperature'),
    (ALTITUDE, 'altitude'),
    (RELATIVE_HUMIDITY, 'relative_humidity'),
    (AMBIENT_LIGHT, 'ambient_light'),
    (LUX, 'lux'),
    (CO2, 'CO2')
])

# Breakout boards
PCA9546A = 0x0001
PCA9548A = 0x0002
TCA9548A = PCA9548A
BMP390   = 0x0003
SHT41    = 0x0004
VEML7700 = 0x0005
SCD41    = 0x0006

# Device profiles
# XXX can capabilities be AND and OR at some point?
class DeviceProfile:
    def __init__(self, name: str, address: int, device_id: int, capabilities: list[int],
                 typ: int, subtype: int):
        self._name = name
        self._address = address
        self._dev_id = device_id
        self._caps = capabilities
        self._type = typ
        self._subtype = subtype

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

    @property
    def subtype(self) -> int:
        return self._subtype

    def is_mux(self) -> bool:
        return True if self._type == CONTROL and self._subtype == MUX else False

    def is_sensor(self) -> bool:
        return True if self._type == SENSOR else False

    def is_detector(self) -> bool:
        return True if self._type == DETECTOR else False

    def has_capability(self, cap: int) -> bool:
        return True if cap in self._caps else False

pca9546a = DeviceProfile('PCA9546A', 0x70, PCA9546A, [ FOUR_CHANNEL ], CONTROL, MUX)
bmp390 = DeviceProfile('BMP390', 0x77, BMP390, [ PRESSURE, TEMPERATURE, ALTITUDE ], SENSOR, METER)
sht41 = DeviceProfile('SHT41', 0x44, SHT41, [ TEMPERATURE, RELATIVE_HUMIDITY ], SENSOR, METER)
veml7700 = DeviceProfile('VEML7700', 0x10, VEML7700, [ AMBIENT_LIGHT, LUX ], SENSOR, METER)
scd41 = DeviceProfile('SCD41', 0x62, SCD41, [ CO2, RELATIVE_HUMIDITY, TEMPERATURE ], SENSOR, METER)

device_types = dict([
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
    def address(self) -> int:
        return hex(self._device_profile.address)

    @property
    def board(self) -> int:
        return self._device_profile.device_id

    @property
    def name(self) -> str:
        return self._device_profile.name
