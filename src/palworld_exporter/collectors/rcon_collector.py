import csv
import logging
from typing import List
from palworld_exporter.collectors.data import Player, ServerInfo

from rcon import Console
import re

info_re = re.compile(r"\[v(?P<version>.*?)\](?P<name>.*$)")


class RCONCollector:
    def __init__(self, rcon_host, rcon_port, rcon_password, ignore_logging_in):
        self.rcon_host = rcon_host
        self.rcon_port = rcon_port
        self.rcon_password = rcon_password
        self.ignore_logging_in = ignore_logging_in

    def __enter__(self):
        self._console = self._get_console()
        logging.debug('RCON collector opened connection')
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._console:
            self._console.close()
            logging.debug('RCON collector closed connection')

    def _get_console(self):
        return Console(self.rcon_host, self.rcon_password, self.rcon_port)

    def _cmd_showplayers(self):
        return self._console.command('ShowPlayers')

    def _cmd_info(self):
        return self._console.command("Info")

    def players(self) -> List[Player]:
        player_resp = self._cmd_showplayers()
        if player_resp:
            player_reader = csv.reader(player_resp.split('\n'))
            # Ensure field headers
            fields = next(player_reader)
            if fields:
                # Read actual data rows
                players = []
                for row in player_reader:
                    if row:
                        if row[1] == '00000000' and self.ignore_logging_in:
                            # Ignore players with Player UUID all zeroes. This means they are logging in.. Right?
                            logging.debug(
                                f'Excluding from metrics (--ignore-logging-in) player: {row[0]}, {row[1]}')
                            continue
                        # Make new  player instance and add to list which will be returned
                        # TODO Is it possible for row to have more/less then 3 elements?
                        players.append(Player(row[0], row[1], row[2]))
                    else:
                        # Skip empty lines
                        # TODO Log debug maybe?
                        pass
                return players
            else:
                logging.warn('Empty field list from ShowPlayers')
                return []
        else:
            logging.warn('Empty or null response from ShowPlayers')
            return []

    def info(self) -> ServerInfo:
        info_resp = self._cmd_info()
        info = info_re.search(info_resp)
        if info:
            version = info.group("version")
            name = info.group("name")
            return ServerInfo(name, version)
        else:
            logging.warn('No response from Info RCON command')
            return ServerInfo('unknown', 'unknown')
