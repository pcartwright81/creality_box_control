"""Tests for the data object."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.creality_box_control.const import DOMAIN
from custom_components.creality_box_control.data import CrealityBoxData
from tests import TEST_CONFIG_ENTRY_ID, TEST_TITLE


@pytest.fixture
def mock_client() -> AsyncMock:
    """Mock the client."""
    return AsyncMock()


@pytest.fixture
def coordinator() -> MagicMock:
    """Mock the coordinator."""
    return MagicMock()


@pytest.fixture
def config_entry() -> MagicMock:
    """Mock the config entry."""
    return MagicMock(
        data={"host": "1.2.3.4", "port": 81, "model": "CR-10"},
        entry_id=TEST_CONFIG_ENTRY_ID,
        title=TEST_TITLE,
        domain=DOMAIN,
    )


async def test_data_object(
    mock_client: AsyncMock,
    coordinator: MagicMock,
    config_entry: MagicMock,
) -> None:
    """Test the data object."""
    # Arrange
    # Act
    data = CrealityBoxData(
        client=mock_client,
        coordinator=coordinator,
        integration=config_entry,
    )
    # Assert
    assert data.client == mock_client
    assert data.coordinator == coordinator
    assert data.integration == config_entry
