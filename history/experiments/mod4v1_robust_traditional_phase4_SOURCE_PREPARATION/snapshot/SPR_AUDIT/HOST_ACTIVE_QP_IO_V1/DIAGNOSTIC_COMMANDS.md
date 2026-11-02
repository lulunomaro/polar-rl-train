# Historical diagnostics — do not replay while blocked

These are already-executed investigations before the parent's19:23:54 stop instruction, not a retry prescription. Compiler logs and maps survive. No command modifies protection settings. Parent/source chronology is described in the [error report](<ERROR_REPORT.md>).

Build01/02 complete exact argv are recorded in [receipt01](<BUILD_RECEIPT_01.json>) and [receipt02](<BUILD_RECEIPT_02.json>). Revision snapshots retain the executed scripts and compiler inputs.

Common flags for adapter/core/clock objects were:

```text
-std=c99 -O2 -Wall -Wextra -Werror -pedantic -Wvla
-fno-fast-math -ffp-contract=off -msse2 -mfpmath=sse
-I ../ACTIVE_BOX_QP_V3
```

All following commands ran from this new directory with C:\MinGW\bin\gcc.exe:

```powershell
# Compile-only probe, saved verbose stdout/stderr:
gcc -v <common_flags> -c ./active_qp_host.c -o ./adapter_diagnostic_01.o
# Full three-source verbose link:
gcc -v <common_flags> active_qp_host.c aq_clock.c ../ACTIVE_BOX_QP_V3/active_box_qp.c -lm -o active_qp_host_diagnostic.exe
# Explicit objects, same strict flags:
gcc <common_flags> -c aq_clock.c -o clock_diagnostic_01.o
gcc <common_flags> -c ../ACTIVE_BOX_QP_V3/active_box_qp.c -o core_diagnostic_01.o
# Link trace/map (diagnostic output was absent):
gcc -v adapter_diagnostic_01.o clock_diagnostic_01.o core_diagnostic_01.o -Wl,-Map,link_diagnostic_01.map,--trace -lm -o explicit_link_diagnostic_01.exe
# Minimal library probes (initial exists=True for3; later strtof exe absent; no solver):
foreach ($mode in @('NONE','PROBE_FENV','PROBE_STRTOF')) {
  gcc -std=c99 -O2 -Wall -Wextra -Werror -pedantic "-D$mode" link_probe.c -lm -o "link_probe_$mode.exe"
}
# Last diagnostic link, with a FileSystemWatcher on this directory:
gcc adapter_diagnostic_01.o clock_diagnostic_01.o core_diagnostic_01.o -lm -o watch_link_diagnostic_01.exe
```

The watcher subscribed to Created/Deleted/Renamed of `*.exe` before the last command, then dumped queued events, compiler exit status and `Test-Path`; subscriptions/watcher were disposed afterward. This removes only in-process event subscriptions, not files. [Observed events](<file_events_diagnostic_01.log>) identify the full target path and ordering, not the actor.

After the stop instruction, the only event-log operation was a read-only check over the exact production/harness/diagnostic full paths and the recorded build window, for Defender Operational1116/1117 and Application1000/1001. Its [receipt](<EVENT_CHECK_01.json>) records no matches. No further compilation followed. Standalone already-existing fixture processes were subsequently run only for SDK lifecycle checks, as explicitly distinguished in the [SDK-only report](<SDK_ONLY_TESTS_01.json>).
