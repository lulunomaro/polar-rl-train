# Native supervisor attempts and limits

## Scope and actual attempts

This is an independent new in-process functionality, not a repair/rename/retry of the blocked old stdio build. No SDK/worker/parser was run or created. No protection settings, compiler flags or old files were changed to evade a missing artifact.

- Before implementation, a read request guessed `pc3_replay.c`; it did not exist and read failed without mutation. A subsequent glob located the actual [pc3_replay_host.c](<../portable_control_v3_current/pc3_replay_host.c>), which was then read. The existing saved C3 reply records and original fixture drive metadata were used as data, not rerun through the SDK.
- [Freeze01](<freeze_01.log>) succeeded: 924 old files, 13 references, unchanged real H15, 4068B const payload, numerical budget written before C execution.
- [Host build01](<HOST_BUILD_01.json>) succeeded: 7 commands, every expected artifact physically present. All exact argv/stdout/SHA and source/budget snapshots remain under the original attempt. New host test and C++ executables were subsequently actually executed and retained.
- [Run01](<HOST_RUN_01.json>) succeeded: 3717 fixed tuples, 36 raw old-H15 cold/warm calls, 45 clock insertion tuples and native typed cases, 84531 checks/0 failed; actual C++ extern-C smoke passed. That count is checks, not independent cases/robot episodes.
- [Analysis01](<analysis_01.log>) read the saved new evidence and unmodified parent Python v2, without rerunning the C test. It found 0 selection/ordered-state/counter/gradient/box/warm/fallback mismatches under the preregistered budget. All actual kernel problem inputs were bit-identical in this cohort; this is not a general proof that compressed arithmetic is bit-exact for arbitrary inputs.
- [ARM01](<ARM_BUILD_01.json>) succeeded: 4/4 new objects, macros/fromelf exit0. No ARM link or execution. [Object inspection](<object_inspection_01.log>) also read actual COFF/ELF symbol bytes to prove compiled data bits, not merely source literals.

After those executions, the parent explicitly requested a documentation boundary: ground-model yaw/pitch limits are not ground/flight permission, and jump/predicted-flight/non-normal/unbound-contact callers must disable this MPC. Only README/semantic mapping were appended; source/test/budget/object bytes did not change, and the original build snapshots retain the earlier wording. R39 GT/contact data was not read.

There was no failed C compiler/test attempt in this new module so far. Draft literal edits before the first build are not backdated as executed failures or extra successful runs. All first-run evidence is preserved; no hidden warning suppression, solver retry, H regularization, cap/tolerance enlargement or trajectory-based tuning.

## Metadata seal attempt01 — actual failure preserved

[seal01](<seal_01.log>) failed only at the link audit after old/source/build checks passed: the validator treated a byte-preserved archived SEMANTIC_MAPPING snapshot as a live document in its deeper revision directory, so its original relative parent link resolved from the wrong base. Three metadata files had explicitly `PENDING_FINAL_LINK_CHECK_NOT_A_SEAL` status, not a success receipt. Eight original files (script/error/log/provisional metadata/discovery/report) were copied unchanged into the original attempt archive before edits.

The metadata-only correction audits current top-level Markdown as live documentation; archived copies retain exact original bytes/relative paths as evidence, not relocated clickable documentation. Root provisional metadata is overwritten only after proving it matches the archived failed attempt and is not a completed seal. The final attempt uses a fresh host-glob inventory and distinct log. No C source, budget, compiler, test, solver output or old file is rerun/changed to repair metadata.

## Honest nonconvergence

**334** real new in-process ASQP results were nonconverged under the unchanged .002/64 cap and correctly selected independent GUARDED. They remain invalid kernel results with zero accepted kernel z; they are not used as a candidate or new warm. [Every record](<ALL_NONCONVERGED.json>) is preserved. The 1510 accepted / 1676 domain / 195 empty-intersection / invalid / disabled distribution is not upgraded to an all-MPC success score.

## Clock and typed extensions

Callback availability and monotonic ns checks, epoch equality, typed alias/context checks and saturating counters are explicitly new C contracts rather than old Python exception ABI. Alias output is unusable. Bad-certificate cases are pure helper unit tests on explicit result structures, not mutation of the real solver callback or a fake-solver integration path. Clock fault latching is actually integrated and tested.

ASQP START uses an explicitly anchored PRE_QP observed microsecond seed so delayed entry does not renew the complete cycle deadline. Clock-error poison is exclusively a cooperative termination signal; its kernel timestamps are not physical measurements. The final raw ns poll excludes all work afterwards. Fallback `valid1` only describes a valid mathematical C3 fallback, not eligibility to dispatch late output.

## Not inferred

No new physics/TRAIN episodes, contact/voltage/energy prediction, robot closed loop, C3 MPC final enqueue, BSP/CAN/bindings, target soft-double/libm resolution, FPSCR/FTZ, ARM runtime/stack/WCET, or complete 3ms driver qualification. The old blocked IO remains blocked. These module-local facts do not block other authorized component work or expand old physical conclusions.
