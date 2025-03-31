from typing import Generator
from unittest.mock import AsyncMock, patch

import pytest

from bot import db


@pytest.fixture
def mock_session() -> AsyncMock:
    """Create a mock for the SQLAlchemy AsyncSession"""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture(autouse=True)
def mock_session_factory(mock_session: AsyncMock) -> Generator[None, None, None]:
    """Create a mock for the async_session_factory that returns our mock session"""
    with patch("bot.db.async_session_factory", return_value=mock_session):
        yield


@pytest.mark.asyncio
async def test_get_session_successful_operation(mock_session: AsyncMock) -> None:
    """Test that get_session successfully yields a session and commits on normal operation"""
    async with db.get_session() as session:
        assert session is mock_session

    # After context manager exits, ensure commit was called and rollback wasn't
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()
    mock_session.close.assert_called_once()


@pytest.mark.asyncio
async def test_get_session_with_exception(mock_session: AsyncMock) -> None:
    """Test that get_session rolls back the transaction when an exception occurs"""
    with patch("bot.db.logger") as mock_logger:
        with pytest.raises(ValueError):
            async with db.get_session() as session:
                assert session is mock_session
                # Simulate an error
                raise ValueError("Database error")

    # After exception, ensure rollback was called and commit wasn't
    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()
    mock_logger.error.assert_called_once()
    assert "Database error" in mock_logger.error.call_args[0][0]
