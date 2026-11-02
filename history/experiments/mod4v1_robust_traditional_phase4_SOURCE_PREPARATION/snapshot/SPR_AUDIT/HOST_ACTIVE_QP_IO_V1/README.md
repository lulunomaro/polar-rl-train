# HOST_ACTIVE_QP_IO_V1 — BLOCKED / NOT SEALED

**Production resident bridge has not been delivered. Do not connect this draft to R37 or any robot-control loop.** The C adapter/QPC/SDK/schema sources exist, but every attempted production/test-clock worker executable was absent after link. Compiler exit0 is not accepted as build success. The actor/cause of deletion remains **unknown**; no matching exact-artifact Windows event establishes AV action. Parent instructed stopping further same-source compilation/rename probes; that instruction is respected.

[Scope fixed before work](<SCOPE.md>) · [Detailed failure chronology](<ERROR_REPORT.md>) · [Exact-artifact event receipt](<EVENT_CHECK_01.json>) · [File creation/deletion observation](<file_events_diagnostic_01.log>)

## Actual evidence versus pending evidence

| Item | Actual result |
|---|---|
| Sealed ASQP source/header | Read-only direct compiler inputs, no kernel copy/patch; see [frozen hashes](<SOURCE_FREEZE.json>) |
| First build | All5 compiler commands exit0, but only standalone clock/lifecycle fixture PE32 files retained; production/harness absent. [Receipt01](<BUILD_RECEIPT_01.json>) is not a successful bridge qualification. |
| Second build | Production compiler exit0 but artifact guard failed; script exit1; no production acceptance. [Receipt02](<BUILD_RECEIPT_02.json>) |
| Exact tick conversion/QPC component | **254 Python-bigint-derived vectors**, **2514 checks/0 failures**, including huge frequencies/overflow and real nondecreasing QPC observations; [unit log](<clock_run_01.log>) |
| SDK-only checks | **29154 checks/0 failures**; most are f32 encoding bit checks, not optimizer executions. [SDK-only report](<SDK_ONLY_TESTS_01.json>) |
| 93 cases × cold/warm | **186 prepared frames, 0 sent**; all input tokens roundtrip exact f32. [UNSENT frames](<PREPARED_UNSENT_186_FRAMES.jsonl>) |
| Production numeric replay vs direct C | **NOT EXECUTED** |
| Production malformed/truncated/duplicate/nonfinite raw requests | **NOT EXECUTED** |
| Deterministic early-abort I/O harness | Source exists, executable absent; **NOT EXECUTED** |
| Host timing / board / physics | No robot timing gate, new physics, GPU, BSP, ARM execution or WCET claim |

