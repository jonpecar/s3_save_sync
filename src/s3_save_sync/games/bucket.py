import logging
import os
import json

import boto3
import botocore.exceptions

from .game import LocalGame
from ..logging import LOGGER
from .save_file_instance import SaveFileInstance

MANIFEST_NAME = 's3_save_sync_manifest.json'

class BucketGame:
    def __init__(self, key: str):
        self.endpoint = os.getenv('S3_SAVE_SYNC_ENDPOINT')
        self.bucket = os.getenv('S3_SAVE_SYNC_BUCKET')
        self.key = os.getenv('S3_SAVE_SYNC_KEY')
        self.key_id = os.getenv('S3_SAVE_SYNC_KEY_ID')

        self.game_key = key

        if not all([self.endpoint, self.bucket, self.key, self.key_id]):
            LOGGER.log(logging.ERROR, "Missing S3 environment variables")
            raise Exception("Missing S3 environment variables")


    def get_existing(self) -> list[SaveFileInstance]:
        s3 = boto3.client(service_name='s3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.key_id,
                aws_secret_access_key=self.key)
        try:
            s3_object = s3.get_object(
                Bucket=self.bucket,
                Key=f'{self.game_key}/{MANIFEST_NAME}')
            manifest_bytes = s3_object.get('Body')
            manifest = json.load(manifest_bytes)
            return [SaveFileInstance.from_s3_manifest(s) for s in manifest]
        except s3.exceptions.NoSuchKey as e:
            return []
        except Exception as e:
            LOGGER.exception("Error connecting to S3: %s")
            raise

        



