from unittest.mock import patch

from palworld_exporter.providers.rcon import (PlayersProvider, RCONContext,
                                              ServerInfoProvider)


class FakeRCONContext(RCONContext):
    def __init__(self):
        pass


@patch('palworld_exporter.providers.rcon.PlayersProvider._cmd_showplayers')
def test_PlayersProvider(mock_showplayers):
    mock_showplayers.return_value = 'name,steamid,playerUid\nMr Rogers,123456789,987654321\n'
    pp = PlayersProvider(FakeRCONContext(), True)
    players = pp.fetch()
    assert len(players) == 1


@patch('palworld_exporter.providers.rcon.PlayersProvider._cmd_showplayers')
def test_PlayersProvider_NoPlayers(mock_showplayers):
    mock_showplayers.return_value = 'name,steamid,playerUid\n\n'
    pp = PlayersProvider(FakeRCONContext(), True)
    players = pp.fetch()
    assert len(players) == 0


@patch('palworld_exporter.providers.rcon.PlayersProvider._cmd_showplayers')
def test_PlayersProvider_Korean(mock_showplayers):
    # I don't know Korean :( I'm sorry if this is stupid
    name = '트리나'
    mock_showplayers.return_value = f'name,steamid,playerUid\n{name},123456789,123456789\n'
    pp = PlayersProvider(FakeRCONContext(), True)
    players = pp.fetch()
    assert len(players) == 1
    assert name == players[0].name


@patch('palworld_exporter.providers.rcon.PlayersProvider._cmd_showplayers')
def test_PlayersProvider_EmptyResponse(mock_showplayers):
    mock_showplayers.return_value = None
    pp = PlayersProvider(FakeRCONContext(), True)
    players = pp.fetch()
    assert len(players) == 0


@patch('palworld_exporter.providers.rcon.ServerInfoProvider._cmd_info')
def test_ServerInfoProvider(mock_info):
    mock_info.return_value = 'Welcome to Pal Server[v0.1.4.0] http://palworld.lol 1 | OPEN 24/7 Dedicated'
    sip = ServerInfoProvider(FakeRCONContext())
    serverInfo = sip.fetch()
    assert serverInfo.version == '0.1.4.0'
    assert serverInfo.name == 'http://palworld.lol 1 | OPEN 24/7 Dedicated'
