import os
import platform
import tomllib
from pathlib import Path

from .save_file_instance import SaveFileInstance

class LocalGame:
    def __init__(self,
                 key: str,
                 name: str,
                 path: Path):
        self.key = key
        self.name = name
        self.path = path
    
    def saves_exist(self) -> bool:
        return self.path.exists()

    def get_existing(self) -> list[SaveFileInstance]:
        files = []
        for file in self.path.iterdir():
            if file.is_file():
                files.append(SaveFileInstance.from_local_filesystem(file, self.path))
        return files

def load_games_from_toml(toml_path: Path):
    if not toml_path.exists():
        return []
    with open(toml_path, 'rb') as f:
        data = tomllib.load(f)
    for key, game in data.items():
        name = game.get('name', key)
        if not platform.system().lower() in [k.lower() for k in game.keys()]:
            continue
        if platform.system().lower() == 'windows':
            path: Path
            os_key = [k for k in game.keys() if k.lower() == platform.system().lower()][0]
            path_data = game[os_key]
            if 'path' not in path_data:
                continue
            if ('path_type' in path_data 
                and path_data['path_type'] == 'absolute'
                or 'path_type' not in path_data):
                path = Path(path_data['path'])
            elif (path_data['path_type'] == 'locallow'):
                path = Path(os.getenv('USERPROFILE')) / "Appdata" / "LocalLow" / game[os_key]['path']
            elif (path_data['path_type'] == 'appdata'):
                path = Path(os.getenv('APPDATA')) / game[os_key]['path']
            elif (path_data['path_type'] == 'local_appdata'):
                path = Path(os.getenv('LOCALAPPDATA')) / game[os_key]['path']
            elif (path_data['path_type'] == 'userprofile'):
                path = Path(os.getenv('USERPROFILE')) / "Appdata" / "Roaming" / game[os_key]['path']
            if not path or not path.exists():
                continue
            yield LocalGame(key, name, path)
