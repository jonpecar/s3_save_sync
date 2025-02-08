from pathlib import Path

from .games.game import load_games_from_toml, LocalGame
from . import APP_PATH
from .games.bucket import BucketGame

def run():
    default_games = load_games_from_toml(Path(__file__).parent / 'games' / "default_games.toml")
    custom_games = load_games_from_toml(APP_PATH / "game_config.toml")
    games = [g for g in custom_games]
    for game in default_games:
        if not any(game.key == g.key for g in games):
            games.append(game)



    for game in games:
        bucket_game = BucketGame(game.key)
        bucket_game.get_existing()


