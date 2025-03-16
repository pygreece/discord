import os

from dotenv import load_dotenv

from bot.exceptions import IncorrectConfigException

load_dotenv()

try:
    DATABASE_URL = os.environ["DATABASE_URL"]
except KeyError:
    raise IncorrectConfigException("DATABASE_URL is not set")

try:
    DISCORD_TOKEN: str = os.environ["DISCORD_TOKEN"]
except KeyError:
    raise IncorrectConfigException("DISCORD_TOKEN is not set")

try:
    DISCORD_GUILD = os.environ["DISCORD_GUILD"]
except KeyError:
    raise IncorrectConfigException("DISCORD_GUILD is not set")

MEMBER_ROLE_NAME = os.getenv("MEMBER_ROLE_NAME", "members")

_COC_MESSAGE_ID_ENV = os.getenv("COC_MESSAGE_ID")
COC_MESSAGE_ID = None
if _COC_MESSAGE_ID_ENV is not None:
    COC_MESSAGE_ID = int(_COC_MESSAGE_ID_ENV)
