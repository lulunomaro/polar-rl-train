# 下一单一干预：低位正速度tracking奖励与真实抬升进度耦合

## 触发证据与边界

fresh1cd / N20000 / 25次PPO已真实完整收口，两Adam各500、2400万优化转移；原N80 qualified但0/74，同五姿候选h=.198817/v=.684080/XY=5.325706，冻结1cd=.241437/.038073/.639393，严格工程信用双方0/5。原母版继续保留，H1/其它专家/Registryv12不动。见[本轮实测](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_FRESH1CD_CLOSED25_QUALITY_RESULTS_V1.md>)。这不是已证明奖励因果诊断，也不按25/205数盲续。

只读critic核对已排除当前worker自己把线速度拼到尾部的假设，不据未知1cd原始schema重排输入。1200控制恰是低位400timeout整数边界，训练末态.1781可能刚reset，不将它当全程/峰值高度。

## 实际源链支持的窄假设

- [原E3掩码](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/e3_recovery_runtime_v1.py#L9-L25>)仅height六项与lin_vel_z，不屏蔽三个正tracking项。
- [linear_exp/yaw_exp](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/scut_flat_rescue.py#L19-L41>)直接计算零指令速度误差的exp，不依赖起身高度/recovery阶段。
- [注册项](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/original_runtime_refs/mod4_task.py#L1658-L1670>)为track_lin_vel、track_lin_vel_tight、track_ang_vel。[旧可选height gate](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/original_runtime_refs/mod4_task.py#L620-L637>)默认off且这三个实际注册函数不直接调用它。
- 因而存在“低趴不抬身时仍拿正tracking收益”的可检验激励冲突。源码可证明公式，旧run实际effective权重未有单独回读，不能用defaults冒称已证明权重或整段reward贡献。

## 唯一行为改变

仅训练recipe>=13，将这3个既有正tracking项原返回值乘：

```text
clip((真实root高度_above_origin - .1781) / (.23 - .1781), 0, 1)
```

保持原func/params/正weight和std；在新constructed config中核对实际三项weight>0，记录实际函数、参数来源、两端高度。不会改负误差项、height六项、起身potential、动作代价或其它reward。旧fall0..11与normal12完全走原值。新门控连续到.23饱和，不降低hcmd=.25，不改原/新接受条件。

只重建fresh1cd 8+8 MLP warm分支，encoder随机fresh/latent列0/STD.5/两Adam-LR-private-generator-计数fresh，与前一pilot相同seed/初始化设置/N20000/T48/max25，不继承坏246ac/3e64/8af4。Fudan核心、5frame监督encoder、PPO 5×4、物理/fullDR、命令、31体/原限位/400N-k2000-d3/50-100-.0025、五低姿、原fall/normal和8s/400timeout全部保持。不得热补旧sealed runtime，必须新purpose和source hash。

## 被动观测（不是第二训练干预）

复用每次原phase.update已经取得的height/low，不新增physics/传感器/RNG/getter；只加每env一个episode_peak_height向量和6个固定累计标量，记录段内高度采样总和/数量/≥.23数量，以及已结束low episode峰值之和/≥.23数量。reset累加原episode峰值后归原.1781，不额外reset、不给它当acceptance。typed state保存/恢复包含新buffer，保持现有全部phase字段。

这样可区分“末态刚reset”与“段内曾经抬升”；不写逐步日志/不加控制回调/不改奖励值之外的行为。summary仍明确training描述非独立接受率。

## 实际执行与判定

原唯一canonical、authority2EX/privateGPU_EX、train finiteSH/eval finiteEX、reserve86412.86069250107、3900/3600/300及1800preGO、charge_values/inner+outer实际wait均不变，无外国signal/清锁/账本副本/退款/扩预算。源模型每真实用途仅一次物理读/hash/CPUdecode，Git/状态不打开模型或raw。

新有限窗完整保存、SDK close、原wait/结清/释放后，原N80/160/seed20260928/74+6/fullDR/一reset/0优化和同五姿名义MuJoCo再实跑，门限分母不改；新训练gate从不安装进评测。所有成功失败、被动证据、实际effective参数和保留/晋升决定按下一有意义阶段feature-only唯一annotated trial归档，main只读。单次AST/限定差异检查后转真实运行，不开CPU/seal/审计农场。
