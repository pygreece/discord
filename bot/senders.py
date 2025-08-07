import logging

import discord
from discord.ext.commands import Bot

from bot.config import MEMBER_ROLE_NAME

logger = logging.getLogger(__name__)


async def send_direct_message(member: discord.Member, content: str) -> bool:
    """Sends a message to the member via DM."""

    try:
        await member.send(content)
        logger.info(f"Sent message to {member.name} ({member.id})")
        return True
    except discord.Forbidden:
        logger.warning(f"Could not send DM to {member.name} ({member.id}) - DMs may be disabled.")
        return False
    except Exception as e:
        logger.error(f"Error sending DM to {member.name}: {e}")
        return False


async def send_message_in_channel(
    purpose_prefix: str, guild: discord.Guild, bot: Bot, member: discord.Member, content: str
) -> bool:
    """Sends a message to the member via channel."""

    logger.info(f"Fallback: sending {purpose_prefix} message via channel")

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    if f"{purpose_prefix}-{MEMBER_ROLE_NAME}" not in [
        category.name for category in guild.categories
    ]:
        category = await guild.create_category(
            f"{purpose_prefix}-{MEMBER_ROLE_NAME}", reason="Fallback for closed DMs"
        )
        if not category:
            logger.error(f"Error creating {purpose_prefix}-{MEMBER_ROLE_NAME} category")
            return False
    else:
        category = discord.utils.get(guild.categories, name=f"{purpose_prefix}-{MEMBER_ROLE_NAME}")
        if not category:
            logger.error(f"Error getting {purpose_prefix}-{MEMBER_ROLE_NAME} category")
            return False

    channel = await category.create_text_channel(
        name=f"{purpose_prefix}-{member.name}",
        overwrites=overwrites,
        reason="Fallback for closed DMs",
    )
    if not channel:
        logger.error(f"Error creating {purpose_prefix} channel for {member.name}")
        return False

    message = await channel.send(content)
    if not message:
        logger.error(f"Error sending message in {channel.name}")
        return False

    logger.info(f"Sent message to {member.name} ({member.id}) via channel")
    return True
