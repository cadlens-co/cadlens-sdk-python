# Changelog

## API service — 2026-07-16 (no SDK changes required)

- Large-file parses are ~3x faster: redundant conversion retries that could
  not change the outcome are skipped and the streaming geometry filter
  fast-forwards over out-of-budget sections. Results are identical (same
  entities, layers, `truncated` flag). Conversion time limits for very
  complex drawings are also higher and configurable server-side. No
  request/response shape changes.

## API service — 2026-07-15 (no SDK changes required)

- `mode=sync` uploads now auto-divert to async when the file is large or its
  converted geometry turns out huge: the API returns `202` immediately with a
  human-readable `message` instead of holding the connection until the sync
  wait times out. Poll `GET /v1/jobs/:jobId` or use webhooks as usual.
- Oversized drawings that previously failed with `FILE_TOO_COMPLEX` are now
  parsed with a bounded streaming pre-filter and return `truncated: true` in
  the result summary. No request/response shape changes.

## API service — 2026-07-14 (no SDK changes required)

- Large-file reliability fix on the API: drawings whose converted geometry
  exceeds processing limits now fail fast with status `FAILED` and a clear
  error message (previously they could remain `PROCESSING` indefinitely after
  a server interruption). Failure emails and `job.failed` webhooks now fire
  for every terminal outcome. No request/response shape changes.

## [0.6.0] — 2026-07-13

### Changed — BREAKING (API Schema v2.0.0)
- `Sheet.entities` is now a list of typed `Entity` objects (was raw dicts).
  Flat coordinate fields (`start`, `end`, `vertices`, `center`, `position`,
  `radius`, angles, scales) moved into `entity.geometry` — read coordinates
  from `entity.geometry["..."]` now (the raw dict remains available as
  `entity.raw`). Each entity also carries `handle` (original CAD handle or
  `None` — never derived from `id`), `category` (`Geometry` / `Annotation` /
  `BlockReference` / `Hatch` / `Other`), `layout`, and always-present
  `properties`, `bbox`, `metrics` (computed helpers, 6-decimal, `None` when
  not applicable), plus `text` (TEXT/MTEXT) and `reference` (INSERT).

### Added
- `JobResult.schema_version` / `JobResult.parser_version` ("2.0.0").
- `JobResult.parse_info` (`ParseInfo`): `duration_ms` (`None` for jobs parsed
  before Schema v2), `warnings`, `errors`.
- `JobResult.statistics` property: entity counts `byType` and `byCategory`.
- `WebhookResult.schema_version` (additive — webhook sheets stay metadata-only).
- `Entity`, `ParseInfo`, `Sheet` exported from the package root.

## [0.5.0] — 2026-07-07

### Added
- `DrawingMetadata.unsupported_3d_count`: optional count of 3D-only entity
  types (3DSOLID/BODY/SURFACE/REGION/MESH) with no extractable geometry.

### Fixed (API behaviour, no type change)
- `metadata.is3D` no longer reports `true` for drawings whose only 3D content
  is unsupported entity types with an empty 3D scene.

## [0.4.0] — 2026-07-06

### Added
- `parse(..., notify_email=...)`: optional email address — CADLens emails a link
  to the job when it finishes, but only if the uploader stopped watching (no
  email when the result was seen live).
- `get_job(job_id, watch=True)`: marks the poll as a live viewer so the
  notify email is suppressed when the user watches the job complete. Use in
  interactive poll loops; leave `False` for unattended polling.
- `WebhookPayload` / `WebhookResult` types for webhook receivers, including the
  new `result_url` field.

### Changed (breaking for webhook consumers)
- `job.completed` webhook payloads no longer include `sheets[].entities` /
  `sheets[].layers` — sheets carry metadata only (name, key, counts, bounding
  box, area, perimeter, image URL). Fetch full geometry from `result_url`
  (`GET /v1/jobs/:id/result`, unchanged) or `get_result()`. Payloads over
  256 KB omit `sheets` entirely. Fixes webhook delivery timeouts on large drawings.

### Notes (API v1.4.1, 2026-07-06)
- API responses are now gzip-compressed via standard content negotiation
  (`Accept-Encoding`). HTTP clients handle this automatically — no SDK code
  change or upgrade required; large results simply download ~12× faster.

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
