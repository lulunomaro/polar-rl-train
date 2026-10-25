"""Executable in-process bindings for fixed T2-z training symbols.

Does not call main, instantiate Wan, load weights or start training itself.
The CLI deliberately exposes only data checking/CPU import/stub checks.
"""
from __future__ import annotations
import copy
from pathlib import Path
from moe_data import DataError, MoETrainingDataset, need

FIXED_COMMIT = "c72f051f5cffcb1f372a32bc488df273556d39b9"
REQUIRED_HASHES = {
    "t2z/train.py": "22f73b894bfbed6872d1fa77738412bc52c921515119a6344286d1648a521d89",
    "t2z/training/ours.py": "373b4593280012fec85c584847ea9165ff17c360138f982244092f8d39c83cdf",
    "scripts/train.py": "ed27585ca03f77f8c758a0661c03971757f770b51ef28829470eaacb3f94e08b",
    "wan_video_action/pipelines/wan_video_action.py": "9d3ef2a45d72329b44303d2875e907481eb6199ab5b72517d8c6a8b456a9b9a5"}


def verify_fixed_sources(root):
    import hashlib
    root = Path(root)
    for name, expected in REQUIRED_HASHES.items():
        path = root / name
        need(path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == expected,
             "UPSTREAM_SOURCE_MISMATCH", name)
    return FIXED_COMMIT


def split_pretrained_state(state):
    """No old action tensor is loaded, even temporarily into a14D encoder."""
    forbidden = {key: value for key, value in state.items() if "action_encoder." in key}
    allowed = {key: value for key, value in state.items() if key not in forbidden}
    return allowed, sorted(forbidden)


def load_pretrained_without_actions(pipe, state):
    """Future authorized initializer; accepts an already-read dict, never a path."""
    allowed, skipped = split_pretrained_state(state)
    physical = "pipe.physical_context_encoder."
    context = {k[len(physical):]: v for k, v in allowed.items() if k.startswith(physical)}
    dit = {k: v for k, v in allowed.items() if not k.startswith("pipe.physical_context_encoder.")}
    need(not any(k.startswith(("pipe.background_context_encoder.", "pipe.physical_adapter_bank.")) for k in dit),
         "UNREVIEWED_PRETRAINED_BRANCH", "primary MoE transfer disables extra background/adapter branches")
    dit_result = pipe.dit.load_state_dict(dit, strict=False)
    context_result = None
    if context:
        need(getattr(pipe, "physical_context_encoder", None) is not None, "MISSING_CONTEXT_BRANCH", "checkpoint/context architecture mismatch")
        context_result = pipe.physical_context_encoder.load_state_dict(context, strict=False)
    return {"skipped_action_keys": skipped, "dit_missing": list(dit_result.missing_keys),
            "dit_unexpected": list(dit_result.unexpected_keys),
            "context_missing": None if context_result is None else list(context_result.missing_keys),
            "context_unexpected": None if context_result is None else list(context_result.unexpected_keys)}


def binding_registry(index, *, mode, decoder, train_stats, expected_metadata_path="moe://train-fit"):
    """Return real callables installed into imported upstream modules, not a plan."""
    from moe_action_adapter import install_moe_action_encoder
    rows = index.train_metadata()
    need(bool(rows), "TRAIN_DATA_MISSING", "train/fit partition is empty")
    ticks = index.raw["backend"]["video_period_ns"] // index.raw["backend"]["physics_dt_ns"]
    def check_path(path):
        need(str(path) == expected_metadata_path, "TRAIN_METADATA_HANDLE", "only the explicitly bound train/fit metadata handle is accepted")
    def read_rows(_path):
        check_path(_path)
        return copy.deepcopy(rows)
    def values(_path):
        check_path(_path)
        return sorted({float(r["context_index"]) for r in rows})
    def grouped(_path):
        check_path(_path)
        result = {}
        for i, row in enumerate(rows):
            result.setdefault(float(row["context_index"]), {}).setdefault(row["action_id"], []).append(i)
        return result, copy.deepcopy(rows)
    def build_dataset(args, runtime_config):
        check_path(args.dataset_metadata_path)
        need(not getattr(args, "background_context_enabled", False), "BACKGROUND_BRANCH_DISABLED", "no hidden task-specific grouping")
        need(not getattr(args, "canonical_target_eef", False), "ARM_ACTION_PATH_FORBIDDEN", "native MoE loader required")
        return MoETrainingDataset(index, mode=mode, decoder=decoder)
    def install(pipe):
        return install_moe_action_encoder(pipe, ticks=ticks, mode=mode,
                                          mean=train_stats["mean"], scale=train_stats["scale"])
    return {"_read_jsonl": read_rows, "_unique_friction_values": values,
            "_metadata_index": grouped, "build_dataset": build_dataset,
            "install_action_encoder": install}


