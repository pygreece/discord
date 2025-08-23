import logging

import discord

from bot import config, db, exceptions
from bot.models import Member, Ticket
from bot.roles import member_has_role

logger = logging.getLogger(__name__)


async def can_claim_ticket(member: discord.Member | discord.User, ticket_id: str) -> bool:
    """
    Checks if a member can claim a ticket.

    :discord.Member member: The discord member attempting to claim a ticket.
    :str ticket_id: The ticket ID to be claimed as a string, since it is user provided input.
    
    :returns bool: True if the member can claim the ticket, False otherwise.
    """
    if not isinstance(member, discord.Member):
        raise exceptions.UserNotMemberException("User was not a member.")
    
    if not ticket_id or not ticket_id.isdigit() or len(ticket_id) != 10:
        raise exceptions.InvalidTicketIdException("Ticket ID must be a 10-digit number.")
    if member_has_role(member, config.TICKET_HOLDER_ROLE_NAME):
        raise exceptions.TicketHolderRoleAlreadyAssignedException("Member already has the ticket holder role.")

    async with db.get_session() as session:
        db_member, _ = await Member.get_or_create(member.id, session=session)
        if not db_member.reacted:
            raise exceptions.MemberHasNotReactedToCocException("Member has not reacted to the coc message.")
        if db_member.ticket:
            raise exceptions.TicketAlreadyClaimedException("Member has already claimed a ticket.")
        
        db_ticket = await Ticket.get_by_id(int(ticket_id), session=session)
        if not db_ticket:
            raise exceptions.TicketNotFoundInDatabaseException("Ticket not found in the database.")
    return True