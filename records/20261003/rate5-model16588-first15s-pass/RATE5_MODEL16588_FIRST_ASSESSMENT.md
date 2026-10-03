# 5rad/s首轮15秒确定性验收通过，继续同档复核

已有auto0034三份raw flat/rate/decision实际完成，无新probe或生产修改。正式model16588 SHA `ee41488be9ea89154ad58e0935de06c500433cb860bdd8d2ed491b550b9aabe8`，white_v2。rate seed20261002、88env×1500steps15秒，88/88存活，11组各8/8原技能/物理通过，corrected与legacy布尔均true；初末实际参数读回通过。独立flat seed20260927、80env15秒协议全部64个已训练环境准入，旧strict_pass_window=false保留。这是不同seed、不同协议，不能冒称同初态配对或两seed复核。

按交错group_ids取逐环境数据：纯+5组实测平均4.988522rad/s，纯-5组-4.972645rad/s；各8/8技能和存活通过。两组最坏peak tilt1.324856deg，最坏每环境平均网格支撑点滑移代理0.138550m/s，低于原0.15门槛；+5右轮最坏0.129815，-5左轮最坏0.138550。该值是原控制采样代理的逐环境平均，不是PhysX流形或子步峰。最坏输入网格间隙0.560619mm，最长双轮低载12ms，闭链0.084750mm、mimic0.001827rad。纯5各环境wheel/leg实际执行器rating裁剪比例0，100Hz力矩轮速不代表子步峰。启停/停车/反向组亦8/8通过。

原父2888037/start19114965、guardian2888078/start19115034正常。首45分钟完整保存后自动从正式16588完整actor/critic/optimizer/std/iter续训，不重置std。当前单一正式trainer2956745/start19430761，active_log `auto_0035_autonomous_continued_cap5_white_v2.log`，run `logs/2026-10-03_22-54-58_auto_0035_autonomous_continued_cap5_white_v2`。23:57已CPU回读完整16825 SHA `c3eb8f6804dfc41464418151584c1d6efc18e0c2be552c59fdfe9ab195148e84`，68浮点有限、PID绑定latest_complete、source16588/SHA、manifest start16588/KEEP_STD1/cap5/white_v2和104源实际核验一致；约30.9k环境策略步/秒、GPU80%/14560MiB/47C为快照。最新16825尚未确定性回放，不能借16588首次验收称最新策略或5档多seed毕业。

S.consecutive=1、failed_blocks=0。下一段截止2026-10-04 00:52:08北京时间，之后已有flat/rate回放，不能重复发probe。仍需第二份不同完整策略通过，再同候选两个seed nominal/white_v2各flat/spin精确root/q配对通过。现保持5/white_v2，不升6或扩DR。旧rate_rejected=[6,5]保留，5旧拒绝对应16450源；6档行为超限未解决。targeted_mature5.phase=saved_pending_assessment和entry receipt是首次试训历史流程标记，当前由同父v4控制器正常continued段运行，不能因此重复入口/盲resume。5成熟后下一6拒绝则专项修复hold，不无限叠成熟档。

唯一70h/252000秒canonical和三授权扩展不变，23:57实际余79934秒约22h12为快照，PPO正常计同账本。仅采集/CPU验证/审查/同步及Git归档，没有追加预算、重复结账、暂停/重启训练或改物理/奖励/DR/门槛。用户原地小陀螺优先、两小时巡检和健康安静保持。
