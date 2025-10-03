"""Adds config flow for Denon AVR-3805."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .api import DenonAvr3805ApiClient
from .const import CONF_HOST
from .const import CONF_NAME
from .const import CONF_PORT
from .const import CONF_MODEL
from .const import DEFAULT_MODEL
from .const import DOMAIN
from .const import PLATFORMS


class DenonAvr3805FlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for denon_avr_3805."""

    VERSION = 1

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
                    vol.Optional(CONF_MODEL, default=user_input.get(CONF_MODEL, DEFAULT_MODEL) if user_input else DEFAULT_MODEL): str,
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
        """Initialize options flow."""
        super().__init__()
        self.options = dict(config_entry.options)

    async def async_step_init(self, user_input=None):  # pylint: disable=unused-argument
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["connection", "platforms"]
        )

    async def async_step_connection(self, user_input=None):
        """Handle connection configuration."""
        if user_input is not None:
            # Update the config entry data (not options)
            new_data = dict(self.config_entry.data)
            new_data.update(user_input)
            
            # Test the connection before saving
            valid = await self._test_connection(
                user_input[CONF_HOST], user_input[CONF_PORT]
            )
            if not valid:
                return self.async_show_form(
                    step_id="connection",
                    data_schema=self._get_connection_schema(user_input),
                    errors={"base": "invalid_host"}
                )
            
            self.hass.config_entries.async_update_entry(
                self.config_entry, data=new_data
            )
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="connection",
            data_schema=self._get_connection_schema()
        )

    async def async_step_platforms(self, user_input=None):
        """Handle platform configuration."""
        if user_input is not None:
            self.options.update(user_input)
            return await self._update_options()

        return self.async_show_form(
            step_id="platforms",
            data_schema=vol.Schema(
                {
                    vol.Required(x, default=self.options.get(x, True)): bool
                    for x in sorted(PLATFORMS)
                }
            ),
        )

    def _get_connection_schema(self, user_input=None):
        """Get connection configuration schema with current values."""
        current_data = self.config_entry.data
        
        return vol.Schema(
            {
                vol.Required(
                    CONF_HOST, 
                    default=user_input.get(CONF_HOST) if user_input else current_data.get(CONF_HOST, "")
                ): str,
                vol.Required(
                    CONF_PORT, 
                    default=user_input.get(CONF_PORT) if user_input else current_data.get(CONF_PORT, 2000)
                ): int,
                vol.Optional(
                    CONF_NAME, 
                    default=user_input.get(CONF_NAME) if user_input else current_data.get(CONF_NAME, "Denon")
                ): str,
                vol.Optional(
                    CONF_MODEL, 
                    default=user_input.get(CONF_MODEL) if user_input else current_data.get(CONF_MODEL, DEFAULT_MODEL)
                ): str,
            }
        )

    async def _test_connection(self, host, port):
        """Test connection to AVR."""
        try:
            client = DenonAvr3805ApiClient(host, port)
            await client.connect()
            status = await client.async_get_power_status()
            await client.disconnect()
            return status is not None
        except Exception:
            return False

    async def async_step_user(self, user_input=None):
        """Handle legacy options flow."""
        return await self.async_step_platforms(user_input)

    async def _update_options(self):
        """Update config entry options."""
        return self.async_create_entry(
            title="", data=self.options
        )
