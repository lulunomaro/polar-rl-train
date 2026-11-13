# polar-rl-train

## 2026-11-12 平地速度恢复40分钟完成：保留最终实验候选

从用户命名的Rough-v1 120m/7cc1fc6d…完整接续，512env实际PPO2405.762s，210更新；轮输出行专项后转全策略，五分钟全局检查点与全部完整PT保存。35/78/6、原R3资产、fullDR范围与−1.5e²不改；轮反馈改为400Hz，腿100Hz/策略50Hz。原成熟父包保持冻结。

最终候选iter24692/SHA979e355a…：原六项名义MuJoCo6×10初态60/60，49点网格27/49→45/49、MAE0.2089→0.0757m/s；原生完整DR原六项同批17/30→23/30、推扰后18/30→24/30。名义PhysX24/30→20/30的前向欠速退步、额外高站姿残余均保留，未宣称所有后端毕业。两种抬高上阶与下阶名义单次对照保持。

[完整报告与限制](sources/local/MOD4V3_FLAT_SPEED_REPAIR_20261112/REPORT.md) · [完整候选PT](sources/local/MOD4V3_FLAT_SPEED_REPAIR_20261112/weights/selected_flat_speed_candidate.pt) · [配方/源码/全检查点入口](sources/local/MOD4V3_FLAT_SPEED_REPAIR_20261112/README.md)。

## 2026-11-12 平地超速原因调查：腿控迁移已验证

93个冻结回放、0重置；腿/轮输出互换定位主要偏移跟随腿控。高站姿速度改善、低站姿超速扩大，原平方罚未漏；额外助跑进展奖励范围过宽，旧Rough阶段也已有偏差。没有新训练、未更换原最佳模型。[完整证据与最小修复建议](sources/local/MOD4V3_STAIR_SPEED_AUDIT_20261112/REPORT.md)。

## 2026-11-12 台阶抬高底盘20分钟接续：末段待收

从用户选定Rough-v1 120m/7cc1fc6d…完整接续，保留fullDR和原−1.5e²，只新增台阶抬高/进展引导。已取回5m、10m与首次完整PT；最后确认10分36秒后目标SSH失联，15/20/final与原生fullDR对照待收。本机低阶抬高上阶保持、前向超速增加，原命名模型继续保留。

[实验配方、完整PT、实际结果与待办](sources/local/MOD4V3_SCUT_STAIR_LIFT_20M_20261112/REPORT.md)。

## 2026-11-12 用户选定：最牛逼的模型，上台阶手动回放快照

当前播放的 Rough-v1 120m / iter24482 / SHA `7cc1fc6deeee…` 已单独命名保存，完整PT本体、全部训练参数与源码、当前机械资产、手动驾驶/站立高度控制、750块地形和成功上阶轨迹一起归档。本机MuJoCo名义条件：高度缓慢调至0.365或0.40m，2.2m/s指令助跑，已连续上两级各16.5cm、进入33cm平台。

[模型本体、配方、手动回放完整包](deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/README.md)。此前完整DR PhysX分项结果保留原报告；这是当前120m权重的用户命名快照，未新增训练更新。

## 2026-11-12：统一Rough-v1两小时PPO完成，验收5/10

从用户选择的Rough-v0 100m/iter23665/SHA0010283962…接续，实际PPO7206.600s、817更新、80,314,368环境策略步；24定时点加首次/final，共26完整PT、25种字节。11族/10级统一训练及完整DR、原物理/接口/奖励保留。总模型索引30阶段、190个完整训练PT记录。

已收齐同批PhysX5组：完整DR最高档穿越父/105m/120m=170/162/169（各200），高速162/154/154（各180）；宽阶上行未稳定掌握。名义平地34/41/40，完整DR35/32/34（各60）。Rough线保留原Rough-v0 100m，本轮105m/120m实验候选，未晋升，也未回退R1重训。原实车包保留。

目标机SSH超时，第6组gyro末段和后续落地/原Rough-v0保留测量待收齐；训练及全部PT已在本机完整核验。不能称验收全部完成或GPU已确认释放。未自动开下一轮。

[本轮最终报告/全PT](sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112/README.md) · [Rough-v0逐地形完成报告](sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/COURSE_COMPLETION_REPORT.md)。以下旧轮次按各自时刻保留。

## 最新训练记录：2026-11-12统一Rough-v0两小时

7206.137秒PPO与8组PhysX对照已完成，26份完整PT本体保存；综合接续仍选R1第二轮005m，新100m/120m未晋升。见[当前报告与全PT入口](sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/README.md)，当前无训练在运行。原R0～R4表保留为历史规划，本轮按用户统一科目新指令执行。

2026-11-12 当前：**R2首轮40分钟及配对评测已完成**。5–10cm低落高能力已具备；综合保留r1round2_005m（iter22959/SHA0dcc15f5…），本轮R2新权重未晋升，005m保留实验备选；40m不作默认接续。28阶段/138完整PT文件索引，R2的10个PT实体均保留。[结果与选择](sources/local/MOD4V3_ROUGH_R2_20261112/DECISION.md)。



