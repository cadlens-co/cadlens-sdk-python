from __future__ import annotations

import time
from pathlib import Path
from typing import IO, Any, Union

import httpx

from .exceptions import AuthError, CadlensError, JobFailedError, JobNotReadyError
from .exceptions import TimeoutError as CadlensTimeoutError
from .types import Job, JobResult

_DEFAULT_BASE_URL = "https://api.cadlens.co"


class CadlensClient:
    """Synchronous client for the Cadlens CAD parsing API.

    See https://cadlens.co/docs for full API documentation.
    """

    def __init__(self, api_key: str, base_url: str = _DEFAULT_BASE_URL) -> None:
        if not api_key:
            raise AuthError("api_key is required")
        self._http = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60.0,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "CadlensClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def _raise_for(self, res: httpx.Response) -> None:
        if res.status_code == 401:
            raise AuthError("Invalid or missing API key", status_code=401)
        if res.status_code == 409:
            raise JobNotReadyError("Job result not yet available", status_code=409)
        if not res.is_success:
            raise CadlensError(f"API error {res.status_code}: {res.text}", status_code=res.status_code)

    def parse(
        self,
        file: Union[str, Path, IO[bytes]],
        file_name: str | None = None,
        webhook_url: str | None = None,
        mode: str = "async",
        notify_email: str | None = None,
    ) -> dict[str, Any]:
        """Upload a CAD file for parsing. Returns job metadata including job_id.

        ``notify_email``: optional address CADLens emails a job link to when the
        parse finishes — only if the uploader is no longer watching (polls with
        ``watch=True`` suppress the email when the result is seen live).
        """
        if isinstance(file, (str, Path)):
            path = Path(file)
            file_name = file_name or path.name
            content = path.read_bytes()
        else:
            content = file.read()
            file_name = file_name or "upload.dwg"

        files = {"file": (file_name, content)}
        data: dict[str, str] = {"mode": mode}
        if webhook_url:
            data["webhookUrl"] = webhook_url
        if notify_email:
            data["notifyEmail"] = notify_email

        res = self._http.post("/v1/parse", files=files, data=data)
        self._raise_for(res)
        return res.json()

    def get_job(self, job_id: str, watch: bool = False) -> Job:
        """Fetch current status and metadata for a job.

        Pass ``watch=True`` from interactive poll loops: it marks the caller as
        a live viewer, so a job's ``notify_email`` is suppressed when the user
        watches it finish. Leave ``False`` for unattended/server-side polling.
        """
        params = {"watch": "1"} if watch else None
        res = self._http.get(f"/v1/jobs/{job_id}", params=params)
        self._raise_for(res)
        return Job(res.json())

    def list_jobs(self) -> list[Job]:
        """List recent parse jobs (up to 100)."""
        res = self._http.get("/v1/jobs")
        self._raise_for(res)
        return [Job(j) for j in res.json().get("jobs", [])]

    def get_result(self, job_id: str) -> JobResult:
        """Get the full parsed result (vectorJson, layersJson, metadata).

        Only available when job status is COMPLETED.
        """
        res = self._http.get(f"/v1/jobs/{job_id}/result")
        self._raise_for(res)
        return JobResult(res.json())

    def get_image(self, job_id: str) -> str:
        """Return a fresh presigned PNG preview URL (1-hour TTL)."""
        res = self._http.get(f"/v1/jobs/{job_id}/image")
        self._raise_for(res)
        return res.json()["imageUrl"]

    def delete_job(self, job_id: str) -> None:
        """Delete a job and its S3 artifacts. Irreversible."""
        res = self._http.delete(f"/v1/jobs/{job_id}")
        self._raise_for(res)

    def parse_and_wait(
        self,
        file: Union[str, Path, IO[bytes]],
        file_name: str | None = None,
        webhook_url: str | None = None,
        poll_interval: float = 3.0,
        timeout: float = 300.0,
    ) -> JobResult:
        """Upload a file and block until the job completes, then return the result."""
        upload = self.parse(file, file_name=file_name, webhook_url=webhook_url)
        job_id: str = upload["job_id"]

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            job = self.get_job(job_id)
            if job.status == "COMPLETED":
                return self.get_result(job_id)
            if job.status == "FAILED":
                raise JobFailedError(f"Job {job_id} failed")
            time.sleep(poll_interval)

        raise CadlensTimeoutError(f"Job {job_id} did not complete within {timeout}s")
