from glob import glob
import os
from typing import Iterable

from prometheus_client import CollectorRegistry, Metric
from prometheus_client.metrics_core import GaugeMetricFamily

from palworld_exporter.providers.save import SaveCountProvider


class SaveCollector(CollectorRegistry):
    def __init__(self, save_directory: str):
        self._save_provider = SaveCountProvider(save_directory)

    def collect(self) -> Iterable[Metric]:
        try:
            save_count = self._save_provider.fetch()
            save_count_metric = GaugeMetricFamily('palworld_save_count', 'Number of player save files',
                                                  save_count)
            yield save_count_metric
        except:
            pass
