"""Build the local manual MoE from complete checkpoints, without changing training.

The trained S4 gate remains exactly its original E0/W35 pair. Public operator
requests dispatch H1 jump, E3 recovery, or E2 spin as whole six-action vectors.
The spin selector occupies mode6 in this *player* interface and is converted to
normal mode before E2 inference. This is not a newly trained five-way gate.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import traceback
import time
import numpy as np
import onnx
import onnxruntime as ort
import torch
from torch import nn
from torch.nn import functional as F

ROOT = Path(__file__).resolve().parent
WORK = ROOT.parent
STAGE = WORK / "MOD4_LOCAL_LATEST_MOE_WASD_20261018"
LATEST = WORK / "MOD4_THREE_GPU_HOUR3_CONTINUATION_20261018/actual_closed_three_finals"
PAIR = WORK / "MOD4_S4_GATE_FIRST_FINAL_FROZEN35_20261015/payload/source"
SOURCES = {
    "H1": (LATEST / "h1/model_update73.pt", "c3904f1484645877332f43ecb09b99619020993a4c345769b4f35d45dd2c4236"),
    "E2": (LATEST / "e2/model_update240.pt", "b7415bba9d7ca961b973525bb957b4dbea0d606146cf8b743318141131b72470"),
    "E3": (LATEST / "recovery/final_valid_update98.pt", "dc55e041119bc5a6211b6d44fac12657f1c5417df0c5f0e6bb558f76c9b2639f"),
    "E0": (PAIR / "E0_frozen_source.pt", "b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8"),
    "W35": (PAIR / "E1_WAVE35_frozen_source.pt", "b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd"),
    "gate148": (PAIR / "S4_gate_first_final.pt", "02718c74024508c50ff559be2fa6351b7f63046afeb4ee3fd7c51ad6160ae1f3"),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Mean35(nn.Module):
    def __init__(self, state):
        super().__init__()
        self.mlp = nn.Sequential(nn.Linear(35, 256), nn.ELU(),
            nn.Linear(256, 128), nn.ELU(), nn.Linear(128, 64), nn.ELU(), nn.Linear(64, 6))
        keys = {f"mlp.{i}.{s}" for i in (0, 2, 4, 6) for s in ("weight", "bias")}
        assert set(state) == keys | {"distribution.std_param"}
        assert all(t.dtype == torch.float32 and torch.isfinite(t).all() for t in state.values())
        assert state["distribution.std_param"].shape == (6,) and (state["distribution.std_param"] > 0).all()
        self.load_state_dict({k: state[k] for k in keys}, strict=True)

    def forward(self, x):
        return self.mlp(x)


class Gate(nn.Module):
    def __init__(self, state):
        super().__init__()
        assert set(state) == {"w1", "b1", "w2", "b2", "w3", "b3"}
        for k, v in state.items():
            assert v.dtype == torch.float32 and torch.isfinite(v).all()
            self.register_buffer(k, v.clone())

    def forward(self, x):
        return F.linear(F.elu(F.linear(F.elu(F.linear(x, self.w1, self.b1)), self.w2, self.b2)), self.w3, self.b3)


class ManualMoE(nn.Module):
    def __init__(self, checkpoints):
        super().__init__()
        self.experts = nn.ModuleDict({k: Mean35(checkpoints[k]["actor_state_dict"]) for k in ("E0", "W35", "H1", "E2", "E3")})
        gs = checkpoints["gate148"]["actor_state_dict"]
        # Verify that the frozen pair embedded in gate148 is still the same pair.
        keys = ["distribution.std_param"] + [f"mlp.{i}.{s}" for i in (0, 2, 4, 6) for s in ("weight", "bias")]
        for j, k in enumerate(("E0", "W35")):
            assert all(torch.equal(gs[f"experts.{j}.frozen_{i}"], checkpoints[k]["actor_state_dict"][key]) for i, key in enumerate(keys))
        self.gate = Gate({k.removeprefix("gate."): v for k, v in gs.items() if k.startswith("gate.")})

    @staticmethod
    def normal_view(x):
        onehot = torch.cat((torch.ones_like(x[:, :1]), torch.zeros_like(x[:, :6])), dim=1)
        return torch.cat((x[:, :28], onehot), dim=1)

    def choice(self, x):
        base = self.gate(self.normal_view(x)).argmax(1)
        base = torch.where(x[:, 34] > .5, torch.full_like(base, 3), base)
        base = torch.where(x[:, 31] > .5, torch.full_like(base, 4), base)
        return torch.where(x[:, 32] > .5, torch.full_like(base, 2), base)

    def forward(self, x):
        normal = self.normal_view(x)
        actions = torch.stack((self.experts["E0"](normal), self.experts["W35"](normal),
            self.experts["H1"](x), self.experts["E2"](normal), self.experts["E3"](x)), dim=1)
        index = self.choice(x).reshape(-1, 1, 1).expand(-1, 1, 6)
        return actions.gather(1, index).squeeze(1).clamp(-6., 6.)


def main():
    torch.set_num_threads(2)
    checkpoints, index = {}, {}
    for role, (path, expected) in SOURCES.items():
        assert sha(path) == expected, role
        checkpoints[role] = torch.load(path, map_location="cpu", weights_only=False)
        index[role] = dict(path=str(path), bytes=path.stat().st_size, sha256=expected,
            iteration=checkpoints[role].get("iter"))
    model = ManualMoE(checkpoints).eval()
    output = ROOT / "policies/imported/mod4_latest_moe_20261018.onnx"
    output.parent.mkdir(parents=True, exist_ok=True)
    assert not output.exists(), "Use a new versioned output instead of overwriting an existing export"
    torch.onnx.export(model, torch.zeros(1, 35), str(output),
        input_names=["observation"], output_names=["action"],
        dynamic_axes={"observation": {0: "batch"}, "action": {0: "batch"}},
        opset_version=18, dynamo=False)
    graph = onnx.load(str(output))
    # Gather's shape inference leaves the fixed action width symbolic in the
    # legacy exporter. The router always gathers one complete six-vector.
    graph.graph.output[0].type.tensor_type.shape.dim[1].dim_value = 6
    onnx.checker.check_model(graph)
    onnx.save(graph, str(output))
    rng = np.random.default_rng(20261018)
    x = rng.normal(0, .1, (350, 35)).astype(np.float32)
    x[:, 3] = 1.7
    x[:, 7:10] = [0, 0, -1]
    x[:, 28:35] = np.eye(7, dtype=np.float32)[np.arange(len(x)) % 7]
    tx = torch.from_numpy(x)
    with torch.no_grad():
        expected = model(tx).numpy()
        choices = model.choice(tx).numpy()
        # Independent whole-action routing check, including every public selector.
        for i, mode in enumerate(np.arange(len(x)) % 7):
            role = "H1" if mode == 4 else "E3" if mode == 3 else "E2" if mode == 6 else ("E0", "W35")[choices[i]]
            view = tx[i:i+1] if role in ("H1", "E3") else model.normal_view(tx[i:i+1])
            assert torch.equal(model(tx[i:i+1]), model.experts[role](view).clamp(-6, 6))
    session = ort.InferenceSession(str(output), providers=["CPUExecutionProvider"])
    actual = session.run(None, {"observation": x})[0]
    error = float(np.max(np.abs(actual - expected)))
    assert actual.shape == (350, 6) and np.isfinite(actual).all() and error <= 1e-4, error
    meta = dict(schema_version=1, role="latest_manual_moe", manual_moe=True,
        input={"name": "observation", "shape": ["batch", 35], "dtype": "float32"},
        output={"name": "action", "shape": ["batch", 6], "clamp": [-6, 6]},
        onnx_sha256=sha(output), source_checkpoint="Latest closed third-hour H1/E2/E3 + protected gate148 E0/W35",
        sources=index, observation_semantics="mod4_plain_frame35_v1",
        routing={"normal": "original trained gate148 argmax E0/W35; shared normal35, no hysteresis",
                 "jump_mode4": "latest H1", "recover_mode3": "latest E3",
                 "spin_mode6_player_alias": "latest E2, mode rewritten to normal before inference"},
        whole_six_action_selection=True, weight_or_action_averaging=False,
        not_a_newly_trained_five_way_gate=True, deterministic_mean=True,
        parity_max_abs_error=error, parity_bound=1e-4, parity_rows=len(x),
        latest_complete_final_at_collection="2026-10-18 third three-GPU hour; fourth hour still training",
        mujoco_transfer_skill_not_qualified=True, production_training_changed=False,
        yaw_assist_default=0, terrain_truth_auto_default=False)
    output.with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    report = dict(status="PASS", onnx_path=str(output), bytes=output.stat().st_size, **meta)
    (STAGE / "reports/LOCAL_LATEST_MOE_EXPORT_ACTUAL.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(output), "parity_max_abs_error": error}))


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        (STAGE / f"reports/LOCAL_MOE_EXPORT_ORIGINAL_ERROR_{time.time_ns()}.txt").write_text(traceback.format_exc(), encoding="utf-8")
        raise
