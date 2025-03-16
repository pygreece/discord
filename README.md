# discord

Repo dedicated to the discord setup of the PyGreece online community on Discord.

## Features

The bot

## Development

To run the bot locally:

1. Create an application on the Discord Developer portal.
1. Generate a token that has permissions to manage member roles.
1. Have the bot join a server.
1. Copy `.env.sample` into a new file called `.env`:
   ```
   DISCORD_TOKEN=<insert the token created above here>
   DISCORD_GUILD=<test server name>
   DATABASE_URL="sqlite+aiosqlite:///bot.db"  # Example name for local sqlite database
   MEMBER_ROLE_NAME="members"                 # Example role for membersß
   COC_MESSAGE_ID=1293819238                  # Example message id for COC message
   ```
1. Run `uv run alembic upgrade head` to create a local development
   `sqlite` database.
1. Run `uv run python -m bot` to run the bot.
