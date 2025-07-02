"""Tests for the button platform."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.creality_box_control.button import (
    ENTITY_DESCRIPTIONS,
    CrealityBoxButton,
    async_setup_entry,
)
from custom_components.creality_box_control.const import (
    PRINT_PAUSE,
    PRINT_RESUME,
    PRINT_STOP,
)
from tests import TEST_CONFIG_ENTRY_ID, TEST_TITLE


@pytest.fixture
def coordinator() -> MagicMock:
    """Mock the coordinator."""
    coordinator = MagicMock(
        config_entry=MagicMock(
            data={"host": "1.2.3.4", "port": 81, "model": "CR-10"},
            entry_id=TEST_CONFIG_ENTRY_ID,
            title=TEST_TITLE,
        ),
    )
    coordinator.send_command = AsyncMock()  # Make it an AsyncMock
    return coordinator


@pytest.mark.parametrize(
    "command",
    [
        (PRINT_STOP),
        (PRINT_PAUSE),
        (PRINT_RESUME),
    ],
)
async def test_buttons(
    coordinator: MagicMock,
    command: str,
) -> None:
    """Test button press."""
    button = CrealityBoxButton(
        coordinator=coordinator,
        entity_description=MagicMock(key=command),
    )
    # Act
    await button.async_press()
    # Assert
    coordinator.send_command.assert_awaited_once_with(command)


async def test_button_setup_entry(hass: HomeAssistant) -> None:
    """Test the async_setup_entry function."""
    entry = MagicMock()
    coordinator = AsyncMock()
    coordinator.async_request_refresh = AsyncMock()
    entry.runtime_data = MagicMock(coordinator=coordinator)
    async_add_entities = AsyncMock()

    await async_setup_entry(hass, entry, async_add_entities)

    # Convert the generator expression to a list
    sensors = list(async_add_entities.call_args[0][0])

    # Assert that async_add_entities was called with a list of the expected sensors
    assert async_add_entities.call_count == 1
    assert len(sensors) == len(ENTITY_DESCRIPTIONS)
