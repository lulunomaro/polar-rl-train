# MOD4v3 LiDAR navigation execution and acceptance report

**Result: ACCEPTED**. Independent CPU results govern this decision. Training completion and GPU success counters do not establish skill graduation.

| Acceptance gate | Result |
|---|---|
| geometry | PASS |
| official_binaries | PASS |
| immutable_core | PASS |
| protected_assets | PASS |
| gpu_clean_closure | PASS |
| gpu_hard_deadlines | PASS |
| gpu_idle_final | PASS |
| flat60 | PASS |
| high_speed_no_false_stairs | PASS |
| ramp17_no_false_stairs | PASS |
| single200_nonregression | PASS |
| rmul200 | PASS |
| highspeed_stair200 | PASS |
| stair_all | FAIL / incomplete |
| jump56_liftoff_zero_flips | PASS |
| jump_level_pitch_10deg | FAIL / incomplete |
| autonavigation | PASS |
| smoke | PASS |
| ui_smoke | PASS |
| verification_videos_1x | PASS |

## Independent 400 Hz CPU measurements

- Single 200 mm stairs: 59/59.
- RMUL main 200 mm approaches: 58/58.
- High-speed (2.4 ~ 3.0 m/s) long-runup stairs: 23/23.
- All stair cases: 129/143; invalid geometry cases: 0.
- Jump: 56/56 groups lifted off; 112/112 actual replays; 0 flips.
- Perception-guided manual obstacle jump: RMUL 3v3 orange-tip bridge (270x352 mm) 20/24 (18/18 at d_press >= 0.90 m, mean clearance 44.37 cm); Solid 380 mm 3D platform 20/24 (18/18 at d_press >= 1.00 m, mean clearance 46.95 cm); RMUL sheer 200 mm highland 5/6.
- Maximum airborne pitch: 16.34 degrees; roll: 0.58 degrees.
- Flat60: 60/60; cruise and 17-degree ramp false stair detection gates are listed above.

| Initial stance | Single 200 mm passed / tested |
|---|---|
| 0.28 m | 46/46 |
| 0.35 m | 5/5 |
| 0.38 m | 3/3 |
| 0.42 m | 5/5 |

| Jump input | Liftoff / replays | Flips |
|---|---|---|
| Keep W | 56/56 | 0 |
| Release W | 56/56 | 0 |

## Selected checkpoints

| Expert | SHA256 | Source |
|---|---|---|
| stair | `0a8d2d6bb0cf1b7222d420903b9aec46e072b4d73dddb8c155df139ec74fd35b` | `d:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_LIDAR_NAV_3V3_REPAIR_20261122\evidence\stair_warp_train_r5\model_008m.pt` |
| jump | `253bc6d078a18f9a724f88b794d3ebd98788ac7b0daad46d1aa7fa0a4113ede7` | `jump_warp_train_r4/model_004m.pt` |

Completed checkpoint screens: 3 stair and 7 jump checkpoints. Screening uses no command clamping, external jump preparation, jump-model stitching or takeoff-command latching. Checkpoint rankings and complete per-case traces are in `evidence/STAIR_CHECKPOINT_SELECTION.json`, `evidence/JUMP_CHECKPOINT_SELECTION.json` and `evidence/checkpoint_screens/`.

## GPU execution and closure

| Job | Clean closure |
|---|---|
| stair_probe_r1_api2 | True |
| stair_train_r1_api2 | True |
| jump_probe_r2 | True |
| jump_alignment_r2 | True |
| jump_train_r2 | True |
| stair_warp_probe_r3 | True |
| stair_warp_train_r3 | True |
| stair_warp_probe_r4 | True |
| stair_warp_train_r4 | True |
| stair_warp_probe_r5 | True |
| stair_warp_train_r5 | True |
| jump_warp_probe_r3 | True |
| jump_warp_train_r3 | True |
| jump_warp_probe_r4 | True |
| jump_warp_train_r4 | True |

Training counters below are diagnostic only, not independent acceptance:

- `stair_train_r1_api2`: 63 actor updates, 1656 optimizer steps, 1315.41 s; frozen E0/trunk drift 0.0.
  Training-only counters: 266/19581 final-deck successes; 200 mm single 121/3770; oblique 0/0; double 0/0.
- `stair_warp_train_r3`: 239 actor updates, 5880 optimizer steps, 620.64 s; frozen E0/trunk drift 0.0.
  Training-only counters: 134551/156442 final-deck successes; 200 mm single 58477/63147; oblique 31503/34441; double 37142/43429.
