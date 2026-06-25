# Changelog

## [0.2.0] — 2026-06-25

### Added
- `Sheet.key`: HTML/CSS-safe unique slug derived from the sheet display label.
  Safe to use as an HTML `id` attribute. Deduplicated with `-2`, `-3` suffix when
  the same label appears on multiple sheets. Accessed as `sheet.key`.
- `DrawingMetadata.layout_labels`: original display labels in image order (may contain
  duplicates across sheets). Parallel to `layouts`.
- `DrawingMetadata.layout_keys`: HTML/CSS-safe slugs in image order. Parallel to `layouts`.

### Fixed
- Per-viewport frozen-layer rendering: named layout sheets now show only layers
  visible in that viewport (previously all layers rendered on every sheet).
- PNG preview now correctly scales entity text height through viewport transforms.

## [0.1.0] — 2026-06-19

Initial release with sheets-based response schema.