2026-11-11 当前进展：**R1第二轮及同批评测已完成**，实际2404.901s，8个5分钟保存点和完整PT已保留。优先保留本轮005m作较均衡实验候选（iter22959，SHA0dcc15f5…），010m作L3穿越对照；40m非全面最优。旧六类低档首次穿越均120/120。[本轮选择](sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/DECISION.md) · [全部地形图](sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/terrain_all/README.md)。主冻结保持，未开R2。

R1本轮已完成40min三段训练及同批评测：[最终报告与模型选择](sources/local/MOD4V3_ROUGH_R1_ABSCUBIC_20261111/DECISION.md)。名义PhysX跟踪改善，fullDR偏速未解决；Flat1.5_020m保留回退，总26阶段/118完整PT实体。

本轮切段历史：同一40min轮在010m完整PT后切段，速度平方项−1.5e²→−2.0e²，原R1课程等级/计数保留，接续1643s。见[sources/local/MOD4V3_ROUGH_R1_SQUARE2_20261111/README.md](sources/local/MOD4V3_ROUGH_R1_SQUARE2_20261111/README.md)。


MOD4 强化学习项目的修复、训练、诊断和交接档案。仓库创建于 2026-10-03，默认私有。

本次从本机及 4090 目标机收集 **83 个资料目录、20,078 份文件**，为 **968 条有保存证据的试验/修复/验证记录**补建提交和注释 Git 标签。另有每目录一个 `version-*` 标签。包含成功、失败、无效探针、被否决方案及其他 AI 留下的资料。

## 从这里看

- **[Rough 课程计划：对照华南虎版本与预训练记录](docs/ROUGH_CURRICULUM_README_20261111.md)**：MOD4-R0～R4、完整 DR 继承、低难度接入、每五分钟检查与模型接续；R0/R1首轮及配对评测已完成；R1第二轮已完成，R2首轮已启动。
- **[DR各阶段配方、保留模型与训练方法（含完整PT）](docs/DR_TRAINING_INDEX_20261111.md)**：26个阶段/分支、118份完整检查点、父子谱系和SHA；[直接取模型](sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md)、[后续续训方法](docs/DR_TRAINING_RESUME_20261111.md)。
- [按阶段看修了什么](docs/REPAIR_TIMELINE.md)：人工整理的修复主线、重要纠正和未完成事项。
- [完整试验/修复标签表](history/INDEX.md)：每条记录的标签、类别和证据链接。
- [全部版本目录](history/VERSIONS.md)：83 个目录各自的来源、源码和交接说明。
- [原有 Git 记录](provenance/ORIGINAL_GIT_RECORDS.json)：播放器两个原仓库中仍可读取的 5 条提交，其作者/时间和文本差异保留，另有 `original-*` 标签。
- [下一位 AI 的记录工作流](docs/NEXT_AI_GIT_WORKFLOW.md)：新增修复/试错按版本追加，不覆盖旧失败或标签。
- [所有试错与报告的长期Git要求](docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md)：失败、拒绝、读者错误、同步与最终验证报告也必须记录，阶段后生成的报告补交。
- [当前生产状态快照](CURRENT_STATE.md)：归档时实际阶段与未部署候选；不会自动更新为实时状态。
- [项目代码入口](project/README.md)：当前生产源代码的固定副本及外部运行依赖。
- [归档范围与缺口](docs/ARCHIVE_POLICY.md)、[检查结果](provenance/ARCHIVE_VALIDATION.json)。

## 后续 DR 计划与执行约束（2026-11-11）

用户要求后续 DR 按本表推进。目标是让原 Step7 父权重谱系适应随机化，同时保持前进、后退、旋转和高度任务能力。Step6 已晋升冻结。原始父权重 SHA256 为 `884cd07b3942df9c8484b905994e302906c84151f6f9c5d079a417ec98158f24`；实际续训父检查点另按路径、SHA 和 iteration 记录。

**当前累计范围：Step7物理延迟、独立刚体质量、输出倍率、分部位材质、速度推扰，以及全范围COM/PD/摩擦/原生气弹簧阻尼/外力/噪声和MOD4可行reset，奖励保留`-0.5e²`。** 合并40分钟轮已训练与配对，本轮诊断候选remaining_010m，iter22265，SHA`978994b2614f4454f96bfd0ac264f00cbe3ffd219a5372487c558435503dbd15`；完整DR成绩2.0→1.90988（4/10）、2.2→2.18903（6/10）；正式任务39/60、reset=0。原push020m为本轮父，原主冻结保留；本轮适应未完成，PhysX名义前进回归明确保留，已接受范围接续仍为push020m，Rough尚未启动。

