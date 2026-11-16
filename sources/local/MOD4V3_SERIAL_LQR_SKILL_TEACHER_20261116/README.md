# MOD4v3 Serial技能教师

当前为实验性原生 MOD4v3 LQR/VMC，无c874教师执行或源轨迹回放。动作质量尚未对齐开源，不能宣称等价或技能教师合格。200mm三起点3/3，补五起点4/5，-30mm仍失败，未毕业；学生/PPO更新0，c874默认未改。

当前证据见 [200mm接管修复报告](equivalent_controller_v1/STEP200_PHASEPLANE_REPORT.md) 和 [逐例结果](equivalent_controller_v1/STEP200_PHASEPLANE_RESULTS.json)。实际回放在 equivalent_controller_v1/replays_step200_phaseplane/，失败视频同样保留。

[REPORT.md](REPORT.md) 是旧教师路线历史，旧1/3及所有失败保留；不能将其教师/学生分数继承给当前原生控制器。旧207例矩阵被用户停止，未重开；当前五起点失败解决前不做学生蒸馏。

2026-11-16人类动作质量纠偏及逐帧对照见 [动作质量报告](equivalent_controller_v1/motion_quality_audit_20261116/REPORT.md)。源端、当前MOD4、两个隔离探针及严格配速失败均保留，未修改当前控制器或开训。
