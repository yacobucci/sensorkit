import logging
from typing import Any

from ..meters import MeterInterface
from ..tools.mixins import NodeMixin
from .virtual import Virtual

logger = logging.getLogger(__name__)

class StaticDevice(NodeMixin, Virtual):
    def __init__(self, name: str, capability: str, value: Any, units: str):
        super().__init__(name, capability)
        self._value = value
        self._units = units

    @property
    def measure(self) -> Any:
        return self._value

    @property
    def measurement(self) -> int:
        return self._measurement
    
    @property
    def units(self) -> str:
        return self._units

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