原Step7质量适应模型与训练配方继续[冻结](sources/local/MOD4V3_STEP7_FROZEN_20261111/README.md)，iteration21754、SHA `23c112b16e9629215c7265124925daaf0f9b6bbbb62be61689c714ba1fc7a772`，保留为主对照。输出倍率020m备用、材质010m实际接续到推扰020m；材质轮实际权重父仍是质量040m，不能按目录顺序接错。**这些模型的完整`.pt`已经收进本次Git档案**，见[阶段总索引](docs/DR_TRAINING_INDEX_20261111.md)和[全部模型表](sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md)。

**2026-11-11 剩余DR合并轮完成：** 4096env、2403.405s、8次完整5min检查点与同源配对已完成。[最终报告](sources/local/MOD4V3_STEP7_REMAINING_DR_20261111/FINAL_REPORT.md)。保留[remaining_010m](sources/local/MOD4V3_STEP7_REMAINING_DR_20261111/weights/model_010m.pt)，iter22265，SHA`978994b2614f4454f96bfd0ac264f00cbe3ffd219a5372487c558435503dbd15`；完整DR受扰后2.0→1.90988（4/10）、2.2→2.18903（6/10）；正式任务39/60、reset=0。COM/PD/摩擦/阻尼/外力/噪声full范围和MOD4可行reset已实际训练；各任务与随机reset适应限制按报告记录，原Step7主冻结保持，Rough未启动。完整PT及配方也入Git。

**第二轮40分钟完成：** fixed819名义/3277完整DR，从首轮10m完整PPO接续，实际2401.101s，8检查点及同源配对。[第二轮结果](sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/FINAL_REPORT.md)。保留[mixed2_020m](sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/weights/model_020m.pt)，iter22502；名义/DR具体追踪及失败见报告，不自动替换已接受候选/主冻结，Rough未启动。

第二轮实际结论：完整DR20m前进5/10、6/10（均值1.93541/2.21671m/s），总41/60、reset0；PhysX名义前进仍0/20（1.76473/1.92687m/s），未解决。原样继续堆时间收益有限；最新诊断候选mixed2_020m，25m综合备用，不覆盖原主冻结/已接受push020范围。

参考范围以 [保存的华南虎 trained_env.yaml](sources/local/MOD4V3_FORWARD_REGRESSION_AUDIT_20261110/reference/trained_env.yaml) 及对应实际事件实现为准。D 编号用于追踪项目。已先完成 **D4 输出倍率 → D5 分部位材质 → D10 速度推扰**，随后按用户授权合并实训 D2/D3/D6–D9 与MOD4可行reset。下表保留目标范围并更新本轮实训状态；实际适应成绩按最终报告，不凭范围已开宣布全过。

