# I/O build blocker and preserved attempts — NOT SEALED

## 1. Concrete blocker

The required `active_qp_host.exe` and `active_qp_clock_harness.exe` are absent. Six ASQP-linked attempts (including diagnostic object links) reported compiler exit0 with no emitted warning/error, yet no retained worker artifact. The complete [link map](<link_diagnostic_01.map>) and [verbose link trace](<explicit_link_diagnostic_01.log>) show a linker path, not a usable executable. Do not equate those receipts with a successful binary.

A [FileSystemWatcher observation](<file_events_diagnostic_01.log>) at19:20:05 shows Created then Deleted for the exact diagnostic output, and `compiler_exit=0 exists=False`. It records lifecycle only, **not the deleting process**. Root cause remains unknown. There is no evidence sufficient to label this AV disposal.

## 2. Chronology before the parent's stop instruction

- [Build01 source snapshot](<revisions/build_attempt_01/build_io.py>) invoked strict GCC C99/O2/Wall/Wextra/Werror/pedantic/Wvla/no-fast-math/ffp-contract=off/SSE2 math. All5 commands returned0, but the [receipt](<BUILD_RECEIPT_01.json>) contained only clock_selftest and lifecycle-fixture PE32 files. Production and logical-clock worker were missing. The initial script checked compiler statuses but lacked an exhaustive required-output gate; this was an evidence/guard defect, not a valid delivery.
- Build02 preserved the two existing tiny binaries in the first revision, used short relative paths and added explicit output existence checks. [Receipt02](<BUILD_RECEIPT_02.json>) records production exit0 / artifact_exists=false, and the [runner log](<build_02.log>) has exit1. It stopped at that missing artifact; no compiler warning was suppressed and no kernel math/flags changed.
- A targeted edit of the final build condition first returned `old_string was not found` because the literal included a leading space not present after a semicolon. No bytes changed on that failed call. The relevant lines were read and an exact replacement succeeded; the executed revision is preserved. This is a tooling edit mismatch, not a compiler error.
- [Adapter compile-only verbose log](<missing_output_diagnostic_01.log>) produced a COFF object. [Three-source link trace](<missing_output_link_diagnostic_01.log>) still left no diagnostic executable.
- [Explicit-object link](<explicit_link_diagnostic_01.log>) and [map](<link_diagnostic_01.map>) were preserved. Minimal [link probes](<link_probe.c>) using no special math, fenv alone and strtof alone initially all reported `artifact_exists=True`. During the later partial inventory, the strtof-only executable was also absent, while the NONE/fenv probes remained. Initial existence is therefore not durable-retention evidence. This did not identify the deleting actor or establish a cause.
- The final [watcher observation](<file_events_diagnostic_01.log>) confirmed creation/deletion. Diagnostic target names merely preserved distinct attempts and were not accepted as renamed production solutions.

The parent instructed at19:23:54 to stop repeated same-source compilation/rename probes, perform one exact-artifact read-only event check and report attribution/unknown. **No compilation followed that instruction.** No AV settings, exclusion paths, protection state or detection evasion were changed or attempted.

## 3. Exact-artifact event/cleanup check

[EVENT_CHECK_01](<EVENT_CHECK_01.json>) covers19:11:28–19:25:05 and the full production/harness/three diagnostic paths. Defender Operational1116/1117 and Application1000/1001 returned no matching events in that window (`NoMatchingEventsFound`); the receipt has no artifact-specific disposition event. Earlier relevant crash/protection observations also had no matching result, but are not elevated into an attribution claim.

Static inspection of new project py/c/h found no unlink/rmtree/os.remove/DeleteFile/Remove-Item/move/rename cleanup call. The [builder](<build_io.py>) copies revision snapshots and invokes compiler commands; the [fixture](<sdk_fault_fixture.c>) only emits a banner and Sleep/exit; the [SDK](<active_qp_stdio.py>) closes its own streams and terminates only its owned process. Production was never executed. GCC/collect2/ld internal cleanup and external file-system actors are not attributed by these observations.

## 4. Valid partial tests, and explicit missing tests

- [Clock component run](<clock_run_01.log>):254 exact integer vectors,2514 checks/0 failures. These include overflow/frequency0/huge-remainder fallback and real monotonic QPC samples, with no stochastic wall-time pass threshold.
- [SDK-only run](<sdk_only_run_01.log>) / [report](<SDK_ONLY_TESTS_01.json>):29154 checks/0 failures. This includes186 **UNSENT** prepared input frames with exact f32 tokens, synthetic response rejection checks, explicit invalid warm, and standalone fixture EOF/nonreading-pipe timeout cleanup. The5087-character fixture request observed212733300ns at a0.2s watchdog; it is not an optimizer/MCU timing measurement.
- **Not run:** any production QP request;186-frame direct C output comparison; raw malformed/truncated/duplicate/nonfinite production parser tests; logical-clock early-abort through stdio; parent TRAIN MPC, physics, GPU, BSP or ARM runtime.

All stage conclusions are therefore **BLOCKED / NOT SEALED**. The prior sealed ASQP package remains read-only and independently qualified; this failure does not rewrite its results. Old-file/source hashes are checked in the [partial validation](<VALIDATION.json>), and all retained files/attempts are indexed by the [partial index](<INDEX.json>).
