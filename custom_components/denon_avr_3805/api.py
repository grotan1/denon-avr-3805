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

    async def _send_command(self, command: str, expected_prefix: str = None) -> str | None:
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

                # If we know what prefix to expect, try to find the right response
                if expected_prefix:
                    return await self._read_expected_response(expected_prefix)
                else:
                    # Fallback to original behavior
                    response = await asyncio.wait_for(
                        self._reader.readuntil(b"\r"), timeout=5.0
                    )
                    decoded = response.decode().strip()
                    _LOGGER.debug("Received response: %s", decoded)

                    # Filter out command echoes
                    if decoded == command:
                        _LOGGER.debug("Received echo of command, reading actual response")
                        try:
                            response2 = await asyncio.wait_for(
                                self._reader.readuntil(b"\r"), timeout=2.0
                            )
                            decoded2 = response2.decode().strip()
                            _LOGGER.debug("Received actual response: %s", decoded2)
                            return decoded2
                        except asyncio.TimeoutError:
                            _LOGGER.debug("No actual response received after echo")
                            return None

                    return decoded
            except asyncio.TimeoutError:
                _LOGGER.debug("Timeout reading response for command: %s", command)
                return None
            except Exception as e:
                _LOGGER.error("Error sending command %s: %s", command, e)
                raise

                _LOGGER.error("Error sending command %s: %s", command, e)
                raise

    async def _read_expected_response(self, expected_prefix: str) -> str | None:
        """Read responses until we find one that starts with the expected prefix."""
        start_time = asyncio.get_event_loop().time()
        timeout = 5.0  # Total timeout for finding the right response
        
        while asyncio.get_event_loop().time() - start_time < timeout:
            try:
                response = await asyncio.wait_for(
                    self._reader.readuntil(b"\r"), timeout=1.0
                )
                decoded = response.decode().strip()
                _LOGGER.debug("Received response: %s", decoded)
                
                # Check if this is the expected response
                if decoded.startswith(expected_prefix):
                    _LOGGER.debug("Found expected response: %s", decoded)
                    return decoded
                
                # If it's a command echo, skip it
                if decoded in ["PW?", "MV?", "MU?", "SI?", "SI ?", "CV?", "ZM?"]:
                    _LOGGER.debug("Skipping command echo: %s", decoded)
                    continue
                    
                # Skip other invalid responses
                _LOGGER.debug("Skipping unexpected response: %s", decoded)
                
            except asyncio.TimeoutError:
                _LOGGER.debug("Timeout waiting for expected response with prefix: %s", expected_prefix)
                break
            except Exception as e:
                _LOGGER.debug("Error reading response: %s", e)
                break
                
        _LOGGER.debug("Failed to find expected response with prefix: %s", expected_prefix)
        return None
        """Turn the AVR on."""
        await self._send_command("PWON")

    async def async_power_off(self) -> None:
        """Turn the AVR to standby."""
        await self._send_command("PWSTANDBY")

    async def async_get_power_status(self) -> str | None:
        """Get power status (PWON or PWSTANDBY)."""
        return await self._send_command("PW?", "PW")

    async def async_mute_on(self) -> None:
        """Mute the AVR."""
        await self._send_command("MUON")

    async def async_mute_off(self) -> None:
        """Unmute the AVR."""
        await self._send_command("MUOFF")

    async def async_get_mute_status(self) -> str | None:
        """Get mute status (MUON or MUOFF)."""
        return await self._send_command("MU?", "MU")

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
        return await self._send_command("MV?", "MV")

    async def async_select_input(self, input_code: str) -> None:
        """Select input (e.g., 'VCR', 'TV', 'DVD')."""
        await self._send_command(f"SI{input_code}")

    async def async_get_input(self) -> str | None:
        """Get current input."""
        return await self._send_command("SI?", "SI")

    async def _drain_input(self) -> None:
        """Drain any pending input from the connection."""
        if not self._reader:
            return
        try:
            # Read any pending data with a short timeout
            while True:
                data = await asyncio.wait_for(
                    self._reader.readuntil(b"\r"), timeout=0.1
                )
                _LOGGER.debug("Drained pending data: %s", data.decode().strip())
        except asyncio.TimeoutError:
            # No more data to drain
            pass
        except Exception as e:
            _LOGGER.debug("Error draining input: %s", e)
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
        # Try MV? again as fallback (CV? was returning power status)
        return await self._send_command("MV?", "MV")

    async def async_get_power_alt(self) -> str | None:
        """Try alternative power query methods."""
        # Try PW? first
        response = await self._send_command("PW?", "PW")
        if response:
            return response
        # Some AVRs use ZM? for main zone power
        return await self._send_command("ZM?", "ZM")

    # Add more methods as needed for other AVR functions
