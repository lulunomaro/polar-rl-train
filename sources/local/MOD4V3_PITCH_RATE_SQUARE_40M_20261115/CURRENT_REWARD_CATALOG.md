# 当前奖励函数完整清单（2026-11-15，瞬时俯仰平方修复轮）

对应 `MOD4V3_PITCH_RATE_SQUARE_40M_20261115` 实际 `rough_scut_v1` 配置。以实际 STARTUP.json 的51个权重、冻结SCUT公式、MOD4适配和两个环境附加奖励为准。只整理记录本轮已运行配方。

基础51项配置中34项非零权重，其中3项当前实际为零：2项空中关节限位适配返回零，1项驻停防漂移的开关关闭；其余31项按状态和条件产生贡献。另有5项自定义台阶奖励/成本、2项俯仰专项成本。

每个策略步 `dt=0.02s`：

`r_env = dt * sum(w_i * f_i_after_state_scales) + r_continuous_stair + r_pitch_specialist`

下表基础/空中奖励公式已计入各自权重，尚需乘dt。台阶事件/有限进展奖励直接相加，只有时间成本已含dt；俯仰专项公式单独含dt。基础总奖励没有“只保留正值”截断。数值保护环境的基础奖励清零；新台阶/俯仰项排除已终止环境。

## 统一符号

- `C_a(x)=clip(x,-a,a)`；`S(x)=clip(x,0,1)`。
- `e_v = cmd_vx - root_lin_vel_b.x*cos(pitch)`：当前前进速度奖励使用该水平投影，尽管键名含xy，实际追踪的是前向速度。
- `e_w = cmd_wz - root_ang_vel_b.z`。
- `e_h = height_reward_reference - height_reward_target`。普通状态为机身相对地面高度；连续台阶地面参考取两驱动轮中心竖直射线地面高度的较小值。
- `g_x/g_y` 是机体系归一化重力投影的前向/侧向分量。
- `A=2*exp(-cmd_vx^2/3)+2`。
- `qdot_leg`为4个主动腿电机；`qdot_wheel`为2个轮电机；`tau`为6个主动电机实际力矩。
- `D a = a_t-a_(t-1)`，`D2 a = a_t-2a_(t-1)+a_(t-2)`；动作项使用原始6维策略动作历史。
- `delta_x=x_left_wheel_b-x_right_wheel_b`：左右轮沿机身x轴的前后错位。

## 1. 速度、转向和高度（6项）

| 函数键 | 配置权重 | 实际加权函数，未乘dt | 作用 |
|---|---:|---|---|
| `track_lin_vel_xy` | +1.2 | `+1.2*exp(-C_1(e_v)^2/0.5)` | 前进/后退速度指数追踪 |
| `track_lin_vel_xy_square` | -1.5 | `-1.5*e_v^2` | 超速和欠速对称平方惩罚，无1m/s误差截断 |
| `track_ang_vel_z` | +1.0 | `+exp(-C_0.8(e_w)^2/0.25)` | 偏航角速度追踪 |
| `track_ang_vel_z_square` | -0.1 | `-0.1*(0.5*e_w)^2 = -0.025*e_w^2` | 转得过快/过慢的平方误差 |
| `track_height_exp_tight` | +1.0 | `+exp(-C_0.15(e_h)^2/0.001)` | 接近目标高度的正奖 |
| `track_height_square` | -1.0 | `-(10*e_h)^2 = -100*e_h^2` | 原始高度误差平方成本，无0.15m误差截断 |

当前速度追踪的高度/姿态门控均关闭。指数速度项会在误差绝对值1m/s之后饱和，速度平方项仍对原始误差继续增加。高度平方项在airborne状态被乘0，见第5节。

## 2. 机身姿态、晃动与左右轮错位（8项）

| 函数键 | 配置权重 | 实际加权函数，未乘dt | 作用 |
|---|---:|---|---|
| `flat_orientation_y_v` | -2.0 | `-2*(A*g_x)^2` | 随速度指令调整强度的俯仰姿态成本 |
| `flat_orientation_y_exp` | +1.0 | `+exp(-g_x^2/0.02)` | 俯仰接近水平的正奖 |
| `flat_orientation_x_v` | -2.0 | `-2*(A*g_y)^2` | 随速度指令调整强度的横滚姿态成本 |
| `flat_orientation_x_exp` | +1.0 | `+exp(-g_y^2/0.01)` | 横滚接近水平的正奖 |
| `ang_vel_xy` | -0.05 | `-0.05*(omega_x^2+omega_y^2)` | 全任务的滚转/俯仰角速度平方成本 |
| `lin_vel_z` | -0.5 | `-0.5*(root_lin_vel_b.z)^2` | 机体系竖直速度成本 |
| `no_fork` | -1.0 | `-I(abs(delta_x)>0.05m)` | 左右轮前后错位超过5cm的成本 |
| `no_fork_square` | -1.0 | `-(5*delta_x)^2 = -25*delta_x^2` | 前后错位的连续平方成本 |

