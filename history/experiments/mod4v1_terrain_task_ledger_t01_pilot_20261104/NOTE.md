# MOD4v1 terrain task ledger and first full-CAD T01 pilot

This is a bounded progress checkpoint, not completion of T01 or the full robot goal.

## Request and change

The user requested a complete 36-item adaptation task table, sequential execution, explicit Stop That Shit limits, durable progress across context compression, reuse of prior work, and Git recording. The task ledger records the one current item, consumed case IDs, actual jobs/results, the next allowed action, historical reusable evidence, and per-task Git requirements.

The current baseline reuses the existing coord_soft controller and original sensors, model, PD/D4/DC path, motor limits and closed-chain constraints. The full latest RMUC CAD static geometry is imported without the old RL robot, policy or yaw assistance. Only this scene adopts the collision-fix source's MULTICCD-disabled flag.

## Actual T01 pilot

- Case: t01_latest_cad_stand_nominal_420101_pilot001; original latest_rm flat_run spawn; seed 420101, nominal, stationary 0/0 command.
- One fresh model and one FullDR instance; 8 simulation seconds, 800 control calls, 16000 physics steps; complete and finite.
- Peak true pitch 0.007998031928684653 rad; peak roll 0.043762008190847926 rad; max XY displacement 0.013051287089074883 m.
- Max cached closure 4.5962502698668724e-6 m; mimic 1.0185031400322675e-5 rad. Current root pose and last dynamics-stage caches are separately labeled.
- Model build 8.2871993 s; whole case 25.7646033 s, including Python, logging and concurrent load. Not ARM WCET or isolated native-physics timing.
- Two-kHz contact identity was not instrumented in this pilot: null/UNKNOWN, never zero. full_T01_acceptance=false.
- Job pwsh-c75e8938e8d14f1b completed with exit 0 and was collected. Do not rerun it.

## Reused work, including unsuccessful alternatives

The selected flat-controller sources and all twelve small result summaries preserve baseline and rejected alternatives, not just the selected controller. They are prior TRAIN evidence, not proof of success on this new CAD or final reliability. Existing H1/H2/H4/H5 are immutable and are not rerun or tuned here.

The FPS source and stationary-jump wrapper are source snapshots. jump_moving_v2 is an unexecuted candidate, not a moving-jump result. Interactive GUI processes do not hot-reload source; this snapshot is not claimed to be an exact binding to every historical live-GUI interval.

## Cutoff and pending work

The new formal T01 runner and contact-audit module are active work and intentionally excluded at this cutoff. No formal 12s/slow/DR T01 case is claimed here. T02-T36 remain pending their stated scopes. Older C18-C23, deployment/operator materials, new-source reuse and other PH12-pending work remain pending in the existing local ledgers; this narrow checkpoint does not claim to archive every earlier report.

Large raw traces, mesh assets, CAD, USD and ZIPs remain at their original sources. External indexes record actual paths/sizes and existing hashes; unknown hashes remain unknown. No raw payload is reopened or hashed solely for this checkpoint. No training/GPU/SSH/hardware action is added.

## Repository isolation

Only the separate repo-lqr-robust worktree and mod4v1-lqr-mpc-robust branch are used. Do not alter the RL worktree/index or push main. Use the original archive_tools/record_experiment.py with one unique annotated trial; if push fails after commit, continue pushing those objects instead of recording again.
