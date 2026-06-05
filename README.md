# cadlens

[![PyPI version](https://badge.fury.io/py/cadlens.svg)](https://pypi.org/project/cadlens/)

Official Python SDK for [Cadlens](https://cadlens.co) — the [CAD file preview API](https://cadlens.co) that converts DWG, DXF, and DWF files into preview images, structured JSON, layer metadata, and vector entities.

- Website: [cadlens.co](https://cadlens.co)
- API Docs: [cadlens.co/docs](https://cadlens.co/docs)
- Dashboard: [cadlens.co/dashboard](https://cadlens.co/dashboard)

---

## Install

```bash
pip install cadlens
```

Requires Python 3.8+ and [`httpx`](https://www.python-httpx.org/).

---

## Quick Start

```python
from cadlens import CadlensClient

client = CadlensClient(api_key="cadl_your_key_here")

# One-shot: upload + poll + return result
result = client.parse_and_wait("drawing.dwg")

print("Layers:  ", len(result.layers_json))
print("Entities:", len(result.vector_json))
print("Metadata:", result.metadata)
print("Preview: ", result.image_url)
```

---

## Step-by-step Usage

```python
import time
from cadlens import CadlensClient

client = CadlensClient(api_key="cadl_your_key_here")

# 1. Upload
upload = client.parse("drawing.dwg")
job_id = upload["job_id"]
print("Job ID:", job_id)

# 2. Poll
while True:
    job = client.get_job(job_id)
    print("Status:", job.status)
    if job.status == "COMPLETED":
        break
    if job.status == "FAILED":
        raise RuntimeError("Job failed")
    time.sleep(3)

# 3. Result
result = client.get_result(job_id)
print(result.metadata)
print(result.vector_json[:5])
```

---

## Context Manager

```python
with CadlensClient(api_key="cadl_your_key_here") as client:
    result = client.parse_and_wait("drawing.dwg")
```

---

## API Reference

### `CadlensClient(api_key, base_url?)`

| Argument | Type | Description |
|----------|------|-------------|
| `api_key` | `str` | Your `cadl_xxx` API key (required) |
| `base_url` | `str` | Override API base URL (default: `https://api.cadlens.co`) |

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `parse(file, file_name?, webhook_url?, mode?)` | `dict` | Upload a CAD file; get a `job_id` |
| `parse_and_wait(file, ...)` | `JobResult` | Upload, poll, and return result |
| `get_job(job_id)` | `Job` | Get job status and metadata |
| `list_jobs()` | `list[Job]` | List recent jobs (up to 100) |
| `get_result(job_id)` | `JobResult` | Get vectorJson, layersJson, metadata |
| `get_image(job_id)` | `str` | Get presigned PNG preview URL (1h TTL) |
| `delete_job(job_id)` | `None` | Delete job and S3 artifacts |

---

## Supported Formats

DWG · DXF · DWF · DWFx · DGN · PDF

---

## Get an API Key

Sign up at [cadlens.co](https://cadlens.co), go to the dashboard, and create an API key. Keys start with `cadl_`.

---

## Links

- [Cadlens official website](https://cadlens.co)
- [API documentation](https://cadlens.co/docs)
- [Cadlens pricing](https://cadlens.co/pricing)

---

## GitHub Topics

Add these topics to this repo for discovery:
`cad` `dwg` `dxf` `python` `sdk` `pip` `cad-api` `engineering-api` `automation` `aec`

---

## License

MIT
