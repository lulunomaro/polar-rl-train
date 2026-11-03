# Unparented writer 独立 SOURCE 审计 v1

## 结论

**当前证据指向 C1 的 writer 元数据域/时钟过宽；没有证据证明 PhysicsActionQueue 真正 apply(-1)。实际 seq0 是否气簧写入仍为 UNKNOWN。**

本目录只交 SOURCE 审计、自己的小型顺序 toy 与 NEW C2 最小规范，不交 C2 实现、不重跑 Native。技能目录只有 Office/ACL，无匹配 RL/source 审计技能；使用 read/glob/grep 与获准 Python314 `-B` stdlib/AST。A194 的 C2 目录独立，未触及。

结果见 [SOURCE_AUDIT.json](<SOURCE_AUDIT.json>)：8 角色自己的 entry→import→local MRO、17 个精确函数 pin、E3 本地直接 target setter 全量 AST inventory 已通过。`native_enabled:false`、`exact:false`、actual gate1 UNKNOWN / stage2_GO false 保持。该 JSON 是本次 SOURCE 检查结果，不是 installed SDK binding 或 actor/queue 数值 receipt。

## 1. actual 小聚合证明到哪里

唯一读取的 actual 数据是 [允许的小聚合:55–134](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_V4_A2_ACTUAL_QUEUE_SCALAR_DIAGNOSTIC_V1.json#L55-L134>)，7898 bytes，SHA256 `b9a83cb124b5d202dfaaf7e10420eb8e447f5111fa34676c630ebb3762c21c07`。未打开其指向的 actual whole FINAL、trace、PT 或 canonical 对象。

实际导出的失败点：control index=0、local index=0、`seq=0, kind=target_write, group=legs, tick=-1`，tick 为 Python int；原 pure 在 `integer(e.tick,0)` 抛 `ValueError: typed integer/range`。对应 [pure integer:54–56](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L54-L56>) / [actuation_component:365–412](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L365-L412>)。本地 pure SHA 与小聚合 expected SHA 同为 `2b4ae157a54ea59711556cb8dc02c18151db54afc5b5d0dcff95bc0c5a86e979`。

| 项目 | SOURCE 确认/推导 | actual 已直接导出 |
|---|---|---|
| seq0 在回调入口先分配 | C1 先分配 seq；初始 context 空，只有 term_apply 入栈 | 只导出 seq0 / target_write |
| 此时没有先前 tapped term_apply 父 | 条件于此 C1 正常安装/绑定及原上下文规则，成立 | parent 字段未导出，非直接实测字段 |
| 此时 counter=0 | 按 C1 target_write 的 `counter-1` 规则，由 typed tick=-1 推导 | counter 未直接导出 |
| 真正 queue.apply(-1) | 本记录不支持；事件 kind 是 target_write | 没有 queue.apply 实参证据 |
| seq0 是气簧 callback | 有可达注册的候选路径；身份仍 UNKNOWN | 无 caller / joint_ids / target width |

不得把“由当前 source 规则推导”改写成“实际字段已捕获”。control0 本身也不证明全局 counter0；这里的零来自 C1 已审计公式与实际 typed -1 的组合。

## 2. C1 为什么容易误标

[C1 安装:85–110](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_capture_v1/actuation_tap.py#L85-L110>) 以方法名选择同 asset 的 position/velocity setter，并按当时 term 的 group 固定写入 `target_write`；没有按原 joint_ids 或 caller 分类。同 robot 的 gas position setter 调用也会落入该 position hook；这不证明实际 seq0 就是 gas。

[C1 包装:143–181](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_capture_v1/actuation_tap.py#L143-L181>)：149 入口预留 seq；155–156 对所有 target_write 与 term_apply 统一记 counter-1；162 读取当前 term parent；164 才对 term_apply push；166 原函数一次；181 finally pop。事件是完成时 append，故完成列表顺序不等于 seq 入口顺序。

原 [pure:379–381](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_evidence_verifier_v1/capture_evidence_verifier_v1.py#L379-L381>) 在 kind 分组前对每一事件要求非负 tick，所以本失败甚至早于真实 queue apply 链检查。**处理方向是区分事件域，而不是放宽真实 queue tick。**

## 3. 气簧路径：配置注册与原 step，而不是注释

1. [E3 entry:134–153](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/train_mod4v1_e3.py#L134-L153>) 构造 Mod4EnvCfg，调用 recovery/fresh configure，再构造原 RecoveryEnv。相关 configure 只处理已查的 reward/term/spawn/closure，不移除 gas event。
2. [EventCfg:1630–1634](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/mod4_task.py#L1630-L1634>) 在类体直接注册 `skills.gas_spring_preload`, `mode='step'`，params 用 GAS_JOINTS 和 contract 的 target_position_m；[Mod4EnvCfg:1837–1847](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/mod4_task.py#L1837-L1847>) 接入 EventCfg。
3. [Mod4Env.step:141–147](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/mod4_env.py#L141-L147>) 在 available_modes 包含 step 时，先 `event_manager.apply(mode='step',dt=self.step_dt)`，再 `super().step(action)`。实际类名是 Mod4Env，没有本地 StepEventEnv 类；不以别名替代证据。
4. [gas_spring_preload:452–474](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/skills_isaac.py#L452-L474>) 取同一个 `env.scene['robot']`，缓存/解析配置 joint_names 与 targets，原自然调用 `set_joint_position_target(...,joint_ids=ids)`。这条调用不通过 D4 queue。
5. [SDK step source:192–229](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py#L192-L229>)：process_action 在 193；非 backend-decimated 循环每轮 215 先 counter++，217 再 apply_action，之后 scene write/sim step/update。
6. [D4 adapter:14–46](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/action_delay_sdk_adapter.py#L14-L46>) 要求 dt=.0025、control=.02、decimation=8，明确禁止 backend handles-decimation。process 原函数后 submit 用 counter；apply 用 counter-1 → queue.apply → 原 apply。因此首次物理 apply counter=1 对应 queue tick0，而前置 event 的 counter0 从来不是 apply tick-1。

若原 EventManager 按此注册实际 dispatch，则 gas writer 的 SOURCE 路径是在 process/counter++/term_apply 之前发生。EventManager / ActionManager / SDK joint action / articulation setter 实现未在已给的 source 中找到，所以实际 dispatch、writer 内部 buffer mutation、live selector 和此次 seq0 caller 均仍 UNKNOWN。这里没有把 SDK source snapshot 当作本次 installed bitwise binding。

## 4. 分清所有可见 writer 路径与缺源边界

| 路径 | SOURCE 所见自然时钟/父关系 | 本次身份/资格 |
|---|---|---|
| 已注册 step gas preload | Mod4Env pre-SDK step，natural counter；无 D4 term parent | 配置及调用点确认，实际 seq0 身份 UNKNOWN |
| legs4 term application | ActionsCfg 位置项 + D4 term_apply→queue.apply→原 SDK apply；counter-1 属真实 apply 区间 | SDK writer 具体实现/本次原实参仍需 live binding |
| wheels2 term application | ActionsCfg 速度项 + 同上物理链 | 同上，不按 setter 名凭空证明完整性 |
| 其他同 asset setter、SDK reset/default/内部二次 setter | 外部 SDK 源缺失；若 tap 生效期间自然出现，按原 counter/参数完整保留 | UNKNOWN，不预判不存在或自动承认为腿 |
| reset/恢复 placement 的 state 写入 | 可见源码是 joint/root **state** setter；不是本 hook 的 target setter | 不把 state write 强行纳入 target 队列 |
| 单独 probe 的三个 target setter | [probe_mimic:87–117](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/probe_mimic.py#L87-L117>) 在 main guard 内另造 Articulation/Sim，非 E3 entry 注册路径 | 排除为本 entry 的已证可达直接调用；不猜实际 caller |

E3 目录所有 Python 的直接 AST setter call 仅 4 个：gas 474，以及 standalone probe 114/115/116。动态 SDK 调用及未给出的 module 不在该穷举范围。DR spring/gas damping/explicit PD 可见 apply 写的是原物理参数，未发现把它们注册为额外 target setter 的源码证据。

legs 的 [LEG_ORDER / WHEEL_ORDER / GAS_JOINTS:114–117](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/mod4_task.py#L114-L117>) 与 [ActionsCfg:1284–1293](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/mod4_task.py#L1284-L1293>) 是不同配置来源。本次未打开 contract 数据或实际 joint_ids，故不宣称实际 selector 的数值、相等/交集/不相交，也不以 target 宽度单独判组。

## 5. 八角色 MRO 与控制顺序

自己的 [source_audit.py](<source_audit.py>) 从每个角色自己的 entry ImportFrom alias 和 ClassDef base 独立递归解析 MRO，然后才交叉核对旧 B2 固定 pin；没有仅复制旧 manifest 结论。8 角色每个 entry/MRO 文件的 SHA 都单独核对。

- E0：ChassisPD→GasDamping→SpringPressure→ActionDelay→DelaySensor→Mod4Env。
- E2：在上述前加 E2H1FlatEnv，自己的 step 27–30。
- E3：加 RecoveryEnv，自己的 step 63–66。
- W35：RetentionLearning→E1ResetEvidenceLearning→E1TerrainLearning→E1ChassisTerrain→上述公共链；分别来自该角色 v3 文件。
- 两 curb / 两 slope：各自己的 retention/evidence/terrain 源链→上述公共链。

所有自定义 step 都只出现一次 super.step；没有直接 target setter、没有 counter 写入。所有角色自己的公共 Mod4Env.step 源 SHA 相同，每个角色 cfg 都独立确认该 gas 注册与 EventCfg 接入。它们的具体 live modes / manager dispatch 仍未执行确认。

完整 MRO/行/SHA 在 [SOURCE_AUDIT.json](<SOURCE_AUDIT.json>)；便于复核的 17 函数 + 24 role entry/event/step + 4 setter 表见 [SOURCE_PATH_SHA_LINES.md](<SOURCE_PATH_SHA_LINES.md>)。

## 6. NEW C2 最小方向及本次执行边界

[C2_MINIMAL_OBSERVER_SPEC.md](<C2_MINIMAL_OBSERVER_SPEC.md>) 要点：raw sim counter / 原 queue tick / parented physical apply tick 三域分开；term parent 由 push-before-original/finally-pop 动态 context 给出；同 setter 的 unparented 调用不硬标 legs，完整保留 joint selector/方法/asset/原参数、count 与边界。未知来源仍 UNKNOWN，不自动放行。不得删除合法非物理 write，不改变真实队列/0-1-2 tick/每组8次/阈值/RNG/动作或 acceptance。

本次实际运行：

- Python 3.14.3 `-B` 执行自己的 SOURCE/AST audit：PASS，8 roles / 17 function pins / 4 direct setter calls。原任务模块没有 import/exec；AST parse 旧 probe 文档时提示其既有 `\\S` escape SyntaxWarning，旧源码保持原样。
- [自己的 7 个 stdlib 时序 toy](<test_clock_context_toy.py>) 全 PASS，0 failures/errors，约 .001006 秒，[receipt](<STDLIB_TOY_TEST_RECEIPT.json>)。覆盖 seq0 unparented counter0、8 个 apply tick0–7、后续 counter8 非 parent 写、同方法不同 selector、不等的入口/完成顺序、返回/异常/清栈、真实负 queue tick 仍失败。**不是 C1/C2 实现测试，也不是原 queue 数值/RNG 或 SDK/Native 证据。**
- 仅 NEW 本目录写入；原 source、C1/B2 seal、pure、queue、阈值与 A194 目录均未编辑。未使用 SSH / actual FINAL / trace / PT / Torch / SDK 实例 / GPU / C canonical / Git / 锁 / signals / Native / 训练。

[FINAL_HANDOFF_RECEIPT.json](<FINAL_HANDOFF_RECEIPT.json>) 记录本目录独立交付 pins；source-only 与 actual 未知保持分列。父仍负责 review 和任何后续资源准入，不由本报告推进 stage1/stage2 状态。
