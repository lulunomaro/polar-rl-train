"""Fixed SOURCE pin/old-seal checks, off-loop stdlib only; never imports originals."""
from pathlib import Path
import ast
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCES = {
 "discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/action_delay_physics_queue.py": "a4238c581611ef7cdb710692291ddac48e076364b0587f631eb71fd6a7d15eb8",
 "discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/action_delay_sdk_adapter.py": "ecd1db05a0dfe215cdf089ccf346aea1a5c51d7974a2bcd6e486dff66b7f5494",
 "source_phase1_actuation_capture_v1/actuation_tap.py": "b9b9e288124a1ba8c031a030c00a231f4d02d2ba7efee9981141ae90b8e28828",
}
OLD_SEALS = {
 "source_phase1_state_context_partition_v1/SOURCE_SEAL.json": "e7f3d29bc0319fbd9f0d4e1d5a4981edd551b6c47f16431c8545bb86b7756630",
 "source_phase1_actuation_capture_v1/SOURCE_SEAL.json": "ed77f3a3b0ce7aea6f904a09be8d038097bfb00729d57bec94feae5ab67bd081",
}
API = {
 "__init__": ["self", "n", "device", "seed", "enabled", "physics_us", "control_us"],
 "reset": ["self", "key", "ids", "neutral", "new_scene_clock"],
 "submit": ["self", "key", "x", "tick"], "apply": ["self", "key", "tick"],
 "receipt": ["self", "key", "tick"], "state_dict": ["self"],
}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(root=ROOT):
    root = Path(root)
    checked = {}
    for rel, expected in SOURCES.items():
        if sha(root / rel) != expected: raise ValueError("Source pin changed: " + rel)
        checked[rel] = expected
    original = root / next(iter(SOURCES))
    tree = ast.parse(original.read_bytes(), filename=str(original))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PhysicsActionQueue")
    methods = {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}
    for name, args in API.items():
        if [a.arg for a in methods[name].args.args] != args: raise ValueError("Original API differs: " + name)
    # submit returns None by fallthrough; apply returns its own cloned tensor.
    if any(isinstance(n, ast.Return) and n.value is not None for n in ast.walk(methods["submit"])):
        raise ValueError("Original submit return contract differs")
    ret = next(n for n in ast.walk(methods["apply"]) if isinstance(n, ast.Return))
    if ast.unparse(ret.value) != "g['applied'].clone()": raise ValueError("Original apply clone return differs")
    old = {}
    for rel, expected in OLD_SEALS.items():
        path = root / rel
        if sha(path) != expected: raise ValueError("Old seal changed: " + rel)
        body = json.loads(path.read_text(encoding="utf-8"))
        for name, item in body["files"].items():
            target = path.parent / name
            if sha(target) != item["sha256"] or target.stat().st_size != item["bytes"]:
                raise ValueError("Old member changed: " + str(target))
        old[rel] = {"sha256": expected, "members": len(body["files"]), "unchanged": True}
    return {"sources": checked, "original_api": API, "old_seals": old, "old_members_unchanged": 17,
            "original_submit_return": "None", "original_apply_return": "g['applied'].clone()",
            "real_torch_cpu_executed": False, "actual_sdk_pass": False, "exact": False}


def build():
    value = verify()
    text = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    target = HERE / "SOURCE_PINS.json"
    if target.exists():
        if target.read_text(encoding="utf-8") != text: raise ValueError("New pin manifest frozen/differs")
    else:
        with target.open("x", encoding="utf-8", newline="\n") as f: f.write(text)
    print(json.dumps({"source_count": len(SOURCES), "old_members_unchanged": 17,
                      "pin_sha256": sha(target), "real_torch_cpu_executed": False}))

if __name__ == "__main__":
    if sys.argv[1:] == ["--build"]: build()
    elif not sys.argv[1:]: print(json.dumps(verify(), ensure_ascii=False))
    else: raise SystemExit("Use --build once, or no args for readonly verification")
