import asyncio

from src.common.logger import logger
from src.facility_feed.application.use_cases import GenerateFacilityFeedUseCase
from src.facility_feed.infrastructure.adapters.db_repository import FacilityRepository
from src.facility_feed.infrastructure.adapters.s3_storage import S3FeedStorage
from src.facility_feed.infrastructure.config import settings


async def main():
    logger.info("Initializing feed generation service...")
    try:
        async with FacilityRepository(settings) as facility_repo:
            s3_storage = S3FeedStorage(settings)

            use_case = GenerateFacilityFeedUseCase(repository=facility_repo, storage=s3_storage)

            await use_case.execute()

            logger.info("Feed generation process finished.")

    except Exception as e:
        logger.critical(f"Service execution failed critically: {e}", exc_info=True)
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
