# MOD4 DR 训练配方、阶段模型与续训索引

记录日期：2026-11-11，Asia/Shanghai。首次入口覆盖17个阶段/分支、61份检查点；追加本轮后共18个阶段/分支、70份完整检查点；原始试错、失败、提前停止和后续修复并列保留。首次总档案只整理已有成果；其后用户明确开训，新增剩余DR合并轮的实时状态与最终结果另行追加，旧原始记录保持。

**当前最新完整DR诊断候选为第二轮 `mixed2_020m`，实际父是第一轮 `remaining_010m`；此前已接受范围接训/回退仍为`push_020m`，原 Step7 `mass_040m` 主冻结保持。诊断候选未晋升，完整PT实体均在Git。**

- [逐份模型完整索引（SHA、iteration、父子关系、配方、原始两端路径）](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json)
- [全部 61 份模型表和直接下载入口](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md)
- [取回模型、准备新运行目录、续训与检查方法](DR_TRAINING_RESUME_20261111.md)
- [原始报告、补收证据和源码入口](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/README.md)

2026-11-11追加：[剩余DR合并轮](../sources/local/MOD4V3_STEP7_REMAINING_DR_20261111/README.md)已从push020m完整恢复，4096env/40min/5min保存；COM、PD、摩擦、阻尼、外力、噪声full范围与MOD4可行reset一起开启，这是启动时状态；现已完成一轮，适应尚未完成，实际结果见下面最终报告。

本轮已完成：[合并DR最终报告](../sources/local/MOD4V3_STEP7_REMAINING_DR_20261111/FINAL_REPORT.md)。本轮完整DR前进诊断候选为 **remaining_010m**，iter22265，SHA`978994b2614f4454f96bfd0ac264f00cbe3ffd219a5372487c558435503dbd15`；2.0→1.90988（4/10）、2.2→2.18903（6/10）；正式任务39/60、reset=0。原61份初次档案与下面历史阶段成绩保持，新增完整PT见[模型表末节](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md)。

最新第二轮结论：**20%名义采样只带来有限改善，名义前进尚未恢复。** 本轮保留mixed2_020m，iter22502，SHA`15775671f430cda69b1f268a230d85c5d1a74878760d26625afefb759e792c20`；同批完整DR前进11/20、正式41/60、reset0，PhysX名义前进0/20。25m综合43/60但1reset单独备用；40m不选。见[第二轮报告](../sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/FINAL_REPORT.md)，当前总索引19阶段/分支、79份完整PT；此前已接受范围的接续仍是push020m，原主冻结不变。

## 1. 首次归档时的候选与冻结模型

下表“最佳”指该轮已经测试的训练检查点中选出的候选；不是跨阶段、跨引擎、所有 DR 分布上的统一最优。每轮最后一个检查点不自动晋升。

| 角色 | 模型实体 | iteration | 已有同源 PhysX 证据 | 选择与使用 |
|---|---|---:|---|---|
| 当前累计 DR 接训候选 | [速度推扰 020m](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/weights/push_020m.pt) | 22141 | 受扰后 2.0→1.93406（8/10）、2.2→2.19139（7/10）；后退、旋转、两高度 40/40；正式任务 reset=0 | 速度推扰阶段可用，累计保留 DR 继续推进。额外 2.7 诊断有 1 次 reset；尚未全部 DR 毕业 |
| 原 Step7 主冻结 | [质量轮 040m/final](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/weights/mass_040m.pt) | 21754 | 当轮实际 DR：1.90307（8/10）、2.15548（9/10）；其它四项 40/40，无 reset；2.7 诊断 2.61062 | 模型和配方固定保留，用作回退及对照；不被后续候选覆盖 |
| 材质轮保留模型 | [材质 010m](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/weights/material_010m.pt) | 21882 | 1.96108（10/10）、2.25097（8/10）；其它四项 40/40，无 reset | 已作为速度推扰轮的实际父权重 |
| 输出倍率轮备用 | [输出倍率 020m](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/weights/effort_020m.pt) | 22017 | 1.87778（7/10）、2.14561（9/10）；其它四项 40/40，无 reset | 本轮最佳训练候选；材质轮实际未接这份权重 |
| 原始谱系基线 | [旧 Stage5 final](../sources/local/MOD4V3_SCUT_INCREMENTAL_DR_20261109/weights/stage5_obs_delay_40m_final.pt) | 20838 | 原 MuJoCo 固定任务前进等 10/10；后续修复版 PhysX 前进成绩单独保留 | 实际旧 7a 和集中修复的父权重；以 SHA 884cd07b…识别 |

