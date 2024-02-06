import os
from glob import glob


class SaveCountProvider:
    """
    Get the number of save files on disk in the Players save directory.
    """

    def __init__(self, save_directory: str):
        self._save_directory = save_directory

    def fetch(self) -> int:
        players_save_path = os.path.join(self._save_directory, "Players")
        # Ensure Players directory exists
        if not os.path.exists(players_save_path):
            raise FileNotFoundError(
                f'Player saves directory does not exist in: {self._save_directory}')
        player_saves = glob(os.path.join(players_save_path, '*.sav'))
        return len(player_saves)
