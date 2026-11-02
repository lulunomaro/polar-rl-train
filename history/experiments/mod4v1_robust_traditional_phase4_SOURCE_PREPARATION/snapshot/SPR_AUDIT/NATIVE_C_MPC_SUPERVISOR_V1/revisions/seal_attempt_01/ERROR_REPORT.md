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

## Honest nonconvergence

**334** real new in-process ASQP results were nonconverged under the unchanged .002/64 cap and correctly selected independent GUARDED. They remain invalid kernel results with zero accepted kernel z; they are not used as a candidate or new warm. [Every record](<ALL_NONCONVERGED.json>) is preserved. The 1510 accepted / 1676 domain / 195 empty-intersection / invalid / disabled distribution is not upgraded to an all-MPC success score.

## Clock and typed extensions

Callback availability and monotonic ns checks, epoch equality, typed alias/context checks and saturating counters are explicitly new C contracts rather than old Python exception ABI. Alias output is unusable. Bad-certificate cases are pure helper unit tests on explicit result structures, not mutation of the real solver callback or a fake-solver integration path. Clock fault latching is actually integrated and tested.

ASQP START uses an explicitly anchored PRE_QP observed microsecond seed so delayed entry does not renew the complete cycle deadline. Clock-error poison is exclusively a cooperative termination signal; its kernel timestamps are not physical measurements. The final raw ns poll excludes all work afterwards. Fallback `valid1` only describes a valid mathematical C3 fallback, not eligibility to dispatch late output.

## Not inferred

No new physics/TRAIN episodes, contact/voltage/energy prediction, robot closed loop, C3 MPC final enqueue, BSP/CAN/bindings, target soft-double/libm resolution, FPSCR/FTZ, ARM runtime/stack/WCET, or complete 3ms driver qualification. The old blocked IO remains blocked. These module-local facts do not block other authorized component work or expand old physical conclusions.
