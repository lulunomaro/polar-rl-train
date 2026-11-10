# Step7 独立刚体质量 DR

以仓库 [README 后续 DR 计划](../../../README.md#后续-dr-计划与执行约束2026-11-11) 为后续推进约束。本目录只负责 D1；其它 DR 保持上一轮实现。

机身质量倍率 U(0.9,1.3)；匹配 front1–4、rear1–2、spring1–2 的左右16个腿部连杆及左右轮各 U(0.9,1.1)，每环境/刚体独立 startup 抽样。未选导向和传动刚体质量为名义值，每刚体惯量按自身质量同比缩放；base COM 仍 XYZ±.01m。保留修正版 Step7 延迟、原控制频率、电机包络、-.5e²奖励和 PPO 参数。

父权重为完整 Step7 015m，iteration21234，SHA `74c25dd19708148808d1928fc4d6eb1278239fcdc6ab97598d866cf477dc561f`，原始谱系884cd07b。见 evidence/PARENT_SELECTION.json。该权重真实 DR 前进改善但未毕业，名义MuJoCo已有过冲。不得把本次质量适应当作Step7已通过。

当前状态（2026-11-11约01:17）：r1/r2 reset 惯量回读失败保留，已把同一startup质量/惯量写入放到原COMsetter之后；r3的64env×80steps探针通过，8reset质量/惯量变化均0、numerical0、closuremax0.719mm。4096环境40分钟主训练已启动，首更新完整checkpoint保存SHA `3b9447ef22470358224011f194418a0f0654bc2e8aaed7a2c2731b6a54ad0054`，actor/critic/std/Adam/RNG均从选定父恢复，每5分钟保存检查。训练中不自动晋升。

实施、失败和后续运行结果见 [REPORT.md](REPORT.md) 与 evidence；大型权重只路径/SHA索引。
