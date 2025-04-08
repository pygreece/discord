import asyncio

import discord
from discord.ext import commands

from bot import cog, config


async def main() -> None:
    """Main function to run the bot."""
    intents = discord.Intents.default()
    intents.members = True

    discord.utils.setup_logging()
    bot = commands.Bot(command_prefix="/", intents=intents)
    await bot.add_cog(cog.WelcomeAndCoC(bot))
    await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
