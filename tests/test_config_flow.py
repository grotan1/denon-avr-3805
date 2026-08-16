"""Test Denon AVR-3805 config flow."""
from custom_components.denon_avr_3805.const import BINARY_SENSOR
from custom_components.denon_avr_3805.const import CONF_HOST
from custom_components.denon_avr_3805.const import CONF_MODEL
from custom_components.denon_avr_3805.const import CONF_NAME
from custom_components.denon_avr_3805.const import CONF_PORT
from custom_components.denon_avr_3805.const import DOMAIN
from custom_components.denon_avr_3805.const import MEDIA_PLAYER
from custom_components.denon_avr_3805.const import SENSOR
from custom_components.denon_avr_3805.const import SWITCH
from homeassistant import config_entries
from homeassistant import data_entry_flow
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG


async def test_user_form_shown(hass):
    """The user step should show a form with the connection fields."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {}


async def test_successful_config_flow(hass, bypass_connect):
    """A reachable AVR should result in a created config entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["title"] == MOCK_CONFIG[CONF_NAME]
    assert result["data"] == MOCK_CONFIG


async def test_failed_config_flow(hass, error_on_connect):
    """An unreachable AVR should show the form again with an error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input=MOCK_CONFIG
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"] == {"base": "invalid_host"}


async def test_options_flow_shows_menu(hass, bypass_connect):
    """The options flow should start with a menu of what to configure."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == data_entry_flow.FlowResultType.MENU
    assert result["step_id"] == "init"
    assert set(result["menu_options"]) == {"connection", "platforms"}


async def test_options_flow_platforms(hass, bypass_connect):
    """Selecting platforms from the menu should update the enabled platforms."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "platforms"}
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "platforms"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            BINARY_SENSOR: True,
            SENSOR: False,
            SWITCH: True,
            MEDIA_PLAYER: True,
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert entry.options == {
        BINARY_SENSOR: True,
        SENSOR: False,
        SWITCH: True,
        MEDIA_PLAYER: True,
    }


async def test_options_flow_connection_success(hass, bypass_connect):
    """A successful connection test should update the entry's connection data."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "connection"}
    )
    assert result["step_id"] == "connection"

    new_data = {
        CONF_HOST: "5.6.7.8",
        CONF_PORT: 23,
        CONF_NAME: "Denon",
        CONF_MODEL: "AVR-3805",
    }
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input=new_data
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert entry.data == new_data


async def test_options_flow_connection_failure(hass, error_on_connect):
    """A failed connection test should redisplay the connection form with an error."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "connection"}
    )

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_HOST: "5.6.7.8",
            CONF_PORT: 23,
            CONF_NAME: "Denon",
            CONF_MODEL: "AVR-3805",
        },
    )

    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == "connection"
    assert result["errors"] == {"base": "invalid_host"}

