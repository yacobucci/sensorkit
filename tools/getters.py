import abc
import json
import logging
import urllib.parse
import urllib.request

from sensorkit import datastructures

logger = logging.getLogger(__name__)

class Getter(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, '_handler') and
                callable(subclass._handler) or
                NotImplemented)

    def url_get(self, url: str, params: dict) -> None:
        endpoint = url + urllib.parse.urlencode(params)

        logger.debug('calling api endpoint %s', endpoint)
        contents = urllib.request.urlopen(endpoint)
        self._handler(contents)

    @abc.abstractmethod
    def _handler(self, state, contents):
        raise NotImplementedError

class OpenMeteoGetter(Getter):
    def __init__(self, state: datastructures.State):
        self._state = state

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

