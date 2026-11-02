# ACTIVE_BOX_QP_V3 — honest attempts, failures and restart handling

## Input/method freeze

[freeze_01.log](<freeze_01.log>) froze530 old files and exact real H15 inputs before solver results. [NUMERICAL_BUDGET](<NUMERICAL_BUDGET.json>) was fixed first; no tolerance/H/box/seed/pivot-cap retuning. [Python proof](<python_proof_01.log>) first success:93 problems/186 double runs, no failure, worst54pivots; no parent physics import/step.

## Attempt01 — real warm failures, not an all-pass claim

[build_01.log](<build_01.log>) strict compilation first success. [runs_01.log](<runs_01.log>)1302 configurations/900CONVERGED/402nonconverged,21573 contract checks/0failure. Exit0 means return-contract consistency, not that every QP converged. Real cold64=18/18, warm64=14/18; warm256=16/18. MAX/CYCLE remained valid0 and z0. Original [source](<revisions/build_attempt_01/active_box_qp.c>), [binary](<active_driver_host.exe>), [raw runs](<C_RUNS_01.jsonl>), [analysis](<revisions/run_attempt_01/COMPARISON.json>) and [all402 failures](<revisions/run_attempt_01/ALL_NONCONVERGED.json>) retained.

[Read-only buffered diagnostic](<diagnose_warm01.c>) first success; [raw iteration trace](<WARM01_TRACE.csv>) proved free-face gradient noise about1e−6 amplified into several-ULP Newton jitter while wrong active multipliers remained about.3–.38. The original p-relative-ULP gate prevented sign release. No IO occurred inside the diagnostic callback and it did not mutate solver memory. See [full structural rationale](<ALGORITHM_REVISION_02.md>).

## Attempt02 — structural repair, same acceptance

[build_02.log](<build_02.log>)/[runs_02.log](<runs_02.log>) first success:1302 configurations/910CONVERGED/392honest nonconverged/21596checks/0contract failures. Repair qualifies free-face stationarity with the already-declared conservative KKT upper≤same.002, not a Hessian/regularization/tolerance/budget change. No cold restart or hidden fallback. Real64 cold/warm each18/18;8 active each8/8, max25/54pivots. All75 independent stress cold/warm64 pass. [Double regrade](<COMPARISON.json>) has no feasibility/certificate or actual-H15 accuracy budget failure. All392 low-budget failures remain [raw diagnostics](<ALL_NONCONVERGED.json>), never accepted candidate outputs.

## Clock/fault/software validation

[unit_build_01.log](<unit_build_01.log>)/[unit_run_01.log](<unit_run_01.log>) first success,531checks/0failure. [Clock CSV](<EARLY_ABORT_CASES_01.csv>) shows deadline while only1/120 full-factor cell completed, face/gradient/triangular/line/iteration internal stops, exit expiry after an exact solution, rollback and uint64 edge behavior. Also finite/pivot/shape/alias/fixed/tiny-tol/no-progress/roundoff faults. These are intentional fault returns, not discarded test failures or measured MCU deadlines.

18:29 host restart interrupted the session after attempt02 and531-unit evidence was already written. On continuation, current source, snapshots, raw output and logs were read from disk. Completed1302/531 computations were not rerun merely to replenish a missing conversation message. Only remaining new CPP/ARM and seal/hash validation were performed.

[C++ active-bound extern-C smoke](<cpp_run_01.log>) passed. New[ARM -c receipt](<BUILD_RECEIPT.json>)/[object QA](<OBJECT_SUMMARY.json>) has2/2 M4/M7 SP hard objects with all macro/fromelf events0; no old object/source overwrite. No unexpected compiler failure or warning suppression occurred in this stage.

## Remaining limits

No actual host timing benchmark, ARM runtime/FPSCR/FTZ/stack/ISR/WCET/board/BSP link or3ms/full robotMPC qualification. Relative timeout begins at first START sample after fixed setup; full control-cycle deadline is caller responsibility. No coupled/state/contact/power constraints. Clock callbacks are cooperative nonblocking observers; they are not asynchronous preemption. Numerical valid is not actuator permission. Previous QP1/2 failures and all older sealed artifacts remain part of the evidence, not retroactively upgraded by attempt02.
