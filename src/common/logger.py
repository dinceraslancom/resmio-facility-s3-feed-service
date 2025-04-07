import logging
import sys

from src.facility_feed.infrastructure.config import settings

log_level = settings.log_level.upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
)

logging.getLogger("asyncpg").setLevel(logging.WARNING)
logging.getLogger("aioboto3").setLevel(logging.WARNING)
logging.getLogger("botocore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.info(f"Logging configured with level: {log_level}")
