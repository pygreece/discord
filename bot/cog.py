import datetime
import logging

import discord
from discord.ext import commands
from sqlalchemy import select

from bot import config, db, messages
from bot.exceptions import WrongGuildException, WrongUserException
from bot.models import Member

logger = logging.getLogger(__name__)


class WelcomeAndCoC(commands.Cog):
    """The cog that implement CoC acceptance for the PyGreece Discord bot.

    This class implements functionality for handling member join events,
    sending welcome messages, and assigning roles based on reactions to the
    PyGreece CoC.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the cog with the bot instance."""
        self.bot = bot
        self.start_time = datetime.datetime.now(datetime.timezone.utc)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info("PyGreece bot is now logged in")

    async def _send_welcome_message(
        self, member: discord.Member, db_member: Member, content: str
    ) -> bool:
        """Sends a welcome message to the member via DM."""

        try:
            await member.send(content)
            logger.info(f"Sent welcome message to {member.name} ({member.id})")

            async with db.get_session() as session:
                db_member.dm_sent = True
                session.add(db_member)

            logger.info(f"Updated dm_sent=True for {member.name} ({member.id}) in database.")
            return True
        except discord.Forbidden:
            logger.warning(
                f"Could not send DM to {member.name} ({member.id}) - DMs may be disabled."
            )
            return False
        except Exception as e:
            logger.error(f"Error sending DM to {member.name}: {e}")
            return False

    async def _send_welcome_message_in_channel(
        self, member: discord.Member, db_member: Member, content: str
    ) -> None:
        """Sends a welcome message to the member via channel."""

        guild = discord.utils.get(self.bot.guilds, name=config.DISCORD_GUILD)
        if guild is None:
            msg = "Guild not found. Possibly an issue with intents."
            logger.warning(msg)
            raise WrongGuildException(msg)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            self.bot.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        channel = await guild.create_text_channel(
            name=f"welcome-{member.name}", overwrites=overwrites, reason="Fallback for closed DMs"
        )

        await channel.send(content)
        logger.info(f"Sent welcome message to {member.name} ({member.id}) in channel")

        async with db.get_session() as session:
            db_member.dm_sent = True
            session.add(db_member)

        logger.info(f"Updated dm_sent=True for {member.name} ({member.id}) in database.")

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
                name=member.name, guild=member.guild.name
            )
        else:
            logger.info(f"New member {member.name} ({member.id}) added to database.")
            message_content = messages.NEW_MEMBER_MESSAGE.format(
                name=member.name, guild=member.guild.name, link=config.COC_MESSAGE_LINK
            )

        if not await self._send_welcome_message(member, db_member, message_content):
            logger.info(
                f"Failed to send welcome message to {member.name} ({member.id}), sending in channel"
            )
            await self._send_welcome_message_in_channel(member, db_member, message_content)

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

        if payload.message_id != config.COC_MESSAGE_ID:
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

        # Delete the welcome channel
        for channel in guild.text_channels:
            if channel.name.startswith(f"welcome-{member.name}"):
                await channel.delete(reason="Member reacted to CoC message")
                logger.info(f"Deleted welcome channel for {member.name} ({member.id})")
                break

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx: commands.Context[commands.Bot]) -> None:
        """Sync the command tree with the guild."""
        logger.info("Received sync command.")
        assert ctx.guild is not None
        self.bot.tree.copy_global_to(guild=discord.Object(ctx.guild.id))
        await self.bot.tree.sync(guild=discord.Object(ctx.guild.id))
        await ctx.reply("Command tree synced.")

    @commands.hybrid_command()  # type: ignore
    @commands.guild_only()
    @commands.has_role("pygreece organizers")
    async def health(self, ctx: commands.Context[commands.Bot]) -> None:
        """Send the bot's health status."""
        logger.info("Received health check command.")

        embed = discord.Embed(
            title="Bot Health Status",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )

        # Discord connection
        latency = round(self.bot.latency * 1000)
        embed.add_field(name="Discord Connection", value=f"Latency: {latency}ms", inline=False)

        # Database connection
        try:
            async with db.get_session() as session:
                # Simple query to test connection
                await session.execute(select(1))
                embed.add_field(name="Database Connection", value="✅ Connected", inline=False)
        except Exception as e:
            embed.add_field(name="Database Connection", value=f"❌ Error: {str(e)}", inline=False)

        # Uptime
        uptime = datetime.datetime.now(datetime.timezone.utc) - self.start_time
        days, remainder = divmod(int(uptime.total_seconds()), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        embed.add_field(name="Uptime", value=uptime_str, inline=False)

        await ctx.send(embed=embed)
