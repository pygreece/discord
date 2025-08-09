import logging

import discord
from discord.ext import commands

from bot import config, db, messages
from bot.models import Member, Ticket
from bot.senders import send_private_message_in_thread, delete_private_thread
from bot.assign_role import assign_role
from bot.sanitizers import sanitize_ticket_id

logger = logging.getLogger(__name__)


class TicketVerification(commands.Cog):
    """The cog that implements ticket verification for the PyGreece Discord bot.

    This class implements functionality for handling ticket verifications. It sends messages to
    new members and members who react to the relevant ticket message and assigns the ticket holder
    role based on commands.
    """
    
    def __init__(self, bot: commands.Bot) -> None:
        """Initialize the cog with the bot instance."""
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
            f"private {config.TICKET_THREAD_PREFIX} thread"
        )
    
    @commands.Cog.listener()
    async def on_member_reacted_to_ticket(self, member: discord.Member) -> None:
        """Called when a member reacts to the ticket message."""

        logger.info("Event on_member_reacted_to_ticket triggered.")
        # Create the private thread
        await send_private_message_in_thread(
            config.TICKET_CHANNEL_ID,
            config.TICKET_THREAD_PREFIX,
            member,
            messages.ASK_FOR_TICKET_MESSAGE.format(name=member.mention),
            f"private {config.TICKET_THREAD_PREFIX} thread"
        )
        
    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        """Called when a member leaves the server."""

        await delete_private_thread(
            config.TICKET_CHANNEL_ID,
            config.TICKET_THREAD_PREFIX,
            member,
            f"member left the server",
        )
    
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_role("members")
    async def ticket(self, ctx: commands.Context[commands.Bot], ticket_id: str = "") -> None:
        """Allows members to claim tickets by typing !ticket <ticket_id>."""
        
        logger.info(f"Ticket command received from {ctx.author.name}.")
        
        # Ensure command is used in a private ticket channel
        is_valid_thread = (isinstance(ctx.channel, discord.Thread)
                           and ctx.channel.name.startswith(config.TICKET_THREAD_PREFIX))
        if not is_valid_thread:
            await ctx.send(messages.INVALID_THREAD_MESSAGE.format(link=config.TICKET_MESSAGE_LINK), delete_after=10)
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
        is_valid_ticket_id = ticket_id.isdigit() and len(ticket_id) == 10
        if not is_valid_ticket_id:
            await ctx.send(messages.INVALID_TICKET_ID_MESSAGE)
            logger.info(f"Member {ctx.author.name} ({ctx.author.id}) was denied a ticket."
                            " The ticket was not 10 digits long or it was non numeric.")
            return
        
        # Ensure member has reacted to the CoC message
        async with db.get_session() as session:
            db_member, _ = await Member.get_or_create(id=ctx.author.id, session=session)
            if not db_member.reacted:
                await ctx.send(messages.COC_NOT_ACCEPTED_MESSAGE.format(link=config.COC_MESSAGE_LINK))
                logger.info(f"Member {ctx.author.name} ({ctx.author.id}) was denied a ticket."
                                " They did not react to the CoC message.")
                return
        
            # Organizers might be notified for the next ticket denies
            og_role = discord.utils.get(ctx.guild.roles, name=config.ORGANIZER_ROLE_NAME)
            if og_role is None:
                logger.error("Organizer role not found.")
                og_mention = config.ORGANIZER_ROLE_NAME
            else:
                og_mention = og_role.mention
                
            # Ensure ticket is in the database
            db_ticket = await Ticket.get_by_id(id=int(ticket_id), session=session)
            if db_ticket is None:
                await ctx.send(messages.TICKET_NOT_FOUND_IN_DATABASE_MESSAGE.format(role=og_mention))
                logger.info(f"Member {ctx.author.name} ({ctx.author.id}) was denied a ticket."
                                " The ticket was not found in the database.")
                return
            if db_ticket.member_id is not None and db_ticket.member_id != db_member.id:
                await ctx.send(messages.TICKET_IN_USE_MESSAGE.format(role=og_mention))
                logger.info(f"Member {ctx.author.name} ({ctx.author.id}) was denied a ticket."
                                " The ticket was already claimed.")
                return
            elif db_ticket.member_id is not None and db_ticket.member_id == db_member.id:
                await ctx.send(messages.TICKET_DOUBLE_CLAIM_MESSAGE)
                logger.info(f"Member {ctx.author.name} ({ctx.author.id}) was denied a ticket."
                                " They already claimed this ticket.")
                return
            
            # Claim the ticket
            db_ticket.member_id = db_member.id
            try:
                session.add(db_ticket)
                logger.info(f"Ticket {ticket_id} claimed by {ctx.author.name} ({ctx.author.id}) in database.")
            except Exception as e:
                await ctx.send(messages.TICKET_DB_ERROR_MESSAGE.format(role=og_mention))
                logger.error(f"Error updating member_id for ticket {ticket_id}: {e}")
                return
        
        if await assign_role(ctx.author, config.TICKET_HOLDER_ROLE_NAME):
            logger.info(f"Assigned '{config.TICKET_HOLDER_ROLE_NAME}' role to {ctx.author} ({ctx.author.id}).")
            await ctx.send(messages.TICKET_ACCEPTED_MESSAGE.format(name=ctx.author.mention))
        else:
            logger.error(f"Failed to assign '{config.TICKET_HOLDER_ROLE_NAME}' role to {ctx.author} ({ctx.author.id}).")
            await ctx.send(messages.TICKET_ROLE_ASSIGNMENT_ERROR.format(role=og_mention))