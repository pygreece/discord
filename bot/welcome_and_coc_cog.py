import logging

import discord
from discord.ext import commands

from bot import config, db, messages
from bot.models import Member
from bot.senders import send_message_in_channel, delete_channel_and_or_category
from bot.assign_role import assign_role

logger = logging.getLogger(__name__)


class WelcomeAndCoC(commands.Cog):
    """The cog that implements CoC acceptance for the PyGreece Discord bot.

    This class implements functionality for handling member join events,
    sending welcome messages, and assigning roles based on reactions to the
    PyGreece CoC.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the cog with the bot instance."""
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Called when a member joins the server."""

        async with db.get_session() as session:
            # Get or create the member in database
            db_member, created_now = await Member.get_or_create(member.id, session=session)

        # Prepare welcome message
        if not created_now:
            logger.info(f"Member {member.name} ({member.id}) has already joined the guild before.")
            message_content = messages.ALREADY_EXISTS_MESSAGE.format(
                name=member.mention, guild=member.guild.name, link=config.COC_MESSAGE_LINK
            )
        else:
            logger.info(f"New member {member.name} ({member.id}) added to database.")
            message_content = messages.NEW_MEMBER_MESSAGE.format(
                name=member.mention, guild=member.guild.name, link=config.COC_MESSAGE_LINK
            )

        # Creates the channel (and the category if it doesn't exist)
        await send_message_in_channel(
            self.bot,
            member,
            message_content,
            config.WELCOME_CHANNEL_PREFIX,
            config.WELCOME_CATEGORY_NAME,
        )
        try:
            async with db.get_session() as session:
                db_member.dm_sent = True
                session.add(db_member)

            logger.info(f"Updated dm_sent=True for {member.name} ({member.id}) in database.")
        except Exception as e:
            logger.error(f"Error updating dm_sent for {member.name} ({member.id}): {e}")
            

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """Called when a member leaves the server."""

        await delete_channel_and_or_category(
            member,
            config.WELCOME_CHANNEL_PREFIX, 
            config.WELCOME_CATEGORY_NAME, 
            "Member left the server",
        )
        
        try:
            async with db.get_session() as session:
                db_member, _ = await Member.get_or_create(id=member.id, session=session)
                db_member.dm_sent = False
                db_member.reacted = False
                session.add(db_member)    
                logger.info(f"Updated dm_sent=False and reacted=False for {member.name} ({member.id}) in database.")
        except Exception as e:
            logger.error(f"Error updating reacted for {member.name} ({member.id}): {e}")
            
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """Grants the 'members' role and updates the database when a user reacts to the Code of Conduct message."""

        if payload.message_id != config.COC_MESSAGE_ID or payload.emoji.name not in config.ACCEPTABLE_REACTION_EMOJIS:
            return

        member = payload.member
        if not member:
            return
        await assign_role(member, config.MEMBER_ROLE_NAME)

        try:
            async with db.get_session() as session:
                db_member, _ = await Member.get_or_create(id=member.id, session=session)
                if db_member.reacted:
                    logger.info("Member already reacted to CoC message.")
                    return
                db_member.reacted = True
                session.add(db_member)
            logger.info(f"Updated reacted=True for {member.name} ({member.id}) in database.")
        except Exception as e:
            logger.error(f"Error updating reacted for {member.name} ({member.id}): {e}")
        self.bot.dispatch("member_reacted_to_coc", member)
        
        await delete_channel_and_or_category(
            member,
            config.WELCOME_CHANNEL_PREFIX, 
            config.WELCOME_CATEGORY_NAME, 
            "Member reacted to CoC message"
        )
