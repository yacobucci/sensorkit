import json
import logging
from typing import Any

from .mixins import GetterMixin, SchedulableMixin
from ..datastructures import State
from ..devices import VirtualDevice
from ..meters import Meter
from ..constants import VIRTUAL, PRESSURE, HECTOPASCAL_UNITS

logger = logging.getLogger(__name__)

class OpenMeteoGetter(Meter, GetterMixin, SchedulableMixin):
    # XXX add typing hints
    def __init__(self, device: VirtualDevice, state: State, scheduler = None):
        super().__init__(device)
        self._state = state
        self._location = 'https://api.open-meteo.com/v1/forecast?'
        self._scheduler = scheduler
        self._jobs = {}

    @property
    def location(self) -> str:
        return self._location

    @property
    def measure(self) -> float:
        self._state.altimeter_calibration

    @property
    def measurement(self) -> int:
        return PRESSURE

    @property
    def units(self) -> str:
        return HECTOPASCAL_UNITS

    @property
    def real_device(self):
        return None

    def add_schedule(self, method: str, params: dict[str, Any], interval_secs: int) -> None:
        if self._scheduler is None:
            raise AttributeError('not provided with a valid scheduler')

        func = getattr(self, method, None)
        if func is None and not callable(func):
            raise ValueError('{} is not a callable attribute on {}'.format(method, self))

        if method in self._jobs:
            self._jobs[method].remove()

        self._jobs[method] = self._scheduler.add_job(func, 'interval',
                                                     seconds=interval_secs, kwargs = {
            'params': params
        })

    def stop_schedule(self, method: str) -> None:
        if method not in self._jobs:
            return
        self._jobs[method].remove()

    def stop(self):
        for method, job in self._jobs.items():
            job.remove()

    # XXX add typing information for contents
    def _handler(self, contents) -> None:
        logger.debug('open_meteo_handler called with status %s', contents.status)

        if contents.status != 200:
            logger.warning('open_meteo_handler failed GET, using pre-set MSL')
            return

        data = contents.read()
        obj = json.loads(data)
        msl = obj['current']['pressure_msl']
        logger.debug('open_meteo_handler: acquired mean sea level pressure %s', msl)

        set_state = False
        original_msl = None
        try:
            original_msl = self._state.altimeter_calibration
            if msl != original_msl:
                logger.debug('open_meteo_handler: mean sea level pressure changed')
                set_state = True
        except:
            set_state = True
        finally:
            if set_state is True:
                logger.info('open_meteo_handler: updating mean sea level pressure from %s to %s',
                            original_msl, msl)
                self._state.altimeter_calibration = msl
            else:
                logger.debug('open_meteo_handler: no change in mean sea level pressure (%s, %s)',
                             original_msl, msl)
