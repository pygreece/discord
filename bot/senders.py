import logging

import discord
from discord.ext.commands import Bot
from discord.utils import get as dget
from bot.sanitizers import sanitize_user_name


logger = logging.getLogger(__name__)

async def send_message_in_channel(
    bot: Bot, member: discord.Member, content: str, channel_prefix: str, category_name: str
) -> None:
    """
    Sends a message to the member via channel. Creates the category and channel if they don't exist.
    
    Description:
        The category name will be "{category_name}" and the channel name will be "{channel_prefix}-{member.name}"
        if member.name is a valid channel name, otherwise it will be "{channel_prefix}-{}
        e.g Category "Private Channels" will contain the "private-AlexMatoa" channel if channel_prefix is "private"
        and the category_name is "Private Channels". Returns whether the message was sent.
        
        
    Args:
        bot (Bot): The bot that will send the message.
        member (discord.Member): The member that will receive the message.
        content (str): The content of the message.
        channel_prefix (str): The prefix of the channel name.
        category_name (str): The name of the category.
        
        
    Returns:
        None.
    """

    guild = member.guild
    category = dget(guild.categories, name=category_name)
    if not category:
        try:
            category = await guild.create_category(
                name=category_name, reason=f"{category_name} for {channel_prefix}-member_name channels"
            )
        except Exception as e:
            logger.error(f"Error creating {category_name} category: {e}")
            return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    
    member_name = sanitize_user_name(member.name, member.id)
    channel = dget(category.text_channels, name=f"{channel_prefix}-{member_name}")
    if not channel:
        try:
            channel = await category.create_text_channel(
                name=f"{channel_prefix}-{member_name}",
                overwrites=overwrites,
                reason=f"Private {channel_prefix} channel for {member.name}",
            )
        except Exception as e:
            logger.error(f"Error creating {channel_prefix}-{member_name} channel: {e}")
            return
    else:
        await channel.set_permissions(member, overwrite=overwrites[member])

    try:
        await channel.send(content)
        logger.info(f"Sent message to {member.name} ({member.id}) via channel")
    except Exception as e:
        logger.error(f"Error sending message in {channel.name}: {e}")
        

async def delete_channel_and_or_category(member: discord.Member, channel_prefix: str, category_name: str, reason: str) -> None:
    """
    Deletes the channel and/or the category if it's empty.
    
    Description:
        Looks for a channel named "{channel_prefix}-{member_name}" and deletes it.
        The member_name will be member.name if it's a valid channel name, otherwise it will be member.id[:10].
        Looks for a category named "{category_name}" and deletes it if it's empty.
        Returns whether the category was deleted.


    Args:
        member (discord.Member): The member whose channel will be deleted.
        channel_prefix (str): The prefix of the channel name.
        category_name (str): The name of the category.
        reason (str): The reason for deleting the channel.
        
    Returns:
        None.
    """

    guild = member.guild
    member_name = sanitize_user_name(member.name, member.id)
    channel = dget(guild.text_channels, name=f"{channel_prefix}-{member_name}")
    if channel:
        try:
            await channel.delete(reason=reason)
            logger.info(f"Deleted private {channel_prefix}-{member_name} channel for {member.name} ({member.id}) because {reason}.")
        except Exception as e:
            logger.error(f"Error deleting {channel.name}: {e}")
            return
        
    category = dget(guild.categories, name=category_name)
    if category and len(category.channels) == 0:
        try:
            await category.delete(reason=reason)
            logger.info(
                f'Deleted "{category_name}" category after {member.name} ({member.id}) emptied the queue because {reason}.'
            )
        except Exception as e:
            logger.error(f"Error deleting {category_name}: {e}")
            