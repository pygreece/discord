from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.bot import PyGreeceBot
from bot.config import MEMBER_ROLE_NAME
from bot.exceptions import WrongGuildException, WrongUserException
from bot.models import Member


async def test_on_ready() -> None:
    """Test the on_ready event."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    bot._user = MagicMock()
    bot._user.id = 123456789
    with patch("bot.bot.logger") as mock_logger:
        await bot.on_ready()
        mock_logger.info.assert_called_once()


async def test_send_welcome_message(
    mock_discord_member: MagicMock, mock_session: AsyncSession
) -> None:
    """Test sending welcome message to a member."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    db_member = Member(id=mock_discord_member.id)
    mock_session.add(db_member)
    await mock_session.commit()

    await bot._send_welcome_message(mock_discord_member, db_member, "Test welcome message")

    # Check Discord API to send message was called
    mock_discord_member.send.assert_called_once_with("Test welcome message")

    # Check DB was updated
    stmt = select(Member).filter(Member.id == mock_discord_member.id)
    result = await mock_session.execute(stmt)
    db_member = result.scalar_one()
    assert db_member.dm_sent


async def test_send_welcome_message_discord_failure(
    mock_discord_member: MagicMock, mock_session: AsyncSession
) -> None:
    """Test handling of errors when sending welcome message."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    db_member = Member(id=mock_discord_member.id)
    mock_session.add(db_member)
    await mock_session.commit()

    # Simulate Discord API error
    mock_discord_member.send.side_effect = discord.Forbidden(
        MagicMock(), "Cannot send messages to this user"
    )

    with patch("bot.bot.logger") as mock_logger:
        await bot._send_welcome_message(mock_discord_member, db_member, "Test welcome message")

        # Check warning was logged
        mock_logger.warning.assert_called_once()

    # Check DB was NOT updated
    stmt = select(Member).filter(Member.id == mock_discord_member.id)
    result = await mock_session.execute(stmt)
    db_member = result.scalar_one()
    assert not db_member.dm_sent


async def test_send_welcome_message_random_failure(
    mock_discord_member: MagicMock, mock_session: AsyncSession
) -> None:
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    db_member = Member(id=mock_discord_member.id)
    mock_session.add(db_member)
    await mock_session.commit()

    # Simulate Discord API error
    mock_discord_member.send.side_effect = Exception("Random message")

    with patch("bot.bot.logger") as mock_logger:
        await bot._send_welcome_message(mock_discord_member, db_member, "Test welcome message")

        # Check error was logged
        mock_logger.error.assert_called_once()

    # Check DB was NOT updated
    stmt = select(Member).filter(Member.id == mock_discord_member.id)
    result = await mock_session.execute(stmt)
    db_member = result.scalar_one()
    assert not db_member.dm_sent


async def test_on_member_join_new_member(
    mock_discord_member: MagicMock, mock_session: AsyncSession
) -> None:
    """Test handling a new member joining."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    bot._send_welcome_message = AsyncMock()

    await bot.on_member_join(mock_discord_member)

    # Check DB has new member
    stmt = select(Member).filter(Member.id == mock_discord_member.id)
    result = await mock_session.execute(stmt)
    db_member = result.scalar_one()
    assert db_member is not None
    assert db_member.id == mock_discord_member.id

    # Check welcome message sent
    bot._send_welcome_message.assert_called_once_with(mock_discord_member, db_member, mock.ANY)


async def test_on_member_join_existing_member(
    mock_discord_member: MagicMock, mock_session: AsyncSession
) -> None:
    """Test handling a new member joining."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())
    bot._send_welcome_message = AsyncMock()

    # Simulate existing member in DB
    db_member = Member(id=mock_discord_member.id)
    mock_session.add(db_member)
    await mock_session.commit()

    await bot.on_member_join(mock_discord_member)

    # Check welcome message sent
    bot._send_welcome_message.assert_called_once_with(mock_discord_member, db_member, mock.ANY)


async def test_assign_role(
    mock_discord_member: MagicMock, mock_discord_role: MagicMock, mock_discord_guild: MagicMock
) -> None:
    """Test assigning a role to a member."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    await bot._assign_role(mock_discord_member, mock_discord_guild, MEMBER_ROLE_NAME)

    # Check Discord API was called
    mock_discord_member.add_roles.assert_called_once_with(mock_discord_role)


async def test_assign_role_already_has_role(
    mock_discord_member: MagicMock, mock_discord_role: MagicMock, mock_discord_guild: MagicMock
) -> None:
    """Test assigning a role to a member who already has it."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    mock_discord_member.roles = [mock_discord_role]

    await bot._assign_role(mock_discord_member, mock_discord_guild, MEMBER_ROLE_NAME)

    # Check Discord API was NOT called
    mock_discord_member.add_roles.assert_not_called()


async def test_assign_role_missing_role(
    mock_discord_member: MagicMock, mock_discord_guild: MagicMock
) -> None:
    """Test assigning a non-existent role."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    mock_discord_guild.roles = []

    with patch("bot.bot.logger") as mock_logger:
        await bot._assign_role(mock_discord_member, mock_discord_guild, MEMBER_ROLE_NAME)

        # Check warning was logged
        mock_logger.warning.assert_called_once()

    # Check Discord API was NOT called
    mock_discord_member.add_roles.assert_not_called()


