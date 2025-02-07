import os
import platform
import tomllib
from pathlib import Path

class TrackedGame:
    def __init__(self,
                 key: str,
                 name: str,
                 path: Path):
        self.key = key
        self.name = name
        self.path = path

def load_games_from_toml(path: Path):
    if not path.exists():
        return []
    with open(path, 'rb') as f:
        data = tomllib.load(f)
    for key, game in data.items():
        name = game.get('name', key)
        if not platform.system().lower() in [k.lower() for k in game.keys()]:
            continue
        if platform.system().lower() == 'windows':
            path: Path
            path_data = game[[k for k in game.keys() if k.lower() == platform.system().lower()][0]]
            if 'path' not in path_data:
                continue
            if ('path_type' in path_data 
                and path_data['path_type'] == 'absolute'
                or 'path_type' not in path_data):
                path = Path(path_data['path'])
            elif (path_data['path_type'] == 'local_low'):
                path = Path(os.getenv('USERPROFILE')) / "Appdata" / "LocalLow" / game['windows']['path']
            elif (path_data['path_type'] == 'appdata'):
                path = Path(os.getenv('APPDATA')) / game['windows']['path']
            elif (path_data['path_type'] == 'local_appdata'):
                path = Path(os.getenv('LOCALAPPDATA')) / game['windows']['path']
            elif (path_data['path_type'] == 'userprofile'):
                path = Path(os.getenv('USERPROFILE')) / "Appdata" / "Roaming" / game['windows']['path']
            if not path or not path.exists():
                continue
            yield TrackedGame(key, name, path)
