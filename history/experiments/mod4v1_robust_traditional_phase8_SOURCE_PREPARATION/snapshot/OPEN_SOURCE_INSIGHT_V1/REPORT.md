# SPR与Qi-Q26：对MOD4v1传统保底控制最有价值的启发

## 结论

**有启发，主要是控制结构，而不是把别人LQR矩阵/跳跃增益直接搬过来。** SPR给出了可追踪的嵌入式执行路径；Qi-Q26给出了高度/Roll支撑力MPC、腿长调度LQR和LESO的推导材料。两者都没有给出可直接认证MOD4v1“270mm稳定跳阶”的现成方案。

本次仅指定ZIP目录、选择源码和PDF内容审读：没有执行ZIP里的代码、MATLAB或构建脚本，没有新物理试验、参数替换、旧成绩重判。原R62名义2/2、选定TRAIN1/4 vs同seed旧2/4不变。新材料PH8pending。

## 1. 先弄清这两包实际有什么

| 包 | 实际材料 | 能支持的结论 |
|---|---|---|
| SPR Balanced-infantry (1).zip | 外层21 entries；代码在嵌套chassis/gimbal，另有MATLAB与Futile实验包；本次核外层CRC/size，复用同来源的已提取参考源码 | 可以从任务、行为、控制、VMC直到发送路径追踪；未重新运行固件/实机 |
| Qi-Q26-Leg_Robot.zip | 仅LQR_calc.m（4711B）和17页PDF（1690184B），没有C++/main/task运行工程或生成函数 | 可以审查模型、设计和作者陈述，不能闭合其部署调用链 |

[指定ZIP中央目录证据](<ARCHIVES_CENTRAL_DIRECTORY.json>)；[Qi MATLAB源码](<QI_Q26/source/Qi-Q26-Leg_Robot/LQR_calc.m>)；[Qi PDF原件](<QI_Q26/source/Qi-Q26-Leg_Robot/山东理工大学轮足机器人腿长建模及LESO观测器开源.pdf>)及[带页码文字](<QI_Q26/PDF_TEXT.txt>)。

