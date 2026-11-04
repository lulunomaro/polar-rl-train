"""Content-address the NEW phase1 package; no old source writes or native calls.
Initial shell here-string was blocked before execution by analysis.dynamic-shell-source.
Use this explicit literal script entry. Creation is append-only; existing seal is read-only verified.
"""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
NAMES = ("README.md", "SOURCE_RECEIPT.json", "SYNTHETIC_TEST_LOG.txt", "build_schema.py",
         "partition_schema_v1.json", "phase1_contract.py", "source_manifest.json",
         "test_phase1_contract.py", "seal_source.py")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    target = HERE / "SOURCE_SEAL.json"
    if not target.exists():
        files = {name:{"sha256":sha(HERE/name),"bytes":(HERE/name).stat().st_size} for name in sorted(NAMES)}
        root = hashlib.sha256("".join(name+"\0"+value["sha256"]+"\n" for name,value in files.items()).encode()).hexdigest()
        seal = {"seal_version":1,"kind":"SOURCE_CONTENT_ADDRESS_FREEZE_NOT_ACTUAL_SDK",
                "files":files,"content_root_sha256":root,"actual_sdk_pass":False,"gate1_admitted":False,"exact":False,
                "scope":"Only NEW phase1 artifacts; source originals unchanged. Corrections need new lineage, not rewriting this seal."}
        with target.open("x",encoding="utf-8",newline="\n") as handle:
            handle.write(json.dumps(seal,indent=2,ensure_ascii=False)+"\n")
    seal = json.loads(target.read_text(encoding="utf-8"))
    if set(seal["files"]) != set(NAMES):
        raise ValueError("Seal filename set differs")
    for name,value in seal["files"].items():
        if sha(HERE/name) != value["sha256"] or (HERE/name).stat().st_size != value["bytes"]:
            raise ValueError("Frozen source artifact changed: " + name)
    root = hashlib.sha256("".join(name+"\0"+seal["files"][name]["sha256"]+"\n" for name in sorted(NAMES)).encode()).hexdigest()
    if root != seal["content_root_sha256"]:
        raise ValueError("Seal content root differs")
    print(json.dumps({"sealed_files":len(NAMES),"content_root_sha256":root,"seal_sha256":sha(target),
                      "seal_verify":True,"actual_sdk_pass":False,"exact":False}))

if __name__ == "__main__":
    main()
