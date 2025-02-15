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
        time_since_last_check = 0
        LOGGER.info(f"Starting filesystem synconronisation loop")
        if time_since_last_check > 0:
            LOGGER.info(f"Full synchronisation to occur every {sync_freq} seconds")
        observer.start()
        try:
            while observer.is_alive():
                sleep(1)
                # observer.join(60)
                
                if sync_freq > 0:
                    time_since_last_check += 1
                    if time_since_last_check > sync_freq:
                        for syncher in synchers:
                            syncher.synchronise()
                        time_since_last_check = 0
        finally:
            observer.stop()
            observer.join()

    if sync_freq > 0 and not monitor:
        LOGGER.info(f"Starting synchronisation loop at {sync_freq} seconds")
        while True:
            sleep(sync_freq)
            for syncher in synchers:
                syncher.synchronise()


        







