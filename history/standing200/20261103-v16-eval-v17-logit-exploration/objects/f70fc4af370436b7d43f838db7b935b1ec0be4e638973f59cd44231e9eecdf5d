V16最终独立评测仍为0/80：39次姿态终止、41次跑满10秒，平均5.65275秒，双轮真实台顶支持和稳定计数均为0。当前模型原生审查四例侧视/俯视回放和两组曲线：三个长时案例贴台沿停住，pitch约−22.7°，轮底远低于200mm，不能把寿命增加称为站爬改善。

V17测试训练探索不足这一具体假设。所选四例初始右轮目标59.34–59.38rad/s而左轮7.59–8.99rad/s。旧动作空间std=.1很难采样到显著减速；新训练在既有动作压缩前的total-logit空间采样高斯，std=sqrt(.15²+(.6*mean)²)，上限2，再通过原动作映射。确定性actor、任务奖励、物理、PD、DR、队列和200mm站爬验收保持。真实奖励和done进入actor，H32 learned-world-model BPTT保留，完整Gaussian概率和old-to-new KL包含状态依赖std，沿用实际梯度主导和postAdam完整回退。没有脚本左右轮同步、MPC或力矩模仿。

数值检查通过：Normal log-prob最大误差3.55e−15，KL误差1.04e−17；64×512合成采集/更新/terminal bootstrap/单次commit/停止保存边界通过。另一次必要V16最终检查点完整CPU恢复通过，actorAdam3154、WM/aux13348、critic13240、verifiedBPTT3153和历史unverified1完整保留；确定性动作差0。合成fixture不是实际onpolicy数据，候选验证后四网络和四Adam全部恢复，生产优化0、SDK/physics0。

新包run MOD4_STANDING200_RLBPTT_V17_1793711403986814000 已冻结但尚未启动。另一scope的原postround collector占用串行通道，V17四卡查询/launch/FIRST均未消费；不增加watcher，不第二SSH，不更改其它scope。释放后重新读取freshLOCAL exactCIM，再对72两卡、210一张、86一张串行有限检查；canonical/private准入后只执行本包。CPU/prepare不得重复。

完整source finalV16: 239095569B SHA51ba7bf4ac55bbb706581b2585e57a244589215b6e271dff0e07134c251bb94f。四网络/四Adam/normalizers/teacher/replay/RNG完整继承，fresh实际DR与队列显式重置。原3900/save3600/exit300/唯一canonical及strictreserve保持。旧phase tagobjects/peels不改，新phase只record一次，后续补充提交。
