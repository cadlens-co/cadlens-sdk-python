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
        self.color: int = data["color"]
        self.lineweight: int = data["lineweight"]
        self.is_visible: bool = data["isVisible"]

    def __repr__(self) -> str:
        return f"<Layer name={self.name!r} visible={self.is_visible}>"


class DrawingMetadata:
    def __init__(self, data: dict[str, Any]) -> None:
        self.version: str = data.get("version", "")
        self.units: str = data.get("units", "")
        self.width: float = data.get("width", 0)
        self.height: float = data.get("height", 0)
        self.created_date: str | None = data.get("createdDate")

    def __repr__(self) -> str:
        return f"<DrawingMetadata {self.width}x{self.height} {self.units}>"


class JobResult:
    def __init__(self, data: dict[str, Any]) -> None:
        self.job_id: str = data["jobId"]
        self.status: JobStatus = data["status"]
        self.vector_json: list[dict[str, Any]] = data.get("vectorJson", [])
        self.layers_json: list[Layer] = [Layer(l) for l in data.get("layersJson", [])]
        self.metadata: DrawingMetadata = DrawingMetadata(data.get("metadata", {}))
        self.image_url: str | None = data.get("imageUrl")
        self.created_at: str = data["createdAt"]

    def __repr__(self) -> str:
        return (
            f"<JobResult job_id={self.job_id!r} "
            f"entities={len(self.vector_json)} layers={len(self.layers_json)}>"
        )