名称`_v`表示随速度指令调整姿态权重；真正的角速度项为`ang_vel_xy`以及本轮的专项`omega_y^2`。

## 3. 电机能耗与动作平滑（9项）

| 函数键 | 配置权重 | 实际加权函数，未乘dt | 作用 |
|---|---:|---|---|
| `leg_joint_acc` | -5e-7 | `-5e-7*sum(qddot_leg^2)` | 腿电机加速度成本 |
| `leg_joint_vel` | -0.005 | `-0.005*sum(qdot_leg^2)` | 腿电机转速成本 |
| `joint_torque` | -1e-4 | `-1e-4*sum(tau_active6^2)` | 6个主动电机力矩成本 |
| `wheel_acc` | -1e-8 | `-1e-8*sum(qddot_wheel^2)` | 轮电机加速度成本 |
| `wheel_vel` | -1e-5 | `-1e-5*sum(qdot_wheel^2)` | 轮电机转速成本 |
| `wheel_power` | -1e-4 | `-1e-4*sum(max(tau_wheel*qdot_wheel,0))` | 仅正机械功率成本 |
| `action_rate` | -0.05 | `-0.05*sum((D a_active6)^2)` | 六维动作一阶变化成本 |
| `action_smoothness_leg` | -0.1 | `-0.1*sum((D2 a_leg4)^2)` | 腿动作二阶差分成本 |
| `action_smoothness_wheel` | -0.03 | `-0.03*sum((D2 a_wheel2)^2)` | 轮动作二阶差分成本 |

## 4. 接触与失败（2项）

| 函数键 | 配置权重 | 实际加权函数，未乘dt | 作用 |
|---|---:|---|---|
| `undesired_contact` | -2.0 | `-2*I(any harmful body historical contact force >3N)` | 机身、结构件、导轮等有害组的二值接触成本 |
| `termination` | -200.0 | `-200*I(reset_terminated)` | 非超时失败终止成本，普通每次约-4 |

台阶导轮接触的终止豁免改的是终止接触选择，基础`undesired_contact`仍按自身有害组与3N阈值计罚。闭链2mm等保护是单环境终止条件，由终止项参与；numerical保护环境基础奖励清零。

## 5. 空中与落地（6项可贡献 + 2项适配为零）

内部Airborne状态机开启；主动起跳状态机、通用旧stair状态机和通用前向扫描状态机关闭。以下状态项只在各自airborne/接触计时窗口生效。

| 函数键 | 配置权重 | 当前实际加权函数，未乘dt | 条件/作用 |
|---|---:|---|---|
| `airborne_landing_down_vel` | -1.0 | `-2*max(-vz_world,0)^2` | 轮接触计时达到20ms后，抑制机身继续向下撞 |
| `airborne_wheel_heading_x_centering` | +10.0 | `+10*mean(exp(-wheel_x_heading^2/0.02))` | 空中早期轮/底盘接触计时<20ms，且双轮heading-z<-0.1m；鼓励轮子前后居中 |
| `airborne_air_wheel_zero_torque_exp` | +20.0 | `+20*exp(-(max(abs(tau_wheel))/1.5)^2)` | 任一轮接触计时达到20ms前，鼓励小轮力矩 |
| `airborne_precontact_wheel_directional_speed` | +10.0 | `+10*s` | `s=min_i S(direction*qdot_wheel_i/10)`；指令和机身前向速度同向且绝对值均>1m/s，接触计时<20ms |
| `airborne_precontact_wheel_directional_speed_shortfall` | -10.0 | `-10*(1-s)` | 同样方向/速度门控；接触计时已开始且<50ms，抑制轮速不足 |
| `airborne_landing_wheel_max_contact_force` | -10.0 | `-10*S((max_i norm(F_wheel_i)-200N)/200N)` | 接触开始20ms后且轮接触>1N；200N起罚，400N满罚 |
| `airborne_joint_pos_limits` | -10.0 | **0** | MOD4适配`motor_stop_terms()`返回零 |
| `airborne_joint_pos_limits_vel_reg` | -100.0 | **0** | 同上，当前没有实际贡献 |

Airborne状态还会修改已有基础项：

| 基础项 | 状态倍率 | 实际系数变化 |
|---|---:|---|
| `undesired_contact` | x25 | -2 -> -50 |
| `termination` | x6 | -200 -> -1200 |
| `lin_vel_z` | x2 | -0.5 -> -1.0 |
| `flat_orientation_y_v` | x0 | 当前这一负姿态项暂停 |
| `track_height_square` | x0 | 高度平方成本暂停 |

空中高度指数奖励仍存在。其高度参考改为`root_z-max(wheel_center_z)+0.0625m`；目标改为`min(height_cmd+0.12m,0.36m)`。目标高度上限是此状态奖励内部参考，不是机身可达高度上限。落地轨迹参考功能当前关闭。

## 6. 连续200mm两级台阶的自定义附加项（5项）

