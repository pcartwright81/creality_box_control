"""Tests for the binary sensor platform."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from creality_wifi_box_client.creality_wifi_box_client import BoxInfo
from homeassistant.core import HomeAssistant

from custom_components.creality_box_control.binary_sensor import (
    ENTITY_DESCRIPTIONS,
    CrealityBoxBinarySensor,
    async_setup_entry,
)
from custom_components.creality_box_control.const import DOMAIN, HOST, MODEL
from tests import TEST_CONFIG_ENTRY_ID, TEST_HOST, TEST_MODEL, TEST_TITLE


@pytest.fixture
def coordinator(mock_box_info: BoxInfo) -> MagicMock:
    """Mock the coordinator."""
    return MagicMock(
        data=mock_box_info,
        config_entry=MagicMock(
            data={HOST: TEST_HOST, MODEL: TEST_MODEL},
            entry_id=TEST_CONFIG_ENTRY_ID,
            title=TEST_TITLE,
            domain=DOMAIN,
        ),
    )


@pytest.mark.parametrize(
    ("entity_description", "expected_state"),
    [
        (
            MagicMock(
                key="upgrade_status",
                name="Upgrade Available",
                value_fn=lambda x: bool(x.upgrade_status),
            ),
            False,
        ),
        (
            MagicMock(key="error", name="error", value_fn=lambda x: x.error),
            False,
        ),
        (
            MagicMock(
                key="none",
                name="None",
                value_fn=lambda x: None,  # noqa: ARG005
            ),
            None,
        ),
    ],
)
async def test_binary_sensor(
    coordinator: MagicMock,
    entity_description: MagicMock,
    expected_state: bool | None,  # noqa: FBT001
) -> None:
    """Test the binary sensor."""
    # Arrange
    # Act
    sensor = CrealityBoxBinarySensor(
        coordinator=coordinator, entity_description=entity_description
    )
    # Assert
    assert sensor.is_on == expected_state


async def test_binary_sensor_setup_entry(hass: HomeAssistant) -> None:
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


async def test_binary_sensor_update(coordinator: MagicMock) -> None:
    """Test the binary sensor update."""
    entity_description = MagicMock(
        key="upgrade_status",
        name="Upgrade Available",
        value_fn=lambda x: bool(x.upgrade_status),
    )
    sensor = CrealityBoxBinarySensor(
        coordinator=coordinator, entity_description=entity_description
    )
    sensor.async_write_ha_state = MagicMock()

    # Initial state
    assert sensor.is_on is False

    # Update data
    coordinator.data = MagicMock(upgrade_status=1)

    # Act
    sensor._handle_coordinator_update()  # noqa: SLF001

    # Assert
    assert sensor.is_on is True
    sensor.async_write_ha_state.assert_called_once()
