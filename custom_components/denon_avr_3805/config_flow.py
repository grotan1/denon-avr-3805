"""Adds config flow for Denon AVR-3805."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .api import DenonAvr3805ApiClient
from .const import CONF_HOST
from .const import CONF_NAME
from .const import CONF_PORT
from .const import DOMAIN
from .const import PLATFORMS


class DenonAvr3805FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for denon_avr_3805."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        """Initialize."""
        self._errors = {}

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        self._errors = {}

        # Uncomment the next 2 lines if only a single instance of the integration is allowed:
        # if self._async_current_entries():
        #     return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            valid = await self._test_connection(
                user_input[CONF_HOST], user_input[CONF_PORT]
            )
            if valid:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, "Denon"), data=user_input
                )
            else:
                self._errors["base"] = "invalid_host"

            return await self._show_config_form(user_input)

        return await self._show_config_form(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return DenonAvr3805OptionsFlowHandler(config_entry)

    async def _show_config_form(self, user_input):  # pylint: disable=unused-argument
        """Show the configuration form to edit location data."""
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, "") if user_input else ""): str,
                    vol.Required(CONF_PORT, default=user_input.get(CONF_PORT, 2000) if user_input else 2000): int,
                    vol.Optional(CONF_NAME, default=user_input.get(CONF_NAME, "Denon") if user_input else "Denon"): str,
                }
            ),
            errors=self._errors,
        )

    async def _test_connection(self, host, port):
        """Return true if connection to AVR is successful."""
        try:
            client = DenonAvr3805ApiClient(host, port)
            await client.connect()
            # Test with a status query
            status = await client.async_get_power_status()
            await client.disconnect()
            return status is not None
        except Exception:  # pylint: disable=broad-except
            pass
        return False


class DenonAvr3805OptionsFlowHandler(config_entries.OptionsFlow):
    """Config flow options handler for denon_avr_3805."""

    def __init__(self, config_entry):
        """Initialize HACS options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title=self.config_entry.data.get(CONF_HOST), data=self.options
        )
