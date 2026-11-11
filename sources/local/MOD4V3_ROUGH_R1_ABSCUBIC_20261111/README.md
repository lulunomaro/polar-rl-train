# R1 二次项叠加绝对三次项：本轮已完成

2026-11-11，用户要求下一个检查点加强速度惩罚。实际速度项为−2e²(1+|e|/1m/s)，保留二次项、叠加对称绝对三次项；指数项1.2和原门控保持。三段PPO实际合计2400.031秒，每5分钟完整PT与回放，未另开40分钟。

**结论：名义PhysX跟踪改善，完整DR偏速未解决；本轮不晋升三次项模型。** 三次005m名义六项60/60，但fullDR前进MAE0.29700/正式33/60，原Flat同批0.12888/43/60。三次010m在R1 level3穿越143/160，对照139/160，同时有平地正式4次reset和低身精度下降。MuJoCo名义最终仍明显超速。

- [最终同批结果](FINAL_REPORT.md)：PhysX名义/fullDR、R1两个难度、MuJoCo诊断与真实失败。
- [模型选择与下一步](DECISION.md)：保留Flat1.5_020m回退；R1_010m实验候选、三次005m名义备用；全PT和配方位置。
- [训练配方](PLAN.json)：父square2_015m/iter23027/SHA22513a6e…；完整PPO和课程等级/累计计数恢复，新物理episode。
- [完整PT索引](evidence/MODEL_ARCHIVE_INDEX.json)：本段4份完整PT；前两段另7份，全部Git实体。
- [分段时间](evidence/ROUND_SEGMENTS.json)：756.803s＋903.074s＋740.153s。
- [速度与OOD说明](SPEED_AND_OOD.md)：偏速是跟踪问题，是否OOD还需实际训练分布证据。

地形、DR、指令、PPO、MOD4接口/时序/solver/2mm单env重置保持。训练累计numerical12，三组固定评测numerical均0、action槽误差0、电机包络超出0。原始失败/提前切段收据保留。原Step7主冻结保持；后续先固定权重定位DR敏感项，不自动R2或追加训练。Git网络操作7897代理。
