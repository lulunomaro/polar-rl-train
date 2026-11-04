# Phase1 actuation passive capture v1 — SOURCE / fake only

状态：`SOURCE_PASSIVE_OBSERVER_CONTRACT`；`actual_sdk_pass=false`、`Gate1=UNKNOWN`、`exact=false`。本目录是新的 lineage；既有 state/context 分区封件的9个成员及 seal 全部只读复验，不热改旧 xi、checkpoint、NNnorm、physics 或 trainer。

Catalog：本会话仅 Office / Windows ACL，均不匹配 RL 入口；使用 FS/CLI 和 Python314 stdlib。没有 SSH、SDK/native/GPU/PT、模型/replay/rawJSONL、canonical 预算、运行锁、Git、stager 或训练动作。

## 小而稳定的 API

[actuation_tap.py](<actuation_tap.py>) 只 import `functools`：

```python
from actuation_tap import (
    install_actuation_tap, snapshot_static, queue_snapshot,
    validate_apply_window, validate_reset_edge, validate_static_snapshot,
    CaptureUnknown, CaptureViolation,
)
# 未来由既有 driver 在原 adapter 已装配后组合；本次没有执行这段 native 入口。
tap = install_actuation_tap(existing_env, capacity=8192)
# 不调用 step/reset/RNG/模型；只让原 driver 原有调用自然经过。
events = tap.drain()       # callback 外；只取内存，不做磁盘/JSON/CPU 转换
static = tap.snapshot_static()
status = tap.status()
restore = tap.close()      # 可重复；有 later-wrapper 冲突会持续返回 restored=false
```

- `drain()` 将事件按 enter sequence 排列，不调用 getter / SDK / 模型。需要 JSON 或 stdlib 离线验证时，由调用方在 loop 外物化已拥有的 Tensor 快照；observer 本身没有 `cpu()` / `tolist()` / 序列化路径。
- `validate_apply_window(events, start_tick, expected_episode, status=None)`：输入 builtin 离线快照，一次 reset-free 8-tick 窗口；`expected_episode={"legs":[...],"wheels":[...]}`。返回 queue＋原 writer **argument** 合约，不返回 physical admission。
- `validate_reset_edge(previous_post, next_pre)`：仅用于同 group 相邻自然观测之间的 reset 边缘；检查 selected episode +1、valid/issue 清空、last_apply 全局钟不重置、unselected 全字段不变。reset 的准确 tick、真实 neutral readback 仍 UNKNOWN；不从未观察的中间过程拼造 reset receipt。
- `validate_static_snapshot(snapshot)`：检查 motor 4＋2 现存内存、white source 不变量 `step_scale==1`；数据缺件为 `CaptureUnknown`，观察到矛盾为 `CaptureViolation`。没有 physical readback 升格通道。
- `status()` 包含自然调用 counts、drop/error、missing hook、恢复冲突及长期 `actual_sdk_pass=false/exact=false`。安装方法或文件存在都不等于已观察到自然调用。

## 精确 hook 清单与 B 的组合边界

只包装已有对象上的以下入口，所有原调用恰好一次，原参数对象照传，返回对象 identity 不变；原异常对象原样重抛。观察失败只记录 UNKNOWN，不替换原异常或补调原函数。

| hook | 源含义 | observer 读取 |
|---|---|---|
| `adapter.queue.submit(key,x,tick)` | 原 processed target issue | 原 args、pre/post 12个 queue 字段、已有 static 内存 |
| `adapter.queue.apply(key,tick)` | 真物理 apply tick 入口 | 原 tick、pre/post 字段、原返回 selected target 的拥有快照 |
| `adapter.terms[group].process_actions(actions)` | 原 policy issue 关联 | 原 action args；不重做 scale、CAD 或处理动作 |
| `adapter.terms[group].apply_actions()` | 关联原 apply 与下游 writer | 原调用上下文；不改变 `_processed_actions` |
| 已有 asset `set_joint_position_target/velocity_target` | 原 target 写入入口 | 原 args/kwargs，包含 target/joint_ids；无新写入和 readback |

**不 wrap** `env._reset_idx`、`term.reset`、`queue.reset`、termination 或任何 sensor 入口。B 可独占 reset/termination，先装 B 或先装本 tap 都保持其 identity。若另一组件确实包装同一个 action process/apply/writer 方法，要求反向拆卸 wrapper；本 tap 遇到 later wrapper 不覆盖它，报告 conflict。单线程控制回调合约，不宣称并发线程安装/拆卸可交换。

安装读取 adapter 存储的 `terms`，不额外 `action_manager.get_term()`；状态读取用 instance `__dict__`，不触发 lazy property/SDK getter。目标 writer 的外部 SDK 方法定义未在本任务执行或活绑定验证；不存在则 missing hook UNKNOWN，存在但无自然调用也不算 binding 证明。

## 已审核真实 source 与时钟

