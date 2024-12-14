from .constants import *

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
