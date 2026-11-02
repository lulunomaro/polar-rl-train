"""SRC_ONLY ZIP metadata and explicitly selected text extraction; never executes archive code."""
from pathlib import Path, PurePosixPath
import argparse, hashlib, io, json, re, stat, sys, traceback, zipfile
from contextlib import contextmanager


@contextmanager
def source_archive(member=None):
    with zipfile.ZipFile(ZIP) as outer:
        if member:
            raw = outer.read(member)
            with zipfile.ZipFile(io.BytesIO(raw)) as inner:
                yield inner, {"member": member, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        else:
            yield outer, None

ROOT = Path(__file__).resolve().parent
ZIP = Path(r"C:\Users\lulu\Downloads\SPR Balanced-infantry (1).zip")
ERRORS = ROOT / "ERRORS.jsonl"
INDEX = ROOT / "SPR_SOURCE_INDEX.json"


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha_file(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["central", "nested_central", "extract"])
    parser.add_argument("--selection", type=Path)
    parser.add_argument("--archive-member")
    args = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    if not ERRORS.exists():
        ERRORS.write_text("", encoding="utf-8")
    if args.mode == "central":
        with zipfile.ZipFile(ZIP) as archive:
            entries = [{"member": i.filename, "uncompressed_bytes": i.file_size,
                        "compressed_bytes": i.compress_size, "crc32": f"{i.CRC:08x}",
                        "compression": i.compress_type, "is_directory": i.is_dir(),
                        "flags": i.flag_bits, "external_attributes": i.external_attr}
                       for i in archive.infolist()]
        original = {"path": str(ZIP), "bytes": ZIP.stat().st_size, "sha256": sha_file(ZIP)}
        dump(ROOT / "zip_central_index.json", {"original_archive": original, "members": entries})
        candidates = [i for i in entries if not i["is_directory"] and
                      re.search(r"(?i)(readme|licen[cs]e|copying|\.ioc$|\.uvprojx?$|\.uvoptx?$|cmakelists|makefile|state.?machine|damiao|(^|[/_])dm([/_\.]|\d)|motor|can\.|imu|ins\.|kalman|lqr|mpc|jump|power|chassis|board|main\.[ch]$|\.(ld|sct)$)", i["member"])]
        dump(ROOT / "central_candidates.json", candidates)
        dump(INDEX, {"schema_version": 1, "audit_mode": "SRC_ONLY", "original_archive": original,
                     "central_index": "zip_central_index.json", "member_count": len(entries),
                     "uncompressed_bytes": sum(i["uncompressed_bytes"] for i in entries),
                     "selected_members": [], "evidence": [], "limitations": [],
                     "skills": {"catalog_inspected": True,
                                "available_categories": ["Office/PDF", "Windows sandbox ACL"],
                                "matched": [], "reason": "No Office/PDF or access-denial action; use filesystem, Python stdlib zipfile and CLI only."}})
        print(json.dumps({"original_archive": original, "members": len(entries),
                          "candidates": len(candidates), "uncompressed_bytes": sum(i["uncompressed_bytes"] for i in entries)}, ensure_ascii=False))
        for i in candidates:
            print(f"{i['uncompressed_bytes']:>9}  {i['member']}")
    elif args.mode == "nested_central":
        if not args.archive_member:
            raise ValueError("nested_central requires --archive-member")
        with source_archive(args.archive_member) as (archive, nested):
            entries = [{"member": i.filename, "uncompressed_bytes": i.file_size,
                        "compressed_bytes": i.compress_size, "crc32": f"{i.CRC:08x}",
                        "compression": i.compress_type, "is_directory": i.is_dir(),
                        "flags": i.flag_bits, "external_attributes": i.external_attr}
                       for i in archive.infolist()]
        label = PurePosixPath(args.archive_member).stem
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        index.setdefault("nested_archives", {})[args.archive_member] = nested
        dump(INDEX, index)
        dump(ROOT / (label + "_central_index.json"), {"nested_archive": nested, "members": entries})
        candidates = [i for i in entries if not i["is_directory"] and re.search(r"(?i)(readme|licen[cs]e|copying|\.ioc$|\.uvprojx?$|\.uvoptx?$|cmakelists|makefile|state.?machine|damiao|(^|[/_])dm([/_\.]|\d)|motor|can\.|imu|ins\.|kalman|lqr|mpc|jump|power|chassis|board|main\.[ch]$|\.(ld|sct)$)", i["member"]) and not re.search(r"(?i)(^|/)(\.git|objects|listings)(/|$)|\.(o|obj|d|crf|hex|bin|axf|htm|html|map)$", i["member"])]
        dump(ROOT / (label + "_candidates.json"), candidates)
        print(json.dumps({"nested_archive": nested, "members": len(entries), "candidate_count": len(candidates)}, ensure_ascii=False))
        for i in candidates:
            print(f"{i['uncompressed_bytes']:>9}  {i['member']}")
    else:
        if args.selection is None:
            raise ValueError("extract requires --selection")
        members = json.loads(args.selection.read_text(encoding="utf-8"))
        if not isinstance(members, list) or not all(isinstance(i, str) for i in members):
            raise ValueError("selection must be a JSON list of exact ZIP member names")
        index = json.loads(INDEX.read_text(encoding="utf-8"))
        existing = {(i.get("container_archive"), i["member"]): i for i in index["selected_members"]}
        allowed_suffixes = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".s", ".ld", ".sct", ".ioc", ".uvproj", ".uvprojx", ".uvopt", ".uvoptx", ".txt", ".md", ".markdown", ".json", ".yml", ".yaml", ".xml", ".cmake", ".mk", ".in"}
        total = sum(i["member_bytes"] for i in existing.values())
        with source_archive(args.archive_member) as (archive, nested):
            for member in members:
                identity = (args.archive_member, member)
                if identity in existing:
                    print("already selected: " + member)
                    continue
                if "\\" in member or "\x00" in member or re.match(r"^[A-Za-z]:", member):
                    raise ValueError("ZIP path rejected: " + repr(member))
                parts = PurePosixPath(member)
                if parts.is_absolute() or any(p in {"..", "."} for p in parts.parts):
                    raise ValueError("ZIP traversal rejected: " + repr(member))
                if re.search(r"(?i)(^|/)(\.git|\.ssh|\.aws|\.env)(/|$)|(^|/)(knn_model|knn_impact_model)\.h$|\.(pem|key|p12|pth|pt|onnx|ckpt|safetensors)$", member):
                    raise ValueError("out-of-scope member rejected: " + repr(member))
                suffix = parts.suffix.lower()
                if suffix not in allowed_suffixes and parts.name.lower() not in {"license", "copying", "makefile", "cmakelists.txt", ".project", ".cproject"}:
                    raise ValueError("non-text extension rejected: " + repr(member))
                info = archive.getinfo(member)
                if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16):
                    raise ValueError("directory/symlink rejected: " + repr(member))
                if info.file_size > 2 * 1024 * 1024 or total + info.file_size > 12 * 1024 * 1024:
                    raise ValueError("selected-source size cap exceeded: " + repr(member))
                prefix = [PurePosixPath(args.archive_member).stem] if args.archive_member else []
                destination = (ROOT / "reference_selected" / Path(*prefix, *parts.parts)).resolve()
                destination.relative_to((ROOT / "reference_selected").resolve())
                raw = archive.read(info)
                if b"\x00" in raw:
                    raise ValueError("binary data rejected: " + repr(member))
                encoding = None
                for candidate in ("utf-8-sig", "gb18030", "cp1252"):
                    try:
                        text = raw.decode(candidate)
                        encoding = candidate
                        break
                    except UnicodeDecodeError:
                        pass
                if encoding is None:
                    raise ValueError("text decoding failed: " + repr(member))
                destination.parent.mkdir(parents=True, exist_ok=True)
                with destination.open("w", encoding="utf-8", newline="") as output:
                    output.write(text)
                total += len(raw)
                record = {"container_archive": args.archive_member, "member": member, "member_bytes": len(raw),
                          "member_sha256": hashlib.sha256(raw).hexdigest(),
                          "crc32": f"{info.CRC:08x}", "source_encoding": encoding,
                          "extracted_path": destination.relative_to(ROOT).as_posix(),
                          "extracted_bytes": destination.stat().st_size,
                          "extracted_sha256": sha_file(destination),
                          "line_count": len(text.splitlines()),
                          "transcoded": raw != destination.read_bytes()}
                index["selected_members"].append(record)
                existing[identity] = record
                dump(INDEX, index)
                print(json.dumps(record, ensure_ascii=False))
        print(f"Selected {len(existing)} members; {total} raw member bytes")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        ROOT.mkdir(parents=True, exist_ok=True)
        detail = {"operation": sys.argv[1:], "exception_type": type(error).__name__,
                  "exception": str(error), "traceback": traceback.format_exc()}
        with ERRORS.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(detail, ensure_ascii=False) + "\n")
        traceback.print_exc()
        sys.exit(1)
