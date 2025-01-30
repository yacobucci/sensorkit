import logging
from collections.abc import Iterator
from typing import Any

import board
from busio import I2C

from . import constants
from . import controls
from . import datastructures
from . import devices
from . import meters
from . import profiles
from .tools.mixins import NodeMixin

logger = logging.getLogger(__name__)

class DeviceTree:
    def __init__(self, i2c: I2C, env: dict[str, Any] | None = None):
        self._i2c = i2c
        self._env = env

    def build(self) -> None:
        self._build_tree(self._i2c, None, self._env)

    def add(self, obj: NodeMixin | None, kind: int, parent: NodeMixin | None):
        datastructures.links.insert({'node': obj.uuid,
                                     'parent': parent.uuid if parent is not None else '__none__'})
        datastructures.nodes.insert({'uuid': obj.uuid, 'kind': kind, 'obj': obj,
                                     'is_virtual': bool(kind & constants.VIRTUAL)})

        match kind:
            case constants.MUX:
                datastructures.multiplexer_attributes.insert(obj)
            case constants.CHANNEL:
                datastructures.channel_attributes.insert(obj)
            case constants.DEVICE:
                datastructures.device_attributes.insert(obj)
            case constants.METER:
                datastructures.meter_attributes.insert(obj)
            case _:
                if bool(kind & (constants.VIRTUAL | constants.METER)):
                    datastructures.virtual_attributes.insert(
                            {'uuid': obj.uuid, 'name': obj.name, 'measurement': obj.measurement,
                             'capability': obj._capability})
                else:
                    raise ValueError('unsupported kind {}'.format(kind))

    def _build_tree(self, i2c, parent: NodeMixin | None, env: dict[str, Any] | None = None,
                    addr_filter: set = set()):
        try:
            if i2c.try_lock():
                devs = i2c.scan()
            i2c.unlock()
        except AttributeError:
            devs = i2c.scan()

        logger.debug('initial scan results: %s, applying filter: %s',
                     [hex(n) for n in devs],
                     [hex(n) for n in addr_filter])

        devs = [n for n in devs if n not in addr_filter]

        for addr in devs:
            logger.info('building node for address: %s', hex(addr))

            try:
                record = profiles.profile_selector(address=addr)
                if record.found is False:
                    message = 'bus scan reports unsupported address {}, continuing...'.format(
                        hex(addr))
                    logger.warning(message)
                    continue

                self._build_node(i2c, addr, record.record, parent, env)
            except Exception as e:
                message = 'bus scan raised exception, {}'.format(e)
                logger.warning(message)

    def _build_node(self, i2c, address, profile, parent: NodeMixin | None,
                    env: dict[str, Any] | None = None):
        if profile.is_mux():
            logger.info('multiplexer %s found at addr %s, setting up multiple channels',
                        profile.name, hex(address))

            mux = controls.mux_factory.get_mux(i2c, profile.name, profile.device_id,
                                               profile.capabilities, address)
            logger.info('multiplexer supported channels: %s', len(mux))

            self.add(mux, constants.MUX, None)

            for channel in mux.channels():
                self.add(channel, constants.CHANNEL, mux)

                addr_set = set()
                addr_set.add(mux.address)
                self._build_tree(channel, channel, env, addr_set)
        else:
            dev = devices.device_factory.get_device(i2c, profile.name, profile.device_id,
                                                    address, env)

            self.add(dev, constants.DEVICE, parent)
            self._build_leaves(i2c, dev)

    def _build_leaves(self, i2c, parent):
        # XXX only do this for meters, eventually need to discriminate with detectors
        for cap in parent.capabilities_gen():
            try:
                m = meters.Meter(parent, cap)
                self.add(m, constants.METER, parent)
            except ValueError as e:
                capstr = datastructures.capabilities_selector('capability', id=cap)
                logger.warning('name %s, device_id %s, capability %s - no ctor',
                               device.name, device.device_id, capstr.field)
