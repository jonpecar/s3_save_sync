import watchdog.events

from .games.bucket import BucketGame
from .games.game import LocalGame
from .logging import LOGGER

class SaveSyncher(watchdog.events.FileSystemEventHandler):
    def __init__(self, bucket_game: BucketGame, local_game: LocalGame):
        super().__init__()
        self.bucket_game = bucket_game
        self.local_game = local_game

    def on_created(self, event: watchdog.events.FileCreatedEvent) -> None:
        LOGGER.info(f"{self.local_game.name}: File created: {event.src_path}")
        self.synchronise()

    def on_modified(self, event: watchdog.events.FileModifiedEvent) -> None:
        LOGGER.info(f"{self.local_game.name}: File modified: {event.src_path}")
        self.synchronise()

    
    def synchronise(self) -> None:
        local_versions = self.local_game.get_existing()
        self.bucket_game.refresh_manifest

        LOGGER.info(f"Syncing {self.local_game.key}...")
        for local_version in local_versions:
            retry_count = 0
            while retry_count < 3:
                try:
                    matched_remote = False
                    for remote_version in self.bucket_game.manifest:
                        if (local_version.rel_path != remote_version.rel_path):
                            continue
                        matched_remote = True
                        if (local_version.timestamp == remote_version.timestamp):
                            pass
                            LOGGER.debug(f"{local_version} already synced. Skipping.")
                        elif (local_version.timestamp > remote_version.timestamp):
                            LOGGER.info(f"Uploading new version of {local_version}")
                            self.bucket_game.upload(local_version, self.local_game)
                            LOGGER.info(f"Upload complete")
                        elif (local_version.timestamp < remote_version.timestamp):
                            LOGGER.info(f"Downloading new version of {remote_version}")
                            self.bucket_game.download(remote_version, self.local_game)
                            LOGGER.info(f"Download complete")
                        break
                    if not matched_remote:
                        LOGGER.info(f"No matching version found on S3 for {local_version}. Uploading")
                        self.bucket_game.upload(local_version, self.local_game)
                        LOGGER.info(f"Upload complete")
                    break
                except Exception as ex:
                    LOGGER.exception(f"Exception on updating file. Retry count: {retry_count}")
                    retry_count += 1
        
        for remote_version in self.bucket_game.manifest:
            for local_version in local_versions:
                matched_local = False
                if (remote_version.rel_path == local_version.rel_path):
                    matched_local = True
                    break
            if not matched_local:
                retry_count = 0
                while retry_count < 3:
                    try:
                        LOGGER.info(f"Downloading missing {remote_version}")
                        self.bucket_game.download(remote_version, self.local_game)
                        LOGGER.info(f"Download complete")
                        break
                    except Exception as ex:
                        LOGGER.exception(f"Exception on updating file. Retry count: {retry_count}")
                        retry_count += 1

