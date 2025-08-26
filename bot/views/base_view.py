import logging
from typing import Any

import discord
from discord.ui.select import BaseSelect

logger = logging.getLogger(__name__)


# Inspired by
# https://github.com/FallenDeity/discord.py-masterclass/blob/master/docs/views.md
class BaseView(discord.ui.View):
    interaction: discord.Interaction | None = None
    message: discord.Message | None = None

    def __init__(self, member: discord.Member, timeout: float | None = None) -> None:
        """Called when the view is initialized."""
        super().__init__(timeout=timeout)
        # Set the member who invoked the command as the member who can interact with the view
        self.member = member

    async def interaction_check(self, interaction: discord.Interaction[discord.Client]) -> bool:
        """Called to check whether an interaction should be handled by this view."""
        # Only respond to interactions from the member who invoked the command that sent this view
        if interaction.user.id != self.member.id:
            await interaction.response.send_message(
                f"Only {self.member.mention} can use this view.", ephemeral=True
            )
            return False
        self.interaction = interaction
        return True

    def _disable_all(self) -> None:
        """Disable all buttons in the view."""
        for item in self.children:
            if isinstance(item, discord.ui.Button) or isinstance(item, BaseSelect):
                item.disabled = True

    async def _edit(self, **kwargs) -> None:
        """Edit the message this view is attached to."""
        if self.interaction is None and self.message is not None:
            # If the view was never interacted with and the message attribute is not None, edit the message
            await self.message.edit(**kwargs)
        elif self.interaction is not None:
            try:
                # If the interaction has not yet been responded to, respond to it
                await self.interaction.response.edit_message(**kwargs)
            except discord.InteractionResponded:
                # If the interaction has already been responded to, edit the original response
                await self.interaction.edit_original_response(**kwargs)

    async def on_error(
        self,
        interaction: discord.Interaction[discord.Client],
        error: Exception,
        item: discord.ui.Item[Any],
    ) -> None:
        message = f"A type ({type(error)}) occurred while processing interaction {interaction} for {str(item)}: {error}"
        logger.error(message)
        self._disable_all()
        await self._edit(content=message, view=self)
        self.stop()
        return await super().on_error(interaction, error, item)

    async def on_timeout(self) -> None:
        self._disable_all()
        await self._edit(view=self)
