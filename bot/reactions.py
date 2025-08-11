import discord
from discord.utils import get as dget

from bot.config import ACCEPTABLE_REACTION_EMOJIS

async def member_has_reacted_to_msg(member: discord.Member, channel_id: int, message_id: int) -> bool:
    guild = member.guild
    if not guild:
        return False
    channel = dget(guild.text_channels, id=channel_id)
    if not channel:
        return False
    message = await channel.fetch_message(message_id)
    if not message:
        return False
    reaction = dget(message.reactions, member=member)
    return reaction in ACCEPTABLE_REACTION_EMOJIS