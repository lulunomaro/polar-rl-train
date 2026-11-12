# Rough-v1 训练与复现

完整机器可读配方：[EFFECTIVE_RECIPE.json](EFFECTIVE_RECIPE.json)。使用独立profile `rough_scut_v1`；运行 `launch.py train120m_scut_rough_v1_r1 --kind train --num-envs 4096 --seconds 7200`。实际启动命令、源清单及父SHA均见evidence/TRAIN_LAUNCH.json、UPLOADED_MANIFEST.json和STARTUP/RESTORE。

25ms/20ms延迟等旧路径不用于本轮；当前传感器5–15ms、动作5–10ms按物理时间推进，actor动作槽保持原始策略输出。原DR全范围保留。

参考13列是11种地形，共1.3原始权重；本轮非平地权重比不变，平地独立20%，复制成75列。空中出生请求根高.12–.42m，选可行bank支撑高≤.34m，并抬至其上至少.08m；初始vx和临时指令均限制±2.2m/s，参考roll±.1、pitch±.2，临时命令3s。宽阶与指定高速下阶轴向出生。

每五分钟MuJoCo是平地保留能力筛查；轮末另做PhysX固定权重同批比较，不能把MuJoCo结果替代完整DR能力。
