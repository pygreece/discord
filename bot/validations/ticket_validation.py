import logging

import discord
from bot import db, config, messages
from bot.models import Member, Ticket
from bot.assign_role import assign_role
from bot.reactions import member_has_reacted_to_msg

logger = logging.getLogger(__name__)

async def validate_ticket(member: discord.Member, ticket_id: str) -> bool:
    """
    Process a ticket claim by a member.

    :param interaction: The interaction object from Discord.
    :param ticket_id: The ID of the ticket being claimed.
    """
    
    # Ensure a ticket ID was given
    if not ticket_id:
        logger.info("Ticket ID was not given.")
        return False

    async with db.get_session() as session:
        db_member, _ = await Member.get_or_create(id=member.id, session=session)
        db_ticket = await Ticket.get_by_id(int(ticket_id), session=session)

    # Ensure member has reacted to the CoC message
    if not db_member.reacted:
        if member_has_reacted_to_msg(member, config.COC_CHANNEL_ID, config.COC_MESSAGE_ID):
            db_member.reacted = True
            try:
                session.add(db_member)
                logger.info(f"Updated reacted=True for {member.name} ({member.id}) in database.")
            except Exception as e:
                logger.error(f"Error updating reacted for {member.name} ({member.id}): {e}")
                return False
        else:
            return False

    # Ensure ticket is in the database
    if not db_ticket:
        logger.info("Invalid ticket ID. Not found in db.")
        return False

    # Ensure ticket is not claimed
    if db_ticket.member_id and db_ticket.member_id != db_member.id:
        logger.warning(f"Member {member.name} ({member.id}) was denied a ticket."
                        " The ticket was already claimed.")
        return False
        
    elif db_ticket.member_id and db_ticket.member_id == db_member.id:
        logger.warning(f"Member {member.name} ({member.id}) was denied a ticket."
                        " They already claimed this ticket.")
        return False

    # Claim the ticket
    db_ticket.member_id = db_member.id
    async with db.get_session() as session:
        try:
            session.add(db_ticket)
            logger.info(f"Ticket {ticket_id} claimed by {member.name} ({member.id}) in database.")
        except Exception as e:
            logger.error(f"Error updating member_id for ticket {ticket_id} in database: {e}")
            return False

    return await assign_role(member, config.TICKET_HOLDER_ROLE_NAME)
