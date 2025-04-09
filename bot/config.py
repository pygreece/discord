import os

from dotenv import load_dotenv

from bot.exceptions import IncorrectConfigException

load_dotenv()


def get_env_var(name: str, default: str | None = None) -> str:
    """Get an environment variable, with optional default value"""

    value = os.getenv(name, default)
    if value is None:
        raise IncorrectConfigException(f"{name} is not set")
    return value


def get_env_var_int(name: str, default: int | None = None) -> int:
    """Get an environment variable as an integer, with optional default value"""
    value = os.getenv(name, default)
    if value is None:
        raise IncorrectConfigException(f"{name} is not set")

    try:
        return int(value)
    except ValueError:
        raise IncorrectConfigException(f"{name} must be an integer, got {value}")


DATABASE_URL = get_env_var("DATABASE_URL")
DISCORD_TOKEN = get_env_var("DISCORD_TOKEN")
DISCORD_GUILD = get_env_var("DISCORD_GUILD")
MEMBER_ROLE_NAME = get_env_var("MEMBER_ROLE_NAME", "members")
COC_MESSAGE_ID = get_env_var_int("COC_MESSAGE_ID")
COC_MESSAGE_LINK = get_env_var("COC_MESSAGE_LINK")
