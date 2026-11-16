# MOD4v3 Serial技能教师

2026-11-16 19:22：当前只有前段修复单例候选，动作质量未验收。200mm标准起点前段峰值2.824°、window峰值6.644°、稳定4.46s，但入lift仍丢速且短暂后退。不扩矩阵、不进示范池、不蒸馏/开PPO，默认c874不变。

最新[前段修复与全试错报告](equivalent_controller_v1/prelift_contact_repair_20261116/REPORT.md)，参数在同目录CANDIDATE_PROFILE.json，视频为SOURCE_BASELINE_PRELIFT_REPAIR_1X.mp4。旧3/3和4/5仅为原版历史成绩，不继承到新候选。

当前为实验性原生 MOD4v3 LQR/VMC，无c874教师执行或源轨迹回放。动作质量尚未对齐开源，不能宣称等价或技能教师合格。200mm三起点3/3，补五起点4/5，-30mm仍失败，未毕业；学生/PPO更新0，c874默认未改。

当前证据见 [200mm接管修复报告](equivalent_controller_v1/STEP200_PHASEPLANE_REPORT.md) 和 [逐例结果](equivalent_controller_v1/STEP200_PHASEPLANE_RESULTS.json)。实际回放在 equivalent_controller_v1/replays_step200_phaseplane/，失败视频同样保留。

[REPORT.md](REPORT.md) 是旧教师路线历史，旧1/3及所有失败保留；不能将其教师/学生分数继承给当前原生控制器。旧207例矩阵被用户停止，未重开；当前五起点失败解决前不做学生蒸馏。

2026-11-16人类动作质量纠偏及逐帧对照见 [动作质量报告](equivalent_controller_v1/motion_quality_audit_20261116/REPORT.md)。源端、当前MOD4、两个隔离探针及严格配速失败均保留，未修改当前控制器或开训。
