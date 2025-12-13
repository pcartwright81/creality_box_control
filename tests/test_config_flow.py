"""Tests for the config flow."""

import pathlib
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from creality_wifi_box_client.creality_wifi_box_client import BoxInfo
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.loader import Integration

from custom_components.creality_box_control.config_flow import CrealityBoxFlowHandler
from custom_components.creality_box_control.const import DOMAIN, HOST, MODEL, PORT
from tests import TEST_HOST, TEST_MODEL, TEST_PORT

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def bypass_custom_component_scan(hass: HomeAssistant):  # noqa: ANN201
    """Manually register our integration."""
    # Path to your actual component folder
    component_path = (
        pathlib.Path(__file__).parent.parent
        / "custom_components"
        / "creality_box_control"
    )

    # Create a dummy Integration object representing your component
    # This manually mimics what the loader would create if it scanned the disk
    integration = Integration(
        hass=hass,
        pkg_path=f"custom_components.{DOMAIN}",
        file_path=component_path,
        manifest={
            "domain": DOMAIN,
            "name": "Creality Box Control",
            "version": "0.0.1",
            "config_flow": True,
            "documentation": "https://www.example.com",
            "requirements": [],
            "dependencies": [],
            "codeowners": [],
        },
    )

    # Patch the loader to return OUR integration object immediately
    with patch(
        "homeassistant.loader.async_get_custom_components",
        return_value={DOMAIN: integration},
    ):
        yield


@pytest.fixture
def mock_client() -> AsyncMock:
    """Mock the client."""
    return AsyncMock()


async def test_show_form(hass: HomeAssistant) -> None:
    """Test showing the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": "user"}
    )
    assert "type" in result
    assert "step_id" in result
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"


async def test_create_entry(
    hass: HomeAssistant, mock_client: AsyncMock, mock_box_info: BoxInfo
) -> None:
    """Test creating an entry."""
    # Arrange
    mock_client.get_info = AsyncMock(return_value=mock_box_info)

    # We patch the internal method or the client method used by the flow
    with patch(
        "creality_wifi_box_client.creality_wifi_box_client.CrealityWifiBoxClient.get_info",
        return_value=mock_box_info,
    ):
        # Act
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={HOST: TEST_HOST, PORT: TEST_PORT},
        )

        # Assert
        assert result["type"] == FlowResultType.CREATE_ENTRY
        assert result["title"] == f"{TEST_MODEL}@{TEST_HOST}"
        assert result["data"] == {HOST: TEST_HOST, PORT: TEST_PORT, MODEL: TEST_MODEL}


async def test_cannot_connect(hass: HomeAssistant) -> None:
    """Test handling connection errors."""
    # Force the client mock (if used by the flow via a factory/patch) to raise
    with patch(
        "creality_wifi_box_client.creality_wifi_box_client.CrealityWifiBoxClient.get_info",
        side_effect=Exception("Connection error"),
    ):
        # Act
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={HOST: TEST_HOST, PORT: TEST_PORT},
        )

    # Assert
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}


async def test_blank_model(hass: HomeAssistant) -> None:
    """Test handling a blank model."""
    info = MagicMock(model="")

    with patch(
        "creality_wifi_box_client.creality_wifi_box_client.CrealityWifiBoxClient.get_info",
        return_value=info,
    ):
        # Act
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={HOST: TEST_HOST, PORT: TEST_PORT},
        )

    # Assert - It should error and show the form again
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}


async def test__test_connect_and_get_model_success(mock_box_info: BoxInfo) -> None:
    """Test successful credential validation."""
    with patch(
        "creality_wifi_box_client.creality_wifi_box_client.CrealityWifiBoxClient.get_info",
        return_value=mock_box_info,
    ) as mock_test_connection:
        handler = CrealityBoxFlowHandler()
        result = await handler._test_connect_and_get_model(TEST_HOST, TEST_PORT)  # noqa: SLF001
        assert result == TEST_MODEL
        mock_test_connection.assert_called_once_with()


async def test__test_connect_and_get_model_error() -> None:
    """Test successful credential validation."""
    with patch(
        "creality_wifi_box_client.creality_wifi_box_client.CrealityWifiBoxClient.get_info",
        return_value=MagicMock(model=""),
    ) as mock_test_connection:
        handler = CrealityBoxFlowHandler()
        with pytest.raises(ValueError) as exc_info:  # noqa: PT011
            await handler._test_connect_and_get_model(TEST_HOST, TEST_PORT)  # noqa: SLF001

        assert str(exc_info.value) == "Model was blank."
        mock_test_connection.assert_called_once_with()