[SPR外层说明](<SPR/source/SPR%20Balanced-infantry/readme.txt#L1-L9>)明确“底盘妙板02、云台C板”，不代表底盘固件已同时适配两种板。我们的大疆C板/达妙板双路径仍须分别绑定BSP、时钟、CAN与电机域；SPR的3508轮电流协议也不是目标达妙轮电机协议。

## 2. 优先借鉴SPR的相位分工，而非继续让轮子承担全部空中纠偏

### A. 检测离地后，轮侧退出地面控制，腿负责空中摆角

[SPR控制分支](<../SPR_AUDIT/reference_selected/chassis/chassis/Task/chassis_task.c#L666-L731>)在KNN判为离地时将wheel.set_current置零，腿Tp只保留虚拟腿角度/角速度相关反馈。它的theta是虚拟腿摆角与机身姿态的组合，不是直接在四个关节位置上叠加body-pitch偏置。

对照[我们当前MiniHop](<../MINIHOP_V1/controller.py#L65-L99>)，push与flight的轮请求都含25*pitch+4*pitchrate。R62坏例已观察到两轮接近并跨过负向no-load后，原signed-DC允许区间变成正向mandatory-brake；继续请求负峰值并不等于还能提供该方向纠偏。[本次实际工作包络](<../R62_DRIVER_HEADROOM_SAVED_V1/REPORT.md>)只证明模型box，不冒硬件反馈或唯一失效原因。

**建议迁移的是“地面/腾空分域＋轮速/角动量头房管理＋腿摆角通道”，不是简单把轮请求改零就宣称解决。** 单独切掉轮PD可能损失已有纠偏能力；必须与腿的角向控制/径向伸缩分工一起验证。目标达妙在超no-load时box可能不含零，仍须保留原DC/再生限制，不能强制真实τ为0。已保存跨no-load的两帧发生于首hard/次hard附近，不据此宣称整个腾空期都超速、或轮PD已被证明是碰撞原因。

### B. 起跳用腿长/力和摆角两个通道，不只用高刚度关节拉目标

[SPR腿长/力生成](<../SPR_AUDIT/reference_selected/chassis/chassis/Task/chassis_task.c#L898-L975>)与[leg_force接口](<../SPR_AUDIT/reference_selected/chassis/chassis/algorithm/leg_force.c#L14-L25>)将虚拟腿轴向F与摆角Tp映射为两关节力矩。我们现有飞行关节PD则会在整体±40Nm请求裁剪时遮蔽一部分h纠偏，已由[真实请求诊断](<../R62_AIRREF_RESPONSE_CAUSAL_V1/REPORT.md#L23-L36>)验证。

可研究MOD4v1自己的`径向伸缩/轴向力`与`角向姿态力矩`分解，在可行扭矩盒中先保姿态项、再分配伸缩项。**“姿态优先分配”是针对本项目提出的改进，不是宣称SPR已经有严格优先级或力矩可行性证明。** 五杆/等效腿的生成代码不能当MOD4v1六杆、被动闭链和气弹簧的Jacobian直接用；应重用我们自己的全机构FK/Jacobian与符号核查。

### C. 值得首先检查：跳跃时是否被静态气弹簧补偿抵消了助跳

[SPR气弹簧处理](<../SPR_AUDIT/reference_selected/chassis/chassis/Task/chassis_task.c#L956-L973>)在JumpFlyFlag有效时把**控制器软件补偿**清零，机械气弹簧仍保留。源码作者也记录过持续补偿使不同气弹簧助跳效果被抵消的现象。

我们插值使用静态trim的前馈力矩，值得分离其中重力、气弹簧及其他项，确认push阶段是否应保留/淡出某些补偿。先做模型分解与方向核查，不能直接删除整条trim前馈，更不能关闭MuJoCo机械弹簧或削弱原模型以制造高度。

## 3. 阶段切换应随实际腿状态推进；检测器仍要有资格和超时

[SPR跳跃阶段](<../SPR_AUDIT/reference_selected/chassis/chassis/Task/chassis_task.c#L827-L896>)根据测得腿长先压缩、再伸展、再收腿、准备落地，部分阶段才使用计数。相比我们固定0.14s push、固定predicted-air的原型，这能启发按“实际伸展完成”而非只按时间切换，减少D4/负载/增益变化导致的相位漂移。

但它不是可直接照搬的可靠触地FSM：Fn来自控制侧F/Tp及惯性项而非力传感器；作者记录过气弹簧相关偏差、KNN训练数据不足；每周期Fn_flag清零使JumpFlyFlag不单独保证air分支；220计数仍在特定条件下累加，触地条件有注释掉的部分。**必须保留我们现有UNKNOWN、滞回、连续窗口、阶段deadline、异常INHIBIT和默认未绑定权限；腿伸展完成也不等于已确认全体离地。**

## 4. Qi最值得借鉴：把高度与Roll放到同一受约束支撑力分配中

[Qi PDF p1、p8–10](<QI_Q26/PDF_TEXT.txt#L200-L532>)用`x=[roll,rolldot,H,Hdot]`、`u=[FN_left,FN_right]`，同时调总支撑力与左右差，避免独立腿长PID和Roll PID互相对抗；求得的支撑力再与LQR腿摆角力矩一起VMC映射。

这是改进起伏路段/侧身下台阶/落地缓冲的有价值方向。它的N=15、Ts=0.01s看未来0.15s，说明预测覆盖动作时间比单纯追求1kHz更重要。另一路平衡LQR+LESO才是1ms。

迁移前要重新建模：本文26kg、轮距半长0.16m不是MOD4v1；文中FN为绝对支撑还是增量存在“平衡mg/2”与“再加重力前馈”的表述歧义，须统一，避免double-G。20..150N、每步30N变化只是其地面模型限制，不能放到腾空腿上保留正20N下界，也不能替代我们的关节速度—扭矩/功率/接触约束。包内没有MPC C++，作者Linux求解时间不是我们的M4/M7 WCET证据。

PDF p6还明确记录跳跃瞬时放电能力不足导致掉电、比赛转向触阶后规划腿长/摆角的跨越。这提醒我们同时保留跳跃与受控跨阶路线，电源能力/冲击缓冲是独立验收项；仿真机械功率不等于已验证母线能力。

## 5. Qi的腿长调度LQR/LESO：值得做后续ground shadow，不是本次空中急救

[MATLAB 7–50行](<QI_Q26/source/Qi-Q26-Leg_Robot/LQR_calc.m#L7-L50>)随腿长重算6状态/2输入LQR，再[三次拟合](<QI_Q26/source/Qi-Q26-Leg_Robot/LQR_calc.m#L94-L141>)；[63–88行](<QI_Q26/source/Qi-Q26-Leg_Robot/LQR_calc.m#L63-L88>)构造8状态LESO，假设2维matched慢变输入扰动、原6状态可测。可以借鉴按工作姿态调度及扰动观测，但应使用MOD4v1自己的完整模型/状态域。

- Ts=1ms的K/极点不能复制给100Hz、带100Hzboxcar及0/10ms反馈队列的链；增益、扩张模型与延迟必须重算。
- 使用与观测窗口/时间对齐的有效输入，而非把已经超出signed-DC能力的requested τ当真实输入；不要让ESO把饱和/mandatory-brake错误解释成“需要再补更多τ”。实际驱动反馈未绑定时先shadow。
- K/Ae/Be/L逐元素多项式拟合不自动保证整个区间闭环/观测器稳定；极点序号也不等于物理扰动模态。全状态可测和我们相关、延迟的估计状态不同。
- 有界、持续变化的扰动通常只能讨论估计误差界；不能仅凭稳定极点承诺所有冲击误差渐近归零，更不把地面匹配扰动ESO用于替代未知初始角动量或接触许可。

## 建议下一轮顺序（仅设计建议，本次未执行）

1. 先锁定一个MOD4v1跳跃相位/VMC分工方案：径向与角向通道、扭矩优先级、轮速头房及UNKNOWN/timeout策略，旧controller默认关闭不改。
2. 先做气弹簧前馈分解与虚拟功/符号/可行力矩盒零步核查；“撤软件抵消”与“撤物理弹簧”严格区分。
3. 再以独立新case做单改动名义flat→匹配条杆，随后固定TRAIN配对，报告身体俯仰角/率、wheel速度/允许box、guide/hard、净空与恢复。不要同时叠五个补丁后靠个别seed报喜。
4. 高度/Roll力MPC与LESO另开地面shadow路线；重新验证模型/采样/驱动和deadline后，才谈C板或达妙板部署。

本次没有新增270mm或实机通过证据。最优先不是把反馈增益再加大，而是**起跳能量/角动量、空中执行器分工、接触模式和落地缓冲的一致设计**。

另一个可借思想是SPR的“先保平衡，再分移动/转向预算”，但[原功率代码](<SPR/source/chassis/Task/chassis_task.c#L1064-L1165>)存在预算差值/零分母保护和右侧字段混用问题，也没有完整signed速度包络。保留我们已有独立六轴功率分配合同及其未绑定校准状态，不用这些3508常数填目标达妙的空缺。

详细逐行来源审阅：[SPR（含active/unused与实现缺口）](<SPR/REPORT.md>) · [Qi-Q26（含PDF页号、LESO及模型歧义）](<QI_Q26/REPORT.md>)。本报告主要结论均有原源码或PDF文字引用；不把作者性能陈述、源码可达和本机动态验收混为一谈。
