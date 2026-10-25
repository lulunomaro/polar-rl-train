# H1 T2-z transfer: method, data and paper preparation

Status: **PREPARATION_ONLY / REAL_RGB_DATASET_MISSING / NO_T2Z_TRAINING_STARTED**. All files here are local and pending root's unified Git archive. This directory does not grant a training, rollout, download or host reservation authorization. Preparation may be deployed by root to an isolated namespace on host72; T2-z training starts only after the existing H1 training has completed and root confirms the actual process/save/resource boundary.

The selected research direction is a direct **H1 visual T2-z transfer**. It is a new task/domain transfer of the fixed upstream method, with a new H1 action encoder; it is not a reproduction of the upstream manipulation task results. A small state latent model is a separately named comparator and diagnostic. Neither is a modification of the current PPO actor, observations, PD, rewards, physics or canonical accounting.

Read `METHOD_AND_INTERFACE.md`, `DATA_CONTRACT.md`, `PAPER_PREREGISTRATION.md`, `NO_GO_AND_RESULT_TEMPLATES.md`, then `INTEGRATION_HANDOFF.md`. `reports/ACTUAL_PREPARATION_AND_ERRORS.json` records what happened here. `reports/REPRODUCIBILITY_INDEX.json` inventories files and SHA256 values, with all failures preserved. Git completion is root-owned; no commit, tag or push was performed by this agent.

Executable preparation source:

- `contract_v1.py`: standard-library raw-manifest validator, exact physics-tick action packer, split leakage checks and model-view allowlist.
- `h1_temporal_action_adapter.py`: new small trainable PyTorch action module exposing the upstream adaln output shapes. No upstream/model import or weights are needed for CPU tests.
- `test_contract_cpu.py`, `test_adapter_cpu.py`, `run_cpu_preparation_tests.py`: synthetic-only CPU checks. The synthetic URI/SHA examples are deliberate placeholders and cannot satisfy `--require-real`.
- `synthetic_example_manifest.json`, `synthetic_example_split.json`: generated test fixtures, **not H1 data**. The five-frame fixture only tests alignment; it is not the proposed 41-frame training clip.

Run from this directory with an existing Python that has torch, on CPU:

```powershell
$env:CUDA_VISIBLE_DEVICES = ''
& 'C:\Users\lulu\miniconda3\envs\env_isaaclab\python.exe' .\run_cpu_preparation_tests.py
& 'C:\Users\lulu\miniconda3\envs\env_isaaclab\python.exe' .\contract_v1.py .\synthetic_example_manifest.json .\synthetic_example_split.json .\synthetic_conversion_NEW_UNIQUE.json
```

The second command produces a non-training-ready diagnostic interchange file. Adding `--require-real` to the synthetic example must reject it with `SYNTHETIC_NOT_TRAINING`. Do not repeatedly execute an earlier output path: the converter refuses overwrite. In actual deployment, the engineer must export `model` views separately from evaluator truth and complete the documented real-loader integration and file-content audit.

Current local evidence is limited: source67 short saved PPO records were consulted through small reports and source text. They describe 48 control frames / 0.48s, selected examples, zero recorded crossing environment-frames and zero landing increments in that excerpt. They are not a frozen FINAL evaluation or a complete dataset. Neither a policy checkpoint nor large NPZ/raw was opened here. Checkpoint references supplied by root are retained as provenance, not remeasured.

Fixed primary sources: [paper v1](https://arxiv.org/html/2610.22364v1), [upstream commit](https://github.com/T2-z-latent-optimization/T2-z/commit/c72f051f5cffcb1f372a32bc488df273556d39b9), [action encoder](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/wan_video_action/models/wan_video_action_encoder.py), [dataset loader](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/t2z/data.py). Direct GitHub API calls were not used in this preparation.
