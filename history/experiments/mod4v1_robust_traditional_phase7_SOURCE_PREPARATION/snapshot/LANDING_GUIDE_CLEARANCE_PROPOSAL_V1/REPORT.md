# LANDING_GUIDE_CLEARANCE_PROPOSAL_V1 — 名义参考静态几何检查

## 结论与资格
- 在预先指定的**三existing pose × 两reference weight × 五pitch=30点**，guide05相对6cm水平顶面的垂向余量全部为正：**30正、0零、0负**。不追加点找边界，不选择gain，不修改控制。
- 这仅是**level-floor主轮几何支撑、roll/yaw=0、名义FK、理想reference跟踪、canonical wheel_spin=0**的条件结果；不是实际4505 clearance/q、动态稳定、概率证书或新operating limit。其他pitch、roll、wheel phase、其他部件/有限bar的XY关系均不从本表外推。
- [预锁方法](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/LANDING_GUIDE_CLEARANCE_PROPOSAL_V1/METHOD.json>) / [11小来源及原pose](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/LANDING_GUIDE_CLEARANCE_PROPOSAL_V1/SOURCE_LOCK.json>) / [30点小JSON](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/LANDING_GUIDE_CLEARANCE_PROPOSAL_V1/STATIC_GEOMETRY.json>) / [receipt](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/LANDING_GUIDE_CLEARANCE_PROPOSAL_V1/RECEIPT.json>)。

## 已核的实际guide primitive
- Authoritative [XML:747–750](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mod4v1_usd_source_aligned.xml#L747-L750>)及本次compiled model均确认：`guide_wheel_05`是**cylinder**，半径15mm、半长8mm，非sphere/capsule。
- 所属body为`guide_roller_05`，parent是chassis，body offset=[-.259,+.131,-.135]m；geom局部offset0，quat归一化为[.7071067812,.7071067812,0,0]，cylinder局部Z轴映到chassis **-Y**。guide hinge轴为body+Y；本次取0，其圆柱轴对称几何不随该自转改变。
- compiled同一body仅此一个geom，没有同body其他guide可追加。未把其他child body的guide余量或全机避碰当作已查。

## 支持算法与假设
- 仅读取原[crouch q](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/JUMP270_V1/GAIN_BANK.json#L7-L16>)及[原nominal δ−.2](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/nominal_gain_v1.json#L25-L34>)、[δ0](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/TALL_ROUGH_BANK_V1/gain_delta0.json#L2-L11>)、[δ20](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/TALL_ROUGH_BANK_V1/gain_delta20.json#L2-L11>)的joint references；线性weight作用于hip/crank-minus-hip四项，再还原绝对hip/crank，不做DARE/增益拟合。
- 原[continuous-branch FK:21–36](<F:/RMPOLAR-RL/traditional_control_20261101/kinematics.py#L21-L36>)填完整被动链与mimic，沿其公开默认wheel_spin=0。wheel phase是明确的名义补充约定，不声称所有实际轮相位均同此表。
- 一次原XML正常model boot；每点在临时rootZ=1m做一次`mj_forward`，避免无意义的参考高度穿地。随后按同一刚性root-Z平移解析归一到level floor，无第二次forward、无root动力学纠偏。
- 仅缓存两个实际tire的**compiled mesh vertices**，按[helper:94–136](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mesh_support_helper_v1/mesh_support.py#L94-L136>)用geom_xmat/xpos变换一次，取全部轮vertex最低z；`dz=-min(z)`，root支持高度为`1+dz`。**未把.0625滚动半径或.0637 circumradius当vertical高度**，未重复应用mesh PCA/centering。
- 精确圆柱最低点：`zmin = center_z + dz - [r*hypot(R20,R21) + halfLength*abs(R22)]`，R是compiled geom世界旋转，局部Z为轴。**无rboundSphere近似**；当前roll0网格中轴水平，垂向support为15mm。
- 余量=`zmin-.060m`，是相对水平顶面整体最低点的垂向差；未假定bar有限XY overlap。负值若出现也只代表潜在垂向不足，不单独证明碰撞；正值不证明其他部件清杆或可稳定落地。

## 30点余量表（mm，均为正）
weight为crouch→目标reference的线性系数；pitch单位rad，roll/yaw均0。

| 目标reference | weight | -.25 | -.2153 | -.15 | 0 | +.15 |
|---|---:|---:|---:|---:|---:|---:|
| 原nominal δ−.2 | .5 | +9.777 | +17.753 | +33.287 | +67.693 | +100.361 |
| 原nominal δ−.2 | 1 | +33.108 | +41.290 | +57.354 | +92.011 | +124.652 |
| 原δ0 | .5 | +25.664 | +33.721 | +49.583 | +83.904 | +116.385 |
| 原δ0 | 1 | +64.350 | +73.294 | +89.631 | +124.394 | +157.035 |
| 原δ20 | .5 | +41.553 | +50.002 | +65.898 | +100.032 | +132.308 |
| 原δ20 | 1 | +94.998 | +104.117 | +120.684 | +156.144 | +188.232 |

- 最小查询点为原nominal/weight.5/pitch−.25，guide最低z=69.777mm，余量+9.777mm；这不是连续pitch安全区间或新阈值。
- 在pitch−.2153，三个weight.5点的root几何支撑高度分别279.969/295.937/312.218mm；它们来自各自理想q与轮mesh，并非4505实测root高或真实active q。

## 一次执行与封存
- 1次模型boot，nq37/nv36/nbody32/ngeom312/nmesh279；正常boot可加载原资产，但没有另做279资产hash或逐点遍历279mesh，计算对象仅两轮cache和guide05 primitive。未读raw/H5/DR样值或R56源码。
- **30个静态查询、30次mj_forward、6个integrator入口调用均0、time始终0。** 未调用step/step1/step2/Euler/RK/implicit，未构造Plant/controller/DR、未运行新episode或旧QA。
- 数值一致性：两轮归一支撑残差最大2.22e−16m；闭链site残差最大7.33e−13m；compiled primitive与body-offset公式差最大5.55e−17m；reference active-q设置误差0。支撑残差检查只是浮点一致性，不是机械容差/operating limit。
- **本任务PH7 pending**。没有从正余量选择gain/加控制/提高contact confidence；实际4505的q、roll、支撑/轮相位/动态与跟踪状态不被reference替代。本表不撤销既有guide3失败，也不修改父R56候选源码。
