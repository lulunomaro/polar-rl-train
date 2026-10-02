"""Fast package integrity, interface and topology smoke test."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import mujoco
import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from sim_runtime import Mod4Sim, POLICY_TERM_DIMS, pack_term_major_history  # noqa: E402
from launcher import validate_model, validate_policy  # noqa: E402
from drive_wasd import CONTROL_KEYS, MUJOCO_DIRECT_RESERVED_KEYS  # noqa: E402


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def main():
    policy = ROOT / "policies" / "mod4_extended_800.onnx"
    if not policy.exists():
        policy = ROOT / "policies" / "mod4_general_16295.onnx"
    meta = json.loads(policy.with_suffix(".json").read_text(encoding="utf-8"))
    assert sha256(policy) == meta["onnx_sha256"]
    policy_contract = validate_policy(policy)
    full_model_contract = validate_model(ROOT / "model" / "rm_training_arena.xml")
    input_width = int(policy_contract["input"]["shape"][-1])
    assert input_width in (35, 175)
    assert policy_contract["output"]["shape"][-1] == 6
    assert full_model_contract["nu"] == 6 and full_model_contract["equalities"] == 10
    drive_keys = {key for values in CONTROL_KEYS.values() for key in values}
    assert not drive_keys.intersection(MUJOCO_DIRECT_RESERVED_KEYS)
    xml = ROOT / "model" / "rm_training_arena_headless.xml"
    sim = Mod4Sim(xml, policy)
    assert (sim.model.nq, sim.model.nv, sim.model.nu, sim.model.neq) == (37, 36, 6, 10)
    assert sim.observation_frame().shape == (35,)
    assert sim.observation().shape == (input_width,)
    frames = [np.arange(35, dtype=np.float32) + 100 * i for i in range(5)]
    packed = pack_term_major_history(frames)
    cursor = frame_cursor = 0
    for width in POLICY_TERM_DIMS:
        for frame in frames:
            assert np.array_equal(packed[cursor:cursor + width], frame[frame_cursor:frame_cursor + width])
            cursor += width
        frame_cursor += width
    sim.command.vx = .4
    for _ in range(300):
        action = sim.step_control()
    health = sim.health()
    assert action.shape == (6,)
    assert np.isfinite(action).all() and health["finite"]
    assert sim.max_closure_error < .002
    assert sim.max_mimic_error < .01
    report = {
        "status": "PASS", "onnx_sha256": sha256(policy),
        "launcher_contract": {"input_dim": input_width, "output_dim": 6,
                              "observation_semantics": policy_contract["observation_semantics"],
                              "full_model_equalities": full_model_contract["equalities"],
                              "viewer_key_conflicts": 0},
        "model": {"nq": sim.model.nq, "nv": sim.model.nv, "nu": sim.model.nu,
                  "bodies": sim.model.nbody, "geoms": sim.model.ngeom,
                  "equalities": sim.model.neq},
        "steps": 300, "max_closure_error_m": sim.max_closure_error,
        "max_mimic_error_rad": sim.max_mimic_error,
    }
    out = ROOT / "reports" / "smoke_report.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
