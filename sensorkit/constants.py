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
