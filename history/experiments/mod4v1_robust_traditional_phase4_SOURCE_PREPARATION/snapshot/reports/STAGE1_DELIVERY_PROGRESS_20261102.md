# MOD4v1 传统控制保底 — 阶段性交付 V1

**交付性质：平台无关控制源码、host验证与仿真基线；尚非可刷固件或整车最终验收。Goal持续推进。** 本报告对应2026-11-02用户询问进度时的稳定cutoff；仍在实验中的版本不混入已封存baseline。

## 一、实际进度

|能力/模块|目前证据|当前判定|
|---|---|---|
|最新MOD4v1全模型/接触/闭链/D0–D7|原模型SHA、311 geoms/31 bodies，0.5ms physics/10ms control，原执行器PD/延迟/增益/signed DC链保持|基线已核定；本阶段未删碰撞或弱化随机化|
|实际C估计器+P25，20s站立|H4独立64个全DR：60/64过现有门槛，64/64完整|4个位置漂移失败保留，未宣称全过|
|实际C闭环，2m/s前进12s|H4另64个全DR：速度/姿态/支撑原门槛64/64；实际均速1.87515–2.00844m/s|**不是直线车道毕业**：52/64的世界横向峰值超过0.3m；该项不是原H4速度门槛|
|航向保持改进|新Python TRAIN配对5案，车道门槛从baseline1/5改善到候选4/5|未移植到冻结H4 C profile，未新holdout，不抹去剩余误差|
|持续4πrad/s原地自转|H2独立64案角速度/姿态长时保持64/64；加入漂移/vRMS的综合门槛56/64|持续自转已有证据，启停/换向尚未鲁棒毕业|
|MPC求解核＋原生C监督|ASQP实际H15 cold/warm各18/18、stress各75/75；新C监督3717固定输入、84531检查/0失败，45时钟插点通过|**内核与监督合同已交付**；真实非收敛334次均回退，不是完整机器人MPC/3ms目标板资格|
|接触/异常/保护FSM原生C|61context/1042步，46087 replay检查0差异、native1993/0、C++调用通过|**核心交付**；可信触地和动作绑定仍unknown/unbound|
|真实RM-derived粗糙几何|确切SCUT tiny_step家族2–6cm/有限9×9m；2cm名义有通过，4–6cm未鲁棒通过|不是完整11家族/CAD场地毕业|
|粗糙地形失效因果|高腿几何确实抬高；35–43°pitch造成约7–12cm竖直投影损失，BODY腿drop反而更长|不是“腿没伸长”或“静态必然撞底”；转向主动姿态/腿策略|
|新主动小跳R39|四个新名义flat profile全完整；按预先80mm净空/无导向轮与硬接触/末端稳定2s筛选3/4过；失败案有19个导向轮接触physics样本|仅名义手动timer机理试验，**不是4–6cm粗糙地形或全DR资格**|
|270mm跳阶/落台|有TRAIN越障/恢复轨迹，严格2k审计暴露guide/riser辅助、冲击与DR失败|持续攻关，不作为本阶段可用技能交付|
|2k传感器/COM窗口|新R38六case，48020采集合同检查0失败；后续窗口模块13/13合成测试及六case sensor-only shadow已封存|新增信息shadow；连续时间误差未绑定，全部trusted cue仍UNKNOWN|
|主控/板级/功率/HIL|M4/M7已有真实编译对象；板型、CAN、电机标定、IMU、母线/热模型尚待绑定|没有BSP固件/BIN、刷写、目标运行或WCET结论|

所有上述通过率均按各自已冻结的门槛报告，不合并成“整车成功率”。H4前进64/64的95%Wilson下界约0.9434，也不是95%可靠率已证实。

## 二、阶段包里有什么

### 已封存源码与合同

