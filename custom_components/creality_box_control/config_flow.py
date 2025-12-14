"""Adds config flow for Creality Box."""

from __future__ import annotations

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from creality_wifi_box_client.creality_wifi_box_client import (
    CrealityWifiBoxClient,
)
from homeassistant import config_entries

from .const import DOMAIN, HOST, LOGGER, MODEL, PORT


class CrealityBoxFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Creality Box."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                model = await self._test_connect_and_get_model(
                    host=user_input[HOST],
                    port=user_input[PORT],
                )
            except Exception as exception:  # noqa: BLE001
                LOGGER.exception("Connection failed: %s", exception)
                _errors["base"] = "unknown"
            else:
                user_input[MODEL] = model
                return self.async_create_entry(
                    title=f"{model}@{user_input[HOST]}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(HOST): cv.string,
                    vol.Required(PORT, default=81): cv.port,
                },
            ),
            errors=_errors,
        )

    async def _test_connect_and_get_model(self, host: str, port: int) -> str:
        """Validate input and get model."""
        client = CrealityWifiBoxClient(box_ip=host, box_port=port)
        info = await client.get_info()
        model = info.model.strip()
        if model == "":
            msg = "Model was blank."
            raise ValueError(msg)
        return model
