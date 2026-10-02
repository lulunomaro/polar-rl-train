# MOD4 RL follow-up fix — 2026-09-15

This package fixes defects found while `s2_mild_dr` was running. It does not contain a new
robot asset and does not alter the baked tyre-load USD.

## Fixed

- Flight progress now requires the legal fly-ramp launch-region latch.
- Jump curriculum statistics include `jump_in_place` only; fly-ramp events cannot inflate it.
- Per-kind training totals are accumulated from terminal events before reset, so polling cannot
  miss one-step success pulses.
- Per-kind CSV is written inside its own run directory.
- `run_manifest.json` records and snapshots the USD selected by `RM_MOD4_USD`.
- Closure and mimic maxima are reported separately after spawn grace.
- Action smoothness excludes episode-reset discontinuities.
- Acceptance has nominal/DR per-route hard gates and exits nonzero when any gate fails.
- The v2 pipeline adds a 450-iteration specialist phase for tunnel/fly/in-place jump and writes
  `NEEDS_TRAINING` instead of `COMPLETE` when deterministic acceptance fails.

## Safe application boundary

Python source files may be installed while the current `s2_mild_dr` interpreter is running;
that interpreter has already imported its modules and remains unchanged. New code takes effect
when the next Python process starts. Do not overwrite or restart the currently executing shell
pipeline. Use `train_1536_skill_recovery_v2.sh` for a controlled resume from the completed s2
checkpoint so the specialist phase is not skipped.

Resume contract:

```bash
RM_RESUME_FROM_S2=1 \
RM_RESUME_CHECKPOINT=/absolute/path/to/s2/model_599.pt \
RM_RUN_TAG=takeover_1536_fix2_20260915 \
bash train_1536_skill_recovery_v2.installed.sh
```

The resume checkpoint path is hashed into `supervisor/RESUME_CHECKPOINT.sha256` before Isaac
starts. The s1/s2 blocks are skipped and training begins with `s2b_specialist_recovery`.

## Validation

- All seven changed Python files parse and compile locally.
- Static assertions cover the launch latch, in-place-only counters, active USD path, run-local
  CSV, post-grace plant metrics, and reset-masked smoothness.
- Synthetic acceptance pass exits 0; a tunnel failure writes its reasons and exits 2.
- Target-side `py_compile`, contract tests, and a short Isaac smoke test are required before
  resuming training.
