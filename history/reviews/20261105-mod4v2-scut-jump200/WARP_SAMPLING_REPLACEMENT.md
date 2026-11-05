# MOD4v2 Fudan sampling replacement

Human request, 2026-11-06: “用这套流程替换我们现在的，来加速我们训练”.

Implemented the GPU kernel/preallocated-output/CUDA-graph sampling pattern from
PoplarCrystal/basic_loco_lib, pinned commit
`e4181af587330d0b70ca72e0d36b49be32e12a65`. The reference files are
`source/basic_loco_lib/basic_loco_lib/tasks/velocity/mdp_warp/rewards.py` and
`doc/newton.md`. The first replacement preserves the proven PhysX TGS32/4
backend, actual MOD4v2 closed chains/mimic/CAD stops, 300N60mm gas model,
PD/DC/D0–D7, command/observation clocks, full learner checkpoint format and
the pinned Fudan reward equations. It does **not** claim that Newton,
ManagerBasedRLEnvWarp or the complete third-party framework has been installed.

The concrete affected hot path was the original per-wheel contact manifold
reduction (64 candidate points per filter per environment), hundreds of Torch
operations for the independent400Hz jump meter, and all16 Fudan terms at50Hz.
The new `warp_kernels.py` fuses each into GPU kernels. `warp_sampling.py`
stages changing Torch inputs into preallocated buffers, captures the small
kernel sequence and replays it, retaining Torch/Warp stream dependencies.
The actual manifold bounds error is latched on the GPU and checked before
the next policy endpoint can reach PPO; it no longer synchronizes twice
per physics tick. Invalid entries are not read by the kernel.

The same checkpoint-visible Fudan fields and per-term dictionaries are used.
The original contact history, reward clipping±2.5*dt, one dt.02, negative total,
command-tail order and fresh-reset behavior remain. The original independent
jump meter still rejects spawn falls, requires ground takeoff/whole-wheel
clearance/actual horizontal dual support and500ms stability. Raw flight
remains a reward flag, distinct from validated flight.

Local CPU and CUDA tests compared40 controls/all16 terms/contact and airtime
memory/reset;270 jump-meter endpoints included successful stable landing,
spawn drop, failed return and random orientations/contacts/history.
CPU maximum reward difference1.49e-8; CUDA1.86e-8. All15 existing CPU tests
passed. No policy/model or simulator was run for these checks.

Three retained synthetic20k contact+acceptance timing runs on the local
RTX5070Ti Laptop measured Torch/Warp respectively11.704/0.697ms,
10.661/0.583ms and6.761/0.277ms per endpoint. Variability is retained.
These are component-only timings; **no end-to-end training speedup has yet
been measured**. Production logging uses the same480000 samples/rollout,
so collection and iteration times can be compared directly after switching.

The old frozen Fudan segment `fudan_jump_final357_1h` completed104 PPO updates,
49.92M samples and2080 Adam steps, reaching final461. Full checkpoint SHA
`08c0888706a8b454fb80f8b218a1d6ce1d7436a3fdf976593252aa4c8e2a61ff`.
Its original owner safely closed and completed independent80 before release;
the original collector29424 returned the artifacts and exited. One full learner
diagnosis verified17 Adam entries at9220, LR0.00011390625, complete actor/critic/
STD/DR/RNG/queues/counter11064 and protected constructor nominals. Complete
train/eval logs contain no actual errors. All80 timed out at7.98s with zero
validated ground takeoff, clearance, landing or success. All4 early/late saved
pose images were reviewed with current native vision: spawn descent followed
by a low supported stance approaching the vertical face, without a jump.

The small overlay `fudan_warp_final461_1h` then launched at01:45:27 China time.
The actual4090 passed the same source-relative kernel tests before restoring
full461, including all17 Adam entries at9220 and LR0.00011390625. No observation,
action or command-profile adaptation was needed. One fresh physical reset
preserved the new constructor's nominal parameters. FIRST462 completed24
controls/480000 samples/192 physics callbacks/20 new Adam steps with nonzero
actor and critic gradients, then fully saved37124209 bytes, SHA
`2c77e32c2823b36a7724a4a2d7c7acf03212ca3f8530698b69da3053a458ccc8`.
The complete first log was checked without another checkpoint decode and
contains no actual errors. The original launch controller73776 exited and
bound the sole postround collector74388.

The first production rollout measured25255 step/s,18.675s collection,
0.331s learning and19.01s total iteration. The previous complete hour averaged
16211.740 step/s and29.642971s collection: this first-vs-prior-hour comparison
is55.8% greater throughput and37.0% less collection time. It is not yet a
complete-hour or steady-state benchmark. The environment/PPO population and
physics contract are unchanged. FIRST is execution evidence, not learned skill.

The fixed save boundary is02:45:27, nominal exit02:50:27 and the sole collector
starts finite formal return after02:46:12. The original direct GPU owner/private
lock/no-ledger admission, fullsave/safeexit/independent80 and3600+300 boundary
remain. Active source/INDEX/once are frozen; only local collector checks while
healthy. No second current-run receiver or live hotpatch.

Full Newton migration is separate work: the pinned library requires an
IsaacLab3.0/Newton1.7/Warp1.17 stack and a different solver. It has not been
substituted silently for the existing physical contract.

Development failures were corrected before any production change: JSON
case-collision in PowerShell, Warp dynamic-loop boolean declarations,
indexed tuple assignments, loop symbol types, boolean raw-flight dtype,
and capture on an imported Torch default stream. The final implementation
uses a Warp-owned stream with explicit dependencies. The exact failure
categories and retained test reports are indexed with this stage.
