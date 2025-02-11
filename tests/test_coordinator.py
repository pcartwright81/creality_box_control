"""Tests for the coordinator."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.creality_box_control.const import (
    PRINT_PAUSE,
    PRINT_RESUME,
    PRINT_STOP,
)
from custom_components.creality_box_control.coordinator import (
    CrealityBoxDataUpdateCoordinator,
)
from tests import TEST_BOX_INFO, TEST_CONFIG_ENTRY_ID, TEST_TITLE


@pytest.fixture
def mock_client() -> AsyncMock:
    """Mock the client."""
    client = AsyncMock()
    client.get_info = AsyncMock(return_value=TEST_BOX_INFO)
    return client


@pytest.fixture
def coordinator(
    hass: HomeAssistant, mock_client: AsyncMock
) -> CrealityBoxDataUpdateCoordinator:
    """Mock the coordinator."""
    config_entry = MagicMock(
        data={"host": "1.2.3.4", "port": 81, "model": "CR-10"},
        entry_id=TEST_CONFIG_ENTRY_ID,
        title=TEST_TITLE,
    )
    coordinator = CrealityBoxDataUpdateCoordinator(
        hass=hass,
    )
    coordinator.config_entry = config_entry
    coordinator.config_entry.runtime_data.client = mock_client
    return coordinator


@pytest.mark.parametrize(
    ("command", "client_method"),
    [
        (PRINT_STOP, "stop_print"),
        (PRINT_PAUSE, "pause_print"),
        (PRINT_RESUME, "resume_print"),
        ("error", ""),
    ],
)
async def test_send_command(
    coordinator: CrealityBoxDataUpdateCoordinator,
    command: str,
    client_method: str,
) -> None:
    """Test sending commands to the printer."""
    # Assert
    if command == "error":
        with pytest.raises(Exception) as exc_info:  # noqa: PT011
            await coordinator.send_command(command)
        assert str(exc_info.value) == "Unknown command: error"
    else:
        await coordinator.send_command(command)
        getattr(
            coordinator.config_entry.runtime_data.client, client_method
        ).assert_awaited_once()
