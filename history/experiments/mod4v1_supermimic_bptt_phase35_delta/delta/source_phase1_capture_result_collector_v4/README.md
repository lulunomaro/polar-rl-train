# Collector V4 — fixed SOURCE derivation, not an actual collection

## Scope and completion evidence

This NEW directory derives from the immutable [collector V3](<../source_phase1_capture_result_collector_v3/README.md>). The session catalog offers Office and Windows ACL skills, neither matching this SOURCE/stdlib task; work uses FS/CLI and the existing Python314 `-B` interpreter only.

The final suite contains **51 current collector SOURCE/fake/AST tests**. Its first complete run passed **51/51**, zero failures/errors, 3.398 s. The final receipt records a fresh complete run, with no skipped or excluded tests. This is not an upstream 11/28/44, prior V3 43 or template 40 result.

Artifacts: [fixed inventories](<SOURCE_PINS.json>), [final SOURCE receipt](<SOURCE_RECEIPT.json>), [actual test log](<FAKE_TEST_LOG.txt>) and [nine-member content seal](<SOURCE_SEAL.json>). Subsequent sealer calls verify bytes only; no frozen member is rewritten.

This package does not run actual collection, full metadata-closure import, fixture/canonical import, Torch, B2 CPU/native, SDK/GPU, PT/raw/model reads, canonical ledger/locks, Git, staging, dispatch or training. It does not read actual reports or traces. **Gate1 remains UNKNOWN; capture interface, exact and stage2 remain false.**

## Final published worker V4 identities

All final identities were supplied before local inventory/receipt/seal creation and then checked against full actual SOURCE bytes. The whole [worker seal](<../source_phase1_capture_worker_v4/SOURCE_SEAL.json>) and all thirteen members are verified, not only the five candidates.

| Fixed SOURCE input | Bytes | SHA256 / root |
|---|---:|---|
| Worker index | 134423 | `75e36c0255a3b354dd0efeec33600f9b38d51ca28484de2dbed55db865fc7b2d` |
| Worker seal | 2919 | `ba3409a5450e378ea97eac64f0fec4c3409ac974a4c3378d0c6e6a6cfc405180` |
| Thirteen-member root | — | `758dc867cc4040a6f1eb9f587cc88f69a3866e03a9553290128a1681cda039e8` |
| Worker candidate | 16326 | `25fa00939694f9558c8aa1a9af73a40bf9b6b1cae666e1e636c70e6e8ab2f7e9` |

The other four candidate identities remain exact V3 bytes: runtime 19145/`490dcb8fd561b8db3af78db29db59d28b6dea33e7a8026609f3d1ddb62a93017`, parent 9336/`d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41`, contract 9518/`7910d7f3378923275b430b7960ed833f79b394feb3317c857d3a98c501729a0a`, observer 10438/`8a6faa66d55d4498fd1249aaabfeb9dfd7bb9e0b01013137adce3756b3c9004c`.

A dedicated full-byte test replaces the single V4 call `boundary=core().OriginalEpisodeBoundary(torch,bridge.device,n=80)` with its V3 `env.device` form and proves the **entire** worker becomes identical to V3. The other four files compare byte-for-byte directly. This proves the SOURCE delta, not the cause of any actual native failure.

## Three explicit inventories: 50, 174 and independent boundary 9

[Source validation](<source_pins.py>) keeps the inventories separate. The original fifty and B2 174 overlap; no disjoint union count is asserted.

1. **Fifty fixed source inputs:** final worker thirteen-member package, original partition nine, complete original17 + candidate5 + dependency5 mapping, original controller/connector/static dispatcher reference. Runtime aliases remain exactly **27**. Old collector V1/V2/V3 nine-member seals and every member are independently rechecked but not added to the fifty.
2. **Inherited independent B2 extra 174:** complete B2 thirteen-member package plus seal; 435 manifest declarations resolve to 155 unique full original Python files, each checked with full bytes/SHA and AST only; diagnostic four and final SOURCE handoff are checked separately. The old 105 count is not substituted for 155. B2's upstream content root remains null. The B2 wrapper/reset verifier is neither imported, executed nor reimplemented. Nine SOURCE-reference validation helpers retain exact V3 AST after SOURCE-version string normalization, and B2/diagnostic dependency constants and paths remain exact.
3. **New independent boundary SOURCE 9:** the [boundary source seal](<../source_phase1_boundary_device_contract_v1/SOURCE_SEAL.json>) plus its eight exact members are all read and hashed; four `.py` files are AST-parsed only. These nine are **not claimed covered by fifty or B2 174**, not runtime aliases, and not imported or executed. The fixed SOURCE test log is a sealed package member, not a runtime log tail.

