import abc
import logging
from typing import Any
import urllib.parse
import urllib.request
import uuid

logger = logging.getLogger(__name__)

class NodeMixin():
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._uuid = uuid.uuid4()

    @property
    def uuid(self) -> uuid.UUID:
        return str(self._uuid)

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

class SchedulableInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'schedule') and
                callable(subclass.schedule) and
                hasattr(subclass, 'unschedule') and
                callable(subclass.unschedule) or
                NotImplemented)

    @abc.abstractmethod
    def schedule(self, immediate: bool) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def unschedule(self) -> None:
        raise NotImplementedError

class RunnableInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'run') and
                callable(subclass.run) and
                hasattr(subclass, 'stop') and
                callable(subclass.stop) or
                NotImplemented)

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self):
        raise NotImplementedError
