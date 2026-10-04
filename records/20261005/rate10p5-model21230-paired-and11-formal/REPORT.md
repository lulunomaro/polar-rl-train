# 10.5档21230配对接受，11档正式学习

核验时间：2026-10-05T07:42:16.992001+08:00。

正式21230完整保存后，auto0120单seed站跑/自转及auto0121两个seed、nominal/white_v2各flat/spin八份15秒回归全部通过SCUT v4故障/模型/数据准入。4对完整初始root/q精确相同。四份自转352/352存活，四份平地320/320存活（其中256个已训练环境）。自转名义/DR参数初末实际读回与DR平地读回通过，名义flat原报告未独立提供参数对象，不冒称补做读回。auto0122登记实际暴露2724.142秒、learning_admission_only=true。

四份纯正10.5的组平均signed yaw为10.493336–10.497427rad/s；纯反10.5为-10.513667–-10.503461rad/s，约1.67转/秒。逐环境水平平均速度与世界XY excursion分别保存在REVIEW和原raw。原网格/legacy spin_skill=false、flat strict_window=false继续保留；有限性能值不重新成为硬否决。接受课程学习不等于旧质量规则毕业、2rev/s或实车认证。

随后仅提高cap到11。auto0124短物理22/22存活；auto0125两万环境1.2秒实际terminations=0、数值/材料/闭链检查通过v4。原combined=false、短高差62.935680mm警告保留；auto0126的128环境两轮完整PPO通过，21231预检权重弃用并扣原账本。旧从21075预检11发生2次任务重置的失败仍保留；当前源不同，不宣称奖励隔离因果。

实际parent134255/start30620372、guardian134297/start30620443、唯一trainer152545/start31154527，/proc cwd/argv及独立session核验。当前run=/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/logs/2026-10-05_07-28-57_auto_0127_scut_v4_rate_learning_cap11_white_v2。从精确21230 SHAff871b96ecea01b5e88bb5830adb4298fc4609c365824e427d8f5045e2993af1完整actor/critic/optimizer/std/iter恢复，KEEP_STD1/cap11/white_v2/rolling_v1。自己的完整21275 SHA6cac7736b3e5c59c611514b43a73d4cee9d258769cae6688bb412b074c2bff5d已CPU核查68浮点有限；新权重尚未15秒回放。145候选源及104原生产源全部实际核验一致，最近日志无NaN/OOM/Traceback，GPU92, 14346, 52为快照。

当前段截止2026-10-05T08:11:06.474189+08:00，父已有保存、单seed及双seed回归安排；不发重复probe。路线11→12→4π，只有实际双seed/final左右signed yaw确认才称2rev/s。随后按用户授权，预算内接世界定向低速自转移动0.15→0.3→0.5m/s；当前没有部署该课程。

唯一canonical仍324000有效PPO秒90小时、四条已登记20小时扩展各一次。核验实时余75767.990秒≈21.05小时，此后扣活跃尾段；本轮没有追加、清charged或重复结账。只读已有报告/CPU/来源核查及结果交接归档，未增加模拟/PPO或暂停重启。原地完成后保留阶段final与监控，预算耗尽并完成当前实际阶段终验才删除mod4-10。
