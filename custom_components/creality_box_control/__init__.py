"""
Custom integration to integrate creality_box_control with Home Assistant.

For more details about this integration, please refer to
https://github.com/pcartwright81/creality_box_control
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from creality_wifi_box_client.creality_wifi_box_client import CrealityWifiBoxClient
from homeassistant.const import Platform
from homeassistant.loader import async_get_loaded_integration

from custom_components.creality_box_control.const import HOST, PORT

from .coordinator import CrealityBoxDataUpdateCoordinator
from .data import IntegrationBlueprintData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import CrealityBoxControlConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: CrealityBoxControlConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = CrealityBoxDataUpdateCoordinator(
        hass=hass,
    )
    entry.runtime_data = IntegrationBlueprintData(
        client=CrealityWifiBoxClient(
            box_ip=entry.data[HOST], box_port=entry.data[PORT]
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: CrealityBoxControlConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: CrealityBoxControlConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