| 编号 | DR 项目 | 已有实现 / 当前状态 | 后续目标及采样方式 |
|---|---|---|---|
| D0 | 动作、传感器延迟 | 修正版已保留至 D1 完整训练与配对回放 | 动作组独立 `{5,10}` ms；传感器组独立 `{5,10,15}` ms。env reset 采样、episode 内固定；按物理子步推进，保持 100 Hz PD、50 Hz policy 和原始动作记忆槽 |
| **D1 已完成本轮** | **独立刚体质量** | **4096 环境 40 分钟完成；实际 DR 下 2.0→1.903（8/10）、2.2→2.155（9/10）；2.7 指令诊断→2.611，均无重置** | **机身 `0.9～1.3`；16 个指定腿部连杆和左右轮各自 `0.9～1.1`，每 env、每刚体独立。startup 采样后保持；各刚体惯量随自身质量同比例缩放。未选中的导向/传动刚体保持名义质量** |
| D2 | 机身质心 | 合并轮全范围已实训；适应结果见本轮FINAL_REPORT | 仅机身：X ±4 cm，Y/Z ±2 cm；startup 基于名义 COM 采样，禁止 reset 累加；不虚构腿部 COM 随机项 |
| D3 | PD 刚度、阻尼 | 合并轮全范围已实训；适应结果见本轮FINAL_REPORT | 各适用执行器 Kp、Kd 分别 `0.75～1.25`；按参考 reset 事件及 `min_step_count_between_reset=720` 的实际语义接入；不改控制频率和电机包络 |
| **D4 已完成一轮** | **电机输出比例误差** | **实现/探针通过，40分钟与8次检查完成；20m候选DR2.0→1.878（7/10）、2.2→2.146（9/10），其它四项各10/10；原冻结基线仍有优势，040m不选为默认起点** | 腿部输出 `0.8～1.1`；轮子 `0.9～1.1`，各执行器独立，按参考 reset 事件及 `min_step_count_between_reset=720` 的实际语义采样；最终写入力矩仍受原部署电机包络约束 |
| **D5 一轮完成** | **分部位接触材质** | 40min及1440env配对完成：候选010m实际DR2.0→1.9611(10/10)、2.2→2.2510(8/10)，其它四项10/10；后半程掉速，final不晋升；原主冻结保留 | startup：轮静摩擦 `0.5～1.2`、动摩擦 `0.4～1.0`、恢复 `0.02～0.2`；机身静/动 `0.01～0.1`、恢复 `0.02～0.2`；导向件静/动 `0.1～0.7`、恢复 `0.01～0.1`。保留参考 bucket 与 dynamic≤static 一致性 |
| D6 | 关节摩擦 | 合并轮全范围已实训；适应结果见本轮FINAL_REPORT | 恢复参考全范围、按选中关节独立 startup：主动腿静/动 `0.25～1.0`、粘性 `0.05～0.2`；轮静 `0.05～0.25`、粘性 `0～0.01`；被动腿静 `0.05～0.1`、粘性 `0.01～0.025`。具体关节选择依据原参考，禁止不同组相互覆盖 |
| D7 | 弹簧阻尼 | 合并轮全范围已实训；适应结果见本轮FINAL_REPORT | 目标阻尼 `0.5～1.5`，按参考 reset 事件；先核对真实符号和施加路径。参考 YAML 中 stiffness scale 固定 `0.01` 与本项目气弹簧合同需核清，不能顺手把原气弹簧刚度乘 `0.01`；本项不批准更改 plant |
| D8 | 外力、外力矩 | 合并轮全范围已实训；适应结果见本轮FINAL_REPORT | 全范围每轴 ±10 N、±1 N·m，间隔 5～10 s；施加坐标系和持续时间按参考事件实现核对，不仅对齐数值范围 |
| D9 | 观测噪声 | 合并轮全范围已实训；适应结果见本轮FINAL_REPORT | 全范围：角速度 ±0.25、重力投影 ±0.05、关节位置 ±0.025、腿关节速度 ±0.5、轮速度 ±1.0、高度 ±0.01；对齐原参考是在归一化前还是后的噪声，不污染命令和原始动作槽 |
| **D10 一轮完成** | **速度推扰** | 40min+1600env受扰评测完成；候选020m受扰后2.0→1.9341(8/10)、2.2→2.1914(7/10)，其它四项10/10，正式任务无reset；原主冻结保留，final不晋升 | 每 env 每 5～10 s 对机身**世界坐标 XY 速度加上**独立 `[-0.25,0.25]` m/s 增量；z 与角速度保持。已核对目标机原函数 `vel_w += ...`，此前“设置为区间内速度”的描述更正；native interval/reset 语义，记录触发与恢复轨迹 |

本次两项结果（2026-11-11）：D5与D10各完成一轮40min及每5min保存检查。D5选010m继续，D10另存020m候选（iteration22141，SHA `b3eec7bae3045b24a95ea7cd2940a3e1f0b062841cc47ab1785a627bea36408a`）；两轮后半程都有掉速，末权重不晋升。原Step7主冻结 `23c112...` 与配方不变。详见 [D5报告](sources/local/MOD4V3_STEP7_MATERIAL_20261111/FINAL_REPORT.md)、[D10报告](sources/local/MOD4V3_STEP7_VELOCITY_PUSH_20261111/FINAL_REPORT.md)。尚有表中全范围DR未完成，Rough未启动。

执行约束：

