"""Cloudinary media upload for Phiversity (stdlib only, no SDK).

Videos live on Cloudinary in the cloud deployment so nothing important
depends on the backend's ephemeral disk:

  POST https://api.cloudinary.com/v1_1/<cloud>/video/upload
  signed params: public_id + timestamp (sha1 over sorted k=v pairs)

Conventions
  public_id : phiversity/<slug>/lecture   -> video asset
  thumbnail : .../video/upload/so_<n>/<public_id>.jpg  (poster frame)

The API secret stays in backend env vars (CLOUDINARY_API_SECRET); it is
never sent to a browser and never appears in a URL.
"""

from __future__ import annotations

import hashlib
import os
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path


class MediaError(RuntimeError):
    """Raised when an upload or delete to the media CDN fails."""


def cloudinary_configured() -> bool:
    return all(os.environ.get(name, "").strip()
               for name in ("CLOUDINARY_CLOUD_NAME", "CLOUDINARY_API_KEY",
                            "CLOUDINARY_API_SECRET"))


def signature(params: dict, api_secret: str) -> str:
    """Cloudinary signing: sha1 hex of the alphabetically sorted
    `key=value` pairs joined by '&' plus the api secret."""
    signed = "&".join(f"{key}={params[key]}" for key in sorted(params))
    return hashlib.sha1(f"{signed}{api_secret}".encode("utf-8")).hexdigest()


def video_url(cloud_name: str, public_id: str) -> str:
    return f"https://res.cloudinary.com/{cloud_name}/video/upload/{public_id}.mp4"


def thumbnail_url(cloud_name: str, public_id: str, at: float = 2.0) -> str:
    moment = f"{at:g}"
    return (f"https://res.cloudinary.com/{cloud_name}/video/upload/"
            f"so_{moment}/{public_id}.jpg")


def _multipart(fields: dict, file_field: tuple[str, bytes, str]) -> bytes:
    """Encode a multipart/form-data body."""
    boundary = uuid.uuid4().hex
    parts = []
    for key, value in fields.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                     f"name=\"{key}\"\r\n\r\n{value}\r\n".encode("utf-8"))
    name, data, ctype = file_field
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                 f"name=\"{name}\"; filename=\"upload.bin\"\r\n"
                 f"Content-Type: {ctype}\r\n\r\n".encode("utf-8"))
    parts.append(data + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), boundary


def upload_video(path: str | Path, public_id: str,
                 timeout: float = 300.0) -> dict:
    """Upload an mp4 as a signed Cloudinary video asset.

    Returns {url, thumbnail_url, duration, public_id, bytes}."""
    if not cloudinary_configured():
        raise MediaError("cloudinary is not configured: set "
                         "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and "
                         "CLOUDINARY_API_SECRET")
    cloud = os.environ["CLOUDINARY_CLOUD_NAME"].strip()
    key = os.environ["CLOUDINARY_API_KEY"].strip()
    secret = os.environ["CLOUDINARY_API_SECRET"].strip()
    upload = Path(path)
    if not upload.is_file():
        raise MediaError(f"video file not found: {upload}")

    timestamp = str(int(time.time()))
    signed = {"public_id": public_id, "timestamp": timestamp}
    fields = {"api_key": key, "timestamp": timestamp,
              "public_id": public_id, "signature": signature(signed, secret)}
    data = upload.read_bytes()
    body, boundary = _multipart(
        fields, ("file", data, "video/mp4"))
    url = f"https://api.cloudinary.com/v1_1/{cloud}/video/upload"
    request = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                 "Content-Length": str(len(body))})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json_loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise MediaError(f"cloudinary upload failed ({exc.code}): {detail}") \
            from None
    except (urllib.error.URLError, OSError) as exc:
        raise MediaError(f"cloudinary unreachable: {exc}") from exc
    if result.get("error"):
        raise MediaError(f"cloudinary upload failed: "
                         f"{result['error'].get('message', result['error'])}")
    return {
        "url": result.get("secure_url") or video_url(cloud, public_id),
        "thumbnail_url": thumbnail_url(cloud, public_id),
        "duration": float(result.get("duration") or 0),
        "public_id": result.get("public_id") or public_id,
        "bytes": int(result.get("bytes") or len(data)),
    }


def destroy(public_id: str, timeout: float = 60.0) -> bool:
    """Delete a video asset (used when a lecture is removed)."""
    if not cloudinary_configured():
        raise MediaError("cloudinary is not configured: set "
                         "CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and "
                         "CLOUDINARY_API_SECRET")
    cloud = os.environ["CLOUDINARY_CLOUD_NAME"].strip()
    key = os.environ["CLOUDINARY_API_KEY"].strip()
    secret = os.environ["CLOUDINARY_API_SECRET"].strip()
    timestamp = str(int(time.time()))
    signed = {"public_id": public_id, "timestamp": timestamp}
    fields = {"api_key": key, "timestamp": timestamp,
              "public_id": public_id, "signature": signature(signed, secret)}
    body, boundary = _multipart(fields, ("unused", b"", "text/plain"))
    url = f"https://api.cloudinary.com/v1_1/{cloud}/video/destroy"
    request = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}",
                 "Content-Length": str(len(body))})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json_loads(response.read().decode("utf-8"))
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
        raise MediaError(f"cloudinary destroy failed: {exc}") from exc
    return result.get("result") == "ok"


def json_loads(text: str) -> dict:
    import json
    return json.loads(text or "{}")
