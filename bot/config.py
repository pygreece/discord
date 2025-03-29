import os

from dotenv import load_dotenv

from bot.exceptions import IncorrectConfigException

load_dotenv()

empty = object()


def get_env_var(name: str, default: str = empty) -> str:
    """Get an environment variable, with optional default value"""

    value = os.getenv(name, default)
    if value is empty:
        raise IncorrectConfigException(f"{name} is not set")
    return value


def get_env_var_int(name: str, default: str = empty) -> int:
    """Get an environment variable as an integer, with optional default value"""
    value = get_env_var(name, default)
    try:
        return int(value)
    except ValueError:
        raise IncorrectConfigException(f"{name} must be an integer")


DATABASE_URL = get_env_var("DATABASE_URL")
DISCORD_TOKEN = get_env_var("DISCORD_TOKEN")
DISCORD_GUILD = get_env_var("DISCORD_GUILD")
MEMBER_ROLE_NAME = get_env_var("MEMBER_ROLE_NAME", "members")
COC_MESSAGE_ID = get_env_var_int("COC_MESSAGE_ID")
