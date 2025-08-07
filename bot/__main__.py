import asyncio

import discord
from discord.ext import commands

from bot import welcome_and_coc_cog, utility_cog, config


async def main() -> None:
    """Main function to run the bot."""
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True

    discord.utils.setup_logging()
    bot = commands.Bot(command_prefix="!", intents=intents)
    await bot.add_cog(utility_cog.Utility(bot))
    await bot.add_cog(welcome_and_coc_cog.WelcomeAndCoC(bot))
    await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
