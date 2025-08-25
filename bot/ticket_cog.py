import logging

import discord
from discord.ext import commands

from bot import config, exceptions, messages
from bot.roles import get_random_member_from_role, member_has_role
from bot.sanitizers import sanitize_ticket_id
from bot.senders import delete_private_thread, send_private_message_in_thread
from bot.services.ticket_services import claim_ticket
from bot.validations.ticket_validation import can_claim_ticket
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
    @commands.has_role(config.MEMBER_ROLE_NAME)
    async def ticket(self, ctx: commands.Context[commands.Bot], ticket_id: str = "") -> None:
        """Allows members to claim tickets by typing !ticket <ticket_id>."""

        # The decorator guild_only() explicitly ensures that ctx.guild is not None
        assert ctx.guild is not None, "This command can only be used in a guild."
        logger.info(f"Ticket command received from {ctx.author.name}.")

        # Ensure command is used in a private ticket channel
        is_valid_thread = (
            isinstance(ctx.channel, discord.Thread)
            and ctx.channel.parent_id == config.TICKET_CHANNEL_ID
        )
        if not is_valid_thread:
            await ctx.message.delete()
            await ctx.send(
                messages.TICKET_INVALID_THREAD_MESSAGE.format(link=config.TICKET_MESSAGE_LINK),
                ephemeral=True,
                delete_after=10,
            )
            logger.warning(
                f"Ticket command received from {ctx.author.name} in an invalid channel."
            )
            return

        assert isinstance(ctx.channel, discord.Thread), (
            "Ticket command must be used in a private thread."
        )
        assert isinstance(ctx.author, discord.Member), "Ticket command must be used by a member."

        if member_has_role(ctx.author, config.TICKET_HOLDER_ROLE_NAME):
            logger.info(
                f"Member {ctx.author.name} ({ctx.author.id}) already has the {config.TICKET_HOLDER_ROLE_NAME} role."
            )
            return

        organizer_role = discord.utils.get(ctx.guild.roles, name=config.ORGANIZER_ROLE_NAME)
        if not organizer_role:
            logger.error("The ticket cog could not find the organizer role.")
            return
        try:
            random_organizer = get_random_member_from_role(organizer_role)
        except exceptions.EmptyRoleException as e:
            logger.error(e)
            return

        # Remove the hashtag and/or whitespace from the ticket ID
        ticket_id = sanitize_ticket_id(ticket_id)
        try:
            member_can_claim_ticket = await can_claim_ticket(ctx.author, ticket_id)
        except exceptions.UserNotMemberException as e:
            logger.error(f"Error claiming ticket for {ctx.author.name} ({ctx.author.id}): {e}")
            return
        except exceptions.InvalidTicketIdException:
            await ctx.send(messages.TICKET_INVALID_ID_MESSAGE, ephemeral=True, delete_after=10)
            return
        except exceptions.TicketHolderRoleAlreadyAssignedException:
            await ctx.send(
                messages.TICKET_MEMBER_ALREADY_CLAIMED_MESSAGE, ephemeral=True, delete_after=10
            )
            return
        except exceptions.MemberHasNotReactedToCocException:
            await ctx.send(messages.COC_NOT_ACCEPTED_MESSAGE, ephemeral=True, delete_after=10)
            return
        except exceptions.TicketAlreadyClaimedException:
            await ctx.channel.add_user(random_organizer)
            await ctx.send(
                messages.TICKET_MEMBER_ALREADY_CLAIMED_WITH_NO_ROLE_MESSAGE.format(
                    role=organizer_role.mention
                )
            )
            return
        except exceptions.TicketNotFoundInDatabaseException:
            await ctx.channel.add_user(random_organizer)
            await ctx.send(
                messages.TICKET_NOT_FOUND_IN_DATABASE_MESSAGE.format(role=organizer_role.mention)
            )
            return
        except Exception as e:
            await ctx.channel.add_user(random_organizer)
            await ctx.send(messages.TICKET_DB_ERROR_MESSAGE.format(role=organizer_role.mention))
            logger.error(f"Error claiming ticket for {ctx.author.name} ({ctx.author.id}): {e}")
            return

        if not member_can_claim_ticket:
            await ctx.channel.add_user(random_organizer)
            await ctx.send(
                messages.TICKET_GENERIC_ERROR_MESSAGE.format(role=organizer_role.mention)
            )
            logger.error(f"Error claiming ticket for {ctx.author.name} ({ctx.author.id})")
            return

        try:
            member_claimed_ticket = await claim_ticket(ctx.author, int(ticket_id))
        except exceptions.RoleAssignmentFailedException:
            await ctx.channel.add_user(random_organizer)
            await ctx.send(
                messages.TICKET_ROLE_ASSIGNMENT_ERROR_MESSAGE.format(role=organizer_role.mention)
            )
            return
        except Exception as e:
            await ctx.channel.add_user(random_organizer)
            await ctx.send(messages.TICKET_DB_ERROR_MESSAGE.format(role=organizer_role.mention))
            logger.error(f"Error claiming ticket for {ctx.author.name} ({ctx.author.id}): {e}")
            return

        if not member_claimed_ticket:
            await ctx.channel.add_user(random_organizer)
            await ctx.send(
                messages.TICKET_GENERIC_ERROR_MESSAGE.format(role=organizer_role.mention)
            )
            logger.error(f"Error claiming ticket for {ctx.author.name} ({ctx.author.id})")
            return

        await ctx.send(messages.TICKET_ACCEPTED_MESSAGE.format(name=ctx.author.mention))