完整 SHA256：

| 模型 ID | SHA256 |
|---|---|
| `push_020m` | `b3eec7bae3045b24a95ea7cd2940a3e1f0b062841cc47ab1785a627bea36408a` |
| `mass_040m` | `23c112b16e9629215c7265124925daaf0f9b6bbbb62be61689c714ba1fc7a772` |
| `material_010m` | `49a2bb7b53d3d88b7d47dfc3d5eb15999c5fd8fcfd3a1cf3f0a67d96030c71a1` |
| `effort_020m` | `0a1a8ccb5d1f5cec1582e071798597baa55e43dfb13e4eba6472a7fd82f3b22c` |
| `stage5_obs_delay_40m_final` | `884cd07b3942df9c8484b905994e302906c84151f6f9c5d079a417ec98158f24` |

用户已确认 **Step6 晋升冻结**，本档案保留这一状态。历史磁盘上带 `stage6/6b/6c` 的三个旧试验文件按各自 SHA 归档，不用文件名替用户重新指定冻结身份。后续实际接训入口绑定上表的精确模型。

## 2. 实际父子关系

```text
partial-base 075m → Stage1 final
                    → Stage2 初轮 025m → cont10m → cont20m
                                                    ├→ cont30m（对照，未接主线）
                                                    ├→ Stage2b（奖励试验，未接主线）
                                                    └→ Stage3 20m → cont10m_r1 → cont10m_r2
                                                          → Stage4 first segment → cont20m/final
                                                          → Stage5 final 884cd07b…
                                                               ├→ 旧 6 / 6b / 6c（各自直接取同一父）
                                                               ├→ 旧 7 / 7a（前进退化，保留对照）
                                                               ├→ 物理延迟 005m（未晋升）
                                                               └→ 集中修复（固定权重，无 PPO）
                                                                    → 平方项过渡 015m f4960781…
                                                                    → Step7 范围纠正 015m 74c25dd1…
                                                                    → 质量 040m 23c112b1…（主冻结）
                                                                         ├→ 输出倍率 020m 0a1a8ccb…（备用）
                                                                         └→ 材质 010m 49a2bb7b…
                                                                               → 推扰 020m b3eec7ba…（当前接训候选）
```

**材质轮配方启用了累计输出倍率 DR，但其权重父是质量 040m，不是输出倍率 020m。** 输出倍率轮后半程掉速，原质量冻结模型仍保留为后续起点。阶段目录的先后顺序不等于权重逐轮相接。

## 3. 早期阶段记录

早期阶段共同证据：[原 RECIPE](../sources/local/MOD4V3_SCUT_INCREMENTAL_DR_20261109/RECIPE.json)、[原 MODEL_INDEX](../sources/local/MOD4V3_SCUT_INCREMENTAL_DR_20261109/MODEL_INDEX.json)、[本次补收的 RESTORE/FINAL/五分钟收据](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/early_evidence/)。各文件实体和完整 SHA 都收在模型表中。

