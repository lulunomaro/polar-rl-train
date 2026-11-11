# Step7 剩余 DR 合并适应（2026-11-11）

用户明确“剩下的能一口气全部训了吗”，随后“开训”。本轮覆盖此前README逐项推进的限制，合并剩余D2/D3/D6/D7/D8/D9和MOD4可行reset分布；保留已适应的独立质量、输出倍率、分部位材质、物理延迟和速度推扰。从push020m、iter22141、SHA`b3eec7bae3045b24a95ea7cd2940a3e1f0b062841cc47ab1785a627bea36408a`完整PPO恢复，fresh物理episode。

- 4096env、2400s，300s完整checkpoint并检查。fixedLR3e-5、clip.1、3epochs，其它PPO不改。
- 奖励仍指数追踪＋对称平方项`−0.5e²`；物理2.5ms、PD10ms、policy20ms、TGS32/4；闭链2mm单环境reset；接口35/78/6与原motor包络保持。
- COM startup固定X±.04、YZ±.02m；PD Kp/Kd独立.75–1.25，first/720全局步eligible reset；主动显式PD、被动原生阻尼按真实施加路径接。
- 关节摩擦startup全范围，按原组和字段：主动腿static/dynamic/viscous，轮与被动static/viscous。补入native f3r1对应参考front3，避免semantic/native名漏组。
- 气弹簧阻尼为原生3×.5–1.5，去掉本profile继承的附加阻尼力矩；原plant刚度2000保持，不移植参考.01刚度缩放或第二套气弹簧。
- 外力每轴±10N、力矩±1Nm，沿用5–10s和10策略步hold；观测噪声full幅度，仍只作用原sensor槽。
- reset正常.5、ground总.5（参考modes.3+.2，上层旧prob.2不重复乘）；ground逐腿独立positive.6/negative.4，root.25m、0.2s零力矩和1.5s低命令。正常腿长.13–.32m，角−π/2至3π/4；轮角±2π、腿主动速度±π/2、轮速±50rad/s；被动速度由闭链运动学切向生成。
- 参考ground腿长上限.36m超过MOD4实际可达.346699m，因此按真实机构截断；不复制SCUT连杆尺寸、不修改plant。reset bank3072姿态由交付运动学精确支路生成，离散均匀样本近似参考连续分布，原始生成器/源SHA与实际范围保存。
- 新checkpoint实际保存DR samples/timers字典；恢复仍fresh episode，不声称完整物理瞬时状态续接。

原Step7主冻结mass040与推扰020不覆盖。64/4096固定父权重短测及真实失败分别保留，短测数值正常后启动主轮；单环境闭链reset不扩为整批失败。现有来源目录、其他AI未提交改动不改。本轮PT实体与源码/报告按用户要求Git保存，网络走7897。
