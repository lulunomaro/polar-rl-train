# Phase1 own capture result collector v2 — SOURCE only, typed APIv1

## Delivery state

This package supplies a future metadata collector, deterministic stdlib fake/AST tests, fixed SOURCE pins and an append-only SOURCE seal. Its authoring/test run does **not** connect to the server, run the future collector, read an actual FINAL/trace/PT/NPZ/model, import Torch/SDK, create a parent, inspect a GPU/PID, open the canonical ledger or operate a lock. The original partition's nine sealed members remain byte-identical. A fake execution-metadata PASS is only a function-contract test, not actual execution, SDK, Gate1 or interface proof.

No stage2, stager, trainer, scheduler, resource-admission replacement, native timeout/stop/restart or accounting writer is supplied.

## Fixed V2 derivation; unchanged APIv1

Only the source index, local worker source mappings/seal and additive SOURCE version/derivation metadata change from collector V1. Production function/class ASTs are tested identical after removing the two additive metadata keywords and normalizing the NEW local report-directory version suffix. All 30 original test methods are reused byte-for-AST without relaxation; three V2 tests add old-index rejection, actual V2 path/identity negatives, and full logic/wire preservation.

- Fixed worker SOURCE package: [worker V2 seal](<../source_phase1_capture_worker_v2/SOURCE_SEAL.json>), 2815 bytes, SHA256 `caacf07e8bc46bd2cc5f4fa14138782430d86de4f6382bbb35adcdcde5d469d5`, 13-member root `83cb35d61298fdac4d2c720d1322ada0fbfa43b866709b4e5958b99ac82b62d2`.
- Fixed [worker V2 index](<../source_phase1_capture_worker_v2/CAPTURE_SOURCE_INDEX.json>): 65961 bytes, SHA256 `cdb2ca55c08a544cd01e462b7ce27261900f3b6ebaffb4784350717f756b7cf7`. No floating/latest pin and no V1-index fallback.
- V2 worker 16323 bytes / `f2b7326efb546f0a274c978aa69c126506ed0d3c3a8a1792d80893fa9f163b0b`; V2 runtime 19145 bytes / `490dcb8fd561b8db3af78db29db59d28b6dea33e7a8026609f3d1ddb62a93017`.
- Original parent `d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41`, controller `95952059e6e8640a5ba37e858ca29c5f313340e041260093ecc8aaf671665831`, purpose, root prefix and every wire filename/kind stay APIv1. SOURCE receipt/seal/pin kinds explicitly end V2; packet and CLOSED typed kinds remain V1 with `source_version=2` / `source_derivation` extras.
- The future parent supplies a NEW unique group ending `BOOTSTRAP_FIX_V2` beneath the preserved `MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_` prefix. The original dispatch shape/root guard is unchanged; the exact fixed V2 index rejects an old V1 deployment before any full closure import. This authoring run did not create/read a future V2 dispatch JSON.
- The existing V1 dispatcher is a pinned static historical reference only. A future V2 caller has the same envelope shape and is not forced into a floating/nonexistent source-file dependency. The original connector remains pinned.
- [Collector V1 seal](<../source_phase1_capture_result_collector_v1/SOURCE_SEAL.json>) SHA256 `c6847784e4733f53767dc20f064b584eecda02f1046d88855f25d8e8381eca6c` and all nine members are independently verified unchanged, in addition to the 50 V2 source inputs. The V1 actual closed report was not opened or changed here.

## Future operator entry point

From the existing local project environment, after its **one original parent** dispatch:

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B `
  'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_capture_result_collector_v2\collect_capture_result.py' `
  --dispatch '[ABSOLUTE_NEW_V2_DISPATCH_JSON]'
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

## V1 history and fixed V2 producer — no collector verdict repair

V1 SOURCE history remains intact: the non-fast returned-binding call lacked the real `(binding, helper)` signature argument, and automatic top-level `capture_metadata_epoch` publication could differ from the nested original binding. The parent additionally reported V1's actual pre-SDK helper bootstrap-path failure; this child did not open that actual closed report.

The separately frozen worker V2 narrowly fixes its staged original-helper bootstrap, passes the real helper in the non-fast branch, and opts out of automatic epoch only for binding publication while keeping the default epoch behavior elsewhere. The collector merely pins this exact V2 source package; it does not perform those worker fixes itself, strip an epoch, relax whole-binding equality, regrade the producer, modify a running parent or rewrite a V1 failure. The old unequal-binding negative remains unchanged among the reused 30 tests. Actual primary errors and producer source-grade errors remain in future collection output.

## Local SOURCE verification only

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B `
  'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_capture_result_collector_v2\test_collector_source.py'
```

Tests use only owned temporary fake JSON/logs and AST/stdlib. They cover unknown-vs-zero, old/foreign roots, fake complete execution, RC0-only failure, both EX releases, outer-wait independence, start-tick/PID mismatch, original errors/resource-expiry reasons, group-plan/full-FINAL hashes, one read plus trace projection, binding epoch mismatch, returned-helper signature shape, bounded tails/watch, output atomicity/reuse, injected transport/close failure and no native-lifecycle calls. No actual local dispatch report or server result is read by these tests.

[source_pins.py](<source_pins.py>) verifies the corresponding 50 fixed V2 SOURCE inputs, the original partition's nine members and worker V2's 13 members. Its independent derivation check also verifies the old collector V1 seal/nine members unchanged; that check is listed separately, not mislabeled as another runtime source count. It never calls the connector. [SOURCE_RECEIPT.json](<SOURCE_RECEIPT.json>) records fake/AST evidence only. [seal_source.py](<seal_source.py>) first creates the NEW nine-member seal, and future runs only verify it and its fixed SOURCE inputs. This is a content seal, not an ACL/lock assertion. The log SHA uses actual `read_bytes()` so the prior V1 LF/CRLF preflight history is not repeated or rewritten.

The first V2 development run had 32 PASS and one error in the newly added AST boundary-constant test: `ValueError: malformed node or string on line 33: Name(id='OUTER', ctx=Load())`. The wire tuple deliberately references the already-defined `OUTER` alias. The SOURCE test's literal resolver was corrected to resolve only prior literal aliases (no exec/import); no production logic was changed to satisfy it. Final receipt/seal require 33/33 PASS and zero failures/errors. All tests remain fake/stdlib/AST, not actual SSH/native/SDK/closure-import proof.
