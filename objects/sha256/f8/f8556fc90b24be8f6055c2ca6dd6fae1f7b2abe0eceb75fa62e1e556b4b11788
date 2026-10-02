"""Create the deterministic delivery manifest and ZIP archive."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT.parent / "MOD4_ONNX_MUJOCO_LAUNCHER_20260913.zip"
SKIP_PARTS = {".git", ".runtime", "__pycache__", "imported"}


def keep(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if any(part in SKIP_PARTS for part in rel.parts):
        return False
    if path.suffix in {".pyc", ".zip"} or "quick" in path.name:
        return False
    return path.name != "PACKAGE_MANIFEST.json"


def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def main():
    files = sorted(p for p in ROOT.rglob("*") if p.is_file() and keep(p))
    manifest = {
        "package": ROOT.name,
        "main_policy": "policies/mod4_extended_800.onnx",
        "launcher": "启动器.bat",
        "fallback_launcher": "run_wasd.bat",
        "file_count_excluding_manifest": len(files),
        "files": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
                   "sha256": sha256(p)} for p in files],
    }
    mpath = ROOT / "PACKAGE_MANIFEST.json"
    mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    all_files = files + [mpath]
    if ARCHIVE.exists():
        ARCHIVE.unlink()
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for path in all_files:
            zf.write(path, (Path(ROOT.name) / path.relative_to(ROOT)).as_posix())
    print(json.dumps({"archive": str(ARCHIVE), "bytes": ARCHIVE.stat().st_size,
                      "sha256": sha256(ARCHIVE), "files": len(all_files)}, indent=2))


if __name__ == "__main__":
    main()
