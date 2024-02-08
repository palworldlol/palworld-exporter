import logging
import os
from glob import glob
from typing import Iterable

from palworld_exporter.providers.data import SaveInformation

"""
Provide metadata about the files in the game save directory.
"""


class PlayerSaveFileProvider:
    """
    Get information about each .sav file on disk
    """

    def __init__(self, save_directory: str):
        self._save_directory = save_directory

    def fetch(self) -> Iterable[SaveInformation]:
        players_save_path = os.path.join(self._save_directory, "Players")
        # Ensure Players directory exists
        if not os.path.exists(players_save_path):
            raise FileNotFoundError(
                f'Player saves directory does not exist in: {self._save_directory}')
        player_saves = glob(os.path.join(players_save_path, '*.sav'))
        for p in player_saves:
            s = os.stat(p)
            info = SaveInformation(filename=os.path.basename(p),
                                   file_size=s.st_size,
                                   last_modified=int(s.st_mtime))
            yield info

    def convert_filename_to_player_uid(self, filename: str) -> str:
        try:
            return str(int(filename[:8], 16))
        except Exception as e:
            logging.error(
                f'Error converting player save filename to player uid: {filename}', e)


class LevelSaveSizeProvider:
    """
    Get the size of Level.sav file on disk
    """

    def __init__(self, save_directory: str):
        self._save_directory = save_directory

    def fetch(self) -> SaveInformation:
        """
        Get Level.sav file size in bytes
        """
        level_sav_path = os.path.join(self._save_directory, "Level.sav")
        if not os.path.exists(level_sav_path):
            raise FileNotFoundError(
                f'Level.sav file does not exist in: {self._save_directory}')

        s = os.stat(level_sav_path)
        info = SaveInformation(filename='Level.sav',
                               file_size=s.st_size,
                               last_modified=int(s.st_mtime))
        return info


"""
        level_meta_sav_path = os.path.join(self._save_directory, "LevelMeta.sav")
        if not os.path.exists(level_meta_sav_path):
            raise FileNotFoundError(
                f'LevelMeta.sav file does not exist in: {self._save_directory}')

        s = os.stat(level_meta_sav_path)
        info_meta = SaveInformation(filename='LevelMeta.sav',
                                    file_size=s.st_size,
                                    last_modified=int(s.st_mtime))
        yield info_meta
 """
