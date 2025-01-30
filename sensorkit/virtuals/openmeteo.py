import abc
import json
import logging
from typing import Any

from isodate import parse_duration
import littletable as db

from ..constants import (
        VIRTUAL_ADDR,
        VIRTUAL_DEVICE,
        PRESSURE_MSL,
        TEMPERATURE,
        RELATIVE_HUMIDITY,
)
from ..datastructures import (UniqueRecordFieldByWhere,
                              capabilities_selector,
)
from ..meters import MeterInterface
from ..tools.mixins import (
        GetterMixin,
        SchedulableInterface,
        NodeMixin,
)
from .virtual import Virtual

logger = logging.getLogger(__name__)

open_meteo_data = f"""\
id,capability,open_meteo_capability
{TEMPERATURE},temperature,temperature_2m
{RELATIVE_HUMIDITY},relative_humidity,relative_humidity_2m"""

open_meteo = db.Table('open_meteo')
open_meteo.csv_import(open_meteo_data, transforms={"id": int})

fields = UniqueRecordFieldByWhere(open_meteo)

class _OpenMeteoInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, '_handler') and
                callable(subclass._handler) or
                NotImplemented)

    @abc.abstractmethod
    def _handler(self) -> None:
        raise NotImplementedError

class _OpenMeteoCurrentGetterImpl(GetterMixin, SchedulableInterface):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(_OpenMeteoCurrentGetterImpl, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, capabilities: list[str], interval: str, params: dict[str, int | str],
                 scheduler):
        self._location = 'https://api.open-meteo.com/v1/forecast?'
        self._handlers = {}

        self._interval = parse_duration(interval).seconds
        self._params = params
        self._capabilities = capabilities
        self._scheduler = scheduler
        self._job = None

        param = [ c if not fields('open_meteo_capability', capability=c).found else \
                fields('open_meteo_capability', capability=c).field for c in capabilities ]
        self._params['current'] = ','.join(param)

    def schedule(self, immediate: bool) -> None:
        if self._job is not None:
            return

        if immediate:
            self.url_get(self._params)

        self._job = self._scheduler.add_job(self.url_get, 'interval', seconds=self._interval,
                                            kwargs = { 'params': self._params })

    def unschedule(self) -> None:
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
            om_cap = fields('open_meteo_capability', capability=c)
            v = current_values[c] if not om_cap.found else current_values[om_cap.field]
            u = current_units[c] if not om_cap.found  else current_units[om_cap.field]
            func(c, v, u)

class _OpenMeteoCurrent(NodeMixin, Virtual, _OpenMeteoInterface):
    def __init__(self, name: str, capability: str, interval: str,
                 params: dict[str, int | str], scheduler):
        super().__init__(name, capability)
        self._measure = 0.0
        self._units = None

    @property
    def measure(self) -> float:
        return self._measure

    @property
    def measurement(self) -> int:
        return self._measurement

    @property
    def units(self) -> str:
        return self._units

    def _handler(self, capability: str, value: float | int, units: str) -> None:
        logger.debug('open_meteo_handler called with %s %s %s',
                     capability, value, units)

        if capability != self._capability:
            msg = 'open meteo meter - called with mismatch capability: got %s != wanted %s'
            logger.warning(msg, capability, self._capability)
            return

        self._measure = value
        self._units = units

class OpenMeteoCurrentBuilder:
    def __init__(self, name: str, capabilities: list[str]):
        self._name = name
        self._caps = capabilities

    def __call__(self, interval: str, params: dict[str, int | str], scheduler,
                 **_ignored) -> list[_OpenMeteoCurrent | _OpenMeteoCurrentGetterImpl]:
        # the builder knows what this is, put your smarts here when building other layered
        # virtual devices

        getter_impl = _OpenMeteoCurrentGetterImpl(self._caps, interval, params, scheduler)

        devs = []
        for cap in self._caps:
            obj = _OpenMeteoCurrent(self._name, cap, interval, params, scheduler)
            getter_impl.set_handler(cap, obj._handler)
            devs.append(obj)

        getter_impl.schedule(True)

        return devs
