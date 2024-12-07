NONE = 0x00

# Device Types
SENSOR  = 0x00000001
CONTROL = 0x00000002

# SubTypes
MUX   = 0x00010000
METER = 0x00020000

# Multiplexer capacities
FOUR_CHANNEL  = 0x01
EIGHT_CHANNEL = 0x02

# Meters
PRESSURE          = 0x00000001
TEMPERATURE       = 0x00000002
ALTITUDE          = 0x00000004
RELATIVE_HUMIDITY = 0x00000008
AMBIENT_LIGHT     = 0x00000010
LUX               = 0x00000020

# Breakout boards
PCA9546A = 0x01
PCA9548A = 0x02
TCA9548A = PCA9548A
BMP390   = 0x03
SHT41    = 0x04
VEML7700 = 0x05

# Device profiles
# XXX can capabilities be AND and OR at some point?
pca9546a = {
    'address': 0x70,
    'name': 'PCA9546A',
    'id': PCA9546A,
    'capabilities': [ FOUR_CHANNEL ],
    'type': CONTROL,
    'subtype': MUX
}

bmp390 = {
    'address': 0x77,
    'name': 'BMP390',
    'id': BMP390,
    'capabilities': [ PRESSURE, TEMPERATURE, ALTITUDE ],
    'type': SENSOR,
    'subtype': METER
}

sht41 = {
    'address': 0x44,
    'name': 'SHT41',
    'id': SHT41,
    'capabilities': [ TEMPERATURE, RELATIVE_HUMIDITY ],
    'type': SENSOR,
    'subtype': METER
}

veml7700 = {
    'address': 0x10,
    'name': 'VEML7700',
    'id': VEML7700,
    'capabilities': [ AMBIENT_LIGHT, LUX ],
    'type': SENSOR,
    'subtype': METER
}

device_types = dict([
    (0x70, pca9546a),
    (0x77, bmp390),
    (0x44, sht41),
    (0x10, veml7700)
])

class DeviceInterface:
    def address(self) -> int:
        pass

    def board(self) -> int:
        pass
