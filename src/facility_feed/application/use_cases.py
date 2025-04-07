import asyncio
import gzip
import json
import time
from typing import List, Optional

from src.common.logger import logger
from src.facility_feed.domain.transformer import transform_facility_for_feed_short
from src.facility_feed.infrastructure.adapters.db_repository import FacilityRepository
from src.facility_feed.infrastructure.adapters.s3_storage import FeedStorage
from src.facility_feed.infrastructure.config import settings


class GenerateFacilityFeedUseCase:
    def __init__(self, repository: FacilityRepository, storage: FeedStorage):
        self.repository = repository
        self.storage = storage
        self.feed_chunk_size = settings.feed_chunk_size
        self.db_chunk_size = settings.feed_chunk_size
        self.max_concurrent_uploads = settings.max_concurrent_uploads

    async def _process_and_upload_chunk(
            self,
            chunk_index: int,
            facility_chunk: List[dict],
            generation_timestamp: int,
            semaphore: asyncio.Semaphore
    ) -> Optional[str]:

        async with semaphore:  # Acquire semaphore before processing/uploading
            logger.info(f"Starting processing/upload for output chunk {chunk_index} ({len(facility_chunk)} facilities)")
            try:
                # Transform Data
                feed_facilities: List[dict] = [
                    transform_facility_for_feed_short(f) for f in facility_chunk
                ]

                # 2. Prepare feed file content
                feed_content = dict(data=feed_facilities)
                json_bytes = json.dumps(feed_content, default=str).encode('utf-8')

                # 3. Compress data
                compressed_data = gzip.compress(json_bytes)

                # 4. Generate file name
                file_name = f"facility_feed_{generation_timestamp}_{chunk_index}.json.gz"

                # 5. Upload feed file chunk
                logger.info(f"Starting S3 upload for chunk {chunk_index} as {file_name}...")
                await self.storage.upload_feed_file(file_name, compressed_data)
                logger.info(f"Finished S3 upload for chunk {chunk_index} ({file_name})")
                return file_name

            except Exception as e:
                logger.exception(f"Failed to process or upload chunk {chunk_index}: {e}")
                raise

    async def execute(self) -> None:
        logger.info(
            f"Starting facility feed generation. Output chunk size: {self.feed_chunk_size}, DB fetch chunk size: {self.db_chunk_size}, Max concurrent uploads: {self.max_concurrent_uploads}.")
        start_time = time.time()
        generation_timestamp = int(start_time)
        upload_tasks: List[asyncio.Task] = []
        semaphore = asyncio.Semaphore(self.max_concurrent_uploads)
        output_chunk_index = 0
        processed_files: List[str] = []
        any_task_failed = False

        try:
            async for db_chunk in self.repository.fetch_facilities_chunked(self.db_chunk_size):
                if not db_chunk:
                    logger.info("Received empty DB chunk, continuing...")
                    continue

                output_chunk_index += 1
                logger.debug(f"Received DB chunk, scheduling task for output chunk {output_chunk_index}")

                # Create Task
                task = asyncio.create_task(
                    self._process_and_upload_chunk(
                        output_chunk_index,
                        db_chunk,
                        generation_timestamp,
                        semaphore
                    ),
                    name=f"ProcessChunk-{output_chunk_index}"
                )
                upload_tasks.append(task)

            logger.info(f"All DB data fetched. Waiting for {len(upload_tasks)} processing/upload tasks to complete...")

            results = await asyncio.gather(*upload_tasks, return_exceptions=True)
            logger.info("All processing/upload tasks finished.")

            # Check Results
            for i, result in enumerate(results):
                task_name = upload_tasks[i].get_name()
                if isinstance(result, Exception):
                    logger.error(f"Task {task_name} failed: {result}", exc_info=result)
                    any_task_failed = True
                elif isinstance(result, str):
                    processed_files.append(result)
                    logger.debug(f"Task {task_name} completed successfully, added file: {result}")
                elif result is None:
                    logger.info(f"Task {task_name} completed but skipped file generation.")
                else:
                    logger.warning(f"Task {task_name} returned unexpected result type: {type(result)}")
                    any_task_failed = True

            if any_task_failed:
                logger.error("One or more tasks failed during processing/upload. Metadata file will not be generated.")
                raise RuntimeError("Facility feed generation failed due to task errors.")

            if not processed_files:
                logger.warning("No feed files were successfully generated (no data found or all tasks failed/skipped).")
                return

            logger.info(f"Successfully generated {len(processed_files)} feed file(s). Generating metadata.")
            processed_files.sort()
            metadata_content = dict(
                generation_timestamp=generation_timestamp,
                data_file=processed_files
            )
            metadata_json_bytes = json.dumps(metadata_content).encode('utf-8')
            metadata_file_name = "metadata.json"

            await self.storage.upload_metadata_file(metadata_file_name, metadata_json_bytes)

            end_time = time.time()
            logger.info(f"Facility feed generation completed successfully in {end_time - start_time:.2f} seconds.")
            logger.info(f"Generated {len(processed_files)} feed file(s) and {metadata_file_name}.")

        except Exception as e:
            logger.exception(f"An critical error occurred during feed generation orchestration: {e}")
            raise
