import logging

import discord
from bot import db
from bot.models import Member
from bot.exceptions import RoleAssignmentFailedException
from bot.roles import assign_role
from bot.config import TICKET_HOLDER_ROLE_NAME

logger = logging.getLogger(__name__)

async def claim_ticket(member: discord.Member, ticket_id: int) -> bool:
    """
    Claims a ticket for a member.

    :discord.Member member: The discord member attempting to claim a ticket.
    :int ticket_id: The ticket ID to be claimed.
    
    :returns bool: True if the ticket was successfully claimed, False otherwise.
    """
    if not await assign_role(member, TICKET_HOLDER_ROLE_NAME):
        raise RoleAssignmentFailedException(f"Failed to assign {TICKET_HOLDER_ROLE_NAME} role to {member.name} ({member.id}).")
    
    async with db.get_session() as session:
        db_member, _ = await Member.get_or_create(member.id, session=session)
        db_member.ticket_id = ticket_id
        try:
            session.add(db_member)
        except Exception as e:
            logger.error(f"Error updating ticket_id for {member.name} ({member.id}): {e}")
            return False
    return True