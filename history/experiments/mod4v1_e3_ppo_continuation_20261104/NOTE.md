# E3 单独续训与质量复测结果

## 结论
**本轮有效完成20次真实PPO更新并完整保存；新候选表现退化，保留原选中版本1cd，不替换演示、不晋升新候选a3ce，也未追加下一训练窗。**

本轮从上一轮完整PPO候选67ee（iter43110/Adam866460）接续，而非重放母版1cd已跑的20步，亦非旧SuperMimic分支。新候选a3ce相对母版1cd累计多40次PPO，其中本次20次。未对输入67ee做同样MuJoCo本地对照，因此差异不全部归因于本次20步。

## 实际训练
- 单4090，20,000环境，原PPO/fullD0–D7、原奖励/命令/接受判据，MOD4v1 400N/k2000/d3、50Hz/100Hz、.0025s/TGS32/4、closure/mimic .01均未改。
- 实际20 PPO updates、400 optimizer.step、480控制步、9,600,000 transitions；无未完成rollout。
- 完整保存iter **43130**、17 Adam一致step **866860**、实际LR **0.0002562890625000001**，actor/critic/STD/optimizer/DR/历史/队列/RNG及未知字段完整验证保留。
- 新检查点SHA：`a3cef1489614a018492bbe3078e752e3384604371ddaf7a3fa0062d728923fec`；14721171 bytes。训练执行成功、实际内外wait/费用结清/释放完整；技能判定另列。
- 首次W1在初始完整保存的旧“只接受母版”元数据检查处中断，尚未调用PPO；原producer更新计数缺失，未把它伪造为计数0或技能0%。W2仅为当前run_id使用独立保存元数据命名空间，旧元数据完整保留。两次实际成本均保留：W1 **408.095**、W2 **1164.245** expert-seconds（按原GO到实际parent terminal推导，非新账本）。

## 原Isaac恢复科目
N80、seed20260928、原13种recipe，160控制步/3.2s，原连续.5s稳定判据和第一episode范围不变。

| 子项 | 原选中1cd | 新a3ce |
|---|---:|---:|
| 请求恢复首episode稳定credit | 0/74 | 0/74 |
| 正常recipe首episode物理终止 | 0/6 | 0/6 |

新评测实际执行合格、1280物理/320反馈、0学习更新、完整关闭/wait/EX释放。终止事件：`{"time_out": 0, "bad_orientation": 19, "base_contact": 6, "closure": 0, "mimic": 0, "low_base": 0}`；事件可重叠，不加总成独立失败人数。该3.2秒原科目统计不是“任何场景都起不来”的结论，也不是实机毕业。

## 同一个后收平放上电场景：本地MuJoCo
与原基线采用同一个22关节后收闭链姿态、初始高度.18495m/平放/零速度、同一场景与动作映射，0–8s mode3/vx0，8–13s mode0/vx.2；全程同一个E3，不换E0。只运行新候选一次，旧zero-torque未重跑。

| 指标 | 原选中1cd | 新a3ce |
|---|---:|---:|
| 8s机身高度 | 24.19cm | 22.60cm |
| 8s倾角 | 0.62° | 14.59° |
| 恢复阶段世界X位移 | -0.857m | -6.044m |
| 恢复阶段世界Y位移 | +0.004m | -6.410m |
| 8s线速度（指令为0） | 0.042m/s | 1.880m/s |
| 8–13s世界X位移 | +1.202m | -1.483m |
| 13s倾角 | 1.85° | 22.63° |

新候选在零速度恢复指令下发生较大前后/侧向漂移，平衡与停稳明显差于当前使用版本。两者都在.36s一度达到参考高度/角度，**该穿越时刻不代表稳定起身成功**。世界位移与机身局部速度分开报告；不把旧CAD局部坐标vx直接当作世界前向跟踪指标。此处仅一个名义MuJoCo姿态诊断，不替代Isaac/fullDR/实机资格，也未建立本轮20步的严格因果归因。

## 保留策略与证据
原母版、67ee输入及新a3ce完整候选均保留，Registryv12/H1/当前可视回放未修改。原恢复credit无提升且本地上电保持更差，因此不采用新候选、不盲目再加一窗。

- [训练完整闭环](<mod4v1_e3_continue_v2_20261104/TRAIN_CLOSED_RESULT.json>)
- [原N80逐recipe评测](<mod4v1_e3_continue_v2_20261104/E3_ORIGINAL_FROZEN_SCOPE_RESULT.json>)
- [新候选本地紧凑结果](<mod4v1_e3_continue_v2_20261104/mujoco_startup/SUMMARY.json>)
- [旧选中版本上电基线](<mod4v1_e3_stowed_startup_20261104/SUMMARY.json>)
- [W1实际失败及最小保存修复](<mod4v1_e3_continue_v2_20261104/W1_FAILURE_AND_V2_METADATA_FIX.json>)
- [本地评测源AST读者错误及修复](<mod4v1_e3_continue_v2_20261104/EVAL_LOCAL_AST_READER_FAILURE_AND_V2_FIX.json>)，发生在SSH/新root/SDK之前，未重跑旧评测。

本报告及本轮源码、实际失败/结果将合并一次feature-only annotated trial归档，最终远端核验以工具返回为准；不为Git重开权重或原始轨迹。

W1 actual startup-save guard failure and costs remain preserved, not relabeled success. W2 changed only current-window save metadata namespace in the worker, retained all source roots and original PPO/full20k/fullDR state. The one-GPU owner uses original accounting and resource/close/wait logic with producer eligibility for the previously saved complete candidate. Original selected1cd mother, H1 and Registryv12 are unchanged unless the report explicitly records a later separate scoped decision. Independent native original-skill and local startup diagnostics remain distinct from hardware qualification. Weights/large originals stay at their producer paths; no model or trajectory was reopened for Git.
