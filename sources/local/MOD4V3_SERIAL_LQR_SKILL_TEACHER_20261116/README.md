## 2026-11-16 20:54 人类授权斜向摸底：200mm四角仅1/4稳定

按最新人类“测试斜着能否上台阶”授权，仅冻结476006f4当前候选做center起点−20/−10/+10/+20°四例，航向目标等于初始斜角，全程保持，不先转正。−10°实际触阶−8.75°通过，连续稳定5.10s；+10°实际+7.40°仅短暂台顶0.40s后掉台（最大横滚63.63°）；±20°触阶实际−19.27/+15.66°，全程idle未触发lift，台顶支撑0。当前不能可靠斜上200mm，不能从正向5/5推断斜向已会。

控制器、原候选profile、scene/碰撞、PD/电机、35/78/6、2.5ms/100Hz/400Hz/50Hz和默认c874均未改；仅独立测试脚本设置初始/目标航向并按相对指定航向评分，原世界零航向RESULT保留。无学生/PPO更新，不扩大矩阵。证据：sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1/oblique_probe_20261116/REPORT.md。本轮最新人类授权覆盖下方旧“暂不扩斜向”范围，仅限这四例测试。

## 2026-11-16 20:28 五起点授权与接管修复：5/5稳定，仍未无倒溜验收

最新人类授权保持92e8cdbe前段候选，先跑200mm五起点[-60,-30,0,+30,+60]mm。原版v2实测2/5（−30与center过，另三例落台后退失稳）；保留其CANDIDATE_PROFILE。当前forward_capture_repair_20261116候选仅修capture承载时错误重入plant/超时、去除仅腿45ms旧力矩偏移、退出capture后停车位置参考回拉，五点5/5稳定4.60/5.24/5.26/5.36/5.38s。五例首次capture之前状态/动作与各自v2原版逐帧相同。

仍未动作质量合格：center前段2.824°、整段6.644°不变，等待期vx .560→.392、首lift记录.276m/s仍未修好。center接管后退44.8→25.2mm，−30约23mm；含lift/swing等整个上阶过程分别仍后退约41.5/45.7mm。三个原失败点均稳定；停车后不再退回松油位置，但末端仍约.02～.03m/s微正速度，非精确原地停车。失败探针已全部退出在用代码、记录并列保留。五点稳定通过不等于无明显倒溜，也不等于技能教师毕业。

硬边界不变：scene/platform/tire、原PD/电机、35/78/6、2.5ms/100Hz/400Hz/50Hz、2mm仅诊断、默认c874不变。无学生/PPO更新、无大矩阵；下一步只修剩余丢速与短暂回缩，视频未获人类确认前不扩验收/蒸馏/PPO。证据：sources/local/MOD4V3_SERIAL_LQR_SKILL_TEACHER_20261116/equivalent_controller_v1/forward_capture_repair_20261116/REPORT.md。下方旧“只准单点/不能五起点”由本轮五点授权覆盖；旧通过率不继承。

# MOD4v3 Serial技能教师

2026-11-16 19:22：当前只有前段修复单例候选，动作质量未验收。200mm标准起点前段峰值2.824°、window峰值6.644°、稳定4.46s，但入lift仍丢速且短暂后退。不扩矩阵、不进示范池、不蒸馏/开PPO，默认c874不变。

最新[前段修复与全试错报告](equivalent_controller_v1/prelift_contact_repair_20261116/REPORT.md)，参数在同目录CANDIDATE_PROFILE.json，视频为SOURCE_BASELINE_PRELIFT_REPAIR_1X.mp4。旧3/3和4/5仅为原版历史成绩，不继承到新候选。

当前为实验性原生 MOD4v3 LQR/VMC，无c874教师执行或源轨迹回放。动作质量尚未对齐开源，不能宣称等价或技能教师合格。200mm三起点3/3，补五起点4/5，-30mm仍失败，未毕业；学生/PPO更新0，c874默认未改。

当前证据见 [200mm接管修复报告](equivalent_controller_v1/STEP200_PHASEPLANE_REPORT.md) 和 [逐例结果](equivalent_controller_v1/STEP200_PHASEPLANE_RESULTS.json)。实际回放在 equivalent_controller_v1/replays_step200_phaseplane/，失败视频同样保留。

[REPORT.md](REPORT.md) 是旧教师路线历史，旧1/3及所有失败保留；不能将其教师/学生分数继承给当前原生控制器。旧207例矩阵被用户停止，未重开；当前五起点失败解决前不做学生蒸馏。

2026-11-16人类动作质量纠偏及逐帧对照见 [动作质量报告](equivalent_controller_v1/motion_quality_audit_20261116/REPORT.md)。源端、当前MOD4、两个隔离探针及严格配速失败均保留，未修改当前控制器或开训。
