import json
import logging
import urllib.parse
import urllib.request

from sensorkit import datastructures

logger = logging.getLogger(__name__)

def url_get(state: datastructures.StateInterface, url: str, params: dict,
            handler: callable) -> None:
    endpoint = url + urllib.parse.urlencode(params)

    logger.debug('calling api endpoint %s', endpoint)
    contents = urllib.request.urlopen(endpoint)
    handler(state, contents)

class OpenMeteoHandler:
    def __init__(self):
        pass

    # XXX add typing information for contents
    def handle_response(self, state: datastructures.StateInterface, contents) -> None:
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
            original_msl = state.altimeter_calibration
            if msl != original_msl:
                logger.debug('open_meteo_handler: mean sea level pressure changed')
                set_state = True
        except:
            set_state = True
        finally:
            if set_state is True:
                logger.info('open_meteo_handler: updating mean sea level pressure from %s to %s',
                            original_msl, msl)
                state.altimeter_calibration = msl
            else:
                logger.debug('open_meteo_handler: no change in mean sea level pressure (%s, %s)',
                             original_msl, msl)

