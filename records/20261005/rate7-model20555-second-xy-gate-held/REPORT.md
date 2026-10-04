# 7档正式20555第二次原地平均水平速度未过

2026-10-05T01:02:23.539946+08:00仅读取主机已有auto0085的80env flat/88env contact-spin各1500步15秒原报告，无新probe或PPO安排。正式权重20555精确SHAe3bbebc514470347c5670b857997fb5e9ea4d8b82be18b15ab2a8d715ac1e90f，不是全目录最高iteration搜索选源。

v2=scut_style_nonslip_gate_v2_flat_and_spin。平地64已训练环境全部原非滑移准入通过，spin88/88存活/physical_smoke=true，11组中9组各8/8；纯+7仅3/8=37.5%、纯-7仅1/8=12.5%通过，技能总false。12个失败个体的非滑移reason都仅spin_translation_speed（平均水平速度>.12m/s）；纯+7失败env7/18/51/62/84，.120168–.129891m/s；纯-7失败env8/19/30/41/52/63/74，.120418–.121806m/s。不是滑移.15硬否决，也不是崩溃或实际材料点滑移认证。

左右纯7实测组平均yaw+6.965380/−6.947732rad/s；纯±7最坏peaktilt3.097182deg、gap1.160361mm、双轮低载11ms。每环境均值不冒充瞬时峰；平均水平速度不同于世界净漂移，组平均root_xy_excursion约.08418/.09852m也独立保留。其余物理、动作、承重、停车、闭链、数据完整性及原站跑门槛通过，severe个体额外否决为空。原网格与legacy skill=false、loaded015布尔/全部滑移测量原样保留，有限滑移只诊断。

与第一份20132同seed20261002/white_v2、probe SHA、完整reset root/q及初始参数exact，weight不同；不归因于物理/DR变化或单独奖励因果。纯+7通过5/8→3/8、纯-7 8/8→1/8，当前仍未持续达标；.12附近的数值保留而不改门槛毕业。

实际专项consecutive0/failed_blocks2。parent50057/start28076744、guardian50092/start28076814独立session正常；单一trainer73337/start28749064从20555完整actor/critic/optimizer/std/iter KEEP_STD1恢复。run=/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-05_00-48-01_auto_0086_rate7_transition_trial_or_continued_cap7_white_v2，active_log=auto0086_rate7_transition_trial_or_continued_cap7_white_v2.log。最新PID绑定20600 SHA95d57acdcdc2abb5eb76d873aecc62365ba8349187740be069a98c87952d4fe4，CPU68浮点完整有限，20600尚未15秒回放，不能借20555称新策略通过。137候选/104生产实际源一致，近期无NaN/Traceback/OOM。

继续既有有界7训练至2026-10-05T02:45:11.847596+08:00保存后已有顺序flat/rate，无重复probe。第三连续失败才按已配置规则回实际paired成熟19975/cap6/white_v2并repair_hold保存预算；不热改当前trainer、清拒绝或直接跳8。两份不同策略和双seed nominal/white八份严格初态/参数复核全过才7成熟。120rpm/4π仍未达到。

唯一canonical总324000有效PPO秒90h，四条已授权20h扩展各一次；本轮实读剩87694.893s约24h21m仅快照，实时扣active尾段。此次没有追加/复制/清charged/重复结账，未改reward/DR/硬件/物理/PPO/测量或门槛。原地spin优先，移动/FPS/地形等延期。每2h巡检健康静默保持，不恢复每小时/5分钟SSH或ping。hold不等于finished，真实目标/预算全部终验才删除自动化。
