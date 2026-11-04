# E3 reset identity 失败诊断与 B2 源级修正（SOURCE ONLY）

结论：**旧 gate 把实际安装的实例 reset wrapper 误按原 class descriptor 校验，是已确认的源级契约缺口；V2 现场实际 outer metadata 未打印，其具体身份仍为 UNKNOWN。** B2 只加入固定组合逐层核验和有界只读 metadata，不跳过 outer、不猜 live pin、不调用 reset/getter/RNG。`native_enabled:false`、`exact:false`；不是阶段1现场通过声明。

## 1. 现场事实，和源预测分开

已读 [实际 V2 closed receipt:62832–62837](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_CLOSED_20261103_210748/CLOSED_RESULT.json#L62832-L62837>)：

```text
install_passive_capture → preflight → verify_callable
ValueError: Function identity mismatch: RecoveryEnv._reset_idx
```

同一 [receipt:106–194](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_CLOSED_20261103_210748/CLOSED_RESULT.json#L106-L194>) 中 GO/READY/FINAL 缺失，`WORKER_ERROR` 存在，父 RC1；子 RC0 是既有 fast-close 的退出行为，不代表捕获成功。原 PID/锁均已 closed/released。现场 capture/counts 字段为 null，不写成实测0。错误只打印 expected qualname，没有 observed module/qualname/code filename/source SHA/closure，故实际最外层属于何者仍 UNKNOWN。

旧 [B1 preflight:170–173](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v1/passive_capture.py#L170-L173>) 直接将 `env._reset_idx` 与 first-MRO `RecoveryEnv._reset_idx` pin 比较。`inspect.unwrap` 对没有 `__wrapped__` 的已发布 MethodType closure 保留原状，因此合法实例包装也会失配。这解释源级 gate 缺口，不冒充现场 outer 的观测结果。

## 2. E3 原 constructor / reset 组合

原 entry [train_mod4v1_e3:82、153](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/train_mod4v1_e3.py#L82-L153>) 将 `RecoveryEnv as Mod4Env`，最终 `Mod4Env(cfg=cfg)`。环境构造逐层先 super：

1. [SpringPressureMod4Env:40–44](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/spring_pressure_training_env.py#L40-L44>) 安装 `_spring_pressure`。
2. [GasDampingMod4Env:6–11](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/gas_damping_training_env.py#L6-L11>) 安装 `_gas_damping`。
3. [ChassisPDMod4Env:8–14](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/chassis_pd_training_env.py#L8-L14>) 依次安装 `_chassis_com`、`_explicit_pd`。

源预测实际 installed outer→inner 为：

```text
ExplicitPDSDK.__init__.<locals>.reset_idx
  → ChassisCOMSDK.__init__.<locals>.reset_idx
    → GasDampingSDK.__init__.<locals>.reset_idx
      → SpringPressureSDK.__init__.<locals>.reset_idx
        → RecoveryEnv._reset_idx   # actual first MRO defining class descriptor
```

每个已发布 wrapper 都是 `original(ids); adapter.reset(ids)`，绑定 `types.MethodType(reset_idx, env)`，没有 `__wrapped__`，隐式返回 None。B2 保留其原行为，不把原 endpoint return 透传作为“修正”。四个 E3 已发布 source SHA：

| 原源 | source SHA256 |
|---|---|
| [ExplicitPD:20–22](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/explicit_pd_sdk_adapter.py#L20-L22>) | `e9995ecd802f26cae1061a9540efdea1b34ae143bdfc9c8619508c560b438ae3` |
| [ChassisCOM:39–41](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/chassis_com_pose_roundtrip_sdk_adapter.py#L39-L41>) | `32d554f4efa29a2cb7bc669d5067c03315d1cf55603269ea9a6041dc8244f6e1` |
| [GasDamping:34–37](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/gas_damping_sdk_adapter.py#L34-L37>) | `3b318b827329e22038a2abb89ba97827355bf4ac5e6211ebce697def714e1ea5` |
| [SpringPressure:28–32](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/spring_pressure_index_runtime.py#L28-L32>) | `4ea0a70293f09dda4d7fe862068c1460ea6acbb8db2accb7ea0fa31d9ccedc58` |

## 3. 不应加入白名单的疑似层

- [fresh guard:179–208](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/mod4v1_fresh_dr_guard.py#L179-L208>) 的 full-state context 临时替换 `env.reset` 而非 `_reset_idx`，该 worker 未进入此 context。
- [getter.capture_initial:157–161](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/actual_DR_memory_getter272.py#L157-L161>) 原样读取/缓存既有 DR，不包装 reset。
- [paired-pose installer:312–343](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_pose_cache_runtime_adapter_v3/pose_cache_runtime_adapter_v3.py#L312-L343>) 只替换 robot 的 pose 方法，不接触 env reset。
- [OriginalEpisodeBoundary:284–305](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py#L284-L305>) 没有 env 引用。
- [DecisionHistoryVec:37–44](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/frozen_history_policy.py#L37-L44>) 的确另有 reset wrapper，但当前 synthetic-zero worker 不构建该 policy；不得据此扩大 B2 fixed chain。
- [n80 allocation ctor:1–8](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/phase1_first_startup_failure_v1/worker_sources/parent/n80_gpu_capacity.py#L1-L8>) 只调整既有 cfg allocation 后调用原 constructor，返回同一 env；没有 reset/scene/term wrap。实际发布 SHA `ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc` 已 stdlib 只读复核。

## 4. B2 严格校验，而非 unwrap 放行

[B2 source_api:501–571](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/source_api.py#L501-L571>) 必须同时满足：

- installed `_reset_idx` 本身就是原 pinned raw MethodType；四层固定顺序，不允许未知/缺失/重复 outer。
- 每层 actual module/qualname/source SHA/line/live compiled bytecode/signature/default/freevars；sys.modules、function globals、class module binding 都一致，禁止 `__wrapped__` 跳过 outer。
- closure `original` 是同一 env 的下一层 bound method；`adapter` 是 env 内对应 `_explicit_pd/_chassis_com/_gas_damping/_spring_pressure` 的同一对象，adapter.env 同一 env，原 initialized memory fields 存在。
- 原 adapter local MRO、constructor/reset descriptor source/code 和 `__class__` closure 逐项验证，禁止替换 instance.reset。
- 终点必须恰好为实际 env MRO 第一个定义 `_reset_idx` 的 class descriptor 对象，且固定 source/code/声明 class cell 一致；仅有相同名字/字节码的 clone 也失配。

八角色分别从自身 constructor/import alias/MRO/source 生成固定 manifest；均 `SOURCE_CONFIRMED_LIVE_UNKNOWN`，不是 E3 的通用开放白名单。任一源证明缺失返回 UNKNOWN+空 layers，安装 gate 保持关闭。

[B2 diagnostic:374–490](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/source_api.py#L374-L490>) 只读实际 function metadata：reset 默认最多6节点、scene最多8函数、MRO最多16类；包括 observed module/qualname/code filename/SHA/line/freevars/same-env/adapter槽布尔值。无 tensor/state repr、无 SDK getter/RNG accessor、无 task 函数调用、无 tick 内写盘。preflight error 保留类别并附 `binding_diagnostic`；所有检查在 install setattr 前。

## 5. 剩余 E3 preflight 源矩阵（未现场执行）

| Gate | 源级已核实内容 | 现场状态 |
|---|---|---|
| env/MRO/clock | 原 entry RecoveryEnv；allocation alias 返回原实例；physics 2.5ms / control20ms / decimation8；原 SDK false backend-decimation 路径每8子步 scene.update | `UNKNOWN`，维持原 gate |
| sensor/delay/helper | 原 SensorCorruption/FeedbackDelay，原 helper/sys.modules/global feedback 绑定；所有类/函数固定 source pins | `UNKNOWN` |
| policy functions/default/params/scale | 原 feedback functions；五通道与16维；gyro .5、gravity1、qrel1、dqrel .1；actual default q/dq 由原 SDK减法，不假定 live zero | `UNKNOWN`，resolved joint_ids 的 live 表示亦待验 |
| scene.update | 原 config 中 [contact eager/integrated:10–11](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/original_run_manifest.json#L10-L11>) 均1；SOURCE outer→inner 为 Recovery.update → DelaySensor sampling → Mod4Env.integrated_update → Mod4Env.update_with_contact_capture → original SDK scene.update | 既有 closure search 找唯一 pinned sampling/self/global module，不直接要求 outer==sampling；源上未找到 reset 式同类误判。SDK terminal 源缺失，live UNKNOWN |
| termination.compute | 原 worker 在 capture 前按 alias `native_supermimic_bridge` 加载桥 SHA8211964c…，构造器把 active compute 设为原 bound `_termination_capture`；Recovery 原 term 位于桥 `_oldterm` 内 | SOURCE符合原 gate，actual module/class/descriptor/decorator/code 仍待 live；保留 @torch.no_grad 的既有 unwrap 验证 |
| SDK observations | 已读原 four functions，generic_io_descriptor 属既有 decorator；default position/velocity subtraction 出处明确 | 现场 SDK source/decorator对象/default asset/ids/dtype UNKNOWN；未新增 SDK import |
| clean100Hz | 原回调 tick%4，第4/8子步10/20ms各一次；raw参数是真 clean16，原缓存给 noise-used/lag queue | raw35 已 noisy/delayed；full clean35 mid/end及未暴露的局部 due/delayed 继续 UNKNOWN |

其余 E3 源链详见 [原 runtime:62–86](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/feedback_delay_runtime.py#L62-L86>)、[Mod4Env contact:78–124](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/mod4_env.py#L78-L124>)、[桥:84–96](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L84-L96>)、[V2 worker:98–138](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_worker_v2/worker_passive_interface_v1.py#L98-L138>)。未发现第二个源已确认的同类 identity gate 缺口；这不意味着剩余 native gate 已通过。

## 6. 实测证据分层

1. 新 stdlib **28项方法 PASS**：原21项 + 新7项，新增内含21个独立负例 subTests。四 wrapper 是固定已发布 SHA 的原 CODE compile→FunctionType→MethodType，不是手写玩具 wrapper；真实 constructor/reset descriptor code 只绑定、不执行。流守恒测试的 adapter.reset 明确 fake 且绕开 native preflight；证明原 code 组合调用一次/顺序/None return identity/异常原对象/queue/private RNG/global RNG/双slot/terminal pre-reset，非物理 DR。
2. [旧 actual TorchCPU+tap receipt:88–130](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_PASSIVE_TAP_CPU_V1.json#L88-L130>) 已读：原 Sensor+Delay TorchCPU、fake env、25 output bitwise /50 return identity、private/global RNG与queue一致；SDK/native preflight/actor35 equality false。它是 B1 历史执行，不是 B2 新执行。
3. 新 [只读源继承 audit](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_sensor_reset_identity_diagnosis_v1/SOURCE_EVIDENCE_AUDIT.json>) 实际 stdlib PASS：B1 seal+13成员未变；CPUfixture/fake runtime/hook spec bytes相同；8个 runtime defs、9个原 verification helper defs、原21测试class AST相同；public install/preflight 参数相同。故可沿用旧 runtime-only CPU观察范围，**B2 changed preflight 并未从旧 receipt 得到验证**。
4. [B2 最终 stdlib receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/STDLIB_FAKE_TEST_RECEIPT_v3.json>) 与 [B2 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v2/SOURCE_SEAL.json>) 是独立 NEW 交付。旧17/19 receipts 保留历史源 SHA，不充当 B2 final proof。

最终准入仍归父会：review → 原资源 bounded small-window actual binding+source diagnostics → bitwise actor35 equality 与 original call/getter/RNG/queue/terminal/reset证据。该子会话未执行 Native/SDK/GPU/SSH/训练，未触碰 PT/rawJSONL/canonical/锁/Git/旧封件；物理DR、H1、mothers、acceptance 不变。
