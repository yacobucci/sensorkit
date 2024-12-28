SensorKit
---------

Work in Progress

Simple abstraction for I2C bus devices.

Installation
------------

- Install adafruit-blinka. Since I2C may need to be enabled on your device you may prefer
to install blinka separately to ensure its setup success.

Some devices do not respond to the scan method used in microcontroller/generic_linux. See [Issue 365](https://github.com/adafruit/Adafruit_Blinka/issues/365).

For this library to discover devices microcontroller/generic_linux/i2c.py needs to be patched with either patch1 (re-implementation of i2cdetect scan algorithm) or patch2 (replace read_byte with write_quick for all addresses).

pip install sensorkit --upgrade
