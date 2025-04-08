from unittest.mock import MagicMock

import discord
from discord.ext import commands
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.cog import WelcomeAndCoC
from bot.models import Member


async def test_full_member_flow(
    mock_discord_member: MagicMock,
    mock_discord_guild: MagicMock,
    mock_discord_role: MagicMock,
    mock_reaction_payload: MagicMock,
    mock_session: AsyncSession,
) -> None:
    """Test the full flow of a member joining and reacting to the CoC."""
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
    cog = WelcomeAndCoC(bot)

    # Set up the mocks
    bot.get_guild = MagicMock(return_value=mock_discord_guild)
    mock_discord_guild.get_member = MagicMock(return_value=mock_discord_member)

    # Step 1: Member joins
    await cog.on_member_join(mock_discord_member)

    # Check database after join
    stmt = select(Member).filter(Member.id == mock_discord_member.id)
    result = await mock_session.execute(stmt)
    db_member = result.scalar_one()
    assert db_member is not None
    assert db_member.dm_sent
    assert not db_member.reacted

    # Step 2: Member reacts to CoC
    # Directly call the event handler
    await cog.on_raw_reaction_add(mock_reaction_payload)

    # Check database after reaction
    stmt = select(Member).filter(Member.id == mock_discord_member.id)
    result = await mock_session.execute(stmt)
    db_member = result.scalar_one()
    assert db_member.reacted

    # Check role was assigned
    mock_discord_member.add_roles.assert_called_once_with(mock_discord_role)
