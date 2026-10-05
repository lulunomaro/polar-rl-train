# 新世界净漂移奖励正式45min试训



实际部署核验 2026-10-05T22:05:02.243540+08:00：奖励off/on实际通过，动作/指令/rootXY/heading/q完整bit-exact，reward差公式最大误差 9.31322574615e-10/step。auto0233独立20k1.2s检查terminations=0、finite与材料/闭链通过v4，原combined=False、短高差0.06269720196723938m继续保留。auto0234/0235/0236原站跑/4pi/world各15秒分别80/88/88全存活、任务/模型/数据准入通过。固定旧22775世界事实16/64，不是新奖励已学效果。

128env2轮和20kenv4轮完整PPO预检通过，均扣原canonical、预检权重弃用；20k吞吐28660.99环境策略步/s。正式从精确完整22775恢复，KEEP_STD1/white_v2/world_v1/rolling_v1/goal.5/纯spin cap4pi，新term cycle_v1。实际run /home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-05_22-03-39_auto_0239_world_drift_learning_cap12.5664_white_v2。新PID330317/start36402806自己的22775 SHA737a8ce92a8647994e6684487917df7083c59574e1081cfbbcc4eff9b6eae7d3已CPU68浮点有限；这是新run初始保存，未做该策略15秒回放或宣称改善。

实际独立parent325437/start36271233、guardian325476/start36271298，唯一trainer的cwd/argv/session和账本PID一致；candidate164冻结与run完全相同、原P104精确核查。首段deadline 2026-10-05T22:45:49.269821+08:00，随后已有顺序flat/spin/world及双seed nominal/white十二份回归，不重复probe。预算总90h不变，本核验实时剩49126.871s，后续扣active尾段。世界完成后按授权再独立扩大物理DR，当前不混入；两小时监控保持。


当前唯一根D=/home/egde/rl_candidates/MOD4_WORLD_DRIFT_REWARD_20261005；P仍为status/log/canonical owner。入口supervise_world_drift.py --readback-review-continuation已执行，migrate_saved_reward、stage_and_migrate、两次launch_review及所有旧entry/continuation/预算交易不得重跑或盲--resume。REWARD_HANDOVER尾段96.94167160987854秒已结一次，旧213707/213749/311263已退出。首次来源字典比较、22env审计误套88env样本合同的错误与hold都保留在INITIAL_SOURCE_RECORD_ERROR/READBACK_PROTOCOL_HELD_STATE/REVIEW；修复不改奖励数学或正式88env门槛，off原回放明确复用。STATE.reason可能保留旧group_samples字串，真实phase/日志/receipt优先。

先读WORLD_SPIN_STATE/ACTUAL_VERIFIED/REWARD_READBACK_PASSED/REWARD_BASELINE_PASSED/SOURCE_FREEZE/REWARD_HANDOVER及P/status/AUTONOMY_STATE，每轮重新核查/proc身份、PID绑定run/latest_complete/run_manifest/rolling_source_freeze，不按目录最大iter或缓存字段选源。新的checkpoint未actual15s不能称通过或漂移修好。新term .10是连续优化尺度、-.3、clamp4上限1.2/s，仅moving；实际heading/位置整圈边界插值与理想周期位移补偿，不罚理想正常摆动、不增加性能硬否决、工程余圈估计非实车证明。SCUTv4质量诊断、实际reset/非有限/闭链/参数与接触数据一致及硬件包络保持，旧原始布尔全部保留。

canonical唯一总324000秒90h及四条20h扩展均已应用一次，不加预算/清charged/复制或重结尾段。冻结/迁移不计PPO，预检/加载/保存退出/正式PPO均计同账本。父guardian独立本机离线继续，出现真实故障保留现场/完整权重/账本并隔离，trainer活跃先修监督不双开20k，不干预其他AI。每2h健康静默、无小时/5minSSH或ping，Rich原P窗口5s本地刷新不新开。原地21697终验已完成保留，但世界目标/actualfinal未完成，不删监控；真实世界完成后预算内独立物理DR，terrain/gimbal/MoE后续，队列非已部署。预算耗尽且当前实际科目终验全部完成才结束监控；hold不等于finished、不自动加时。
