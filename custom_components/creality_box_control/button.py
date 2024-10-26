"""Button platform for creality_box_control."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription

from custom_components.creality_box_control.const import (
    PRINT_PAUSE,
    PRINT_RESUME,
    PRINT_STOP,
)

from .entity import CrealityBoxEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import CrealityBoxDataUpdateCoordinator
    from .data import CrealityBoxControlConfigEntry

ENTITY_DESCRIPTIONS = (
    ButtonEntityDescription(
        key=PRINT_PAUSE,
        name="Pause Print",
    ),
    ButtonEntityDescription(
        key=PRINT_RESUME,
        name="Resume Print",
    ),
    ButtonEntityDescription(
        key=PRINT_STOP,
        name="Stop Print",
    ),
)


async def async_setup_entry(
    _: HomeAssistant,
    entry: CrealityBoxControlConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        CrealityBoxButton(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class CrealityBoxButton(CrealityBoxEntity, ButtonEntity):
    """creality_box_control Button class."""

    def __init__(
        self,
        coordinator: CrealityBoxDataUpdateCoordinator,
        entity_description: ButtonEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description)
        self.entity_description: ButtonEntityDescription = entity_description

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.coordinator.send_command(self.entity_description.key)
