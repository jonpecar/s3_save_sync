from pathlib import Path

from watchdog.observers import Observer

from .logging import LOGGER
from .games.game import load_games_from_toml, LocalGame
from . import APP_PATH
from .games.bucket import BucketGame
from .monitor import SaveSyncher

def run(initial_sync: bool, monitor: bool):
    default_games = load_games_from_toml(Path(__file__).parent / 'games' / "default_games.toml")
    custom_games = load_games_from_toml(APP_PATH / "game_config.toml")
    games = [g for g in custom_games]
    for game in default_games:
        if not any(game.key == g.key for g in games):
            games.append(game)


    if monitor:
        observer = Observer()

    for game in games:
        if not game.saves_exist():
            LOGGER.info(f"{game.key} not found locally. Skipping")
            continue

        bucket_game = BucketGame(game.key)
        if initial_sync:
            SaveSyncher(bucket_game, game).synchronise()
        if monitor:
            observer.schedule(SaveSyncher(bucket_game, game), path=game.path, recursive=True)
    
    if monitor:
        observer.start()
        try:
            while observer.is_alive():
                observer.join(1)
        finally:
            observer.stop()
            observer.join()




        







