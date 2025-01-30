from ..constants import (
        VIRTUAL_ADDR,
        VIRTUAL_DEVICE,
)
from ..datastructures import (
        capabilities_selector,
)
from ..meters import MeterInterface

class Virtual(MeterInterface):
    def __init__(self, name: str, capability: str):
        self._name = name
        field = capabilities_selector('id', capability=capability)
        if field.found is False:
            raise ValueError('unsupported capability {}'.format(capability))
        self._measurement = field.field
        self._capability = capability

    @property
    def address(self) -> int:
        return VIRTUAL_ADDR

    @property
    def device_id(self) -> int:
        return VIRTUAL_DEVICE

    @property
    def name(self) -> str:
        return self._name

    @property
    def channel_id(self) -> [ int | None ]:
        return None