async def test_get_guild_and_user(
    mock_reaction_payload: MagicMock, mock_discord_guild: MagicMock, mock_discord_member: MagicMock
) -> None:
    """Test getting guild and user from reaction payload."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())
    bot.get_guild = MagicMock(return_value=mock_discord_guild)

    mock_discord_guild.get_member = MagicMock(return_value=mock_discord_member)

    guild, user = await bot._get_guild_and_user(mock_reaction_payload)

    assert guild == mock_discord_guild
    assert user == mock_discord_member


async def test_get_guild_and_user_no_guild(mock_reaction_payload: MagicMock) -> None:
    """Test handling None guild."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())
    mock_reaction_payload.guild_id = None

    with pytest.raises(WrongGuildException):
        await bot._get_guild_and_user(mock_reaction_payload)


async def test_get_guild_and_user_get_guild_none(mock_reaction_payload: MagicMock) -> None:
    """Test handling None guild."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())
    bot.get_guild = MagicMock(return_value=None)

    with pytest.raises(WrongGuildException):
        await bot._get_guild_and_user(mock_reaction_payload)


async def test_get_guild_and_user_wrong_guild(
    mock_reaction_payload: MagicMock, mock_discord_guild: MagicMock
) -> None:
    """Test handling wrong guild."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())
    mock_discord_guild.name = "Random wrong name"
    bot.get_guild = MagicMock(return_value=mock_discord_guild)

    with pytest.raises(WrongGuildException):
        await bot._get_guild_and_user(mock_reaction_payload)


async def test_get_guild_and_user_no_user(
    mock_reaction_payload: MagicMock, mock_discord_guild: MagicMock
) -> None:
    """Test handling None user."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())
    bot.get_guild = MagicMock(return_value=mock_discord_guild)

    # Mock the guild's get_member method to return None
    mock_discord_guild.get_member = MagicMock(return_value=None)

    with pytest.raises(WrongUserException):
        await bot._get_guild_and_user(mock_reaction_payload)


async def test_get_guild_and_user_bot_user(
    mock_reaction_payload: MagicMock, mock_discord_guild: MagicMock, mock_discord_member: MagicMock
) -> None:
    """Test handling bot user."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())
    bot.get_guild = MagicMock(return_value=mock_discord_guild)

    # Set up the mock member as a bot
    mock_discord_member.bot = True
    mock_discord_guild.get_member = MagicMock(return_value=mock_discord_member)

    with pytest.raises(WrongUserException):
        await bot._get_guild_and_user(mock_reaction_payload)


async def test_on_raw_reaction_add(
    mock_reaction_payload: MagicMock,
    mock_session: AsyncSession,
    mock_discord_guild: MagicMock,
    mock_discord_member: MagicMock,
) -> None:
    """Test handling a reaction to the Code of Conduct message."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    bot._get_guild_and_user = AsyncMock(return_value=(mock_discord_guild, mock_discord_member))
    bot._assign_role = AsyncMock()

    await bot.on_raw_reaction_add(mock_reaction_payload)

    # Check methods were called
    bot._get_guild_and_user.assert_called_once_with(mock_reaction_payload)
    bot._assign_role.assert_called_once()

    # Check DB was updated
    stmt = select(Member).filter(Member.id == mock_discord_member.id)
    result = await mock_session.execute(stmt)
    db_member = result.scalar_one()
    assert db_member is not None
    assert db_member.reacted is True


async def test_on_raw_reaction_add_wrong_message(mock_reaction_payload: MagicMock) -> None:
    """Test handling a reaction to a different message."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    mock_reaction_payload.message_id = 999999

    bot._get_guild_and_user = AsyncMock()
    bot._assign_role = AsyncMock()

    await bot.on_raw_reaction_add(mock_reaction_payload)

    # Check methods were NOT called
    bot._get_guild_and_user.assert_not_called()
    bot._assign_role.assert_not_called()


async def test_on_raw_reaction_add_guild_user_error(mock_reaction_payload: MagicMock) -> None:
    """Test handling errors in getting guild and user."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    # Mock _get_guild_and_user to raise an exception
    bot._get_guild_and_user = AsyncMock(side_effect=WrongGuildException("Test error"))
    bot._assign_role = AsyncMock()

    await bot.on_raw_reaction_add(mock_reaction_payload)

    # Check _assign_role was NOT called
    bot._assign_role.assert_not_called()
