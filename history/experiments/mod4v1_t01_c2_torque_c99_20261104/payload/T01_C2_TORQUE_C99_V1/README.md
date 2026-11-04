# 当前T01 C2：C99请求力矩数学后端

这是所选nominal C2算法的力矩生成实现，不是新控制候选、机器人通过证书或整机固件。原T01严格承载门仍失败，3/3物理机制计数不变；本轮物理步为0，试玩和V3观看入口未动。

## 已迁移的实际控制顺序

1. [PC2参考模块](<../T01_C2_REFERENCE_C99_V1/pc2_reference.h>)生成左右腿参考和可选航向外环。heading=1用于原始yaw-rate指令，heading=0用于FPS已纠偏的yaw-rate，避免双航向环。
2. 低速park积分独立于里程计；静止时按原2s时间常数泄漏，不重置估计器。
3. 原coord_soft加速度0.6、jerk2、yaw加速度2的命令整形与原轮速包络投影。
4. 复用冻结P25矩阵与[CTK 6×14 LQR](<../SPR_AUDIT/portable_core_v2_kinematics/ct_kinematics.c>)；对称化sagittal腿状态，保留共同机身俯仰/俯仰率反馈，未用固定腿PD覆盖它。
5. 原yaw PI/积分限幅/前馈/加速度前馈与可用轮力矩防积分饱和；第一次全轴限幅。
6. 仅叠加左右差分PD120/4，第二次限幅。此两次限幅的先后次序按原Python保留。
7. 复用[PC3行映射](<../SPR_AUDIT/portable_control_v3_current/pc3_controller.c>)，输出LH/LC/LW/RH/RC/RW和wheel-first排列。

[实现](<pc2_balance.c>)直接复用旧FK/LQR和数据；[接口](<pc2_balance.h>)由调用者持有状态，无显式heap、MuJoCo、OS或CAN调用。不是旧pc3_p25_step的别名；那个后端的腿行覆盖/整形/积分语义不同。

## 调用边界

- 先pc2_balance_init，再固定100Hz调用pc2_balance_step。输入是已有pc3_estimate，检查valid、sampled/estimated/now一致性、age<=50ms、有限性及参考模块的姿态/机构域。
- 返回pc3_control_result中的力矩是**外环requested load-side Nm**，不是2kHz实际扭矩、电流、PVT报文或物理停机。必须同时检查返回码和valid；NULL/alias前提错误不改调用者对象，不能只检查旧valid。
- 普通检测错误锁存，重新init才能清除；调用者仍须进入原driver disable/故障处理，不要把请求0当作真实失能或停转。
- 结果布局相同不代表pc3_cycle能直接接此新状态类型；现有cycle、BSP、arming、功率分配、PD目标反解、D4和有符号DC链尚未接入本后端。原执行链必须在外部保留，勿在本后端里额外重复DC裁剪。
- 只含当前固定nominal P25工作点；不是腿长/支持模式全域调度、接触识别、自救、飞行MPC、全DR或硬实时资格。

## 一次实际新组件验证

[预声明协议](<validation001/protocol.json>) / [结果](<validation001/result.json>) / [验证器](<verify_torque.py>)。

GCC C99 -O2 -Wall -Wextra -Werror -fno-fast-math：编译exit0，原生执行exit0。

- 2300个**新合成数学输入**，覆盖慢速指令、停车积分、前进/刹车/反向、关闭内部航向时的高命令数值压力；不是动力学轨迹或实际FPS操纵。
- 15种故障触发＋15次锁存复核＋alias/NULL/未初始化3项，共33条原生断言通过。
- 相对原Python C1/C2，六轴力矩最大绝对差 **8.8702421e-5 Nm**（预声明门2e-3）；无无效普通行、无力矩界限超差。
- ref14与投影后v/w/整形a逐元素最大差3.54679e-5；ref14含不同SI单位，不是单一姿态误差或机器人跟踪误差。yaw积分最大差3.87453e-6，park最大差3.05268e-8m。
- 1040行触发请求限幅，386行触发速度包络，证实这两条数学分支有覆盖；不代表真实2kHz裁剪占空比。
- host状态192B。原生整批0.493328s含进程启动、ASCII输入输出和故障断言，不是单步WCET或ARM时限。

未跑旧case/holdout或新机器人物理，没有更改冻结模型/K/协议/gate/失败结果。ARM编译、完整cycle接线、BSP/HIL和实机标定仍分别缺证据。
