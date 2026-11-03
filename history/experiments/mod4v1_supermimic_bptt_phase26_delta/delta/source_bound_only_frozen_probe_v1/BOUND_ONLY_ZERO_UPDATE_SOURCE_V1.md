# ZERO_UPDATE bound-only frozen probe：SOURCE交付，native未启用

## 1. 目的与当前事实

仅回答“同一实际A1全量容器、同一原actor输入协议，把有效输出残差 `0.05*delta` 换为 `0.05*tanh(delta)`，零更新时质量如何”。这不是训练、BPTT、权重修复或训练收益。本包 **source_implemented=true、native_enabled=false**；未提供新native parent/worker/完整stage index，不把两段helper当作已接通的评测系统。

已读取的qualified历史事实见[单seed教师/候选筛查](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/QUALIFIED_E3_W35_REFERENCE_CANDIDATE_SCREEN_V1.json#L15-L165>)及[实际教师基线及容器身份](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/QUALIFIED_EMBEDDED_TEACHER_ORIGINAL_SKILL_BASELINE_V1.json#L210-L235>)：

| 原条件 | 教师 | 原unbounded A1候选 | 解释 |
|---|---:|---:|---|
| E3请求recipe0..11首次episode原稳定credit | 0/74 | 0/74 | normal6排除 |
| E3 normal6首次physical terminated | 0/6 | 6/6 | 单列保持性诊断，不拼入74分母 |
| W35 moving原有效same-UID完整非终止区间 | 19/63，partial190 | 10/69，partial143 | 各自自然条件分母 |
| W35 standing同定义 | 26/26，partial37 | 16/17，partial33 | 与moving分离 |

这些是单seed独立cohort；relative/causal/多seed总技能接受仍null，保母、不promote。父已完成[真实软件CPU fixture](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/BOUND_ONLY_FROZEN_CPU_V1.json#L15-L45>)：RC0、4×N80独立公式误差0、对clipped teacher最大分量差0.050000011920928955（float32容差1e-6）、对旧unbounded公式差0.954431414604187（不是收益）。完整state/norm/teacher、构造后strict load、RNG、原STD与独立norm守卫/sticky均通过；1read/hash/decode、原PT/native/training0。只有自己的synthetic软件证明；native闭环和技能结果仍null。本子代理未读实际raw/PT/NPZ，未运行Torch/SDK/GPU/SSH、C/锁/Git/native或训练。仅Office/ACL技能可用且不匹配RL，使用FS/stdlib。

## 2. 真实actor API与最小改动

[原cache一次性build](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py#L157-L221>)先构造原Wrapper，再严格载入整pi。关键风险是[原Wrapper构造器](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/native_supermimic_bridge.py#L70-L82>)会把residual末层weight/bias置零：在已载入actor外再调用一次该构造器会抹训练权重。故本包不重包已用mean、不对旧cache rearm、不修改旧模块或安装生产forward hook。

实际更小实现是[新build函数](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_frozen_probe_v1/bound_only_frozen_probe_v1.py#L163-L215>)直接消费 **fresh原FrozenA1CheckpointCache**：

1. 核验旧cache源码19226B/`1ea4bcfa...`、role E3/W35及实际qualified容器SHA；原cache仍执行一次全量读取/hash/CPU decode，N1024根对象完整保留。
2. 一次build声明置`cache._built=True`，包括失败也不清除，阻止回退/重建；无加载旧母PT。
3. 原runtime module源码PIN保持，实际RSL必须10334B/`6219ebb3...`；只选择[新有效Wrapper subclass](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_frozen_probe_v1/bound_only_frozen_probe_v1.py#L95-L112>)。它**直接继承原构造器**，唯一有效动作公式新增输出delta的tanh；不新增参数、buffer或子module。
4. 原构造、全key/shape/dtype/finite、全部pi/norm/teacher strict load与逐值核验、eval/no-grad、device迁移整个with块，经变量/Wrapper选择归一化后与原代码AST完整相等。
5. [新Mean](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_frozen_probe_v1/bound_only_frozen_probe_v1.py#L115-L160>) **act函数对象直接继承原act**，没有复制历史采样路径。保留整CPU根及所有pi参数/普通buffer的身份/版本冻结；另固定有效class、forward、原构造器身份。

[原act与freeze](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py#L224-L277>)继续原35噪声/延迟输入、10帧history、首帧/真实T或Tr时重复当前帧、同一raw35前三维knowncmd、scale0.05/offset0/clip6。原[Policy的latent tanh不是输出delta的界](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/networks.py#L194-L222>)：输出仍是decoder MLP的无界值。本probe的输出tanh是实际新增的有效forward。原[RunningNorm.forward](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/networks.py#L34-L67>)只读取统计，未调用update；所有统计buffer仍严格载入且冻结。

## 3. API与SOURCE route

完整[字段合同](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_frozen_probe_v1/BOUND_ONLY_SOURCE_FIELDS_CONTRACT_V1.json>)、[SOURCE adapter](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_frozen_probe_v1/bound_only_frozen_route_v1.py#L16-L55>)。

```python
# 未来已核验的原fresh cache，未调用其build_mean_policy；这里是API，不在本子执行。
mean = build_bound_only_mean_policy(
    cache, device, num_envs=80,
    expected_container_sha=QUALIFIED_CONTAINERS[role],
    collect_action_statistics=False, synthetic_only=False)
caller = BoundOnlyPolicyCaller(
    mean, boundary=OriginalEpisodeBoundary(mean.t, mean.device))
# 原循环仅caller(original_TensorDict, stochastic_output=False)，
# 每次原env.step之后caller.observe_transition(true_terminated, true_truncated)。
```

新variant：`A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_RESIDUAL_PROBE_V1`；新purpose：`FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_N80_V1`。

SOURCE adapter继承[原A1CheckpointAdapter](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py#L324-L366>)的FINAL绑定/全量cache构造、check/check_actor；覆actor factory与receipt。额外SOURCE task字段：

```json
{"bound_only_probe":{"purpose":"FROZEN_ZERO_UPDATE_BOUND_ONLY_E3_W35_N80_V1","policy_variant":"A1_RAW35_ZERO_UPDATE_BOUND_ONLY_TANH_RESIDUAL_PROBE_V1","zero_update":true,"native_enabled":false,"collect_action_statistics":false}}
```

Receipt明确区分：`container_checkpoint_SHA/container_algorithm_*`仍原A1，`effective_wrapper`/`policy_variant`是新bound-probe；`source_producer_actual_BPTT_policy_steps/source_producer_counts`只是历史来源，`probe_BPTT_policy_steps/probe_training_updates=0`，四optimizer更新全0，不创建learner/WM/critic/replay或恢复RNG。新component validator不是资源准入、p.wait、App.close或技能qualification。

## 4. 数学范围及同forward统计

记`C(x)=clip(x,-6,6)`、原teacher未clip输出`b`、原residual输出`d`：

- 原候选：`C(b+0.05*d)`；本probe：`C(b+0.05*tanh(d))`。
- 实数算术下，**每个action分量**的preclip残差绝对值≤0.05；由C的非扩张性，相对`C(b)`的postclip分量差也≤0.05。
- 这不是相对旧候选的0.05界：`b=0,d=1000`时旧preclip=50、新preclip≈0.05；总clip后仍相差5.95。6维L2也不是0.05；上界是`0.05*sqrt(6)`。单位是原actor action，不是物理力矩保证。
- tanh不是硬clip；未来训练梯度为`0.05*(1-tanh(d)^2)`，大delta尾部会衰减。此处无训练，任何bounded短训须新版本，独立比较，不能把动作后处理收益记作BPTT收益。
- float32加法/clip存在舍入，未来CPU fixture用1e-6绝对数值容差；这不是原技能接受阈值变更。

[可选统计](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_frozen_probe_v1/bound_only_frozen_probe_v1.py#L41-L92>)默认关闭。开启时只对**本次已经算出的**teacher/delta做算术与标量归约，比较残差幅值、相对clipped teacher与旧公式action差、`abs(preclip)>6`总clip计数。teacher/residual各仅一次forward，无多采obs/RNG/physics。读标量可能GPU host同步并增加walltime，原deadline仍生效；绝不把该walltime当simtime。旧公式是probe观察上的算术counterfactual，不是独立旧policy物理rollout，更不是paired技能效果。

## 5. 测试与父用真实Torch CPU脚本

[初始47测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_frozen_probe_v1/CPU_TEST_RESULTS_V1.json>)47/47 PASS；新增SOURCE route/历史计数隔离后[52测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_frozen_probe_v1/CPU_TEST_RESULTS_WITH_ROUTE_V1.json#L1-L11>)52/52 PASS、0fail/0error、0.054989s。包含2000点纯标量非扩张反例、同forward计数/无统计额外归约、全原构造strict-load块AST、继承act身份、cache失败后不可重建、RSL/容器/新variant/计数类型/边界PIN及真实T/Tr/missing-step负例。不把fake对象测试等同实际Torch或技能证明。

父已独立运行[新CPU fixture](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_bound_only_frozen_probe_v1/remote_cpu_bound_only_synthetic_v1.py>)；本子未运行它：

```bash
# 复用已验证的CPU Torch/RSL/TD/vendor/bridge；各DIR均由父选其已核验目录。
PYTHONPATH="$NEW_SOURCE:$ORIGINAL_FROZEN_CACHE_DIR:$ORIGINAL_37927_CORE_DIR:$REVIEWED_DEPENDENCY_DIRS" \
  "$OWN/run-python.sh" -B "$NEW_SOURCE/remote_cpu_bound_only_synthetic_v1.py" \
  --new-output "$NEW_UNUSED_CPU_OUTPUT"
```

它只生成自己的全量synthetic root：非零residual、非平凡rms、4×N80原mean公式/历史/边界核验、零末层构造后strict-load恢复、原teacher及全部pi值、teacher/residual各4次实际子forward计数、caller RNG不变、live teacher STD及独立新cache norm负例。每个新case cache仅1 open/hash/decode，不重置旧cache；不接受原模型输入参数，不打开母PT/旧模型，不运行native/optimizer。synthetic状态显式标记，组件PASS不升级为真实producer或native qualification。

## 6. 未来native接入前必须补齐的独立SOURCE工作

本包提供helper/adapter/字段合同而非可启动native计划。父/405须在另一个NEW目录：

1. 新kind/purpose/role2 task validator、worker/runtime factory与新receipt semantic gate，明确选择BoundOnlyCheckpointAdapter；不直接复用声称unbounded mean的旧gate/FINAL。
2. 为新runtime/worker和两个新增模块生成完整SHA stage index；保持[原14项依赖库存](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/payload_frozen_microbatch_v2/MICROBATCH_STAGE_INDEX_V2.json#L8-L98>)及所有原静态native依赖。[AppV6明确import Base](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/app_close_semantics_v6.py#L23>)即`resume_runtime_contracts_v3 as _base`，不能遗漏。没有把当前旧worker+两个新增模块谎称已完成bound native接线。
3. N80/seed20260928/E3 160/W35 1600、原35采样噪声/延迟、原command、DR/physics/速度/原接受谓词保持；private GPU EX/global finite EX、canonical C只读、原fresh admission、actual p.wait和完整AppV6 close不改。
4. 原observer/grader不改：新外层FINAL/receipt/group必须先证明 **bound-probe policy语义**，再用原row消费者一次读取新自有case。单凭row/source_SHA区分不了同容器的teacher/unbounded/bound三种有效actor。
5. 先记录未来**零更新bound-only**结果，再另行source版本/资源准入做bounded短训；源权重历史计数与本probe零更新分离。当前不承诺提升，也不据当前不等cohort推因果回归或接受。

## 7. 当前unknown

实际Torch CPU probe软件验证已PASS；实际native index/新schema/entry、准入/close、boundProbe原技能率、matched UID/pose/noise cohort、相对或训练收益仍 **null**；不promote。所有本次输出仅在此NEW目录；旧seal/训练/评测源未改。
