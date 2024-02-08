import pytest
from pyfakefs.fake_filesystem_unittest import TestCase

from palworld_exporter.providers.save_meta import (LevelSaveSizeProvider,
                                                   PlayerSaveFileProvider)


class PlayerSaveProviderTestCase(TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_valid_count(self):
        base_dir = "/Pal/Saved/SaveGames/0/F0951AC10BED42C6B0EA92ACABB01E95/"
        self.fs.create_dir(f"{base_dir}/Players")
        self.fs.create_file(
            f"{base_dir}/Players/FBB2E40C000000000000000000000000.sav")
        self.fs.create_file(
            f"{base_dir}/Players/E522CF3B000000000000000000000000.sav")
        self.fs.create_file(
            f"{base_dir}/Players/3C291D4D000000000000000000000000.sav")

        prov = PlayerSaveFileProvider(base_dir)
        assert 3 == sum(1 for _ in prov.fetch())

    def test_no_save_files(self):
        base_dir = "/Pal/Saved/SaveGames/0/F0951AC10BED42C6B0EA92ACABB01E95/"
        self.fs.create_dir(f"{base_dir}/Players")

        prov = PlayerSaveFileProvider(base_dir)
        assert 0 == sum(1 for _ in prov.fetch())

    def test_no_players_directory(self):
        base_dir = "/Pal/Saved/SaveGames/0/F0951AC10BED42C6B0EA92ACABB01E95/"

        provider = PlayerSaveFileProvider(base_dir)
        with pytest.raises(FileNotFoundError):
            sum(1 for _ in provider.fetch())

    def test_ignore_nonsav_files(self):
        base_dir = "/Pal/Saved/SaveGames/0/F0951AC10BED42C6B0EA92ACABB01E95/"
        self.fs.create_dir(f"{base_dir}/Players")
        self.fs.create_file(f"{base_dir}/Players/ABC123.txt")
        self.fs.create_file(f"{base_dir}/Players/ABC123.sav.backup")
        self.fs.create_file(
            f"{base_dir}/Players/3C291D4D000000000000000000000000.sav")

        prov = PlayerSaveFileProvider(base_dir)
        assert 1 == sum(1 for _ in prov.fetch())

    def test_convert_filename_to_player_uid(self):
        prov = PlayerSaveFileProvider("")
        assert "1009327437" == prov.convert_filename_to_player_uid(
            "3C291D4D000000000000000000000000.sav")
        assert "4222805004" == prov.convert_filename_to_player_uid(
            "FBB2E40C000000000000000000000000.sav")


class LevelSaveSizeProviderTestCase(TestCase):
    def setUp(self):
        self.setUpPyfakefs()

    def test_valid_levelsav(self):
        base_dir = "/Pal/Saved/SaveGames/0/F0951AC10BED42C6B0EA92ACABB01E95/"
        file_size = 1234
        self.fs.create_file(f"{base_dir}/Level.sav", st_size=file_size)

        provider = LevelSaveSizeProvider(base_dir)
        assert file_size == provider.fetch().file_size

    def test_no_players_directory(self):
        base_dir = "/Pal/Saved/SaveGames/0/F0951AC10BED42C6B0EA92ACABB01E95/"

        provider = LevelSaveSizeProvider(base_dir)
        with pytest.raises(FileNotFoundError):
            provider.fetch()