1. 每次续训只接入一个明确的 DR 变化项（D1 的质量与匹配惯量属于同一项），累计保留前面已适应的 DR；在独立运行目录固定源码、父检查点 SHA、范围和采样时机。当前后续累计DR候选为 D10 的 020m，iteration 22141，SHA `b3eec7bae3045b24a95ea7cd2940a3e1f0b062841cc47ab1785a627bea36408a`；D1 的 040m/final 主冻结继续保留作对照。已在跑的分布不热改；切换须先有完整检查点、退出原进程并确认 GPU 释放。
2. 默认沿用用户已授权的 **每轮 40 分钟、每 5 分钟完整保存并检查**。中止、续接、额外新轮分别记实际消耗；不能把较小范围训练算成完整目标 DR，也不能把未运行的计划当新训练授权。
3. 检查包括数值/闭链与完整保存，以及固定任务真实表现：前进 2.0/2.2 m/s（误差≤0.15）、后退 -1.5 m/s（≤0.20）、旋转 4.5π rad/s（≤2%）、高度 0.20/0.40 m（≤0.02 m），保留每项 10 初态结果和失败样本。沿用既有任务协议；MuJoCo 名义、PhysX 名义和实际 DR 结果分别报告，不能互相替代。回报提高不能单独作为晋升结论。
4. 当前质量最终权重的实际 PhysX DR：2.0→1.9031（8/10），2.2→2.1555（9/10），2.7 指令诊断→2.6106；各 10 初态均无重置，后退/旋转/两高度各 10/10。前进能力已恢复，可保留为后续适应基线；原跟踪误差未全通过的样本照实保留，不能笼统写成前进退化。名义 MuJoCo 2.2→2.7442、2.7→3.3678 的跨引擎过冲另列，不等同于当前 PhysX DR 失败，也不宣称部署已通过。2.7 仅是固定权重诊断，训练指令仍为 `[-2.2,2.2]` m/s。
5. MOD4 资产、35D actor/6D action、导出顺序、电机包络、闭链约束与冻结证据按项目合同执行。本计划不更换资产、不放宽现有门槛、不改变奖励或 solver 来凑通过。不加入华南虎参考未启用的独立惯量项、腿部质心项等额外科目。
6. 每项实际成功、失败、中止和回退都保留源码、配置、父子 SHA 和报告，依仓库既有工作流提交唯一 trial 记录。Git 推送使用 `127.0.0.1:7897` 代理；旧标签、失败报告和冻结权重不覆盖。
7. **下一步按 [Rough 课程计划](docs/ROUGH_CURRICULUM_README_20261111.md) 接入低难度地形。** 2026-11-11 已核实当前完整 DR 项目全开；建议以 square1_030m（iter22618、SHA `d5e17640…`）作为 R0 父候选，20m 备用，原冻结保留。保留全部 DR、当前奖励与 2.5/10/20ms 时序，初期20%平地与20%名义参数交叉分配，不要求先把Flat每项刷到10/10；名义欠速与跨引擎偏差继续列回归。旧 `rough_v0` 继承早期环境、只恢复actor，还会切换物理步长/solver并关闭闭链reset，不能直接换profile开训。新R0需从当前fullDR实现接地形、最低等级出生和实际升降级。详细华南虎Rough v0/v1、Flat v1/v2、rough_dash/rotation_translation对照及后续阶段见计划；R0首轮已完成2405.700s及配对评测，20m候选/5m备用；原Flat父保留，R1未运行，详见计划末节。

## Git 标签是什么

`trial-日期-编号-试验名` 对应一次有证据的试验、训练运行、修复/诊断、失败程序或保存源码变体。类别写在记录里；不是每个标签都代表一次成功训练。`version-local--...` / `version-remote--...` 对应原始资料目录的完整归档快照。标签直接指向本次创建的提交，可在 GitHub 的 **Tags** 或提交历史查看，也可以：

```bash
git clone https://github.com/lulunomaro/polar-rl-train.git
cd polar-rl-train
git tag -l 'trial-*'
git show <tag>
git switch --detach <tag>
```

这些是**补建的证据历史**：提交时间是真实归档时间，记录另列原试验日期及来源。没有把今天的提交伪装成当时提交，也没有根据目录名猜测作者。保存的运行源码快照可证明当时版本；仅有当前源码或报告的记录会明确写出证据等级。

## 收录内容

`sources/local/` 与 `sources/remote/` 保留原相对路径，包含代码、配置、报告、交接、备份和资产。`objects/sha256/` 是去重内容库，`provenance/capture_inventory.json` 记录原路径、字节数、时间、原始/归档哈希及采集方式。训练 `run_manifest` 的环境参数、源码指纹和可找到的 `src_snapshot` 一起保留；相邻运行配置差异有单独记录。

**模型权重和大型二进制轨迹没有上传到 Git。** [检查点索引](provenance/checkpoints.jsonl) 保留 11,429 个文件条目的路径、大小、时间和能从原凭据解析到的哈希；重复目录副本也计作文件条目。未读取权重内容，不伪造缺失哈希。原目标机/本机权重原样保留。大型日志保留明确标注的首尾摘录，详见归档范围。

## 以后每次修复怎么记

先写一份说明：问题、改动、配置/来源权重、检查协议、实际结果和仍失败的项目。再把改变的代码/配置/证据连同标签一起推送：

```bash
python archive_tools/record_experiment.py --id yaw6-regression-01 --title "6rad/s 回归复核" --kind evaluation --note-file notes/yaw6.md --files project/isaac/mod4/env.json reports/yaw6.json --validation "协议与结果见报告" --push
```

这是用法示例，需替换为真实文件。脚本拒绝覆盖标签、夹带已暂存的无关改动或提交权重/明文凭据。历史批量构建脚本仅用于本次首次归档，不应重跑来改写既有标签。

仓库只记录项目，不会启动训练、变更目标机预算或停止现有任务。上游代码与资产的原许可证/来源保留，[第三方说明](docs/THIRD_PARTY.md) 不替代原许可。


2026-11-11回放复核：同一mixed2_020m在MuJoCo名义超速、PhysX名义欠速；0/5ms复测保留方向，原训练actor观测与paired包装逐帧最大差0。尚无新确认的输入回放bug，物理/执行差异未定位，不能只凭跨引擎差异定为策略退化。完整DR同时有欠速和超速样本。详见`sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/replay_environment_check/REPORT.md`；未启动第三轮训练。


