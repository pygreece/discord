import logging

import discord
from discord.utils import get as dget

logger = logging.getLogger(__name__)


async def assign_role(member: discord.Member, role_name: str) -> None:
    """Assigns a role to the member if they don't already have it."""

    # Assign the "role_name" role
    guild = member.guild
    role = dget(guild.roles, name=role_name)
    if role:
        if role not in member.roles:
            await member.add_roles(role)
            logger.info(f"Assigned '{role.name}' role to {member.name} ({member.id}).")
        else:
            logger.info(f"{member.name} ({member.id}) already has the '{role.name}' role.")
    else:
        logger.warning(f"Role '{role_name}' not found in the server.")
