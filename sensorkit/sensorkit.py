from importlib import import_module
import logging
from typing import Any

from busio import I2C

from .calibration import Calibration
from .config import Config
from .constants import VIRTUAL
from .datastructures import (
        join_devices,
        devicetypes_selector,
        nodes,
)
from .devices import device_factory, DeviceInterface
from .devicetree import DeviceTree
from .tools.mixins import RunnableInterface, SchedulableInterface

logger = logging.getLogger(__name__)

class SensorParameters(RunnableInterface):
    def __init__(self, reset_at_exit: bool | None, selectors: dict[str, Any],
                 parameters: dict[str, dict[str, Any]]):
        self._reset = reset_at_exit if (reset_at_exit is not None and
                                        reset_at_exit is True) else False
        self._selectors = None
        self._parameters = None

        if selectors is not None:
            self._selectors = selectors
            if 'name' in self._selectors:
                self._selectors['name'] = self._selectors['name'].upper()

            if 'channel_id' in self._selectors:
                self._selectors['has_channel'] = True
        else:
            raise ValueError('selectors cannot be None')

        if parameters is not None:
            self._parameters = parameters

    @property
    def selectors(self) -> dict[str, Any]:
        return self._selectors

    @property
    def parameter(self) -> dict[str, Any]:
        return self._parameters

    def pre_run(self):
        devices = join_devices()

        for device in devices.where(**self._selectors):
            chan = device.channel_id if device.has_channel is True else '-'
            logger.info('applying config to device {} {} {}'.format(device.name,
                                                                    device.address,
                                                                    chan))
            dev = device.obj
            for param in self._parameters:
                if hasattr(dev.real_device, param['property']):
                    param['saved_value'] = getattr(dev.real_device, param['property'])
                    setattr(dev.real_device, param['property'], param['value'])

    def run(self):
        pass

    def stop(self):
        devices = join_devices()

        for device in devices.where(**self._selectors):
            chan = device.channel_id if device.has_channel is True else '-'
            logger.info('reseting startup config on device {} {} {}'.format(device.name,
                                                                            device.address,
                                                                            chan))
            dev = device.obj
            for param in self._parameters:
                if hasattr(dev.real_device, param['property']):
                    setattr(dev.real_device, param['property'], param['saved_value'])

class SensorKit(RunnableInterface):
    def __init__(self, bus: I2C, config: dict[str, Any], scheduler):
        self._bus = bus
        self._config = Config(config)

        self._env = self._config.env

        self._tree = DeviceTree(bus, self._env)
        self._tree.build()
        self._scheduler = scheduler

        self._listeners = []

        self._static_args = {
            'scheduler': self._scheduler,
        }

        for sensor in self._config.sensors:
            logger.info('preparing sensor config for application {}'.format(sensor))
            self.register_listener(SensorParameters(**sensor))

        self._virtual_devices = self._config.virtual_devices
        for dev in self._virtual_devices:
            conf = self._virtual_devices[dev]
            objs = self._instantiate_device(dev, conf)

            for d in objs:
                field = devicetypes_selector('type', device=conf['type'])
                if field.found is False:
                    logger.warning('skipping unknown device: %s', conf['type'])
                    continue

                self._tree.add(d, (field.field | VIRTUAL), None)

        calibrations = self._config.calibrations
        self._build_calibrations(calibrations)

    def register_listener(self, obj: [RunnableInterface | SchedulableInterface]):
        if not isinstance(obj, RunnableInterface) and not isinstance(obj, SchedulableInterface):
            raise ValueError('must be a RunnableInterface or SchedulableInterface')
        self._listeners.append(obj)

    @property
    def tree(self) -> DeviceTree:
        return self._tree

    def run(self):
        # Order:
        #   Pre:
        #     - SchedulableInterfaces
        #
        #   Run:
        #     - Runnables
        for obj in self._listeners:
            if isinstance(obj, SchedulableInterface):
                obj.schedule(True)
        for obj in self._listeners:
            if isinstance(obj, RunnableInterface):
                obj.pre_run()
                obj.run()

        for node in nodes:
            if node.obj is not None and isinstance(node.obj, RunnableInterface):
                node.obj.run()

    def stop(self):
        # Order:
        #   Pre:
        #     - SchedulableInterfaces
        #
        #   Run:
        #     - Runnables
        for obj in self._listeners:
            if isinstance(obj, SchedulableInterface):
                obj.unschedule()
        for obj in self._listeners:
            if isinstance(obj, RunnableInterface):
                obj.stop()

        for node in nodes:
            if node.obj is not None and isinstance(node.obj, RunnableInterface):
                node.obj.stop()

    def _build_calibrations(self, calibrations) -> None:
        for c in calibrations:
            for d in join_devices().where(name=c.upper()):
                for conf in calibrations[c]:
                    cobj = Calibration(c, conf, d.obj, self._tree, self._scheduler)
                    self.register_listener(cobj)

    def _instantiate_device(self, name: str, config: dict[str, Any]) -> DeviceInterface:
        module = import_module(config['module'], package='sensorkit')

        builder_name = config['builder']
        builder = getattr(module, builder_name)
        build_obj = builder(name, config['capabilities'])

        args = { **self._static_args, **config['args'] }
        objects = build_obj(**args)

        return objects
