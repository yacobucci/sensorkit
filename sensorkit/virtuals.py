import json
import logging

from isodate import parse_duration

from .tools.mixins import GetterMixin, SchedulableMixin
from .datastructures import Store
from .devices import VirtualDevice
from .meters import Meter
from .constants import VIRTUAL_DEVICE, MEAN_SEA_LEVEL_PRESSURE, HECTOPASCAL_UNITS

logger = logging.getLogger(__name__)

class OpenMeteoBuilder:
    def __init__(self):
        pass

    def __call__(self, interval: str, params: dict[str, int | str], store: Store,
                 scheduler, **_ignored):
        return OpenMeteo(interval, params, store, scheduler)

class OpenMeteo(Meter, GetterMixin, SchedulableMixin):
    # XXX add typing hints
    def __init__(self, interval: str, params: dict[str, int | str], store: Store,
                 scheduler):

        super().__init__(VirtualDevice(None, 'open-meteo', VIRTUAL_DEVICE,
                                       [ MEAN_SEA_LEVEL_PRESSURE ]))
        self._location = 'https://api.open-meteo.com/v1/forecast?'

        self._interval_secs = parse_duration(interval).seconds
        self._params = params
        self._store = store
        self._scheduler = scheduler
        self._job = None

    @property
    def location(self) -> str:
        return self._location

    @property
    def measure(self) -> float:
        self._store.altimeter_calibration

    @property
    def measurement(self) -> int:
        return MEAN_SEA_LEVEL_PRESSURE

    @property
    def units(self) -> str:
        return HECTOPASCAL_UNITS

    @property
    def real_device(self):
        return None

    def start(self, immediate: bool) -> None:
        if self._job is not None:
            return

        if immediate:
            self.url_get(self._params)

        self._job = self._scheduler.add_job(self.url_get, 'interval', seconds=self._interval_secs,
                                            kwargs = { 'params': self._params })

    def stop(self) -> None:
        if self._job is None:
            return

        self._job.remove()
        self._job = None

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

        set_store = False
        original_msl = None
        try:
            original_msl = self._store.altimeter_calibration
            if msl != original_msl:
                logger.debug('open_meteo_handler: mean sea level pressure changed')
                set_store = True
        except:
            set_store = True
        finally:
            if set_store is True:
                logger.info('open_meteo_handler: updating mean sea level pressure from %s to %s',
                            original_msl, msl)
                self._store.altimeter_calibration = msl
            else:
                logger.debug('open_meteo_handler: no change in mean sea level pressure (%s, %s)',
                             original_msl, msl)
