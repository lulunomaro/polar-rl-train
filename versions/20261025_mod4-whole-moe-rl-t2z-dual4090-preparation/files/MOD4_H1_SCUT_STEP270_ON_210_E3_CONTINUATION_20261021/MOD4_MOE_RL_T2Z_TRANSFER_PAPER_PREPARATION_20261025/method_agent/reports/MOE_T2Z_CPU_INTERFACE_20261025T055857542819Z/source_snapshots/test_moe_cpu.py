"""Whole-MoE synthetic CPU tests; includes real fixed-source AST call bodies."""
from __future__ import annotations
import ast
import copy
from datetime import timedelta
import json
from pathlib import Path
import types
import unittest
import torch
from torch import nn
from moe_data import (SCHEMA, EXPERTS, EXPERT_PERIOD_NS, BACKENDS, DataError,
                      SafeMoEIndex, MoETrainingDataset, validate)
from moe_action_adapter import MoETemporalActionEncoder, install_moe_action_encoder
from upstream_bridge import bind_ours, split_pretrained_state

BASE = Path(__file__).resolve().parent
WORKSPACE = BASE.parents[2]
OLD_SOURCES = BASE.parents[1] / "MOD4_T2Z_H1_TRANSFER_PAPER_PREPARATION_20261025/method_agent/integration_v1/upstream_source_receipts"