| 阶段 | 当时新增项 / 实际方法 | 保留与实际接续权重 | 已有选择依据 / 局限 |
|---|---|---|---|
| 轻量 DR 基座 | 统一质量/惯量因子 0.9～1.1、增益 0.9～1.1、base COM ±1cm、轻量材质和力矩噪声 | `base_partial_75m`，iter17133；101m 另存 | Stage1 实际从 075m 接；101m 前向误差略小也不改写实际父子关系 |
| Stage1 | 原 DR + 关节摩擦参考范围的 50%；4096 env，实际 3600.940s | `stage1_joint_friction_final`，iter18166，`c2b5299d…` | 后续 Stage2 的实际父；原名义 MuJoCo 2.0/2.2 实速 2.12634/2.32229。未做全检查点同源 DR 排名，不能补称全局最优 |
| Stage2 | 再加气弹簧阻尼 25%，scale 0.875～1.125；名义阻尼3.0，附加阻尼力矩上限±10Nm | `stage2_spring_damping_cont20m_final`，iter19152，`ffbabfe5…` | 初轮曾从 025m 回取后续训10m、20m，再试cont30m；cont20m名义前向2.04243/2.21223，cont30m过冲，不是Stage3父 |
| Stage2b | 同时改多个速度奖励项的10m分支 | `stage2b_speed_preserve_10m_final`，iter19336，`a58f8923…` | 2.2命令→2.44793；未接主线，不作为后来单项平方惩罚的成功证明 |
| Stage3 | 累计外力/力矩25%：各轴±2.5N/±0.25Nm，5～10s，hold10策略步 | 20m `6ccdfebc…` → cont10m_r1 `5d1b4013…` → cont10m_r2 `f25cc7a7…`，iter19724 | Stage4 RESTORE确实读取r2；三个 `.pt` 和两次续训的原始记录都保留 |
| Stage4 | 累计观测噪声25%，只作用actor输入 | 末段 final `74d65e18…`，iter20285 | 历史名称“40m”：首进程因iteration20000在1162.965s结束，后段1202.981s；实际更新2365.946s，未补写成精确2400s。原固定初态yaw按当时明确的±2%工程容差冻结 |
| Stage5 | 再加旧一策略步20ms观测延迟 | final `884cd07b…`，iter20838，实际2401.595s | 原固定10初态前进、后退、旋转、高度通过；旧输入定义不冒充后来的物理时间延迟实现 |
| 旧6/6b/6c对照 | 分别100%/50%/25%的一策略步20ms动作延迟；三个都从884父读取，并非串接 | 三个各自final已进Git | 原名义10初态前向2.0/2.2分别约0.32758/−0.01476、0.62881/0.23127、0.74166/0.22389；保留失败，不据此改判用户确认的Step6冻结状态 |
| 旧7/7a | 旧7用策略tick范围；7a固定20ms动作和传感器组，上一动作槽含已应用动作 | 7a final `0da8f78e…`，iter21103；005/010/015m同时归档 | 7a零延迟名义回放2.0→0.4974、2.2→0.2360，随训练退化；旧7没有FINAL，只有已有startup/restore/progress，不虚构完成模型 |

这些早期训练的 PPO 用原 adaptive schedule、5 epochs、clip0.2；恢复父检查点实际 LR 后继续调度。名义配置初始LR1e-4不代表每个续训都以1e-4运行，实际保存LR见 [LOCAL_MODEL_READBACK](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/LOCAL_MODEL_READBACK.json)。最近修复线改为 fixed3e-5、3epochs、clip0.1，不能把两套方法混写。

## 4. 修复与当前适应阶段

