# 父模型起步混训两小时实际结果（2026-11-13）

状态：superseded by human request for a new SCUT-reference7200s run。用户明确重新授权从父模型训练两小时，本轮独立7200秒，实际5853.118秒；此前两段被用户要求收尾，未从新预算中扣除。实际保存21份完整PPO，actor35/critic78/action6、17项Adam、LR/RNG/DR均读回核验。

候选continuous_stairs200_parent_mixed_2h_20261113_035m，iter25011，连续两阶0/10、平地60/60。

实际父为平地速度修复完整父iter24692，SHA979e355a563b3057d7509e9e5ef33e7a364906bd80bd16789ad80df654efa64d，原固定平地60/60、连续两阶2/10。完整actor/critic/STD/Adam/LR/RNG恢复；父保存512环境，新运行2048环境，按既有支持路径重新建立物理episode和采样分组，不更换plant。

从第一次更新开始固定50%连续200mm台阶（1024环境）、30%原Rough-v1十类非平地/十级（614）、20%平地（410）；约20%名义物理和80%完整DR独立交叉。原速度/转向/高度/落地恢复采样保留，附加台阶起点、指令与登阶奖励只作用于专项环境。MOD4 R3资产、35/78/6、电机包络、2.5ms物理/400Hz轮/100Hz腿/50Hz策略、TGS32/4、−1.5e²＋指数1.2、2mm单环境闭链重置保持。未加入动作保持或新奖励。

选模优先固定平地保留通过数，再看连续两阶通过数和成功样本阶间耗时。原成熟包和健康父保留；本轮混训不自动晋升实车模型。

| 段 | 检查点 | 完整连续两阶/10 | 阶间耗时s | 平地/60 | 下阶/5 |
|---|---|---:|---:|---:|---:|
| 2 | model_005m.pt | 2 | 1.318 | 40 | 5 |
| 2 | model_010m.pt | 3 | 1.363 | 40 | 5 |
| 2 | model_015m.pt | 5 | 1.358 | 40 | 5 |
| 2 | model_020m.pt | 2 | 1.231 | 30 | 5 |
| 2 | model_025m.pt | 0 | inf | 40 | 0 |
| 2 | model_030m.pt | 0 | inf | 40 | 0 |
| 2 | model_035m.pt | 0 | inf | 60 | 0 |
| 2 | model_040m.pt | 0 | inf | 60 | 0 |
| 2 | model_045m.pt | 0 | inf | 30 | 0 |
| 2 | model_050m.pt | 0 | inf | 40 | 0 |
| 2 | model_055m.pt | 0 | inf | 40 | 0 |
| 2 | model_060m.pt | 0 | inf | 40 | 0 |
| 2 | model_065m.pt | 0 | inf | 40 | 5 |
| 2 | model_070m.pt | 0 | inf | 30 | 5 |
| 2 | model_075m.pt | 0 | inf | 30 | 5 |
| 2 | model_080m.pt | 0 | inf | 40 | 5 |
| 2 | model_085m.pt | 0 | inf | 30 | 5 |
| 2 | model_090m.pt | 0 | inf | 30 | 5 |
| 2 | model_095m.pt | 0 | inf | 50 | 5 |
| 2 | model_final.pt | 0 | inf | 30 | 5 |


用户要求按华南虎方法重开，旧轮额外4组GPU回放取消，不写通过。包含level0/9穿越、level5小陀螺和落地恢复；使用父与候选匹配DR/噪声/外力/推扰、相同400Hz轮反馈，逐方向与逐环境结果及轨迹在evidence/rough_retention。失败和未收齐均不写通过。名义MuJoCo台阶/平地筛查不能代替完整DR或实车验收。

配方和来源见PLAN.json，首轮恢复和分布见evidence/training/RESTORE.json、TERRAIN_STARTUP.json。每五分钟完整保存、SHA下载核验与巡检，所有真实PT、原始回放、失败和报告随Git普通blob归档，网络走7897代理。
