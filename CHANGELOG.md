# Changelog

## [0.3.0] — 2026-07-02

### Added
- `HATCH` entities in `sheet.entities` now include `patternLines` — exact hatch
  pattern geometry (line families: `angle`, `base`, `offset`, `dashes`, in drawing
  units with rotation/scale applied). `patternAngle` / `patternScale` are now also
  reliably populated.
- `DrawingMetadata.linetype_patterns` (LTYPE table: name -> dash/gap array) and
  `DrawingMetadata.ltscale` ($LTSCALE) mapped from the result metadata.

### Fixed (API behaviour, no client change required)
- Mirrored-OCS entities (DXF extrusion normal 0,0,-1) are returned at correct WCS
  coordinates; nested blocks under mirrored inserts expand with correct rotation.
- 2D entities with small Z artifacts are projected instead of dropped — entity
  counts may increase slightly for affected drawings.

## [0.2.1] — 2026-06-26

### Fixed
- `get_job_result()` / `GET /v1/jobs/:id/result`: response is now returned promptly for
  drawings with large entity counts (PDFs, complex DXF files). Previously the endpoint
  timed out for sheets with thousands of entities, leaving `image_urls` inaccessible.
- PDF files now correctly populate `image_urls` with one presigned URL per page. Previously
  only a single entry was returned (or the request timed out entirely).

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
