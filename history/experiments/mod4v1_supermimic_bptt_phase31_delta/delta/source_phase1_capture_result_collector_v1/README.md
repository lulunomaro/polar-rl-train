# Phase1 own capture result collector v1 — SOURCE only

## Delivery state

This package supplies a future metadata collector, deterministic stdlib fake/AST tests, fixed SOURCE pins and an append-only SOURCE seal. Its authoring/test run does **not** connect to the server, run the future collector, read an actual FINAL/trace/PT/NPZ/model, import Torch/SDK, create a parent, inspect a GPU/PID, open the canonical ledger or operate a lock. The original partition's nine sealed members remain byte-identical. A fake execution-metadata PASS is only a function-contract test, not actual execution, SDK, Gate1 or interface proof.

No stage2, stager, trainer, scheduler, resource-admission replacement, native timeout/stop/restart or accounting writer is supplied.

## Future operator entry point

From the existing local project environment, after its **one original parent** dispatch:

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B `
  'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_capture_result_collector_v1\collect_capture_result.py' `
  --dispatch 'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\reports\PHASE1_E3_CAPTURE_V1_ORIGINAL_PARENT_DISPATCH_ONCE.json'
```

Optional `--output-root` must be a NEW absent absolute local directory. The default is a NEW timestamped directory under the existing project's reports tree. Output is the atomic `CLOSED_RESULT.json` inside it; an existing output root is left intact. On failure or a collector-only cap, the result retains the reason and unknowns; it does not replay or replace the original parent.

The actual CLI was **not run during this SOURCE delivery**. A later caller explicitly runs it. `connect_original()` verifies and uses the existing project connector's `connect72()`; existing RAM credential recovery stays there, with no copied credential/provider implementation or credential export.

Stable Python interfaces:

```python
collect(dispatch, output_root, *, connector=None, packet_reader=None,
        cap_seconds=6000, interval_seconds=20) -> (result_path, result)
