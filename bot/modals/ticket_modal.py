import logging

import discord
from discord import Interaction, ui, TextStyle
from bot.validations.ticket_validation import validate_ticket
from bot import messages

logger = logging.getLogger(__name__)

class TicketModal(ui.Modal, title="Verify your Ticket"):
    input_ticket_id = ui.TextInput(
        label="Ticket ID", 
        style=TextStyle.short, 
        placeholder="Enter your ticket ID", 
        required=True, 
        min_length=10, 
        max_length=10,
        custom_id="ticket_id"
    )
    success = False
        
    async def on_submit(self, interaction: Interaction) -> None:
        """Called when the modal is submitted. Validates the entered ticket ID which claims the ticket if it is valid."""
        ticket_id = self.input_ticket_id.value
        if not ticket_id:
            await interaction.response.send_message(messages.TICKET_ID_MISSING_MESSAGE, ephemeral=True, delete_after=10)
        if not ticket_id.isdigit():
            await interaction.response.send_message(messages.INVALID_TICKET_ID_MESSAGE, ephemeral=True, delete_after=10)
            return
            
        if not isinstance(interaction.user, discord.Member):
            logger.info("Member missing, ignoring ticket claim.")
            return
        
        self.success = await validate_ticket(interaction.user, ticket_id)
        if self.success:
            await interaction.response.send_message(messages.TICKET_ACCEPTED_MESSAGE.format(name=interaction.user.mention))
        else:
            await interaction.response.send_message(messages.INVALID_TICKET_ID_MESSAGE, ephemeral=True, delete_after=10)
            