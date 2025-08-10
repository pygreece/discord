
import logging

from typing import Any
import discord
from discord.ui.select import BaseSelect

logger = logging.getLogger(__name__)

#Inspired by
#https://github.com/FallenDeity/discord.py-masterclass/blob/master/docs/views.md
class BaseView(discord.ui.View):
    interaction : discord.Interaction | None = None
    message: discord.Message | None = None
    
    def __init__(self, user: discord.User, timeout: float | None = None) -> None:
        """Called when the view is initialized."""
        super().__init__(timeout=timeout)
        # Set the user who invoked the command as the user who can interact with the view
        self.user = user
    
    async def interaction_check(self, interaction: discord.Interaction[discord.Client]) -> bool:
        """Called to check whether an interaction should be handled by this view."""
        # Only respond to interactions from the user who invoked the command that sent this view
        if interaction.user != self.user:
            await interaction.response.send_message(f"Only {self.user.mention} can use this view.", ephemeral=True)
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
            logger.info(f"View was never interacted with and the message before editing is {self.message} with content {self.message.content}")
            # If the view was never interacted with and the message attribute is not None, edit the message
            await self.message.edit(**kwargs)
            logger.info(f"View was never interacted with and the message is {self.message} with content {self.message.content}.")
        elif self.interaction is not None:
            try:
                # If the interaction has not yet been responded to, respond to it
                await self.interaction.response.edit_message(**kwargs)
                logger.info("Interaction not yet responded to.")
            except discord.InteractionResponded:
                # If the interaction has already been responded to, edit the original response
                await self.interaction.followup.send(**kwargs)
                logger.info("Interaction already responded to.")
                
    async def on_error(self, interaction: discord.Interaction[discord.Client], error: Exception, item: discord.ui.Item[Any]) -> None:
        message = f"A type ({type(error)}) occurred while processing this the interaction for {str(item)}: {error}"
        logger.error(message)
        self._disable_all()
        await self._edit(content=message, view=self)
        self.stop()
        return await super().on_error(interaction, error, item)
    
                
    async def on_timeout(self) -> None:
        self._disable_all()
        await self._edit(view=self)