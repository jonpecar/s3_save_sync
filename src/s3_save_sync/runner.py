from pathlib import Path

from watchdog.observers import Observer
from time import sleep

from .logging import LOGGER
from .games.game import load_games_from_toml, LocalGame
from . import APP_PATH
from .games.bucket import BucketGame
from .monitor import SaveSyncher

def run(initial_sync: bool, monitor: bool, sync_freq: int = -1):
    default_games = load_games_from_toml(Path(__file__).parent / 'games' / "default_games.toml")
    custom_games = load_games_from_toml(APP_PATH / "game_config.toml")
    games = [g for g in custom_games]
    for game in default_games:
        if not any(game.key == g.key for g in games):
            games.append(game)


    if monitor:
        observer = Observer()
    
    if sync_freq > 0:
        synchers = []

    for game in games:
        if not game.saves_exist():
            LOGGER.info(f"{game.key} not found locally. Skipping")
            continue

        bucket_game = BucketGame(game.key)
        syncher = SaveSyncher(bucket_game, game)
        if initial_sync:
            syncher.synchronise()
        if monitor:
            observer.schedule(syncher, path=game.path, recursive=True)
        if sync_freq > 0:
            synchers.append(syncher)
    
    if monitor:
        observer.start()
        try:
            while observer.is_alive():
                observer.join(1)
        finally:
            observer.stop()
            observer.join()

    if sync_freq > 0:
        LOGGER.info(f"Starting synchronisation loop at {sync_freq} seconds")
        while True:
            sleep(sync_freq)
            for syncher in synchers:
                syncher.synchronise()


        







