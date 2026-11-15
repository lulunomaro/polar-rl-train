# 当前模型与时间线更新（用户2026-11-15确认）

当前项目使用最新 **MOD4v3 / MOD4V3_HW300N60_R3**。本条覆盖下方2026-09-10旧模型路径的“唯一live plant”描述；不要据旧e91 pin把当前MOD4v3工作退回9月模型。当前训练资产以`_mod4v2_src_20261106/sources/local/MOD4V3_PITCH_RATE_SQUARE_40M_20261115/PLAN.json`的`asset_identity`及新的同源试验读回为准：MJCF SHA256 `77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f`，USD SHA256 `e057969b136fd75613bb8d77985d43d043f54faae62dc060afb718ebabbe1c1c`。当前冻结综合默认仍为11月13日iteration25331、权重SHA256 `db6e9ccf5c6d4d05a68633fd82861d903c4c52fcc1a6dd89132e55e2a4bf1283`；之后未晋升试验不能覆盖它。

查询进展先按对话时间读取最新消息和实际运行状态，不能把旧总览当实时记忆。MOD4v3的PPO六动作顺序是`left_front1_joint,left_rear1_joint,right_front1_joint,right_rear1_joint,left_wheel_joint,right_wheel_joint`，现有播放器通过`[0,2,1,3,4,5]`映射到模型关节顺序；不要套用下方旧模型的名字。35维actor、78维critic、6动作和现有电机包络保持。新模型不得混用旧模型检查点。retired rm2025_fixed仍不可恢复。

俯仰修复当前试验：`_mod4v2_src_20261106/sources/local/MOD4V3_PITCH_CAUSAL_REPAIR_40M_20261115`，独立40分钟，无自动延长；继承上一轮2mm闭链episode guard，本次不改变物理容差。


当前40分钟俯仰试验在2026-11-16确认20ms奖励窗口时序错位后分段修复：第一段`MOD4V3_PITCH_CAUSAL_REPAIR_40M_20261115`已安全保存，实际1019.2484555s；第二段`MOD4V3_PITCH_CAUSAL_TIMING_R2_20261116`只使用剩余1380s，不是新增40分钟。回放所有原始成功/失败保留，默认综合权重尚未晋升。


本次俯仰训练已于2026-11-16T00:29:14.977693+08:00完整保存结束，PPO两段合计2401.152479s（40分1.15秒），最终iteration25716，最终权重SHA256 930fb0ec09428f92a5f403beed6c74b59cf807bbcd17344a29f449f516b6c18d。训练未自动延长，综合默认未晋升；俯仰效果待本轮所有固定回放完整报告判定。最终报告位于R2/COMBINED_REPORT.md。

---

# MOD4 Git 记录必须遵守

人类2026-10-09明确要求所有试错和所有报告都用Git记录。读取 [完整记录政策](docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md) 与 [既有追加工作流](docs/NEXT_AI_GIT_WORKFLOW.md)。

所有真实成功/失败/拒绝/回退保留独立ID和证据；所有保存的报告，包括同步/验证回执、读者错误、交接和后续补充都需提交。旧失败/false/raw不可改成pass，也不可只归档成功摘要。阶段报告可以合并一次记录，阶段归档后生成的报告必须再补入Git或如实标pending，不能遗漏。

使用archive_tools/record_experiment.py，唯一annotated trial并核验remote main/tag/peeled；推送失败只续已有objects。健康无新报告无需造trial。凭据禁止归档；权重和大型原件只SHA/路径索引。主训练、生产源与canonical预算不因归档修改或暂停，旧once不重跑。

# 三张4090的持续调度要求

人类2026-10-16明确要求：“3张4090要最大程度利用好别让显卡空闲浪费算力时间”。这是持续有效的资源调度偏好。

- 提前准备下一项已授权任务的源码、检查点、准入与交接；在实际完成、安全保存和资源释放后及时接续。
- 三张4090优先分别推进专家；3060承担冻结评测。一个科目等待评测时，优先安排其他已有明确授权且准入通过的工作。
- 记录空闲卡的实际原因与可执行的下一步，主动推进可完成的准备，避免仅排队或等待下一次巡检。
- 本偏好不单独批准新科目、奖励修改、新训练窗、并发计账合同、预算增加或旧试验重跑；实际任务仍须符合既有授权、资源与原canonical计账边界。不得为提高利用率重放已消费任务、关闭安全检查或干扰其他进程。

# 数值审计与训练门槛的范围

2026-11-01人类明确更新：“还有闭链误差调整到10mm终止”。未来新MOD4训练和评测采用0.01m单环境episode重置，覆盖历史2mm数值；实体闭环、奖励、solver和mimic .01rad不因此修改。原2mm记录和冻结source/INDEX/once不可改写；旧未执行2mm任务需另建10mm版本和新准入。按[门槛范围与历史依据](docs/NUMERICAL_AUDIT_AND_TRAINING_GUARDS_20261021.md)的最新更新执行。

人类2026-10-21核历史后明确“以后按照这个继续”。遵守[门槛范围与历史依据](docs/NUMERICAL_AUDIT_AND_TRAINING_GUARDS_20261021.md)：已选2.5ms/TGS32/4；闭链2mm是单环境重置，单峰不整批停训/回退1ms；查询1µm仅特定数值核验，不能升级成统一物理健康或毕业线。不要再用额外FP64、逐位相等、维度不符的三角边缘条件等新增审计规则反复阻断已授权工作。复用已过同源证据；原失败、实际任务所需检查与非有限/完整性/硬件/完整保存保护保留。
