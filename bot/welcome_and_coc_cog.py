import logging

import discord
from discord.ext import commands

from bot import config, db, messages
from bot.assign_role import assign_role
from bot.models import Member
from bot.senders import delete_private_thread, send_private_message_in_thread

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

        # Creates the thread
        await send_private_message_in_thread(
            config.COC_CHANNEL_ID,
            config.COC_THREAD_PREFIX,
            member,
            message_content,
            f"Private {config.COC_THREAD_PREFIX} thread for {member.name} ({member.id})",
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

        async with db.get_session() as session:
            db_member, _ = await Member.get_or_create(member.id, session=session)

        if db_member.dm_sent and not db_member.reacted:
            await delete_private_thread(
                config.COC_CHANNEL_ID,
                config.COC_THREAD_PREFIX,
                member,
                f"{member.name} ({member.id}) left the server",
            )
        else:
            logger.info(
                f"Member {member.name} ({member.id}) left the guild but there was no CoC thread to delete."
            )

        db_member.dm_sent = False
        db_member.reacted = False
        try:
            async with db.get_session() as session:
                session.add(db_member)
                logger.info(
                    f"Updated dm_sent=False and reacted=False for {member.name} ({member.id}) in database."
                )
        except Exception as e:
            logger.error(
                f"Error updating dm_sent and reacted for {member.name} ({member.id}): {e}"
            )

    @commands.Cog.listener()
    async def on_member_reacted_to_coc(self, member: discord.Member) -> None:
        """
        Grants the 'members' role and updates the database when a user reacts to the Code of Conduct message.
        Also invokes the new_member_reacted_to_coc event so the ticket-verification cog can handle it.
        """

        logger.info("Event on_member_reacted_to_coc triggered.")
        
        if not await assign_role(member, config.MEMBER_ROLE_NAME):
            return

        async with db.get_session() as session:
            db_member, _ = await Member.get_or_create(id=member.id, session=session)
            if db_member.reacted:
                logger.info("Member already reacted to CoC message.")
                return

            db_member.reacted = True
            try:
                session.add(db_member)
                logger.info(f"Updated reacted=True for {member.name} ({member.id}) in database.")
            except Exception as e:
                logger.error(f"Error updating reacted for {member.name} ({member.id}): {e}")
                return
            
        self.bot.dispatch("new_member_reacted_to_coc", member)
        
        await delete_private_thread(
            config.COC_CHANNEL_ID,
            config.COC_THREAD_PREFIX,
            member,
            f"{member.name} ({member.id}) reacted to coc message",
        )