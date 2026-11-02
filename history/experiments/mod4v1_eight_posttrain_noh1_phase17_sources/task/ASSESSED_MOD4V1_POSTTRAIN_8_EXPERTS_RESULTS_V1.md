# MOD4v1已完成后训练与原scope评估的8条专家

8/8条已完成有限原PPO窗口、完整派生保存、原父close/wait/成本结算/原锁释放与冻结原scope评估。H1始终冻结排除。训练成功、评测执行成功与技能毕业分别报告，不把单seed fresh80当全20k接受总体或硬件资格。

| 专家 | 实际新增PPO | 实际saved iter | 实际saved LR | 本次保守best |
|---|---:|---:|---:|---|
| E0 |20|32004|0.0002562890625000001|新候选|
| CURB_PROTECTED878 |20|32959|7.593750099961956e-05|新候选|
| E2 |20|42842|0.00050625|冻结母本（新候选仍保留）|
| CURB_INDEPENDENT113 |20|32194|0.00011390625000000006|新候选|
| E3 |20|43110|0.0002562890625000001|冻结母本（新候选仍保留）|
| SLOPE135 |20|32088|0.0003375|新候选|
| W35 |20|32662|0.00017085937500000006|冻结母本（新候选仍保留）|
| SLOPE_INDEPENDENT50 |20|32137|0.00011390625000000003|冻结母本（新候选仍保留）|

## 真实指标与限制

E0三项既有body误差改善且普通失败0；C878原上行22/27→26/27、下行27/27与站立26/26保持。E2 vx/yaw改善但vy微增0.00005794m/s，按保守Pareto保母本，不宣统计显著退化；原世界联合0/187与getter相位/参考点缺口仍明确。C113原上22/27、下27/27、站26/26保持，选新候选。

E3首回合原stable credit0/74→1/74，但普通终止事件25→27，保母本；normal6不计入74个rescue分母。SLOPE135自身原上行25/27→27/27、下行27/27及站立26/26保持，普通失败0，选新候选。

W35原moving18/61→18/64、standing26/26保持，分母及参考相位／匹配UID／完整接受cohort仍有缺口，保母本，不从总44/90推moving；SLOPE50原ownaxis20s普通失败0，boundary41→46、timeout47→43仅描述，完整fullramp接受谓词仍缺，保母本。所有新候选都保留。

各原scope的真实分母、成功/失败、接受谓词缺项、观测/参考系限制与保留选择见下方原评估，不从假设补判据，不把退化候选覆盖为成功，不为推进伪Candidate。原saved iteration语义差异按生产者报告，原RSL lastloop标签差19仍可对应20实际更新，不回填。

原PPO/full20k/原actorcriticlearnedSTD17AdamLRiter/全部D0–D7/RNG/history/queue/unknownroot、原归一化、ONEhelperreset/learn(True)、2c-bae/400N-k2000-d3/50-100Hz/.0025TGS32,4/.01m-.01rad保持。N80评测只唯一wholeCPUcache严格载入当前actor/STD，原20k保存历史不apply或slice到80、无livecriticoptimizer/新增PPO。模型只以原producerpath/bytes/SHA引用，不为报告/归档重开PT/raw或运行SDK。

## 原证据

- Pair1 [真实训练汇总](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json>) · [原scope评估与最佳选择](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_FROZEN_RETENTION_BEST_SELECTION_V1.json>)

- Pair2 [真实训练汇总](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR2_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json>) · [原scope评估与最佳选择](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR2_FROZEN_RETENTION_BEST_SELECTION_V1.json>)

- Pair3 [真实训练汇总](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR3_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json>) · [原scope评估与最佳选择](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR3_FROZEN_RETENTION_BEST_SELECTION_V1.json>)

- Pair4 [真实训练汇总](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR4_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json>) · [原scope评估与最佳选择](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR4_FROZEN_RETENTION_BEST_SELECTION_V1.json>)

[Registry_v12](<EXPERT_NORMALIZATION_REGISTRY_v12.json>) 保留原全部冻结selected_formals，附加各scope本次best源与新候选/母本，不覆盖检查点。

本轮八条有限后训练与原scope冻结评估均已完成，H1保持冻结，所有新候选及母本均保留；未获完整技能／硬件资格和观察器缺项继续明列，不宣全部毕业。[最终报告](<MOD4V1_EIGHT_EXPERTS_POSTTRAIN_FINAL_V1.md>)给出完整scope表、模型目录及本轮完成边界。