仅上行台阶环境，回合>=3s且未终止时启用；下阶和其他科目不获得这些登阶事件分。

| 项目 | 每步实际贡献 | 条件 |
|---|---|---|
| 抬轮并收腿的有限进展 | `+0.6*mean(max(score-best_score,0))` | 接近当前上沿0.45m内；`score_i=S((wheel_z_i-(lower_tread_z+0.0625))/.2)*S((leg_length_ref_i-leg_length_i)/.08)`，只付超过本阶历史最好部分 |
| 首次双轮落上第一级 | `+0.5`一次 | 双轮实际台面支持力>5N，位置与高度同时满足 |
| 首次双轮落上第二级 | `+0.5`一次 | 同上，针对第二台面 |
| 顶部保持完成 | `+2.0`一次 | 双轮上第二台面并连续保持0.3s |
| 两阶之间耗时 | `-0.15*dt = -0.003/策略步` | 已上第一级、尚未完成第二级 |

旧“向台阶中心新增前进距离”项当前贡献**0**。代码仍计算advance用于历史/诊断，但未加进最终奖励；没有旧的`+0.8/新增1m`。当前也没有单独按“腿向后摆多少”直接发分的项，收腿项和实际抬轮进展绑定。

## 7. 本轮俯仰启停专项（2项）

仅615专项：359难度9随机起伏+256平地。首次真实轮接触>5N后锁存到本回合结束，短暂卸载继续计罚，reset清除；age>=1s，已终止环境排除。819台阶与其他非专项不追加这两项，基础姿态/角速度奖励仍然存在。

- 真实机身俯仰角度成本：`-dt*30*max(abs(pitch)-5deg,0)^2`。
- 真实机身y轴角速度平方成本：`-dt*3.5*omega_y^2`。

pitch由机身归一化重力投影`atan2(g_x,norm(g_yz))`求出。角度采用rad，角速度rad/s；5deg仅是该附加角度项的允许区。角速度翻倍，这个平方成本变成4倍。与基础`ang_vel_xy`叠加后，专项活跃时俯仰方向总角速度平方系数为`-3.55`（均乘dt），横滚仍为基础`-0.05`。

## 8. 权重为0的17项

以下当前没有奖励贡献：

```text
leg_joint_pair_pos_diff
wheel_air_spin
flat_orientation_y
flat_orientation_x
track_lin_vel_xy_tight
stand_still
track_height_exp
track_height_exp_soft
track_height_exp_both_wheels_contact
no_fork_exp
no_fork_z_exp
rear2_rear1_joint_pos_limits
rear2_rear1_joint_pos_limits_torque
rear2_rear1_joint_pos_limits_vel
pen_theta_no0
stand32_heading
stand32_wheel_distance
```

另外`stand_still_lin_vel`配置权重-2，但`stand_still_deadzone_enabled=False`使它的mask恒0，当前实际贡献**0**。配置的threshold=0.1在该开关关闭时不生效。零速度命令仍接受通用速度指数/平方追踪。速度误差三次方、旧wrong_direction_vel/speed_preserve_abs以及若干只存在于airborne_cfg但没有最终rewards权重的addition，均未进入本轮奖励和。

## 9. 同时优化的教师辅助损失

这是PPO loss附加项，和环境reward分别记录：

`L_aux = 1.0*L_keep + 0.25*L_high_stance`

`L_keep=mean(sum6((clip(student_action)-clip(frozen_db6_action))^2))`，来自1433非专项（含全部819台阶）。615专项不进入这个在线keep样本集。高站姿项用四个腿动作MSE：固定anchor；有合格在线高姿态样本时取anchor与live的等权平均，再乘0.25。旧快速台阶教师模仿系数0，旧后摆参考模仿系数0。

当前没有额外成功回放奖励；超时结束时PPO的`gamma*V(terminal)` bootstrap是回报估计，不是额外任务奖励。

## 源码依据

- `evidence/training/STARTUP.json`：本轮实际权重/时序。
- `support/mod4v3_ppo_v1/scut_flat_rewards.py`、`scut_flat_forward_square_env.py`、`scut_rough_r2_env.py`、`scut_rough_scut_v1_env.py`：当前配置工厂；只执行纯配置函数重建后，51个权重与STARTUP逐项匹配。
- 冻结SCUT base_env SHA256 `9959c7fae6eff8591d655a18c29986f2c184c13f4905361b6c722efefbad12bc`：基础奖励函数。
- 冻结SCUT airborne SHA256 `12dc18fa8237253872b81d7e2da8f84c63e2c7bcef17868ff397a67811fb3f5b`：空中奖励/状态倍率。
- `support/mod4v3_ppo_v1/continuous_stair_env.py`：5项自定义台阶奖励。
- `support/mod4v3_ppo_v1/pitch_stability_env.py`、`pitch_stability_math.py`：两项俯仰成本及门控。
- `support/mod4v3_ppo_v1/teacher_retention.py`：教师辅助损失。
