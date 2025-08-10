import logging

import discord
from discord import Interaction, ui, TextStyle

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
    submitted_interaction: discord.Interaction | None = None
        
    async def on_submit(self, interaction: Interaction) -> None:
        ticket_id = self.input_ticket_id.value
        if not ticket_id.isdigit():
            await interaction.response.send_message("Invalid ticket ID. Wrong format.", ephemeral=True)
            return
        