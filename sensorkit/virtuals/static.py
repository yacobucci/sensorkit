import logging
from typing import Any

from ..constants import (
        VIRTUAL_DEVICE,
        VIRTUAL_ADDR,
)
from ..datastructures import (
        capabilities_selector,
)
from ..meters import MeterInterface

logger = logging.getLogger(__name__)

class StaticDevice(MeterInterface):
    def __init__(self, name: str, capability: str, value: Any, units: str):
        self._name = name
        self._id = capabilities_selector('id', capability=capability)
        self._capability = capability
        self._value = value
        self._units = units

    @property
    def address(self) -> int:
        return VIRTUAL_ADDR
    
    @property
    def board(self) -> int:
        return VIRTUAL_DEVICE

    @property
    def name(self) -> str:
        return ''.join([self._name, ':', self._capability])

    @property
    def bus_id(self) -> int:
        return VIRTUAL

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
        raise NotImplementedError

class StaticBuilder:
    def __init__(self, name: str, capabilities: list[str]):
        self._name = name
        self._caps = capabilities

    def __call__(self, values: dict[str, dict[str, Any]], **_ignored):
        devs = []
        for cap in self._caps:
            if cap not in values:
                raise ValueError('need value for capability {}'.format(cap))

            value = values[cap]
            if 'value' not in value or 'units' not in value:
                raise ValueError('need value and units for capability {}'.format(cap))

            obj = StaticDevice(self._name, cap, value['value'], value['units'])
            devs.append(obj)

        return devs
