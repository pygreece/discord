import logging

import discord
from discord.utils import get as dget

from bot.sanitizers import sanitize_user_name
from bot.views.base_view import BaseView

logger = logging.getLogger(__name__)


async def send_private_message_in_thread(
    channel_id: int, thread_prefix: str, member: discord.Member, content: str, reason: str, view: BaseView | None = None
) -> None:
    """Creates a private thread, adds the member to it and sends a message inside it.

    :param int channel_id: The ID of the channel to create the thread in.
    :param str thread_prefix: The prefix for the thread name.
    :param discord.Member member: The member to send the message to.
    :param str content: The content of the message.
    :param str reason: The reason for creating the thread and sending the message.
    :param BaseView view: The view of the message.

    :returns None:
    """

    guild = member.guild
    channel = dget(guild.text_channels, id=channel_id)
    if not channel:
        logger.error(f"Channel with id={channel_id} not found in the server.")
        return

    member_name = sanitize_user_name(member.name, member.id)
    
    thread = dget(channel.threads, name=f"{thread_prefix}-{member_name}")
    if not thread:    
        thread = await channel.create_thread(
            name=f"{thread_prefix}-{member_name}",
            reason=reason,
            type=discord.ChannelType.private_thread,
            invitable=False,
        )
    if not thread:
        logger.error(f"Failed to create thread for {member.name} ({member.id}).")
        return

    if member not in thread.members:
        await thread.add_user(member)
        
    if view:
        await thread.send(view=view, content=content)
    else:
        await thread.send(content=content)
    logger.info(
        f"Sent private message{' with view' if view else ''} in thread for {member.name} ({member.id}) because {reason}."
    )

async def delete_private_thread(
    channel_id: int, thread_prefix: str, member: discord.Member, reason: str
) -> None:
    """Deletes a private thread.
    
    :param int channel_id: The ID of the channel containing the thread.
    :param str thread_prefix: The prefix for the thread name.
    :param discord.Member member: The member for which this thread was created.
    :param str reason: The reason for deleting the thread.

    :returns None:
    """

    guild = member.guild
    channel = dget(guild.text_channels, id=channel_id)
    if not channel:
        logger.error(f"Channel with id={channel_id} not found in the server.")
        return

    member_name = sanitize_user_name(member.name, member.id)
    thread = dget(channel.threads, name=f"{thread_prefix}-{member_name}")
    if not thread:
        logger.info(f"Thread with name={thread_prefix}-{member_name} not found in {channel.name}.")
        return

    await thread.delete(reason=reason)
    logger.info(f"Deleted private thread for {member.name} ({member.id}) because {reason}.")
