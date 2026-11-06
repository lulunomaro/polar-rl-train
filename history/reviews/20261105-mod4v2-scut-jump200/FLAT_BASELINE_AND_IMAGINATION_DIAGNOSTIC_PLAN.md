# 当前模型平地基线方案与想象命令错误

2026-11-06，北京时间。本次接续用户要求的原因复盘。final5936已经保存、退出、独立80和全部实际回放；本文件是基线实施方案及新增CPU诊断，不是已完成的新训练或技能评测。

## 新确认的适配错误

真实Newton任务的Commands固定为(.6,0,0)。BPTT的FudanJumpMdp.goal_with_context直接读取context前三个命令槽；context还在35:38重复保存critic的三个命令槽。

ctx_reward_learner.py先计算next_context = context + context_predict_mask * delta_context，再把next_context传给project_predicted_context。当前未传predict_context_mask，因此mask默认为全1。supermimic_newton.py里“Command is held”的赋值value[...,:3] = context[...,:3]，右侧已经是预测更新后的context，只是复制回自身；它没有原始命令可恢复，也没有阻断命令预测误差。随后goal根据这个值更新。

使用当前真实适配器、CPU合成context和明确注入的非零预测误差，重复H1/H8/H32：

| 合成诊断 | 当前实现 | 仅mask对照候选 |
|---|---|---|
| 每步注入速度命令误差+.001 | 保留误差 | 只对命令0:3/35:38屏蔽delta |
| H1/H8/H32的vx命令 | .601/.608/.632 | 全为.600 |
| H32命令 | (.632,.016,.0064) | (.600,0,0) |
| goal_x对该注入误差的梯度H1/H8/H32 | 1/8/32 | 0/0/0 |
| 其它context槽 | 两arm逐项相同 | 两arm逐项相同 |

这证实“短想象期间固定命令”的实现不成立。注入误差是人为fixture，不能冒称final5936的实际命令漂移或证明它单独导致critic失真。只读原replay的先前校准已确认critic超量级；两条证据相关但未完成因果对照。mask对照只说明修正方向，不是生产补丁、学习改善或完整resume通过。

可复现脚本：N/diagnose_imagined_command_hold.py；完整结果：A/reports/IMAGINED_COMMAND_HOLD_CPU_REPRO.json。脚本直接引用本chat适配器，没有载入生产PT、创建环境、物理步、优化器、GPU分配或SSH。两份依赖源码bytes/SHA写入报告。原模型、共享vendor、冻结生产源未修改。

另一个已核清范围：Critic.forward只有输入RunningNorm，没有输出return归一化；policy_update直接将critic加入折扣奖励，critic回归目标来自想象轨迹及自身bootstrap。因此不能用“这是归一化的value所以可超±80”解释既有校准结果。归一化统计漂移/想象分布/多步误差的具体影响仍未隔离。

## 同一当前模型的基础对照

继续固定HW300N60/contract00199c26533a9adaca6a35a49d30e8b8b27182230772674bd936d8b527169f4e、Newton/SolverMuJoCo/MuJoCo-Warp、2.5ms/32/LS15、400Hzphysics/100Hzfeedback/50Hzpolicy、原D0–D7及六执行器机械投影。闭链10mm/mimic.01rad继续单env重置。固定这些条件是为了比较，未新增物理门槛或关闭DR。

历史E0必须区分两代来源：

- 原selected E0 iteration31984，14031973B，SHA a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a，EXPERT_NORMALIZATION_REGISTRY_v1.json记录为flat standing/running/turning来源，注册表本身不等于当前v2通过。
- v1后训练E0 source：/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR1_V4_20261102_120158_1793592118216803700/roles/E0/production/model_final_complete.pt，14035411B，SHA 6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693。已在旧270mm场地完成的同端点输入对照不能称当前v2平地能力，也不重跑那次once。
- 当前冻结teacher是Newton PPO881，SHA 1ef8b57ae5ad3bae01f1f8febe948896480cbad575a57f9121d0eb32e205e03e，本身0跳台成功。当前full5936继续保留，不能把任一旧E0 fullstate直接覆盖进当前plant。

下一实施先做有限的地面支撑/指令方向/实际目标跟踪/压伸响应对照。新平地constructor只替换训练地形和命令协议；不能顺手改奖励族、动作尺度、求解器或DR。原support bank姿态与z=.38的出生下降需单独量化，区分落地恢复与已接地起跳，不能以rawflight当自主跳跃。

## 基线候选协议（尚未执行）

| 子项 | 预先明确的输入 | 主要输出 |
|---|---|---|
| 地面支撑与停车 | 平地、零速度命令、固定合法腿目标 | 双轮接触、机身姿态/漂移、非轮接触、闭链/mimic与重置 |
| 前后行驶 | 同一plant，分段0→+.2→+.4→0→-.2m/s | 稳态实际vx、方向/延迟、速度误差、腿/轮target实际跟踪 |
| 转向与停止 | vx=0，yawrate分段0→+.3→0→-.3rad/s | 实际yawrate、停止漂移、roll/pitch与轮滑 |
| 支撑压腿/伸腿 | 同一机械合法范围内对称轨迹，先确定目标映射 | 电机pos/vel/torque、电压扭矩限幅、气弹簧行程、闭链和支撑力 |

上述是可实施的对照输入，不是已经证明安全/通过的命令包，不再凭本文件增加硬件动作权限。训练阶段拟用普通PPO，先比较当前已有策略/来源的实际表现再选初始化；新平地reward配置需明确实现和记录，不能沿用jump-only16项而称行走基线。当前未编写或启动该训练配置。

基线至少保存目标与实际速度、姿态、腿与轮target/actual、扭矩与限幅、分body接触、400Hzphysical_transition_valid/数值/约束重置、完整episode和命令曲线。数值异常环境与其余统计并列。先看全部案例/误差分布，不事后用一个均值或timeout声称学会。复用原独立80和实际回放收尾，避免另建相互重复的验收工具。

平地站稳/行驶/转向/停车得到可重复证据后，下一阶段才练接地压腿→自主双轮起跳→落地恢复；最终仍必须真实越过单200mm直角沿并双轮稳定落台，低目标训练不等于毕业。

## BPTT隔离顺序

先在CPU候选修正命令固定和goal语义，再在可复用的小fixture核梯度与四Adam/replay/RNG恢复；共享vendor/foreign不改。后续确需生产数据时，在一次必要的新数据读取内完成比较，不反复decode旧final。固定同一数据/状态比较真实reward、短程return、critic与bootstrap分解及H8/H16/H32预测误差；想象目标通过尺度校准后，再与普通PPO做同起点真实策略对照。

改变predict_context_mask会改变既有extension_contract；旧完整恢复的严格比较不能直接绕过。实际修复时需要明确记录仅mask语义迁移，保留未变模型/四Adam/replay/RNG，并在同一fixture证明接续，不能把新配置冒称原契约逐字段不变。

现有训练不启动，未修复critic、未声称mask修正即可解决训练。本次仅新增明确可复现的适配错误和基线方案。原300s完整checkpoint、原每窗3600save+300exit/累计100h保守上界71437.705711秒、直接真实空闲GPU/noledger及foreign隔离保持。

## 本次读者错误与范围

PowerShell ConvertFrom-Json在CURRENT_STATE已有GO/go大小写并存键上拒绝；随后Python314 json读取成功，未改原键。一次rg把Windows通配符写进路径参数遭os error123，已用目录加-g读取。两个错误只发生在本地读取，未改变模型/状态或产生SSH。原工具输出保留。
