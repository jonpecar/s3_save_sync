from pathlib import Path

from .games.game import load_games_from_toml, TrackedGame
from . import APP_PATH
from .bucket import SaveBucket

def run():
    default_games = load_games_from_toml(Path(__file__).parent / 'games' / "default_games.toml")
    custom_games = load_games_from_toml(APP_PATH / "game_config.toml")
    games = [g for g in custom_games]
    for game in default_games:
        if not any(game.key == g.key for g in games):
            games.append(game)

    bucket = SaveBucket()

    for game in games:
        bucket.get_existing(game)

