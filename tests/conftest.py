from contextlib import asynccontextmanager
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import discord
import pytest
import pytest_asyncio
from discord.ext import commands
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from bot import config
from bot.cog import WelcomeAndCoC
from bot.models import Base


@pytest_asyncio.fixture(loop_scope="session", scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a test engine for the test session."""
    engine = create_async_engine(config.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test session for each test."""
    connection = await test_engine.connect()
    transaction = await connection.begin()

    async_session_factory = async_sessionmaker(
        connection, class_=AsyncSession, expire_on_commit=False
    )
    session = async_session_factory()

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture
def mock_session(test_session: AsyncSession, monkeypatch: pytest.MonkeyPatch) -> AsyncSession:
    """Mock the db_session context manager to return the test session."""

    @asynccontextmanager
    async def mock_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_session

    # Patch the db_session function
    monkeypatch.setattr("bot.db.get_session", mock_get_session)

    return test_session


@pytest.fixture
def mock_discord_user() -> MagicMock:
    """Create a mock Discord user."""
    user = MagicMock(spec=discord.User)
    user.id = 123456789
    user.name = "TestUser"
    user.bot = False
    return user


@pytest.fixture
def mock_discord_role() -> MagicMock:
    """Create a mock Discord role."""
    role = MagicMock(spec=discord.Role)
    role.name = "members"
    role.id = 987654321
    return role


@pytest.fixture
def mock_discord_guild(mock_discord_role: MagicMock) -> MagicMock:
    """Create a mock Discord guild."""
    guild = MagicMock(spec=discord.Guild)
    guild.name = config.DISCORD_GUILD
    guild.id = 111222333
    guild.roles = [mock_discord_role]
    return guild


@pytest.fixture
def mock_discord_member(mock_discord_user: MagicMock, mock_discord_guild: MagicMock) -> MagicMock:
    """Create a mock Discord member."""
    member = MagicMock(spec=discord.Member)
    member.id = mock_discord_user.id
    member.name = mock_discord_user.name
    member.bot = False
    member.guild = mock_discord_guild
    member.roles = []
    member.add_roles = AsyncMock()
    member.send = AsyncMock()
    return member


@pytest.fixture
def mock_reaction_payload(
    mock_discord_user: MagicMock, mock_discord_guild: MagicMock
) -> MagicMock:
    """Create a mock reaction payload."""
    payload = MagicMock(spec=discord.RawReactionActionEvent)
    payload.user_id = mock_discord_user.id
    payload.message_id = 123456789
    payload.guild_id = mock_discord_guild.id
    payload.emoji = MagicMock(spec=discord.Emoji)
    payload.emoji.name = "✅"
    return payload


@pytest.fixture
def mock_bot() -> MagicMock:
    """Create a mock Discord bot."""
    bot = MagicMock(spec=commands.Bot)
    bot.latency = 0.05  # Simulate a latency of 50ms
    return bot


@pytest.fixture
def mock_cog(mock_bot: MagicMock) -> WelcomeAndCoC:
    """Create a mock instance of the WelcomeAndCoC cog."""
    cog = WelcomeAndCoC(mock_bot)
    return cog


@pytest.fixture
def mock_context() -> MagicMock:
    """Create a mock Discord context."""
    context = MagicMock(spec=commands.Context)
    context.send = AsyncMock()
    return context
