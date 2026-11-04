"""Off-loop SOURCE pin builder/verifier. Reads fixed original paths; never imports them.
This is not used by tick callbacks and does not verify live class/function binding.
"""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OLD=ROOT/"source_phase1_state_context_partition_v1"
OLD_SEAL_SHA256="e7f3d29bc0319fbd9f0d4e1d5a4981edd551b6c47f16431c8545bb86b7756630"
ROLES=("E3","W35","CURB_INDEPENDENT113","CURB_PROTECTED878","SLOPE135","SLOPE_INDEPENDENT50","E0","E2")
MODULES=("action_delay_physics_queue.py","action_delay_sdk_adapter.py","action_delay_training_env.py",
         "mild_dr.py","autonomy_policy.py","mod4_task.py","explicit_pd_component.py","explicit_pd_sdk_adapter.py",
         "chassis_com_component.py","chassis_com_pose_roundtrip_sdk_adapter.py","chassis_pd_training_env.py",
         "spring_pressure_training_env.py","spring_pressure_component.py","spring_pressure_audit_runtime.py",
         "gas_damping_training_env.py","gas_damping_factor.py","gas_damping_sdk_adapter.py")


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_old_seal():
    if sha(OLD/"SOURCE_SEAL.json")!=OLD_SEAL_SHA256:raise ValueError("Old sealed lineage changed")
    seal=json.loads((OLD/"SOURCE_SEAL.json").read_text(encoding="utf-8"))
    for name,meta in seal["files"].items():
        if sha(OLD/name)!=meta["sha256"]:raise ValueError("Old member changed: "+name)
    return {"old_seal_sha256":OLD_SEAL_SHA256,"old_members":len(seal["files"]),"all_unchanged":True}


def verify_source_pins(root=None, role=None):
    root=Path(root) if root is not None else ROOT
    pins=json.loads((HERE/"SOURCE_PINS.json").read_text(encoding="utf-8"))
    entries=pins["sources"]
    if role is not None:
        if role not in ROLES:raise ValueError("Unknown role")
        entries={p:v for p,v in entries.items() if p.split("/")[2]==role}
    for path,meta in entries.items():
        if sha(root/path)!=meta["sha256"]:raise ValueError("Source pin mismatch: "+path)
    return {"source_count":len(entries),"pin_file_sha256":sha(HERE/"SOURCE_PINS.json"),
            "source_hashes_match":True,"live_binding":"UNKNOWN","actual_sdk_pass":False,"exact":False}


def build():
    baseline=verify_old_seal()
    old_manifest=json.loads((OLD/"source_manifest.json").read_text(encoding="utf-8"))["sources"]
    old_schema=json.loads((OLD/"partition_schema_v1.json").read_text(encoding="utf-8"))
    sources={}
    for role in ROLES:
        paths=[f"discovery/reward_command_audit_v1/{role}/runtime/isaac/mod4/{name}" for name in MODULES]
        paths += [item["path"] for item in old_schema["layouts"][role]["source_binding"]["chain"]]
        for path in paths:
            value={"sha256":sha(ROOT/path),"bytes":(ROOT/path).stat().st_size}
            if path in old_manifest and value["sha256"]!=old_manifest[path]["sha256"]:
                raise ValueError("Source differs from prior sealed evidence: "+path)
            sources[path]=value
    pins={"version":1,"status":"SOURCE_PINS_ONLY_NOT_RUNTIME_BINDING","old_seal":baseline,
          "sources":dict(sorted(sources.items())),"per_tick_IO":False,"native_execution":False,"actual_sdk_pass":False,"exact":False}
    target=HERE/"SOURCE_PINS.json"
    text=json.dumps(pins,ensure_ascii=False,indent=2)+"\n"
    if target.exists():
        if target.read_text(encoding="utf-8")!=text:raise ValueError("Frozen SOURCE_PINS differs")
    else:target.write_text(text,encoding="utf-8")
    return verify_source_pins()

if __name__=="__main__":print(json.dumps(build()))
