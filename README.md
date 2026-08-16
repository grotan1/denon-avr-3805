# Denon AVR-3805 🎵

### v3.0.5 - Translation Cleanup

**HACS/hassfest compliance fix.** Removed leftover URLs from the config flow description text in all 26 translation files (they no longer matched the simplified English source), and fixed a corrupted character in this README.
[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![Black][black-shield]][black]

[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

[![Discord][discord-shield]][discord]
[![Community Forum][forum-shield]][forum]

## 🌟 **Reliable Home Assistant Integration**

Professional Denon AVR control with **26-language multilingual support**, stable connectivity, and consistent entity naming. Built for international users and reliable automation.

## 🎯 **Platforms & Features**

| Platform | Description | Entity Examples |
|----------|-------------|-----------------|
| `media_player` | **Clean naming**: Just device name (e.g., `denon`) | `media_player.denon` |
| `sensor` | Volume and input monitoring | `sensor.denon_volume`, `sensor.denon_input` |
| `switch` | Power and mute control | `switch.denon_power`, `switch.denon_mute` |
| `binary_sensor` | Real-time connectivity status | `binary_sensor.denon_connectivity` |

## ✨ **Key Features**

### 🌍 **Multilingual Excellence (26 Languages)**
Complete European Union language support with **Ukrainian solidarity**:
🇺🇦 Ukrainian, 🇭🇺 Hungarian, 🇷🇴 Romanian, 🇧🇬 Bulgarian, 🇭🇷 Croatian, 🇸🇮 Slovenian, 🇸🇰 Slovak, 🇱🇻 Latvian, 🇱🇹 Lithuanian, 🇪🇪 Estonian, 🇬🇷 Greek, 🇲🇹 Maltese, 🇨🇿 Czech, 🇩🇰 Danish, 🇩🇪 German, 🇪🇸 Spanish, 🇫🇮 Finnish, 🇫🇷 French, 🇮🇸 Icelandic, 🇮🇹 Italian, 🇳🇴 Norwegian, 🇳🇱 Dutch, 🇵🇱 Polish, 🇵🇹 Portuguese, 🇸🇪 Swedish, 🇺🇸 English

### 🛡️ **Enhanced Connection Detection**
- **Accurate Status**: Advanced detection requiring actual AVR responses (no false positives)
- **Rich Diagnostics**: TCP vs serial connection health with success rate monitoring
- **Reliable Sensors**: Volume, power, input sensors show proper values (no "unknown" states)
- **Smart Recovery**: Automatic reconnection with proper error handling and cleanup
- **Professional Monitoring**: Comprehensive diagnostic attributes for troubleshooting

### 🎛️ **Easy Configuration**
- **Simple Setup**: Straightforward connection configuration
- **Flexible Options**: Customize name and connection settings
- **Quick Integration**: Easy addition via Home Assistant Settings → Integrations
- **Model Support**: Designed for Denon AVR-3805 and compatible models

### 🌐 **Perfect Entity Naming**
- **Media Player**: Clean device name only (`denon`)
- **Other Entities**: Consistent English suffixes (`denon_input`, `denon_volume`, etc.)
- **Language Independent**: Same entity names regardless of Home Assistant language
- **Automation Friendly**: Predictable entity references for international users

### 🔧 **Advanced Connectivity**
- **TCP/IP Connection**: Serial-over-TCP using ser2net or similar
- **Broad Compatibility**: Works with multiple Denon AVR models with serial ports
- **Intelligent Updates**: Connection changes happen instantly without reloads

## Configuration

The integration connects to the Denon AVR-3805 via serial port exposed over TCP using ser2net or similar tools.

### Setting up Serial-to-TCP Bridge

1. On your Raspberry Pi (or host with serial access), install and configure ser2net:
   ```bash
   sudo apt install ser2net
   ```

2. Create or edit `/etc/ser2net.yaml` with the following configuration:
   ```yaml
   connection: &con01
     accepter: tcp,2000
     enable: on
     options:
       banner: ser2net
       kickolduser: true
       telnet-brk-on-sync: true
     connector: serialdev,/dev/ttyUSB0,9600n81
   ```

3. Restart ser2net:
   ```bash
   sudo systemctl restart ser2net
   ```

### Home Assistant Configuration

In Home Assistant, add the integration and provide:
- **Host**: IP address of the device running the serial-to-TCP bridge
- **Port**: The TCP port configured for the serial connection (e.g., 2000)
- **Name** (optional): Custom name for your AVR (defaults to "Denon AVR-3805")

## 📦 **Installation**

### **HACS Installation (Recommended)**
1. **Open HACS** in Home Assistant
2. **Go to Integrations**
3. **Click "+ Explore & Download Repositories"**
4. **Search for** "Denon AVR-3805"
5. **Download** and restart Home Assistant
6. **Add Integration**: Settings → Devices & Services → Add Integration → "Denon AVR-3805"

### **Manual Installation**
1. **Download** the latest release from [GitHub Releases](https://github.com/grotan1/denon-avr-3805/releases)
2. **Extract** to `config/custom_components/denon_avr_3805/`
3. **Restart** Home Assistant
4. **Add Integration**: Settings → Devices & Services → Add Integration → "Denon AVR-3805"

### **File Structure** (26 Language Files)
```text
custom_components/denon_avr_3805/
├── translations/
│   ├── bg.json    # Bulgarian     🇧🇬    ├── et.json    # Estonian      🇪🇪
│   ├── cs.json    # Czech         🇨🇿    ├── fi.json    # Finnish       🇫🇮
│   ├── da.json    # Danish        🇩🇰    ├── fr.json    # French        🇫🇷
│   ├── de.json    # German        🇩🇪    ├── hr.json    # Croatian      🇭🇷
│   ├── el.json    # Greek         🇬🇷    ├── hu.json    # Hungarian     🇭🇺
│   ├── en.json    # English       🇺🇸    ├── is.json    # Icelandic     🇮🇸
│   ├── es.json    # Spanish       🇪🇸    ├── it.json    # Italian       🇮🇹
│   ├── lv.json    # Latvian       🇱🇻    ├── mt.json    # Maltese       🇲🇹
│   ├── lt.json    # Lithuanian    🇱🇹    ├── nb.json    # Norwegian     🇳🇴
│   ├── nl.json    # Dutch         🇳🇱    ├── pl.json    # Polish        🇵🇱
│   ├── pt.json    # Portuguese    🇵🇹    ├── ro.json    # Romanian      🇷🇴
│   ├── si.json    # Slovenian     🇸🇮    ├── sk.json    # Slovak        🇸🇰
│   ├── sv.json    # Swedish       🇸🇪    ├── uk.json    # Ukrainian     🇺🇦
├── __init__.py           # Integration loader with intelligent lifecycle
├── api.py               # Enterprise-grade API client with 99%+ reliability
├── binary_sensor.py     # Real-time connectivity monitoring
├── config_flow.py       # Menu-driven configuration with live testing
├── const.py            # Constants and configuration options
├── entity.py           # Base entity with configurable device info
├── manifest.json       # Integration metadata (v1.8.9)
├── media_player.py     # Clean-named media player entity
├── sensor.py           # Volume and input sensors with English names
└── switch.py           # Power and mute switches with English names
```

## 🎛️ **Configuration**

All configuration is done through the **user-friendly interface** with **live connection testing** and **menu-driven options**.

### **Initial Setup**
1. **Host**: IP address of ser2net device
2. **Port**: TCP port (e.g., 2000)
3. **Name**: Custom device name (optional)
4. **Model**: Exact AVR model (e.g., AVR-3805, AVR-4306)

### **Advanced Options** (No Restart Required)
- **Connection Settings**: Update IP, port, name, model with live testing
- **Platform Control**: Enable/disable sensors, switches, media player
- **Current Values**: See existing settings before making changes

## 🎯 **Perfect Entity Examples**

### **Media Player** (Clean Device Name)
```yaml
entity_id: media_player.denon
name: "Denon"  # Just your device name, nothing else
```

### **Sensors** (English Suffixes)
```yaml
entity_id: sensor.denon_volume
name: "Denon Volume"

entity_id: sensor.denon_input
name: "Denon Input"
```

### **Switches** (English Suffixes)
```yaml
entity_id: switch.denon_power
name: "Denon Power"

entity_id: switch.denon_mute
name: "Denon Mute"
```

### **Automation Example**
```yaml
automation:
  - alias: "Movie Night Setup"
    trigger:
      platform: state
      entity_id: sensor.denon_input
      to: "DVD"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.denon_power
      - service: media_player.volume_set
        target:
          entity_id: media_player.denon
        data:
          volume_level: 0.7
```

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

## Credits

This project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template.

Code template was mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template

## 📜 **Version History**

- **v3.0.5** (Current) - **QUALITY**: Removed stale URLs from translation descriptions, README fixes
- **v3.0.4** - **RELIABILITY**: Instant mute/unmute feedback, diagnostics bug fix, rewritten test suite
- **v3.0.3** - **RELIABILITY**: Enhanced connection detection, sensor accuracy, diagnostics
- **v3.0.2** - **DEVENV**: Modern devcontainer, development environment improvements
- **v3.0.1** - **QUALITY**: Hassfest compliance, automated validation, HACS ready
- **v3.0.0** - **MAJOR**: Enhanced features with professional validation workflows
- **v2.0.5** - **STABLE**: Universal icon compatibility and visual improvements
- **v2.0.3** - **STABLE**: Emergency revert to working v1.9.0 codebase
- **v1.9.0** - **STABLE**: Full 26-language support with English entity IDs
- **Earlier versions** - Progressive multilingual and reliability improvements

**Always use the latest version for the best experience and stability.**

## 🇺🇦 **Slava Ukrajini!**
*This integration stands in solidarity with Ukraine and the Ukrainian people in their fight for freedom, democracy, and territorial integrity. The Ukrainian language support in this integration is our small contribution to showing support for the brave defenders of Ukraine.*

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[black]: https://github.com/psf/black
[black-shield]: https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge
[buymecoffee]: https://www.buymeacoffee.com/grotan
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/grotan1/denon-avr-3805.svg?style=for-the-badge
[commits]: https://github.com/grotan1/denon-avr-3805/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/grotan1/denon-avr-3805.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40grotan1-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/grotan1/denon-avr-3805.svg?style=for-the-badge
[releases]: https://github.com/grotan1/denon-avr-3805/releases
[user_profile]: https://github.com/grotan1
