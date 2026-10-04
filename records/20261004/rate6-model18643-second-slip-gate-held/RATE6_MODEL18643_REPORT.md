# 6档18643：同一滑移门控仍未过，第二个连续失败块

auto0055原定平地80env与自转88env各15秒已完成。正式源18643 SHA9d90660062e8ea47c79004b9ca2c2e5218e806aa77e977c1bd6753749068212a已按精确评测路径独立CPU读取actor/critic/optimizer/std/iter，68浮点完整有限。flat64已训练环境全部原准入通过，旧strict_window=false保留；rate88/88存活、physical=true、初末实际参数读回通过，corrected与legacy_reference spin_skill均false。

交错group_ids逐环境重算与原报告分数相同。纯+6正确参考点技能2/8=25%，旧参考点5/8=62.5%，两者均低于原80%；6个失败仅为右轮平均网格滑移代理>.15m/s：env18=0.159647、env29=0.151956、env40=0.162308、env62=0.151673、env73=0.161435、env84=0.155621。正转8个样本右轮范围0.134142–0.162308；纯-6与其余9组均8/8，反转左轮范围0.118357–0.139359。不通过组均值、切换参考点或降低阈值毕业；没有死亡、NaN、物理或旧站跑退化。

纯±6实际yaw均5.993749/-5.962062rad/s，逐环境最坏peaktilt1.615557deg、控制gap0.785850mm、双轮低载11.500ms、平均XY速度0.101856m/s，closure0.080073mm/mimic0.001827rad。与18207同seed20261002、white_v2、probe源码及完整初始root/q严格相同，权重不同。17773首次通过及18207反转失败均保留；失败轮侧随策略变化，不能宣称持久修好、奖励单独因果或PhysX材料点/实车滑移。

REPAIR_STATE consecutive=0/failed_blocks=2，原监督器继续已经安排的第三个有界6学习块，未升8；只有第三个连续技能失败或物理/旧能力退化才按既定规则保留权重、回实际paired成熟17196/5并hold，不抢先热改活跃trainer。本轮与已通知的滑移门控是同一未解条件，没有新严重故障，不重复通知。

核验时单一正式trainer3905371/start23845428从18643完整恢复、KEEP_STD1，run logs/2026-10-04_11-10-45_auto_0056_rolling_rate_trial_or_continued_cap6_white_v2；parent3238128/start20735397与guardian3238171/start20735462独立会话正常，cap6/white_v2/rolling v1固定。PID绑定19025 SHA2446198c0ebdb04a1bf8ea2c99b99af0c09d51982b6da8e759afaa229c79bb28已CPU读回68浮点有限，104原源/123候选源一致；19025尚无15秒回放，不借训练success/reward宣布毕业。约29.7k环境策略步/s、GPU77%/14562MiB/47C是快照，近期无NaN/Traceback/OOM。下一段deadline约北京时间2026-10-04 13:07:55，随后已有自动保存及顺序flat/rate，不发重复probe。

唯一252000有效PPO秒与三授权扩展不变，核验剩42564.70秒约11小时49分为快照，后续扣活跃尾段。本轮只读已有报告、CPU/来源/进程/GPU与Git归档及交接更新，无额外probe/PPO、暂停重启、奖励/物理/DR/硬件/门槛或预算改变。原地小陀螺优先，移动/FPS/地形延期，120rpm未达到。
