# 连续台阶与Rough-v1能力保留实际结果（2026-11-13）

状态：superseded by human request: stop prior trial and launch fresh7200s from healthy iter24692。原预算7200秒；专项段2708.201秒，混合接续段1906.296秒，合计4614.497秒，不另开两小时。保留19份实际完整PPO，actor35/critic78/action6、17项Adam、LR/RNG/DR均读回核验。

候选continuous_stairs200_roughv1_retention_20261113_075m，iter25484，连续两阶8/10、平地40/60。

阶段一80%连续台阶/20%平地；用户纠正后阶段二50%连续200mm台阶＋30%原Rough-v1非平地＋20%平地，十类粗糙地形/十级，原速度/转向/高度/落地恢复采样。附加登阶奖励与定制起点/指令仅限专项环境。完整DR、MOD4 R3资产、电机包络、400Hz轮/100Hz腿/50Hz策略、原速度−1.5e²＋指数项、2mm单环境保护未改。

根父iter24692固定连续两阶2/10、平地60/60；阶段一30m平地40/60已退化。环境占比代表实际训练分布，不能证明能力恢复。原成熟模型保留，无自动晋升。

| 段 | 检查点 | 完整连续两阶/10 | 阶间耗时s | 平地/60 | 下阶/5 |
|---|---|---:|---:|---:|---:|
| 1 | model_005m.pt | 3 | 1.454 | 40 | 5 |
| 1 | model_010m.pt | 3 | 1.529 | 40 | 5 |
| 1 | model_015m.pt | 3 | 1.292 | 40 | 5 |
| 1 | model_020m.pt | 2 | 1.214 | 40 | 5 |
| 1 | model_025m.pt | 2 | 1.118 | 40 | 5 |
| 1 | model_030m.pt | 6 | 3.011 | 40 | 5 |
| 1 | model_035m.pt | 8 | 3.412 | 40 | 5 |
| 1 | model_040m.pt | 5 | 4.088 | 40 | 5 |
| 1 | model_045m.pt | 7 | 1.170 | 40 | 5 |
| 1 | model_final.pt | 7 | 1.119 | 40 | 5 |
| 2 | model_050m.pt | 4 | 0.990 | 40 | 5 |
| 2 | model_055m.pt | 5 | 1.000 | 40 | 5 |
| 2 | model_060m.pt | 5 | 1.002 | 40 | 5 |
| 2 | model_065m.pt | 7 | 1.133 | 40 | 5 |
| 2 | model_070m.pt | 5 | 0.996 | 40 | 5 |
| 2 | model_075m.pt | 8 | 1.476 | 40 | 5 |
| 2 | model_final.pt | 5 | 0.989 | 40 | 5 |


用户要求重新从健康父模型开训，旧轮收尾的额外GPU回放取消；此次旧轮不再申请这4组回放，不把取消项写通过。原始逐地形、逐方向、名义/完整DR、穿越/旋转/落地结果及轨迹在evidence/rough_retention，聚合在evidence/ROUGH_RETENTION_SUMMARY.json；失败和未收齐均不写通过。使用原Rough-v1地形和判定，轮反馈匹配当前400Hz。本实验名义MuJoCo台阶和平地结果不能代替完整DR或实车毕业。

执行配方、切换保存点、前后预算、来源、恢复和实际环境分布分别在PLAN.json、evidence/SWITCH_COMPLETE.json、evidence/training/RESTORE.json与TERRAIN_STARTUP.json。两段全部保存点、失败和报告随Git保存，PT为完整普通blob。
