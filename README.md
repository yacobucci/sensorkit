SensorKit
---------

Work in Progress

Simple abstraction for I2C bus devices.

Installation
------------

- Install adafruit-blinka. Since I2C may need to be enabled on your device you may prefer
to install blinka separately to ensure its setup success. See [CircuitPython Libraries on Linux and Raspberry Pi](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi).

Some devices do not respond to the scan method used in microcontroller/generic_linux. See [Issue 365](https://github.com/adafruit/Adafruit_Blinka/issues/365).

For this library to discover devices microcontroller/generic_linux/i2c.py needs to be patched with either patches/i2c-read-or-write.patch (re-implementation of i2cdetect scan algorithm) or i2c-write.patch (replace read_byte with write_quick for all addresses).

pip install sensorkit --upgrade

Usage
-----

[WIP]

```
from sensorkit import SensorKit

kit = SensorKit(board.I2C(), config)
kit.run()

for m in kit.tree.meters_iter:
    print m.measure
```
