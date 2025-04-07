from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    database_url: str = Field(validation_alias='DATABASE_URL')

    s3_bucket_name: str = Field(validation_alias='S3_BUCKET_NAME')
    aws_region: str = Field(validation_alias='AWS_REGION')
    aws_endpoint_url: str = Field(validation_alias='AWS_ENDPOINT_URL')
    aws_access_key_id: Optional[str] = Field(None, validation_alias='AWS_ACCESS_KEY_ID')

    aws_secret_access_key: Optional[str] = Field(validation_alias='AWS_SECRET_ACCESS_KEY')

    log_level: str = Field(default='INFO', validation_alias='LOG_LEVEL')

    feed_chunk_size: int = Field(default=100, validation_alias='FEED_CHUNK_SIZE', gt=0)
    max_concurrent_uploads: int = Field(default=10, validation_alias='MAX_CONCURRENT_UPLOADS', gt=0)


settings = Settings()
