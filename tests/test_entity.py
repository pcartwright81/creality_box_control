"""Tests for the base entity."""

from unittest.mock import MagicMock

import pytest
from creality_wifi_box_client.creality_wifi_box_client import BoxInfo

from custom_components.creality_box_control.const import DOMAIN, HOST, MODEL
from custom_components.creality_box_control.entity import CrealityBoxEntity
from tests import TEST_CONFIG_ENTRY_ID, TEST_HOST, TEST_MODEL, TEST_TITLE


@pytest.fixture
def coordinator(mock_box_info: BoxInfo) -> MagicMock:
    """Mock the coordinator."""
    # We pass the REAL Pydantic object (mock_box_info) as 'data'
    # This ensures .did_string returns a real string "CR-BOX_12345"
    return MagicMock(
        data=mock_box_info,
        config_entry=MagicMock(
            data={HOST: TEST_HOST, MODEL: TEST_MODEL},
            entry_id=TEST_CONFIG_ENTRY_ID,
            title=TEST_TITLE,
            domain=DOMAIN,
        ),
    )


async def test_entity(coordinator: MagicMock, mock_box_info: BoxInfo) -> None:
    """Test the entity."""
    # Arrange
    entity_description = MagicMock(key="test_key", name="Test Name")

    # Act
    entity = CrealityBoxEntity(coordinator=coordinator, description=entity_description)

    # Assert
    # The expected string is constructed from the mock_box_info data
    expected_unique_id = f"{mock_box_info.did_string}_{entity_description.key}".lower()

    assert entity.unique_id == expected_unique_id
    assert entity.device_info["identifiers"] == {(DOMAIN, mock_box_info.did_string)}
    assert entity.device_info["name"] == TEST_TITLE
    assert entity.device_info["model"] == TEST_MODEL


async def test_entity_attributes(coordinator: MagicMock) -> None:
    """Test the entity attributes."""
    entity_description = MagicMock(key="test_key", name="Test Name")
    entity = CrealityBoxEntity(coordinator=coordinator, description=entity_description)

    assert entity.icon == "mdi:printer-3d"
    assert entity.has_entity_name is True
