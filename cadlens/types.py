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


class Sheet:
    def __init__(self, data: dict[str, Any]) -> None:
        self.name: str = data["name"]
        self.key: str = data.get("key", "")
        self.index: int = data["index"]
        self.image_url: str | None = data.get("imageUrl")
        self.entity_count: int = data.get("entityCount", 0)
        self.layer_count: int = data.get("layerCount", 0)
        self.layers: list[Layer] = [Layer(l) for l in data.get("layers", [])]
        self.entities: list[dict[str, Any]] = data.get("entities", [])
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

    def __repr__(self) -> str:
        return f"<DrawingMetadata format={self.format!r} units={self.units!r}>"


class JobResult:
    def __init__(self, data: dict[str, Any]) -> None:
        self.job_id: str = data["jobId"]
        self.status: JobStatus = data["status"]
        self.file: dict[str, str] | None = data.get("file")
        self.summary: dict[str, Any] | None = data.get("summary")
        self.sheets: list[Sheet] = [Sheet(s) for s in data.get("sheets", [])]
        self.metadata: DrawingMetadata = DrawingMetadata(data.get("metadata", {}))
        self.image_url: str | None = data.get("imageUrl")
        self.image_urls: list[str] = data.get("imageUrls", [])
        self.created_at: str = data["createdAt"]

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
