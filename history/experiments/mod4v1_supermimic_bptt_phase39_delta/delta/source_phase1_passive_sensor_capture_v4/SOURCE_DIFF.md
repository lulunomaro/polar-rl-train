# B3 → NEW V4 strict dependency API diff

## 生产组件范围

|组件|变更|
|---|---|
|[dependency_contract.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/dependency_contract.py>)|仅修改 preinstall expected pins 完整性与字面值类型检查；新 receipt kind/revision 明确区分 guard 版本|
|[passive_capture.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/passive_capture.py>)|37157 bytes，SHA256 `ddead70de7cb1e01acc79899320c0aaadd9c217cd7ba35e9e9f4a00f03c54745`，与 B3 原字节相同|
|[field_snapshot.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/field_snapshot.py>)|3327 bytes，SHA256 `ef4d1895e06087db023d55aa58203bd5b58f915fa71f65ade541e8ae588a61d4`，与 B3 原字节相同|
|[source_api.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/source_api.py>)|31456 bytes，SHA256 `a334766d6a9ca88d02d682e73d70a15e9098f1e77d1aa7a45e6d0154a4b73b62`，与 B3/B2 原字节相同|
|[CODEC_SOURCE_PINS.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/CODEC_SOURCE_PINS.json>)|原 19153 bytes / `5cd6c770c7f3541308201389f721b43f9e7c681199443c9a2f80d2f80347e452`，复制不改，不重新发布 codec|

[unified patch](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/SOURCE_DIFF.patch>) 仅涵盖这一生产文件；这是审阅 diff，没有应用到任何旧目录。

## API / schema

```python
verify_typed_dependency(snapshot, ledger, *, dependency_pins=None)
```

参数签名不变。`dependency_pins` 的 authority 收窄为完整、精确类型相同的 fixed publication compatibility input；empty/missing/extra/altered override 均失败。

- 新 Source revision：4。
- 新 binding inspection kind：`V4_TYPED_SOURCE_BINDING_INSPECTION_V1`。
- 原 capture schema/report kind：`PASSIVE_SENSOR_CAPTURE_V3`，未改。
- 原 independent codec publication/layout：未改。
- 原 B2 source API lineage revision：2，未改；原四层 reset/MRO 检查保持。
- 旧 6 wrappers、字段 dtype/shape/layout、100 Hz 两 slots、ledger、RNG、queue mutation、原返回/异常和原 DR/H1/mothers/acceptance 源码均未编辑。本任务只用同字节证明行为组件保留，不声称重新获得现场行为或 bitwise actor35 证据。

新测试仅为 11 项 own stdlib preinstall tests，不复制或重跑原 B3 30 控制行为套件。Source/numerical/native 边界见 [README](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v4/README.md>)。