summarize(dispatch, metadata_packet) -> closed_result
atomic_closed(new_absolute_output_root, result) -> result_path
```

The injected connector/packet reader in the tests is fake; production uses only the pinned original connector and the fixed remote metadata-reader source.

## Read boundaries and watch

- Dispatch identity is the actual current envelope: `root/group_id`, controller and parent `pid/linux_start_ticks`, one original parent Popen, parent/controller/stage SHA, new purpose. No `/proc`, process scan or PID-disappearance inference is used by the collector.
- Only its NEW root under `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_*` is admitted. No remote directory listing or recursive exploration occurs.
- Exactly one SSH metadata reader watches fixed own metadata aliases at 20-second intervals. Cap is 6000 seconds **for the collector only**. It sends no signal, starts no native parent/worker, changes no original deadline, writes no remote file, and touches no ledger/lock. The SSH channel read bound is not a native-worker timeout.
- It stops watching when the external actual-parent-wait file is published, or at its collector cap. File publication alone is not proof: final checks separately verify its identity, actual returned wait, zero rc and controller errors.
- Small metadata is parsed only when absent-before/changed; immutable published metadata changing is a contradiction. The original mutable barrier/resource-wait metadata remains observable. Published resource-wait reasons, including an original 1800-second resource expiry, are retained.
- It preserves the **complete GROUP_PLAN**, original producer SOURCE_GRADE, separate parent finally/EX scope, separate outer actual-parent wait/errors, terminal metadata, worker coverage/deficits and bounded own stdout tails. Three fixed own logs are tail-read once, at most 16 KiB each. It does not invoke GPU tools or reopen the canonical ledger represented by admission metadata.
- Bounds: ordinary metadata 2 MiB/file, complete plan 8 MiB, each large terminal JSON 64 MiB, aggregate SSH export 16 MiB. Exceeding a bound produces an explicit gap/error, not a truncated success. A metadata log tail is not a full-log hash claim.

## Honest whole FINAL / trace read semantics

The worker publishes `bounded_trace` inside its own FINAL. Therefore terminal collection **does read and parse that NEW own FINAL's complete bytes**, including its embedded trace. It does not describe this as “trace unread.” Each of the following has at most one full read attempt, only after external-wait publication or at collector cap:

1. own group FINAL;
2. own TERMINAL_ROWS (which repeats worker data);
3. own `cases/E3/FINAL`.

The same bytes supply `bytes/SHA256` and JSON parsing; the parsed object is cached for original preclose and fast-close checks. The worker projection drops `bounded_trace`, sensor/actuation raw event exports, RNG event payloads and setup buffers. Complete trace bytes are not downloaded or written locally. Reports explicitly record:

```json
{
  "remote_whole_FINAL_JSON_read": true,
  "new_capture_trace_fields_parsed": true,
  "trace_payload_exported": false,
  "remote_FINAL_read_count": 1
}
```

These are observed-reader fields: if no file/read evidence is available they remain null or a documented missing/read count, not invented success. Raw/full SHA is in file metadata; a projection is never passed to a whole-FINAL grading function or saved as though it were the original artifact.

No old raw, mother checkpoint, PT, replay, NPZ or unrelated trace file is opened. This permission is specific to the NEW own result-collection purpose.

## Complete metadata source closure

Before collecting, the future remote reader checks the exact capture index SHA and all **27** full source aliases (17 original + 5 new + 5 dependencies), plus the current controller's source. It imports the actual full capture runtime and original full core, AppV6 and its full Base dependency, checks their module origins, and enables a no-native-import/no-mutation audit guard. No Torch/SDK, AST-stripped helper or fake App/Base is substituted. Original parent/worker/module `main` functions are not called. This future full import was **not executed by this SOURCE authoring/test run**.

Original metadata predicates validate the complete plan and cached full worker FINAL/preclose. Fast close validates the original App binding plus exact full-FINAL SHA/bytes using the cached read, and compares the whole published binding faithfully. Returned close calls the actual core's two-argument metadata validator with the real helper. These are extra metadata checks, not physical SDK queries.

The producer's existing SOURCE_GRADE is preserved as its own original result. The collector does **not** reexecute `grade_closed_capture_group` on a local projection/mirror, monkeypatch its filesystem, repair its verdict, or claim a metadata projection is a raw artifact.

## PASS meaning and unknowns

Execution-metadata PASS requires all of the following together: exact current dispatch identity/stage+plan hashes; original admission/GO/worker identities; complete original source closure and metadata predicates; current own worker's bounded 64/128-control result and actual callback counts; original child terminal wait plus both EX releases; producer closed execution grade; independent outer `Popen.wait` receipt; and no published primary error. RC0, materialization, PID disappearance, parent finally, intent publication or a SOURCE-only grade alone each falls short.

Producer missing fields are null, not measured zero. In particular controls, callbacks, delay counts, actual Popen count, PT/training/optimizer counts and actual parent wait do not default to zero/true. Explicit PT0/zero-six synthetic probe fields are checked as published; PT0 does not mean SDK wall cost zero, policy quality, training success or interface admission.

Regardless of execution closure, this collector does not admit Gate1/interface/exact/stage2. It preserves producer `UNKNOWN/False`, reports contradictory promotions as errors, and keeps skill/eight-role success rates null. SDK cost settlement stays unverified; no new ledger gate/writer is added.

## Preserved producer defects — no hot repair

Source review found two possible original semantic-close failure paths:

- Current runtime's non-fast evaluator calls the original core returned-binding validator with one argument, while the actual signature requires `(binding, helper)`.
- Current `put_json` adds `capture_metadata_epoch` to a top-level binding document, whereas the nested intent/returned binding may retain the original dict without that extra key. Original whole-dict equality can then fail.

This package leaves every original source/producer verdict intact. It does not strip the epoch to manufacture a match, repair a running parent, or promote execution when the original producer grade/semantic failed. Tests explicitly exercise the unequal-binding case. Actual primary errors and source-grade errors remain in the result for the parent audit.

## Local SOURCE verification only

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B `
  'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_capture_result_collector_v1\test_collector_source.py'
```

Tests use only owned temporary fake JSON/logs and AST/stdlib. They cover unknown-vs-zero, old/foreign roots, fake complete execution, RC0-only failure, both EX releases, outer-wait independence, start-tick/PID mismatch, original errors/resource-expiry reasons, group-plan/full-FINAL hashes, one read plus trace projection, binding epoch mismatch, returned-helper signature shape, bounded tails/watch, output atomicity/reuse, injected transport/close failure and no native-lifecycle calls. No actual local dispatch report or server result is read by these tests.

[source_pins.py](<source_pins.py>) verifies 50 fixed SOURCE inputs, the original partition's nine sealed members and capture worker's 13 sealed members. It never calls the connector. [SOURCE_RECEIPT.json](<SOURCE_RECEIPT.json>) records test evidence only. [seal_source.py](<seal_source.py>) first creates the NEW seal, and future runs only verify it and its source inputs. This is a content seal, not an ACL/lock assertion.
