import logging
from typing import Any

from ..constants import VIRTUAL_DEVICE
from ..datastructures import (
        capabilities_selector,
)
from ..devices import VirtualDevice
from ..meters import Meter

logger = logging.getLogger(__name__)

class StaticDevice(Meter):
    def __init__(self, capability: str, value: Any, units: str):
        self._id = capabilities_selector('id', capability=capability)
        super().__init__(VirtualDevice(None, 'static-virtual', VIRTUAL_DEVICE,
                                       [ self._id ]))
        self._capability = capability
        self._value = value
        self._units = units

    @property
    def measure(self) -> Any:
        return self._value

    @property
    def measurement(self) -> int:
        return self._id
    
    @property
    def units(self) -> str:
        return self._units

    @property
    def real_device(self):
        return None

class StaticBuilder:
    def __init__(self, capabilities: list[str]):
        self._caps = capabilities

    def __call__(self, values: dict[str, dict[str, Any]], **_ignored):
        devs = []
        for cap in self._caps:
            if cap not in values:
                raise ValueError('need value for capability {}'.format(cap))

            value = values[cap]
            if 'value' not in value or 'units' not in value:
                raise ValueError('need value and units for capability {}'.format(cap))


            obj = StaticDevice(cap, value['value'], value['units'])
            devs.append(obj)

        return devs
