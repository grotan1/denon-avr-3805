"""Constants for Denon AVR-3805."""
# Base component constants
NAME = "Denon AVR-3805"
DOMAIN = "denon_avr_3805"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "1.9.0"
MANUFACTURER = "Denon"

ATTRIBUTION = "Data provided by http://jsonplaceholder.typicode.com/"
ISSUE_URL = "https://github.com/grotan1/denon-avr-3805/issues"

# Icons
ICON = "mdi:amplifier"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
MEDIA_PLAYER = "media_player"
PLATFORMS = [BINARY_SENSOR, SENSOR, SWITCH, MEDIA_PLAYER]


# Configuration and options
CONF_ENABLED = "enabled"
CONF_HOST = "host"
CONF_NAME = "name"
CONF_PORT = "port"
CONF_MODEL = "model"

# Defaults
DEFAULT_NAME = DOMAIN
DEFAULT_MODEL = "AVR-3805"


STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
