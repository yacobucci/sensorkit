import abc
import logging
from typing import Any
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

class GetterMixin(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, '_handler') and
                callable(subclass._handler) and
                hasattr(subclass, 'location') and
                callable(subclass.location) or
                NotImplemented)

    def url_get(self, params: dict) -> None:
        endpoint = self.location + urllib.parse.urlencode(params)

        logger.debug('calling api endpoint %s', endpoint)
        contents = urllib.request.urlopen(endpoint)
        self._handler(contents)

    @abc.abstractmethod
    def location(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _handler(self, state, contents):
        raise NotImplementedError

class SchedulableMixin(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'start') and
                callable(subclass.start) and
                hasattr(subclass, 'stop') and
                callable(subclass.stop) or
                NotImplemented)

    @abc.abstractmethod
    def start(self, immediate: bool) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self) -> None:
        raise NotImplementedError
