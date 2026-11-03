# Phase1 SOURCE 状态/上下文分区合约 v1

**结论：SOURCE 分区与可执行 stdlib 检查已冻结；Gate1 = UNKNOWN，actual SDK pass = false，exact = false。**

目录只服务阶段1，不含 trainer、native adapter、采样器、旧 checkpoint 迁移或旧向量切片。实际训练/物理/传感器路径未执行。Office/ACL skill catalog 无 RL 审计匹配，采用 FS/CLI + Python314 stdlib。

## 文件与稳定 API

- [partition_schema_v1.json](<partition_schema_v1.json>)：八角色逐字段 offset / width / name / native_unit / legacy_stored_unit / canonical_unit / scale / time / source / class / evidence；缺件保留 `offset:null`。
- [source_manifest.json](<source_manifest.json>)：固定 allowlist 的 202 个源/已发布 STARTUP 元数据 SHA256。仅源字节/AST，不导入或执行原 task。
- [phase1_contract.py](<phase1_contract.py>)：`load_schema(path=None)`、`validate_schema(schema)`、`validate_named_context(role,named,schema)`、`validate_actor_view(raw_named,original_actor35,schema)`、`validate_sensor_pair(samples,start_physics_tick,episode,schema,previous=None)`、`validate_action_trace(capture,start_physics_tick,episode,schema)`、`validate_static_episode(before,after,schema,role)`、`exact_gate(schema,receipt=None)`。
- [test_phase1_contract.py](<test_phase1_contract.py>)：固定确定性 synthetic 正反例，无随机数。
- [SOURCE_RECEIPT.json](<SOURCE_RECEIPT.json>) / [SYNTHETIC_TEST_LOG.txt](<SYNTHETIC_TEST_LOG.txt>)：测试结果和证据边界；由 final stdlib 测试运行生成。
- [SOURCE_SEAL.json](<SOURCE_SEAL.json>)：封件相对路径/字节 SHA256。[seal_source.py](<seal_source.py>) 首次创建，其后只读复验；内容寻址防漂移封件，不冒充磁盘 ACL 锁或实际 SDK admission。初次 here-string shell 入口被 host `analysis.dynamic-shell-source` 在执行前拦截，未产生封件；后改用明确脚本文件入口，原错误保留在脚本说明。
- [build_schema.py](<build_schema.py>)：仅生成审计资料。恢复后已读回现有产物，未盲目重跑 builder；保留原 source hash 与既有生成记录。

`ContractUnknown` 表示缺失或 UNKNOWN 证据；`ContractViolation` 表示现有值与 source 合约矛盾。任一情况均停止该项 exact 声明，不补零、不 hold、不重抽噪声、不把 endpoint 当 MID。`exact_gate` 在本 SOURCE v1 **始终抛 ContractUnknown**；给 receipt 加 actual 字样不提升证据等级。将来的现场证据需独立 provenance verifier，而非一个 `true` 开关。

## 已观察程度（不扩大声明）

|角色|已发布 context dim|STARTUP/layout证据|历史 actual BPTT policy steps|
|---|---:|---|---:|
|E3|122|OBSERVED_TRAINED_STARTUP_LAYOUT；已发布 saved-report layout 一致|2182|
|W35|119|OBSERVED_TRAINED_STARTUP_LAYOUT；已发布 saved-report layout 一致|1973|
|CURB_INDEPENDENT113|119|OBSERVED_ACTUAL0_CAPTURE_STARTUP_LAYOUT_NOT_TRAINING|0|
|CURB_PROTECTED878|119|同上|0|
|SLOPE135|119|同上|0|
|SLOPE_INDEPENDENT50|119|同上|0|
|E0|117|同上|0|
|E2|117|同上|0|

159 个已发布命名字段是结构/维度观察，不代表159项数值、clock 或 live class identity 已现场通过。单位与更新语义来自原 source；每 transition 的 clean/noise-used/FIFO/timing 仍 UNKNOWN。仅源文件存在不证明 binding：新 builder 用 entry -> constructor 的本地 `ImportFrom` 边作 AST 检查；完整 live `module.__file__`、class/function identity、配置 readback 仍属 Gate1。

