NONE = 0x00

# Device Types
SENSOR = 0x01
CONTROL = 0x02

# SubTypes
MUX = 0x01
METER = 0x02

# Multiplexer capacities
FOUR_CHANNEL  = 0x01
EIGHT_CHANNEL = 0x02

# Meters
PRESSURE    = 0x01
TEMPERATURE = 0x02
ALTITUDE    = 0x04

# Breakout boards
PCA9546A = 0x01
PCA9548A = 0x02
TCA9548A = PCA9548A
BMP390   = 0x03

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

device_types = dict([
    (0x70, pca9546a),
    (0x77, bmp390)
])