The existing sealed ASQP numerical conclusions remain independent and unchanged. Its [public contract](<../ACTIVE_BOX_QP_V3/active_box_qp.h#L28-L36>) and [sealed qualification](<../ACTIVE_BOX_QP_V3/README.md>) are not upgraded by this I/O draft. postR16 / PH3 pending; no PH2 enlargement.

## Draft API and source closure

Python module: [active_qp_stdio.py](<active_qp_stdio.py>). Class/method sketch:

```python
with ActiveQPLocal(timeout_s=5.0) as qp:
    result = qp.solve(H, f, lo, hi, warm,
                      max_pivots=64, tolerance=.002, budget_us=remaining_us)
# Main fields: valid: bool, status: int (0=CONVERGED), z: list[n],
# kkt_upper: float, stats: dict; all JSON-compatible.
```

This is an **interface sketch**, not a working-production example while the worker file is missing. There is no ctypes or NumPy dependency in the SDK. The worker is intended as one resident PE32 x86 process owned by the Python64 client; no automatic worker restart or implicit saved warm. Each frame explicitly supplies every input and option. Fatal solver/protocol/transport/client-validation faults stop only that owned worker; MAX/DEADLINE/NO_PROGRESS/CYCLE/ROUNDOFF return invalid-zero numerical outcomes rather than success.

C source closure is [adapter](<active_qp_host.c>) + [clock implementation](<aq_clock.c>) / [clock header](<aq_clock.h>) + [generated identity header](<aq_io_build.h>) + the unchanged sealed [core](<../ACTIVE_BOX_QP_V3/active_box_qp.c>) / [public header](<../ACTIVE_BOX_QP_V3/active_box_qp.h>). Compiler argv use the sealed file itself. Standard C/MinGW runtime and Windows QPC are the platform dependencies. [Schema](<PROTOCOL_SCHEMA.json>) and [SDK](<active_qp_stdio.py>) are the Python-side closure. Full project-file hashes are in [source closure](<SOURCE_CLOSURE.json>).

Only accepted output is `status0 AND valid1`. For other solver statuses, accepted z/cost/KKT remain zero; status/pivot/clock statistics are retained. The adapter separately labels a private-iterate `diagnostic_kkt_upper` where computable. That post-return, read-only metric is outside the solver time window, exposes no usable decision vector and never changes acceptance. There is exactly one core solve per S frame—no diagnostic second solve or retry.

## Draft wire/time contract

[Protocol schema](<PROTOCOL_SCHEMA.json>) fixes magic `ABQPIO`, version1, operation, canonical decimal uint64 sequence and uint32 payload-token count. SOLVE prefix has n/max_pivots/tolerance/budget_us/warm_present/H_count/vector_count, then row-major n×n H and n-entry f/lo/hi/optional warm. Count is `7+n*n+3*n+(warm_present?n:0)`. Replies have42 typed fields, including16 z slots, with accepted trailing slots zero. First sequence is arbitrary positive uint64; later frames require exactly previous+1, no wrap. The SDK EOF-closes at exhaustion.

Production is intended to use real `QueryPerformanceCounter`: checked exact quotient/remainder conversion to uint64 microseconds, with a bounded modular decimal fallback when remainder×1e6 would overflow. The SDK admits only a `QPC / RN_NO_FTZ_DAZ / PE32 / sealed-SHA` banner. The separately named TEST_LOGICAL build is not silently accepted by the default SDK; this admission check was tested in isolation.

The sealed cooperative budget starts at ASQP START and excludes Python encoding, IPC, parsing, fixed pre-START setup, post-return diagnostics and response validation. SDK `roundtrip_wall_ns` spans solve entry through response validation/lifecycle; `completed_monotonic_ns` is a Python perf-counter sample. Neither checks the parent's full cycle. The parent must begin its absolute deadline before its C3 RPC, skip the solver when remaining_us<=0 (budget0 disables timeout), and recheck the reply/exit against that same deadline before selecting any numerical result. This is not MCU3ms/preemption/WCET evidence.

## SDK-only lifecycle evidence

[Tests](<sdk_only_tests.py>) exercised finite/shape/integer and response magic/version/count/sequence/status/valid/KKT/zero-on-failure checks, including uint64 values above2^53 and uint64/uint32 overflow. Explicit invalid warm was checked even with all-fixed bounds and max_pivots0. These are client checks, not production C parser qualification.

The [standalone lifecycle fixture source](<sdk_fault_fixture.c>) contains no optimizer. Its existing PE32 binary was used only for owned-worker EOF/timeout/cleanup checks: a5087-character request to a nonreading fixture timed out with the configured0.2s watchdog (observed212733300ns, observation only), and reader/writer threads plus the owned process all ended. This is neither a QP roundtrip nor a robot time limit test. Tests preserve [executed SDK snapshot](<revisions/sdk_only_attempt_01/active_qp_stdio.py>).

## Resume gate

1. Obtain a concrete explanation/receipt for linker-created output removal without modifying protection settings or using rename/obfuscation evasion.
2. Retain a verified production PE32 executable from the unchanged sealed source closure; preserve any new attempt separately.
3. Execute186 real/stress cold/warm requests, compare numeric outputs and algorithm counters to sealed direct C evidence, then test raw malformed/duplicate/truncated/nonfinite/integer-boundary handling and deterministic early-abort I/O.
4. Recheck all frozen old hashes; only then consider a successful I/O seal and parent TRAIN integration.
