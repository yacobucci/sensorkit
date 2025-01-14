import builtins
import logging

from isodate import parse_duration

from .datastructures import (capabilities_selector,
                             deviceids_selector,
)
from .tools.mixins import SchedulableMixin

logger = logging.getLogger(__name__)

class Calibration(SchedulableMixin):
    def __init__(self, target, conf_dict, target_obj, store, scheduler):
        self._last = None
        self._policy = None
        self._policy_interval = None
        self._target_obj = None
        self._static = None
        self._type = None

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

        self._by_property = True if 'property' in self._conf['target'] else False
        self._attribute = self._conf['target']['property'] if self._by_property is True \
                else self._conf['target']['method']

        measurement = self._conf['measurement']
        source = self._conf['source']
        func = None
        if 'meter' in source:
            def __filter(node):
                meta = getattr(node, 'metadata', None)
                devid = deviceids_selector('id', source['meter'])
                if ((meta is not None and meta.is_meter) and
                    (devid.found is True and devid.field == node.obj.board)):
                    field = capabilities_selector('id', capability=measurement)
                    if field.found and field.field == node.obj.measurement:
                        return True
                return False
            func = __filter
        elif 'virtual' in source:
            def __filter(node):
                meta = getattr(node, 'metadata', None)
                if meta is not None and meta.is_virtual and source['virtual'] == node.name:
                    field = capabilities_selector('id', capability=measurement)
                    if field.found and field.field == node.obj.measurement:
                        return True
                return False
            func = __filter
        else:
            def __filter(node):
                meta = getattr(node, 'metadata', None)
                if meta is not None and meta.is_meter:
                    field = capabilities_selector('id', capability=measurement)
                    if field.found and field.field == node.obj.measurement:
                        return True
                return False
            func = __filter
        self._sources = self._store.tree.findall(func)

        if self._conf['policy']['aggregation'] == 'average':
            self._policy = self._cast_measure(self._measure_average)
        elif self._conf['policy']['aggregation'] == 'first':
            self._policy = self._cast_measure(self._measure_first)
        else:
            raise NotImplementedError

        if 'type' in self._conf['policy']:
            self._type = self._conf['policy']['type']

        self._policy_interval = 'oneshot' if self._conf['policy']['interval'] == 'oneshot' else \
                parse_duration(self._conf['policy']['interval']).seconds

        logger.debug('config: interval %s policy %s object %s',
                     self._policy_interval, self._policy, self._target_obj)

    def schedule(self, immediate: bool) -> None:
        if self._policy_interval == 'oneshot':
            self._job = 'finished'
            self.calibrate()
            return
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

    def _cast_measure(self, func: callable):
        def __cast():
            v = func()
            v = v if self._type is None else getattr(builtins, self._type)(v)
            return v
        return __cast

    def _measure_average(self):
        l = len(self._sources)
        v = 0
        for s in self._sources:
            v = v + s.measure
        v = v / l
        return v

    def _measure_first(self):
        s = self._sources[0]
        return s.measure

    def _measure_specific(self):
        raise NotImplementedError

    def _setter(self, value):
        _value = value if self._type is None else getattr(builtins, self._type)(value)
        if self._by_property:
            setattr(self._target_obj, self._attribute, _value)
        else:
            func = getattr(self._target_obj, self._attribute)
            func(_value)
        self._last = _value

    def calibrate(self):
        logger.debug('Calibration.calibrate source %s setting %s for %s',
                     self._conf['source'], self._attribute,
                     self._target)
        value = self._policy()
        if self._last is None or self._last != value:
            logger.info('found change from %s to %s', self._last, value)
            logger.debug('will pull new value %s from %s.measure', value,
                         self._conf['source'])
            logger.debug('will set value %s to %s.%s with %s device', value, self._target,
                         self._attribute, self._conf['target']['where'])

            self._setter(value)
        else:
            logger.debug('no changes in %s', self._attribute)
