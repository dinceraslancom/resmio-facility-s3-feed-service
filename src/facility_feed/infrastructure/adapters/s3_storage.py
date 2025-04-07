import abc

import aioboto3

from src.common.logger import logger
from src.facility_feed.infrastructure.config import Settings


class FeedStorage(abc.ABC):
    @abc.abstractmethod
    async def upload_feed_file(self, file_name: str, content: bytes) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    async def upload_metadata_file(self, file_name: str, content: bytes) -> None:
        raise NotImplementedError


class S3FeedStorage(FeedStorage):
    def __init__(self, settings: Settings):
        self.bucket_name = settings.s3_bucket_name
        self.aws_region = settings.aws_region
        self.aws_secret_access_key = settings.aws_secret_access_key
        self.aws_access_key_id = settings.aws_access_key_id
        self.endpoint_url = settings.aws_endpoint_url
        self.session = aioboto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=self.aws_region
        )

    async def upload_feed_file(self, file_name: str, content: bytes) -> None:
        try:
            async with self.session.client("s3", endpoint_url=self.endpoint_url) as s3:
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=file_name,
                    Body=content,
                    ContentType='application/json',
                    ContentEncoding='gzip'
                )
                logger.info(f"Successfully uploaded feed file {file_name} to s3://{self.bucket_name}")
        except Exception as e:
            logger.exception(f"Failed to upload feed file {file_name} to S3.")
            raise

    async def upload_metadata_file(self, file_name: str, content: bytes) -> None:
        try:
            async with self.session.client("s3", endpoint_url=self.endpoint_url) as s3:
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=file_name,
                    Body=content,
                    ContentType='application/json'
                )
                logger.info(f"Successfully uploaded metadata file {file_name} to s3://{self.bucket_name}")
        except Exception as e:
            logger.exception(f"Failed to upload metadata file {file_name} to S3.")
            raise
