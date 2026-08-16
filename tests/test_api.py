"""Tests for the Denon AVR-3805 API client."""
import asyncio

import pytest

from custom_components.denon_avr_3805.api import ConnectionStats
from custom_components.denon_avr_3805.api import DenonAvr3805ApiClient

# Fixed responses this fake AVR gives to status queries.
_RESPONSES = {
    "PW?": "PWON",
    "MU?": "MUOFF",
    "MV?": "MV50",
    "SI?": "SITV",
}


class FakeDenonServer:
    """A minimal TCP server that emulates Denon AVR-3805 serial-over-TCP responses."""

    def __init__(self):
        self.received = []
        self.port = None
        self._server = None

    async def start(self):
        """Start listening on an ephemeral localhost port."""
        self._server = await asyncio.start_server(self._handle, "127.0.0.1", 0)
        self.port = self._server.sockets[0].getsockname()[1]

    async def stop(self):
        """Stop the server."""
        self._server.close()
        await self._server.wait_closed()

    async def _handle(self, reader, writer):
        try:
            while True:
                line = await reader.readuntil(b"\r")
                command = line.decode().strip()
                self.received.append(command)
                response = _RESPONSES.get(command)
                if response is not None:
                    writer.write((response + "\r").encode())
                    await writer.drain()
        except (asyncio.IncompleteReadError, ConnectionResetError):
            pass
        finally:
            writer.close()


@pytest.fixture
async def fake_server(socket_enabled):
    """Run a fake AVR TCP server for the duration of a test."""
    server = FakeDenonServer()
    await server.start()
    yield server
    await server.stop()


async def test_connect_and_disconnect(fake_server):
    """Connecting and disconnecting should update the is_connected property."""
    client = DenonAvr3805ApiClient("127.0.0.1", fake_server.port)
    assert not client.is_connected

    await client.connect()
    assert client.is_connected

    await client.disconnect()
    assert not client.is_connected


async def test_connect_with_retry_failure(socket_enabled):
    """Connecting to a closed port should fail after retries and update stats."""
    client = DenonAvr3805ApiClient(
        "127.0.0.1", 1, config={"max_retries": 2, "retry_delay": 0.01}
    )

    assert await client.connect_with_retry() is False
    assert client.connection_stats.failed_connections == 1
    assert client.connection_stats.consecutive_failures == 1
    assert client.connection_stats.success_rate == 0.0

    with pytest.raises(ConnectionError):
        await client.connect()


async def test_get_power_status(fake_server):
    """A power query should return the AVR's power state."""
    client = DenonAvr3805ApiClient("127.0.0.1", fake_server.port)
    await client.connect()

    assert await client.async_get_power_status() == "PWON"

    await client.disconnect()


async def test_power_on_off_send_expected_commands(fake_server):
    """Power on/off should send the correct raw commands, with no response expected."""
    client = DenonAvr3805ApiClient("127.0.0.1", fake_server.port)
    await client.connect()

    await client.async_power_on()
    await client.async_power_off()
    await asyncio.sleep(0.05)  # let the fake server process the fire-and-forget commands

    await client.disconnect()
    assert "PWON" in fake_server.received
    assert "PWSTANDBY" in fake_server.received


async def test_mute_on_off_and_status(fake_server):
    """Mute on/off should send the correct commands and the status query should parse them."""
    client = DenonAvr3805ApiClient("127.0.0.1", fake_server.port)
    await client.connect()

    await client.async_mute_on()
    await client.async_mute_off()
    assert await client.async_get_mute_status() == "MUOFF"

    await client.disconnect()
    assert "MUON" in fake_server.received
    assert "MUOFF" in fake_server.received


async def test_volume_up_down_and_get(fake_server):
    """Volume up/down commands should be sent and the current level parsed."""
    client = DenonAvr3805ApiClient("127.0.0.1", fake_server.port)
    await client.connect()

    await client.async_volume_up()
    await client.async_volume_down()
    assert await client.async_get_volume() == "MV50"

    await client.disconnect()
    assert "MVUP" in fake_server.received
    assert "MVDOWN" in fake_server.received


async def test_set_volume_sends_formatted_command(fake_server):
    """Setting the volume should send a zero-padded MV command."""
    client = DenonAvr3805ApiClient("127.0.0.1", fake_server.port)
    await client.connect()

    await client.async_set_volume(7)
    await asyncio.sleep(0.05)  # let the fake server process the fire-and-forget command

    await client.disconnect()
    assert "MV07" in fake_server.received


@pytest.mark.parametrize("level", [-1, 99])
async def test_set_volume_out_of_range_raises(level):
    """Volume levels outside of 0-98 should be rejected before sending anything."""
    client = DenonAvr3805ApiClient("127.0.0.1", 1)

    with pytest.raises(ValueError):
        await client.async_set_volume(level)


async def test_select_input_and_get_input(fake_server):
    """Selecting an input should send the SI command and the query should parse the source."""
    client = DenonAvr3805ApiClient("127.0.0.1", fake_server.port)
    await client.connect()

    await client.async_select_input("DVD")
    assert await client.async_get_input() == "SITV"

    await client.disconnect()
    assert "SIDVD" in fake_server.received


async def test_get_all_status(fake_server):
    """The diagnostic helper should query power, volume, mute and input."""
    client = DenonAvr3805ApiClient("127.0.0.1", fake_server.port)
    await client.connect()

    status = await client.async_get_all_status()

    await client.disconnect()
    assert status == {
        "power": "PWON",
        "volume": "MV50",
        "mute": "MUOFF",
        "input": "SITV",
    }


async def test_get_volume_alt_and_power_alt(fake_server):
    """Alternative query helpers should fall back correctly."""
    client = DenonAvr3805ApiClient("127.0.0.1", fake_server.port)
    await client.connect()

    assert await client.async_get_volume_alt() == "MV50"
    assert await client.async_get_power_alt() == "PWON"

    await client.disconnect()


async def test_send_command_without_connection_raises():
    """Sending a command while not connected should raise ConnectionError."""
    client = DenonAvr3805ApiClient("127.0.0.1", 1)

    with pytest.raises(ConnectionError):
        await client._send_command("PW?", "PW")


async def test_command_timeout_returns_none(fake_server):
    """Querying for a prefix the AVR never sends should time out gracefully."""
    client = DenonAvr3805ApiClient(
        "127.0.0.1",
        fake_server.port,
        config={"read_timeout": 0.05, "command_timeout": 0.5},
    )
    await client.connect()

    assert await client._send_command("ZZ?", "ZZ") is None

    await client.disconnect()


async def test_get_diagnostics(fake_server):
    """Diagnostics should expose connection info, config and stats."""
    client = DenonAvr3805ApiClient("127.0.0.1", fake_server.port)
    await client.connect()
    await client.async_get_power_status()

    diagnostics = client.get_diagnostics()

    await client.disconnect()
    assert diagnostics["connection"]["host"] == "127.0.0.1"
    assert diagnostics["connection"]["port"] == fake_server.port
    assert diagnostics["stats"]["total_commands"] >= 1


def test_connection_stats_success_rate_with_no_attempts():
    """With no connection attempts yet, the success rate should default to 1.0."""
    stats = ConnectionStats()
    assert stats.success_rate == 1.0
    assert stats.is_healthy is True


def test_connection_stats_unhealthy_after_failures():
    """Repeated consecutive failures should mark the connection unhealthy."""
    stats = ConnectionStats()
    stats.failed_connections = 3
    stats.consecutive_failures = 3
    assert stats.is_healthy is False

