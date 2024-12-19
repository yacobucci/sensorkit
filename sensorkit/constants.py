NONE = 0x00

# Addresses
VIRTUAL_ADDR = 0xFF

# Interfaces
ADAFRUIT = 0x0001
DFROBOT  = 0x0002

# Device interfaces
adafruit = 'adafruit'
dfrobot  = 'dfrobot'

to_interface = dict({
    adafruit: ADAFRUIT,
    dfrobot:  DFROBOT
})

# Device Types
VIRTUAL       = 0x80000000

BUS           = 0x0001
MUX           = 0x0002
CHANNEL       = 0x0004
DEVICE        = 0x0008
METER         = 0x0010
DETECTOR      = 0x0020

# Type strings
mux      = 'mux'
meter    = 'meter'
detector = 'detector'

to_device_type = dict({
    mux:      MUX,
    meter:    METER,
    detector: DETECTOR
})

# Capabilities
FOUR_CHANNEL            = 0x0001
EIGHT_CHANNEL           = 0x0002
PRESSURE                = 0x0004
TEMPERATURE             = 0x0008
ALTITUDE                = 0x0010
RELATIVE_HUMIDITY       = 0x0020
AMBIENT_LIGHT           = 0x0040
LUX                     = 0x0080
CO2                     = 0x0100
PRESSURE_MSL            = 0x0200

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
pressure_msl      = 'pressure_msl'

to_capability_strings = dict([
    (FOUR_CHANNEL,            four_channel),
    (EIGHT_CHANNEL,           eight_channel),
    (PRESSURE,                pressure),
    (TEMPERATURE,             temperature),
    (ALTITUDE,                altitude),
    (RELATIVE_HUMIDITY,       relative_humidity),
    (AMBIENT_LIGHT,           ambient_light),
    (LUX,                     lux),
    (CO2,                     co2),
    (PRESSURE_MSL,            pressure_msl),
])

to_capabilities = dict({
    four_channel:      FOUR_CHANNEL,
    eight_channel:     EIGHT_CHANNEL,
    pressure:          PRESSURE,
    temperature:       TEMPERATURE,
    altitude:          ALTITUDE,
    relative_humidity: RELATIVE_HUMIDITY,
    ambient_light:     AMBIENT_LIGHT,
    lux:               LUX,
    co2:               CO2,
    pressure_msl:      PRESSURE_MSL,
})

# Units
CELSIUS_UNITS                = 'Celsius (C)'
HECTOPASCAL_UNITS            = 'Hectopascal (hPa)'
METER_UNITS                  = 'Meter (M)'
PERC_RELATIVE_HUMIDITY_UNITS = 'Percent Relative Humidity (% rH)'
AMBIENT_LIGHT_UNITS          = 'Ambient Light Data'
LUX_UNITS                    = 'Lux (Lx)'
PPM_UNITS                    = 'Parts per Million (PPM)'

# Breakout boards
VIRTUAL_DEVICE = NONE
PCA9546A       = 0x0001
PCA9548A       = 0x0002
TCA9548A       = PCA9548A
BMP390         = 0x0003
SHT41          = 0x0004
VEML7700       = 0x0005
SCD41          = 0x0006

to_device_ids = dict({
    'virtual':  VIRTUAL_DEVICE,
    'pca9546a': PCA9546A,
    'pca9548a': PCA9548A,
    'tca9548a': TCA9548A,
    'bmp390':   BMP390,
    'sht41':    SHT41,
    'veml7700': VEML7700,
    'scd41':    SCD41
})
