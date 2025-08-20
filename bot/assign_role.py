import logging

import discord
from discord.utils import get as dget

logger = logging.getLogger(__name__)


async def assign_role(member: discord.Member, role_name: str) -> bool:
    """Assigns a role to the member if they don't already have it. Returns whether the role was assigned.

    :param discord.Member member: The member to assign the role to.
    :param str role_name: The name of the role to assign.

    :returns bool: True if the role was assigned, False otherwise.
    """

    # Assign the "role_name" role
    guild = member.guild
    role = dget(guild.roles, name=role_name)
    if not role:
        logger.warning(f"Role '{role_name}' not found in the server.")
        return False
    if role in member.roles:
        logger.info(f"{member.name} ({member.id}) already has the '{role.name}' role.")
        return False

    try:
        await member.add_roles(role)
        logger.info(f"Assigned '{role.name}' role to {member.name} ({member.id}).")
        return True
    except discord.Forbidden:
        logger.error(
            f"Failed to assign '{role.name}' role to {member.name} ({member.id}) due to insufficient permissions."
        )
    except discord.HTTPException as e:
        logger.error(f"Failed to assign '{role.name}' role to {member.name} ({member.id}): {e}")
    return False
