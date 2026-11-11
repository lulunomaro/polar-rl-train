# Step7 双侧速度平方惩罚加倍独立实验

2026-11-11用户明确要求超速、欠速再加强一档，并从父检查点单开40分钟。沿用第二轮直接父remaining_010m（iter22265，SHA978994b2...），独立目录执行。唯一行为改动为track_lin_vel_xy_square权重−0.5→−1.0，sigma=1；指数奖励不变。误差e=command_vx−root_lin_vel_b_x×cos(pitch)，每步为−e²×0.02。超速/欠速对称加倍，不额外叠加单侧惩罚。

沿用819/4096名义、3277完整DR，同一随机reset分布；奖励以外的PPO/DR/solver/plant/35actor78critic6action保持。原父和两轮结果保留，不覆盖。40分钟、每5分钟完整PPO检查点并回放检查；不以短冻结探针声称训练有效。具体参数PLAN.json，实际启动/权重/结果追加到evidence与weights。

当前状态：准备完成，先执行实际奖励路径短探针；训练尚未启动。


已于2026-11-11 11:37:42 Asia/Shanghai启动，PID1044972，实际系数−1.0；首完整PPO已保存到weights/model_first_complete.pt，iter22266、SHAf8384096a14d2942c688abfa8090b14ce09e6189f03786b671dfe861c39ce384。短奖励路径已验证，详情REPORT.md。
