import abc
import json
import logging

from isodate import parse_duration

from ..tools.mixins import GetterMixin, SchedulableMixin
from ..datastructures import Store
from ..devices import VirtualDevice
from ..meters import Meter
from ..constants import (VIRTUAL_DEVICE,
                         PRESSURE_MSL,
                         TEMPERATURE,
                         RELATIVE_HUMIDITY,
                         to_capabilities,
)

logger = logging.getLogger(__name__)

# XXX how to set this properly?
logger.setLevel(logging.DEBUG)

to_open_meteo = dict({
    'temperature': 'temperature_2m',
    'relative_humidity': 'relative_humidity_2m',
})
from_open_meteo = { v:k for k,v in zip(to_open_meteo.keys(), to_open_meteo.values()) }

open_meteo_measures = dict({
    'temperature_2m': TEMPERATURE,
    'relative_humidity_2m': RELATIVE_HUMIDITY,
})
open_meteo_measures = { **open_meteo_measures, **to_capabilities }

class OpenMeteoMixin_(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, '_handler') and
                callable(subclass._handler) or
                NotImplemented)

    @abc.abstractmethod
    def _handler(self) -> None:
        raise NotImplementedError

class OpenMeteoCurrentGetterImpl_(GetterMixin, SchedulableMixin):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(OpenMeteoCurrentGetterImpl_, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, capabilities: list[str], interval: str, params: dict[str, int | str],
                 store: Store, scheduler):
        self._location = 'https://api.open-meteo.com/v1/forecast?'
        self._handlers = {}

        self._interval = parse_duration(interval).seconds
        self._params = params
        self._capabilities = capabilities
        self._scheduler = scheduler
        self._job = None

        param = [ c if c not in to_open_meteo else to_open_meteo[c] for c in capabilities]
        self._params['current'] = ','.join(param)

    def start(self, immediate: bool) -> None:
        if self._job is not None:
            return

        if immediate:
            self.url_get(self._params)

        self._job = self._scheduler.add_job(self.url_get, 'interval', seconds=self._interval,
                                            kwargs = { 'params': self._params })

    def stop(self) -> None:
        if self._job is None:
            return

        self._job.remove()
        self._job = None

    def set_handler(self, capability: str, handler: callable) -> None:
        if capability not in self._capabilities:
            logger.warning('open meteo impl: requested unset cap: %s', capability)
            return

        self._handlers[capability] = handler

    @property
    def location(self) -> str:
        return self._location

    def _handler(self, contents) -> None:
        if contents.status != 200:
            logger.warning('open meteo impl: API failed GET - %s', contents.status)
            return

        data = contents.read()
        obj = json.loads(data)

        current_values = obj['current']
        current_units = obj['current_units']

        for c in self._handlers:
            func = self._handlers[c]
            v = current_values[c] if c not in to_open_meteo else current_values[to_open_meteo[c]]
            u = current_values[c] if c not in to_open_meteo else current_units[to_open_meteo[c]]
            func(c, v, u)

class OpenMeteoCurrent_(Meter, OpenMeteoMixin_):
    def __init__(self, capability: str, interval: str,
                 params: dict[str, int | str], store: Store,
                 scheduler, device: VirtualDevice | None = None):
        if device is None:
            super().__init__(VirtualDevice(None, 'open-meteo', VIRTUAL_DEVICE,
                                           [ open_meteo_measures[capability] ]))
        else:
            super().__init__(device)

        self._capability = capability
        self._store = store

    @property
    def measure(self) -> float:
        return getattr(self._store, self._capability)

    @property
    def measurement(self) -> int:
        return open_meteo_measures[self._capability] 

    @property
    def units(self) -> str:
        units_key = self._capability + '_units'
        return getattr(self._store, units_key)

    @property
    def real_device(self):
        return None

    def _handler(self, capability: str, value: float | int, units: str) -> None:
        logger.debug('open_meteo_handler called with %s %s %s',
                     capability, value, units)

        if capability != self._capability:
            msg = 'open meteo meter - called with mismatch capability: got %s != wanted %s'
            logger.warning(msg, capability, self._capability)
            return

        setattr(self._store, capability, value)
        setattr(self._store, capability + '_units', units)

class OpenMeteoCurrentBuilder:
    def __init__(self, capabilities: list[str]):
        self._caps = capabilities

    def __call__(self, interval: str, params: dict[str, int | str], store: Store,
                 scheduler, **_ignored) -> list[OpenMeteoCurrent_ | OpenMeteoCurrentGetterImpl_]:
        # the builder knows what this is, put your smarts here when building other layered
        # virtual devices

        getter_impl = OpenMeteoCurrentGetterImpl_(self._caps, interval, params, store, scheduler)

        devs = []
        for cap in self._caps:
            obj = OpenMeteoCurrent_(cap, interval, params, store, scheduler)
            getter_impl.set_handler(cap, obj._handler)
            devs.append(obj)

        getter_impl.start(True)

        return devs