| 阶段 | 变化 / 实际完成范围 | 接续与保留模型 | 报告 |
|---|---|---|---|
| 物理时间延迟诊断 | 固定权重回放；5ms buffer、传感器5ms；原100HzPD下一刷新约10ms生效 | 884父短延迟下原任务通过；不是新模型 | [延迟诊断](../sources/local/MOD4V3_STEP7_DELAY_DIAG_20261110/REPORT.md) |
| 物理延迟5m适应 | reset按组0/5ms；低LR、完整PPO恢复；当时COM/摩擦/外力hold问题尚未修 | `bc22ea7a…`，iter20905，300.478s；未晋升，后续没有以它为父 | [5m试验](../sources/local/MOD4V3_STEP7_PHYSICAL_DR_ADAPT_20261110/REPORT.md) |
| 集中DR修复 | 修COM累加、摩擦分组覆盖、外力hold、力矩噪声累加及限幅/零力矩、native guard索引、critic槽 | 固定884父，无PPO新权重；4096×300 numerical0，PhysX前向仍欠速 | [实现修复](../sources/local/MOD4V3_STEP7_DR_REPAIR_20261110/REPORT.md) |
| 速度平方项 | 原有效`−0.00625e²`改为`−0.5e²`，指数奖励保留；超速/欠速对称。过渡DR仍为0/5ms | 015m `f4960781…`，iter21036，检查点903.181s；实际段计费949.001s后停止，未完成40m | [平方项](../sources/local/MOD4V3_STEP7_FORWARD_SQUARE_20261111/REPORT.md) |
| Step7延迟范围纠正 | 动作{5,10}ms，传感器{5,10,15}ms；沿用平方项。原轮剩余预算另段接续 | 015m `74c25dd1…`，iter21234，904.451s检查点；用户要求接质量后提前结束，没有伪造FINAL/SAFE_CLOSED | [范围纠正](../sources/local/MOD4V3_STEP7_FORWARD_SQUARE_RANGEFIX_20261111/REPORT.md) |
| D1 独立质量 | base0.9～1.3，16腿连杆+2轮各0.9～1.1；startup逐env逐body，惯量随本body质量缩放；40m完成 | `mass_040m`，23c112b1…，主冻结 | [质量结果](../sources/local/MOD4V3_STEP7_BODY_MASS_20261111/FINAL_REPORT.md)、[完整冻结配方](../sources/local/MOD4V3_STEP7_FROZEN_20261111/RECIPE.json) |
| D4 输出倍率 | 腿0.8～1.1、轮0.9～1.1，逐env逐电机；首次reset及距上次≥720全局策略步的reset抽样；40m完成 | `effort_020m`，0a1a8ccb…；final前进退化，不选 | [输出倍率结果](../sources/local/MOD4V3_STEP7_EFFORT_SCALE_20261111/FINAL_REPORT.md) |
| D5 材质 | 累计D4配方，从mass040权重另起；轮/机身/导向独立bucket材质；40m完成 | `material_010m`，49a2bb7b…；已接推扰 | [材质结果](../sources/local/MOD4V3_STEP7_MATERIAL_20261111/FINAL_REPORT.md) |
| D10 速度推扰 | 累计D1+D4+D5及Step7其余项；每env5～10s给世界XY速度加±0.25m/s；40m完成 | `push_020m`，b3eec7ba…；阶段可用，保留累计DR继续；final掉速，不选 | [推扰结果](../sources/local/MOD4V3_STEP7_VELOCITY_PUSH_20261111/FINAL_REPORT.md) |

近四轮实际训练秒数：质量2400.147、输出倍率2401.976、材质2400.734、推扰2404.033。每轮4096环境，300s完整PPO检查点并检查；末尾完整update/保存收尾会有数秒差异。

## 5. push020m父模型的累计DR配方（合并轮前）

精确执行依据为 [推扰轮 PLAN](../sources/local/MOD4V3_STEP7_VELOCITY_PUSH_20261111/PLAN.json)、[实际 STARTUP](../sources/local/MOD4V3_STEP7_VELOCITY_PUSH_20261111/evidence/train040m_velocity_push_r1_STARTUP.json) 和该目录 support；下表是便于查找的展开。

| 项目 | 当前数值与采样 / 施加方式 |
|---|---|
| D0 延迟 | 物理2.5ms、PD10ms、策略20ms。5ms量子；动作腿/轮组{5,10}ms，4传感器组{5,10,15}ms；每env每组reset采样，episode固定；只延迟actor4:22，22:28保留原策略动作，critic不延迟，低通关闭。buffer到期不等于立刻刷新PD |
| D1 质量 | base0.9～1.3；16指定腿连杆、2主轮各0.9～1.1；startup逐env逐body独立，跨reset保持；其它刚体名义质量；每body惯量同比缩放 |
| D2 COM | 仅base，XYZ各±0.01m；从名义COM+delta重采，不能跨reset累加。全范围仍待接入 |
| D3 增益 | 继承轻量腿/轮增益0.9～1.1和原混合；腿Kd=2固定，尚非全Kp/Kd0.75～1.25 |
| D4 输出倍率 | 各主动电机独立；腿0.8～1.1、轮0.9～1.1；eligible reset重采。完整raw PD合力矩乘倍率→原DC包络→原噪声→再次包络；不乘被动气弹簧，不改电机常数 |
| D5 轮材质 | static0.5～1.2、dynamic0.4～1.0、restitution0.02～0.2，64buckets |
| D5 机身材质 | static/dynamic0.01～0.1、restitution0.02～0.2，64buckets |
| D5 导向材质 | static/dynamic0.1～0.7、restitution0.01～0.1，8buckets |
| D5 时机/一致性 | startup逐env逐选中collider bucket；dynamic=min(dynamic,static)，选中材质跨reset固定。未选中shapes继承原Step7轻量材质reset；不是全名义。critic六个材质槽记录左右轮三元组，未新增base/guide专属槽 |
| D6 关节摩擦50% | 主动腿static/dynamic0.125～0.5、viscous0.025～0.1；轮static/dynamic0.025～0.125、viscous0～0.005；被动static/dynamic0.025～0.05、viscous0.005～0.0125；分组写回，互不覆盖 |
| D7 弹簧阻尼25% | scale0.875～1.125，名义阻尼3.0，附加力矩±10Nm限幅；本项不更改气弹簧刚度 |
| D8 外力25% | 每轴±2.5N、±0.25Nm，间隔5～10s，hold10策略步并递减；不与D10速度增量混为一项 |
| D9 观测噪声25% | actor槽：height±0.0025；角速度±0.0625；重力投影±0.0125；关节位置±0.00625；腿速±0.125；轮速±0.25。只在原对应归一化观测流加噪，不污染命令/原始动作槽。旧summary误名已在修复中纠正 |
| D10 推扰 | 直接调用安装的IsaacLab原函数`push_by_setting_velocity`；其实现实际是世界XY速度**加增量**±0.25m/s，z/角速度保持。逐env5～10s，native post-step interval，episode reset重采timer |

