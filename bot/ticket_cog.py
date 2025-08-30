import logging

import discord
from discord.ext import commands

from bot import config, messages
from bot.roles import member_has_role
from bot.senders import delete_private_thread, send_private_message_in_thread
from bot.views.ticket_view import TicketView

logger = logging.getLogger(__name__)


class TicketVerification(commands.Cog):
    """Commands related to the ticket verification system."""

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
        """Claim tickets by typing !ticket to start a thread. | Επικύρωσε το εισιτήριό σου γράφοντας !ticket για να ξεκινήσεις ένα νήμα.

        Click the button in the private thread created by the bot
        to claim your ticket and join the event channels. 
        You need to have reacted to the coc message and 
        have the community member role in order to use this command.
        
        Κάνε κλικ στο κουμπί στο προσωπικό νήμα που δημιουργεί το bot 
        για να επικυρώσεις το εισιτήριό σου και να αποκτήσεις πρόσβαση στα κανάλια της εκδήλωσης. 
        Θα πρέπει να έχεις αντιδράσει στον κώδικα δεοντολογίας και 
        να έχεις το ρόλο community member για να χρησιμοποιήσεις αυτήν την εντολή.
        """

        assert ctx.guild is not None, "This command can only be used in a guild."
        assert isinstance(ctx.author, discord.Member), "Ticket command must be used by a member."

        if not member_has_role(ctx.author, config.MEMBER_ROLE_NAME):
            await ctx.message.delete()
            await ctx.reply(
                messages.COC_NOT_ACCEPTED_MESSAGE.format(link=config.COC_MESSAGE_LINK),
                ephemeral=True,
                delete_after=30,
            )
            logger.info(
                f"Member {ctx.author.name} ({ctx.author.id}) does not have the {config.MEMBER_ROLE_NAME} role."
                f"Ticket command ignored."
            )
            return

        if member_has_role(ctx.author, config.TICKET_HOLDER_ROLE_NAME):
            await ctx.message.delete()
            await ctx.reply(
                messages.TICKET_MEMBER_ALREADY_CLAIMED_MESSAGE, ephemeral=True, delete_after=30
            )
            logger.info(
                f"Member {ctx.author.name} ({ctx.author.id}) already has the {config.TICKET_HOLDER_ROLE_NAME} role."
                f"Ticket command ignored."
            )
            return

        if ctx.channel.id != config.BOT_INTERACTIONS_CHANNEL_ID:
            bot_channel = self.bot.get_channel(config.BOT_INTERACTIONS_CHANNEL_ID)
            if not (bot_channel and isinstance(bot_channel, discord.TextChannel)):
                logger.error("Could not find the bot interactions channel.")
                return

            await ctx.message.delete()
            await ctx.send(
                messages.TICKET_INVALID_CHANNEL_MESSAGE.format(channel=bot_channel.mention),
                ephemeral=True,
                delete_after=30,
            )
            logger.warning(
                f"Ticket command received from {ctx.author.name} in an invalid channel."
            )
            return

        logger.info(
            f"Ticket command received from {ctx.author.name} ({ctx.author.id}) in the bot interactions channel."
        )

        await send_private_message_in_thread(
            config.TICKET_CHANNEL_ID,
            config.TICKET_THREAD_PREFIX,
            ctx.author,
            messages.ASK_FOR_TICKET_MESSAGE.format(name=ctx.author.mention),
            f"private {config.TICKET_THREAD_PREFIX} thread",
            view=TicketView(ctx.author),
        )
