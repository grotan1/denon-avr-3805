"""
Custom integration to integrate Denon AVR-3805 with Home Assistant.

For more details about this integration, please refer to
https://github.com/grotan1/denon-avr-3805
"""
import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.update_coordinator import UpdateFailed

from .api import DenonAvr3805ApiClient
from .const import CONF_HOST
from .const import CONF_PORT
from .const import DOMAIN
from .const import PLATFORMS
from .const import STARTUP_MESSAGE

SCAN_INTERVAL = timedelta(seconds=30)

_LOGGER: logging.Logger = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    host = entry.data.get(CONF_HOST)
    port = entry.data.get(CONF_PORT)

    client = DenonAvr3805ApiClient(host, port)

    coordinator = DenonAvr3805DataUpdateCoordinator(hass, client=client)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][entry.entry_id] = coordinator

    platforms_to_setup = []
    for platform in PLATFORMS:
        if entry.options.get(platform, True):
            coordinator.platforms.append(platform)
            platforms_to_setup.append(platform)

    if platforms_to_setup:
        await hass.config_entries.async_forward_entry_setups(entry, platforms_to_setup)

    entry.add_update_listener(async_reload_entry)
    return True


class DenonAvr3805DataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        client: DenonAvr3805ApiClient,
    ) -> None:
        """Initialize."""
        self.api = client
        self.platforms = []

        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=SCAN_INTERVAL)

    async def _async_update_data(self):
        """Update data via library."""
        try:
            await self.api.connect()
            # Give AVR time to be ready after connection
            await asyncio.sleep(0.5)
            data = {}
            try:
                power_status = await self.api.async_get_power_status()
                if not power_status:
                    # Try alternative power query
                    power_status = await self.api.async_get_power_alt()
                data["power"] = power_status
                _LOGGER.debug("Power status query returned: %s", power_status)
            except Exception as e:
                _LOGGER.debug("Power status query failed: %s", e)
                data["power"] = None

            # Small delay between queries to avoid overwhelming the AVR
            await asyncio.sleep(0.2)

            try:
                volume_status = await self.api.async_get_volume()
                if not volume_status:
                    # Try alternative volume query
                    volume_status = await self.api.async_get_volume_alt()
                data["volume"] = volume_status
                _LOGGER.debug("Volume status query returned: %s", volume_status)
            except Exception as e:
                _LOGGER.debug("Volume status query failed: %s", e)
                data["volume"] = None

            # Small delay between queries to avoid overwhelming the AVR
            await asyncio.sleep(0.2)

            try:
                mute_status = await self.api.async_get_mute_status()
                data["mute"] = mute_status
                _LOGGER.debug("Mute status query returned: %s", mute_status)
            except Exception as e:
                _LOGGER.debug("Mute status query failed: %s", e)
                data["mute"] = None

            await asyncio.sleep(0.2)

            try:
                input_status = await self.api.async_get_input()
                data["input"] = input_status
                _LOGGER.debug("Input status query returned: %s", input_status)
            except Exception as e:
                _LOGGER.debug("Input status query failed: %s", e)
                data["input"] = None

            await asyncio.sleep(0.2)

            # Try additional queries that might work better with this AVR
            try:
                # Some AVRs respond better to different query formats
                alt_input = await self.api._send_command("SI ?")
                if alt_input and alt_input != input_status:
                    _LOGGER.debug("Alternative input query returned: %s", alt_input)
                    if input_status is None and alt_input:
                        data["input"] = alt_input
            except Exception as e:
                _LOGGER.debug("Alternative input query failed: %s", e)

            await self.api.disconnect()
            _LOGGER.info("Coordinator update completed - Power: %s, Volume: %s, Mute: %s, Input: %s",
                        data.get("power"), data.get("volume"), data.get("mute"), data.get("input"))
            return data
        except Exception as exception:
            _LOGGER.error("Failed to update AVR data: %s", exception)
            raise UpdateFailed() from exception


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    unloaded = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, platform)
                for platform in PLATFORMS
                if platform in coordinator.platforms
            ]
        )
    )
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
