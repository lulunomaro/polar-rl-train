# 2026-11-13 连续上台阶动作调查

冻结本轮最优iter24692，按每2.5ms记录关节、动作、驱动力矩/功率、接触、轮速和姿态；四例名义MuJoCo，无优化器更新。

**动作：撞立面→前导向小轮搭台面→前俯收腿抬轮→落轮压缩→恢复再加速，逐阶重复。** 约0.09m/s最低速度发生在攀爬末段/落轮时，旧“已经站上一级平台”的说法已在报告更正。

- [完整分析、失败对照与训练含义](REPORT.md)
- [半速动作](figures/STAIR_MOTION_HALF_SPEED.gif)
- [八个关键帧](figures/STAIR_KEYFRAMES.png)
- [速度、姿态、腿长、轮速与支撑曲线](figures/MOTION_PHASES.png)
- [全部动作指标](evidence/MOTION_SUMMARY.json)
- [时间对齐与旧轨迹一致性](evidence/VALIDATION.json)
- [实际完整冻结权重](../MOD4V3_FLAT_SPEED_REPAIR_20261112/weights/selected_flat_speed_candidate.pt)

运行capture_motion.py会新建四个固定case目录；已有结果不要覆盖或重跑。原始成功/失败数据均位于evidence，源快照在source_snapshot。analyze_motion.py和render_motion.py只消费已有轨迹，可重建指标和图。Windows解释器D:/claude2/fangzhen/.venv/Scripts/python.exe；执行场景资产来自已冻结的成熟交付包。迁移路径后用capture_motion重新生成新案例目录里的绝对mesh路径。

原始权重、机器人和训练配方不改；当前未开始连续台阶专项训练。完整原始数组、图、接触JSONL、配方源码与报告一起Git归档，同步回执另附。
