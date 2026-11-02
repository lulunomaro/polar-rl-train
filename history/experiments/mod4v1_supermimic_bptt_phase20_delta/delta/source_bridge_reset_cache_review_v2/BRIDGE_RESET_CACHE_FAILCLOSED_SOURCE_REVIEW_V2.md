# Bridge reset cache / quaternion / fail-closed 源审计 v2

**状态：新目录 source-only 候选，未部署、未启动训练。** 仅审计闭窗 producer 小元数据和限定 SDK/task Python 源，执行 stdlib CPU 反例。原 reward 审计 v1、既有/封版源、原 C 结算和已释放租约均保留。Office/ACL skills 与此 RL/SDK 源审计不匹配；使用 read/glob/grep、受限文本/AST/hash 和显式 Python `-S -B`，未加载无关 skill。

## 1. 结论先行与证据等级

1. **已观测**：原 H16 闭窗 E0/E2 分别 2520/2392 actual BPTT，有限窗口已全存；其余六角色均在原 gravity guard 抛 `AssertionError ('SDK quaternion convention', err)`，producer counts/FINAL/startup 为 null，实际等待 RC 为 0。**null 不是 producer 的 BPTT=0**；“guard 位于 learner 构造前，因此未更新”是由栈及源码时序得到的推断。
2. **已证实的源级遗漏**：已关联 PhysX 源的 root pose setter 更新 actor pose、使 root_state 缓存失效，却遗漏 projected gravity、heading 及若干 root-derived 缓存。getter 仅在 `buffer.timestamp < _sim_timestamp` 刷新。reset 写 pose 后同 tick 读取，具备 **root fresh / gravity stale** 的可执行反例；`update(0)` 在此源中只加零，不修复相等 timestamp。
3. **未证明的历史归因**：过去六 worker 的实际 data type/MRO/source SHA、same-tick timestamps、原始 quaternion/normalized world gravity/stream 同步收据尚缺。工厂/type-check import 及源级 PhysxCfg 不是实际 binding 收据。**旧 run 的 physical cache root cause 仍为 null**，不把小误差形态直接判成缓存已坐实，也不把 guard 名字直接判成 quaternion 顺序错误。
4. **已证实的 owner 假阴性链**：worker 原码确实写 WORKER_ERROR 后 `raise`；owner 原码却仅以 `rc != 0` 决定阻止待启动角色。RC=0 + WORKER_ERROR + FINAL=null 被当作非 original_error，后续继续调度。清理期间退出覆盖 pending 异常是一种可复现实例，但实际 app.close 实现尚未读取，具体 RC=0 机制保留 unknown。
5. 最小候选为 **已验证 binding 后、实例级 full-state writer 返回处，仅失效明确 8 个派生缓存 timestamp**，不改 quaternion、guard、原物理状态或 clock，不加 physics step/reset/observation compute。独立 owner receipt gate 必须保留，不能只靠修 worker 返回码。

### 闭窗小元数据

| 角色 | actual BPTT producer 值 | 原 guard error | waited RC | FINAL / WORKER_ERROR |
|---|---:|---:|---:|---|
| E0 | 2520 | 0.00021932624804321676（startup） | 0 | present / absent |
| E2 | 2392 | 0.0002193391410401091（startup） | 0 | present / absent |
| E3 | null | 1.0002192258834839 | 0 | null / present |
| W35 | null | 0.1558399349451065 | 0 | null / present |
| CURB_PROTECTED878 | null | 0.05059302598237991 | 0 | null / present |
| CURB_INDEPENDENT113 | null | 0.0506722591817379 | 0 | null / present |
| SLOPE135 | null | 0.05062456056475639 | 0 | null / present |
| SLOPE_INDEPENDENT50 | null | 0.05059302598237991 | 0 | null / present |

