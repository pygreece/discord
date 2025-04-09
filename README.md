[![Run Tests](https://github.com/pygreece/discord/actions/workflows/test.yml/badge.svg)](https://github.com/pygreece/discord/actions/workflows/test.yml)
[![codecov](https://codecov.io/github/pygreece/discord/graph/badge.svg?token=TRIHAIZE7D)](https://codecov.io/github/pygreece/discord)

# PyGreece Discord Bot 🤖

A Discord bot for the PyGreece online community that handles member onboarding through a Code of Conduct acceptance flow.

## ✨ Features

- 👋 Automatically sends welcome messages to new members
- 📜 Implements a Code of Conduct acceptance workflow
- 🏷️ Assigns roles when members react to the Code of Conduct message
- 🗄️ Tracks member status in a database

## 🔧 Requirements

- 🐍 Python 3.12+
- 🐘 PostgreSQL database (for production)
- 🔑 Discord Bot Token

## 🚀 Setup

### Discord Application

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Create a new application
3. Go to the "Bot" tab and create a bot
4. Enable the "Server Members Intent" under Privileged Gateway Intents
5. Copy the bot token for configuration

### Environment Configuration

1. Copy `.env.sample` to a new file called `.env`:
   ```
   DISCORD_TOKEN=<your-discord-bot-token>
   DISCORD_GUILD=<your-discord-server-name>
   DATABASE_URL=postgresql+asyncpg://<username>:<password>@postgres/<db>
   MEMBER_ROLE_NAME=members
   COC_MESSAGE_ID=<message-id-of-code-of-conduct>
   COC_MESSAGE_LINK=<message-link-of-code-of-conduct>
   ```

2. Replace the placeholder values with your actual configuration

### Local Development

1. Clone the repository
   ```bash
   git clone https://github.com/pygreece/discord.git
   cd discord
   ```

2. Install dependencies with `uv`
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   uv sync
   ```

### Docker Deployment 🐳

The project includes Docker configuration for easy local deployment:

```bash
docker-compose up -d
```

## 📁 Project Structure

- `bot/`: Main bot code
  - `__main__.py`: Entry point
  - `cog.py`: Core bot functionality
  - `models.py`: Database models
  - `db.py`: Database connection management
  - `config.py`: Configuration handling
  - `exceptions.py`: Custom exceptions
- `tests/`: Test suite
- `alembic/`: Database migrations

## 🧪 Testing

Run the test suite:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov
```

## 👥 Contributing

1. Fork the repository
2. Create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Run tests and make sure they pass ✅
5. Push your branch and create a pull request

## 💬 Code of Conduct

This project follows the [PyGreece code of conduct](https://pygreece.org/code-of-conduct/).
Please be respectful and inclusive when contributing to this project.
