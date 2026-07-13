from __future__ import annotations

from typing import Any, Literal

JobStatus = Literal["PENDING", "PROCESSING", "COMPLETED", "FAILED"]


class Job:
    def __init__(self, data: dict[str, Any]) -> None:
        self.id: str = data["id"]
        self.status: JobStatus = data["status"]
        self.file_name: str = data["fileName"]
        self.file_size: int = data["fileSize"]
        self.webhook_url: str | None = data.get("webhookUrl")
        self.created_at: str = data["createdAt"]
        self.completed_at: str | None = data.get("completedAt")
        self.image_url: str | None = data.get("imageUrl")

    def __repr__(self) -> str:
        return f"<Job id={self.id!r} status={self.status!r}>"


class Layer:
    def __init__(self, data: dict[str, Any]) -> None:
        self.name: str = data["name"]
        self.color: int | str | None = data.get("color")
        self.color_hex: str | None = data.get("colorHex")
        self.line_type: str | None = data.get("lineType")
        self.is_visible: bool = data.get("isVisible", True)
        self.entity_count: int = data.get("entityCount", 0)

    def __repr__(self) -> str:
        return f"<Layer name={self.name!r} entities={self.entity_count}>"


class Entity:
    """Schema v2 entity envelope.

    ``geometry`` holds spatial data only (per-type fields, original precision —
    e.g. LINE: ``start``/``end``; LWPOLYLINE: ``vertices``/``closed``/``filled``).
    ``bbox`` and ``metrics`` are always present with ``None`` values when not
    applicable. ``handle`` is the original CAD handle (or ``None`` — never
    derived from ``id``); ``category`` is one of ``Geometry``, ``Annotation``,
    ``BlockReference``, ``Hatch``, ``Other``.
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self.id: str = data.get("id", "")
        self.handle: str | None = data.get("handle")
        self.type: str = data.get("type", "")
        self.category: str = data.get("category", "Other")
        self.layer: str = data.get("layer", "")
        self.layout: str | None = data.get("layout")
        self.geometry: dict[str, Any] = data.get("geometry", {})
        # TEXT/MTEXT only: {"value", "height", "style"} — None on other types.
        self.text: dict[str, Any] | None = data.get("text")
        # INSERT only: {"blockName"} — None on other types.
        self.reference: dict[str, Any] | None = data.get("reference")
        self.properties: dict[str, Any] = data.get("properties", {})
        self.bbox: dict[str, float | None] = data.get("bbox", {})
        # {"length", "area", "perimeter", "vertexCount"} — values None when N/A.
        self.metrics: dict[str, float | None] = data.get("metrics", {})
        #: Raw entity dict as returned by the API.
        self.raw: dict[str, Any] = data

    def __repr__(self) -> str:
        return f"<Entity type={self.type!r} id={self.id!r} layer={self.layer!r}>"


class ParseInfo:
    """Parse diagnostics. ``duration_ms`` is ``None`` for jobs parsed before Schema v2."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.duration_ms: int | None = data.get("durationMs")
        self.warnings: list[str] = data.get("warnings", [])
        self.errors: list[str] = data.get("errors", [])

    def __repr__(self) -> str:
        return f"<ParseInfo duration_ms={self.duration_ms!r} warnings={len(self.warnings)}>"


class Sheet:
    def __init__(self, data: dict[str, Any]) -> None:
        self.name: str = data["name"]
        self.key: str = data.get("key", "")
        self.index: int = data["index"]
        self.image_url: str | None = data.get("imageUrl")
        self.entity_count: int = data.get("entityCount", 0)
        self.layer_count: int = data.get("layerCount", 0)
        self.layers: list[Layer] = [Layer(l) for l in data.get("layers", [])]
        self.entities: list[Entity] = [Entity(e) for e in data.get("entities", [])]
        self.bounding_box: dict[str, float] = data.get("boundingBox", {})
        self.area: float = data.get("area", 0)
        self.perimeter: float = data.get("perimeter", 0)

    def __repr__(self) -> str:
        return f"<Sheet name={self.name!r} entities={self.entity_count}>"


