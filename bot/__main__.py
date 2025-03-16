import discord

from bot import config
from bot.bot import PyGreeceBot

intents = discord.Intents.default()
intents.members = True

discord.utils.setup_logging()
bot = PyGreeceBot(command_prefix="!", intents=intents)
bot.run(config.DISCORD_TOKEN)