Boundary SOURCE seal: 1570 bytes / `c9fae49e96b7042863372e7fb681c7c93fd8ce733646908222c9af6f7d306bdc`; eight-member root `5b4d0134e8ec0d828adef1fae8156d195ede032eacea2476457a403162e9e106`.

The independent boundary checker compares exact SOURCE paths, complete member identities and SOURCE-only scope. Negative tests cover missing/duplicate/traversing members, changed full bytes, AST failures, stale/wrong seal/root, runtime-alias promotion and invented actual/CPU claims. It does **not** implement the canonical boundary predicate or reset verifier. The upstream contract's `full_canonical_imported` field describes its original SOURCE producer, not an import performed here. Upstream eleven tests and the parent's actual Torch CPU report are not rerun, read, used or claimed.

## Strict V3 production preservation

[The collector](<collect_capture_result.py>) changes only its local default report tail V3 → V4. [The remote reader](<remote_metadata_reader.py>) changes only SOURCE version/derivation constants and final fixed worker/index metadata. Every production function/class AST matches V3 after normalizing **only that report tail**. Earlier V1/V2 preservation proofs and all thirty original core test-method ASTs remain intact.

Unchanged future collection contract:

- Typed APIv1 wire kinds/filenames, purpose `NEW_PASSIVE_INTERFACE_PROBE_NO_TRAIN`, root prefix `MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_`, five worker aliases and the original parent SHA `d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41`.
- Original controller SHA `95952059e6e8640a5ba37e858ca29c5f313340e041260093ecc8aaf671665831`; original RAM-only `connect72` factory in the future caller, never called here.
- Whole 27-alias runtime → core → full AppV6 → Base metadata closure with actual origins and original predicates. No AST stub or Torch subset substitutes for future metadata closure.
- Producer SOURCE_GRADE, original own-child actual waits/both EX releases, worker semantic close and independent outer controller actual parent wait remain distinct. RC0/materialization/finally alone never pass.
- One bounded whole read/hash/parse of each terminal FINAL, caching the exact bytes. Embedded trace parsing is reported truthfully; raw trace fields are not exported. A projection is never substituted for whole-FINAL hash proof, and no grader reopens a partial mirror.
- Full binding equality and original errors preserved. No epoch stripping, producer verdict repair, boundary/term/trunc normalization or fast-intent/full-FINAL hash repair is done by the collector.
- Missing observed counts remain null, not fabricated zeros. PT0 synthetic actions are not policy quality, training or interface proof.
- Collector interval 20 s / cap 6000 s only; original resource/ready/worker bounds 1800/900/2400 stay unchanged. No parent restarts, stops, signals, remote writes, PID-disappearance inference, `/proc` scan, locks or accounting actions.
- Bounds remain ordinary JSON 2 MiB, plan 8 MiB, each large terminal JSON 64 MiB, each of three own log tails 16 KiB, export 16 MiB. Atomic new local output only.

## Template history and final checks

Before final V4 pins existed, the unsealed template passed 39 tests (0.227 s), then 40 with the B2 AST proof added (0.236 s). Its declared full suite was then 47, with seven final-dependent tests excluded; those runs emitted no inventory/receipt/seal and were explicitly NOT_READY. That history is retained in the final receipt, not relabeled as final evidence.

After final pins arrived, four boundary/worker-source tests were added, producing the current full 51. The final run executes all 51. The inherited pending-pin and pending-sealer tests still patch identities to `None` and prove stopping before source/receipt I/O. The old upstream worker receipt and its recorded bootstrap-test history remain immutable inside its fixed thirteen-member package.

No actual V3 flag tensors, dtype/shape/device or actual env-device type were published to this child; these fields remain unknown/null. The SOURCE candidate does not confirm the V3 root cause. Live 100Hz MID/END noise-used, queue/reset identity, clean-sample and actual close receipts remain evidence gaps. Source success does not promote Gate1 or stage2.

## Local verification and future caller

Read-only SOURCE tests after freeze:

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B `
  'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_capture_result_collector_v4\test_collector_source.py'
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B `
  'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_capture_result_collector_v4\seal_source.py'
```

The final `--receipt` creation occurred once before sealing. Repeated receipt creation is an explicit error. Template mode remains an inspection mode with exclusions, never a final receipt or readiness result.

Future collection example — **not executed by this child**:

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B `
  'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_capture_result_collector_v4\collect_capture_result.py' `
  --dispatch '[ABSOLUTE_NEW_V4_DISPATCH_JSON]' `
  --output-root '[ABSOLUTE_NEW_ABSENT_LOCAL_OUTPUT_ROOT]'
```

The future dispatch must identify the parent's new unique V4 group beneath the original typed root prefix. No old V3 dispatch/result is relabeled or reused, and no new wire suffix gate is invented. Parent SOURCE review and actual work are separate from this completed SOURCE package.
