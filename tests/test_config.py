import importlib
import os
from unittest.mock import patch

import pytest

from bot import config
from bot.exceptions import IncorrectConfigException


@patch.dict(os.environ, {"TEST_VAR": "test_value"})
def test_get_env_var_with_value() -> None:
    """Test that get_env_var returns the value when set"""
    assert config.get_env_var("TEST_VAR") == "test_value"


@patch.dict(os.environ, {}, clear=True)
def test_get_env_var_with_default() -> None:
    """Test that get_env_var returns the default when var is not set"""
    assert config.get_env_var("TEST_VAR", "default_value") == "default_value"


@patch.dict(os.environ, {}, clear=True)
def test_get_env_var_missing_no_default() -> None:
    """Test that get_env_var raises an exception when var is not set and no default"""
    with pytest.raises(IncorrectConfigException, match="TEST_VAR is not set"):
        config.get_env_var("TEST_VAR")


@patch.dict(os.environ, {"TEST_INT": "42"})
def test_get_env_var_int_with_value() -> None:
    """Test that get_env_var_int returns the value as int when set"""
    assert config.get_env_var_int("TEST_INT") == 42


@patch.dict(os.environ, {}, clear=True)
def test_get_env_var_int_with_default() -> None:
    """Test that get_env_var_int returns the default when var is not set"""
    assert config.get_env_var_int("TEST_INT", 42) == 42


@patch.dict(os.environ, {}, clear=True)
def test_get_env_var_int_missing_no_default() -> None:
    """Test that get_env_var_int raises an exception when var is not set and no default"""
    with pytest.raises(IncorrectConfigException, match="TEST_INT is not set"):
        config.get_env_var_int("TEST_INT")


@patch.dict(os.environ, {"TEST_INT": "not_an_int"})
def test_get_env_var_int_not_integer() -> None:
    """Test that get_env_var_int raises an exception when var is not an integer"""
    with pytest.raises(
        IncorrectConfigException, match="TEST_INT must be an integer, got not_an_int"
    ):
        config.get_env_var_int("TEST_INT")


@patch.dict(
    os.environ,
    {
        "DATABASE_URL": "postgresql://user:pass@localhost/db",
        "DISCORD_TOKEN": "test_token",
        "DISCORD_GUILD": "test_guild",
        "MEMBER_ROLE_NAME": "custom_members",
        "COC_MESSAGE_ID": "123456789",
    },
)
def test_config_variables() -> None:
    """Test that all required environment variables are set"""
    importlib.reload(config)

    # Verify all config variables have the expected values
    assert config.DATABASE_URL == "postgresql://user:pass@localhost/db"
    assert config.DISCORD_TOKEN == "test_token"
    assert config.DISCORD_GUILD == "test_guild"
    assert config.MEMBER_ROLE_NAME == "custom_members"
    assert config.COC_MESSAGE_ID == 123456789


@patch.dict(
    os.environ,
    {
        "DATABASE_URL": "postgresql://user:pass@localhost/db",
        "DISCORD_TOKEN": "test_token",
        "DISCORD_GUILD": "test_guild",
        "COC_MESSAGE_ID": "123456789",
    },
)
def test_member_role_name_default() -> None:
    """Test that MEMBER_ROLE_NAME uses the default value when not set"""
    # Reload the config module
    importlib.reload(config)

    # Verify MEMBER_ROLE_NAME uses default
    assert config.MEMBER_ROLE_NAME == "members"