固定 [SOURCE_PINS.json](<SOURCE_PINS.json>) 覆盖8角色共182个 source paths，包含原 entry/import 链与 actuation/static 组件；[source_pins.py](<source_pins.py>) 仅在 loop 外对固定 allowlist 做 bytes SHA256，绝不 import/执行原模块。

代表性的 W35 活继承源：

- [action_delay_training_env.py:6–18](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/action_delay_training_env.py#L6-L18>) 构造已有 `env._physics_action_delay`，`collect=False`。
- [action_delay_sdk_adapter.py:35–50](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/action_delay_sdk_adapter.py#L35-L50>)：issue=`env._sim_step_counter`；apply=`counter-1`，原 integration 前；原 adapter 自己执行的 target 检查保持原样，tap 不再取一次 data/getter。
- [action_delay_physics_queue.py:10–78](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/action_delay_physics_queue.py#L10-L78>)：`lag_steps, episode, pending, pending_valid, issued_tick, due_tick, applied, applied_valid, applied_issue_tick, first_apply_tick, last_submit_tick, last_apply_tick`。

`physics=2500us`，`control=20000us`，一个 control 原8个 apply tick。腿 processed targets 为4维 rad，轮为2维 rad/s，不是 torque。requested lag ∈ {0,1,2} physics ticks → {0,2500,5000}us。

- `first_transition_latency_us=(first_apply_tick-applied_issue_tick)*2500`
- `held_command_age_us=(current_apply_tick-applied_issue_tick)*2500`

两者不同：第二 control 的 lag=2 在新 target 尚未 due 前仍持有旧 target，首 latency 仍5000us，而 held age 可以20000us。validator 检查每 group 8个自然 apply、due=issue+lag、valid transition、pre/post queue、selected target 与原 writer 参数；missing/重复/跨 episode 的窗口保持 UNKNOWN，不从50Hz端点补样。

## static snapshot：内存来源与真实 readback 分离

[已审核 mild_dr.py:57–93,115–118](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/mild_dr.py#L57-L118>)：

- `env._mild_dr.factor`：episode mass/inertia factor；`mu/nominal/reset_count/output`：原存储内存，不是 PhysX getter readback。
- `env._explicit_pd.legs/wheels.episode_scale`：原4＋2 motor gain；`step_scale`：原属性，white profile source auditor 要求恒1。缺属性或 descriptor 不主动求值，记 UNKNOWN。
- 原 [ExplicitPDSDK:9–18](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/explicit_pd_sdk_adapter.py#L9-L18>) 已存 `legs/wheels/component` references；tap 不从 scene 再查 actuator，不调用 coefficients/audit。
- `_explicit_pd.component.factor/episode`、`_chassis_com.component.delta_m/episode`、`_spring_pressure/_gas_damping.component.factor/episode`：源里现存的字段才 snapshot。COM 是 m；各 gain/stiffness/damping factor 为 dimensionless，绝不冒充实际力、力矩、质量、摩擦或 COM 的物理 readback。

不调用 `state_dict()`，因为它会读 RNG state；不碰任何 generator、RNG 或 reset；不调静态 auditor，因为 auditor 内部含 SDK getters。`physical_readback` 字段始终显式 UNKNOWN。

快照只复制已存在内存，builtin 容器做拥有拷贝；未来已有 `torch.Tensor` 只 `detach().clone()` 保留原 device，暂未实际执行。clone 会增加内存/计算开销，本 fake 测试不证明 native 时序零扰动或 GPU 时延。opaque/Warp/descriptor 值保持 UNKNOWN；不为凑数读取 SDK。没有 extra action/model/reset/step/noise draw，不等于已证明所有 physical observer-effect 条件。

## tests / receipts / freeze

[测试](<test_actuation_tap.py>) 为 stdlib 确定性 fake，覆盖9种 lag pair、2env partial reset、8 callbacks、第二 control held age、args/kwargs 与 return identity、原异常 identity、observer 故障、无 tick I/O、快照防 alias、methods 完整恢复、later-wrapper conflict、B组合两顺序、buffer overflow 硬 UNKNOWN、source pins 和旧封件不变。

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B 'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_actuation_capture_v1\test_actuation_tap.py'
```

[SOURCE_RECEIPT.json](<SOURCE_RECEIPT.json>) 与 [FAKE_TEST_LOG.txt](<FAKE_TEST_LOG.txt>) 仅记录 SOURCE/fake 合约。`--receipt` 首次生成后即停写。 [SOURCE_SEAL.json](<SOURCE_SEAL.json>) 由 [seal_source.py](<seal_source.py>) 内容寻址冻结，后续运行只读复验；不是 ACL 锁或 actual SDK admission。

Gate1 仍需现场自然调用 source/class/binding receipts、完整 queues 和 writer arguments、原有物理 readback 及 observer-effect 证据。sensor MID/END/noise-used 由独立 B tap 采集；本包不补造这些数据。physics400-k2000-d3/.0025/50–100/D0D7/H1/mothers/原接受均不改；阶段2 absent。
