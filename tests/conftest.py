"""Global fixtures for Denon AVR-3805 integration."""
from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

pytest_plugins = "pytest_homeassistant_custom_component"


# Custom components are not loaded by default in the test environment, this
# fixture makes the ones in custom_components/ available for tests to set up.
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integrations for every test."""
    yield


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications", autouse=True)
def skip_notifications_fixture():
    """Skip notification calls."""
    with patch("homeassistant.components.persistent_notification.async_create"), patch(
        "homeassistant.components.persistent_notification.async_dismiss"
    ):
        yield


# This fixture bypasses the API client's connection and status queries so that
# integration/platform setup can be tested without a real AVR on the network.
@pytest.fixture(name="bypass_connect")
def bypass_connect_fixture():
    """Make the API client behave as if it is connected to a healthy AVR."""
    with patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient.connect",
        new=AsyncMock(return_value=None),
    ), patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient.connect_with_retry",
        new=AsyncMock(return_value=True),
    ), patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient.disconnect",
        new=AsyncMock(return_value=None),
    ), patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient.async_get_power_status",
        new=AsyncMock(return_value="PWON"),
    ), patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient.async_get_power_alt",
        new=AsyncMock(return_value="PWON"),
    ), patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient.async_get_volume",
        new=AsyncMock(return_value="MV50"),
    ), patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient.async_get_volume_alt",
        new=AsyncMock(return_value="MV50"),
    ), patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient.async_get_mute_status",
        new=AsyncMock(return_value="MUOFF"),
    ), patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient.async_get_input",
        new=AsyncMock(return_value="SITV"),
    ), patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient._send_command",
        new=AsyncMock(return_value=None),
    ):
        yield


# This fixture simulates a AVR that cannot be reached at all.
@pytest.fixture(name="error_on_connect")
def error_on_connect_fixture():
    """Simulate a connection failure to the AVR."""
    with patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient.connect",
        new=AsyncMock(side_effect=ConnectionError),
    ), patch(
        "custom_components.denon_avr_3805.api.DenonAvr3805ApiClient.connect_with_retry",
        new=AsyncMock(return_value=False),
    ):
        yield

