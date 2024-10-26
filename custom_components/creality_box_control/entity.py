"""CrealityBoxEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, HOST, MODEL
from .coordinator import CrealityBoxDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class CrealityBoxEntity(CoordinatorEntity[CrealityBoxDataUpdateCoordinator]):
    """CrealityBoxEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: CrealityBoxDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self.entity_description = description
        self.use_device_name = True
        self._model = coordinator.config_entry.data[MODEL]
        self._host = coordinator.config_entry.data[HOST]
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(self._model, self._host)},
            manufacturer="Creality",
            name=f"{self._model}@{self._host}",
        )

    @property
    def name(self) -> str | None:
        """Return the name of this device."""
        return f"{self._model}@{self._host} {self.entity_description.name}"

    @property
    def unique_id(self) -> str | None:
        """Return a unique identifier for this sensor."""
        return f"{self._model}_{self._host}_{self.entity_description.key}".lower()

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend."""
        return "mdi:printer-3d"
