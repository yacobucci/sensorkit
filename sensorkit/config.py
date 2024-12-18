from typing import Any
import os.path

import yaml

class Config:
    def __init__(self, config: dict[str, Any]):
        self._data = config

        self._metrics_endpoint = None
        self._metrics_encoding = None
        self._metrics_labels = None

        self._virtual_devices = None
        self._calibrations = None
        self._indoors = None

    @property
    def virtual_devices(self) -> dict[str, dict[str, str]]:
        if self._virtual_devices is not None:
            return self._virtual_devices

        self._virtual_devices = self._data.get('virtual-devices', {})
        return self._virtual_devices

    @property
    def indoors(self):
        if self._indoors is not None:
            return self._indoors

        self._indoors = self._data.get('indoors', True)
        return self._indoors

    @property
    def calibrations(self) -> dict[str, dict[str, str]]:
        if self._calibrations is not None:
            return self._calibrations

        self._calibrations = self._data.get('calibrations', {})
        return self._calibrations
