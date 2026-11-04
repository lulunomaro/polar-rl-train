# 200mm 底盘支撑站爬：2026-11-05最新人类指令

本聊天人类明确要求：“站着上台阶……抬高底盘给奖励让机器人站起来，然后底盘卡上台阶，然后收腿上……设置定时任务，反思经验继续推进”。这覆盖本聊天此前必须飞行越沿的选择；本分支允许底盘/导轮形成真实支撑。其它聊天jump200分支和100小时授权不被本分支挪用或停止。

目标为单个200mm直角台阶，抬高底盘、接近并搭上水平台沿、有支撑后收腿抬轮、双轮整轮在台顶稳定至少0.5s。原2.5ms/TGS32/4、增强USD/完整D0–D7、PD/DC/队列、0.01m闭链/0.01rad mimic、硬件目标限位和原canonical严格reserve保留。动作仍由PPO策略输出，无预写运动和外力辅助。

旧站爬V30已远端完整结束：final1709、新237PPO、45504physics，checkpoint8924208B/SHA56459cb4ae1e052d6061ae42218477acd3fd8760a0a804e4e5cdf618f1c55f5b；OWNER_EXIT1793796843.4999783、errornull、wait/cost/release完成。独立80 strict0、both-top0，15提前终止/65满10s、mean9.1995。其原closed transfer仍unused，先freshLOCAL释放后取原结果并原生审图，不重评。

失败经验：旧训练还在平地准备阶段，既无真实200mm台沿训练，也没有台沿支撑后的收腿奖励；旧底盘/导轮接触>1N持续20控制会终止。已有髋target限位合规，但受载实际角低于target，不能只根据target当作站起。初始0.38m无支撑的下落不算主动蹲下或站起效果。单纯加高度常量奖励会留下原地站高的捷径。

新候选改动：真实单台阶训练场、前进门控站高、位移增量、实际台顶支撑、支撑后实际轮缘高度、双轮台顶稳定奖励；停滞与长时间挂台扣分。保留成本项，关掉与新目标相冲突的旧静止正奖励。只有upright且root高、对应body有真实台顶向上法向力和接触点的底盘/导轮接触免除contact termination；侧撞、落地、倾倒和所有数值/闭链/mimic保护保持。

当前仅本地候选。NumPy检查不代表真实SDK/恢复通过。外部E3 collector39092/parent51972正在使用串行连接，当前network0/launch0；不抢连接或canonical。

下一次定时执行先读CURRENT_WORK_ORDER和该目录：完成unused V30 closed transfer、已有轨迹渲染和全80审查；针对本候选核实际冻结SDK的contact sensor/body ordering和完整恢复命令字段；必要时修正独立候选，冻结小文件及shared SHA引用。新生产只在freshLOCAL FREE、四卡新读取、原canonicalNone/privateGPU/finite准入后进行原3600save+300exit有限窗；不复制runtime、不重复old once、不逐小时原样续训。每窗立即独立80、400Hzmanifold/bodyposes、原生侧俯及曲线检查，再决定修复或接续。所有失败与报告进入Git。

技能未完成时定时任务持续推进；成功、失败、预算/资源/网络问题或需要人类行动才通知。普通健康等待保持静默。
