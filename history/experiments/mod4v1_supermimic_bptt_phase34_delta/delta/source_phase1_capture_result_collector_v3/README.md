# Phase1 own capture collector V3 — fixed SOURCE derivation

## Result and scope

This NEW directory derives from the frozen [collector V2](<../source_phase1_capture_result_collector_v2/README.md>) with seal SHA256 `8a0dfd808483687f3a718d327c6dddf77d6989ed140eddc4de6dc262b832c29c`. Both V1 and V2 nine-member preservation checks remain independent of the fifty fixed runtime/source inputs.

The completed suite has **43 SOURCE / stdlib fake / AST tests**, including the original 30 test-method ASTs unchanged, V2 production-AST preservation and seven new B2 source-reference tests with negative subcases. This is this collector's own suite, not a reuse of upstream 28, worker 44 or old 96 test totals. Before final pins arrived, a separate unsealed template run passed 34 tests and explicitly claimed no final pins or extra refs verified. No failed development run occurred in this V3 derivation.

There was no actual SSH, result collection, remote metadata/trace read, full AppV6/Base metadata-closure import, B2 CPU/native execution, plant-module import, reset-verifier execution, PT/raw/model read, GPU/SDK execution, canonical ledger/lock operation, Git operation or training. Hashing source/AST is not actual SDK proof. Gate1 remains UNKNOWN; capture interface, exact, paper-ready and stage2 remain false.

## Exact final worker and sensor pins

| Source metadata | Bytes | SHA256 |
|---|---:|---|
| [worker V3 index](<../source_phase1_capture_worker_v3/CAPTURE_SOURCE_INDEX.json>) | 124202 | `bdeea3f057fb922bd9ae2670dcbf19188f651ca64ab2cbb0331f56a5a1124797` |
| [worker V3 seal](<../source_phase1_capture_worker_v3/SOURCE_SEAL.json>) | 2920 | `80b27d160b68cc67d38fe406b3507f2df10621a054ab237e758fd6e1af1061da` |
| [B2 sensor source API](<../source_phase1_passive_sensor_capture_v2/source_api.py>) | 31456 | `a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62` |
| [B2 passive capture](<../source_phase1_passive_sensor_capture_v2/passive_capture.py>) | 26599 | `4e05fe172068f8ed3e1f438ec73b57e89986e7da8316d16fd764026c8f53da9b` |
| [B2 SOURCE API manifest](<../source_phase1_passive_sensor_capture_v2/SOURCE_API_MANIFEST.json>) | 336133 | `2801135d1ff028f09a5eb7cd571cc3ca90694b60340d17e62374a42cbe60eaca` |
| [B2 complete thirteen-member seal](<../source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json>) | 2909 | `be538a07c8ccfb785023422ace6985e1fde0bd5b885266124e430527c1ec558a` |

Worker V3 thirteen-member content root: `b1b6ec96f93561d201c307cab9b17fbdc8591c6e362cef45a29ee63419f87963`. The B2 upstream seal has **no content-root field**; its published index root stays null. No B2 root is invented here.

The five worker V3 candidates retain the exact V2 bytes and original APIv1 aliases. Actual V3 paths are checked, so an old V1/V2 path with an identical contract hash is still a source-mapping error. All final hashes/lengths are hardcoded; pending/floating/old-index states stop source verification before the future connector call.

## Independent new source-reference verification

[The source inventory](<SOURCE_PINS.json>) contains two separately named inventories:

1. `sources`: exactly **50** fixed inputs, including full original17 + new5 + dependency5 aliases, worker13 and original partition9 sealed members, original controller and static original-dispatch/connector references. The original V1/V2 collector nine-member checks remain separate.
2. `extra_source_refs.sources`: **174** unique SOURCE file identities, separately checked and sealed. This includes the B2 seal + all thirteen members, **435** manifest reference declarations resolving to **155** unique full original Python sources, four reset-diagnostic SOURCE references and their final SOURCE handoff. Some B2 dependency files also occur in the fifty; 50+174 is not asserted to be a disjoint-file total.

For the new manifest closure, the verifier recursively collects `source_path` / `source_sha256` declarations from the pinned whole manifest; rejects incomplete/conflicting declarations; compares the exact 155-path/hash set to the fixed V3 index; reads each full original Python file for byte length and SHA256; and AST-parses it without importing/executing it. The old `oldSource105` count is not evidence for these new 155 files. The eight roles remain SOURCE-confirmed / live binding unknown.

The diagnostic scope is precisely four read-only SOURCE references plus [the final SOURCE handoff](<../source_phase1_sensor_reset_identity_diagnosis_v1/FINAL_SOURCE_HANDOFF_RECEIPT.json>). Their bytes/hashes are verified; the diagnostic Python is only AST-parsed. No reset verifier is implemented or called. The B2 runtime/source-API verifier is not imported or reimplemented; manifest regeneration/equality and actual reset-callable binding remain upstream/source claims and future runtime work, not newly executed proof here.

