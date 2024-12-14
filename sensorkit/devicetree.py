import logging

from anytree import Node, PreOrderIter
import board
from busio import I2C

from . import controls
from . import datastructures
from . import devices
from . import meters

logger = logging.getLogger(__name__)

class Metadata:
    def __init__(self, device_type: int):
        self._device_type = device_type

    @property
    def is_bus(self) -> bool:
        return self._device_type & devices.PHYSICAL_BUS
        
    @property
    def is_mux(self) -> bool:
        return self._device_type & devices.MUX

    @property
    def is_channel(self) -> bool:
        return self._device_type & devices.CHANNEL

    @property
    def is_device(self) -> bool:
        return self._device_type & devices.DEVICE

    @property
    def is_meter(self) -> bool:
        return self._device_type & devices.METER

    @property
    def is_detector(self) -> bool:
        return self._device_type & devices.DETECTOR

class DeviceTree:
    def __init__(self, i2c: I2C, state: datastructures.StateInterface):
        self._state = state
        self._i2c = i2c

        self._root = Node('main-bus', obj=self._i2c, metadata=Metadata(devices.PHYSICAL_BUS))

        self._build_tree(self._i2c, self._root)

    # XXX eventually make this a little more generic
    def meters(self) -> meters.MeterInterface:
        def __filter(node: Node) -> bool:
            meta = getattr(node, 'metadata', None)
            if meta is not None:
                return meta.is_meter
            return False
        for node in PreOrderIter(self._root, __filter):
            yield node.obj

    def _build_tree(self, i2c, parent, addr_filter: set = set()):
        try:
            if i2c.try_lock():
                devs = i2c.scan()
            i2c.unlock()
        except AttributeError:
            devs = i2c.scan()

        logger.debug('initial scan results: %s',
                     [hex(n) for n in devs],
                     [hex(n) for n in addr_filter])

        devs = [n for n in devs if n not in addr_filter]

        for addr in devs:
            logger.info('building node for address: %s', addr)

            d = devices.profiles[addr]

            self._build_node(i2c, d, parent)

    def _build_node(self, i2c, profile, parent):
        if profile.is_mux():
            logger.info('multiplexer %s found at addr %s, setting up multiple channels',
                        profile.name, hex(profile.address))

            mux = controls.mux_factory.get_mux(profile.device_id, i2c)
            logger.info('multiplexer supported channels: %s', len(mux))

            node = Node(profile.address, parent=parent, obj=mux,
                        metadata=Metadata(devices.MUX))
            
            def channel_bus(channel) -> int:
                r = 0
                if 'channel_switch' in channel.__dict__:
                    n = int.from_bytes(channel.channel_switch, 'little')
                    while n > 1:
                        n = n >> 1
                        r = r + 1
                return r
            for channel in mux.channels():
                chan = Node(channel_bus(channel), parent=node, obj=channel,
                            metadata=Metadata(devices.CHANNEL))
                addr_set = set()
                addr_set.add(mux.address)
                self._build_tree(channel, chan, addr_set)
        else:
            dev = devices.device_factory.get_device(profile.device_id, profile, i2c)
            node = Node(profile.address, parent=parent, obj=dev,
                        metadata=Metadata(devices.DEVICE))
            self._build_leaves(i2c, profile, dev, node)

    def _build_leaves(self, i2c, profile, device, parent):
        # XXX only do this for meters, eventually need to discriminate with detectors
        for cap in profile.capabilities_gen():
            try:
                m = meters.meter_factory.get_meter(device, device.board, cap, i2c, self._state)
                leaf = Node(devices.to_capability_strings[cap], parent=parent, obj=m,
                            metadata=Metadata(devices.METER))
            except ValueError as e:
                logger.warning('name %s, board %s, capability %s - no ctor',
                               profile.name, profile.device_id, cap)
