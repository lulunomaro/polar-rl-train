# SCUT Rough-v0 统一科目：2小时（2026-11-12）

用户授权：直接统一训练华南虎Rough-v0，不再分R0/R1/R2短科目；PPO7200秒，每300秒完整保存并检查。当前状态：准备启动，尚无本轮训练成绩。

父模型：R1第二轮005m，iteration22959，SHA `0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f`。完整恢复actor、critic、STD、Adam和RNG；新物理episode。R2最后保存点不作为父。

科目：统一使用保存的SCUT `rough_rotation_stair` / Rough-v0全部9地形族、10级难度：栅格1–3cm、坡度0.05–0.15、正反浅阶5–15mm、正反中阶25–40mm、随机起伏0–3cm和平地。所有级别从启动同时采样，固定各env类型/级别；参考顶层curriculum为空且height-offset curriculum关闭，不能称按能力逐级毕业。

指令：参考15%低档小陀螺、15%高档小陀螺、30%高速组合和其余普通/航向/站立指令；各地形按保存配置覆盖高度。小陀螺6.28–14.14rad/s，gyro的vx±0.1m/s；高速组合2.0–2.2m/s、wz±2pi。ground reset最初1.5秒沿用既有恢复指令。没有air reset和airborne新增奖励。

保留MOD4迁移适配：35actor/78critic/6action、机身坐标指令、2.2m/s速度上限、现有完整DR与20%名义、20%平地独立交叉、原−1.5e²与指数速度权重1.2、2.5/10/20ms、TGS32/4、2mm单env闭链保护和电机包络。MOD4无云台，不新增云台观测。地形70列替代参考14列以分散4096克隆；地形族比例按保存参考，同一科目并行覆盖。

PPO：4096env，LR3e-5 fixed，clip0.1，3epochs，rollout24，seed66。训练计时从首个PPO rollout开始7200秒，启动/探针/验收另记。训练所有300秒保存完整PT，原子写入并记录SHA；本地下载校验及独立MuJoCo保留能力回放，与PhysX粗糙地形成绩分开。

原R1四级地形计数仅保留为父来源，不能重新标成当前十级统计。模型不自动晋升、不覆盖既有冻结或实车调试包。PT本体和训练/评测证据归档Git，推送走7897代理，保留TLS校验。

详见 `PLAN.json`、`TRAINING_RECIPE.md`、`evidence/`。所有启动失败、实际失败与最终成绩如实追加。

完整机器配方见PLAN.json；启动后以STARTUP、RESTORE、PPO_EFFECTIVE和TERRAIN_STARTUP核对实际生效值。


主训练实际首次更新：北京时间2026-11-12T02:57:38.481482+08:00，iter22960；完整PT已下载核SHA并实际读回检查35/78/6、actor/critic/Adam/RNG及9×10地形状态，全部参数有限。父PPO恢复17个optimizer条目，LR3e-5 fixed、clip0.1、epochs3。启动实际2.5/10/20ms、TGS32/4、完整DR、−1.5e²，airborne/air reset关闭。本轮正在运行7200秒预算，尚无最终成绩。

配方读取说明：`EFFECTIVE_RECIPE.json`整理实际启动值；原始`PLAN.json`按启动原件保留。后者有两个继承的描述字段仍写rough_r2/air overlay，实际入口CLI始终是rough_scut_v0，STARTUP确认air_reset_fraction=0、airborne=false，环境源码也没有R2继承。这里修正配方描述，不改训练进程、奖励或分布。


## 已完成与后续定位

实际7206.137秒/848更新；26份完整PT/25种字节，全部PPO/STD/Adam/RNG/DR/9×10状态真实读回。最终选择见DECISION，综合接续R1父，本轮100m/120m未晋升。此配方冻结用于复现，不自动开启下一预算。原始启动PLAN不改；EFFECTIVE_RECIPE整理实际CLI与STARTUP。后续复制源码/配方建独立试验，再显式指定parent/checkpoint；同env数可恢复完整十级状态，新物理episode。
