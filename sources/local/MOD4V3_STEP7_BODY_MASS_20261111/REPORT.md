# 原 Step7 独立刚体质量适应

2026-11-11，Asia/Shanghai。用户要求“机身0.9～1.3；腿部连杆和轮子0.9～1.1，按选中的刚体分别随机化，给加上”，并要求最新checkpoint差不多即可接入。沿用本对话40min/5min规矩，源于884cd07b谱系、Step7_015完整PPOcheckpoint继续，不混入其它fullDR路线。

## 选取父权重

实际同源PhysX固定回放比较原parent、过渡015m和Step7的005/010/015m，7任务×10初态×名义0/Step7DR共700env，300steps/tail120，各模型配对质量、COM、材料、增益、分组延迟与观测/力矩噪声和外力。Step7_015为实际Step7DR中前进最佳候选：2.0=>1.86193（6/10），2.2=>2.03808（4/10），后退、旋转、两高度均10/10，所有条件reset0。原parent的相同DR2.2只有1.62349（0/10）。选择继续适应，不是毕业。

名义MuJoCo仍过冲：同015m在2.0=>2.2120、2.2=>2.4780均0/10。该跨引擎差异没有解决，不把PhysX改善说成部署通过。来源SHA74c25dd19708148808d1928fc4d6eb1278239fcdc6ab97598d866cf477dc561f，iteration21234，原谱系884cd07b。

## 本项改动

1base、16指定腿部连杆、2mainwheels各自独立随机；startup抽样并跨reset保持。baseU(.9,1.3)，腿/轮U(.9,1.1)；其余12导向/传动body的质量scale1。所有刚体惯量按自身质量倍率同比例缩放。替换旧整机共同质量倍率，保留其它reset随机流程。新增MildDR质量写入hook供本profile覆盖，原profile实现行为相同；新增flat_body_mass环境和调用/完整checkpoint字段。critic仍78D，原mass slot写真实总质量/名义总质量，actor35D不增槽。

保持Step7动作5/10ms、传感器5/10/15ms，jointfriction.5/springdamping.25/external.25/obsnoise.25，baseCOMXYZ±.01m，原材质、命令、PD、motor、solver、plant和平方惩罚-.5e²不变。README表D2–D10是后续计划，此轮只D1。

## 实际失败与修复

r1 64env写入/回读质量和惯量后，8次DRreset不变断言失败；r2加完整读数证实质量change0，惯量矩阵entry变化max.00359547。惯量迹保持且非base轴有交换，追踪SDK写法显示父类COMsetter提交全部bodyCOM，发生惯性坐标系更新。本profile改为先完成原COM/其它reset，再重写相同startup质量/惯量；不改USD/solver或范围。r1/r2原始错误、日志和当次源码保留，不重标pass。

r3实测64env×80steps通过：base实测factor.90533–1.29875，腿.90008–1.09924，轮.90128–1.09922；左右front1倍率最大差.18057，未选body全1；masswrite/readerror9.54e-7kg，inertia5.96e-8；8reset后mass/inertiachange均0。实际冻结actor执行80steps，所有观测/奖励有限、35/78维，numerical0、reset0、closuremax.718924mm。此探针验证实现及短时物理，不算任务已适应。

## 运行

2026-11-11约01:17启动train040m_mass_r1，4096env，2400s，完整PPO状态恢复；fixedLR3e-5，clip.1，epochs3。每5min完整保存/SHA核对并在当前chat检查与CPU名义回放，结束后实际质量DR配对PhysX任务比较。首个完整更新iteration21235，SHA3b9447ef22470358224011f194418a0f0654bc2e8aaed7a2c2731b6a54ad0054，numerical0、actor已改变，17个Adam状态条目恢复。周期/最终结果后续追加；不自动晋升/导出/部署。

## 2026-11-11 运行完成补记

40 分钟训练已正常完成，8 个周期检查点均保存检查，040m/final SHA 为 `23c112b16e9629215c7265124925daaf0f9b6bbbb62be61689c714ba1fc7a772`。最终实际 Step7＋质量 DR 前进 2.0→1.9031（8/10）、2.2→2.1555（9/10）、2.7 诊断→2.6106，每项均无重置。前进能力已恢复，少数初态跟踪偏差照实保留，跨引擎差异另列。完整逐检查点结果与后续 DR→Rough 规划见 [FINAL_REPORT.md](FINAL_REPORT.md)。以上启动时记录及原失败证据不改写。
