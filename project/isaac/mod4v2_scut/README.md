# MOD4v2 华南虎单200mm跳跃

人类2026-11-05要求停止旧训练、换MOD4v2并用华南虎奖励重训。运行代码引用原SCUT公式、训练循环、完整保存和独立80评测，仅新增v2资产/目标/复位接入。新actor、critic、STD和Adam从随机初始化开始，旧v1失败策略不载入。

模型来自`F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package`：300N全伸展标称力，200mm伸展、140mm压缩、60mm行程；k2000/d3仍为工程近似。主动hip/crank与从动坐标连续，保留真实CAD等效止挡。

实际OmniPhysics110对发布USD的无限角mimic与单侧角界导入失败，首个20k任务在0PPO时安全关闭。独立新任务层把开放角端点编码为±1e20度数值哨兵；真实有限端点、关节类型、mimic、几何、质量、COM和气缸保持。小规模原生检查确认31body/30DOF、全部硬界回读、20物理步mimic最大误差1.65e-5rad且完整日志无引擎错误。被否决D6表达及读者错误都留存。

奖励采用固定SCUT commit `1a26356d6f591734d4f6f666f5cead1a6925da67` 的保存基础reward字典，启用源码可选的push-height、push-velocity和peak-height公式，权重2/1/2。单200mm场地、实际ray触发、MOD4轮半径及禁物理助推是明确任务适配，不声称公开训练的逐字复现；v1累加projection/bilateral/tuck等奖励修补不带入。

20,000环境、原canonical/reserve、3600s保存+300s退出、完整actor/critic/STD/Adam/DR/RNG/queue/counter保存、退出后立即独立80/seed9137/400Hz评测保持。目标仍为地面主动向上离地、整轮腾空越沿、双轮真实台顶稳定0.5s。

当前真实状态和所有失败见`history/reviews/20261105-mod4v2-scut-jump200/WORK_ORDER.json`与`EVIDENCE_INDEX.json`。原目录及once不清除、不重放。`BINDINGS.json`记录唯一共享依赖；新任务不整树复制旧生产目录。

第二次0PPO失败来自旧motor_stop_terms对连续关节None端点的假设；新v2奖励适配器明确将4个无独立角界电机的限位辅助代价返回0，不修改SCUT奖励公式和权重。6CPU和3phase真实源reward调用的合成端点均有限；独立rewardapi03已启动，FIRST以实际回传为准。
