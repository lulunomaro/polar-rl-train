# AIR_PITCH_AUTHORITY_V1 — 名义无接触瞬时输入响应，不是控制器

## 范围与计数
- 三existing pose：[crouch](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/JUMP270_V1/GAIN_BANK.json#L7-L16>)、[pushend δ+.2](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/TALL_ROUGH_BANK_V1/gain_delta20.json#L2-L11>)、[landing δ0](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/TALL_ROUGH_BANK_V1/gain_delta0.json#L2-L11>)；rootZ=1m、roll/pitch/yaw0、qvel0、canonical wheelphase0。
- [原预锁方法](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/AIR_PITCH_AUTHORITY_V1/METHOD.json>) / [8小来源SHA](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/AIR_PITCH_AUTHORITY_V1/SOURCE_LOCK.json>) / [明确批准的一次frame修订/13上限](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/AIR_PITCH_AUTHORITY_V1/FRAME_AMENDMENT.json>) / [完整12有效query与9差分，小JSON](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/AIR_PITCH_AUTHORITY_V1/RESPONSES.json>)。
- **累计13次mj_forward=原失败1+有效12，累计2次模型boot；6个integrator入口均0、所有有效query time=0。** 不是无说明地重跑：新crouch/0完整诊断先落盘，原阈值gate通过后才继续其余11。
- 所有有效12 query实际ncon=0；每次新MjData+resetData、同pose qpos字节一致，warmstart/qvel/act/applied forces先全0，没有前一ctrl记忆。原ground/所有geoms/闭链/solver/PD/DR未改；不构造Plant/controller/DR。
- 正常boot加载原279mesh；没有资产重hash或逐query遍历279mesh，没有raw/H5/DR样值/大pitch事件分析、新episode、编译、Git或新agent。

## Actuator、pitch与gyro frame核对
- 原[XML actuator](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mod4v1_usd_source_aligned.xml#L776-L783>)与compiled model核实row6=[LH,LC,LW,RH,RC,RW]，joint transmission、gear=[1,0,0,0,0,0]、fixed gain1/bias0/dynamics-none；实际actuator_force恰等于0/1 ctrl，广义力落在对应编译dof。**+1Nm EACH，一对合计+2Nm，不是总共+1Nm。**
- freejoint dofadr=0；在本identity/零速查询中，root pitch ddot取qacc[4]，与chassis角Jacobian Y及regular-frame angular acceleration相符。root Jacobian误差0，12点角加速度交叉核最大差4.26e-14；gyro为固连imu的site-local量，compiled site/body R均I。零gyro本身并非独立的非零姿态frame实验。
- **关键修正：mjOBJ_BODY/local是惯性主轴i-frame，mjOBJ_XBODY/local才是regular chassis frame。** 安装[API枚举:299–300](<C:/Users/lulu/AppData/Local/Programs/Python/Python314/Lib/site-packages/mujoco/include/mujoco/mujoco/mjtype.h#L299-L300>)有明确语义，[API证据](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/AIR_PITCH_AUTHORITY_V1/FRAME_API_EVIDENCE.json>)保留摘录和SHA。不能把BODY local Y当gyro/chassis Y。
- 新crouch/0诊断：regular XBODY Y=+4.978913861，BODY inertia-local Y=-4.977028786 rad/s²；未变换的差9.955943，经ximat旋回world后吻合。[完整首新诊断](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/AIR_PITCH_AUTHORITY_V1/diagnostics_attempt_02/01_crouch_zero.json>)含全部qacc/Jacobians/body与site实际R、两种object/local-world值和调用阶段。
- 首脚本在1次forward后错误frame断言失败；其数值在断言后才计划写，故**原失败数字仍unknown，不用新基线retrofill**。[原source](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/AIR_PITCH_AUTHORITY_V1/revisions/query_attempt_01/query_authority.py>)、[原失败log](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/AIR_PITCH_AUTHORITY_V1/revisions/query_attempt_01/query_01.log>)、[原错误receipt](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/AIR_PITCH_AUTHORITY_V1/revisions/query_attempt_01/PARTIAL_ERROR.json>)均保留。修订只改frame语义与先落盘后assert，1e−8/1e−14阈值、模型和solver未放宽；RNE前后qacc字节值不变。

## 相对同pose ctrl0的加速度差
下表全部角加速度单位rad/s²；每列输入标量u=各选中motor共同增加1Nm。LH/LC等是实际hip/crank/wheel hinge，不是把passive knee或crank-minus-hip混作编码器角。
| pose | 各选中轴+1Nm | Δroot pitch | ΔLH | ΔLC | ΔLW | ΔRH | ΔRC | ΔRW |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| crouch | 双hip +1 | -3.552214 | +17.261936 | +4.473122 | -1.811667 | +17.250561 | +4.478533 | -1.812182 |
| crouch | 双crank +1 | -3.122724 | +4.477240 | +20.209089 | -5.547857 | +4.474416 | +20.209303 | -5.547622 |
| crouch | 双wheel +1 | -2.188568 | -1.810468 | -5.549230 | +573.749283 | -1.813381 | -5.546249 | +573.748632 |
| pushend δ+.2 | 双hip +1 | -4.265821 | +15.540269 | +2.353841 | -0.036965 | +15.531405 | +2.358813 | -0.038224 |
| pushend δ+.2 | 双crank +1 | -4.300362 | +2.357829 | +18.186387 | -4.882490 | +2.354825 | +18.187631 | -4.882757 |
| pushend δ+.2 | 双wheel +1 | -1.572885 | -0.037009 | -4.883979 | +573.285227 | -0.038180 | -4.881269 | +573.284304 |
| landing δ0 | 双hip +1 | -4.055716 | +15.762848 | +3.135505 | -0.503939 | +15.753215 | +3.140531 | -0.505082 |
| landing δ0 | 双crank +1 | -4.024274 | +3.139619 | +18.269296 | -4.993523 | +3.136417 | +18.270274 | -4.993655 |
| landing δ0 | 双wheel +1 | -1.734124 | -0.503717 | -4.995014 | +573.399233 | -0.505304 | -4.992164 | +573.398311 |

- ctrl0绝对root pitch qacc：crouch=+4.978913861；pushend δ+.2=-1.256180893；landing δ0=-0.039568101 rad/s²。未去掉原重力、气弹簧/被动项、armature或soft equalities，所以零ctrl不等于零加速度；crouch的单个+1通道也不保证抵消其全部baseline。
- **符号结论仅在这些模型torque坐标与姿态下：** 三pose的双hip、双crank和双wheel系数均负。若正pitch误差e需要恢复性负Δpitchddot，且u=k·e，则需a·k<0，故这里**k应为正号**；直接套u=−k·e(k>0)会给同向正Δpitchddot，即局部正反馈。没有选择k幅值、没有实现控制，也未证明position-target/D4链可直接沿用此符号。
- wheel common同样有负root反作用，但每轮自身瞬时Δqacc约573rad/s²/每轴1Nm，且伴随leg耦合；**这不是持续速度/动量/电压/电流/四象限DC权威**。本模型unit ctrl没有完整inverse-PD、processed-target、D4队列及实际motor tracking，不由本表推持续可用torque/速度时长。

## 动力学解释边界与资格
- 位置闭链site残差最大7.33e-13m，mimic joint残差0.0rad；12点都是22条equality、相同type/state，Newton各1 iteration。原soft-equality加速度残差最大0.467132（混合m/s²与rad/s²的诊断max，不是统一物理误差限），未调solref/solver或把qacc重新投影成理想刚性FK导数。
- 全模型动力学广义力方程残差max 4.64e-11（平动/转动混合单位诊断）。这些是固定nominal q/v的+1-vs0局部瞬时前向差；未验证负方向、其他幅度、非零姿态/速度、持续air过程或大pitch事件。objectAcceleration的线性后三项仅原始诊断，不命名完整trueCOMproper。
- 父提供的R60 fresh16仅10/16 local；本12名义query不扩大它，旧8seed7/8也不作为强鲁棒资格。没有新runtime、gain选择、动态稳定/概率证书、operating limit或contact confidence/permission提升。**PH7 pending。**