2026-11-11新授权：从与第二轮相同的remaining_010m父检查点（iter22265，978994b2…）单开40分钟，将超速/欠速对称平方惩罚−0.5e²→−1.0e²。其余沿用20%名义/80%完整DR，5分钟保存并检查。独立源与计划：`sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/README.md`，不覆盖旧轮或冻结模型。


双侧平方惩罚加倍实验已完成2400.870s，−1.0e²，其余同第二轮。保留square1_030m（iter22618，SHA`d5e176401c20dd1b88a74003f7d4993aadc9a9cda301f042953de08fb6108851`）供检查；原始结果见`sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/FINAL_REPORT.md`，全部PT实体归档。总20阶段/分支、88完整PT；不自动覆盖原冻结或开下一轮。


2026-11-11 R0首轮完成：2405.700s，保留rough_r0_020m（iter22785，SHA`64affb5794f5518f2b84611ab7d3904aef95b7e1ea660e1efd87820102cc14d6`）为R0实验候选；完整DR level0浅地形越障119→120/120，Flat正式44→40/60。此为同批诊断，不代表Rough全课程毕业；原Flat主冻结保留，R1未启动。报告与全PT见`sources/local/MOD4V3_ROUGH_R0_20261111/FINAL_REPORT.md`，当前总21阶段/分支、97完整PT。


2026-11-11 Flat速度平方项1.5独立实验已启动：从冻结square1_030m恢复，完整DR+20%名义参数，40分钟/5分钟完整保存；[配方和状态](sources/local/MOD4V3_FLAT_SQUARE15_20261111/README.md)。此次不接R0后期权重，不推进R1。


2026-11-11用户中途要求下个检查点切Rough：Flat平方项1.5段在020m/iter22856完整保存后结束，SHA`a5102af62938f6bf472855edba34c5f10efce061eecaeb3aebee34815fe7cf87`，已接续`MOD4V3_ROUGH_R0_SQUARE15_20261111`的R0余下20min。保留−1.5e²/fullDR/20%名义/20%平地；本轮预算按Flat20＋Rough20分配。新结果待同批PhysX配对，原冻结保持。


2026-11-11 Flat1.5→RoughR0接续已结束：Flat1204.923s后按用户要求在020m完整保存点切Rough，Rough再1201.085s，均每5min完整PT保存。保留Flat020m（iter22856，a5102af6…）回退，Rough010m（iter22941，ece8c411…）作实验候选；同批fullDR前进MAE分别0.12165/0.13866，正式44/60(reset0)/41/60(reset0)，Rough010m额外2.7诊断3reset如实保留。R0浅地形均120/120，未测出新增越障能力，Rough训练累计numerical1。原主冻结保留，未自动R1或追加训练。两段10份不同字节完整PT在各自weights目录，候选配方/本机目标机只读存档已完成；[最终报告](sources/local/MOD4V3_ROUGH_R0_SQUARE15_20261111/FINAL_REPORT.md)。总索引23阶段、107完整PT。


2026-11-11 R1首轮40分钟已获用户授权并启动：父Flat1.5_020m/iter22856/a5102af6…，新增中级正反阶梯及完整计划难度范围；Rough低速起步课程，平地组原技能继续；−1.5e²/fullDR/PPO/2.5ms/TGS32/4/2mm保留，每5min完整PT。训练和真实失败计数见[本轮记录](sources/local/MOD4V3_ROUGH_R1_20261111/README.md)。未自动R2。


## 2026-11-11 起摆站立实测

当前R1第二轮005m已经能从部分底盘落地随机腿姿态站起，但未达到随意摆腿可靠起身。固定权重同源PhysX：名义6/8、完整DR25/32达到高度/姿态保持；原逐帧接触严格统计另列。真实失败、准备期闭链中止及正常站姿5/5对照均保留。未训练。[报告、回放视频与逐份证据](sources/local/MOD4V3_GROUND_STAND_PROBE_20261111/README.md)。


## 2026-11-12 实车电控调试完整交付

[完整ZIP](deliveries/MOD4V3_R1_005M_REALCAR_DEBUG_20261112.zip) / [包内说明](deliveries/MOD4V3_R1_005M_REALCAR_DEBUG_20261112/README.md)。主模型是R1第二轮005m/iter22959/SHA0dcc15f5…，完整PT、ONNX、TorchScript、纯C推理/观测编码/动作映射/PD/包络、Windows与Linux示例、实际训练plant及subLayer、中文电控说明、硬件标定模板均随包。800份原环境接口样本及4096组网络输入对齐，8项独立ONNX回放无安全终止，干净目录解压运行通过。

实体电机方向/零偏/IMU安装及电流换算尚无实测标定，真实使能检查按预期阻断未填模板；高速超速和起摆未完整适应的原结果保留。本包是当前综合均衡候选的电控调试交付，不是实车验收或原主冻结晋升。没有训练、没有驱动实车，也没有修改旧部署plant来强行过门。


## 2026-11-12：按用户新指令统一推进 SCUT Rough-v0，2小时

