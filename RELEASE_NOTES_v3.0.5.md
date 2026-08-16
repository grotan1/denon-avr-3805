# v3.0.5 - Translation Cleanup

## What's Fixed

- **Removed stale URLs from translation descriptions**: The `config.step.user.description` field in all 26 `translations/*.json` locale files still contained old "have a look here: `<repo URL>`" text left over from before `strings.json` was simplified. Home Assistant's `hassfest` validator disallows raw URLs in translation strings, which was failing CI on every push. Each locale now has a translated, URL-free description matching the current `strings.json` wording.
- **Fixed a corrupted character in the README banner**: A malformed UTF-8 byte sequence (rendering as `�` in HACS) and a missing newline between the title and subtitle have been corrected.
- **GitHub release title**: Confirmed emoji-free to avoid rendering issues (`?`) in the HACS UI.

## Impact

No functional or behavioral changes to the integration itself — this is a documentation/metadata/CI compliance release.

## Upgrade Notes

Standard update via HACS. No configuration changes required.
