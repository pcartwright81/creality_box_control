"""Tests for the entity."""

from unittest.mock import MagicMock

import pytest

from custom_components.creality_box_control.const import DOMAIN, HOST, MODEL
from custom_components.creality_box_control.entity import CrealityBoxEntity
from tests import TEST_CONFIG_ENTRY_ID, TEST_HOST, TEST_MODEL, TEST_TITLE


@pytest.fixture
def coordinator() -> MagicMock:
    """Mock the coordinator."""
    return MagicMock(
        config_entry=MagicMock(
            data={HOST: TEST_HOST, MODEL: TEST_MODEL},
            entry_id=TEST_CONFIG_ENTRY_ID,
            title=TEST_TITLE,
            domain=DOMAIN,
        )
    )


@pytest.fixture
def entity_description() -> MagicMock:
    """Mock the entity description."""
    return MagicMock(key="test_key", name="Test Name")


async def test_entity(coordinator: MagicMock, entity_description: MagicMock) -> None:
    """Test the entity."""
    # Arrange
    # Act
    entity = CrealityBoxEntity(coordinator=coordinator, description=entity_description)
    # Assert
    assert (
        entity.unique_id == f"{TEST_MODEL}_{TEST_HOST}_{entity_description.key}".lower()
    )
    assert entity.name == f"{TEST_MODEL}@{TEST_HOST} {entity_description.name}"
    assert entity.icon == "mdi:printer-3d"
