"""Append-only SOURCE fixture content seal. Existing seal only read-verifies."""
from pathlib import Path
import hashlib
import json
from source_pins import verify

HERE = Path(__file__).resolve().parent
NAMES = ("real_cpu_fixture.py", "source_pins.py", "SOURCE_PINS.json", "test_source_contract.py",
         "README.md", "SOURCE_RECEIPT.json", "SOURCE_TEST_LOG.txt", "seal_source.py")


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    pins = verify()
    target = HERE / "SOURCE_SEAL.json"
    if not target.exists():
        files = {n: {"sha256": sha(HERE/n), "bytes": (HERE/n).stat().st_size} for n in sorted(NAMES)}
        root = hashlib.sha256("".join(n + "\0" + v["sha256"] + "\n" for n, v in files.items()).encode()).hexdigest()
        seal = {"version": 1, "kind": "SOURCE_ORIGINAL_QUEUE_CPU_FIXTURE_FROZEN_REAL_CPU_PENDING",
                "files": files, "content_root_sha256": root, "source_count": len(pins["sources"]),
                "pin_file_sha256": sha(HERE/"SOURCE_PINS.json"), "old_members_unchanged": 17,
                "real_torch_cpu_executed": False, "actual_sdk_pass": False, "gate1_admitted": False,
                "exact": False, "physical_readback": "UNKNOWN", "actor35": "NOT_TESTED"}
        with target.open("x", encoding="utf-8", newline="\n") as f: f.write(json.dumps(seal, ensure_ascii=False, indent=2) + "\n")
    seal = json.loads(target.read_text(encoding="utf-8"))
    if set(seal["files"]) != set(NAMES): raise ValueError("Seal member set differs")
    for name, item in seal["files"].items():
        if sha(HERE/name) != item["sha256"] or (HERE/name).stat().st_size != item["bytes"]:
            raise ValueError("Frozen SOURCE member changed: " + name)
    root = hashlib.sha256("".join(n+"\0"+seal["files"][n]["sha256"]+"\n" for n in sorted(NAMES)).encode()).hexdigest()
    if root != seal["content_root_sha256"]: raise ValueError("Content root differs")
    print(json.dumps({"sealed_members": len(NAMES), "content_root_sha256": root,
                      "seal_sha256": sha(target), "old_members_unchanged": 17,
                      "seal_verify": True, "real_torch_cpu_executed": False, "actual_sdk_pass": False}))

if __name__ == "__main__": main()
