from dataclasses import dataclass
import logging

import littletable as db

from .constants import *
from .datastructures import UniqueRecordByWhere

logger = logging.getLogger(__name__)

# Device profiles
@dataclass
class DeviceProfile:
    name: str
    address: int
    device_id: int
    capabilities: list[int]
    typ: int
    interface: int = ADAFRUIT

    def is_mux(self) -> bool:
        return True if self.typ == MUX else False

    def is_meter(self) -> bool:
        return True if self.typ == METER else False

    def is_detector(self) -> bool:
        return True if self.typ == DETECTOR else False

    def has_capability(self, cap: int) -> bool:
        return True if cap in self.capabilities else False

profiles = db.Table('profiles')
profiles.insert(DeviceProfile('PCA9546A', 0x70, PCA9546A, [ FOUR_CHANNEL ], MUX))
# FIXME need discovery discrimination before this will work
#profiles.insert(DeviceProfile('TCA9548A', 0x70, TCA9548A, [ EIGHT_CHANNEL ], MUX))
profiles.insert(DeviceProfile('BMP390', 0x77, BMP390, [ PRESSURE, TEMPERATURE, ALTITUDE ], METER))
profiles.insert(DeviceProfile('SHT41', 0x44, SHT41, [ TEMPERATURE, RELATIVE_HUMIDITY ], METER))
profiles.insert(DeviceProfile('VEML7700', 0x10, VEML7700, [ AMBIENT_LIGHT, LUX ], METER))
profiles.insert(DeviceProfile('SCD41', 0x62, SCD41, [ CO2, RELATIVE_HUMIDITY, TEMPERATURE ], METER))
profiles.insert(DeviceProfile('TSL2591', 0x29, TSL2591,
                              [ LUX, FULL_SPECTRUM, VISIBLE, INFRARED, AMBIENT_LIGHT ], METER))

profiles.create_index('name')
profiles.create_index('address')
profiles.create_index('device_id')
profile_selector = UniqueRecordByWhere(profiles)
