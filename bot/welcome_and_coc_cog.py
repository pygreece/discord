import logging

import discord
from discord.ext import commands

from bot import config, db, messages
from bot.exceptions import WrongGuildException, WrongUserException
from bot.models import Member
from bot.senders import send_direct_message, send_message_in_channel

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
    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info("PyGreece bot is now logged in")

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

        if await send_direct_message(member, message_content):
            try:
                async with db.get_session() as session:
                    db_member.dm_sent = True
                    session.add(db_member)

                logger.info(f"Updated dm_sent=True for {member.name} ({member.id}) in database.")
            except Exception as e:
                logger.error(f"Error updating dm_sent for {member.name} ({member.id}): {e}")
        elif await send_message_in_channel(config.WELCOME_CATEGORY_AND_CHANNEL_PREFIX, member.guild, self.bot, member, message_content):
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
        
        # Delete the welcome channel and/or category
        guild = member.guild
        for channel in guild.text_channels:
            if channel.name.startswith(f"{config.WELCOME_CATEGORY_AND_CHANNEL_PREFIX}-{member.name}"):
                for category in guild.categories:
                    if category.name.startswith(f"{config.WELCOME_CATEGORY_AND_CHANNEL_PREFIX}-{config.MEMBER_ROLE_NAME}") \
                    and len(category.channels) == 1:
                        await category.delete(reason=f"Empty queue")
                        logger.info(F"Deleted \"{config.WELCOME_CATEGORY_AND_CHANNEL_PREFIX}-{config.MEMBER_ROLE_NAME}\" \
                                    category after {member.name} ({member.id}) emptied the queue by leaving the server")
                        break
                await channel.delete(reason="Member left the server")
                logger.info(f"Deleted welcome channel for {member.name} ({member.id}) after member left the server")
                break

    async def _assign_role(
        self, member: discord.Member, guild: discord.Guild, role_name: str
    ) -> None:
        """Assigns a role to the member if they don't already have it."""

        # Assign the "members" role
        role = discord.utils.get(guild.roles, name=role_name)
        if role:
            if role not in member.roles:
                await member.add_roles(role)
                logger.info(f"Assigned '{role.name}' role to {member.name} ({member.id}).")
            else:
                logger.info(f"{member.name} ({member.id}) already has the '{role.name}' role.")
        else:
            logger.warning(f"Role '{role_name}' not found in the server.")

    async def _get_guild_and_user(
        self, payload: discord.RawReactionActionEvent
    ) -> tuple[discord.Guild, discord.Member]:
        """Retrieves the guild and user from the payload of a reaction event."""

        if payload.guild_id is None:
            msg = f"Invalid {payload.guild_id=} in reaction event"
            logger.error(msg)
            raise WrongGuildException(msg)

        guild = self.bot.get_guild(payload.guild_id)
        if guild is None:
            msg = "Guild not found. Possibly an issue with intents."
            logger.warning(msg)
            raise WrongGuildException(msg)
        if guild.name != config.DISCORD_GUILD:
            msg = f"Wrong guild. The guild found was {guild.name}"
            logger.warning(msg)
            raise WrongGuildException(msg)

        user = guild.get_member(payload.user_id)
        if user is None:
            msg = "Could not find user that reacted."
            logger.warning(msg)
            raise WrongUserException(msg)
        if user.bot:
            msg = f"Ignoring bot reaction from {user.name} ({user.id})."
            logger.info(msg)
            raise WrongUserException(msg)

        return guild, user

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        """Grants the 'members' role and updates the database when a user reacts to the Code of Conduct message."""

        if payload.message_id != config.COC_MESSAGE_ID or payload.emoji.name != "👍":
            return
        
        try:
            guild, member = await self._get_guild_and_user(payload)
        except (WrongGuildException, WrongUserException):
            return

        await self._assign_role(member, guild, config.MEMBER_ROLE_NAME)

        async with db.get_session() as session:
            db_member, _ = await Member.get_or_create(id=member.id, session=session)
            db_member.reacted = True
            session.add(db_member)
        logger.info(f"Updated reacted=True for {member.name} ({member.id}) in database.")

        # Delete the welcome channel and/or category
        for channel in guild.text_channels:
            if channel.name.startswith(f"{config.WELCOME_CATEGORY_AND_CHANNEL_PREFIX}-{member.name}"):
                for category in guild.categories:
                    if category.name.startswith(f"{config.WELCOME_CATEGORY_AND_CHANNEL_PREFIX}-{config.MEMBER_ROLE_NAME}") \
                    and len(category.channels) == 1:
                        await category.delete(reason=f"Empty queue")
                        logger.info(F"Deleted \"{config.WELCOME_CATEGORY_AND_CHANNEL_PREFIX}-{config.MEMBER_ROLE_NAME}\" \
                                    after {member.name} ({member.id}) emptied the queue by reacting to CoC message")
                        break
                await channel.delete(reason="Member reacted to CoC message")
                logger.info(f"Deleted welcome channel for {member.name} ({member.id}) after reaction to CoC message")
                break