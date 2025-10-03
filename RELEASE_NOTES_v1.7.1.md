# Release Notes - v1.7.1 🐛

## 🚨 **Critical Bug Fix - Home Assistant 2025.12+ Compatibility**

This is a **critical bug fix release** that ensures full compatibility with upcoming Home Assistant 2025.12, which deprecates certain config flow patterns.

## 🔧 **Bug Fixes**

### **Config Flow Deprecation Warning**
- ✅ **Fixed**: Removed deprecated explicit `config_entry` assignment in `OptionsFlow`
- ✅ **Added**: Proper `super().__init__()` call in options flow handler
- ✅ **Simplified**: Options update method title handling
- ✅ **Impact**: Eliminates deprecation warning and ensures future HA compatibility

### **Deprecation Details**
**Warning Fixed:**
```
Detected that custom integration 'denon_avr_3805' sets option flow config_entry explicitly,
which is deprecated at custom_components/denon_avr_3805/config_flow.py, line 84:
self.config_entry = config_entry. This will stop working in Home Assistant 2025.12
```

**Resolution:**
- Removed: `self.config_entry = config_entry` (deprecated pattern)
- Added: `super().__init__()` (modern pattern)
- Updated: Options flow to use proper inheritance

## 🚀 **Upgrade Instructions**

### **Immediate Action Required**
If you see the deprecation warning in your Home Assistant logs, update to v1.7.1 **before** upgrading to Home Assistant 2025.12.

### **HACS Users**
1. Update through HACS to version 1.7.1
2. Restart Home Assistant
3. Deprecation warning will be eliminated

### **Manual Installation**
1. Replace integration files with v1.7.1
2. Restart Home Assistant

## 🎯 **Compatibility**

- ✅ **Home Assistant**: 2023.1.0+ (including 2025.12+)
- ✅ **Backward Compatible**: All existing functionality preserved
- ✅ **Zero Breaking Changes**: No user action required after update
- ✅ **Future Proof**: Compatible with upcoming HA versions

## 📋 **What Changed**

### **Code Changes**
```python
# Before (deprecated):
def __init__(self, config_entry):
    self.config_entry = config_entry
    self.options = dict(config_entry.options)

# After (modern):
def __init__(self, config_entry):
    super().__init__()
    self.options = dict(config_entry.options)
```

### **Impact**
- ❌ **Removes**: Deprecation warning from HA logs
- ✅ **Maintains**: All existing functionality
- ✅ **Ensures**: Future compatibility with HA 2025.12+
- ✅ **No Changes**: To user experience or entity behavior

## 🔄 **Version History Context**

- **v1.7.0**: Major connection robustness enhancements
- **v1.7.1**: Critical config flow deprecation fix ← **Current Release**

This bug fix ensures the major improvements from v1.7.0 remain fully functional with future Home Assistant versions.

## ⚠️ **Important Note**

**This update is recommended for ALL users** to ensure continued compatibility. The fix is minimal and risk-free, addressing only the deprecation warning without affecting any functionality.

---

## 🎯 **Summary**

Version 1.7.1 eliminates the config flow deprecation warning and ensures your Denon AVR-3805 integration will continue working seamlessly when you upgrade to Home Assistant 2025.12 and beyond.

**Result**: Future-proof integration with zero functional changes! 🛡️

---

*Version 1.7.1 is a critical compatibility update - upgrade recommended before HA 2025.12*