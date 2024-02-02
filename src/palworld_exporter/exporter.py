import logging
import re
import time

from prometheus_client import Gauge

from palworld_exporter.collectors.rcon_collector import RCONCollector

info_re = re.compile(r"\[v(?P<version>.*?)\](?P<name>.*$)")


class PalworldMetrics:
    """
    Representation of Prometheus metrics and loop to fetch and transform
    application metrics into Prometheus metrics.
    """

    def __init__(self, rcon_host: str, rcon_port: int, rcon_password: str, polling_interval_seconds: int, ignore_logging_in: bool):
        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_password = rcon_password
        self.polling_interval_seconds = polling_interval_seconds
        self.ignore_logging_in = ignore_logging_in

        # Prometheus metrics to collect
        self.player_count = Gauge(
            'palworld_player_count', 'Current player count')
        self.player_info = Gauge('palworld_player', 'Palworld player information', labelnames=[
                                 'name', 'steam_id', 'player_uid'])
        self.server_info = Gauge(
            'palworld_server', 'Palworld server information', labelnames=['version', 'name'])
        self.palworld_up = Gauge(
            'palworld_up', 'Was last scrape of Palworld metrics successful')

    def run_metrics_loop(self):
        """Metrics fetching loop"""
        while True:
            self.fetch()
            time.sleep(self.polling_interval_seconds)

    def fetch(self):
        """
        Get metrics from application and refresh Prometheus metrics with
        new values.
        """
        collector = None
        success = False

        # Reset player infos. They get populated later if anyone is active.
        self.player_info.clear()

        # Clear server info before populating again.
        self.server_info.clear()

        try:
            with RCONCollector(self.rcon_host, self.rcon_port, self.rcon_password, self.ignore_logging_in) as collector:
                # Update server info gauge
                info = collector.info()
                self.server_info.labels(
                    version=info.version,
                    name=info.name
                ).set(1)

                # Update gauge with labels for each player
                players = collector.players()
                self.player_count.set(len(players))
                for player in players:
                    self.player_info.labels(
                        name=player.name,
                        player_uid=player.playerUid,
                        steam_id=player.steamId,
                    ).set(1)

                # Should always be last after setting other metircs
                success = True
        except ConnectionResetError as e:
            logging.error(e)
        except ConnectionRefusedError:
            logging.warning("Error connecting to RCON server")
        except Exception as e:
            logging.exception(e)
        finally:
            self.palworld_up.set(success)
