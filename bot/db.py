import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot import config

logger = logging.getLogger(__name__)

engine = create_async_engine(config.DATABASE_URL)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session as a context manager.

    This function provides a context manager for database sessions.
    It automatically commits and closes the session when exiting
    the context manager. If an exception occurs, the session is
    rolled back.

    Example:
        async with db_session() as session:
            # Do database operations
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception as e:
        logger.error(f"Error in database session: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()
