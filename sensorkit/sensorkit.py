from importlib import import_module
import logging
from typing import Any

from anytree import LevelOrderIter
from busio import I2C

from .calibration import Calibration
from .config import Config
from .constants import VIRTUAL
from .datastructures import (devicetypes_selector,
                             deviceids_selector,
)
from .devices import device_factory, DeviceInterface
from .devicetree import DeviceTree
from .tools.mixins import RunnableMixin, SchedulableMixin

logger = logging.getLogger(__name__)

class SensorKit(RunnableMixin):
    def __init__(self, bus: I2C, config: dict[str, Any], scheduler):
        self._bus = bus
        self._config = Config(config)

        self._env = self._config.env

        self._tree = DeviceTree(bus, self._env)
        self._tree.build()
        self._scheduler = scheduler

        self._calibrations = []

        self._static_args = {
            'scheduler': self._scheduler,
        }

        self._virtual_devices = self._config.virtual_devices
        for dev in self._virtual_devices:
            conf = self._virtual_devices[dev]
            objs = self._instantiate_device(dev, conf)

            for d in objs:
                field = devicetypes_selector('type', device=conf['type'])
                if field.found is False:
                    logger.warning('skipping unknown device: %s', conf['type'])
                    continue

                self._tree.add(dev, d, (field.field | VIRTUAL))

        calibrations = self._config.calibrations
        self._build_calibrations(calibrations)

    @property
    def tree(self) -> DeviceTree:
        return self._tree

    def run(self):
        # Order:
        #   Pre:
        #     - SchedulableMixins
        #
        #   Run:
        #     - Runnables
        for cobj in self._calibrations:
            if isinstance(cobj, SchedulableMixin):
                cobj.schedule(True)

        for node in LevelOrderIter(self._tree._root):
            if node.obj is not None and isinstance(node.obj, RunnableMixin):
                node.obj.run()

    def stop(self):
        # Order:
        #   Pre:
        #     - SchedulableMixins
        #
        #   Run:
        #     - Runnables
        for cobj in self._calibrations:
            if isinstance(cobj, SchedulableMixin):
                cobj.unschedule()

        for node in LevelOrderIter(self._tree._root):
            if node.obj is not None and isinstance(node.obj, RunnableMixin):
                node.obj.stop()

    def _build_calibrations(self, calibrations) -> None:
        for c in calibrations:
            capc = c.upper()
            for d in self._tree.devices_iter(
                    lambda n: n.obj.device_id == deviceids_selector('id', device_name=capc).field):
                for conf in calibrations[c]:
                    cobj = Calibration(c, conf, d, self._tree, self._scheduler)
                    self._calibrations.append(cobj)

    def _instantiate_device(self, name: str, config: dict[str, Any]) -> DeviceInterface:
        module = import_module(config['module'], package='sensorkit')

        builder_name = config['builder']
        builder = getattr(module, builder_name)
        build_obj = builder(name, config['capabilities'])

        args = { **self._static_args, **config['args'] }
        objects = build_obj(**args)

        return objects