Negative cases cover stale sensor paths, missing/extra aliases, wrong seal/hash/member list, native-flag/root invention, conflicting/missing manifest pins, 435/155 cardinality/set mismatches, old105 substitution, full-source hash and syntax failure, non-source/out-of-project paths, and missing/foreign diagnostic or handoff references. Synthetic `.py` fixtures are owned temporary files within this NEW directory.

## Narrow production derivation

- Preserve typed APIv1: every wire filename/kind, purpose, `MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_` root prefix, five worker aliases, parent SHA `d5575ff2e670fd18ea0a09d9f3d5c05c46bf606a027fcb84d97c6e34a88a2b41` and controller SHA `95952059e6e8640a5ba37e858ca29c5f313340e041260093ecc8aaf671665831`.
- Production changes are restricted to final index/source mappings/seals, additive `source_version=3` / `source_derivation` and the local default report suffix. Every production function/class is compared to V2 AST after normalizing **only** that local report suffix; no grader, waiter, trace reader or projection is changed. All original 30 core test-method ASTs remain unchanged.
- The future caller supplies a NEW unique group ending `RESET_BINDING_V3` under the unchanged V1 prefix. There is no new suffix-gate, dispatch protocol or floating caller-source dependency.
- There is no stager, producer, reset verifier, trainer, scheduler, resource-admission replacement, accounting writer, native stop/restart or native timeout extension here. Original source, original reports and all old seals stay untouched.

## Unchanged future collection semantics

The following logic is inherited, not executed by this SOURCE authoring run:

- Only its NEW own capture root is admitted. Dispatch controller/parent PID and start ticks, stage identity and one original parent Popen are required. No `/proc` scan, PID-disappearance inference, GPU inspection or unrelated root listing occurs.
- Original connector/metadata-reader purpose only; polling 20 seconds, cap 6000 seconds for the collector. Original resource/ready/worker bounds 1800/900/2400 stay untouched. No remote writes, signals, locks, ledger access or parent creation.
- Full GROUP_PLAN and 27 full source aliases, metadata-only runtime → core → AppV6 → Base imports/origins and original metadata predicates remain required. No AST stub or fake App/Base replaces the future closure. This authoring run performs no actual closure import, B2/native execution, SSH or result collection.
- Producer SOURCE_GRADE remains independent and unchanged. Original own-child actual waits, both EX releases and independent outer controller actual `Popen.wait` are required separately. RC0, materialization, intent or parent finally alone does not pass.
- At terminal/cap, each own group FINAL, TERMINAL_ROWS and E3 FINAL has at most one complete read attempt. The same bytes supply SHA/length and JSON parsing; full objects are cached for validation. Reports truthfully state embedded trace was parsed while raw trace payload is stripped from export. No projection is presented as a whole-FINAL hash artifact and no grader reopens a partial mirror.
- Ordinary metadata bound 2 MiB/file, GROUP_PLAN 8 MiB, each large terminal JSON 64 MiB, three own log tails 16 KiB each and aggregate SSH export 16 MiB. Overflow or mutation remains an explicit gap/error.
- Missing counts/waits are null, never fabricated zeros. PT0 synthetic zero-six is not policy quality, training, SDK-cost settlement or interface proof. Whole binding equality and producer errors/history remain intact; no epoch stripping or producer repair occurs.
- Gate1 stays UNKNOWN; capture interface, exact, paper-ready and stage2 stay false; skill/eight-role success stays null. Missing live 100Hz MID/END noise-used, queue, reset-identity and clean-sample receipts stay gaps; source propagation does not fill them.

## Local SOURCE checks and content seal

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B `
  'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_capture_result_collector_v3\test_collector_source.py'
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B `
  'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_capture_result_collector_v3\seal_source.py'
```

The full test command verifies the fixed fifty and independent extra refs. `--receipt` is a one-time authoring option that writes only a NEW [test log](<FAKE_TEST_LOG.txt>) and [SOURCE receipt](<SOURCE_RECEIPT.json>); after freeze, reruns omit it. [The nine-member content seal](<SOURCE_SEAL.json>) is append-only: subsequent sealer calls verify bytes and never replace it. The log hash is computed from actual on-disk bytes.

The retained `--template` mode now excludes all seven final-source-dependent tests, runs only fake/AST checks, writes no receipt and explicitly claims no final inventory verification. Combining `--template` with `--receipt` is an error. Historical pre-pin template evidence remains 34 tests; the completed suite remains 43.

## Future collection entry after parent review

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B `
  'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_capture_result_collector_v3\collect_capture_result.py' `
  --dispatch '[ABSOLUTE_NEW_V3_DISPATCH_JSON]'
```

This command has not been run. An optional `--output-root` must identify a NEW absent absolute local directory. Default output is a NEW V3-suffixed local report directory with atomic `CLOSED_RESULT.json`. Existing reports, V1/V2 failures and all old source seals remain unchanged. The parent separately reviews and performs any actual preflight/full-stage/native operations.
