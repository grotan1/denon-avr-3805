# Serial Connection Detection Improvements

## Overview

Enhanced the Denon AVR-3805 integration to properly detect when serial connections are broken, even when the TCP connection to ser2net remains active.

## Problem Addressed

Previously, the integration only checked TCP connection status, which could result in false positives where:
- TCP connection to ser2net was active ✅
- Serial connection to AVR was broken ❌
- Integration reported "connected" but no control was possible

## Improvements Made

### 1. Enhanced Connection Statistics

Added new tracking fields to `ConnectionStats`:
- `consecutive_timeouts`: Track command timeouts in a row
- `consecutive_no_response`: Track commands with no response
- `commands_without_response`: Total commands that got no response
- `last_successful_response`: Timestamp of last successful AVR response

### 2. Serial Health Detection

Added new properties and methods:
- `response_rate`: Calculate percentage of commands that get responses
- `serial_seems_broken`: Detect patterns indicating serial issues
- `is_serial_healthy`: Overall serial connection health check
- `test_serial_connection()`: Active test requiring AVR response

### 3. Improved Connection Testing

Enhanced connection validation in config flow:
- Now tests actual serial communication, not just TCP
- Requires a response from the AVR to consider connection valid
- Provides better error messages when serial fails

### 4. Enhanced Binary Sensor

Updated connectivity binary sensor to consider both:
- TCP connection status (existing)
- Serial communication health (new)

Added diagnostic attributes:
- `tcp_connected`: TCP connection status
- `serial_healthy`: Serial communication status
- `response_rate`: Percentage of successful responses
- `consecutive_timeouts`: Current timeout streak
- `consecutive_no_response`: Current no-response streak

### 5. Better Error Detection

The coordinator now:
- Tests serial health before each update cycle
- Provides specific error messages for different failure types
- Distinguishes between "AVR off" vs "serial broken"
- Logs detailed connection statistics for troubleshooting

## Detection Patterns

The system now detects serial connection issues when:

1. **Immediate Detection**: 3+ consecutive timeouts or no responses
2. **Pattern Detection**: Response rate below 30% over multiple commands
3. **Health Monitoring**: Overall connection health considers both TCP and serial

## Benefits

- **Accurate Status**: Binary sensor correctly shows "off" when serial is broken
- **Better Diagnostics**: Detailed attributes help troubleshoot connection issues
- **Proactive Detection**: Issues detected before they cause automation failures
- **Clear Error Messages**: Logs distinguish between different failure types

## Error Messages

New specific error messages help identify issues:
- `"Serial connection appears broken (TCP connected but no AVR responses)"`
- `"AVR not responding - may be powered off or serial connection issue"`
- `"Command timeout: X (serial connection may be broken)"`

## Diagnostic Information

Enhanced diagnostics now include:
- Serial connection health status
- Response rate percentages
- Timeout and no-response counters
- Last successful response timestamp

This provides comprehensive visibility into both TCP and serial connection health for better troubleshooting.