1. [C3估计器/P25/独立输出gate](<../SPR_AUDIT/portable_control_v3_current/README.md>)：V4杆臂、vector gate、Joseph KF、P25实际矩阵、指令整形、row映射、期限/失效锁存；6509单测/0失败。
2. [C2 FK依赖](<../SPR_AUDIT/portable_core_v2_kinematics/ct_kinematics.h>)：纯几何/轮里程数学，C3直接依赖，不用旧R00 observer冒充V4。
3. [P25 host adapter](<../SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1/README.md>)：已有可运行本机程序/SDK及41632检查/0失败；用于实际C控制物理路径，非CAN或板固件。
4. [ASQP V3](<../SPR_AUDIT/ACTIVE_BOX_QP_V3/README.md>)：固定workspace、严格KKT与可中断内核；所有原非收敛/低预算失败记录保持。
5. [原生C FSM](<../SPR_AUDIT/portable_fsm_detector_v1/README.md>)：可带走的6件C99源码闭包及M4/M7对象；binary64相对秒，软件double/libm依赖和目标时序仍待绑定。默认jump/recovery/auto-obstacle disabled，force门槛0.8未动。
6. [H2自转数学C移植](<../SPR_AUDIT/portable_spin_h2_v1/README.md>)：冻结nominal-K/τ20反馈数学与数值证明，**不是带发送资格的整机H2闭环**。
7. [原生C MPC监督](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/README.md>)：直接in-process链接ASQP、独立C3回退、双重KKT复核、最终deadline检查后才提交warm；3717软件输入/84531检查0失败，M4/M7新对象4/4。其valid不是执行许可，跳跃/预测腾空/非normal或接触许可未绑定时需显式disabled。

### 基线、报告与接线边界

- [H4独立物理事实](<R34_C_H4_INDEPENDENT_FACTS.json>)、[H4冻结协议](<../C_P25_SPEC625_H4_V1/PROTOCOL.json>)。
- [航向保持TRAIN事实](<R36_HEADING_TRAIN_FACTS.md>)、[R39小跳批次](<../batches/r39_minihop4/BATCH_RESULT.json>)。
- [粗糙姿态因果分析](<../ROUGH_POSTURE_CAUSAL_V1/README.md>)。
- [主控/电机/IMU/功率绑定表](<../HARDWARE_BINDING_CHECKLIST.md>)、[state14语义勘误](<STATE14_SCHEMA_ERRATUM.md>)。

包内MANIFEST逐项列出实际文件与SHA；部分旧INDEX/README保留历史源路径。**包不是全部历史仓库镜像，也不携带巨型模型mesh、机器人raw trace或用户原ZIP资产**；重跑物理仿真仍需原已核定模型资产与环境。可移植C核心/接口/依赖与主要验证材料已随包。

## 三、正在做，但不冒成已交付

- 新原生C MPC supervisor与2k COM窗口在本报告整理期间已完成最终seal，经父级读取VALIDATION核对后纳入稳定cutoff。MPC真实分支为1510接受、1676模型域回退、334非收敛回退、195空交集、1无效、1disabled；不是机器人3717次成功，板上deadline仍未验证。
- 新2k COM窗口仅sensor-only路径，不读DR/GT；cap.50/冻结trusted.60不提高，无新可信触地许可。
- 新world-leg IMU pitch反旋参考已写成独立实验代码，**尚未执行物理实验**。R39小跳也尚未全DR或真实粗糙地形验证。
- 原ASQP production stdio组件仍独立记录为BLOCKED_NOT_SEALED；本包不放入该草稿，不修改防护设置或拿其INDEX冒作运行资格。

## 四、当前工程建议

**现在适合：**代码审查、host接口联调、控制/数学单元测试、板级接口清单对接和后续HIL准备。

**尚未到：**直接刷写并把整套系统当作已验证的比赛最终防线。接下来优先把主动腿/姿态策略放回4–6cm全接触全DR、严格落地审计与停转换向，再完成整周期MPC与板上HIL/功率保护。

## 五、归档

PH3已推送独立分支`mod4v1-lqr-mpc-robust`，commit`fa6838807f4d69d2b8ac52300d74ad40f365d2ed`，tag`trial-20261102-mod4v1-robust-traditional-phase3`；截止R34。后续新模块/实验/失败及本阶段包明确PH4pending，下一稳定cutoff按原策略一起归档，不覆盖原RL工程。
