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


DISCORD_TOKEN = get_env_var("DISCORD_TOKEN")
DISCORD_GUILD = get_env_var("DISCORD_GUILD")
ORGANIZER_ROLE_NAME = get_env_var("ORGANIZER_ROLE_NAME", "organizers")
DATABASE_URL = get_env_var("DATABASE_URL")
SPAM_COOLDOWN = get_env_var_int("SPAM_COOLDOWN", 5 * 60)  # Default to 5 minutes

MEMBER_ROLE_NAME = get_env_var("MEMBER_ROLE_NAME", "members")
COC_MESSAGE_LINK = get_env_var("COC_MESSAGE_LINK")
COC_MESSAGE_ID = int(COC_MESSAGE_LINK.split("/")[-1])
COC_CHANNEL_ID = int(COC_MESSAGE_LINK.split("/")[-2])
COC_THREAD_PREFIX = get_env_var("COC_THREAD_PREFIX", "welcome")

TICKET_HOLDER_ROLE_NAME = get_env_var("TICKET_HOLDER_ROLE_NAME", "ticketholders")
TICKET_MESSAGE_LINK = get_env_var("TICKET_MESSAGE_LINK")
TICKET_MESSAGE_ID = int(TICKET_MESSAGE_LINK.split("/")[-1])
TICKET_CHANNEL_ID = int(TICKET_MESSAGE_LINK.split("/")[-2])
TICKET_THREAD_PREFIX = get_env_var("TICKET_CHANNEL_PREFIX", "ticket-verification")
BOT_INTERACTIONS_CHANNEL_ID = get_env_var_int("BOT_INTERACTIONS_CHANNEL_ID")

ACCEPTABLE_REACTION_EMOJIS = [
    "👍",  # Thumbs up - approval
    "❤️",  # Heart - love and affection
    "✅",  # Check mark - confirmation
    "💯",  # 100 - perfection or strong approval
    "🎉",  # Party popper - celebration
    "😊",  # Smiling face - warmth and friendliness
    "😍",  # Smiling face with hearts - love and positivity
    "🤝",  # Handshake - agreement or partnership
    "🙌",  # Raising hands - celebration or success
    "🌟",  # Star - excellence or positivity
    "🤩",  # Star-struck – admiration and excitement
    "🧡",  # Orange heart – warmth and friendliness
    "💖",  # Sparkling heart - affection and positivity
    "🤗",  # Hugging face - acceptance and comfort
    "🌈",  # Rainbow - hope and inclusion
    "☀️",  # Sun - brightness and optimism
    "🕊️",  # Dove - peace and acceptance
    "🥰",  # Smiling face with hearts - love and positivity
]
