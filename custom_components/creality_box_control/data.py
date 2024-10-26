"""Custom types for creality_box_control."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from creality_wifi_box_client.creality_wifi_box_client import CrealityWifiBoxClient
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .coordinator import CrealityBoxDataUpdateCoordinator


type CrealityBoxControlConfigEntry = ConfigEntry[CrealityBoxData]


@dataclass
class CrealityBoxData:
    """Data for the Creality Box integration."""

    client: CrealityWifiBoxClient
    coordinator: CrealityBoxDataUpdateCoordinator
    integration: Integration
