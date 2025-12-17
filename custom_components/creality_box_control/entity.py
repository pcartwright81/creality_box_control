"""Base entity for the Creality Box Control integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import CrealityBoxDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class CrealityBoxEntity(CoordinatorEntity[CrealityBoxDataUpdateCoordinator]):
    """Defines a base Creality Box entity."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:printer-3d"

    def __init__(
        self,
        coordinator: CrealityBoxDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.entity_description = description

        self._attr_unique_id = (
            f"{coordinator.data.did_string}_{description.key}".lower()
        )
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.data.did_string)},
            name=coordinator.config_entry.title,
            manufacturer="Creality",
            model=coordinator.data.model,
        )
