"""CrealityBoxEntity class."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, HOST, MODEL
from .coordinator import CrealityBoxDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.helpers.entity import EntityDescription


class CrealityBoxEntity(CoordinatorEntity[CrealityBoxDataUpdateCoordinator]):
    """CrealityBoxEntity class."""

    _attr_has_entity_name = (
        True  # Optional: standardizes naming (e.g. "Creality Box Nozzle Temp")
    )

    def __init__(
        self,
        coordinator: CrealityBoxDataUpdateCoordinator,
        description: EntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)

        # 1. Get the Hardware ID (did_string) from the API data
        device_id = coordinator.data.did_string

        # Fallback just in case did_string is missing (sanity check)
        if not device_id:
            device_id = coordinator.config_entry.entry_id

        self.entity_description = description

        # 2. Set the Unique ID based on hardware ID + sensor key
        self._attr_unique_id = f"{device_id}_{description.key}".lower()

        # 3. Create Device Info using the Hardware ID
        # This ensures HA knows this is the same physical box even if IP changes
        self._model = coordinator.config_entry.data[MODEL]
        self._host = coordinator.config_entry.data[HOST]

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, device_id)},  # Use DOMAIN + Hardware ID
            manufacturer="Creality",
            model=self._model,
            name=self._model,  # Or a custom name if you have one
            configuration_url=f"http://{self._host}",  # Clickable link in UI
        )

    # Note: 'name', 'unique_id', and 'icon' properties are removed
    # because we set _attr_* variables or rely on EntityDescription defaults.

    @property
    def icon(self) -> str | None:
        """Return the icon to use in the frontend."""
        # You can keep this if you want a global default,
        # otherwise define icons in your EntityDescriptions.
        return "mdi:printer-3d"
