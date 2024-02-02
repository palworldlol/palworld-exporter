from dataclasses import dataclass


@dataclass
class Player:
    name: str
    playerUid: str
    steamId: str


@dataclass
class ServerInfo:
    name: str
    version: str
