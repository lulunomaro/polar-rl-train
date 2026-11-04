"""Off-loop append-only content seal; existing seal is only read-verified."""
from pathlib import Path
import hashlib
import json
from source_pins import verify_source_pins, verify_old_seal

HERE=Path(__file__).resolve().parent
NAMES=("actuation_tap.py","source_pins.py","SOURCE_PINS.json","test_actuation_tap.py",
       "README.md","SOURCE_RECEIPT.json","FAKE_TEST_LOG.txt","seal_source.py")


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    pins=verify_source_pins();old=verify_old_seal()
    target=HERE/"SOURCE_SEAL.json"
    if not target.exists():
        files={n:{"sha256":sha(HERE/n),"bytes":(HERE/n).stat().st_size} for n in sorted(NAMES)}
        root=hashlib.sha256("".join(n+"\0"+v["sha256"]+"\n" for n,v in files.items()).encode()).hexdigest()
        seal={"version":1,"kind":"SOURCE_FAKE_ACTUATION_PASSIVE_TAP_CONTENT_FREEZE_NOT_ACTUAL_SDK",
              "files":files,"content_root_sha256":root,"source_pins":pins,"old_lineage":old,
              "actual_sdk_pass":False,"gate1_admitted":False,"exact":False,"physical_readback":"UNKNOWN"}
        with target.open("x",encoding="utf-8",newline="\n") as f:f.write(json.dumps(seal,ensure_ascii=False,indent=2)+"\n")
    seal=json.loads(target.read_text(encoding="utf-8"))
    if set(seal["files"])!=set(NAMES):raise ValueError("Seal member set differs")
    for name,value in seal["files"].items():
        if sha(HERE/name)!=value["sha256"] or (HERE/name).stat().st_size!=value["bytes"]:raise ValueError("Frozen artifact changed: "+name)
    root=hashlib.sha256("".join(n+"\0"+seal["files"][n]["sha256"]+"\n" for n in sorted(NAMES)).encode()).hexdigest()
    if root!=seal["content_root_sha256"]:raise ValueError("Content root differs")
    print(json.dumps({"sealed_members":len(NAMES),"content_root_sha256":root,"seal_sha256":sha(target),
                      "source_count":pins["source_count"],"old_nine_members_unchanged":old["all_unchanged"],
                      "seal_verify":True,"actual_sdk_pass":False,"exact":False}))

if __name__=="__main__":main()
