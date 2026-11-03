# PASSIVE_SENSOR_CAPTURE_V3：typed ownership / control provenance

这是 NEW source-only 外层版本，继承 B2 的 reset-binding revision 2，而非修改 B2。精确 class/module/function、参数、source SHA、定义行与闭包 qualname 见 [SOURCE_API_CONTRACT.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/SOURCE_API_CONTRACT.json>)；冻结 codec 的逐函数绑定见 [CODEC_SOURCE_PINS.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v3/CODEC_SOURCE_PINS.json>)。

## 字段语义先于 tensor shape

| 入口 | role | 源 axis / shape | ownership 与保留 |
|---|---|---|---|
| `FieldSnapshot.rows` | `ENV_ROWS_WITNESS` | 显式 axis 0 = 80 | caller 已有同 device int64 witness index；保留 W=1..8 行 |
| `FieldSnapshot.ids` | `ENV_IDS_FULL` | 无 env axis；原 1d K=0..80 | 整条 clone；实际 SDK 原 callback `.int()` 为 int32，绝非默认 long |
| `FieldSnapshot.mask` | `TERMINAL_BOOL_FULL` | axis 0；原 bool[80] | 全 80 clone；非 witness 第 79 行仍保留 |
| `FieldSnapshot.state` | 显式已知 per-env cache/episode 树 | 仅由调用点声明的 ENV_ROWS 叶子 | 不接原 IDs、bridge.pre 或任意未知 tensor；不按首维猜角色 |

565 的 `QUEUE_GROUP_FULL` role 存在，但 B3 不使用，不读取或对接 C2。

每个 owned envelope 保存选择前的真实 `original_dtype / original_shape / original_device / source_env_axis`、`retained_shape`、明确 row mapping、`source_clock`、`source_ref / source_pin_ref / source_field`；`source_pin_ref == source_ref`。原值不 cast。IDs 即使 K=80，也仍为 FULL IDs；mask 即使 shape[80]，也仍为 FULL mask。

row mapping 的证据级别固定为 `CALLER_DECLARED_INDEX_BINDING_NOT_READBACK`：Python witness IDs tuple 只是 caller 声明，未对 GPU index 做 `.cpu/.tolist` 回读。此声明不构成真实 index 内容校验。

## 每 control 的自然时序与 clock

`begin_control(index)` 仅建立 metadata context，顺序 index 从 0 开始。父调用者保留自己的那一次原 step 与 strict boundary，之后才 `end_control(...)`，传其已有原 post flags 与已有 80×35 END actor/raw35 buffer。适配器没有 step/obs/reset/getter/terminal-reduction 入口。

1. 原 400Hz / decimation 8 控制的原 scene-update sampling 在 physics substeps 4、8：MID=10ms、END=20ms，两个自然 100Hz slots，不是每 8 substeps 只采一次。
2. 每 slot 五通道 `base_ang_vel:3 / projected_gravity:3 / leg_pos:4 / leg_vel:4 / wheel_vel:2`，只保留原 feedback raw argument 的 clean16。
3. `normal_sample` 只接 `phase=scene_update / reset_depth=0 / is_original_100hz_slot=true`，MID physics_tick mod8=4，END tick>0 且 mod8=0。同 tick manager 再读只是原 cache 复用，不升级成新自然采样。
4. 保留原 clock 字段：`physics_tick / sim_time_us / feedback_tick / common_control_counter / phase / control_slot / reset_depth`。不更改 counter，不以 callback clock 重造 sample age。
5. terminal wrapper 在原 compute（含 bridge 已有 pre capture）返回后复制已有 `bridge.pre.term/trunc` 全80 与 `bridge.pre.s1` witness；仍在 reset 前。
6. reset wrapper 在原 callback 入口复制完整原 IDs 与 before state；原 reset 一次；其返回或抛出后记录实际 after / partial-after，恢复原 phase/depth，再将 owned IDs 交 ledger 一次。
7. end 只接父原 step 已返回的 full80 flags 与原 END 35 buffer；没有 actor 时明确 UNKNOWN，shape 错则 observer error，不切片、不填补。

atomic 关联使用 run/control index + term/reset event IDs + 原 clocks，不是按 nearest tick 拼接，不 retrojoin late termination。

## 保留上界和失败诚实性

- `ControlLedger` 只支持 64 或 128 controls；最多 128 packs / 1280 normal-channel records。每 control 的 10 normal、pre/reset/full80 flags/原完整 IDs 一起保留，不靠 independent last4 rings。
- debug first/last/max_events 只是额外的混合调试记录；其耗尽不会停止科学记录。无每 tick 文件写入、无 O(n²) tick 重写、无 PID signals。
- B3 另保留至多一个正在进行的 owned control。正常 end 后清空此引用；数据仍由 ledger 原子 pack 持有。该 pending control 只有固定 10 个 normal 槽、一个 pre、一个 reset、一个 post callback，不引入第二套长历史或 tensor clone。
- 原 reset `RAISED`：原 exception 对象原样传播，已有 clean16/pre/full IDs/before/实际 partial-after 仍可在 `incomplete_current_control` 取到。标 `INCOMPLETE / original_post_return=NOT_OBSERVED`，不调用 end 来制造 post flags，不重试 reset。
- end 已获 caller buffers 但验证失败：保留已经拥有的部分 post metadata，标 `CALLER_SUPPLIED_BUFFERS_END_NOT_CLOSED`；绝不将错误 shape actor 宣称有效。
- 自然没有 callback：codec `reset.callback_status=NOT_OBSERVED / ids=None`，且 B3 `original_reset_callbacks=0`。
- 原 callback 参数恰为 K=0：仍是 `OBSERVED` 的原 int dtype 空 IDs envelope，不改成无 callback。
- 原 callback 已发生但 IDs metadata 失败：原函数仍返回或抛出原对象；B3 provenance 明记 `original_reset_callbacks>0 / reset_observation=OBSERVED_METADATA_FAILED`，并把 pack 严格标 INCOMPLETE。codec 因未收到有效 IDs 而保留的默认 NOT_OBSERVED 不是自然无 callback 证据。
- duplicate 原 callback 不吞掉、不重放；各原调用一次。固定首个 owned event 保留，原 callback count、observer error 与 INCOMPLETE 记录重复，避免覆盖成伪完整包。

## 不作出的数据推断

- MID 其余19、MID full clean35、MID actor35、clean0：UNKNOWN，未重算。
- 原 raw35 已 noisy/delayed，未反解 clean35。
- noise 只来自原实际已用 cache draw / bias；不做 noisy-clean 事后减法，不额外取 RNG state / 随机数。
- lag selection 只取原 queue/cache 的 before/after、sample_tick、cur/out；不复制执行选择逻辑，不生成新 GPU mask。
- default joint pos / vel、joint order、scale 来自继承的原 source API/配置；不假定零默认速度，不推断 quaternion 字段次序。

## 导出及准入

回调和 control loop 内仅 detach/index-select/clone 形成 owned tensors，无 `.cpu/.tolist` 或 cast。仅在 outside-loop 对 already-owned tree 显式调用 publisher `codec.materialize(...)`，保持 typed dtype/shape/axis 与 bool/int 值。

`metadata_retention_complete` 只表示已保留该窗口的预期 metadata，不是 native 准入。固定 `native_enabled:false / exact:false / Gate1:UNKNOWN / stage2_go:false`。真实 Torch CPU、SDK/原 worker、untapped actor35 bitwise、原 RNG/call-count parity 都留给后续独立现场证据。
