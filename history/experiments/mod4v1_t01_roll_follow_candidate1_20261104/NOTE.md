# T01 candidate 1: much less roll, but overall low-speed screen still failed

Parent retained the failing nominal baseline and its frozen gates. Bounded saved-data analysis found actual persistent roll rather than a large attitude-estimator error; it did not identify terrain height or prove unique causality. The baseline analysis JSON/short note are included, with no old raw reread for this archive.

## Candidate change

The new sensor-only controller uses public linkage FK and estimated orientation to infer relative wheel-center height. It adjusts opposite left/right joint references, retaining their exact common nominal hip/crank reference, original common sagittal P25 K, shaper, yaw loop, estimator, motor limits and processed-target PD/D4/DC path. It has a bounded height filter/slew, public linkage inverse and reference-rate limit. Its bilateral-ground prior is not an online contact detector, terrain-height measurement or flight policy. It is not wired into the live UI or moving-jump action. Original baseline source and protocol were not edited.

A new protocol version predeclared this candidate and fresh seed range 420120–420125; ALL command, duration, score-window and gate values remain the same as the original T01. Only nominal_slow420121_001 was run; other cases paused after its failure.

## Actual result

One new fresh model/DR instance, 12 seconds, 1200 controls, 24000 physics steps; parent job pwsh-6dca99d9f4dd45ac completed exit 0 and was collected. There are 20000 scored 2kHz contact points. Whole-case time 43.6168595 s; command time 4.9888272 s is aggregate Python wall time, not ARM WCET.

- Roll peak dropped from baseline .42570214395 rad to .04726674114 rad (about 24.39 to 2.71 deg); roll RMS .01617054809 rad. Pitch peak .07901136977 rad and RMS .02771260975 rad. All four attitude gates passed.
- Steady velocity RMSE .04317897167 m/s passed.
- Overall case_screen_pass=false: progress 1.10562613554 m, lateral .24011704880 m and final speed RMS .138384049998 m/s failed their original gates.
- Main-wheel support .8771/.92795 failed; unsupported samples 270, each run at most .0005 s. Guide duty .0073 and longest .0015 s passed their gates; hard contact 0. Peak summed guide normal 268.502 N and total normal 724.898 N are simulated samples, not a hardware impact qualification.
- Inverse diagnostics: no hold, no height clip, max residual below 1e-7 m, max joint reference delta .26963109 rad. A successful inverse is not successful whole-body behavior.

## Stop and next step

Candidate count is 1/3. Do not run the remaining stationary/DR cases yet. Compare saved C1 stop-window estimated velocity, true velocity, yaw/lateral motion and leg states in one bounded new-trace read before selecting a second mechanism. Do not reopen old baseline raw or relax the gates. T01 is not complete and T02–T36 have not started.

The durable task file is included up to this checkpoint. Source/results/analysis of the two original formal baselines were already pushed in commit 5779f03e9e1eaa5a98febe0c338b08564e83dbe5. This new checkpoint adds completed baseline diagnosis, candidate source/protocol and its actual failure. Active C1 stop analysis is excluded and pending the next real stage. Other old PH12 pending work remains pending.

Large traces are indexed by known path/size with SHA unknown; no archive-only payload read/hash. Original record_experiment.py stays unchanged; one in-memory git add --sparse insertion handles the known own-worktree sparse exclusion. No sparse config, other worktree/index or main ref was modified. The helper runs once without push; push existing objects explicitly to own branch/tag. No physics/QA/native/hardware is executed by this archive script.