观察来源：[CLOSED_RESULT.json](<../reports/ACTUAL_A1_NATIVE_V6_ADMISSION2_20261102_232709/CLOSED_RESULT.json>) 的八角色 `startup.context_layout`；仅复核 [E3 已发布语义/布局](<../reports/ACTUAL_SAVED_REPLAY_CONSISTENCY_E3_V1.json#L902-L1003>)、[W35 已发布语义/布局](<../reports/ACTUAL_SAVED_REPLAY_CONSISTENCY_W35_V1.json#L902-L991>)，未读模型或 replay 文件。

## 最关键的 legacy 字段

下表为 **0-based 半开区间**；`stored = native * scale` 是旧上下文缩放，不是新的物理单位。完整逐字段细节见 schema。

|共同前116维|width|类别|native / stored 关系|
|---|---:|---|---|
|actor35_original `[0:35]`|35|ACTOR_VISIBLE + SENSOR_NOISE + SENSOR_DELAY_QUEUE + COMMAND/PHASE|原带噪、原延迟 actor35，**绝非 SENSOR_CLEAN**|
|contact_history `[35:53]`|18|DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE|N 世界系接触力，3×5ms bins×2轮×xyz，newest-first；stored×.01|
|applied_torque `[53:83]`|30|DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE|转动关节 N*m、移动关节 N；SDK computed effort；stored×.02|
|mild_factor `[83:84]`|1|STATIC_DR|共享 mass/inertia 倍率；不等于全部 motor gain|
|delay_legs_lag_steps `[84:85]`|1|STATIC_DR|native0/1/2个2500us tick；stored×.5|
|legs pending/applied `[85:89]`/`[89:93]`|4+4|DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE|processed leg target rad，不是 policy last_action|
|delay_wheels_lag_steps `[93:94]`|1|STATIC_DR|native0/1/2 physics ticks；stored×.5|
|wheels pending/applied `[94:96]`/`[96:98]`|2+2|DYNAMIC_PHYSICAL_OR_ACTUATOR_STATE|processed wheel target rad/s，不是 torque|
|feedback_delay `[98:99]`|1|STATIC_DR + SENSOR_DELAY_QUEUE|native0/1个10000us tick；只记录 delay choice，未记录 FIFO|
|SpringPressure/GasDamping `[99:101]`/`[101:103]`|2+2|STATIC_DR|独立 episode dimensionless 因子；nominal2000N/m、3Ns/m|
|ChassisCOM_delta_m `[103:106]`|3|STATIC_DR|xyz米；stored=200*meter|
|PD_leg_kp/kd `[106:110]`/`[110:114]`|4+4|STATIC_DR|dimensionless因子；actual60*factor、2*factor；与 dynamic applied_torque 分开|
|PD_wheel_kd `[114:116]`|2|STATIC_DR|dimensionless因子；actual .6*factor|

尾部：E3 `command_time_left[116]`、recovery `age/recipe/request/credited/stable[117:122]`；W35+四E1角色 `command_direction[116]`、`command__command_heading[117]`、`command_time_left[118]`；E0/E2 仅 `command_time_left[116]`。

- **command_time_left**：source native 秒，bridge `*.01`，故 canonical 秒 = stored×100；它不是100Hz tick。此处只记录映射，未反缩放后拼回旧权重。其继承 SDK timer live 单位/更新顺序仍需 Gate1。
- **recovery_age/stable**：native centisecond counts，每50Hz control加2；bridge `*.01` 后已为秒。stable不足条件归零，达50native=.5秒credit；这些是动态phase，不是静态gain。
- **command_direction** 是外生 sampled world-direction rad；`_command_heading` 是上次 BODY 投影用的实际heading rad，会动态变化，不能当永久 DR。

## Actor 与 privileged 边界

原 [Raw35ActorMDP.obs](<../source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/command_tracking_torch_candidate_v1.py#L190-L200>) 实际严格 `context[..., :35]`，`add_noise` 是 identity（原 raw35 已被污染，不能再抽一次）。新 validator 只收已经命名的字段，不实现此旧向量 slice。

原35内部：command0:3；height command3:4（5×m，非实测高度）；omega4:7（.5×rad/s）；gravity7:10；leg qrel10:14；wheel pos14:16结构零；leg vel16:20（.1×rad/s）；wheel vel20:22（.1×rad/s）；last policy action22:28；mode onehot28:35。只有 actor35 暴露给 actor，后81/84/87个 context 维度保持 WM/critic/aux privileged-only。actor观测、原task clean critic38 与新WM/critic privileged输入三者不混称。

## 76 条 required extended 缺件

这些是 **NEW named schema** 的必需 actual-source字段，不伪造旧xi维度；所有 legacy offset=null、actual receipt UNKNOWN：

1. 静态5项：legs/wheels `robot.actuators[group].episode_scale` 4+2、`_mild_dr.mu`、`_mild_dr.nominal`、sensor leg encoder bias4。`mild_factor`只涵盖 mass/inertia，bridge可选 `mild_gain_factor` 在八布局均未出现。[mild_dr源](<../discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/mild_dr.py#L57-L93>)。现场还应 readback `step_scale==1` 与相关event关闭；旧 [Mod4DCMotor](<../discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/mod4_task.py#L250-L290>) 支持per-step gain，但本 [white源审计](<../discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/mild_dr.py#L115-L126>) 要求其为1。未据非active getter文件宣称actual。
2. action queue18项：两组各 `episode,pending_valid,issued_tick,due_tick,applied_valid,applied_issue_tick,first_apply_tick,last_submit_tick,last_apply_tick`。旧 `lag,pending,applied` 不是 Markov queue 的完整状态。
3. sensor50项：五channel各 `clean_at_sample,noise_used,noisy_before_queue,queue_cur,queue_out,last,sample_tick,ready,episode,draw_count`。需要原MID/END两次100Hz样本；50Hz endpoint 和 `clean_policy()` 重算当前obs均不替代。
4. E3 `recovery_peak/delta`2项；command phase/resample/next-write receipt1项（role-specific width未知，不编造维度）。

噪声绑定实际 `noise_bias_mild_v1` [source bounds](<../discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/sensor_mild_math.py#L5-L38>)，不是套论文幅度：omega ±.125rad/s、gravity ±.025、legpos ±.005rad、legvel ±.25rad/s、wheelvel ±.5rad/s、episode leg bias ±.0075rad。先 clean+实际noise-used+bias，再 original feedback queue，再 observation scale。

## Gate1 现场被动捕获与可验证条件

**本封件没有执行下述捕获。** 在八角色既有原任务链上，未来需：

1. 捕获entry/hash、实际module/class/function绑定及profile配置；E2 `directional_spin_runtime=e2_directional_spin_runtime_v1`，E3则 alias到 `h1_external_operator_command_v1`，勿因同名文件存在认错实现。
2. 每50Hz control捕获 physics start，原400Hz8次 apply（tick start..start+7）和原100Hz MID/END（start+4、start+8）scene-update采样；100Hz sample tick与bridge50Hz `f` 分开。
3. 每channel每次自然调用前的 clean input、实际noise cache used、bias、draw_count/RNG digest，自然调用后 FIFO `cur/out/last/sample_tick/ready/episode`；probe自身 RNG前后相同、额外噪声draw=0。全环境draw_count增量按due_environment_count，不误当单环境计数。
4. 验证 `noisy=clean+noise+bias`；delay0选current；delay1选紧邻previous；新episode warmup即使配置delay1也选current并ready=false；其后age只0或10000us，禁止跨episode幽灵样本。
5. 两组 action full queue、processed submit target、每物理tick actual articulation target readback；验证due=issue+lag、lag0/1/2、首transition latency0/2500/5000us，区分 held-command sample age（随后会继续增长）。
6. episodeId/resetids/局部reset前后 readback，static motor/PD/COM/friction/bias 同episode不变，其他env reset不污染；恢复E3 age/stable/peak/delta/recipe/request/credited及pre-reset物理s1；终止后的reset样本不得拼作同episode目标。
7. command precontrol/postcompute/next-write、自然resample/reset/boundary receipts，特别E2 `phase_elapsed`写command后推进、E3 recovery pre-reset hooks。只观察现有操作，不新增command/noise抽样或reset。
8. 原actor35逐位相同、只给actor35；observer新增reset/physics/action/model/noise操作均0。unknown source/unit/clock/binding仍为Unknown；完成全覆盖live provenance独立校验后才讨论exact。

保持 physics400-k2000-d3、.0025、原50/100Hz、D0D7、H1、mothers、原接受条件；不改旧封件/预算账本/锁/Git，不执行SSH/SDK/GPU/PT/native训练。不兼容的新分区如将来实施，应fresh lineage；本阶段不迁移checkpoint、不修旧NNnorm。

## 复验

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B 'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_phase1_state_context_partition_v1\test_phase1_contract.py'
```

普通测试调用不写receipt；`--receipt`仅初次生成封件收据，已存在时停止写入。SOURCE synthetic PASS 只说明合约正反例、source hash 与算术通过；不是 actual SDK/paper Eq1闭环通过。
