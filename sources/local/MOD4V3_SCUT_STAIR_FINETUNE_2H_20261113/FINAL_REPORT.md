# SCUT参考配方微调两小时实际结果（2026-11-13）

状态：completed SCUT-method fresh-Adam7200s finetune from iter24692。用户明确重新授权从父模型训练两小时，本轮独立7200秒，实际7203.603秒；此前两段被用户要求收尾，未从新预算中扣除。实际保存26份完整PPO，actor35/critic78/action6、17项Adam、LR/RNG/DR均读回核验。

候选scut_stair_finetune_2h_20261113_015m，iter136，连续两阶0/10、平地60/60。

实际父为平地速度修复完整父iter24692，SHA979e355a563b3057d7509e9e5ef33e7a364906bd80bd16789ad80df654efa64d，原固定平地60/60、连续两阶2/10。载入actor/critic/STD权重；按参考重新建立Adam/seed/迭代计数，父保存512环境，新运行2048环境；保存的新PT全部完整。

从第一次更新开始采用273宽阶/1365其余原Rough-v1/410平地；约20%名义物理和80%完整DR独立交叉。原速度/转向/高度/适用落地恢复采样保留；宽阶使用成功SCUT普通地面奖励，其他环境保留原奖励。自定义登阶分数仅诊断，宽阶无腾空状态机，到顶不提前timeout。MOD4 R3资产、35/78/6、电机包络、2.5ms物理/400Hz轮/100Hz腿/50Hz策略、TGS32/4、旧任务−1.5e²＋指数1.2；宽阶采用保存SCUT−0.00625e²＋指数1.0、2mm单环境闭链重置保持。参考证据和具体适配见SCUT_METHOD_COMPARISON.md。PPO为1e-4 adaptive/clip.2/5epochs/value2，闭链和数值保护保持。

选模优先固定平地保留通过数，再看连续两阶通过数和成功样本阶间耗时。原成熟包和健康父保留；本轮混训不自动晋升实车模型。

| 段 | 检查点 | 完整连续两阶/10 | 阶间耗时s | 平地/60 | 下阶/5 |
|---|---|---:|---:|---:|---:|
| 2 | model_005m.pt | 0 | inf | 40 | 5 |
| 2 | model_010m.pt | 0 | inf | 40 | 5 |
| 2 | model_015m.pt | 0 | inf | 60 | 5 |
| 2 | model_020m.pt | 0 | inf | 30 | 5 |
| 2 | model_025m.pt | 0 | inf | 40 | 5 |
| 2 | model_030m.pt | 0 | inf | 40 | 5 |
| 2 | model_035m.pt | 0 | inf | 21 | 5 |
| 2 | model_040m.pt | 0 | inf | 50 | 5 |
| 2 | model_045m.pt | 0 | inf | 30 | 5 |
| 2 | model_050m.pt | 0 | inf | 39 | 5 |
| 2 | model_055m.pt | 0 | inf | 60 | 5 |
| 2 | model_060m.pt | 0 | inf | 50 | 5 |
| 2 | model_065m.pt | 0 | inf | 30 | 5 |
| 2 | model_070m.pt | 0 | inf | 56 | 5 |
| 2 | model_075m.pt | 0 | inf | 60 | 5 |
| 2 | model_080m.pt | 0 | inf | 40 | 5 |
| 2 | model_085m.pt | 0 | inf | 30 | 5 |
| 2 | model_090m.pt | 0 | inf | 30 | 5 |
| 2 | model_095m.pt | 0 | inf | 30 | 5 |
| 2 | model_100m.pt | 0 | inf | 40 | 5 |
| 2 | model_105m.pt | 0 | inf | 40 | 5 |
| 2 | model_110m.pt | 0 | inf | 40 | 5 |
| 2 | model_115m.pt | 0 | inf | 40 | 5 |
| 2 | model_120m.pt | 0 | inf | 30 | 5 |
| 2 | model_final.pt | 0 | inf | 30 | 5 |


原完整Rough-v1父子同条件固定回放完成4/4组，包含level0/9穿越、level5小陀螺和落地恢复；使用父与候选匹配DR/噪声/外力/推扰、相同400Hz轮反馈，逐方向与逐环境结果及轨迹在evidence/rough_retention。失败和未收齐均不写通过。名义MuJoCo台阶/平地筛查不能代替完整DR或实车验收。

配方和来源见PLAN.json，首轮恢复和分布见evidence/training/RESTORE.json、TERRAIN_STARTUP.json。每五分钟完整保存、SHA下载核验与巡检，所有真实PT、原始回放、失败和报告随Git普通blob归档，网络走7897代理。
