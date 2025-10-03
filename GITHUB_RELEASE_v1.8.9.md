# 🌐 v1.8.9 - English Entity Naming Standardization 🇺🇦

## 🎯 **Global Consistency Release**

This release standardizes all entity naming to use consistent English suffixes, ensuring predictable entity names regardless of your Home Assistant language setting. Perfect for international users, automation developers, and anyone sharing configurations.

### ✨ **What's Standardized**
- 🌐 **English Suffixes**: All entities now use standard English names
- 📝 **Predictable Automation**: Same entity names across all HA language settings
- 🔄 **Global Portability**: Share configs without language-specific entity names
- 🎯 **Professional Consistency**: Standard technical terminology throughout

## 🔍 **The Language Problem Solved**

### **❌ Before v1.8.9 (Language-Dependent)**
Entity names changed based on your Home Assistant language:

**Norwegian Users Saw:**
- `sensor.denon_inngang` (Norwegian: "input")
- `sensor.denon_volum` (Norwegian: "volume") 
- `switch.denon_strøm` (Norwegian: "power")
- `switch.denon_demp` (Norwegian: "mute")

**German Users Saw:**
- `sensor.denon_eingang` (German: "input")
- `sensor.denon_lautstärke` (German: "volume")

**French Users Saw:**
- `sensor.denon_entrée` (French: "input")
- `sensor.denon_volume` (French: "volume")

### **✅ After v1.8.9 (Universal English)**
**All Users See (Regardless of HA Language):**
- `sensor.denon_input` ✅
- `sensor.denon_volume` ✅  
- `switch.denon_power` ✅
- `switch.denon_mute` ✅
- `binary_sensor.denon_connectivity` ✅
- `media_player.denon` ✅ (clean device name only)

## 🛠️ **Technical Implementation**

### **The Challenge**
Home Assistant's entity naming with `_attr_has_entity_name = True` was using `translation_key` to generate localized entity names, causing unpredictable naming across different language settings.

### **The Solution**
```python
# Added explicit English names to all entities
@property
def name(self):
    """Return the name of the sensor."""
    return "Input"  # Always English, always predictable

@property
def translation_key(self):
    """Return the translation key for this entity."""
    return "input"  # Preserved for internal HA functionality
```

### **How It Works**
- **Explicit English names**: Override automatic translation-based naming
- **Language-independent**: Same entity names regardless of HA language
- **Automation-friendly**: Predictable entity references for scripts
- **Documentation-ready**: Examples work for all international users

## 🌍 **Perfect for International Users**

### 🎯 **Automation Portability**
```yaml
# This automation now works identically for all users worldwide:
automation:
  - alias: "Movie Night Setup"
    trigger:
      platform: state
      entity_id: sensor.denon_input  # Always 'input', never 'inngang' or 'eingang'
      to: "DVD"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.denon_power  # Always 'power', never 'strøm' or 'strom'
      - service: media_player.volume_set
        target:
          entity_id: media_player.denon  # Clean device name
        data:
          volume_level: 0.7
```

### 📚 **Documentation Benefits**
- **Universal Examples**: Code samples work for everyone
- **Community Sharing**: Share automations without language barriers
- **Support Simplicity**: Consistent entity names for troubleshooting
- **Professional Standards**: English technical terminology globally

### 🌍 **Multilingual Excellence Preserved**
- **26 Language Support**: All UI translations still work perfectly
- **Cultural Adaptation**: HA interface remains localized
- **Entity Consistency**: Only entity names standardized, not functionality
- **Best of Both Worlds**: Localized UI + consistent entity naming

## 🚀 **Immediate Benefits**

### 📝 **Enhanced Automation Development**
- **Predictable Names**: Entity names never change based on language
- **Copy-Paste Friendly**: Share configs with international community
- **IDE Support**: Better autocompletion with standard English names
- **Reduced Errors**: No more guessing translated entity names

### 🎛️ **Professional Configuration Management**
- **Version Control**: Config files work across different language environments
- **Team Collaboration**: Multi-language teams use same entity references
- **Documentation**: Clear, unambiguous entity identification
- **Migration**: Move configs between different HA language setups

### 🌐 **Global Community Benefits**
- **Forum Support**: Everyone uses same entity names in discussions
- **Tutorial Compatibility**: All guides work regardless of language
- **Add-on Integration**: Third-party tools use consistent entity names
- **Standard Compliance**: Follows international IoT naming conventions

