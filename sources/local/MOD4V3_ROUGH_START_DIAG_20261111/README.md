# R1速度误差原因归档与原配方续训建议

日期：2026-11-11。两组固定权重配对排查已完成，无训练。

在相同R1 level3坡面零速起步下，轮胎摩擦是本次fullDR额外倒滑/欠速的主要被测因素。只恢复轮胎静/动摩擦，R1三次005m均速由−0.0609提高为+0.7426m/s；只消除轮胎弹跳几乎不改善。正常加速/爬阶耗时同样存在，不能把全部欠速归为退化，也不能宣称问题已经全解决。

- [完整原因报告与边界](REPORT.md)
- [原R1奖励与接续建议](NEXT_ROUND_RECOMMENDATION.json)：−1.5e²，指数权重1.2，R1_010m/959dc6a5…，fullDR保留，建议40min/每5min完整保存；未启动。
- [接触材质配对结果](evidence/CAUSE_SUMMARY.json)
- [实际机理数据](evidence/MECHANISM_SUMMARY.json)
- [非目标输入比对](evidence/MATERIAL_PAIR_EQUALITY.json)
- [MuJoCo模型保持检查](evidence/MUJOCO_PLANT_COMPARISON.json)

本目录按独立诊断归档。两份完整原始NPZ与输入、失败、回放smoke均保留。活动MuJoCo日志不固定覆盖档案，稳定副本位于evidence/viewer_snapshot_20261111。
