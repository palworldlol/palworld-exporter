import csv
import logging
import re
from abc import ABC, abstractmethod
from typing import ContextManager, Generic, List, TypeVar

from rcon import Console

from palworld_exporter.providers.data import Player, ServerInfo


class RCONContext(ContextManager):
    """
    A context aware class that returns an instance of a RCON Console.

    For example:

    myctx = RCONContext('localhost', 25575, 'mypassword')
    with myctx as c:
        c.command('ShowPlayers')
    """

    def __init__(self, host, port, password, timeout=10):
        self._host = host
        self._port = port
        self._password = password
        self._timeout = timeout
        self._first_connection_made = False

    def _get_console(self):
        return Console(self._host, self._password, self._port, self._timeout)

    def __enter__(self) -> Console:
        self._console = self._get_console()
        if not self._first_connection_made:
            logging.info('RCON Connection success')
            self._first_connection_made = True
        logging.debug('RCON collector opened connection')
        return self._console

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if self._console:
            self._console.close()
            logging.debug('RCON collector closed connection')


T = TypeVar('T')


class RCONProvider(ABC, Generic[T]):
    @abstractmethod
    def fetch(self) -> T:
        raise NotImplementedError


class PlayersProvider(RCONProvider[List[Player]]):
    """
    Get active Player information.
    """

    def __init__(self, rcon_ctx: RCONContext, ignore_logging_in: bool):
        self._rcon_ctx = rcon_ctx
        self._ignore_logging_in = ignore_logging_in

    def _cmd_showplayers(self):
        with self._rcon_ctx as conn:
            return conn.command("ShowPlayers")

    def fetch(self) -> List[Player]:
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
                        if row[1] == '00000000' and self._ignore_logging_in:
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
                logging.warning('Empty field list from ShowPlayers')
                return []
        else:
            logging.warning('Empty or null response from ShowPlayers')
            return []


class ServerInfoProvider(RCONProvider[ServerInfo]):
    """
    Get Server information including name and version.
    """

    def __init__(self, rcon_ctx: RCONContext):
        self._rcon_ctx = rcon_ctx
        self._info_re = re.compile(r"\[v(?P<version>.*?)\] (?P<name>.*$)")

    def _cmd_info(self):
        with self._rcon_ctx as conn:
            return conn.command("Info")

    def fetch(self) -> ServerInfo:
        info_resp = self._cmd_info()
        info = self._info_re.search(info_resp)
        if info:
            version = info.group("version")
            name = info.group("name").strip()
            return ServerInfo(name, version)
        else:
            logging.warn('No response from Info RCON command')
            return ServerInfo('unknown', 'unknown')
