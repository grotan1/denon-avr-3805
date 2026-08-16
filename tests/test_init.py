"""Test Denon AVR-3805 setup process."""
from unittest.mock import AsyncMock

import pytest
from custom_components.denon_avr_3805 import (
    async_setup_entry,
)
from custom_components.denon_avr_3805 import (
    DenonAvr3805DataUpdateCoordinator,
)
from custom_components.denon_avr_3805.api import ConnectionStats
from custom_components.denon_avr_3805.const import (
    DOMAIN,
)
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from .const import MOCK_CONFIG


async def test_setup_unload_and_reload_entry(hass, bypass_connect):
    """Test entry setup and unload."""
    # Create a mock entry so we don't have to go through config flow
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)

    # Set up the entry and assert that the values set during setup are where we expect
    # them to be. Because the AVR connection is patched via `bypass_connect`, no real
    # code from custom_components/denon_avr_3805/api.py actually runs.
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id]) == DenonAvr3805DataUpdateCoordinator
    )

    # Reload the entry and assert that the data from above is still there
    assert await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert DOMAIN in hass.data and config_entry.entry_id in hass.data[DOMAIN]
    assert (
        type(hass.data[DOMAIN][config_entry.entry_id]) == DenonAvr3805DataUpdateCoordinator
    )

    # Unload the entry and verify that the data has been removed
    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.entry_id not in hass.data[DOMAIN]


async def test_setup_entry_exception(hass, error_on_connect):
    """Test ConfigEntryNotReady when the AVR cannot be reached during entry setup."""
    config_entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test")
    config_entry.add_to_hass(hass)

    # In this case we are testing the condition where async_setup_entry raises
    # ConfigEntryNotReady using the `error_on_connect` fixture which simulates
    # a connection failure.
    with pytest.raises(ConfigEntryNotReady):
        assert await async_setup_entry(hass, config_entry)


def _mock_client(**overrides):
    """Build a mock API client returning healthy status responses by default."""
    client = AsyncMock()
    client.connect_with_retry = AsyncMock(return_value=True)
    client.async_get_power_status = AsyncMock(return_value="PWON")
    client.async_get_power_alt = AsyncMock(return_value="PWON")
    client.async_get_volume = AsyncMock(return_value="MV50")
    client.async_get_volume_alt = AsyncMock(return_value="MV50")
    client.async_get_mute_status = AsyncMock(return_value="MUOFF")
    client.async_get_input = AsyncMock(return_value="SITV")
    client._send_command = AsyncMock(return_value=None)
    client.disconnect = AsyncMock()
    client.connection_stats = ConnectionStats()
    for name, value in overrides.items():
        setattr(client, name, value)
    return client


async def test_coordinator_update_data_returns_status_fields(hass):
    """A successful update cycle should return the parsed status of the AVR."""
    coordinator = DenonAvr3805DataUpdateCoordinator(hass, client=_mock_client())

    data = await coordinator._async_update_data()

    assert data == {
        "power": "PWON",
        "volume": "MV50",
        "mute": "MUOFF",
        "input": "SITV",
    }


async def test_coordinator_update_data_raises_update_failed_when_unreachable(hass):
    """If the AVR cannot be reached, the coordinator should raise UpdateFailed."""
    client = _mock_client(connect_with_retry=AsyncMock(return_value=False))
    coordinator = DenonAvr3805DataUpdateCoordinator(hass, client=client)

    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


async def test_execute_and_refresh_field_confirms_immediately(hass):
    """A confirmed status should be pushed to entities without a full poll."""
    client = _mock_client()
    coordinator = DenonAvr3805DataUpdateCoordinator(hass, client=client)
    coordinator.data = {"power": "PWON", "volume": "MV50", "mute": "MUON", "input": "SITV"}

    command = AsyncMock()
    query = AsyncMock(return_value="MUOFF")

    await coordinator.async_execute_and_refresh_field(
        command, "mute", query, settle_delay=0
    )

    client.connect.assert_awaited_once()
    command.assert_awaited_once()
    query.assert_awaited_once()
    client.disconnect.assert_awaited_once()
    assert coordinator.data["mute"] == "MUOFF"
    # Unrelated fields are preserved.
    assert coordinator.data["power"] == "PWON"


async def test_execute_and_refresh_field_falls_back_to_full_refresh(hass):
    """If the confirmation query fails, fall back to requesting a full refresh."""
    client = _mock_client()
    coordinator = DenonAvr3805DataUpdateCoordinator(hass, client=client)
    coordinator.data = {"mute": "MUON"}
    coordinator.async_request_refresh = AsyncMock()

    await coordinator.async_execute_and_refresh_field(
        AsyncMock(), "mute", AsyncMock(return_value=None), settle_delay=0
    )

    coordinator.async_request_refresh.assert_awaited_once()
    # Data is left untouched since the value couldn't be confirmed.
    assert coordinator.data["mute"] == "MUON"

