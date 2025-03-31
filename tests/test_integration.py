from unittest.mock import MagicMock

import discord
from sqlalchemy import select

from bot.bot import PyGreeceBot
from bot.models import Member


async def test_full_member_flow(
    mock_discord_member, mock_discord_guild, mock_discord_role, mock_reaction_payload, mock_session
):
    """Test the full flow of a member joining and reacting to the CoC."""
    bot = PyGreeceBot(command_prefix="!", intents=discord.Intents.default())

    # Set up the mocks
    bot.get_guild = MagicMock(return_value=mock_discord_guild)
    mock_discord_guild.get_member = MagicMock(return_value=mock_discord_member)

    # Step 1: Member joins
    await bot.on_member_join(mock_discord_member)

    # Check database after join
    stmt = select(Member).filter(Member.id == mock_discord_member.id)
    result = await mock_session.execute(stmt)
    db_member = result.scalar_one()
    assert db_member is not None
    assert db_member.dm_sent
    assert not db_member.reacted

    # Step 2: Member reacts to CoC
    # Directly call the event handler
    await bot.on_raw_reaction_add(mock_reaction_payload)

    # Check database after reaction
    stmt = select(Member).filter(Member.id == mock_discord_member.id)
    result = await mock_session.execute(stmt)
    db_member = result.scalar_one()
    assert db_member.reacted

    # Check role was assigned
    mock_discord_member.add_roles.assert_called_once_with(mock_discord_role)