用户明确要求直接训练华南虎Rough-v0科目，不再分R0/R1/R2逐个短轮。本次从综合接续父R1第二轮005m（iter22959，SHA0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f）恢复完整PPO/RNG，统一使用保存rough_rotation_stair的全部9地形族与10级难度，同时训练行进、小陀螺与组合指令。7200秒PPO，每300秒完整PT保存、下载核验和检查；本条是授权与执行计划，尚非训练成绩。

参考的top-level curriculum为空、height-offset curriculum关闭，所有地形行从启动一起采样；不再要求独立15cm落高探针作为此科目前置门槛。当前MOD435/78/6、2.5/10/20ms、TGS32/4、2mm单env保护、完整DR、20%名义/20%平地、−1.5e²和指数1.2保留；沿用2.2m/s上限和机身坐标语义，无云台观测。为4096env分散出生点，参考14列复制为70列，所有地形族仍在同一科目覆盖。

新目录：[统一科目README](sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/README.md)。原阶段历史、冻结及实车包保留；本轮新检查点未经比较不自动晋升。


## 2026-11-12：统一SCUT Rough-v0两小时已完成

按用户新指令，统一全部9地形族/10难度行和行进/小陀螺/组合指令，一次连续PPO7206.137秒，848更新；每5分钟保存，26份完整训练PT/25种不同字节，8组同批固定权重PhysX对照全部完成。完整DR最高代表档±1m/s穿越：父/100m/120m为134/133/131（各160），±2.2指令为145/148/144；旋转角速MAE为1.7066/1.8705/1.8548rad/s；PhysX名义Flat58/36/30（各60）。综合继续R1第二轮005m/iter22959/0dcc15f5…，本轮100m仅实验候选、120m未晋升。原冻结/实车包未替换，没有自动下一轮，也未重新引入拆分课准入。

[最终报告](sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/FINAL_REPORT.md) · [配方/全PT入口](sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/README.md)。本轮当前总索引29阶段、164个完整训练PT记录；短探针原件另保留。

## 2026-11-13 连续上台阶动作调查

冻结iter24692的4例动作/接触插桩：驱动轮撞立面、前导向小轮承力、前俯收腿抬轮、落轮后恢复再加速。原先约0.09m/s属于攀爬末段，不能按机身投影过阶沿认定已站稳一级。无训练、plant与模型不改。[慢放、分解图、完整报告](sources/local/MOD4V3_STAIR_MOTION_AUDIT_20261113/README.md)。

<!-- CONTINUOUS_STAIRS_200MM_20261113_START -->
## 2026-11-13 连续200mm台阶两小时专项（进行中）

从iter24692完整PPO接续：固定难度3水平尺寸、每级200mm/两级400mm，修正25.8°俯仰奖励硬门控，加入实际抬轮/落台/连续完成与阶间耗时奖励，原速度项/fullDR/35-78-6/电机与2mm单环境保护保持。RTX4090、2048env、7200秒；每5分钟完整PT及检查。首更新iter24693/Adam17已保存。[配方、进展、完整权重入口](sources/local/MOD4V3_CONTINUOUS_STAIRS_200MM_2H_20261113/README.md)。原成熟包不覆盖。
<!-- CONTINUOUS_STAIRS_200MM_20261113_END -->

<!-- CONTINUOUS_STAIRS_ROUGHV1_RETENTION_20261113_START -->
连续台阶已补回原Rough-v1，接续段50%台阶/30%粗糙地形/20%平地。候选continuous_stairs200_roughv1_retention_20261113_075m，iter25484，连续两阶8/10、平地40/60。 同一预算实际4614.497秒；[配方与结果](sources/local/MOD4V3_CONTINUOUS_STAIRS_ROUGHV1_RETENTION_20261113/README.md)，所有完整PT原件归档；原成熟包保留。
<!-- CONTINUOUS_STAIRS_ROUGHV1_RETENTION_20261113_END -->

<!-- CONTINUOUS_STAIRS_PARENT_MIXED_2H_20261113_START -->
从健康父iter24692起步，首轮即50%台阶/30%原Rough-v1粗糙地形/20%平地。候选continuous_stairs200_parent_mixed_2h_20261113_035m，iter25011，连续两阶0/10、平地60/60。 独立新轮实际5853.118秒；[配方与结果](sources/local/MOD4V3_CONTINUOUS_STAIRS_PARENT_MIXED_2H_20261113/README.md)，所有完整PT原件归档；原成熟包保留。
<!-- CONTINUOUS_STAIRS_PARENT_MIXED_2H_20261113_END -->

<!-- SCUT_STAIR_FINETUNE_2H_20261113_START -->
从父iter24692按SCUT方式微调，273宽阶/1365其余rough/410平地。候选scut_stair_finetune_2h_20261113_015m，iter136，连续两阶0/10、平地60/60。 独立新轮实际7203.603秒；[配方与结果](sources/local/MOD4V3_SCUT_STAIR_FINETUNE_2H_20261113/README.md)，所有完整PT原件归档；原成熟包保留。
<!-- SCUT_STAIR_FINETUNE_2H_20261113_END -->

