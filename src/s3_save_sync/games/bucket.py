import logging
import os

import boto3

from .game import LocalGame
from ..logging import LOGGER

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


    def get_existing(self):
        try:
            s3 = boto3.client(service_name='s3',
                            endpoint_url=self.endpoint,
                            aws_access_key_id=self.key_id,
                            aws_secret_access_key=self.key)
            s3.head_bucket(Bucket=self.bucket)
        except Exception as e:
            LOGGER.exception("Error connecting to S3: %s")
            raise

        try:
            paginator = s3.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=self.bucket,
                                        Prefix=self.game_key + '/')
            existing_files = []
            for page in pages:
                if page['KeyCount'] == 0: 
                    continue
                for obj in page['Contents']:
                    if not obj['Key'].endswith('/'):
                        existing_files.append(obj['Key'])
            return existing_files
        except Exception as e:
            LOGGER.exception("Error listing files from S3")
            raise




