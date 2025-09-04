import asyncio
import logging

import discord
from discord.ext import commands

from bot import config, db, messages
from bot.models import Member
from bot.roles import assign_role
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
            else:
                db_member.reacted = True
                try:
                    session.add(db_member)
                    logger.info(
                        f"Updated reacted=True for {member.name} ({member.id}) in database."
                    )
                except Exception as e:
                    logger.error(f"Error updating reacted for {member.name} ({member.id}): {e}")
                    return

        # This opens a new thread for ticket verification. Should be deactivate when a PyCon is not
        # on. TODO: Reactivate it when PyCon Greece 2026 is in the works.
        # self.bot.dispatch("new_member_reacted_to_coc", member)

        await delete_private_thread(
            config.COC_CHANNEL_ID,
            config.COC_THREAD_PREFIX,
            member,
            f"{member.name} ({member.id}) reacted to coc message",
        )

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def syncdbcocreactions(self, ctx: commands.Context[commands.Bot]) -> None:
        """Sync the existing coc reactions with the database."""
        logger.info("Received sync DB COC reactions command.")
        assert ctx.guild is not None

        channel = ctx.guild.get_channel(config.COC_CHANNEL_ID)
        if channel is None or not isinstance(channel, discord.TextChannel):
            await ctx.reply("Could not find the CoC channel.")
            return

        try:
            message = await channel.fetch_message(config.COC_MESSAGE_ID)
        except discord.NotFound:
            await ctx.reply("CoC message not found.")
            return
        except discord.Forbidden:
            await ctx.reply("Missing permissions to fetch the CoC message.")
            return

        updated_users = set()
        reactions = [
            reaction
            for reaction in message.reactions
            if reaction.emoji in config.ACCEPTABLE_REACTION_EMOJIS
        ]
        batch_size = 20  # Number of users to process before sleeping
        sleep_duration = 1.5  # Seconds to sleep between batches

        async with db.get_session() as session:
            for reaction in reactions:
                try:
                    users = [user async for user in reaction.users()]
                except discord.HTTPException as e:
                    logger.warning(f"Failed to fetch users for reaction {reaction.emoji}: {e}")
                    continue

                for i, member in enumerate(users):
                    if member.bot:
                        continue  # Skip bots
                    db_member, _ = await Member.get_or_create(member.id, session=session)
                    if not db_member.reacted:
                        db_member.reacted = True
                        session.add(db_member)
                        updated_users.add(member)

                    # Throttle every batch_size users
                    if (i + 1) % batch_size == 0:
                        await asyncio.sleep(sleep_duration)

        await ctx.reply(f"COC reactions synced for {len(updated_users)} users.")
        logger.info(f"Synced {len(updated_users)} users to the database.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def syncdbmemberrole(self, ctx: commands.Context[commands.Bot]) -> None:
        """Set reacted=True for all members with the Member role."""
        logger.info("Received sync DB Member role command.")
        assert ctx.guild is not None

        member_role = discord.utils.get(ctx.guild.roles, name=config.MEMBER_ROLE_NAME)

        if member_role is None:
            await ctx.reply("❌ Could not find the Member role.", ephemeral=True, delete_after=10)
            return

        updated_count = 0
        failed_count = 0

        await ctx.reply(
            "Starting sync for members with the Member role...", ephemeral=True, delete_after=10
        )

        async with db.get_session() as session:
            for member in member_role.members:
                try:
                    db_member, _ = await Member.get_or_create(member.id, session=session)
                    if not db_member.reacted:
                        db_member.reacted = True
                        session.add(db_member)
                        logger.info(f"Set reacted=True for {member.name} ({member.id})")
                        updated_count += 1
                except Exception as e:
                    logger.error(f"Failed to update {member.name} ({member.id}): {e}")
                    failed_count += 1

        await ctx.reply(
            f"✅ Sync complete. Updated: {updated_count}, Failed: {failed_count}",
            ephemeral=True,
            delete_after=60,
        )
        logger.info(
            f"Finished syncing Member role. Updated: {updated_count}, Failed: {failed_count}"
        )