<!-- OWN_STAIR_REPAIR_20261113_LAUNCH -->

恢复自有连续登阶配方：从健康父iter24692完整PPO接续，50%双级200mm台阶/30%原Rough-v1/20%平地；平地一半固定练原六项目标，用地面reset，保持原速度目标和登阶奖励。无PPO功能探针后独立40分钟，每5分钟保存及固定回放。当前状态与实际结果见[sources/local/MOD4V3_CONTINUOUS_STAIRS_OWN_REPAIR_20261113/README.md](sources/local/MOD4V3_CONTINUOUS_STAIRS_OWN_REPAIR_20261113/README.md)。

<!-- CONTINUOUS_STAIRS_OWN_REPAIR_40M_20261113_START -->
从健康父iter24692起步，首轮即50%台阶/30%原Rough-v1粗糙地形/20%平地。候选continuous_stairs200_own_repair_40m_20261113_010m，iter24783，连续两阶2/10、平地40/60。 独立新轮实际2401.524秒；[配方与结果](sources/local/MOD4V3_CONTINUOUS_STAIRS_OWN_REPAIR_20261113/README.md)，所有完整PT原件归档；原成熟包保留。
<!-- CONTINUOUS_STAIRS_OWN_REPAIR_40M_20261113_END -->


<!-- STAIRS_TRAINING_GUARD_REPAIR_20261113 -->
2026-11-13：连续台阶高度参考改为轮下中心射线，阶沿上行导轮接触按限定窗口放行，接触/倾角独立持续计时；新源码版本经2048环境600步冻结回放，numerical=0，仍执行2mm单环境重置。没有PPO更新。修正协议V3下，最新40m(iter25050)完整双阶1/10，15m(iter24830)为6/10（0.40m指令5/5）；旧分数保留原协议标签。最新窗口可手动操控，完整PT/配方/失败轨迹见[本次修复与回放说明](sources/local/MOD4V3_STAIRS_TRAINING_GUARD_REPAIR_20261113/README.md)。


<!-- STAIRS_PARENT_REPAIRED_40M_20261113_LAUNCH -->
新授权40分钟：修复台阶高度/导轮接触/独立终止计时后，从原父iter24692完整PPO重新开始，环境比例40%台阶/35%原Rough-v1/25%平地（819/717/512）；每5分钟完整保存与回放，不自动延长。[本轮配方与进度](sources/local/MOD4V3_STAIRS_PARENT_REPAIRED_40M_20261113/README.md)。


<!-- STAIRS_NO_PROGRESS_PARENT_40M_20261113_LAUNCH -->
上一轮前向超速未解决，按用户指令正常保存提前结束。新一轮从原父iter24692完整PPO重新开始40分钟，仅删除0.8×advance推进奖励，继续819台阶/717原Rough-v1/512平地；每5分钟完整保存及同协议回放。[本轮单项删除配方与结果](sources/local/MOD4V3_STAIRS_NO_PROGRESS_PARENT_40M_20261113/README.md)。

<!-- STAIRS_PARENT_REPAIRED_40M_20261113_START -->
从健康父iter24692起步，首轮即40%台阶/35%原Rough-v1粗糙地形/25%平地。候选stairs200_parent_repaired_40m_20261113_005m，iter24737，连续两阶5/10、平地40/60。 独立新轮实际1451.965秒；[配方与结果](sources/local/MOD4V3_STAIRS_PARENT_REPAIRED_40M_20261113/README.md)，所有完整PT原件归档；原成熟包保留。
<!-- STAIRS_PARENT_REPAIRED_40M_20261113_END -->

<!-- STAIRS_NO_PROGRESS_PARENT_40M_20261113_START -->
从健康父iter24692起步，首轮即40%台阶/35%原Rough-v1粗糙地形/25%平地。候选stairs200_no_progress_parent_40m_20261113_005m，iter24737，连续两阶5/10、平地40/60。 独立新轮实际2401.777秒；[配方与结果](sources/local/MOD4V3_STAIRS_NO_PROGRESS_PARENT_40M_20261113/README.md)，所有完整PT原件归档；原成熟包保留。
<!-- STAIRS_NO_PROGRESS_PARENT_40M_20261113_END -->

<!-- STAIRS_TEACHER_RETENTION_40M_20261113_START -->
持续教师保留PPO，从005m起步；候选stairs200_teacher_retention_40m_20261113_040m，平地40/60、两阶5/10。 实际2405.004秒，联合源5m保留=True；[配方与结果](sources/local/MOD4V3_STAIRS_TEACHER_RETENTION_40M_20261113/README.md)。
<!-- STAIRS_TEACHER_RETENTION_40M_20261113_END -->
