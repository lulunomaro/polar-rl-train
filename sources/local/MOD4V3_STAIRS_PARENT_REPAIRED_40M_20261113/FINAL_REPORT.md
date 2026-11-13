# 父模型起步台阶判定修复40分钟实际结果（2026-11-13）

状态：Stopped early by human-authorized no-progress restart; original regressions and actual seconds preserved; GPU retention deferred。用户要求修复后重新从父模型训练，并扩大平地/原Rough-v1比例，本轮为新的40分钟轮次，本轮独立2400秒，实际1451.965秒；此前实验独立归档，本轮单独计时。实际保存6份完整PPO，actor35/critic78/action6、17项Adam、LR/RNG/DR均读回核验。

候选stairs200_parent_repaired_40m_20261113_005m，iter24737，连续两阶5/10、平地40/60。

实际父为平地速度修复完整父iter24692，SHA979e355a563b3057d7509e9e5ef33e7a364906bd80bd16789ad80df654efa64d，原固定平地60/60；历史连续两阶2/10为旧即时重置协议，不能与本轮V3直接比较。完整actor/critic/STD/Adam/LR/RNG恢复；父保存512环境，新运行2048环境，按既有支持路径重新建立物理episode和采样分组，不更换plant。

从第一次更新开始固定40%连续200mm台阶（819环境）、35%原Rough-v1十类非平地/十级（717）、25%平地（512）；约20%名义物理和80%完整DR独立交叉。其余rough和一半平地保留原速度/转向/高度/落地恢复采样；另一半平地练原六项固定目标并保留原地面reset热身。附加台阶起点、指令与登阶奖励只作用于专项环境。MOD4 R3资产、35/78/6、电机包络、2.5ms物理/400Hz轮/100Hz腿/50Hz策略、TGS32/4、−1.5e²＋指数1.2、2mm单环境闭链重置保持。保留上一版已验证的台阶轮下高度参考、阶沿导轮接触豁免和独立终止计时；采用V3修正回放规则。

选模优先固定平地保留通过数，再看连续两阶通过数和成功样本阶间耗时。原成熟包和健康父保留；本轮混训不自动晋升实车模型。

| 段 | 检查点 | 完整连续两阶/10 | 阶间耗时s | 平地/60 | 下阶/5 |
|---|---|---:|---:|---:|---:|
| 1 | model_005m.pt | 5 | 1.192 | 40 | 5 |
| 1 | model_010m.pt | 5 | 1.133 | 28 | 5 |
| 1 | model_015m.pt | 5 | 1.300 | 30 | 5 |
| 1 | model_020m.pt | 4 | 1.066 | 30 | 5 |
| 1 | model_final.pt | 2 | 1.178 | 30 | 5 |


原完整Rough-v1父子同条件固定回放完成0/4组，包含level0/9穿越、level5小陀螺和落地恢复；使用父与候选匹配DR/噪声/外力/推扰、相同400Hz轮反馈，逐方向与逐环境结果及轨迹在evidence/rough_retention。失败和未收齐均不写通过。名义MuJoCo台阶/平地筛查不能代替完整DR或实车验收。

配方和来源见PLAN.json，首轮恢复和分布见evidence/training/RESTORE.json、TERRAIN_STARTUP.json。每五分钟完整保存、SHA下载核验与巡检，所有真实PT、原始回放、失败和报告随Git普通blob归档，网络走7897代理。


本轮若存在SUPERSEDED_BY_NO_PROGRESS_RESTART.json，则因前向超速与平地保留退化按用户指令提前保存结束；原Rough-v1 GPU回放延后，0/4不表示通过或失败。


此次恢复自有收腿/落轮/接续奖励；平地保留组的一半固定练原六项目标并用地面reset，余下平地和原rough采样保留；真实terrain_family用于奖励过滤。实际配方、探针和启动核验见PLAN.json及evidence。
