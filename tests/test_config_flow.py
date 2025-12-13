"""Tests for the config flow."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from creality_wifi_box_client.creality_wifi_box_client import BoxInfo
from homeassistant.core import HomeAssistant

from custom_components.creality_box_control.config_flow import CrealityBoxFlowHandler
from custom_components.creality_box_control.const import DOMAIN, HOST, MODEL, PORT
from tests import TEST_HOST, TEST_MODEL, TEST_PORT

pytestmark = pytest.mark.asyncio


# This fixture is used to enable custom integrations, otherwise the custom_components
# folder will not be loaded.
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):  # noqa: ANN001, ANN201, ARG001
    """Enable custom integrations."""
    return


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
    assert result["type"] == "form"
    assert result["step_id"] == "user"


async def test_create_entry(
    hass: HomeAssistant, mock_client: AsyncMock, mock_box_info: BoxInfo
) -> None:
    """Test creating an entry."""
    # Arrange
    mock_client.get_info = AsyncMock(return_value=mock_box_info)
    with patch(
        "custom_components.creality_box_control.config_flow.CrealityBoxFlowHandler._test_connect_and_get_model",
        return_value="CR-10",
    ):
        # Act
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": "user"},
            data={HOST: TEST_HOST, PORT: TEST_PORT},
        )

        # Assert
        assert "type" in result
        assert "title" in result
        assert "data" in result
        assert result["type"] == "create_entry"
        assert result["title"] == f"{TEST_MODEL}@{TEST_HOST}"
        assert result["data"] == {HOST: TEST_HOST, PORT: TEST_PORT, MODEL: TEST_MODEL}


async def test_cannot_connect(hass: HomeAssistant, mock_client: AsyncMock) -> None:
    """Test handling connection errors."""
    # Arrange
    mock_client.get_info.side_effect = Exception("Connection error")

    # Act
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "user"},
        data={HOST: TEST_HOST, PORT: TEST_PORT},
    )

    # Assert
    assert "type" in result
    assert "errors" in result
    assert result["type"] == "form"
    assert result["errors"] == {"base": "unknown"}


async def test_blank_model(hass: HomeAssistant, mock_client: AsyncMock) -> None:
    """Test handling a blank model."""
    info = MagicMock(model="")
    mock_client.get_info = AsyncMock(return_value=info)

    # Act
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": "user"},
        data={HOST: TEST_HOST, PORT: TEST_PORT},
    )

    # Assert - It should error and show the form again
    assert "type" in result
    assert "errors" in result
    assert result["type"] == "form"
    assert result["errors"] == {"base": "unknown"}


async def test__test_connect_and_get_model_success(mock_box_info: BoxInfo) -> None:
    """Test successful credential validation."""
    with patch(
        "creality_wifi_box_client.creality_wifi_box_client.CrealityWifiBoxClient.get_info",
        return_value=mock_box_info,
    ) as mock_test_connection:
        handler = CrealityBoxFlowHandler()
        result = await handler._test_connect_and_get_model(TEST_HOST, TEST_PORT)  # noqa: SLF001
        assert result is TEST_MODEL
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
