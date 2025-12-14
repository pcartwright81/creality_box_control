"""Binary sensor platform for creality_box_control."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from .entity import CrealityBoxEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from creality_wifi_box_client.creality_wifi_box_client import BoxInfo
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import CrealityBoxDataUpdateCoordinator
    from .data import CrealityBoxControlConfigEntry


@dataclass(frozen=True, kw_only=True)
class CrealityBoxBinarySensorEntityDescription(BinarySensorEntityDescription):
    """A class that describes binary sensor entities."""

    value_fn: Callable[[BoxInfo], bool | None]


ENTITY_DESCRIPTIONS: tuple[CrealityBoxBinarySensorEntityDescription, ...] = (
    CrealityBoxBinarySensorEntityDescription(
        key="upgrade_status",
        name="Upgrade Available",
        value_fn=lambda x: bool(x.upgrade_status),
    ),
    CrealityBoxBinarySensorEntityDescription(
        key="error", name="error", value_fn=lambda x: x.error
    ),
)


async def async_setup_entry(
    _: HomeAssistant,
    entry: CrealityBoxControlConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    async_add_entities(
        CrealityBoxBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class CrealityBoxBinarySensor(CrealityBoxEntity, BinarySensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """creality_box_control binary_sensor class."""

    def __init__(
        self,
        coordinator: CrealityBoxDataUpdateCoordinator,
        entity_description: CrealityBoxBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, entity_description)
        self._update_attr_value()

    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._update_attr_value()
        super()._handle_coordinator_update()

    def _update_attr_value(self) -> None:
        """Update the _attr_is_on value based on the coordinator data."""
        self._attr_is_on = self.entity_description.value_fn(self.coordinator.data)  # pyright: ignore[reportAttributeAccessIssue]
