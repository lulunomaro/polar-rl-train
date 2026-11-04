# Typed capture materialized-size SOURCE fixture V1

**SOURCE only.** Adapter ≤150 lines; five NEW AST/ownScalar cases. This pack has executed neither old CPU fixture, imported Torch, nor entered native/SDK/SSH/PT/raw/C/Git work. Actual coupled CPU/native CASE/GROUP bytes remain **UNKNOWN** until the parent separately invokes the new functional purpose. Gate1/Stage1 UNKNOWN; Stage2 False.

## Injection contract

[run_size_fixture](<size_fixture.py>) accepts the real `torch_module`, complete published `codec_module` and `passive_module`, an existing published CPU `CaptureCodec` instance, complete original `b4_run` / `c2_run` functions with their unchanged args/kwargs, and `source_paths` for the nine fixed small Python inputs in [SOURCE_PINS](<SOURCE_PINS.json>). Paths may relocate; bytes/SHA stay fixed. Keep the full old fixture modules, their original sibling source-pin/seal files, and original dependencies available. Use normal Python, not `-O` or inference mode. No source cropping, function transplantation, loader, setup repair or globals/default replacement is supplied here.

The parent prepares the codec with its existing CPU int64 witness index and explicit IDs 0..7, N80. Example **future parent call**, not executed in this SOURCE pack:

```python
size.run_size_fixture(
    torch_module=t, codec_module=codec_mod, passive_module=passive_mod,
    codec=published_cpu_codec, source_paths=actual_nine_source_paths,
    b4_run=complete_b4_fixture.run_fixture,
    b4_args=(t, OriginalSensorClass, OriginalDelayClass),
    b4_kwargs=dict(codec_module=codec_mod, passive_module=passive_mod,
                   field_module=field_mod, dependency_module=dependency_mod),
    c2_run=complete_c2_fixture.run_fixture,
    c2_args=(t, OriginalPhysicsActionQueue, actuation_mod, codec_mod, observer_mod, field_mod),
)
```

Both full old fixture functions run **once each**, normally to completion, solely as materialized-volume inputs. Their old check lists are not new independent 14/7 validations. The adapter neither edits predicates nor interrupts an original call. Existing source/RNG checks inside the full fixtures remain active.

## Precisely bounded observation

The single own `sys.setprofile` observes Python **return** events only for two specified code objects: published `PassiveCapture.finish` (first normal complete 64-control/640-record owned report), then the original C2 `run_fixture` return. Only the latter reads its known `frame.f_locals['wire']`; no other frame locals, object `self`, processes, traces or arbitrary hooks are inspected. References are retained without tensor clone/cast. `finally` restores the prior profile, including original exceptions. The adapter's additional materialization occurs after this hook has been restored and both original functions have completed; the fixtures' own existing serialization stays at its original positions.

The complete sensor report is passed through published `codec.materialize`. The complete C2 wire, including `windows` **and** `original_exception_events`, is retained unchanged; its raw JSON bytes/SHA must equal the original C2 function's own returned `wire_bytes`/`wire_sha256`. Additional own checks cover the nine source PINs, CPU owned object identities/metadata/version counters, canonical materialized inputs/scaffold digests, and global Torch/Python RNG. There is no extra tensor clone/cast or queue/math implementation. Tensor-version evidence is not native physical bitwise/readback evidence.

## Encoding and meaning of the measurements

- Component raw JSON: `ensure_ascii=True, allow_nan=False, sort_keys=True`, ordinary default separators including spaces; no trailing LF. This matches the original C2 raw encoding.
- CASE/GROUP JSON: UTF-8, `ensure_ascii=True, allow_nan=False, indent=2`, insertion-order keys, **internal LF characters and no trailing LF**. This matches producer JSON bodies and the original Linux parent's GROUP text body, not a Windows text-mode CRLF rewrite.
- Canonical digest: ASCII-escaped UTF-8, sorted keys, separators `(',', ':')`, finite values only, no trailing LF.
- Streaming `JSONEncoder.iterencode` counts and hashes the complete serialization without outputting the owned payload. `within_original_64MiB` is only a size statistic (`bytes <= 67,108,864`); it neither changes nor executes the existing reader/writer.

Minimal synthetic CASE is `{'sensor': full_sensor_report, 'actuation': entire_C2_wire}`. GROUP uses the original embedding shape `{'terminal': [{'data': CASE}]}`. There is no invented setup/DR, physical success, return code, wall clock, binding qualification or capture epoch. Label is always **LOWER_BOUND_SYNTHETIC_SERIALIZATION_NOT_FULL_NATIVE_BOUND**. This is a reduced synthetic metadata envelope around CPU-fixture components, **not a mathematical lower/upper bound for a native run**; the CPU fixtures also contain their own additional error/stress material.

Optional `scaffold={'case': {...}, 'terminal': {...}, 'group': {...}}` supplies parent-owned JSON-ready metadata. Sensor is replaced by the entire captured report; all C2 fields are merged into actuation; terminal `data` and GROUP `terminal` use the same embedding. Other supplied fields are kept. The extra result is exact only for these **supplied synthetic objects**, with no ABI/completeness/native guarantee. A desired `capture_metadata_epoch` must already be supplied; this adapter never fabricates one.

Only small statistics/status are returned. No owned payload or actual-report file is emitted. A synthetic size over 64MiB is not a confirmed native failure or a new approval rule; original producer/parent/cap, H1, physics, DR, acceptance thresholds and budgets stay unchanged.

## SOURCE receipt

[Five checks](<test_source_size_fixture.py>) cover AST/line count, exact scalar encoding (including Unicode/int64/bool/finite float), parent embedding/input immutability, targeted first-complete-return references, and original exception/profile restoration. See [results](<SOURCE_TEST_RESULTS.json>) and [seal](<SOURCE_SEAL.json>). These are NEW stdlib/ownScalar checks only: no actual B4/C2 execution, no borrowed parent CPU receipt, no native-size measurement. The parent's earlier 17,274,671-byte C2 component is PARENT_REPORTED only and is neither read nor substituted for this pack's future result.
