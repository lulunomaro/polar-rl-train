# Whole-MoE + mixed RL T2-z transfer preparation

Status: **SOURCE / DATA CONTRACT / CPU STUB PREPARATION ONLY**. The target is the entire existing E0/W35/H1/E2/E3 + gate stack. H1 is one task, not the scope of the transfer. The earlier H1-only package is retained unchanged as history; this package supersedes its scope, not its recorded outcomes.

Main research backend is a future isolated **PhysX2.5ms** collection/modeling stage, with100Hz E0/W35/H1 and50Hz E2/E3 policy clocks. This does not change the running experts or authorize collection/training. The existing MuJoCo player uses0.5ms and is a separate evaluation domain:20fps means100physics ticks/frame there, versus20ticks/frame in PhysX. Its old GUI trajectories are not certified training/contact truth.

The current player manifest contains E0/W35/gate148, H1/E3pair47 and E2cohort52. It explicitly says `new_five_way_learned_gate=false`, `whole_six_action_selection=true`, `weight_or_action_averaging=false`, `skill_qualification=false`. Latest source67 H1/E3 training references are different provenance and are not silently substituted into the player pool. `source_facts.json` records actual small-file hashes and negative routing evidence.

Code:

- `moe_data.py`: backend-aware applied action, actual routing/inference-clock and causal command/route-plan schema; held-out physical-group/source-episode split; train-only loader; native local RGB SHA decoder.
- `moe_action_adapter.py`: newly initialized command/route or applied-diagnostic temporal encoder, retaining actual Wan adaln context/modulation shapes; D comes from the old encoder, not a hard-coded model width.
- `upstream_bridge.py`: executable in-process bindings for fixed upstream `ours.build_dataset`, metadata indexing, context lookup and `scripts.train` pipeline factory. It bypasses `t2z/train.py` task-specific metadata rewriting. No actual friction values are used as context indices. Original14D action weights are never loaded into the new layer, even temporarily.
- `moe_train_entry.py`: defaults to `--check-data`; rejects `--train`; optional CPU-only import/bind against an installed fixed-hash upstream checkout without calling its main or constructing/loading Wan.
- `test_moe_cpu.py`, `run_preparation_cpu.py`: synthetic CPU tests, including exact fixed upstream `ours.main` AST call body with all constructors/launches stubbed, actual Wan action-unit process body and original training input-method bodies.

Run tests using an existing torch Python:

```powershell
$env:CUDA_VISIBLE_DEVICES = ''
& 'C:\Users\lulu\miniconda3\envs\env_isaaclab\python.exe' .\run_preparation_cpu.py
```

The generated `reports/<unique-id>/SYNTHETIC_MANIFEST_NOT_DATA.json` can be checked with `moe_train_entry.py --manifest ... --splits ... --synthetic-contract-test`. Omitting the synthetic test switch must reject it. `--train` always rejects. No native dataset has been certified and no training is enabled by this package. Placeholders in the CPU-import path are labeled non-training statistics.

Read `METHOD_AND_PAPER_PROTOCOL.md`, `DATA_AND_INTEGRATION.md`, and `NO_GO_AND_RESULT_TEMPLATE.md` for the scope, comparisons, actual contact/transition evaluation and remaining integration checks. All reports and failures are retained; Git archive and host72 serial deployment are root-owned and pending. No SSH, GPU/physics/policy execution, weights/data download, install, production/budget edit or Git operation occurred here.
