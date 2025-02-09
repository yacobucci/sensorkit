import RPi.GPIO as GPIO

NONE = 0x00

# Addresses
VIRTUAL_ADDR = 0xFF

# Device Types
VIRTUAL       = 0x80000000

# Non-composable types
BUS           = 0x0001
MUX           = 0x0002
CHANNEL       = 0x0003
DEVICE        = 0x0004

# Composable types
METER         = 0x100
DETECTOR      = 0x200

# Capabilities
FOUR_CHANNEL            = 0x0001
EIGHT_CHANNEL           = 0x0002
PRESSURE                = 0x0004
TEMPERATURE             = 0x0008
ALTITUDE                = 0x0010
RELATIVE_HUMIDITY       = 0x0020
AMBIENT_LIGHT           = 0x0040
LUX                     = 0x0080
VISIBLE                 = 0x0100
INFRARED                = 0x0200
FULL_SPECTRUM           = 0x0400
CO2                     = 0x0800
PRESSURE_MSL            = 0x1000

# Units
CELSIUS_UNITS                = 'Celsius (C)'
HECTOPASCAL_UNITS            = 'Hectopascal (hPa)'
METER_UNITS                  = 'Meter (M)'
PERC_RELATIVE_HUMIDITY_UNITS = 'Percent Relative Humidity (% rH)'
AMBIENT_LIGHT_UNITS          = 'Ambient Light Data'
LUX_UNITS                    = 'Lux (Lx)'
PPM_UNITS                    = 'Parts per Million (PPM)'

# Breakout boards / DeviceIDs
VIRTUAL_DEVICE = 0xFFFF
PCA9546A       = 0x0001
PCA9548A       = 0x0002
TCA9548A       = PCA9548A
BMP390         = 0x0003
SHT41          = 0x0004
VEML7700       = 0x0005
SCD41          = 0x0006
TSL2591        = 0x0007

# Detectors
EDGE_FALLING = GPIO.FALLING
EDGE_RISING = GPIO.RISING
EDGE_BOTH = GPIO.BOTH

PULL_UP = GPIO.PUD_UP
PULL_DOWN = GPIO.PUD_DOWN
PULL_OFF = GPIO.PUD_OFF
