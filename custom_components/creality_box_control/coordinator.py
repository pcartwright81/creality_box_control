"""DataUpdateCoordinator for creality_box_control."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from creality_wifi_box_client.creality_wifi_box_client import BoxInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER, PRINT_PAUSE, PRINT_RESUME, PRINT_STOP

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import CrealityBoxControlConfigEntry


class CrealityBoxDataUpdateCoordinator(DataUpdateCoordinator[BoxInfo]):
    """Class to manage fetching data from the API."""

    config_entry: CrealityBoxControlConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=10),
        )

    async def _async_update_data(self) -> BoxInfo:
        """Update data via library."""
        return await self.config_entry.runtime_data.client.get_info()

    async def send_command(self, command: str) -> None:
        """Send a command to the printer."""
        try:
            client = self.config_entry.runtime_data.client
            if command == PRINT_STOP:
                await client.stop_print()
            elif command == PRINT_RESUME:
                await client.resume_print()
            elif command == PRINT_PAUSE:
                await client.pause_print()
            else:
                msg = f"Unknown command: {command}"
                raise ValueError(msg)  # noqa: TRY301
        except Exception as e:
            msg = f"Failed to send command {command}: {e}"
            LOGGER.error(msg)
            raise
