import logging
from typing import Iterable

from prometheus_client import CollectorRegistry, Metric
from prometheus_client.metrics_core import GaugeMetricFamily

from palworld_exporter.providers.save_meta import (LevelSaveSizeProvider,
                                                   PlayerSaveFileProvider)


class SaveFileCollector(CollectorRegistry):
    def __init__(self, save_directory: str):
        self._player_save_provider = PlayerSaveFileProvider(save_directory)
        self._level_sav_provider = LevelSaveSizeProvider(save_directory)

    def collect(self) -> Iterable[Metric]:
        try:
            # Player game saves
            player_save_iter = self._player_save_provider.fetch()

            player_save_size_metric = GaugeMetricFamily('palworld_player_save_size_bytes',
                                                        'File size of a player save file in bytes',
                                                        labels=['filename', 'player_uid'])
            player_save_mtime_metric = GaugeMetricFamily('palworld_player_save_mtime',
                                                         'Last modified time of a player save file',
                                                         labels=['filename', 'player_uid'])
            player_save_count_metric = GaugeMetricFamily('palworld_player_save_count',
                                                         'Number of player save files')

            count = 0
            for p in player_save_iter:
                player_uid = self._player_save_provider.convert_filename_to_player_uid(
                    p.filename)
                player_save_size_metric.add_metric(
                    labels=[p.filename, player_uid], value=p.file_size)
                player_save_mtime_metric.add_metric(
                    labels=[p.filename, player_uid], value=p.last_modified)
                count += 1

            player_save_count_metric.add_metric(labels=[], value=count)

            yield player_save_size_metric
            yield player_save_mtime_metric
            yield player_save_count_metric

            # Level save file
            level_save = self._level_sav_provider.fetch()
            level_save_size_metric = GaugeMetricFamily('palworld_level_save_size_bytes',
                                                       'File size of Level.sav in bytes',
                                                       labels=['filename'])
            level_save_size_metric.add_metric(
                labels=[], value=level_save.file_size)

            yield level_save_size_metric
        except Exception as e:
            logging.warn(e)
