# 单个200mm台阶跳跃：来源与当前范围

人类2026-11-04纠正：“我说的是跳台阶，机器人跳上去200mm的台阶不是这个碎台阶”。当前任务是从低地自主起跳、越过单个200mm竖直台沿、双主轮落在水平台顶并稳定恢复。此前25–40mm小阶梯及其完整训练保留为任务选择错误，不能作为200mm完成证据；此前“轮子允许保持接触”的选择由本次纠正覆盖。没有重新要求270mm或必须第一次飞行成功。

固定华南虎commit `1a26356d6f591734d4f6f666f5cead1a6925da67`的原始`agent_tasks/manager/mdp/isaaclab/terrains.py`分别定义：

| 源对象 | 原阶高 | 原踏面 | 原平台 |
| --- | --- | --- | --- |
| STAIR_FOR_RM | 200–220mm | 1.5m | 2m |
| HIGH_STAIR_FOR_RM | 150–350mm | 1.25m | 2.5m |
| HIGH_SPEED_STAIR_FOR_RM | 150–400mm | 1.5m | 3m |
| 本次误选inverse-mid | 25–40mm | 0.1m | 1m |

`wheelbipe_V14/cfg_utils.py`的高台阶命令使用高度.22–.34m、正负1.5–2.7m/s、接近轴向朝向、禁止special mode和预定义空中出生。公开`rough_rotation_stair`保存YAML的状态机总开关、Airborne/JumpTakeoff/Stair均关闭；不能称其为起跳训练配方。原V14源码另有Airborne着陆处理、弹道JumpTakeoff与真实raycast检测StepUp/Stair；这些是可选源码能力，启用和参数选择必须明确记录，不能冒称公开权重原本如此训练。

当前新增独立`jump200`任务是明确适配：低地(0,0)出生，单台沿x=.8m，水平台顶z=.2m，台顶延至x=3.5m、横向±3.5m；朝向只在正x附近扰动。底面与平台显式三角形mesh，旧270mm四边场地/小阶梯源码及冻结包不覆盖。允许失败重试；400Hz独立评测要求地面支持后有真实向上飞行、双轮完整后缘在离地状态越过200mm台沿、双轮真实台顶支持，无非轮支撑，落台后恢复稳定.5s。爬台、出生下落、单轮触台均有反例检查。

起跳候选复用原JumpTakeoff弹道辅助计算，目标body相对地面峰值.55–.60m；来源默认push_start.20/release.38等值保持。真实轮前raycast的.18–.22m阶跃请求起跳状态；StepUp不额外抬高全程height命令。push高度与竖直速度跟踪/peak奖励采用上游已有reward types，权重2/1/2，为本项目明确训练配置选择。起跳阶段关闭相冲突的基础高度平方/紧高度指数和竖直速度代价；Airborne辅助保持，无外力、速度赋值或其它物理助推。双轮实际飞跃落台后把前进命令归零，以便学习稳定恢复；这同样是本任务命令适配，不是上游原样配方。

增强MOD4v1 USD/contract、400N气弹簧、k2000/damping3、.0025/TGS32-4、50/100/400Hz、完整D0–D7、原PD/DC/clip6/contract目标限位/CAD/D4和.01m closure/.01rad mimic不改。PPO保持既有保存配方。

8项CPU检查已通过，包括真实起跳+200mm越沿后连续.5s稳定、爬台拒绝、出生下落拒绝、非轮/运动未稳定拒绝、失败后重试、台面mask、无物理助推及raycast事件→起跳请求→上游reward执行。首轮fixture直接写事件后被真实StepUp重算清掉，原false保留，改用真实前扫高度变化fixture后通过；没有为测通过改生产事件。当前只有限80原生评测，0optimizer/0ledgerwrite；模型来源为小阶梯final `f6b6b649…`，不是跳跃专家，不把评测或CPU通过当技能成功。
