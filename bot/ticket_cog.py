import logging

import discord
from discord.ext import commands

from bot import config, messages
from bot.roles import has_role
from bot.sanitizers import sanitize_ticket_id
from bot.senders import delete_private_thread, send_private_message_in_thread
from bot.validations.ticket_validation import validate_ticket
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
        )

    @commands.Cog.listener()
    async def on_member_reacted_to_ticket(self, member: discord.Member) -> None:
        """Called when a member reacts to the ticket message."""

        logger.info("Event on_member_reacted_to_ticket triggered.")

        if has_role(member, config.TICKET_HOLDER_ROLE_NAME):
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
            view=TicketView(member._user),
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
    @commands.has_role("members")
    async def ticket(self, ctx: commands.Context[commands.Bot], ticket_id: str = "") -> None:
        """Allows members to claim tickets by typing !ticket <ticket_id>."""

        logger.info(f"Ticket command received from {ctx.author.name}.")

        # Ensure command is used in a private ticket channel
        is_valid_thread = isinstance(ctx.channel, discord.Thread) and ctx.channel.name.startswith(
            config.TICKET_THREAD_PREFIX
        )
        if not is_valid_thread:
            await ctx.send(
                messages.INVALID_THREAD_MESSAGE.format(link=config.TICKET_MESSAGE_LINK),
                delete_after=10,
            )
            return
        if not isinstance(ctx.author, discord.Member):
            logger.warning("Author is not a member, ignoring ticket claim.")
            return
        if not ctx.guild:
            logger.warning("Guild is not available, ignoring ticket claim.")
            return

        # Ensure a ticket ID was given
        if not ticket_id:
            await ctx.send(messages.TICKET_ID_MISSING_MESSAGE)
            return

        # Remove the hashtag and/or whitespace from the ticket ID
        ticket_id = sanitize_ticket_id(ticket_id)

        # Ensure ticket ID is valid
        if not (ticket_id.isdigit() and len(ticket_id) == 10):
            await ctx.send(messages.INVALID_TICKET_ID_MESSAGE)
            logger.info(
                f"Member {ctx.author.name} ({ctx.author.id}) was denied a ticket."
                " The ticket was not 10 digits long or it was non numeric."
            )
            return

        ticket_validated = validate_ticket(ctx.author, ticket_id)
        if ticket_validated:
            await ctx.send(messages.TICKET_ACCEPTED_MESSAGE.format(name=ctx.author.mention))
        else:
            await ctx.send(messages.INVALID_TICKET_ID_MESSAGE, ephemeral=True, delete_after=10)
