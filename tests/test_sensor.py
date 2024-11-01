"""Tests for the sensor platform."""

from datetime import timedelta
from typing import Literal
from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import HomeAssistant

from custom_components.creality_box_control.const import DOMAIN, HOST, MODEL
from custom_components.creality_box_control.sensor import (
    ENTITY_DESCRIPTIONS,
    CrealityBoxSensor,
    _map_state,
    _to_time_left,
    async_setup_entry,
)
from tests import TEST_BOX_INFO, TEST_CONFIG_ENTRY_ID, TEST_HOST, TEST_MODEL, TEST_TITLE


@pytest.fixture
def coordinator() -> MagicMock:
    """Mock the coordinator."""
    return MagicMock(
        data=TEST_BOX_INFO,
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
                key="wanip",
                name="IP Address",
                value_fn=lambda x: x.wanip,
            ),
            TEST_HOST,
        ),
        (
            MagicMock(
                key="state",
                name="Current State",
                value_fn=lambda x: "Printing"
                if x.state == 1 and x.connect == 1
                else "Unknown",
            ),
            "Printing",
        ),
        (
            MagicMock(
                key="print_job_time",
                name="Time Running",
                value_fn=lambda x: str(timedelta(seconds=x.print_job_time)),
            ),
            "2:00:00",
        ),
        (
            MagicMock(
                key="print_left_time",
                name="Time Left",
                value_fn=lambda x: str(timedelta(seconds=x.print_left_time)),
            ),
            "1:00:00",
        ),
        (
            MagicMock(
                key="print_name",
                name="Currently Printing",
                value_fn=lambda x: x.print_name,
            ),
            "MyPrint.gcode",
        ),
        (
            MagicMock(
                key="nozzle_temp",
                name="Nozzle Temp",
                value_fn=lambda x: x.nozzle_temp,
            ),
            212,
        ),
        (
            MagicMock(
                key="bed_temp",
                name="Bed Temp",
                value_fn=lambda x: x.bed_temp,
            ),
            60,
        ),
        (
            MagicMock(
                key="print_progress",
                name="Print Progress",
                value_fn=lambda x: x.print_progress,
            ),
            56,
        ),
    ],
)
async def test_sensor(
    coordinator: MagicMock,
    entity_description: MagicMock,
    expected_state: Literal["192.168.1.2", "Printing", "0:01:40", "test.gcode", 50]
    | float,
) -> None:
    """Test the sensor."""
    # Arrange
    # Act
    sensor = CrealityBoxSensor(
        coordinator=coordinator, entity_description=entity_description
    )
    # Assert
    assert sensor.native_value == expected_state

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

@pytest.mark.parametrize(
    ("seconds_left", "expected_output"),
    [
        (0, "0:00:00"),
        (30, "0:00:30"),
        (125, "0:02:05"),
        (3666, "1:01:06"),
        (93780, "1 day, 2:03:00"),
    ],
)
def test_to_time_left(seconds_left: int, expected_output: str) -> None:
    """Test the _to_time_left function."""
    assert _to_time_left(seconds_left) == expected_output

@pytest.mark.parametrize(
    ("state", "connect", "expected_output"),
    [
        (1, 1, "Printing"),
        (4, 1, "Stopping"),
        (5, 1, "Suspending"),
        (0, 1, "Idle"),
        (1, 0, "Offline"),
        (4, 0, "Offline"),
        (5, 0, "Offline"),
        (0, 0, "Offline"),
    ],
)
def test_map_state(state: int, connect: int, expected_output: str) -> None:
    """
    Tests the _map_state function.

    Args:
      state: The state of the printer, as an integer.
      connect: The connection status of the printer, as an integer.
      expected_output: The expected output string.

    """
    assert _map_state(state, connect) == expected_output
