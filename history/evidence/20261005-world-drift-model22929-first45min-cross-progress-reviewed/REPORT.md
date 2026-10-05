# 世界净漂移奖励第一正式45min策略22929：完整圈漂移下降，目标未全过

实际读取2026-10-05T23:24:52.004042+08:00。正式22929来自生产auto0239原45min自然完整保存，SHA71fb20bc51f02a080908b2decc46f357dd024f4560fc7814b4c4bc39831cc7aa。actor/critic/optimizer/std/iter CPU68浮点完整有限证明复用第五次预算HANDOVER的同一精确SHA；不是全目录最高iter选源。原22775完整基线及全部旧权重保留。

auto0240平地80/80、0241原地88/88、0242世界88/88各1500步15s全通过SCUT v4任务/模型/数据准入。新世界closure0.123759mm/mimic0.001827rad，实际参数初末读回通过。原mesh/legacy false及flat strict_window false原样保留，有限性能数值继续只诊断，不把准入称旧规则毕业或实车认证。

固定20261002/white_v2的旧22775 auto0236与新22929 auto0242：真实profile字段、probeSHA、完整初始root/q及初始参数对象精确相同。64个moving样本的全完整圈净进度目标16/64→27/64；左右1rad/s仍16/16，左右2rad/s由0/48→11/48。2rad/s样本平均绝对整圈净横向速度0.067346→0.053459m/s，约下降20.62%；最坏绝对横向净速度0.076656→0.064894m/s。新完整圈净along0.477395–0.536632m/s。仍37个2rad/s样本未达到世界方向目标，all_target=false。正常圈内横向摆动与持续净漂移分开；没有用速度模长、半圈选段或全窗口crossspan冒充完整圈净进度。

新增phase_compensated_cycle_cross_v1奖励开始学习后出现改善，但同时权重及学习暴露改变，不能宣称隔离奖励因果。奖励.10归一化仅优化尺度，不新增硬否决。奖励off/on读回、物理/128与20k完整PPO预检已在此前部署完成，不重复。

第一seed nominal/white的auto0243–0248六份全部v4通过，三对完整初始root/q独立精确相同。spin/world初末参数、DR flat mild初末参数实际读回通过；nominal flat没有独立参数对象，不冒称补测。nominal world22/64、white world27/64，都是同一策略，不能计为两份不同正式权重。读取时第二seed20261003 nominal flat auto0249在既有父流程中评测，十二份尚未全完，不登记paired接受或世界完成。

真实parent341833/start36713121、guardian341878/start36713187独立session，eval347355/start36890341当次/proc定位。phase frozen_flat/goal.5，无trainer/active_segment为合法冻结。STATE旧22env group_samples reason是历史，不据此误重启。当前代码E=/home/egde/rl_candidates/MOD4_WORLD_DRIFT_BUDGET130_20261005，status/log/canonical owner仍生产P。165源动态预算接续保持，不重跑新旧entry/安装/迁移/预算/恢复事务，也不追加probe/PPO。

唯一canonical总468000有效PPO秒130h，原36000+四条72000+用户第五次144000一次登记。charged277446.5994386673，冻结余190553.4005613327秒约52h56m；评测不扣PPO，之后减真实active尾段。此次只读既有证据/离线核查与归档交接，没有新增时间、清charged、重复结账或变更配置。

原地4pi21697双seed/final完成保持，当前世界.5/yaw左右1–2不是4pi移动。世界完整双seed/final事实确认后才按既有授权在同预算余量内接独立物理DR，当前DR执行器尚未部署。地形/云台/MoE仍后续；每两小时健康静默监控、主机独立父guardian和原Rich窗口本地刷新保持，单科完成不删除监控。
