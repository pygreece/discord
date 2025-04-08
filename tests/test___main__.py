from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.__main__ import main


@pytest.fixture
def mock_intents() -> Generator[tuple[MagicMock, MagicMock], None, None]:
    """Create a mock for discord.Intents.default()"""
    with patch("discord.Intents.default") as mock_intents_default:
        mock_intents = MagicMock()
        mock_intents_default.return_value = mock_intents
        yield mock_intents, mock_intents_default


@pytest.fixture
def mock_bot() -> Generator[tuple[MagicMock, MagicMock], None, None]:
    """Create a mock for the PyGreeceBot class"""
    with patch("discord.ext.commands.Bot") as mock_bot_class:
        mock_bot_instance = AsyncMock()
        mock_bot_class.return_value = mock_bot_instance
        yield mock_bot_instance, mock_bot_class


@pytest.fixture
def mock_cog() -> Generator[tuple[MagicMock, MagicMock], None, None]:
    """Create a mock for the WelcomeAndCoC cog"""
    with patch("bot.cog.WelcomeAndCoC") as mock_cog_class:
        mock_cog_instance = MagicMock()
        mock_cog_class.return_value = mock_cog_instance
        yield mock_cog_instance, mock_cog_class


@patch("discord.utils.setup_logging")
@patch("bot.config.DISCORD_TOKEN", "mock_token")
async def test_bot_initialization(
    mock_setup_logging: MagicMock,
    mock_bot: tuple[AsyncMock, MagicMock],
    mock_cog: tuple[MagicMock, MagicMock],
    mock_intents: tuple[MagicMock, MagicMock],
) -> None:
    """Test that the bot is initialized with the correct parameters"""
    mock_bot_instance, mock_bot_class = mock_bot
    mock_cog_instance, mock_cog_class = mock_cog
    mock_intents_instance, mock_intents_default = mock_intents

    await main()

    # Verify Discord logging was set up
    mock_setup_logging.assert_called_once()

    # Verify intents were properly configured
    mock_intents_default.assert_called_once()
    assert mock_intents_instance.members

    # Verify bot was initialized correctly
    mock_bot_class.assert_called_once()
    _, kwargs = mock_bot_class.call_args
    assert kwargs["command_prefix"] == "!"
    assert kwargs["intents"] == mock_intents_instance

    # Verify the cog was initialized with the bot instance
    mock_cog_class.assert_called_once_with(mock_bot_instance)

    # Verify the cog was added to the bot
    mock_bot_instance.add_cog.assert_called_once_with(mock_cog_instance)

    # Verify bot.run was called with the token
    mock_bot_instance.start.assert_called_once_with("mock_token")
