"""API Client for Denon AVR-3805 via serial over TCP (ser2net)."""
import asyncio
import logging
import socket

TIMEOUT = 5  # seconds for socket operations


_LOGGER: logging.Logger = logging.getLogger(__package__)


class DenonAvr3805ApiClient:
    def __init__(self, host: str, port: int) -> None:
        """Initialize the API client for TCP connection to ser2net."""
        self._host = host
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()  # To serialize commands

    async def connect(self) -> None:
        """Establish connection to ser2net."""
        try:
            self._reader, self._writer = await asyncio.wait_for(
                asyncio.open_connection(self._host, self._port), timeout=TIMEOUT
            )
            _LOGGER.info("Connected to Denon AVR at %s:%s", self._host, self._port)
        except (asyncio.TimeoutError, OSError) as e:
            _LOGGER.error("Failed to connect to %s:%s - %s", self._host, self._port, e)
            raise

    async def disconnect(self) -> None:
        """Close the connection."""
        if self._writer:
            self._writer.close()
            await self._writer.wait_closed()
            self._reader = None
            self._writer = None
            _LOGGER.info("Disconnected from Denon AVR")

    async def _send_command(self, command: str) -> str | None:
        """Send a command and return the response."""
        if not self._writer or not self._reader:
            raise ConnectionError("Not connected to AVR")

        async with self._lock:
            try:
                # Send command with carriage return
                full_command = (command + "\r").encode()
                _LOGGER.debug("Sending command: %s", command)
                self._writer.write(full_command)
                await self._writer.drain()

                # Read response (up to 100 bytes, timeout 2s)
                response = await asyncio.wait_for(
                    self._reader.readuntil(b"\r"), timeout=2.0
                )
                decoded = response.decode().strip()
                _LOGGER.debug("Received response: %s", decoded)

                # Filter out command echoes - if response matches command, it's an echo
                if decoded == command:
                    _LOGGER.debug("Received echo of command, reading actual response")
                    try:
                        response2 = await asyncio.wait_for(
                            self._reader.readuntil(b"\r"), timeout=1.0
                        )
                        decoded2 = response2.decode().strip()
                        _LOGGER.debug("Received actual response: %s", decoded2)
                        return decoded2
                    except asyncio.TimeoutError:
                        _LOGGER.debug("No actual response received after echo")
                        return None

                # If we get a response that doesn't match the command, it's likely a real response
                return decoded
            except asyncio.TimeoutError:
                _LOGGER.debug("Timeout reading response for command: %s", command)
                return None
            except Exception as e:
                _LOGGER.error("Error sending command %s: %s", command, e)
                raise

    async def async_power_on(self) -> None:
        """Turn the AVR on."""
        await self._send_command("PWON")

    async def async_power_off(self) -> None:
        """Turn the AVR to standby."""
        await self._send_command("PWSTANDBY")

    async def async_get_power_status(self) -> str | None:
        """Get power status (PWON or PWSTANDBY)."""
        return await self._send_command("PW?")

    async def async_mute_on(self) -> None:
        """Mute the AVR."""
        await self._send_command("MUON")

    async def async_mute_off(self) -> None:
        """Unmute the AVR."""
        await self._send_command("MUOFF")

    async def async_get_mute_status(self) -> str | None:
        """Get mute status (MUON or MUOFF)."""
        return await self._send_command("MU?")

    async def async_volume_up(self) -> None:
        """Increase volume."""
        await self._send_command("MVUP")

    async def async_volume_down(self) -> None:
        """Decrease volume."""
        await self._send_command("MVDOWN")

    async def async_set_volume(self, level: int) -> None:
        """Set volume level (0-98)."""
        if not 0 <= level <= 98:
            raise ValueError("Volume level must be between 0 and 98")
        await self._send_command(f"MV{level:02d}")

    async def async_get_volume(self) -> str | None:
        """Get current volume level."""
        return await self._send_command("MV?")

    async def async_select_input(self, input_code: str) -> None:
        """Select input (e.g., 'VCR', 'TV', 'DVD')."""
        await self._send_command(f"SI{input_code}")

    async def async_get_input(self) -> str | None:
        """Get current input."""
        return await self._send_command("SI?")

    async def async_get_status_all(self) -> dict:
        """Get all status information at once (for debugging)."""
        status = {}
        queries = [
            ("power", "PW?"),
            ("volume", "MV?"),
            ("mute", "MU?"),
            ("input", "SI?"),
        ]

        for name, command in queries:
            try:
                response = await self._send_command(command)
                status[name] = response
                _LOGGER.debug("Query %s (%s) returned: %s", name, command, response)
            except Exception as e:
                _LOGGER.debug("Query %s (%s) failed: %s", name, command, e)
                status[name] = None

        return status

    async def async_get_volume_alt(self) -> str | None:
        """Try alternative volume query methods."""
        # Some AVRs respond better to CV? (channel volume)
        response = await self._send_command("CV?")
        if response:
            return response
        # Try MV? again as fallback
        return await self._send_command("MV?")

    async def async_get_power_alt(self) -> str | None:
        """Try alternative power query methods."""
        # Try PW? first
        response = await self._send_command("PW?")
        if response:
            return response
        # Some AVRs use ZM? for main zone power
        return await self._send_command("ZM?")

    # Add more methods as needed for other AVR functions
