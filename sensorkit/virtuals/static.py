import logging
from typing import Any

from ..constants import (VIRTUAL_DEVICE,
                         to_capabilities,
)
from ..datastructures import Store
from ..devices import VirtualDevice
from ..meters import Meter

logger = logging.getLogger(__name__)

class StaticDevice(Meter):
    def __init__(self, capability: str, value: Any, units: str):
        super().__init__(VirtualDevice(None, 'static-virtual', VIRTUAL_DEVICE,
                                       [ to_capabilities[capability] ]))
        self._capability = capability
        self._value = value
        self._units = units

    @property
    def measure(self) -> Any:
        return self._value

    @property
    def measurement(self) -> int:
        return to_capabilities[self._capability]
    
    @property
    def units(self) -> str:
        return self._units

    @property
    def real_device(self):
        return None

class StaticBuilder:
    def __init__(self, capabilities: list[str]):
        self._caps = capabilities

    def __call__(self, values: dict[str, dict[str, Any]], store: Store, **_ignored):
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
