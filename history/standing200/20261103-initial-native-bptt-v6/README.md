# MOD4v1 wheel-leg supported ascent, 200 mm

Human authorization: use the SCUT video 1:55–2:08 and open source as reference, find an actually free GPU, schedule ongoing follow-up, and train RL+BPTT for coordinated standing ascent of a 200 mm step. This branch is separate from the 270 mm jump task. No change to its automation, checkpoint, or accounting.

On November 3, 2026, V6 reached actual native BPTT training on host72 GPU0 (`GPU-16828f91-2b45-b646-8dc0-9481138e2842`), run `MOD4_STANDING200_RLBPTT_V6_1793639156617427400`. GO was 01:07:37.562845 +08; original save deadline 02:07:37.562845; nominal close boundary 02:12:37.562845. Owner PID1496051/create1793639256.7 holds original authority/resource leases. Exact launch/worker identities and source SHA are in the indexed receipts. Do not replay launch/completion/FIRST, mutate live source, reset the canonical, or replace healthy processes.

## Actual evidence

The four-card snapshot covered host72 x2, host210 x1, and host86 x1. At 00:35 +08, both72 GPUs were empty,210 was compute-empty but had only790523904 bytes free on HOME, and86 had91% utilization with2462MiB free. Fresh original resource and canonical admission were repeated before V6. Temporary other-scope frozen E3/W35 evaluation was respected through its original child waits and lease release.

V6 original native constructor and the original full D0–D7 readback passed on the enhanced MOD4v1 asset. USD SHA `2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3`; contract SHA `bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755`. Physics .0025s/TGS32/4,policy50Hz,feedback100Hz,closure .01m per episode,mimic .01rad, original PD/torque-speed limits and queues remain. Course height and supported-ascent reward are explicitly new task configuration.

At FIRST,512 environments had316 controls,161792 real transitions,2528 physics callbacks and632 feedback samples. There was one verified policy BPTT optimizer step,H32, finite cross-time gradient0.01849835,WM path gradient0.00739812,parameter gradient4.309673;404 WM and404 auxiliary optimizer steps and4 critic optimizer steps. First full checkpoint239074513B/SHA `d8fba20dd5e12df318acc6a86d80601161ccabb90584b3ab50c8724e2328a6e9` is indexed by published metadata; it was not reread for this archive. All networks,four optimizers,replay,normalizers and RNG are included. Zero top-support/success events at FIRST; this is training startup, not standing ascent success.

## Training and SCUT relationship

The official repository and released stair policy/config review are already recorded in commit `fc0fbb73dd7532905fe9bf3c8396f51df960f2d8`, tag `trial-20261102-scut-standing-step-video-115-128-review`. The released policy is PPO, and its saved config has state machines disabled; current Rough-v1 also has a depth/height-triggered step-up command. This new MOD4 algorithm is not asserted to reproduce their PPO training or foreign policy weights. It adapts the body-lift command concept for200mm and uses our new supported-ascent objective.

Actor input is44=original noisy/delayed proprio35+current depth9. A frozen native E0 baseline plus a zero-initialized six-motor tanh residual is trained through a learned differentiable world model,H32. Actual simulator reward/termination labels train its auxiliary model; actor gradients do not differentiate PhysX. No online MPC, prerecorded jump feedforward, GT map or future actual depth enters the actor. Height assistance uses current valid depth, held for2s. Camera84x48 is provisional and not claimed calibrated D435i hardware. Fresh optimizer state belongs to the new BPTT learner; the source teacher's full PPO checkpoint/optimizer is preserved frozen, not falsely called resumed BPTT.

## Preserved failures and repairs

V1 optional base/lib missing: partial stage only,no owner/SDK/model. V2 blocked by actual local reader;V3 refused an already-consumed basename;both0network. V4 native constructor rejected mixed NumPy USD point tuple values; repaired conversion to native float lists. V5 created the environment then failed original reset compatibility because genuine `MOD4V1_ASSET_DIFF.json` was missing; zero model reads/optimizer steps. Both native attempts own-waited,settled costs and released leases. V5's local finally receipt reused aV4 basename and failed after SSHclosed; original error preserved.

V6 initially refused its own py.exe grandparent shell; direct executable corrected ancestry. A broad case-insensitive PAIR substring also matched an unrelated CAD `root_repair148.cs`; exact token scope filtering retains the complete raw inventory and every actual project controller. Actual other frozen evaluation blocked the next admission until original release. V6 staging then rejected an incorrect assumed source-asset subdirectory before owner creation. A unique completion filled the existing stagedV6 source/assets without duplicating the runtime tree,checked original metadata and unchanged compatibility validator against actual uploaded asset SHAs,then created its only owner. All original failures/once files remain indexed.

CPU synthetic BPTT and checkpoint test passed; its synthetic samples are not native skill evidence. A separate small CPU test verifies that later actual ground return invalidates previously accrued standing success. Evaluation error paths now retain partial environment/app lifetimes for original closure. These changes were made beforeV6 owner creation.

## Required close/evaluation follow-up

The original owner fullsaves and waits/closes/settles training, then runs an independent frozen80 first-episode evaluation,500 controls/10s,seed9137,new DR at the same fixed200mm course while preserving resource ownership. After its actual OWNER_EXIT, use the finite evidence transfer to obtain actual replayNPZs/manifold/curves and run the prepared renderer on the exact new USD meshes. Current model must `view_image` actual poses and inspect contact/velocity/heading/height curves before deciding continuation or targeted repair.

Declared standing acceptance: full wheel footprints inside the platform,both wheels on actual400Hz solver top support,no subsequent ground/edge return,planar/vertical speed<=.03m/s,roll/pitch<=10deg,yaw<=.2rad for.5s. Unsupported gap<=.10s is this task's declared operational definition; it was not measured from the reference video. Chassis/guide support during ascent is allowed. Loss,life,COM height or rendered geometry alone never passes this test. Full final evaluation is pending.

Hourly automation `mod4-200-rl-bptt` targets this branch and reads its current work order; no duplicate automation or parent-task mutation. Original sole canonical,strict reserve86412.86069250107s and3900/3600/300 window unchanged. No grants,refunds,account copies,clearactive,kills or second writer.

`INDEX.json` maps every captured local source/report/error/automation to exact original SHA and content-addressed Git text, referencing existing same-SHA Git source where available. Models/media/large raw are path/bytes/published-SHA only. Shared source directories were not recopied for each repair; only changed local overrides were added. Credentials are redacted before archival and never printed. Later final/replay/decision evidence requires an ordinary supplement, not retagging this trial.
