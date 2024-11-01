"""Tests for the __init__ module."""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from custom_components.creality_box_control import (
    async_reload_entry,
    async_setup_entry,
    async_unload_entry,
)


# This fixture is used to enable custom integrations, otherwise the custom_components
# folder will not be loaded.
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None):  # noqa: ANN001, ANN201, ARG001
    """Enable custom integrations."""
    return


@pytest.fixture(autouse=True)
def skip_first_refresh() -> Generator:
    """Skip the first refresh."""
    with patch(
        "custom_components.creality_box_control.coordinator.CrealityBoxDataUpdateCoordinator.async_config_entry_first_refresh",
        return_value=None,
    ) as mock:
        yield mock

async def test_async_setup_entry(hass: HomeAssistant) -> None:
    """Test the async_setup_entry function."""
    entry = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    entry.add_update_listener = MagicMock()

    with (
        patch(
            "custom_components.creality_box_control.CrealityBoxDataUpdateCoordinator"
        ) as mock_coordinator,
        patch(
            "custom_components.creality_box_control.async_get_loaded_integration"
        ) as mock_get_loaded_integration,
    ):
        mock_coordinator.return_value.async_config_entry_first_refresh = AsyncMock()
        mock_get_loaded_integration.return_value = MagicMock()
        result = await async_setup_entry(hass, entry)
        assert result is True
        mock_coordinator.return_value.async_config_entry_first_refresh.assert_called_once()
        hass.config_entries.async_forward_entry_setups.assert_called_once_with(
            entry, [Platform.BUTTON, Platform.SENSOR, Platform.BINARY_SENSOR]
        )
        entry.add_update_listener.assert_called_once_with(async_reload_entry)


async def test_async_unload_entry(hass: HomeAssistant) -> None:
    """Test the async_unload_entry function."""
    entry = MagicMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    result = await async_unload_entry(hass, entry)
    assert result is True
    hass.config_entries.async_unload_platforms.assert_awaited_once_with(
        entry,
        [
            Platform.BUTTON,
            Platform.SENSOR,
            Platform.BINARY_SENSOR,
        ],
    )


async def test_async_reload_entry(hass: HomeAssistant) -> None:
    """Test the async_reload_entry function."""
    entry = MagicMock()
    hass.config_entries.async_reload = AsyncMock()
    await async_reload_entry(hass, entry)
    hass.config_entries.async_reload.assert_awaited_once_with(entry.entry_id)
