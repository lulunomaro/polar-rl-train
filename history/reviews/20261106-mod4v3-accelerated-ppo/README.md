# MOD4v3 accelerated PPO and map-only continuation

The user canceled SuperMimic and requested the previous accelerated PPO route.
MOD4v3 R3 now runs on the actual PhysX TGS32/4 GPU backend with Warp fused
closure/mimic sampling, preallocated buffers and CUDA Graph dispatch. It is not
Newton or differentiable physics. Standing forward keeps command +0.35 m/s,
hip-to-wheel 3D L0 target 0.334 m, theta squared coefficient -2 and nominal/DR off.
The new v3 anatomical action order starts with fresh actor/critic/STD/Adam;
the old v2 actor is not falsely labeled compatible.

Real attempt results, including failures, are retained in
`RUN_REPORTS_SNAPSHOT.json` and `logs/`:

- Initial launch: the existing runtime wrapper clears PYTHONPATH. Repaired the
  task bootstrap using explicit sys.path before module execution.
- probe01: unattended SDK launch lacked the same EULA environment used by the
  existing authorized Isaac runs. Reused those existing environment values.
- probe02 / production: native assets loaded, but the SDK Warp proxy exposed a
  packed-state shape that caused an index error. restore02 had no source model
  because probe02 failed. Kit returned process exit 0 despite the recorded
  exception, so the owner now also checks the actual ERROR/FINAL receipts.
- attempt03: private GPU lock rejected a launch while the earlier own child was
  still alive. No foreign process was stopped.
- probe04: synchronous CUDA diagnostics localized the packed-state proxy index
  error. The runtime now unwraps SDK tensors before semantic queries.
- probe05: real PPO update, actor changed, 17 Adam entries, full checkpoint saved
  and scene closed. Maximum closure 7.254 mm, no closure/mimic/numerical resets.
- restore05: independent process restored actor/critic/STD/Adam/LR/RNG, ran the
  next PPO update and saved/closed. 17 Adam entries; closure maximum 6.999 mm.
- The next production launch refused an existing failed output path. It retained
  that failure and used production06 instead of overwriting it.
- production06: 4096 envs on host72 GPU0, fresh private GPU lock. Real first
  update 13,228 env steps/s and full checkpoint SHA
  73b82e16f3c11607d63917c71654d21e8f2e773560f91cf4f11389174134ae60.
  This is an early-iteration rate, not a full-hour speed claim. Native body mass,
  finite CAD stops, implicit gas 2000 N/m and 3 Ns/m, and zero implicit motor
  drives were read back. Individual closure failures reset their episodes at
  10 mm; they do not halt the entire batch. This does not demonstrate walking
  convergence.

The user's follow-up was “加速是加速，只换地图”. The current running source is
left at its existing save boundary. The next configuration selects exactly the
installed `isaaclab.terrains.config.rough.ROUGH_TERRAINS_CFG.copy()` without the
previous easy terrain substitutions. The installed source path and SHA are in
`OFFICIAL_ROUGH_INSTALLED_SOURCE.json`. Source map: easy mixed; destination map:
official rough defaults, 10x20 tiles, difficulty 0..1. Heights and proportions
are inherited from the installed official configuration. Root support Z is
read from the selected collision mesh after distributing isolated env origins.

The map change keeps the same MOD4v3 USD, PPO configuration, actor/critic/STD,
all 17 Adam states, learning rate, action order, reward weights, motor feedback
and voltage limits, PhysX dt/solver, Warp/CUDA Graph sampler, DR off and 4096
training envs. It restores the source final checkpoint after complete save,
safe scene close and independent80/actual replay. The map-boundary process is
already armed; this snapshot records preparation, not a completed map switch.

Large PT/ZIP/USD/NPZ originals are retained externally and indexed by actual
path/bytes/SHA in the report snapshot. The original released package and all
failed trials remain intact. No new chat, goal or automation was created.

The current work order is `CURRENT_WORK_ORDER.json`; the former work order is
preserved in `PRIOR_WORK_ORDER.json`. Later completion and evaluation evidence
must be appended and committed without rewriting this snapshot.