def bind_ours(runner, scripts_train, pipeline_module, *, index, mode, decoder, train_stats,
              pretrained_reader=None):
    """Patch an isolated imported process; bypasses t2z/train.py metadata rewrite.

    Existing numerical `friction_context_table` is retained as an internal
    table class only. Its lookup values are opaque train context indices.
    Actual friction/mass/physical-config labels never reach model input.
    """
    registry = binding_registry(index, mode=mode, decoder=decoder, train_stats=train_stats)
    for name in ("_read_jsonl", "_unique_friction_values", "_metadata_index", "build_dataset"):
        setattr(runner, name, registry[name])
    original_factory = scripts_train.build_wan_video_action_pipeline
    def factory(*args, **kwargs):
        incoming = dict(kwargs)
        checkpoint = incoming.pop("ckpt_path", None)
        # Original builder must not load old action weights before replacement.
        incoming["ckpt_path"] = None
        pipe = original_factory(*args, **incoming)
        receipt = registry["install_action_encoder"](pipe)
        if checkpoint is not None:
            need(pretrained_reader is not None, "PRETRAINED_READER_REQUIRED", "no fallback to old all-module checkpoint loader")
            receipt["pretrained_load"] = load_pretrained_without_actions(pipe, pretrained_reader(checkpoint))
        pipe._moe_t2z_action_install_receipt = receipt
        return pipe
    scripts_train.build_wan_video_action_pipeline = factory
    def get_pipeline_inputs(self, data):
        import torch
        need("friction_mu" not in data and "physical_values" not in data, "PHYSICAL_LABEL_FORBIDDEN", "opaque context indices only")
        clean = dict(data)
        direct = clean.pop("_direct_physical_context", None)
        if direct is None:
            need("context_index" in clean, "CONTEXT_INDEX_MISSING", "training opaque index required")
            clean["physical_context"] = self.friction_context_table.lookup(clean.pop("context_index"),
                                                                          dtype=self.pipe.torch_dtype, device=self.pipe.device)
        else:
            clean.pop("context_index", None)
            clean["physical_context"] = torch.as_tensor(direct, dtype=self.pipe.torch_dtype, device=self.pipe.device)
        need(getattr(self, "background_context_table", None) is None, "BACKGROUND_BRANCH_DISABLED", "primary pipeline only")
        return scripts_train.WanTrainingModule.get_pipeline_inputs(self, clean)
    runner.GroupedContextStage1Module.get_pipeline_inputs = get_pipeline_inputs
    original_main = runner.main
    def disabled_main(*args, **kwargs):
        raise DataError("TRAINING_DISABLED_IN_PREPARATION", "CPU check/import bindings complete; separate reviewed stage must authorize an actual runner")
    # Keep a named reference for a future reviewed launcher, never invoke here.
    runner._moe_uninvoked_original_main = original_main
    runner.main = disabled_main
    return {"registry": registry, "entry": "t2z.training.ours", "main_called": False,
            "metadata_entry_bypassed": "t2z.train.select_environment_groups",
            "legacy_table_storage_name_only": "friction_context_table",
            "actual_feature_key": "context_index", "training_disabled": True}