class DrawingMetadata:
    def __init__(self, data: dict[str, Any]) -> None:
        self.filename: str = data.get("filename", data.get("fileName", ""))
        self.format: str = data.get("format", "")
        self.units: str = data.get("units", "")
        self.bounding_box: dict[str, float] = data.get("boundingBox", {})
        self.layouts: list[str] = data.get("layouts", [])
        self.layout_labels: list[str] = data.get("layoutLabels", [])
        self.layout_keys: list[str] = data.get("layoutKeys", [])
        # LTYPE table: linetype name -> dash/gap array in drawing units (+ dash, - gap)
        self.linetype_patterns: dict[str, list[float]] = data.get("linetypePatterns", {})
        # DXF $LTSCALE global linetype scale factor
        self.ltscale: float = data.get("ltscale", 1.0)
        # Count of 3D-only entity types (3DSOLID/BODY/SURFACE/REGION/MESH) with no extractable geometry
        self.unsupported_3d_count: int | None = data.get("unsupported3DCount")

    def __repr__(self) -> str:
        return f"<DrawingMetadata format={self.format!r} units={self.units!r}>"


class WebhookResult:
    """``result`` block of a ``job.completed`` webhook.

    Sheets carry metadata only (no ``entities``/``layers``) — fetch full
    geometry from ``result_url`` (GET /v1/jobs/:id/result). Payloads over
    256 KB omit ``sheets`` entirely.
    """

    def __init__(self, data: dict[str, Any]) -> None:
        # Semver of the result JSON contract (Schema v2 = "2.0.0").
        self.schema_version: str | None = data.get("schemaVersion")
        self.image_url: str | None = data.get("imageUrl")
        self.image_urls: list[str] = data.get("imageUrls", [])
        self.file: dict[str, str] | None = data.get("file")
        self.summary: dict[str, Any] | None = data.get("summary")
        # Slim sheets: Sheet objects with empty entities/layers lists.
        self.sheets: list[Sheet] = [Sheet(s) for s in data.get("sheets", [])]
        self.metadata: DrawingMetadata = DrawingMetadata(data.get("metadata", {}))
        # URL of the full parse result (entities, layers) on the CADLens API.
        self.result_url: str | None = data.get("resultUrl")

    def __repr__(self) -> str:
        return f"<WebhookResult sheets={len(self.sheets)} result_url={self.result_url!r}>"


class WebhookPayload:
    """Body of a CADLens webhook POST."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.event_id: str = data.get("eventId", "")
        self.sequence: int = data.get("sequence", 0)
        self.event: str = data.get("event", "")
        self.job_id: str = data.get("jobId", "")
        self.status: str = data.get("status", "")
        self.timestamp: str = data.get("timestamp", "")
        self.result: WebhookResult | None = (
            WebhookResult(data["result"]) if data.get("result") else None
        )
        self.error: str | None = data.get("error")

    def __repr__(self) -> str:
        return f"<WebhookPayload event={self.event!r} job_id={self.job_id!r}>"


class JobResult:
    def __init__(self, data: dict[str, Any]) -> None:
        # Semver of the JSON contract (Schema v2 = "2.0.0"); None on pre-v2 responses.
        self.schema_version: str | None = data.get("schemaVersion")
        # CAD parser engine version, independent of application releases.
        self.parser_version: str | None = data.get("parserVersion")
        self.job_id: str = data["jobId"]
        self.status: JobStatus = data["status"]
        self.file: dict[str, str] | None = data.get("file")
        self.summary: dict[str, Any] | None = data.get("summary")
        self.sheets: list[Sheet] = [Sheet(s) for s in data.get("sheets", [])]
        self.metadata: DrawingMetadata = DrawingMetadata(data.get("metadata", {}))
        self.parse_info: ParseInfo | None = (
            ParseInfo(data["parseInfo"]) if data.get("parseInfo") else None
        )
        self.image_url: str | None = data.get("imageUrl")
        self.image_urls: list[str] = data.get("imageUrls", [])
        self.created_at: str = data["createdAt"]

    @property
    def statistics(self) -> dict[str, dict[str, int]]:
        """Entity counts grouped ``byType`` and ``byCategory`` (empty dicts pre-v2)."""
        if self.summary:
            return self.summary.get("statistics", {})
        return {}

    @property
    def total_entities(self) -> int:
        if self.summary:
            return self.summary.get("totalEntities", 0)
        return sum(s.entity_count for s in self.sheets)

    @property
    def total_layers(self) -> int:
        if self.summary:
            return self.summary.get("totalLayers", 0)
        return sum(s.layer_count for s in self.sheets)

    def __repr__(self) -> str:
        return (
            f"<JobResult job_id={self.job_id!r} "
            f"sheets={len(self.sheets)} entities={self.total_entities}>"
        )
