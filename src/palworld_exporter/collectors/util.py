import logging
import os
import re
from glob import glob

server_name_re = re.compile(r'^DedicatedServerName=(?P<name>.*?)$')


def find_server_name(filename: str) -> str:
    with open(filename, 'r') as f:
        for line in f.readlines():
            m = server_name_re.search(line)
            if m:
                return m.group("name")
    return ""


def find_save_directory(starting_dir: str) -> str:
    # First, look for a single Level.sav
    level_sav_search = os.path.join(starting_dir, "**/Level.sav")
    result = glob(level_sav_search, recursive=True)
    if len(result) == 1:
        # Found a single result so let's use it
        save_path = os.path.dirname(result[0])
        logging.info(f"Found save directory: {save_path}")
        return save_path
    elif len(result) == 0:
        logging.warning("No Level.sav found")
    elif len(result) > 1:
        logging.warning("Multiple Level.sav found")

    logging.warning("Searching GameUserSettings.ini for save directory")

    # Second, try using the GameUserSettings.ini to figure out the right
    game_settings_search = os.path.join(
        starting_dir, "**/GameUserSettings.ini")
    result = glob(game_settings_search, recursive=True)
    if len(result) == 1:
        # Found settings so identify the save directory name
        server_name = find_server_name(result[0])
        if server_name:
            save_path_search = os.path.join(starting_dir, f"**/{server_name}")
            save_path = glob(save_path_search, recursive=True)
            if len(save_path) == 1:
                logging.info(f"Found save directory: {save_path}")
                return save_path[0]
            else:
                raise ValueError("Error automatically finding save directory")
        else:
            raise ValueError("GameUserSettings.ini found but it contains no DedicatedServerName")
    elif len(result) == 0:
        raise FileNotFoundError("No GameUserSettings.ini found")
    elif len(result) > 1:
        raise ValueError(
            "Multiple GameUserSettings.ini found. Please use more specific directory.")
