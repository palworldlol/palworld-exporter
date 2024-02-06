import csv
import logging
import re
from typing import Iterable

from prometheus_client.metrics_core import (GaugeMetricFamily,
                                            InfoMetricFamily, Metric)
from prometheus_client.registry import Collector

from palworld_exporter.providers.rcon import (PlayersProvider, RCONContext,
                                              ServerInfoProvider)

info_re = re.compile(r"\[v(?P<version>.*?)\](?P<name>.*$)")


class RCONCollector(Collector):
    def __init__(self, rcon_ctx: RCONContext, ignore_logging_in: bool):
        self._server_info_provider = ServerInfoProvider(rcon_ctx)
        self._players_provider = PlayersProvider(
            rcon_ctx, ignore_logging_in=ignore_logging_in)

    def collect(self) -> Iterable[Metric]:
        result = []
        success = False

        try:
            info = self._server_info_provider.fetch()
            info_metric = InfoMetricFamily('palworld_server', 'Palworld server information', value={
                                           'version': info.version, 'name': info.name})
            result.append(info_metric)

            players = self._players_provider.fetch()
            player_count_metric = GaugeMetricFamily(
                'palworld_player_count', 'Current player count', len(players))
            result.append(player_count_metric)

            players_metric = GaugeMetricFamily('palworld_player', 'Palworld player information', labels=[
                                               'name', 'steam_id', 'player_uuid'])
            for player in players:
                players_metric.add_metric(
                    labels=[player.name, player.steamId, player.playerUid], value=1)
            result.append(players_metric)

            # We made it through the whole scrape
            success = True
        except ConnectionRefusedError:
            logging.warning("Error connecting to RCON server")
        except ConnectionResetError as e:
            logging.error(e)
        except Exception as e:
            logging.exception(e)
        finally:
            up_metric = GaugeMetricFamily('palworld_up', 'Was the last scrape of RCON successful', int(success))
            result.append(up_metric)
            return result
