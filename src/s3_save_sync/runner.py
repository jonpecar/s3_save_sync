from pathlib import Path

from .logging import LOGGER
from .games.game import load_games_from_toml, LocalGame
from . import APP_PATH
from .games.bucket import BucketGame

def first_run_sync():
    default_games = load_games_from_toml(Path(__file__).parent / 'games' / "default_games.toml")
    custom_games = load_games_from_toml(APP_PATH / "game_config.toml")
    games = [g for g in custom_games]
    for game in default_games:
        if not any(game.key == g.key for g in games):
            games.append(game)



    for game in games:
        if not game.saves_exist():
            LOGGER.info(f"{game.key} not found locally. Skipping")
            continue

        bucket_game = BucketGame(game.key)
        local_versions = game.get_existing()
        
        LOGGER.info(f"Syncing {game.key}...")
        for local_version in local_versions:
            matched_remote = False
            for remote_version in bucket_game.manifest:
                if (local_version.rel_path != remote_version.rel_path):
                    continue
                matched_remote = True
                if (local_version.timestamp == remote_version.timestamp):
                    LOGGER.info(f"{local_version} already synced. Skipping.")
                elif (local_version.timestamp > remote_version.timestamp
                    and local_version.hash != remote_version.hash):
                    LOGGER.info(f"Uploading {local_version}")
                    bucket_game.upload(local_version, game)
                elif (local_version.timestamp < remote_version.timestamp):
                    LOGGER.info(f"Downloading {remote_version}")
                    bucket_game.download(remote_version, game)
                break
            if not matched_remote:
                LOGGER.info(f"No matching version found on S3 for {local_version}. Uploading")
                bucket_game.upload(local_version, game)
        
        for remote_version in bucket_game.manifest:
            for local_version in local_versions:
                matched_local = False
                if (remote_version.rel_path == local_version.rel_path):
                    matched_local = True
                    break
            if not matched_local:
                LOGGER.info(f"Downloading missing {remote_version}")
                bucket_game.download(remote_version, game)







