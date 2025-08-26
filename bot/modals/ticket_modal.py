import logging

import discord
from discord import Interaction, TextStyle, ui

from bot import config, exceptions, messages
from bot.roles import get_random_member_from_role
from bot.services.ticket_services import claim_ticket
from bot.validations.ticket_validation import can_claim_ticket

logger = logging.getLogger(__name__)


class TicketModal(ui.Modal, title="Verify your Ticket"):
    input_ticket_id = ui.TextInput(
        label="Ticket ID",
        style=TextStyle.short,
        placeholder="Enter your ticket ID",
        required=True,
        min_length=10,
        max_length=10,
        custom_id="ticket_id",
    )
    success = False

    async def on_submit(self, interaction: Interaction) -> None:
        """Called when the modal is submitted. Validates the entered ticket ID which claims the ticket if it is valid."""
        ticket_id = self.input_ticket_id.value

        # The view is only sent in private threads
        assert isinstance(interaction.channel, discord.Thread), "Channel was not a thread"
        # The view is only sent in private threads so there's always a guild involved
        assert interaction.guild is not None, "Guild was None"

        organizer_role = discord.utils.get(
            interaction.guild.roles, name=config.ORGANIZER_ROLE_NAME
        )
        if not organizer_role:
            self.success = False
            await interaction.response.send_message(
                messages.TICKET_GENERIC_ERROR_MESSAGE.format(role=f"@{config.ORGANIZER_ROLE_NAME}")
            )
            logger.error("The ticket modal could not find the organizer role.")
            return
        random_organizer = get_random_member_from_role(organizer_role)
        if not random_organizer:
            self.success = False
            await interaction.response.send_message(
                messages.TICKET_GENERIC_ERROR_MESSAGE.format(role=f"@{config.ORGANIZER_ROLE_NAME}")
            )
            logger.error("The ticket modal could not find a random organizer.")
            return
        try:
            member_can_claim_ticket = await can_claim_ticket(interaction.user, ticket_id)
        except exceptions.UserNotMemberException as e:
            self.success = False
            logger.error(
                f"Error claiming ticket for {interaction.user.name} ({interaction.user.id}): {e}"
            )
            return
        except exceptions.InvalidTicketIdException:
            self.success = False
            await interaction.response.send_message(
                messages.TICKET_INVALID_ID_MESSAGE, ephemeral=True, delete_after=10
            )
            return
        except exceptions.TicketHolderRoleAlreadyAssignedException:
            self.success = False
            await interaction.response.send_message(
                messages.TICKET_MEMBER_ALREADY_CLAIMED_MESSAGE, ephemeral=True, delete_after=10
            )
            return
        except exceptions.MemberHasNotReactedToCocException:
            self.success = False
            await interaction.response.send_message(
                messages.COC_NOT_ACCEPTED_MESSAGE.format(link=config.COC_MESSAGE_LINK),
                ephemeral=True,
                delete_after=10,
            )
            return
        except exceptions.TicketAlreadyClaimedException:
            self.success = False
            await interaction.channel.add_user(random_organizer)
            await interaction.response.send_message(
                messages.TICKET_MEMBER_ALREADY_CLAIMED_WITH_NO_ROLE_MESSAGE.format(
                    role=organizer_role.mention
                )
            )
            return
        except exceptions.TicketNotFoundInDatabaseException:
            self.success = False
            await interaction.channel.add_user(random_organizer)
            await interaction.response.send_message(
                messages.TICKET_NOT_FOUND_IN_DATABASE_MESSAGE.format(role=organizer_role.mention),
            )
            return
        except Exception as e:
            self.success = False
            await interaction.response.send_message(
                messages.TICKET_DB_ERROR_MESSAGE.format(role=organizer_role.mention)
            )
            logger.error(
                f"Error claiming ticket for {interaction.user.name} ({interaction.user.id}): {e}"
            )
            return

        if not member_can_claim_ticket:
            self.success = False
            await interaction.channel.add_user(random_organizer)
            await interaction.response.send_message(
                messages.TICKET_GENERIC_ERROR_MESSAGE.format(role=organizer_role.mention)
            )
            logger.error(
                f"Error claiming ticket for {interaction.user.name} ({interaction.user.id})"
            )
            return

        # can_claim_ticket() ensures that the user is a member
        assert isinstance(interaction.user, discord.Member), "User was not a member."

        try:
            member_claimed_ticket = await claim_ticket(interaction.user, int(ticket_id))
        except exceptions.RoleAssignmentFailedException:
            self.success = False
            await interaction.channel.add_user(random_organizer)
            await interaction.response.send_message(
                messages.TICKET_ROLE_ASSIGNMENT_ERROR_MESSAGE.format(role=organizer_role.mention)
            )
            return
        except Exception as e:
            self.success = False
            await interaction.channel.add_user(random_organizer)
            await interaction.response.send_message(
                messages.TICKET_DB_ERROR_MESSAGE.format(role=organizer_role.mention)
            )
            logger.error(
                f"Error claiming ticket for {interaction.user.name} ({interaction.user.id}): {e}"
            )
            return

        if not member_claimed_ticket:
            self.success = False
            await interaction.channel.add_user(random_organizer)
            await interaction.response.send_message(
                messages.TICKET_GENERIC_ERROR_MESSAGE.format(role=organizer_role.mention)
            )
            logger.error(
                f"Error claiming ticket for {interaction.user.name} ({interaction.user.id})"
            )
            return

        self.success = True
        await interaction.response.send_message(
            messages.TICKET_ACCEPTED_MESSAGE.format(name=interaction.user.mention)
        )
