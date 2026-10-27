"""Inspect original local checkpoints on CPU; never construct an env or start training."""
from pathlib import Path
import hashlib, json, sys, time, traceback

HERE = Path(__file__).resolve().parent
W = HERE.parents[2]
SOURCE = W / "MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015/payload/source"
EXPECTED = {
    "E0": ("E0_frozen_source.pt", "b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8"),
    "W35": ("E1_WAVE35_frozen_source.pt", "b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd"),
}

def describe(value, torch, depth=0):
    if torch.is_tensor(value):
        return {"kind": "tensor", "shape": list(value.shape), "dtype": str(value.dtype),
                "device": str(value.device), "finite": bool(torch.isfinite(value).all()) if value.is_floating_point() else True}
    if isinstance(value, dict):
        if depth >= 2:
            return {"kind": "dict", "keys": [str(k) for k in value], "count": len(value)}
        return {str(k): describe(v, torch, depth + 1) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return {"kind": type(value).__name__, "count": len(value), "entries": [describe(v, torch, depth + 1) for v in value[:4]]}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return {"kind": type(value).__name__}

def main():
    report = HERE / "reports/E0_W35_ORIGINAL_CHECKPOINT_CPU_METADATA_V1.json"
    assert not report.exists(), "new exact CPU inspection is once-only"
    report.parent.mkdir(parents=True, exist_ok=True)
    import torch
    torch.set_num_threads(2)
    rows = {}
    for role, (filename, expected) in EXPECTED.items():
        path = SOURCE / filename
        sha = hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
        assert sha == expected, (role, sha)
        checkpoint = torch.load(path, map_location="cpu", weights_only=False)
        rows[role] = {"path": str(path), "bytes": path.stat().st_size, "sha256": sha,
                      "metadata": describe(checkpoint, torch)}
        if isinstance(checkpoint, dict):
            for key, value in checkpoint.items():
                if isinstance(value, dict) and "state" in value and "param_groups" in value:
                    steps = [float(v["step"]) for v in value["state"].values() if isinstance(v, dict) and "step" in v]
                    rows[role]["optimizer_summary"] = {"key": key, "states": len(value["state"]),
                        "steps_min": min(steps) if steps else None, "steps_max": max(steps) if steps else None,
                        "param_groups": value["param_groups"]}
    data = {"attempt_id": "E0_W35_SOURCE_CPU_METADATA_20261027_V1", "epoch": time.time(),
            "executable": sys.executable, "torch_version": torch.__version__, "map_location": "cpu",
            "sources": rows, "no_cuda_or_env_or_training_or_remote_or_budget": True,
            "original_frozen_labels_unchanged": True, "new_adaptation_qualification": False,
            "Git_status": "pending_root_ordinary_supplement"}
    report.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")
    print(json.dumps({"report": str(report), "roles": list(rows), "cpu_only": True}))

if __name__ == "__main__":
    try:
        main()
    except Exception:
        error = HERE / ("reports/CPU_METADATA_ORIGINAL_ERROR_" + str(time.time_ns()) + ".json")
        error.parent.mkdir(parents=True, exist_ok=True)
        error.write_text(json.dumps({"epoch": time.time(), "traceback": traceback.format_exc(), "no_GPU": True}, indent=2), encoding="utf8")
        raise
