# T01 full-CAD formal baseline: stand passed, low-speed failed

This is a failure-preserving intermediate checkpoint, not completion of T01.

## Exact execution and unchanged mechanism

The original latest_rm CAD flat_run spawn, 0.5 ms physics, 100 Hz control, source robot, closed chains, motor limits, processed-target D4/PD/DC path and coord_soft controller were retained. Only read-only post-step contact grading was added. Environment contacts cover every collidable world-body geom, not the single ground alias. The source contact-stable MULTICCD-disabled flag is specific to latest_rm.

Each case built one fresh model and one FullDR instance, was nominal, ran 12 s / 1200 controls / 24000 physics steps, and completed with exit 0. Both parent jobs were collected: pwsh-1a4b8120d4384f4d and pwsh-5b05560b4857418a. Each has 20000 contact samples over the predeclared 2–12 s window; current freejoint truth and cached dynamics epochs remain distinguished. Control receives no truth/contact grading.

## Results under unchanged T01_ENGINEERING_SCREEN_V1 gates

- nominal_stand, seed 420110: all case checks passed. Scored pitch peak .0025984496573422055 rad, roll peak .026160619362879636 rad, XY maximum .013051287089074883 m. Both main wheels supported for 100% of the scored window; guide, hard and unsupported sample counts were zero. Whole case wall time 39.5285068 s.
- nominal_slow, seed 420111: robot screen FAILED, not a software error. Progress 1.5033886882398866 m, steady speed RMSE .043550267135277 m/s and final speed RMS .007874197799045423 m/s passed. Roll peak .4257021439501015 rad and RMS .27322424819159674 rad failed. Main wheel support duty .87535/.92525 failed. There were 370 unsupported normal-force samples; the longest consecutive run was only .0005 s, so this is not labeled a continuous .185 s flight. Guide/hard counts were zero. Whole case wall time 40.708311 s.
- The original protocol was not relaxed. The remaining four DR cases were paused after this baseline failure. T01 is still in progress, with one passed and one failed baseline; T02–T36 have not started.

## Next bounded action and preservation

Analyze the saved failing trace once, then form at most three mechanism-grounded candidates. Do not rerun the pilot or these consumed IDs. Do not transfer a passing stationary result to moving robustness. Old frozen gains, heldouts, model, failed records, UI sources and other pending hardware work are untouched. Moving-jump candidate remains unexecuted.

The prior ledger/pilot/flat-source checkpoint is commit 4e4916361e505175e7203ae602377f95ec6b258a, annotated tag trial-20261104-mod4v1-terrain-ledger-t01-pilot. This checkpoint adds the final audit/runner, the actual two formal cases and updated task state. Active trace analysis and future candidate source/results are excluded until complete. Older PH12 pending work is not represented as archived.

Raw traces are indexed by actual path and size only; no large payload was reopened or hashed for this archive. Original record_experiment.py is unchanged. Its add call receives only a narrow in-memory --sparse insertion because this own worktree's sparse-checkout exclusion was already observed. No sparse configuration, old index, RL worktree, main ref or dependency was modified. Record helper is called once, without --push; push existing objects separately to explicit own branch/tag only. No physics, QA, native build or hardware execution occurs here.
