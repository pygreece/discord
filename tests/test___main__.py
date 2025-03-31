from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_intents():
    """Create a mock for discord.Intents.default()"""
    with patch("discord.Intents.default") as mock_intents_default:
        mock_intents = MagicMock()
        mock_intents_default.return_value = mock_intents
        yield mock_intents, mock_intents_default


@pytest.fixture
def mock_bot():
    """Create a mock for the PyGreeceBot class"""
    with patch("bot.bot.PyGreeceBot") as mock_bot_class:
        mock_bot_instance = MagicMock()
        mock_bot_class.return_value = mock_bot_instance
        yield mock_bot_instance, mock_bot_class


@patch("discord.utils.setup_logging")
@patch("bot.config.DISCORD_TOKEN", "mock_token")
def test_bot_initialization(mock_setup_logging, mock_bot, mock_intents):
    """Test that the bot is initialized with the correct parameters"""
    mock_bot_instance, mock_bot_class = mock_bot
    mock_intents_instance, mock_intents_default = mock_intents

    import bot.__main__  # noqa: F401

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

    # Verify bot.run was called with the token
    mock_bot_instance.run.assert_called_once_with("mock_token")