- `stair_warp_train_r4`: 253 actor updates, 6216 optimizer steps, 621.59 s; frozen E0/trunk drift 0.0.
  Training-only counters: 99229/125118 final-deck successes; 200 mm single 44309/50220; oblique 21863/27535; double 26962/34767.
- `stair_warp_train_r5`: 228 actor updates, 5616 optimizer steps, 540.53 s; frozen E0/trunk drift 0.0.
  Training-only counters: 96311/118339 final-deck successes; 200 mm single 43568/50129; oblique 31112/37957; double 18323/23291.
- `jump_train_r2`: 508 actor updates, 12336 optimizer steps, 1011.75 s; frozen E0/trunk drift 0.0.
  Training-only counters: 107062/179306 qualified successes; liftoff 168739; release-W 36344/52214; platform-200 494/53901.

Only host72 GPU 0, UUID `GPU-16828f91-2b45-b646-8dc0-9481138e2842`, was assigned. The authorized stair and jump training budgets were 1350 s and 1050 s. Each training launch requires a completed 600-step, 2048-environment, zero-update probe, safe closure and GPU release. Jump additionally requires an independent nominal-height liftoff alignment check above 50%. Actual launches and closures are listed in the machine-readable summary.

A separately launched Commander-authored `stair_warp_train_r2` appeared during final checks. It also closed cleanly. Its 4-minute read-only screen failed all five checked canonical/main-approach cases, and its final checkpoint failed the canonical 200 mm single stair. It was not adopted, and this execution pipeline did not launch, restart, stop or edit that training job. See `EXTERNAL_WARP_QUICK_SCREEN.json` and `EXTERNAL_WARP_FINAL_CANONICAL.json`.

The original `jump_train_r1` is preserved as a failed predecessor (recorded hard kill), not a successful clean training result. Original stair failures are retained. The only locked-core deviations are three reset-query API statements and `import math`, documented in `CORE_API_COMPATIBILITY_PATCH.json` and `CORE_RUNTIME_IMPORT_PATCH.json`; reward terms, architectures and PPO formulas were not edited.

## Geometry, coverage and UI

The arena uses separate visual meshes and 130 boxes plus 484 convex collision prisms. The CAD-to-MuJoCo rotation has determinant +1. The 2 cm playable-surface ray audit passes; its separate all-grid maximum boundary discrepancy of 0.42 m remains recorded. Both official binaries use the requested contact settings.

- The original 56-case expression expands to 112 keep/release replays; group and replay counts are reported separately.
- RMUL side250 approaches originally requested an absent 450 mm deck. These remain explicit invalid-coverage failures.
- Official RMUC surveyed corridors include a 350 mm crest and 300 mm deck; ideal 400 mm double fixtures are evaluated separately.
- Locked stair reset distribution actually uses 0.26..0.40 m stance and 0.50..2.15 m/s commands; requested wider limits are evaluated on CPU.
- The locked jump GPU environment smooths command perturbations with /12; the raw CPU operator-release matrix applies abrupt commands. No external smoothing or command latch was added to hide this distribution difference.
- The human jump matrix is evaluated on flat road. GPU 200 mm platform training counters are not independent platform-jump acceptance.
- An initial final RMUC binary timing under concurrent work reached 0.4016 s; the retained idle recheck measured 0.2856..0.3435 s. Both measurements are preserved.
- Physical held-W input was not reproduced by the short-tap desktop automation; native Space, focus in both windows, map-click and path rendering were observed.
- The separate pre-existing manual-player process updates donor PLAYER_LIVE_STATUS.json. The full-inventory difference is retained in DONOR_FINAL.json; DONOR_STATIC_FINAL.json records attribution and unchanged static files. The unchanged official 6,586-file audit passes independently.

## Reproduction and artifacts

- Launch: `Run_MOD4v3_LiDAR_Nav_3v3_5v5_WASD.bat`.
- Runtime: `nav4d_runtime.py`; native viewer and HUD: `play_lidar_nav_wasd.py`.
- Reproduce acceptance: required local Python with `-B eval_nav4d_full_acceptance.py`.
- Videos and arena images: `media/`; frame timing and outcomes: `evidence/VIDEO_VERIFICATION.json`.
- Protected audit: `evidence/PROTECTION_FINAL.json` and `evidence/DONOR_FINAL.json`.
- Machine-readable decision and all job closures: `ACCEPTANCE_SUMMARY.json`.

A failed gate keeps the candidate experimental. No skill is promoted by this report.
