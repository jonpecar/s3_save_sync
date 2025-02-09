from collections.abc import Callable
from pathlib import Path 
from typing import Self
import hashlib

BUF_SIZE = 65536

class SaveFileInstance:
    def __init__(self,
                 rel_path: str,
                 timestamp: int,
                 sha1_hash: Callable):
        self.rel_path = rel_path
        self.timestamp = timestamp
        self._sha1_hash = sha1_hash

    @property
    def hash(self) -> str:
        """Returns the SHA-1 hash of this file."""
        return self._sha1_hash()

    def to_dict(self) -> dict[str, str]:
        """Returns a dictionary representation of this file."""
        return {
            'rel_path': self.rel_path,
            'timestamp': self.timestamp,
            'hash': self.hash
        }

    @staticmethod
    def from_local_filesystem(file_path: Path,
                              game_dir_path: Path) -> Self:
        rel_path = file_path.relative_to(game_dir_path)
        file_name = str(rel_path)

        def hash_func(path=file_path):
            sha1 = hashlib.sha1()
            with open(path, 'rb') as f:
                while True:
                    data = f.read(BUF_SIZE)
                    if not data:
                        break
                    sha1.update(data)
            return sha1.hexdigest()

        return SaveFileInstance(rel_path=file_name,
                                timestamp=int(file_path.stat().st_mtime),
                                sha1_hash=hash_func)
    
    @staticmethod
    def from_s3_manifest(file_info: dict) -> Self:
        file_name = file_info['rel_path']
        timestamp = int(file_info['timestamp'])
        def hash_func(hash = file_info['hash']):
            return hash
        return SaveFileInstance(rel_path=file_name,
                                timestamp=timestamp,
                                sha1_hash=hash_func)

    def __str__(self) -> str:
        return f"SaveFileInstance({self.rel_path}, {self.timestamp}, {self.hash})"



