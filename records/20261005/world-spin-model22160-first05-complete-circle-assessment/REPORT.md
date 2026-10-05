# 世界定向0.5首正式22160完整圈回读

实际核验2026-10-05T17:21:37.412687+08:00：当前.5首45分钟正式段已经完整保存22160，SHA7535dc8f91425346049710a490dff213c8d1bc7664b9cd6ca96241708df7090d，PID258612绑定完整actor/critic/optimizer/std/iter；CPU68浮点有限。实际加载/学习/保存/退出段2721.251087秒已经父进程同canonical记账一次，本轮无预算操作。精确源22006、KEEP_STD1/white_v2/world_v1/rolling_v1保持，156候选源及本run冻结一致，当前trainer已自然退出进入既有冻结评测。

auto0199平地80/80、0200原地spin88/88、0201world88/88各15秒全部通过SCUT v4任务/模型/数据检查。原mesh/legacy=false、flat strict_window=false并列保留。world闭链0.149369mm/mimic0.001691rad、实际参数初末读回通过。与22006的auto0197同seed20261002/white_v2/probe SHA及完整初始root/q/参数精确相同，权重不同，不宣称隔离奖励因果。

64个moving样本全部实际完整圈前缀净along 0.470955–0.547368m/s，最大绝对netcross 0.073692m/s，比同源基线0.150288降低；目标事实15/64→16/64。左右1rad/s两组16/16达到方向目标，左右2rad/s及其他2rad/s方向组0/48，仍有横向漂移，all_target=false。有限误差继续诊断与优化，不恢复旧.12/.15硬否决。前进净速度不是速度模长，完整圈、全窗口与首失败前有效样本原样保留；cross span含持续漂移，不当纯周期摆幅。

两seed nominal/white各flat/spin/world12份回归核验时已有5份通过；seed20261002 flat/spin两对完整root/q精确相同，world对第二份auto0207正在既有回放。phase=frozen_world/goal.5，无trainer/active_segment是合法冻结。父213707/start32914339、guardian213749/start32914408及eval273099/start34727607已实际/proc核实，后续实时receipt优先；不重复发probe、entry、continuation、预算或恢复事务。

预算仍324000有效PPO秒90h与四既有登记扩展，冻结余60104.736700秒约16h41m。本轮只读已有报告/CPU/身份与来源、结果归档交接，没有新PPO、加时、配置或奖励/DR/物理/硬件修改。原地4pi21697终验完成保持，世界.5目标和final未完成，DR下一课只在真实世界终验后预算内接续，当前没有部署DR执行器。两小时健康静默监控继续，不删除自动化。