## 📦 **Installation & Update**

### **HACS Installation (Recommended)**
```bash
1. Go to HACS → Integrations
2. Find "Denon AVR-3805"
3. Click "Update" (when available)
4. Restart Home Assistant
5. Verify English entity naming consistency
```

### **Manual Installation**
```bash
1. Download v1.8.9 release
2. Replace existing custom_components/denon_avr_3805/
3. Restart Home Assistant  
4. Check all entities show English suffixes
```

### **Post-Update Verification**
After updating, confirm:
- ✅ `sensor.denon_input` (not inngang/eingang/entrée)
- ✅ `sensor.denon_volume` (consistent across languages)
- ✅ `switch.denon_power` (not strøm/strom/alimentation)
- ✅ `switch.denon_mute` (not demp/stumm/muet)
- ✅ `binary_sensor.denon_connectivity` (universal)
- ✅ `media_player.denon` (clean device name only)

## 🎯 **Migration Notes**

### **From v1.8.8 → v1.8.9**
- **Language-Specific Updates**: Entity names may change if you were using non-English HA
- **Automation Updates**: Update scripts using translated entity names
- **Zero Configuration**: All existing settings and data preserved
- **Immediate Benefits**: Consistent naming applies after restart

### **Entity Name Changes by Language**

| **Entity Type** | **Old (Translated)** | **New (English)** |
|-----------------|---------------------|-------------------|
| Input Sensor | `inngang`/`eingang`/`entrée` | `input` ✅ |
| Volume Sensor | `volum`/`lautstärke`/`volume` | `volume` ✅ |
| Power Switch | `strøm`/`strom`/`alimentation` | `power` ✅ |
| Mute Switch | `demp`/`stumm`/`muet` | `mute` ✅ |
| Connectivity | `tilkobling`/`verbindung`/`connexion` | `connectivity` ✅ |

## 🎮 **Perfect Entity Naming Achieved**

### **Complete Naming Strategy**
- **Media Player**: `denon` (clean device name only)
- **Sensors**: `denon_input`, `denon_volume` (English suffixes)
- **Switches**: `denon_power`, `denon_mute` (English suffixes)  
- **Binary Sensors**: `denon_connectivity` (English suffixes)

### **Automation Excellence**
```yaml
# Perfect, predictable automation syntax:
automation:
  - alias: "AVR Status Monitor"
    trigger:
      - platform: state
        entity_id: binary_sensor.denon_connectivity
        to: "off"
    condition:
      - condition: state
        entity_id: switch.denon_power
        state: "on"
    action:
      - service: notify.mobile_app
        data:
          message: "AVR connection lost while powered on!"
      - service: switch.turn_off
        target:
          entity_id: switch.denon_power
```

## 🙏 **Special Recognition**

### 🇺🇦 **Ukraine Solidarity Through Standards**
This standardization release demonstrates our commitment to both technical excellence and international solidarity. By ensuring Ukrainian users have the same predictable, professional entity naming as users worldwide, we reinforce that quality transcends borders. Every consistently named entity in Ukrainian represents our ongoing support. **Slava Ukrajini! 🇺🇦**

### 🌍 **Global Unity Through Technology**
Standardized English entity naming creates unity in the international Home Assistant community. When a Norwegian user, Ukrainian user, and German user can share the exact same automation code, technology truly serves to unite rather than divide.

### 🤝 **Community Excellence Through Consistency**
Thanks to users who highlighted the importance of consistent entity naming across languages. This attention to international usability drives the pursuit of excellence that benefits the entire global community.

---

## 📊 **Release Summary**

- **Version**: 1.8.9
- **Type**: Global Consistency Release
- **Focus**: English entity naming standardization  
- **Compatibility**: Home Assistant 2021.12.0+
- **Languages**: 26 (UI translations preserved)
- **Breaking Changes**: Entity names may change for non-English HA users
- **Migration**: Update automations using translated entity names

## 🔄 **Recommended Action**

**Update Highly Recommended** for:
- International users with non-English HA language settings
- Automation developers sharing configurations globally
- Professional installations requiring consistent naming
- Community members participating in forums and tutorials
- Anyone wanting predictable, language-independent entity names
- All users seeking professional-grade consistency

This release achieves the perfect balance: localized user interface with standardized technical entity naming for optimal international collaboration and automation reliability.

**Full Changelog**: https://github.com/grotan1/denon-avr-3805/compare/v1.8.8...v1.8.9