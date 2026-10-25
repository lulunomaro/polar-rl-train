"""Read small fixed-commit primary source; no API/model/data/remotehost calls."""
from __future__ import annotations
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.request

BASE = Path(__file__).resolve().parent
COMMIT = "c72f051f5cffcb1f372a32bc488df273556d39b9"
FILES = ("t2z/train.py", "t2z/training/ours.py", "scripts/train.py", "t2z/data.py",
         "t2z/config.py", "t2z/training_data.py", "wan_video_action/pipelines/wan_video_action.py")
out = BASE / "upstream_source_receipts"
out.mkdir(exist_ok=True)
stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
records = []
for name in FILES:
    url = f"https://raw.githubusercontent.com/T2-z-latent-optimization/T2-z/{COMMIT}/{name}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            body = response.read(2_000_001)
        if len(body) > 2_000_000:
            raise ValueError("source exceeds small-source cap")
        path = out / (name.replace("/", "__") + ".txt")
        if path.exists() and path.read_bytes() != body:
            raise ValueError("immutable fixed source mismatch; do not overwrite")
        if not path.exists():
            path.write_bytes(body)
        records.append({"path": name, "url": url, "bytes": len(body),
                        "sha256": hashlib.sha256(body).hexdigest(), "status": "READ_OK"})
    except Exception as exc:
        records.append({"path": name, "url": url, "status": "READ_ERROR_NO_RETRY",
                        "error_type": type(exc).__name__, "detail": str(exc)})
receipt = {"id": "INTEGRATION_FIXED_SOURCE_READ_" + stamp, "observed_utc": stamp,
           "commit": COMMIT, "records": records, "training": False,
           "archive_status": "PENDING_ROOT_SUPPLEMENTAL_GIT"}
(out / (receipt["id"] + ".json")).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt))
