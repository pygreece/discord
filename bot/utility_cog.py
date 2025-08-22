import datetime
import logging

import discord
from discord.ext import commands
from sqlalchemy import select

from bot import db

logger = logging.getLogger(__name__)


class Utility(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.start_time = datetime.datetime.now(datetime.timezone.utc)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        """Called when the bot is ready."""
        logger.info("PyGreece bot is now logged in")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx: commands.Context[commands.Bot]) -> None:
        """Sync the command tree with the guild."""
        logger.info("Received sync command.")
        assert ctx.guild is not None
        self.bot.tree.copy_global_to(guild=discord.Object(ctx.guild.id))
        await self.bot.tree.sync(guild=discord.Object(ctx.guild.id))
        await ctx.reply("Command tree synced.")

    @commands.hybrid_command()  # type: ignore
    @commands.guild_only()
    @commands.has_role("pygreece organizers")
    async def health(self, ctx: commands.Context[commands.Bot]) -> None:
        """Send the bot's health status."""
        logger.info("Received health check command.")

        embed = discord.Embed(
            title="Bot Health Status",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc),
        )

        # Discord connection
        latency = round(self.bot.latency * 1000)
        embed.add_field(name="Discord Connection", value=f"Latency: {latency}ms", inline=False)

        # Database connection
        try:
            async with db.get_session() as session:
                # Simple query to test connection
                await session.execute(select(1))
                embed.add_field(name="Database Connection", value="✅ Connected", inline=False)
        except Exception as e:
            embed.add_field(name="Database Connection", value=f"❌ Error: {str(e)}", inline=False)

        # Uptime
        uptime = datetime.datetime.now(datetime.timezone.utc) - self.start_time
        days, remainder = divmod(int(uptime.total_seconds()), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
        embed.add_field(name="Uptime", value=uptime_str, inline=False)

        await ctx.send(embed=embed)
