# Step7 冻结后新增输出比例误差 DR

2026-11-11，Asia/Shanghai。用户要求“开始推进下一步dr”，并要求冻结 Step7 模型和训练配方。本轮从质量适应 040m/final 继续，仅新增腿部0.8～1.1、轮0.9～1.1的独立输出倍率。

## 冻结基线

[冻结目录](../MOD4V3_STEP7_FROZEN_20261111/README.md)保存完整support、PLAN、实际STARTUP/PPO/恢复/完成回执与逐文件SHA。模型iteration21754，SHA `23c112b16e9629215c7265124925daaf0f9b6bbbb62be61689c714ba1fc7a772`，本地及远端都有完整副本；远端文件0444、目录0555。实际冻结回执在 `evidence/FROZEN_BASELINE.json`，完整权重不入Git。后续运行使用新目录。

## 唯一新增项

每env/主动电机独立抽样；在完整raw PD力矩上乘倍率，然后应用原DC包络；原加性力矩噪声及其最终限幅保持。参考华南虎事件源码的计算路径、reset首次触发和`min_step_count_between_reset=720`语义已核对并保存到reference。本实现相隔720个全局策略步后遇到reset才重采，episode内保持。

原Step7物理延迟、startup独立质量/惯量、轻量COM、增益、摩擦、弹簧阻尼、外力和观测噪声均保留。actor35D/action6D/critic78D；critic现有stiffness/damping字段反映乘倍率后的有效PD增益，实际已施力矩字段保留。奖励、solver、电机常数、资产及控制频率保持上一轮。改变的support文件和前后SHA在 `evidence/IMPLEMENTATION_DIFF_INDEX.json`。

## 探针与启动

64env×80steps冻结父actor探针通过：numerical0、reset0、closuremax 0.633511mm。小力矩及饱和力矩的乘倍率/包络输出最大误差均0；719步不重采、720步仅重采所选reset环境；8reset后startup质量/惯量变化0。该探针证明实现与短时物理通过，不替代本轮适应结果。

北京时间 2026-11-11 02:34:36 启动4096env、2400s训练，按原框架完整恢复actor/critic/std/Adam/RNG，fixed LR3e-5、clip0.1、3epochs，40分钟/5分钟检查点。恢复17个Adam条目，首更新iteration21755完整保存SHA `4e3e3e263230381beeb37a0d29dde7781c9c2b72c8859b53417b95e001f5c2b4`，actor已改变，numerical0。启动首rollout有1次单env闭链重置，原始计数保留，未提高2mm阈值。后续检查点和真实任务结果由当前chat持续检查，完成后补记。

D5分部位材质与D10速度推扰尚未接入本轮；其余后续DR及Flat→Rough按仓库README执行。
