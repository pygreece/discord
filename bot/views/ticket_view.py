import logging

import discord

from bot import config
from bot.messages import TICKET_FAILED_MESSAGE
from bot.modals.ticket_modal import TicketModal
from bot.views.base_view import BaseView
from bot.senders import delete_private_thread

logger = logging.getLogger(__name__)


class TicketView(BaseView):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.timeout = config.TICKET_MESSAGE_EXPIRES_AFTER  # 5 minutes timeout

    @discord.ui.button(
        label="Επικύρωσε το εισιτήριό σου! | Claim your ticket!",
        style=discord.ButtonStyle.blurple,
        custom_id="claim_ticket",
        emoji="🎟️",
    )
    async def button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ) -> None:
        modal = TicketModal(title="Επικύρωση Εισιτηρίου | Ticket Verification")
        await interaction.response.send_modal(modal)
        await modal.wait()
        if modal.success:
            button.label = "Το εισιτήριο επικυρώθηκε! | Ticket Claimed!"
            button.style = discord.ButtonStyle.success
            button.emoji = discord.PartialEmoji(name="✅")
            button.disabled = True
        else:
            button.label = "Προσπάθησε ξανά | Try again"
            button.emoji = discord.PartialEmoji(name="🔄")
        await self._edit(view=self)

    async def on_timeout(self) -> None:
        await delete_private_thread(
            config.TICKET_CHANNEL_ID,
            config.TICKET_THREAD_PREFIX,
            self.member,
            "ticket verification timed out",
        )
