import logging

import discord
from discord.ext import commands

from bot import config, messages
from bot.roles import member_has_role
from bot.senders import delete_private_thread, send_private_message_in_thread
from bot.views.ticket_view import TicketView

logger = logging.getLogger(__name__)


class TicketVerification(commands.Cog):
    """The cog that implements ticket verification for the PyGreece Discord bot.

    This class implements functionality for handling ticket verifications. It sends messages to
    new members and members who react to the relevant ticket message and assigns the ticket holder
    role based on commands.
    """

    def __init__(self, bot: commands.Bot) -> None:
        """Called when the cog is initialized."""
        self.bot = bot

    @commands.Cog.listener()
    async def on_new_member_reacted_to_coc(self, member: discord.Member) -> None:
        """Called when a new member reacts to the code of conduct message."""

        logger.info("Event on_new_member_reacted_to_coc triggered.")
        # Create the private thread
        await send_private_message_in_thread(
            config.TICKET_CHANNEL_ID,
            config.TICKET_THREAD_PREFIX,
            member,
            messages.NEW_MEMBER_TICKET_MESSAGE.format(name=member.mention),
            f"private {config.TICKET_THREAD_PREFIX} thread",
            view=TicketView(member),
        )

    @commands.Cog.listener()
    async def on_member_reacted_to_ticket(self, member: discord.Member) -> None:
        """Called when a member reacts to the ticket message."""

        logger.info("Event on_member_reacted_to_ticket triggered.")

        if member_has_role(member, config.TICKET_HOLDER_ROLE_NAME):
            logger.info(
                f"Member {member.name} ({member.id}) already has the {config.TICKET_HOLDER_ROLE_NAME} role."
            )
            return

        # Create the private thread
        await send_private_message_in_thread(
            config.TICKET_CHANNEL_ID,
            config.TICKET_THREAD_PREFIX,
            member,
            messages.ASK_FOR_TICKET_MESSAGE.format(name=member.mention),
            f"private {config.TICKET_THREAD_PREFIX} thread",
            view=TicketView(member),
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """Called when a member leaves the server."""

        await delete_private_thread(
            config.TICKET_CHANNEL_ID,
            config.TICKET_THREAD_PREFIX,
            member,
            "member left the server",
        )

    @commands.hybrid_command()
    @commands.guild_only()
    async def ticket(self, ctx: commands.Context[commands.Bot]) -> None:
        """Allows members to start the ticket verification flow by typing !ticket in the #bot-interactions channel."""

        channel = discord.utils.get(ctx.guild.text_channels, id=config.BOT_INTERACTIONS_CHANNEL_ID)
        if not channel:
            logger.error("Channel with name=bot-interactions not found in the server.")
            return

        if ctx.channel.id != channel.id:
            logger.info("Message sent in the wrong channel. Deleting.")
            await ctx.message.delete()
            await ctx.send(
                messages.TICKET_INVALID_CHANNEL_MESSAGE.format(channel=channel.mention),
                ephemeral=True,
                delete_after=20,
            )

        logger.info(f"Received !ticket command in #bot-interactions from {ctx.author.name}")
        # Create the private thread
        await send_private_message_in_thread(
            ctx.channel.id,
            config.TICKET_THREAD_PREFIX,
            ctx.author,
            messages.NEW_MEMBER_TICKET_MESSAGE.format(name=ctx.author.mention),
            f"private {config.TICKET_THREAD_PREFIX} thread",
            view=TicketView(ctx.author),
        )
