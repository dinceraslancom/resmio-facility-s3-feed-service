import logging
from typing import List, Optional

import asyncpg

from src.facility_feed.infrastructure.config import Settings

logger = logging.getLogger(__name__)


class FacilityRepository:
    def __init__(self, settings: Settings):
        self.db_url = settings.database_url
        self._pool: Optional[asyncpg.Pool] = None

    async def _get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(self.db_url, min_size=1, max_size=5)
                logger.info("Database connection pool created.")
            except Exception as e:
                logger.exception("Failed to create database connection pool.")
                raise

        if self._pool._closed:
            logger.warning("Database connection pool was closed, recreating.")
            self._pool = await asyncpg.create_pool(self.db_url, min_size=1, max_size=5)
        return self._pool

    async def close_pool(self):
        if self._pool:
            await self._pool.close()
            logger.info("Database connection pool closed.")
            self._pool = None

    async def fetch_facilities_chunked(self, chunk_size: int):
        pool = await self._get_pool()
        query = """
            SELECT id, name, phone, url, latitude, longitude, country,
                   locality, region, postal_code, street_address
            FROM facility
            ORDER BY id;
        """
        current_chunk: List[dict] = []
        try:
            async with pool.acquire() as connection:
                async with connection.transaction():
                    # server-side cursor for memory efficiency
                    async for record in connection.cursor(query):
                        facility_obj = dict(record)
                        current_chunk.append(facility_obj)

                        if len(current_chunk) == chunk_size:
                            logger.debug(f"Yielding DB chunk of size {len(current_chunk)}")
                            yield current_chunk
                            current_chunk = []

                if current_chunk:
                    logger.debug(f"Yielding final partial DB chunk of size {len(current_chunk)}")
                    yield current_chunk

                return

        except (asyncpg.exceptions.PostgresError, OSError) as e:
            logger.exception(f"Database error during fetch: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error during fetch: {e}")
            raise

    async def __aenter__(self):
        await self._get_pool()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_pool()
