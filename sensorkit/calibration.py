import logging

from isodate import parse_duration

from .constants import to_capabilities
from .tools.mixins import SchedulableMixin

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Calibration(SchedulableMixin):
    def __init__(self, target, conf_dict, target_obj, store, scheduler):
        self._last = None
        self._policy = None
        self._policy_interval = None
        self._target_obj = None
        self._static = None

        self._target = target
        self._conf = conf_dict
        self._store = store
        self._scheduler = scheduler
        self._job = None

        if self._conf['target']['where'] == 'real':
            self._target_obj = target_obj.real_device
        elif self._conf['target']['where'] == 'abstract':
            self._target_obj = target_obj
        else:
            raise NotImplementedError

        name = self._conf['source']['device']
        measurement = self._conf['measurement']
        def __filter(node):
            if node.name == name:
                if to_capabilities[measurement] == node.obj.measurement:
                    return True
            return False
        self._sources = self._store.tree.findall(__filter)

        if self._conf['policy']['aggregation'] == 'average':
            self._policy = self._measure_average
        else:
            raise NotImplementedError

        self._policy_interval = 'oneshot' if self._conf['policy']['interval'] == 'oneshot' else \
                parse_duration(self._conf['policy']['interval']).seconds

        logger.debug('config: interval %s policy %s object %s',
                     self._policy_interval, self._policy, self._target_obj)

    def schedule(self, immediate: bool) -> None:
        if self._policy_interval == 'oneshot':
            self._job = 'finished'
            self.calibrate()
        elif self._job is not None:
            return

        if immediate:
            self.calibrate()
        self._job = self._scheduler.add_job(self.calibrate, 'interval',
                                            seconds=self._policy_interval)

    def unschedule(self):
        if self._job is None or self._job == 'finished':
            return

        self._job.remove()
        self._job = None

    @property
    def static(self):
        return self._static

    def _measure_average(self):
        l = float(len(self._sources))
        v = 0.0
        for s in self._sources:
            v = v + s.measure
        v = v / l
        return v

    def _measure_first(self):
        raise NotImplementedError

    def _measure_specific(self):
        raise NotImplementedError

    def _setter(self, value):
        if 'property' in self._conf['target']:
            setattr(self._target_obj, self._conf['target']['property'], value)
        elif 'method' in self._conf['target']:
            func = getattr(self._target_obj, self._conf['target']['method'])
            func(value)
        self._last = value

    def calibrate(self):
        logger.debug('Calibration.calibrate source %s setting %s for %s',
                     self._conf['source'], self._conf['target']['property'],
                     self._target)
        value = self._policy()
        if self._last is None or self._last != value:
            logger.info('found change from %s to %s', self._last, value)
            logger.debug('will pull new value %s from %s.measure', value,
                         self._conf['source'])
            logger.debug('will set value %s to %s.%s with %s device', value, self._target,
                         self._conf['target']['property'], self._conf['target']['where'])

            self._setter(value)
        else:
            logger.debug('no changes in %s', self._conf['target']['property'])