def fixture(backend="PhysX", count=5):
    dt = BACKENDS[backend]
    m = 50_000_000 // dt
    length = m * (count - 1)
    eps = []
    for name, group in (("train", "opaque-A"), ("support", "opaque-B"), ("query", "opaque-B")):
        frames = [{"tick": t, "time_ns": t * dt, "origin": "SYNTHETIC_ONLY",
                   "uri": f"synthetic://{name}/{t}", "sha256": "0" * 64} for t in range(0, length + 1, m)]
        steps = [{"tick": t, "target6": [t / 100 + i for i in range(6)], "expert": EXPERTS[(t // m) % 5],
                  "gate_weights5": [float(i == (t // m) % 5) for i in range(5)]} for t in range(length)]
        events = [{"tick": t, "selected_expert": EXPERTS[(t // m) % 5], "command4": [0.2, 0, 0, .25],
                   "inference_ticks": {e: t - t % (EXPERT_PERIOD_NS[e] // dt) for e in EXPERTS}}
                  for t in range(0, length, 10_000_000 // dt)]
        proposal = {"committed_at_tick": 0, "semantics": "PRECOMMITTED_COMMAND_ROUTE",
                    "steps": [{"tick": t, "command4": [.2, 0, 0, .25], "route": EXPERTS[(t // m) % 5]} for t in range(length)]}
        eps.append({"episode_id": name, "source_episode_uuid": "SYNTHETIC-" + name,
                    "physical_config_id": group, "collector_sha256": "1" * 64,
                    "task_tags": list(EXPERTS) + ["SWITCH_MIX"], "frames": frames,
                    "applied_steps": steps, "policy_events": events, "proposal": proposal,
                    "reset_ticks": [], "evaluation_only": {"physical_values": {"mass": 999}, "contact": "SECRET-TRUTH"}})
    raw = {"schema": SCHEMA, "synthetic": True,
           "backend": {"name": backend, "physics_dt_ns": dt, "video_period_ns": 50_000_000,
                       "dispatch_period_ns": 10_000_000, "expert_period_ns": EXPERT_PERIOD_NS},
           "expert_pool": {e: {"sha256": str(i) * 64, "origin": "SYNTHETIC_ONLY"} for i, e in enumerate(EXPERTS)},
           "episodes": eps}
    split = {"assignments": [{"episode_id": "train", "split": "train", "role": "fit"},
                             {"episode_id": "support", "split": "test", "role": "support"},
                             {"episode_id": "query", "split": "test", "role": "query"}]}
    return raw, split


def actual_method(file, cls, method):
    source = ast.parse((OLD_SOURCES / file).read_text(encoding="utf-8"))
    node = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == cls)
    fn = next(n for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == method)
    namespace = {"torch": torch}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), file, "exec"), namespace)
    return namespace[method]


class FakeOldEncoder(nn.Module):
    def __init__(self, width):
        super().__init__()
        self.action_mlp1 = nn.Sequential(nn.Linear(14, width))


class FakePipe:
    def __init__(self, width=24):
        self.action_encoder = FakeOldEncoder(width).cpu()
        self.device, self.torch_dtype = torch.device("cpu"), torch.float32
        self.action_injection_mode = "adaln"
        self.physical_context_mode = "both"
        self.background_context_enabled = False
        self.loads = []
    def load_models_to_device(self, names):
        self.loads.append(names)


class Tests(unittest.TestCase):
    def setUp(self):
        torch.set_num_threads(1)
        torch.manual_seed(731)

    def rejects(self, code, fn):
        with self.assertRaises(DataError) as out:
            fn()
        self.assertEqual(out.exception.code, code)

    def test_backend_ticks_and_mixed_expert_clocks(self):
        for backend, ticks in (("PhysX", 20), ("MuJoCo", 100)):
            raw, split = fixture(backend)
            idx = SafeMoEIndex(raw, split, require_real=False)
            self.assertEqual(len(idx.packed("query")[1]), ticks)
            self.assertEqual(raw["backend"]["expert_period_ns"]["E3"], 20_000_000)

    def test_physical_config_and_episode_leaks_refused(self):
        raw, split = fixture()
        raw["episodes"][-1]["physical_config_id"] = "opaque-A"
        self.rejects("PHYSICAL_CONFIG_LEAK", lambda: SafeMoEIndex(raw, split, require_real=False))
        raw, split = fixture()
        raw["episodes"][-1]["source_episode_uuid"] = raw["episodes"][-2]["source_episode_uuid"]
        self.rejects("SOURCE_EPISODE_LEAK", lambda: SafeMoEIndex(raw, split, require_real=False))

    def test_real_missing_and_synthetic_refusal(self):
        raw, split = fixture()
        self.rejects("SYNTHETIC_NOT_TRAINING", lambda: SafeMoEIndex(raw, split))
        raw["synthetic"], raw["episodes"] = False, []
        self.rejects("DATASET_MISSING", lambda: SafeMoEIndex(raw, split))

    def test_query_future_truth_actual_actions_and_gate_cannot_change_plan_input(self):
        raw, split = fixture()
        before = SafeMoEIndex(raw, split, require_real=False).model_view("query", "test", "query", for_planning=True)
        raw["episodes"][-1]["evaluation_only"] = {"physical_values": {"mass": -123}, "success": True}
        for row in raw["episodes"][-1]["applied_steps"]:
            row["target6"] = [999] * 6
            row["expert"] = "E3"
            row["gate_weights5"] = [0, 0, 0, 0, 1]
        for frame in raw["episodes"][-1]["frames"][1:]:
            frame["uri"] = "synthetic://SECRET-FUTURE"
        after = SafeMoEIndex(raw, split, require_real=False).model_view("query", "test", "query", for_planning=True)
        self.assertEqual(before, after)
        self.assertNotIn("SECRET", json.dumps(after))

    def test_applied_future_rejected_for_planning_and_late_proposal_rejected(self):
        raw, split = fixture()
        idx = SafeMoEIndex(raw, split, require_real=False)
        self.rejects("FUTURE_APPLIED_PRIVILEGE", lambda: idx.packed("query", "applied_diagnostic", for_planning=True))
        raw["episodes"][-1]["proposal"]["committed_at_tick"] = 1
        self.rejects("PROPOSAL_MISSING", lambda: SafeMoEIndex(raw, split, require_real=False))

    def test_train_dataset_never_sees_support_query_or_numeric_physics(self):
        raw, split = fixture()
        index = SafeMoEIndex(raw, split, require_real=False)
        dataset = MoETrainingDataset(index, decoder=lambda frame: types.SimpleNamespace(size=(8, 8)))
        self.assertEqual([r["episode_id"] for r in dataset.data], ["train"])
        self.assertNotIn("friction_mu", json.dumps(dataset.data))
        self.assertEqual(set(dataset[0]), {"video", "action", "context_index"})

    def test_actual_upstream_action_unit_accepts_whole_moe_dense_tensor(self):
        process = actual_method("wan_video_action__pipelines__wan_video_action.py.txt", "WanVideoUnit_ActionEmbedder", "process")
        for backend, ticks in (("PhysX", 20), ("MuJoCo", 100)):
            raw, split = fixture(backend, 41)
            index = SafeMoEIndex(raw, split, require_real=False)
            item = MoETrainingDataset(index, decoder=lambda frame: types.SimpleNamespace(size=(8, 8)))[0]
            pipe = FakePipe(24)
            receipt = install_moe_action_encoder(pipe, ticks=ticks, mode="command_route", mean=[0] * 9, scale=[1] * 9)
            self.assertEqual(receipt["conditioning_dim_from_old_encoder"], 24)
            result = process(types.SimpleNamespace(onload_model_names=("action_encoder",)), pipe, action=item["action"], num_frames=41)
            self.assertEqual(tuple(result["action_emb"].shape), (1, 41, 24))
            self.assertEqual(tuple(result["action_mod_emb"].shape), (1, 11, 24))

    def test_old_action_weights_forbidden_and_new_adapter_gradients(self):
        module = MoETemporalActionEncoder(24, physics_ticks_per_frame=20, mode="command_route", mean=[0] * 9, scale=[1] * 9)
        with self.assertRaisesRegex(ValueError, "OLD_MANIPULATION"):
            module.load_state_dict({"action_mlp1.0.weight": torch.zeros(24, 14)})
        keep, skipped = split_pretrained_state({"pipe.action_encoder.action_mlp1.0.weight": torch.zeros(1), "dit.weight": torch.zeros(1)})
        self.assertEqual(set(keep), {"dit.weight"})
        self.assertEqual(len(skipped), 1)
        raw, split = fixture()
        action = torch.tensor([SafeMoEIndex(raw, split, require_real=False).packed("query")], dtype=torch.float32)
        output = module.encode_ti2v2(action)
        sum(x.square().mean() for x in output).backward()
        self.assertTrue(all(p.grad is not None and bool(torch.isfinite(p.grad).all()) for p in module.parameters()))
        self.assertFalse(torch.cuda.is_initialized())

    def test_binding_patches_real_symbol_paths_and_disabled_main(self):
        raw, split = fixture()
        index = SafeMoEIndex(raw, split, require_real=False)
        source_video_geometry = actual_method("scripts__train.py.txt", "WanTrainingModule", "_video_geometry")
        source_parse = actual_method("scripts__train.py.txt", "WanTrainingModule", "parse_extra_inputs")
        source_inputs = actual_method("scripts__train.py.txt", "WanTrainingModule", "get_pipeline_inputs")
        Base = type("SourceWanInputs", (), {"_video_geometry": source_video_geometry,
                                             "parse_extra_inputs": source_parse, "get_pipeline_inputs": source_inputs})
        Grouped = type("SourceGroupedStub", (Base,), {})
        runner = types.SimpleNamespace(main=lambda: "UNINVOKED", GroupedContextStage1Module=Grouped)
        factory_calls = []
        def original_factory(**kw):
            factory_calls.append(kw)
            return FakePipe(24)
        scripts = types.SimpleNamespace(build_wan_video_action_pipeline=original_factory, WanTrainingModule=Base)
        receipt = bind_ours(runner, scripts, types.SimpleNamespace(), index=index, mode="command_route",
                            decoder=lambda frame: types.SimpleNamespace(size=(8, 8)), train_stats={"mean": [0] * 9, "scale": [1] * 9})
        self.assertFalse(receipt["main_called"])
        self.rejects("TRAINING_DISABLED_IN_PREPARATION", runner.main)
        self.rejects("TRAIN_METADATA_HANDLE", lambda: runner._unique_friction_values("test-query.jsonl"))
        self.assertEqual(runner._unique_friction_values("moe://train-fit"), [0.0])
        args = types.SimpleNamespace(dataset_metadata_path="moe://train-fit")
        dataset = runner.build_dataset(args, {})
        model = Grouped()
        model.pipe = scripts.build_wan_video_action_pipeline(ckpt_path=None)
        model.friction_context_table = types.SimpleNamespace(lookup=lambda index, **kw: torch.zeros(1, 1, 32))
        model.background_context_table = None
        model.num_history_frames, model.extra_inputs = 1, []
        model.use_gradient_checkpointing, model.use_gradient_checkpointing_offload = True, False
        model.max_timestep_boundary, model.min_timestep_boundary = 1.0, 0.0
        shared, _, _ = model.get_pipeline_inputs(dataset[0])
        self.assertEqual(tuple(shared["action"].shape), (1, 5, 20, 10))
        self.assertNotIn("context_index", shared)
        self.assertEqual(factory_calls, [{"ckpt_path": None}])


if __name__ == "__main__":
    unittest.main(verbosity=2)
