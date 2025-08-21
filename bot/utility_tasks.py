import logging
from datetime import datetime, timedelta, timezone
from discord.ext import tasks
from bot.config import TICKET_MESSAGE_EXPIRES_AFTER

logger = logging.getLogger(__name__)

class AntiSpamTask:
    def __init__(self, bot, expiry_seconds=TICKET_MESSAGE_EXPIRES_AFTER):
        self.bot = bot
        self.recent_reactors = {}  # {message_id: {user_id: timestamp}}
        self.expiry_time = timedelta(seconds=expiry_seconds)
        self.cleanup_loop.start()

    def record_reactor(self, message_id: int, user_id: int):
        """Record a reaction timestamp for a specific message and user."""
        if message_id not in self.recent_reactors:
            self.recent_reactors[message_id] = {}
        self.recent_reactors[message_id][user_id] = datetime.now(timezone.utc)
        logger.info(f"Recorded reactor for message {message_id}, user {user_id} at {self.recent_reactors[message_id][user_id]}")

    def is_on_cooldown(self, message_id: int, user_id: int) -> bool:
        """Check if the user is still on cooldown for a specific message."""
        user_times = self.recent_reactors.get(message_id, {})
        # If it's been 5 minutes since the last reaction, consider it expired
        # even if the user is still in the dictionary
        last_reacted = user_times.get(user_id, datetime.min.replace(tzinfo=timezone.utc))
        return (datetime.now(timezone.utc) - last_reacted) < self.expiry_time

    @tasks.loop(seconds=60)
    async def cleanup_loop(self):
        now = datetime.now(timezone.utc)
        for message_id in list(self.recent_reactors.keys()):
            self.recent_reactors[message_id] = {
                user_id: timestamp for user_id, timestamp in self.recent_reactors[message_id].items() 
                if (now - timestamp) < self.expiry_time
            }
            # Remove the message_id dict if no users are left
            if not self.recent_reactors[message_id]:
                del self.recent_reactors[message_id]

    # Uncomment to run the cleanup loop on cog load
    # a prerequisite if fetching data from the discord api in the task
    # https://github.com/FallenDeity/discord.py-masterclass/blob/master/docs/tasks.md
    # @cleanup_loop.before_loop
    # async def before_cleanup(self):
    #     await self.bot.wait_until_ready()