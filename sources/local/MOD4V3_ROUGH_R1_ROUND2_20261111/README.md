# R1 第二轮：原平方奖励＋完整 DR 续训

2026-11-11，用户明确授权新40分钟轮，每5分钟完整保存并检查。

- 父模型：R1_010m，iter22925，SHA `959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022`。
- 原R1速度项 `−1.5e²`，指数速度奖励权重1.2；完整DR与20%名义、20%平地保持。
- 完整PPO与已有R1地形课程状态恢复，新物理episode；4096env、LR3e-5 fixed、clip0.1、epochs3。
- MOD4、35actor/78critic/6action、物理2.5ms/PD10ms/策略20ms、TGS32/4、2mm单env闭链重置与电机包络保持。
- 本轮仍是R1浅地形/中级正反阶梯课程；R2是后续腾空落地预训练，待本轮结果判断。
- 状态：已启动，首个PPO更新完成。实际启动、恢复与保存收据见evidence。

配方见 [PLAN.json](PLAN.json)，每5分钟检查见evidence/training_round，完整PT见weights。按越障进度、耗时、重置和有实际恢复机会后的跟踪评判；0.5–3s混合窗口不直接作为稳态或退化结论。