## 6. 训练、评测与恢复的口径

当前固定PPO：LR3e-5、clip0.1、3epochs、4minibatches、rollout24、gamma0.99、lambda0.95、entropy0.005、valuecoef4、maxgrad1。actor/critic均ELU256/128/64，无观测归一化；actor35、critic78、action6，actionclip±6。完整值见 [实际 PPO_EFFECTIVE](../sources/local/MOD4V3_STEP7_VELOCITY_PUSH_20261111/evidence/train040m_velocity_push_r1_PPO_EFFECTIVE.json)。

奖励速度误差沿用训练实现的水平前向投影：`e = v_cmd − v_body_x*cos(pitch)`。指数追踪权重1.2保留，平方项每秒`−0.5e²`，每20ms仅乘一次dt。它同时罚超速和欠速。训练有效vx范围为[−2.2,2.2]；2.7只作为额外固定指令诊断，旧base默认2.7没有覆盖当前profile，见 [命令范围核对](../sources/local/MOD4V3_STEP7_BODY_MASS_20261111/evidence/COMMAND_CAP_CHECK.json)。

每5min的MuJoCo名义回放用于观察检查点变化；末轮同源PhysX实际DR配对用于选择接训候选。不能用名义MuJoCo过线替代实际DR评测，也不能用跨轮不同随机分布的均值推断单项因果。原前进误差≤0.15m/s、后退≤0.20m/s、yaw相对±2%、高度±0.02m的协议保留；不另加“所有初态10/10才能继续DR”的新门槛。

**完整PPO恢复与精确物理瞬时状态恢复分开。** `.pt`保存actor/critic/std/Adam/LR/globalRNG，恢复后fresh physical episode；不恢复旧奖励/命令张量。D5/D10历史运行的新增材质及推扰timer/count/delta额外kwargs未写入checkpoint，原记录已说明，见 [CHECKPOINT_STATE_SCOPE](../sources/local/MOD4V3_STEP7_VELOCITY_PUSH_20261111/evidence/CHECKPOINT_STATE_SCOPE.json)。这不把PPO恢复变成仅actor恢复，但不能承诺逐物理状态续接。未来修补文件已单独保留，没有修改历史运行源码。

本轮遵守最新用户给定2mm闭链单环境episode reset；保留MOD4闭链资产、动作顺序与电机包络，不以单环境reset整批停训。历史原始快照的guard语义只作历史记录，不改原失败为pass。

## 7. Git保存范围与历史定位

本次用户明确要求`.pt`本体入Git，覆盖旧“仅存地址/SHA”的归档规则在本阶段的适用范围。**61份完整检查点全部有仓库路径，其中59份新增、2份Stage4/5复用已有Git实体；总计329,673,213字节。** 每份约5～6MB，使用普通Git二进制blob；没有LFS指针，也不需要另外找模型下载源。`040m`与`final`相同字节只存一份，别名在索引中记录。训练大型轨迹、视频和外部仿真依赖仍按实际路径/SHA索引。

原始source/report/recipe保持当时内容。本次集中索引纠正后续使用口径，不回写冻结manifest或把原报告“未运行/失败”改成完成。所有新补收文件带原路径、原字节SHA和归档位置，见 [COLLECTED_EVIDENCE_INDEX](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/COLLECTED_EVIDENCE_INDEX.json)。

