from pathlib import Path

__version__ = "0.0.1"

APP_PATH = Path.home() / ".s3_save_sync"
if not APP_PATH.exists():
    APP_PATH.mkdir(parents=True)