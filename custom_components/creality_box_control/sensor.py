"""Sensor platform for creality_box_control."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.components.sensor.const import SensorDeviceClass
from homeassistant.const import UnitOfTemperature

from custom_components.creality_box_control.const import LOGGER

from .entity import CrealityBoxEntity

if TYPE_CHECKING:
    from collections.abc import Callable
    from datetime import time

    from creality_wifi_box_client.creality_wifi_box_client import BoxInfo
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import CrealityBoxDataUpdateCoordinator
    from .data import CrealityBoxControlConfigEntry


@dataclass(frozen=True, kw_only=True)
class CrealityBoxSensorEntityDescription(
    SensorEntityDescription, frozen_or_thawed=True
):
    """A class that describes sensor entities."""

    value_fn: Callable[[BoxInfo], float | str | datetime | time | None]


ENTITY_DESCRIPTIONS = (
    CrealityBoxSensorEntityDescription(
        key="wanip", name="IP Address", value_fn=lambda x: x.wanip
    ),
    CrealityBoxSensorEntityDescription(
        key="state",
        name="Current State",
        value_fn=lambda x: _map_state(x.state, x.connect),
    ),
    CrealityBoxSensorEntityDescription(
        key="print_job_time",
        name="Time Running",
        value_fn=lambda x: _to_time_left(x.print_job_time),
    ),
    CrealityBoxSensorEntityDescription(
        key="print_left_time",
        name="Time Left",
        value_fn=lambda x: _to_time_left(x.print_left_time),
    ),
    CrealityBoxSensorEntityDescription(
        key="print_name",
        name="Currently Printing",
        value_fn=lambda x: x.print_name,
    ),
    CrealityBoxSensorEntityDescription(
        key="nozzle_temp",
        name="Nozzle Temp",
        value_fn=lambda x: x.nozzle_temp,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CrealityBoxSensorEntityDescription(
        key="bed_temp",
        name="Bed Temp",
        value_fn=lambda x: x.bed_temp,
        device_class=SensorDeviceClass.TEMPERATURE,
        suggested_unit_of_measurement=UnitOfTemperature.CELSIUS,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    CrealityBoxSensorEntityDescription(
        key="print_progress",
        name="Job Percentage",
        value_fn=lambda x: x.print_progress,
        native_unit_of_measurement="%",
    ),
)


def _map_state(state: int, connect: int) -> str:
    # Map the state
    # Pieced together from
    # https://github.com/CrealityOfficial/CrealityPrint/tree/release-v5.0.3/plugins/CrealityUI/CrealityUI/lanprinterqml
    LOGGER.debug(f"State:{state} Connect:{connect}")
    if connect != 1:
        return "Offline"
    printing = 1
    stopping = 4
    suspending = 5
    if state == printing:
        return "Printing"
    if state == stopping:
        return "Stopping"
    if state == suspending:
        return "Suspending"
    return "Idle"


def _to_time_left(seconds_left: int) -> str:
    return str(timedelta(seconds=seconds_left))


async def async_setup_entry(
    _: HomeAssistant,
    entry: CrealityBoxControlConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        CrealityBoxSensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class CrealityBoxSensor(CrealityBoxEntity, SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """creality_box_control Sensor class."""

    def __init__(
        self,
        coordinator: CrealityBoxDataUpdateCoordinator,
        entity_description: CrealityBoxSensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, entity_description)

    @property
    def native_value(self) -> Any:  # pyright: ignore[reportIncompatibleVariableOverride] # noqa: ANN401
        """Return the native value of the sensor."""
        return self.entity_description.value_fn(self.coordinator.data)  # pyright: ignore[reportAttributeAccessIssue]
