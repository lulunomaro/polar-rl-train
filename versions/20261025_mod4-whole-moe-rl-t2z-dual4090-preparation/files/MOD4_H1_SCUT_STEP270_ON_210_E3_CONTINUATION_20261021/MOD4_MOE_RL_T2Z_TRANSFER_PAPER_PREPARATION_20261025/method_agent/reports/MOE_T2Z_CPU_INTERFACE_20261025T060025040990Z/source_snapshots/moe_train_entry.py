"""Whole-MoE preparation entry: data checks by default; training disabled."""
from __future__ import annotations
import argparse
import importlib
import json
import os
from pathlib import Path
import sys
from moe_data import DataError, SafeMoEIndex, need


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--splits", type=Path, required=True)
    parser.add_argument("--mode", choices=("command_route", "applied_diagnostic"), default="command_route")
    parser.add_argument("--check-data", action="store_true", default=True)
    parser.add_argument("--synthetic-contract-test", action="store_true", help="schema/stub tests only, never makes data trainable")
    parser.add_argument("--cpu-import-upstream", type=Path, help="future installed fixed repo: import and bind without invoking main or weights")
    parser.add_argument("--train", action="store_true", help="always rejected in this preparation artifact")
    args = parser.parse_args(argv)
    if args.train:
        raise DataError("TRAINING_DISABLED_IN_PREPARATION", "existing H1 completes first; this entry only checks/binds source")
    raw = json.loads(args.manifest.read_text(encoding="utf-8"))
    splits = json.loads(args.splits.read_text(encoding="utf-8"))
    index = SafeMoEIndex(raw, splits, require_real=not args.synthetic_contract_test)
    summary = {"status": "CHECKED_NOT_TRAINING_READY", "synthetic": raw["synthetic"],
               "backend": raw["backend"], "mode": args.mode,
               "partition_counts": {f"{split}/{role}": len(index.rows(split, role))
                                    for split, role in (("train", "fit"), ("validation", "support"),
                                                        ("validation", "query"), ("test", "support"), ("test", "query"))},
               "training_enabled": False, "actual_upstream_imported": False}
    if args.cpu_import_upstream:
        # No model constructor/main invocation; source hash verification first.
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
        from upstream_bridge import verify_fixed_sources, bind_ours
        verify_fixed_sources(args.cpu_import_upstream)
        sys.path.insert(0, str(args.cpu_import_upstream.resolve()))
        runner = importlib.import_module("t2z.training.ours")
        scripts_train = importlib.import_module("scripts.train")
        pipeline = importlib.import_module("wan_video_action.pipelines.wan_video_action")
        channels = 9 if args.mode == "command_route" else 16
        bind_ours(runner, scripts_train, pipeline, index=index, mode=args.mode,
                  decoder=None, train_stats={"mean": [0] * channels, "scale": [1] * channels})
        import torch
        need(not torch.cuda.is_initialized(), "CUDA_INITIALIZED_DURING_IMPORT", "CPU import boundary violated")
        summary.update(actual_upstream_imported=True, binding_installed=True,
                       main_invoked=False, weights_loaded=False, placeholder_stats_not_for_training=True)
    print(json.dumps(summary, sort_keys=True))
    return summary


if __name__ == "__main__":
    main()