源：[CLOSED_RESULT:5–35](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/ACTUAL_SUPERMIMIC_EIGHT_V1_20261102_184527/CLOSED_RESULT.json#L5-L35>)（all waited/cost settled/leases released），[E0:444–479](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/ACTUAL_SUPERMIMIC_EIGHT_V1_20261102_184527/CLOSED_RESULT.json#L444-L479>)（passed_execution、target_reached=false、finite stop、complete save），[六失败:1254–1398](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/ACTUAL_SUPERMIMIC_EIGHT_V1_20261102_184527/CLOSED_RESULT.json#L1254-L1398>)；原 [E3 waited:6–9](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/ACTUAL_SUPERMIMIC_EIGHT_V1_20261102_184527/roles/E3/PARENT_WAITED_ACTUAL.json#L6-L9>) 明列 RC=0、FINAL=null、original_error=false。本目录 [闭窗 join](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bridge_reset_cache_review_v2/CLOSED_FAILURE_CHAIN_SOURCE_V2.json>) 保留全部八角色原值及独立候选分类，不回写 canonical。

## 2. Quaternion / getter 语义：保留原正确转换

- bridge [pack:87–94](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L87-L94>) clone 原 SDK root_state，将 `root[:,3:7]=root[:,[6,3,4,5]]`，即 xyzw→wxyz。其 [guard:133–136](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L133-L136>) 用 `(-state[1][:,2,:])` 与 raw projected_gravity_b 比较，阈值严格 `err < 1e-3`。
- learned bridge 几何 [geometry:11–27](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/geometry.py#L11-L27>) 归一化 wxyz quaternion，矩阵为 body→world。因此在 normalized world gravity=(0,0,-1) 的前提下，body gravity 是 **负最后一行**，不是负最后一列。真实 world gravity 方向也应在未来 receipt 中核实，而非跳过此条件。
- 已关联 backend [root_link_pose:616–630](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py#L616-L630>) 明确 xyzw；[root_link_quat:1132–1142](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py#L1132-L1142>) 是 actor-frame quaternion；[root_state:1815–1840](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py#L1815-L1840>) 拼 actor root pose + COM velocity。这种 pose/velocity 定义是原 SDK 语义，不能仅凭字段混合称为 COM 错误。
- **flat guard 通过不证明顺序**：xyzw identity=(0,0,0,1) 误当 wxyz 会得到绕 z 180°，gravity 仍相同；纯 yaw 也不区分两者。CPU 测试包含非平凡 pitch/roll、归一化和 q/-q。E0/E2 平地通过与六 non-flat/fall 失败的形态，足以提出缓存假设，不构成历史 root cause 的证明。

SDK 来源：[source fetch receipt:1–52](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/SDK_RESET_CACHE_BACKEND_SOURCE_V2.json#L1-L52>) 明列 bytes/SHA、top-level isaaclab_physx spec=null、actual previous worker backend=null。该 SDK factory 依实际 physics_manager 动态选择 backend：[backend_utils:82–95](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1/base_factory_v4/utils/backend_utils.py#L82-L95>)；任务 [PhysxCfg:1867](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/mod4_task.py#L1867>) 只能建立 source-expected backend。

## 3. 已定位的同 tick cache 失效缺口

### 3.1 精确写入与读取链

已抓 backend [write_root_link_pose_to_sim_index:445–503](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation.py#L445-L503>)：

```python
# source essentials, not a deployed patch
wp.launch(..., outputs=[self.data.root_link_pose_w], ...)
self.data._root_link_state_w.timestamp = -1.0
self.data._root_state_w.timestamp = -1.0
# invalidates several body pose/state and task-space caches, but NOT g/heading/body velocities
self.root_view.set_root_transforms(self.data._root_link_pose_w.data.view(wp.float32), indices=env_ids)
```

[write_root_state_to_sim:4799–4815](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation.py#L4799-L4815>) 依次调用上述 actor pose writer 与 COM velocity writer；后者 [704–733](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation.py#L704-L733>) 只使 root state/root COM state 等相应缓冲失效，并未补 g/heading。

raw g [995–1009](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py#L995-L1009>)：

```python
if self._projected_gravity_b.timestamp < self._sim_timestamp:
    wp.launch(shared_kernels.quat_apply_inverse_1D_kernel,
              inputs=[self.GRAVITY_VEC_W, self.root_link_quat_w], ...)
    self._projected_gravity_b.timestamp = self._sim_timestamp
```

[update:121–131](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py#L121-L131>) 是 `_sim_timestamp += dt`，并读取 joint_acc。对 timestamp 相等的缓存，`update(0)` 不触发严格 `<`。调用正 dt 虚构时间、加物理 warm-up step/reset 都不是最小 cache 修复。

base reset [423–437](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/base/manager_based_env.py#L423-L437>) 是 `_reset_idx → scene.write_data_to_sim → sim.forward → original observation_manager.compute(update_history=True)`，中间未调用 scene.update；原步骤内 [RL step:231–273](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py#L231-L273>) 则 physics/scene update 后 term→reward→reset→command→obs，同一步 reset 后也有同 tick 读缓存的可能。这里只证明本文件的调用顺序；sim.forward 内部及 actual backend stamp 的实际行为仍以绑定 receipt 验证。

### 3.2 为什么是六角色先暴露

E3 [recovery reset:53–62](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/e3_recovery_runtime_v1.py#L53-L62>) 在 super reset 后再写 declared fall 的 joint/root state；W35 [reset:55–80](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/reset208_v3.py#L55-L80>) 写 SciPy xyzw tangent-frame pose 与零 COM velocity；CURB878 [full reset:46–73](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/CURB_PROTECTED878/runtime/isaac/mod4/curb20_entry_v3_full_pose_reset.py#L46-L73>) 同样写 tangent-frame root。非平姿态改变会放大 stale flat gravity 的差异；CPU `asin(0.050593...)` 小倾角和 π/2 fall 的量级反例与观测相容，**不是对每个旧 worker 姿态的重构**。其余三个 E1 的 actual reset/MRO/绑定边界要由各自 source/runtime receipt 核实，不用 878 的一条路径替代四角色实证。

### 3.3 最小实例候选及覆盖边界

新 [候选模块](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bridge_reset_cache_review_v2/reset_cache_and_failclosed_candidates_v2.py>) 中 `install_root_state_cache_invalidation_candidate(robot, *, live_binding_verified=False)` 默认为关闭。在 actual binding/source SHA 先验核实后，仅包该 robot 实例已调用的 full-state writer：原方法返回，原物理写入完成，然后把以下 8 个 buffer timestamp 设为 -1.0：

```text
_projected_gravity_b, _heading_w,
_root_link_vel_w, _root_com_pose_w,
_root_link_lin_vel_b, _root_link_ang_vel_b,
_root_com_lin_vel_b, _root_com_ang_vel_b
```

依赖来源为 [root pose/velocity 派生:633–682](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py#L633-L682>) 与 [g/heading/body velocities:995–1109](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py#L995-L1109>)。AST 测试确认这 8 个字段全未被当前 pose setter timestamp 赋值覆盖。候选先校验全部字段、data backend/module/clock，缺失即停，不静默跳过；不扫描所有私有字段，不替换数组或 ProxyArray，不改 `_sim_timestamp`。

**边界选择**：安装在 build_env 后、原 ONE explicit fresh reset 之前；callback 在 writer 返回处而不是 bridge guard 后，也不只在 `_reset_idx` 尾部。这样同 reset 后续 command/原 observation 第一次读即可刷新，E3 super reset 后最后一次 fall write 也覆盖。若只在 guard 前刷新，原 observation 的原始输入可能早已陈旧；若只包 `_reset_idx` 尾部，中间 command getter 仍可能先读到旧 heading。

**限制**：此 adapter 不是全面 SDK 修复。其他 pose/velocity write API 若绕过 full-state writer，就不在其覆盖内；各角色实际调用路径需先证实。单独 `write_root_com_velocity`、upstream body COM 缓冲、CUDA/Warp stream 依赖或不同 backend 的机制也需分别验证。本候选触发全 batch lazy 缓冲重算，因原 timestamp 本就是全 batch；不声称 per-env timestamp。通用 SDK 上游修复应系统覆盖各 write API 的完整依赖闭包，另立版本评审。

### 3.4 保留原 sensor delay/noise/RNG

原任务 [SensorDelayline:520–544](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/mod4_task.py#L520-L544>) 的 gravity 进入延迟线；[actor slots:1211–1217](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/mod4_task.py#L1211-L1217>) 中 command3/height1/gyro3 后 gravity 为 7:10，另有 [-.05,.05] noise。**不把 actor gravity 改成 raw truth，不要求 actor gravity 等于 SDK raw g，不重跑 observation_manager.compute**。未来验证要分别检查 raw state/raw g 一致性，以及原 delay/noise/history 调用次数和 RNG 流；CPU 无噪 synthetic actor fixture 只证明时序反例，不代表 livecfg。

## 4. Worker / owner fail-closed：与 cache 修复独立

原 [worker:51–68](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/worker_supermimic_bptt.py#L51-L68>) 的显式 reset、teacher/actor、bridge.init_state/guard 在 learner 构造之前。失败六角色由此尚未进入 learner 更新；但不要把 producer null count 改成测量 0。

原 [worker:79–85](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/worker_supermimic_bptt.py#L79-L85>)：

```python
except BaseException:
    ... put(WORKER_ERROR, ...); raise
finally:
    if bridge is not None: bridge.close()
    ... env.close()
    if ns is not None: ns['app'].close(); put(APP_CLOSED, ...)
```

所以“worker 直接吞异常”不成立。Python `finally: raise SystemExit(0)` 或原生立即退出覆盖 pending failure 可造成错误写出但 RC=0；本目录有前者纯 CPU 反例。实际 SimulationApp.close 代码未读取；[isaacsim package:149–150,167–190](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/isaacsim/package_init.py#L149-L190>) 只给扩展路径和 API 暴露规则，不能当 close 实现证据。

候选 `preserve_primary_and_close(primary_callable, cleanups)` 将主异常转成持久 nonzero rc，依次尝试全部 bridge/env/app 清理，记录每个 cleanup 事件，最后一次 exit；cleanup 的 SystemExit(0/None) 不覆盖旧 failure。原生 os._exit/fatal exit不受 Python 捕获，故下一层 owner receipt gate 仍必需。

原 [shared owner:64–78](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/supermimic_original_owner_shared_v2.py#L64-L78>) 读取 FINAL 后仅 `original_error=rc!=0; if rc!=0: blocked=True`，未纳入 WORKER_ERROR/FINAL=null；[80–95](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/supermimic_original_owner_shared_v2.py#L80-L95>) 仍等待已启动子进程并结算。新 `terminal_receipt_decision(...)` 独立检查：

- raw RC 非零，或 WORKER_ERROR 存在，或 FINAL 缺失/格式错，或角色/pass/count/complete-save receipt 异常 → `effective_error=True, block_pending=True`。
- 只阻止尚待启动的任务；所有已启动自有 children 仍逐一 wait/清理/结算。保留 raw RC，不回写旧 account/canonical。
- 有限窗口 target_reached=false 本身不作错误：闭窗 E0/E2 仍保留 2520/2392 execution 和 full-save 收据；不改称 3000 达标或 skill 成功。
- 此 CPU gate 只检查小文本 schema/receipt，不打开 checkpoint 验真；父代理负责模型完整性验证。本目录没有模型读取。

在八份真实小 waited/FINAL/error 元数据上，候选恰将六失败列入 block，E0/E2 保留非错误。测试另覆盖“FINAL 声称成功但仍有 WORKER_ERROR”、错误 role/count/save、nonzero RC、finite partial save。

## 5. 下一窗口、unknown 和禁止混入项

完整关闭的 [预检协议](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bridge_reset_cache_review_v2/RESET_CACHE_MINIMAL_CANDIDATE_PROTOCOL_V2.json>) 的顺序为：

1. 先独立 owner fail-closed receipt gate，后续任何错误先阻止 pending；原清理/全等待/结算职责不减少。
2. actual backend/type/MRO/source SHA、normalized world gravity、raw quaternion norm/order、private timestamps、流依赖 receipt；未知则停，不应用猜测 patch。
3. 在未来新版本中安装已审候选，执行 **原单次 reset**，只在原观察之后读取 same-tick raw clone 对照；不加第二次 reset、extra physics/warm-up action、第二次 obs/history/noise/RNG。
4. 原 guard 保持 1e-3；若仍失败，保留详细错误，不通过降阈值/换 quat order/额外 action 擦掉。preflight 位于第一动作/learner 构造前，不是训练提升试验。
5. C113 原 after-reset command-binding 缺口与缓存分开：原六失败中 C113 也在首动作前停，因此该 gap 未形成实际训练结果。其父代理另立候选；本目录不部署、不混入 reward/DR/physics 变化。E0/S50 binary predicate 缺口仍 null。

| unknown | 影响与最小后续证据 |
|---|---|
| 过去真实 backend binding / source SHA | 决定当前源级 cache 遗漏能否解释历史 worker；不能由 top factory import 代替 |
| 过去 same-tick root/g timestamps、原 pose、world gravity、stream | 决定 root fresh / g stale、异步读或其他原因的归因 |
| TimestampedBufferWarp 精确实现与 shared kernels | 当前 data 导入 Warp buffer，而已抓通用 timestamped_buffer.py 是 Torch 版本；无需导入 SDK，补准确关联源即可加强证据 |
| SimulationApp.close 实际实现 | RC=0 的具体 pending-exception masking 机制；不影响已证明 owner receipt gate 缺口 |
| 所有六角色实际 reset 写 API / wrapper MRO | 防止仅实例 full-state adapter 漏过其他 writer；尤其不可用 878 路径代替四 E1 实证 |
| runtime guard / task acceptance | 本目录仅 CPU/source，不声称物理验证通过、90% 或任务通过率提升 |

## 6. 测试、产物与复现

[CPU results](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bridge_reset_cache_review_v2/CPU_TEST_RESULTS_V2.json>)：当前 **49/49 PASS，0 failures / 0 errors**。覆盖 quaternion、flat-order 假阳性、fresh pose/stale g、strict timestamp/update(0)、上游闭包、late guard repair 留下旧 actor 输入、原单 obs/RNG 次数、精确 8 字段/对象/clock 不变、源码 AST、Python 清理异常覆盖、候选错误保留、真实八角色 RC/error/FINAL。测试从最初 36/36 扩到 49/49，未修改被审源或断言阈值。

```powershell
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' -S -B '.\build_reset_review_v2.py'
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' -S -B '.\test_reset_cache_and_failclosed_v2.py'
```

工作目录为本新目录；以上只读取限定 text/JSON，写本新目录；不加载被审 task/SDK/torch。全部输入及最终 SHA 见 [输入清单](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bridge_reset_cache_review_v2/AUDIT_INPUTS_SHA256_V2.json>) 和封存时生成的 deliverables manifest。未进行 SSH/SDK/GPU/PT/raw/JSONL/C/GO/锁/Git 操作；未执行任何训练、动作、物理步；未读取或复制旧 large raw/模型。
