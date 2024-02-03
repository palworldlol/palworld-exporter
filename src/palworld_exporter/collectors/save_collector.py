from glob import glob
import os


class SaveCollector:
    def __init__(self, save_directory: str):
        self.save_directory = save_directory

    def player_save_count(self) -> int:
        players_save_path = os.path.join(self.save_directory, "Players")
        # Ensure Players directory exists
        if not os.path.exists(players_save_path):
            raise FileNotFoundError(
                f'Player saves directory does not exist in: {self.save_directory}')
        player_saves = glob(os.path.join(players_save_path, '*.sav'))
        return len(player_saves)
