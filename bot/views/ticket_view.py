import logging

import discord
from bot import db, config, messages
from bot.models import Ticket, Member
from bot.views.base_view import BaseView
from bot.modals.ticket_modal import TicketModal
from bot.reactions import member_has_reacted
from bot.assign_role import assign_role

logger = logging.getLogger(__name__)

class TicketView(BaseView):
    @discord.ui.button(
        label="Επικύρωσε το εισιτήριό σου! | Claim your ticket!", 
        style=discord.ButtonStyle.blurple, 
        custom_id="claim_ticket"
    )
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.message:
            logger.warning("Message is not available, ignoring ticket claim.")
            return
        if not isinstance(interaction.user, discord.Member):
            logger.warning("User is not a member, ignoring ticket claim.")
            return
        if not interaction.guild:
            logger.warning("Guild is not available, ignoring ticket claim.")
            return
        
        modal = TicketModal(title="Επικύρωση Εισιτηρίου | Ticket Verification")
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        ticket_id = modal.input_ticket_id.value
        
        # Ensure a ticket ID was given
        if not ticket_id:
            self.message.content = messages.TICKET_ID_MISSING_MESSAGE
            await self._edit(view=self)
            logger.info("Ticket ID was not given.")
            return
        
        async with db.get_session() as session:
            db_member, _ = await Member.get_or_create(id=interaction.user.id, session=session)
            # Ensure member has reacted to the CoC message
            if not db_member.reacted:
                if member_has_reacted(interaction.user, config.COC_CHANNEL_ID, config.COC_MESSAGE_ID):
                    db_member.reacted = True
                    try:
                        session.add(db_member)
                        logger.info(f"Updated reacted=True for {interaction.user.name} ({interaction.user.id}) in database.")
                    except Exception as e:
                        logger.error(f"Error updating reacted for {interaction.user.name} ({interaction.user.id}): {e}")
                        return
                else:
                    await interaction.response.send_message("You have not reacted to the Code of Conduct message.", ephemeral=True)
                    return
            # Organizers might be notified for the next ticket denies
            og_role = discord.utils.get(interaction.guild.roles, name=config.ORGANIZER_ROLE_NAME)
            if og_role is None:
                logger.error("Organizer role not found.")
                og_mention = config.ORGANIZER_ROLE_NAME
            else:
                og_mention = og_role.mention 
            
            # Ensure ticket is in the database
            db_ticket = await Ticket.get_by_id(int(ticket_id), session=session)
            if not db_ticket:
                self.message.content = "Invalid ticket ID. Not found in db."
                await self._edit(view=self)
                logger.info("Invalid ticket ID. Not found in db.")
                return
            # Ensure ticket is not claimed
            if db_ticket.member_id and db_ticket.member_id != db_member.id:
                self.message.content = messages.TICKET_IN_USE_MESSAGE.format(role=og_mention)
                logger.warning(f"Member {interaction.user.name} ({interaction.user.id}) was denied a ticket."
                                " The ticket was already claimed.")
                await self._edit(view=self)
                return
            elif db_ticket.member_id and db_ticket.member_id == db_member.id:
                self.message.content = messages.TICKET_DOUBLE_CLAIM_MESSAGE
                logger.warning(f"Member {interaction.user.name} ({interaction.user.id}) was denied a ticket."
                                " They already claimed this ticket.")
                await self._edit(view=self)
                return
            
            # Claim the ticket
            db_ticket.member_id = db_member.id
            try:
                session.add(db_ticket)
                logger.info(f"Ticket {ticket_id} claimed by {interaction.user.name} ({interaction.user.id}) in database.")
            except Exception as e:
                logger.error(f"Error updating member_id for ticket {ticket_id} in database: {e}")
                return
        self.message.content = f"Ticket claimed! {og_mention} θα κανουν εναντια τον {interaction.user.mention}."
        
        if await assign_role(interaction.user, config.TICKET_HOLDER_ROLE_NAME):
            self.message.content = messages.TICKET_ACCEPTED_MESSAGE.format(name=interaction.user.mention)
            logger.info(f"Assigned '{config.TICKET_HOLDER_ROLE_NAME}' role to {interaction.user} ({interaction.user.id}).")
        else:
            self.message.content = messages.TICKET_ROLE_ASSIGNMENT_ERROR.format(role=og_mention)
            logger.error(f"Error assigning '{config.TICKET_HOLDER_ROLE_NAME}' role to {interaction.user} ({interaction.user.id}).")
        button.style = discord.ButtonStyle.success
        button.label = "Ticket Claimed!"
        button.disabled = True
        await self._edit(view=self)
        self.stop()
    