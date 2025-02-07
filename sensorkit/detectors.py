import abc
import logging
import typing

import RPi.GPIO as GPIO
from adafruit_tsl2591 import ENABLE_NPAIEN, CLEAR_ALL_INTERRUPTS

from . import constants
from .devices import Device
from .datastructures import join_devices
from .devicetree import DeviceTree
from .tools.mixins import NodeMixin

logger = logging.getLogger(__name__)

class DetectorInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'pin') and
                callable(subclass.pin) and
                hasattr(subclass, 'resistor') and
                callable(subclass.resistor) and
                hasattr(subclass, 'edge') and
                callable(subclass.edge) and
                hasattr(subclass, 'address') and
                callable(subclass.address) and
                hasattr(subclass, 'device_id') and
                callable(subclass.device_id) and
                hasattr(subclass, 'name') and
                callable(subclass.name) and
                hasattr(subclass, 'channel_id') and
                callable(subclass.channel_id) and
                hasattr(subclass, 'enable') and
                callable(subclass.enable) and
                hasattr(subclass, 'disable') and
                callable(subclass.disable) and
                hasattr(subclass, 'clear') and
                callable(subclass.clear) and
                hasattr(subclass, 'device') and
                callable(subclass.devcie) or
                NotImplemented)

    @abc.abstractmethod
    def pin(self) -> float:
        raise NotImplementedError

    @abc.abstractmethod
    def resistor(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def edge(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def address(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def device_id(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def channel_id(self) -> int:
        raise NotImplementedError

    @abc.abstractmethod
    def device(self) -> Device:
        raise NotImplementedError

class Detector(DetectorInterface):
    def __init__(self, device: Device, pin: int, resistor: int, edge: int, on_detection: callable):
        super().__init__()
        self._device = device
        self._pin = pin
        self._resistor = resistor
        self._edge = edge

        self._address = self._device.address
        self._device_id = self._device.device_id
        self._name = self._device.name
        self._channel_id = self._device.channel_id
        self._has_channel = self._device.has_channel

        if callable(on_detection) is False:
            raise ValueError('callback must be callable')
        self._on_detection = on_detection

    def __call__(self, channel):
        logger.debug("called in Detector wrapper")
        self._on_detection(self, channel)

    @property
    def address(self) -> int:
        return self._device._address

    @property
    def device_id(self) -> int:
        return self._device._device_id

    @property
    def name(self) -> str:
        return self._device._name

    @property
    def channel_id(self) -> int:
        return self._device._channel_id

    @property
    def pin(self) -> float:
        return self._pin

    @property
    def resistor(self) -> int:
        return self._resistor

    @property
    def edge(self) -> str:
        return self._edge

    @property
    def device(self) -> Device:
        return self._device

class Tsl2591Detector(NodeMixin, Detector):
    def __init__(self, device, pin: int, resistor: int, edge: int, on_detection: callable):
        super().__init__(device, pin, resistor, edge, on_detection)

        self._enabled = False

    def enable(self):
        if self._enabled is False:
            GPIO.setup(self._pin, GPIO.IN, pull_up_down=self._resistor)
            GPIO.add_event_detect(self._pin, self._edge, callback=self)

            self._device.real_device.enable_interrupt(ENABLE_NPAIEN)
            self._enabled = True

    def disable(self):
        if self._enabled is True:
            self._device.real_device.disable_interrupt(ENABLE_NPAIEN)

            GPIO.cleanup()
            self._enabled = False

    def clear(self):
        self._device.real_device.clear_interrupt(CLEAR_ALL_INTERRUPTS)

class DetectorFactory:
    def __init__(self):
        self._ctors = {}

    def register_detector(self, device_id, ctor):
        self._ctors[device_id] = ctor

    def get_detector(self, pin: int, resistor: int, edge: int, on_detection: callable,
                     **kwargs) -> [ list[DetectorInterface] | None]:
        devices = join_devices()
        records = devices.where(**kwargs)
        if len(records) == 0:
            return None

        logger.debug('found matching devices ({}): {}'.format(len(records), records))

        detectors = [None] * len(records)
        for i, record in enumerate(records):
            detectors[i] = self._ctors[record.device_id](record.obj, pin, resistor, edge,
                                                         on_detection)

        return detectors

detector_factory = DetectorFactory()
detector_factory.register_detector(constants.TSL2591, Tsl2591Detector)

def make_detector(pin: int, resistor: int, edge: int, on_detection: callable,
                  tree: [DeviceTree | None] = None, **kwargs) -> [list[DetectorInterface] | None]:
    detectors = detector_factory.get_detector(pin, resistor, edge, on_detection, **kwargs)

    if tree is not None:
        for detector in detectors:
            tree.add(detector, constants.DETECTOR, detector.device)
            logger.debug('added Detector %s:%s:%s to device tree', detector.name, detector.address,
                         detector.channel_id)
    else:
        logger.debug('no devicetree provided - detectors are not searchable')

    return detectors
