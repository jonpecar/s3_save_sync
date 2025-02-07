from pathlib import Path
from typing import Self
import hashlib

BUF_SIZE = 65536

class SaveFileInstance:
    def __init__(self,
                 rel_path: str,
                 timestamp: int,
                 sha1_hash: str):
        self.rel_path = rel_path
        self.timestamp = timestamp
        self.sha1_hash = sha1_hash

    @staticmethod
    def from_local_filesystem(file_path: Path,
                              game_dir_path: Path) -> Self:
        rel_path = file_path.relative_to(game_dir_path)
        file_name = str(rel_path)
        sha1 = hashlib.sha1()
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                sha1.update(data)

        return SaveFileInstance(rel_path=file_name,
                                timestamp=int(file_path.stat().st_mtime),
                                sha1_hash=sha1.hexdigest())
    
    @staticmethod
    def from_s3_manifest(file_info: dict) -> Self:
        file_name = file_info['name']
        timestamp = int(file_info['timestamp'])
        sha1 = file_info['hash']
        return SaveFileInstance(rel_path=file_name,
                                timestamp=timestamp,
                                sha1_hash=sha1)



