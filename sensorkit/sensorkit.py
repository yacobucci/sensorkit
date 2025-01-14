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
                             Store,
)
from .devices import device_factory, DeviceInterface
from .devicetree import DeviceTree
from .tools.mixins import RunnableMixin, SchedulableMixin

logger = logging.getLogger(__name__)

class SensorKit(RunnableMixin):
    def __init__(self, bus: I2C, config: dict[str, Any], scheduler,
                 store: dict[str, Any] | None = None):
        self._bus = bus
        self._config = Config(config)

        self._env = self._config.env

        self._store = Store(store)
        self._store.tree = DeviceTree(bus, self._store, self._env)
        self._store.tree.build()
        self._scheduler = scheduler

        self._calibrations = []

        self._static_args = {
            'store': self._store,
            'scheduler': self._scheduler,
        }

        self._virtual_devices = self._config.virtual_devices
        for dev in self._virtual_devices:
            conf = self._virtual_devices[dev]
            objs = self._instantiate_device(conf)

            for d in objs:
                field = devicetypes_selector('type', device=conf['type'])
                if field.found is False:
                    logger.warning('skipping unknown device: %s', conf['type'])
                    continue

                self._store.tree.add(dev, d, (field.field | VIRTUAL))

        calibrations = self._config.calibrations
        self._build_calibrations(calibrations)

    @property
    def tree(self) -> DeviceTree:
        return self._store.tree

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

        for node in LevelOrderIter(self._store.tree._root):
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

        for node in LevelOrderIter(self._store.tree._root):
            if node.obj is not None and isinstance(node.obj, RunnableMixin):
                node.obj.stop()

    def _build_calibrations(self, calibrations) -> None:
        for c in calibrations:
            for d in self._store.tree.devices_iter(
                    lambda node: node.obj.board == deviceids_selector('id', device_name=c).field):
                for conf in calibrations[c]:
                    cobj = Calibration(c, conf, d, self._store, self._scheduler)
                    self._calibrations.append(cobj)

    def _instantiate_device(self, config: dict[str, Any]) -> DeviceInterface:
        module = import_module(config['module'], package='sensorkit')

        builder_name = config['builder']
        builder = getattr(module, builder_name)
        build_obj = builder(config['capabilities'])

        args = { **self._static_args, **config['args'] }
        objects = build_obj(**args)

        return objects
