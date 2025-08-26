import logging
from random import choice

import discord
from discord.utils import get as dget

from bot.exceptions import EmptyRoleException

logger = logging.getLogger(__name__)


async def assign_role(member: discord.Member, role_name: str) -> bool:
    """Assigns a role to the member if they don't already have it. Returns whether the role was assigned.

    :param discord.Member member: The member to assign the role to.
    :param str role_name: The name of the role to assign.

    :returns bool: True if the role was assigned or the member already has the role, False otherwise.
    """

    # Assign the "role_name" role
    guild = member.guild
    role = dget(guild.roles, name=role_name)
    if not role:
        logger.warning(f"Role '{role_name}' not found in the server.")
        return False
    if role in member.roles:
        logger.info(f"{member.name} ({member.id}) already has the '{role.name}' role.")
        return True

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


def member_has_role(member: discord.Member, role_name: str) -> bool:
    """Checks if the member has a specific role.

    :param discord.Member member: The member to check.
    :param str role_name: The name of the role to check for.

    :returns bool: True if the member has the role, False otherwise.
    """
    role = dget(member.roles, name=role_name)
    return role is not None


def get_random_member_from_role(role: discord.Role) -> discord.Member:
    """Returns a random online member from the specified role.

    :param discord.Role role: The role to get a random member from.

    :returns discord.Member: The random online member from the role.
    """
    if len(role.members) == 0:
        raise EmptyRoleException(f"No members found with the '{role.name}' role.")

    online_members = [member for member in role.members if member.status != discord.Status.offline]
    return choice(online_members) if online_members else choice(role.members)
