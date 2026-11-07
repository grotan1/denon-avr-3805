# v3.0.6 - Home Assistant Marketplace Support

## What's New

- **Marketplace install instructions**: Home Assistant 2026.11 includes HACS as the built-in Marketplace. The README now has a Marketplace section for 2026.11+ and keeps the HACS section for 2026.10 and older.
- **One-click My Home Assistant badges**: Open the repository in the Marketplace (`marketplace_repository`) or HACS (`hacs_repository`), and start the integration setup directly (`config_flow_start`).
- **Integration category**: `manifest.json` now declares `media_entertainment.speakers_audio`, so the integration shows up under Media & entertainment in the Marketplace.
- **Badge fix**: The README badge now reads "Marketplace | HACS - Default" (the integration is in the default catalog) instead of "HACS - Custom".

## Impact

No functional or behavioral changes to the integration itself. This is a documentation and metadata release.

## Upgrade Notes

Update through the Marketplace (Home Assistant 2026.11+) or HACS (older versions). Existing HACS installs are migrated to the Marketplace automatically when you upgrade Home Assistant to 2026.11. No configuration changes required.
