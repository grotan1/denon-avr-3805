# Release Notes - v1.5.0

## 🐛 Bug Fixes

### Fixed Entity Naming Issue

- **Problem**: All entities were showing only "Denon" in the UI instead of descriptive names like "Denon Volume", "Denon Power", etc.
- **Root Cause**: The integration was using both `translation_key` and `name` properties simultaneously, which caused conflicts in Home Assistant's entity naming system when `has_entity_name = True`.
- **Solution**: According to Home Assistant documentation, when using `has_entity_name = True`, entities should use either:
  - `translation_key` for translated names (recommended), OR
  - `name` property for untranslated names

  But **NOT both** at the same time.

### Changes Made

- ✅ Removed explicit `name` properties from all entities that use `translation_key`
- ✅ Kept `translation_key` properties to maintain multilingual support (15 languages)
- ✅ Media player entity correctly returns `name = None` as the main device feature
- ✅ All other entities now properly use their translation keys

### Expected Behavior After Update

With this fix, entities should now display properly as:
- **Denon** (media player - main device)
- **Denon Volume** (volume sensor)
- **Denon Input** (input sensor)
- **Denon Power** (power switch)
- **Denon Mute** (mute switch)
- **Denon Connectivity** (connectivity binary sensor)

### Technical Details

This follows the Home Assistant entity naming pattern where:
- `friendly_name = f"{device.name} {entity.name}"` when entity name is not None
- `friendly_name = f"{device.name}"` when entity name is None (main feature)

## 🔧 Installation

1. Update the integration through HACS to version 1.5.0
2. Restart Home Assistant
3. If entities still show old names, try removing and re-adding the integration to clear the entity registry cache

## 📋 Compatibility

- Home Assistant 2023.1.0+
- All existing configurations remain compatible
- Multilingual support maintained (cs, da, de, en, es, fi, fr, is, it, nb, nl, pl, pt, sv, uk)

## 🙏 Credits

Special thanks for identifying the entity naming issue and helping debug the Home Assistant documentation requirements!