# 华南虎课程思路 v4 已正式接管8档

实际核验 2026-10-05T02:49:59.045704+08:00。用户明确要求对齐华南虎门槛，避免额外质量数值无限卡升档。新验收scut_curriculum_v4_performance_diagnostic、新控制器scut_curriculum_v4_exposure_budget_dynamic已正式部署，不是仅候选准备。

7档完整20775的auto0088两个seed nominal/white八份15秒均通过v3与初态/参数精确配对：自转352/352存活、站跑256已训练环境全部通过。8档原短物理、20k和128完整PPO预检通过后实际开训，20kcombined=false/75.863mm短高差警告保留。此次明确复用旧8预检，未重新执行。当前唯一trainer98569/start29475419，parent98524/start29475344、guardian98567/start29475412独立session，真实/proc身份及PID绑定run已核实；PID仅定位，后续实际receipt优先。

run=/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-05_02-49-06_auto_0094_scut_v4_rate_learning_cap8_white_v2，active_log=/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/auto_0094_scut_v4_rate_learning_cap8_white_v2.log。从PID94798正常完整保存20825 SHA6e33a0bad9baf0e7c14d41a3388e0cc6ebbdf404c5e3ac3f163ce84f6dc9b0c0精确恢复actor/critic/optimizer/std/iter，KEEP_STD1/cap8/white_v2/rolling_v1。新trainer自己的启动恢复20825 SHA1525d385e504a0417960b5ca812588768143cc0c0aba71fbbe7f5d1079244bee已CPU回读68浮点有限，manifest精确init路径/SHA与run冻结v4一致；这是启动恢复保存，不代表新训练后的策略已成熟。GPU86 %, 13914 MiB, 52是快照。

有限性能数值均只作诊断和连续奖励优化：包括原速度/转速误差、均8峰12/严重15deg质量线、高度3cm、delta/d2、10N均载、15ms双低载、2mm网格gap、停车及20%clip使用率，以及滑移全部数值。原fullscale/short/flat/spin/paired旧布尔和失败JSON原样保留；正式decision、paired、3s和20k完整调用路径都已移除旧质量数值硬否决，不仅包装结果。硬件限幅本身不变。

仍检查真实MOD4任务终止/重置、数值有限、closure2mm/mimic.01rad及参数/接触数据完整一致。现有训练重置.75rad/地面底盘50N等保持，不声称与SCUT40deg+20步一比一。公开V14参考的是性能由连续奖励优化、按训练阶段启用命令的思路，不是照搬另一机构所有物理参数。

取消两份正式策略连续通过和80%性能数值毕业合同。当前8档累计有效暴露1004.752s、继承剩余1695.247s，当前段截止约2026-10-05T03:14:30.642908+08:00后已有顺序真实flat/contact-spin及两seed nominal/white八份故障/完整性回归，不重复probe。最新单份完整策略完成有界45min暴露并通过这些回归即允许下一档8→10→4π独立预检和45min学习。学习准入/课程接受不宣称跟踪精度成熟。最终2rev/s要左右实际signed yaw及双seed/最终报告确认，未达继续终点PPO到授权预算，不以cap登记当目标完成。

唯一canonical仍324000有效PPO秒90h，四条登记扩展各一次，无新预算。尾段133.313462496s只结一次，退出观察<=.25s不确定性，冻结/迁移无PPO不计。核验实时剩83723.728s约23.26h。139旧候选与104原生产源字节全部核验不变，只新增gate/controller共141；奖励/white_v2/硬件/物理/PPO/reset/观察网络不改。

以C/reports/SCUT_CURRICULUM_V4_STATE、MIGRATION/HANDOVER/LAUNCHED/GUARDIAN_STARTED/ACTUAL_VERIFIED、SOURCE_FREEZE和P/status/active_log/PID绑定latest_complete/run_manifest/rolling_source_freeze为准。新migrate/stage/entry已完成不可重跑；87308/87340/94798已真实退役，不恢复旧父/--resume，不重复结账。实际任务/model/data故障回真实已验证源并hold保留余预算；不能因旧质量布尔失败再按旧规则hold。当前回滚源20775/cap7/white_v2。

原地spin优先；moving/FPS/地形/云台/MoE延期。每2h线程巡检、健康静默；主机父/guardian独立、本机离线继续；现有Rich同P窗口5s本地刷新。预算或真实目标终验完成才AUTONOMY_FINISHED/finished/删除mod4-10；hold不是finished。详细计划、73项本机/目标CPU和目标静态回调合同见本目录。凭据不归档，权重仅SHA索引。