| 阶段档案 | 原标签 | commit（前12位；完整值在MODEL_REGISTRY） |
|---|---|---|
| 早期轻量DR基座 | `mod4v3-incremental-dr-20261109` | `326bd3919026` |
| Stage1 关节摩擦50% | `mod4v3-incremental-dr-20261109` | `326bd3919026` |
| Stage2 弹簧阻尼25% | `mod4v3-incremental-dr-20261109-cont30m` | `3a47f9853eb7` |
| Stage2b 速度奖励试验 | `mod4v3-incremental-dr-20261110-speed-preserve` | `7ee470864f2e` |
| Stage3 外力/力矩25% | `mod4v3-incremental-dr-20261110-stage3` | `7e2047e3d867` |
| Stage4 观测噪声25% | `mod4v3-stage4-obs-noise-40m-20261110` | `7cd85aaed4d5` |
| Stage5 旧20ms观测延迟 | `mod4v3-stage5-obs-delay-40m-20261110` | `f124715254ce` |
| 物理时钟5分钟适应 | `trial-20261110-step7-adapt-forward-audit-01` | `5fa142e55a86` |
| 集中修复DR实现，无PPO | `trial-20261111-step7-parent-dr-repair-01` | `f1a18c7344d8` |
| 速度平方项与过渡延迟训练 | `trial-20261111-step7-forward-square40m-01` | `ad5d5a8be84d` |
| Step7物理延迟完整范围 | `trial-20261111-step7-body-mass40m-01` | `8b6283508c10` |
| D1 独立刚体质量 | `trial-20261111-step7-mass-final-command27-01` | `bbe8e4507533` |
| D4 电机输出倍率 | `trial-20261111-step7-effort-final-eval-01` | `cea8e6da24e4` |
| D5 分部位接触材质 | `trial-20261111-step7-material-final-push-start-01` | `4c9f7553275b` |
| D10 世界XY速度推扰 | `trial-20261111-step7-two-dr-final-01` | `12240524faa6` |

本次统一模型/配方档案标签：`trial-20261111-dr-training-catalog-pt-01`。旧6/7早期新增补收证据通过此标签归档；表中早期标签指当时已有源/报告，不声称后来补收的文件在旧标签中早已存在。推送走127.0.0.1:7897。

## 8. 接下来仍有什么DR

当前速度推扰阶段可以累计保留继续。用户随后明确授权D2全范围机身COM、D3全Kp/Kd、D6摩擦、D7弹簧阻尼、D8外力、D9噪声与MOD4可行reset合并40分钟训练，覆盖本轮每次只改一项的旧安排；实现范围见[本轮PLAN](../sources/local/MOD4V3_STEP7_REMAINING_DR_20261111/PLAN.json)，本轮现已完成，配对已看到完整DR部分改善和PhysX名义前进回归，适应未完成。Rough尚未启动；进入时保留已适应DR并接低难度课程，旧rough_v0只载actor且不自动继承当前修复链，不能直接把profile字符串换成rough就当全部接好了。


第二轮更新：fixed20%名义/80%完整DR的40分钟轮已完成，同源配对与全部完整PT已归档。保留mixed2_020m（iter22502，SHA`15775671f430cda69b1f268a230d85c5d1a74878760d26625afefb759e792c20`）供检查；结果与使用范围见`sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/FINAL_REPORT.md`，原已接受候选/主冻结未自动替换。总索引现为19阶段/分支、79份检查点。


2026-11-11回放复核：同一mixed2_020m在MuJoCo名义超速、PhysX名义欠速；0/5ms复测保留方向，原训练actor观测与paired包装逐帧最大差0。尚无新确认的输入回放bug，物理/执行差异未定位，不能只凭跨引擎差异定为策略退化。完整DR同时有欠速和超速样本。详见`sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/replay_environment_check/REPORT.md`；未启动第三轮训练。


2026-11-11新授权：从与第二轮相同的remaining_010m父检查点（iter22265，978994b2…）单开40分钟，将超速/欠速对称平方惩罚−0.5e²→−1.0e²。其余沿用20%名义/80%完整DR，5分钟保存并检查。独立源与计划：`sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/README.md`，不覆盖旧轮或冻结模型。
