"""Test Denon AVR-3805 switches."""
from unittest.mock import AsyncMock

from custom_components.denon_avr_3805.const import DOMAIN
from homeassistant.components.switch import SERVICE_TURN_OFF
from homeassistant.components.switch import SERVICE_TURN_ON
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG


async def _setup_entry(hass):
    """Set up a mock config entry and return it."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry


def _entity_id(hass, config_entry, suffix):
    """Look up a switch entity_id by its unique_id suffix."""
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "switch", DOMAIN, f"{config_entry.entry_id}_{suffix}"
    )
    assert entity_id is not None
    return entity_id


async def test_power_switch_reflects_initial_status(hass, bypass_connect):
    """The power switch should be on when the AVR reports PWON."""
    config_entry = await _setup_entry(hass)
    entity_id = _entity_id(hass, config_entry, "power")

    assert hass.states.get(entity_id).state == "on"


async def test_mute_switch_reflects_initial_status(hass, bypass_connect):
    """The mute switch should be off when the AVR reports MUOFF."""
    config_entry = await _setup_entry(hass)
    entity_id = _entity_id(hass, config_entry, "mute")

    assert hass.states.get(entity_id).state == "off"


async def test_power_switch_turn_on_off(hass, bypass_connect):
    """Turning the power switch on/off should call the matching API methods."""
    config_entry = await _setup_entry(hass)
    entity_id = _entity_id(hass, config_entry, "power")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    coordinator.api.async_power_on = AsyncMock()
    coordinator.api.async_power_off = AsyncMock()

    await hass.services.async_call(
        "switch", SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    coordinator.api.async_power_off.assert_awaited_once()

    await hass.services.async_call(
        "switch", SERVICE_TURN_ON, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    coordinator.api.async_power_on.assert_awaited_once()


async def test_mute_switch_turn_on_updates_state_immediately(hass, bypass_connect):
    """Muting should be reflected in the switch state without a full poll cycle.

    This validates the fix for the mute/unmute UI responsiveness bug: the
    coordinator confirms the new value on the same connection instead of
    waiting for the next scheduled poll.
    """
    config_entry = await _setup_entry(hass)
    entity_id = _entity_id(hass, config_entry, "mute")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    coordinator.api.async_mute_on = AsyncMock()
    coordinator.api.async_get_mute_status = AsyncMock(return_value="MUON")

    await hass.services.async_call(
        "switch", SERVICE_TURN_ON, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    await hass.async_block_till_done()

    coordinator.api.async_mute_on.assert_awaited_once()
    assert hass.states.get(entity_id).state == "on"


async def test_mute_switch_turn_off_updates_state_immediately(hass, bypass_connect):
    """Unmuting should be reflected in the switch state without a full poll cycle."""
    config_entry = await _setup_entry(hass)
    entity_id = _entity_id(hass, config_entry, "mute")
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    coordinator.data["mute"] = "MUON"
    coordinator.async_update_listeners()
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == "on"

    coordinator.api.async_mute_off = AsyncMock()
    coordinator.api.async_get_mute_status = AsyncMock(return_value="MUOFF")

    await hass.services.async_call(
        "switch", SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id}, blocking=True
    )
    await hass.async_block_till_done()

    coordinator.api.async_mute_off.assert_awaited_once()
    assert hass.states.get(entity_id).state == "off"

