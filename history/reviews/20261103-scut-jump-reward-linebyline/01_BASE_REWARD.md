# 总奖励计算逐行注释

这里保留_get_rewards整个函数，以及它直接调用的后处理入口；未启用的原始项也解释，并标明权重决定最终是否参与。公开模型参数见00_CONFIG。源码当前提交与七月训练时源码没有逐文件绑定证明。

默认身体高度=root世界z减raycast估计地面高度，后者是有效扫描命中z均值，详见原env.py L5669–5693。台沿附近扫描同时覆盖上下台面时，该均值不等于某一真实支撑点高度。

### 完整_get_rewards及基础后处理入口

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py`，L3474–L4067。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def _get_rewards(self) -> torch.Tensor:  # 原L3474：每个控制step生成每环境总奖励的入口。
        self._update_ground_height_estimate()  # 原L3475：更新/复用本拍raycast地面高度估计，供相对高度使用。
        # prepare  [原L3476：原作者注释，不执行]
        root_quat_inv, wheel_pos_b, wheel_pos_heading_b, wheel_lin_vel_b, wheel_lin_vel_heading_b = (  # 原L3477：取得身体/heading相对轮位置与轮速度；不要混作世界台阶落点。
            self._get_root_quat_inv_and_wheel_pos_b()  # 原L3478：取得身体/heading相对轮位置与轮速度；不要混作世界台阶落点。
        )  # 原L3479：取得身体/heading相对轮位置与轮速度；不要混作世界台阶落点。
        left_leg_length = torch.norm(wheel_pos_heading_b[:,0],dim=-1)  # 原L3480：左右腿长度是各自根到轮heading平面投影向量范数，辅助函数把y置0。
        right_leg_length = torch.norm(wheel_pos_heading_b[:,1],dim=-1)  # 原L3481：左右腿长度是各自根到轮heading平面投影向量范数，辅助函数把y置0。
        left_leg_angle = torch.atan2(-wheel_pos_heading_b[:,0,0],-wheel_pos_heading_b[:,0,2])  # 原L3482：按heading轮x/z算腿角，前后方向取负号约定。
        right_leg_angle = torch.atan2(-wheel_pos_heading_b[:,1,0],-wheel_pos_heading_b[:,1,2])  # 原L3483：按heading轮x/z算腿角，前后方向取负号约定。
        left_wheel_pos_b_normal = wheel_pos_heading_b[:,0]/left_leg_length.unsqueeze(-1)  # 原L3484：腿向量除长度得到单位方向。
        right_wheel_pos_b_normal = wheel_pos_heading_b[:,1]/right_leg_length.unsqueeze(-1)  # 原L3485：腿向量除长度得到单位方向。
        left_leg_length_dot = torch.sum(wheel_lin_vel_heading_b[:,0]*left_wheel_pos_b_normal,dim=-1)  # 原L3486：轮相对速度点乘腿单位向量，得到各腿伸缩速度。
        right_leg_length_dot = torch.sum(wheel_lin_vel_heading_b[:,1]*right_wheel_pos_b_normal,dim=-1)  # 原L3487：轮相对速度点乘腿单位向量，得到各腿伸缩速度。
        # leg_ang_vel = self.joint_vel[:,self._front1_joint_idx] - self.joint_vel[:,self._rear1_joint_idx]  [原L3488：原作者注释，不执行]

        wheel_power = self.robot.data.applied_torque[:,self._wheel_idx]*self.joint_vel[:,self._wheel_idx]  # 原L3490：每轮实际扭矩乘轮角速度，得到机械功率。
        comsume_wheel_power = torch.clamp(wheel_power,min=0)  # 原L3491：只取正功率，不给再生制动抵消消耗。

        # both_height_cmd = self.height_cmd.unsqueeze(-1).repeat((1,2))  [原L3493：原作者注释，不执行]
        # deviation_joints = self._inverse_kinematics(both_height_cmd,torch.zeros_like(both_height_cmd,dtype=torch.float,device=self.device)).transpose(-2,-1).reshape(self.num_envs,-1)[:,:len(self._deviation_joint_idx)]  [原L3494：原作者注释，不执行]

        # 起身训练：整个落地+起身阶段速度命令和角速度命令强制为0（reward 计算用）  [原L3496：原作者注释，不执行]
        # if getattr(self.cfg, 'enable_standup_training', False):  [原L3497：原作者注释，不执行]
        #     in_standup_phase = (self._standup_phase == 0) | (self._standup_phase == 1)  [原L3498：原作者注释，不执行]
        #     self.command[in_standup_phase, :3] = 0.0  [原L3499：原作者注释，不执行]

        # alive  [原L3501：原作者注释，不执行]
        rew_termination = self.reset_terminated  # 原L3502：真实reset_terminated布尔值作为原始终止代价；最后乘负权重。
        rew_epi_len = self.episode_length_buf  # 原L3503：episode已走步数，可作为可选原始项；公开权重表没启用它。

        # regularization  [原L3505：原作者注释，不执行]
        joint_acc = self.robot.data.joint_acc  # 原L3506：取SDK报告的实际关节加速度。
        rew_joint_acc = torch.sum(torch.square(joint_acc[:,self._actuate_idx]), dim=1)  # 原L3507：全部驱动关节加速度平方和。
        rew_leg_joint_acc = torch.sum(torch.square(joint_acc[:,self._legs_act_idx]), dim=1)  # 原L3508：腿驱动关节加速度平方和，公开模型启用。
        rew_leg_joint_com_acc = torch.sum(torch.square(0.5*(joint_acc[:,self._legs_front_idx]+joint_acc[:,self._legs_rear_idx])), dim=1)  # 原L3509：同侧前后腿关节加速度均值再平方的共同分量项。
        rew_leg_joint_diff_acc = torch.sum(torch.square(0.5*(joint_acc[:,self._legs_front_idx]-joint_acc[:,self._legs_rear_idx])), dim=1)  # 原L3510：前后差的一半再平方的差动分量项。
        rew_wheel_acc = torch.sum(torch.square(joint_acc[:,self._wheel_idx]), dim=1)  # 原L3511：左右轮角加速度平方和。
        rew_wheel_com_acc = torch.square(0.5*(joint_acc[:,self._wheel_idx[0]]+joint_acc[:,self._wheel_idx[1]]))  # 原L3512：两轮平均角加速度平方。
        rew_wheel_diff_acc = torch.square(0.5*(joint_acc[:,self._wheel_idx[0]]-joint_acc[:,self._wheel_idx[1]]))  # 原L3513：两轮差动角加速度平方。
        rew_joint_vel = torch.sum(torch.square(self.joint_vel[:,self._actuate_idx]), dim=1)  # 原L3514：所有驱动关节角速度平方和。
        rew_leg_joint_vel = torch.sum(torch.square(self.joint_vel[:,self._legs_act_idx]), dim=1)  # 原L3515：腿关节角速度平方和，公开模型启用。
        rew_leg_joint_com_vel = torch.sum(torch.square(0.5*(self.joint_vel[:,self._legs_front_idx]+self.joint_vel[:,self._legs_rear_idx])), dim=1)  # 原L3516：前后腿共同角速度分量平方和。
        rew_leg_joint_diff_vel = torch.sum(torch.square(0.5*(self.joint_vel[:,self._legs_front_idx]-self.joint_vel[:,self._legs_rear_idx])), dim=1)  # 原L3517：前后腿差动角速度分量平方和。
        left_leg_pair_idx, right_leg_pair_idx = self._left_right_leg_joint_pair_idx  # 原L3518：取左右腿相对应的关节索引。
        if left_leg_pair_idx and right_leg_pair_idx:  # 原L3519：两侧配对索引都有效。
            leg_pair_pos_diff = wrap_to_pi(self.joint_pos[:, left_leg_pair_idx] - self.joint_pos[:, right_leg_pair_idx])  # 原L3520：左右配对实际角差wrap到[-pi,pi]。
            rew_leg_joint_pair_pos_diff = torch.sum(torch.square(leg_pair_pos_diff), dim=-1)  # 原L3521：配对角差平方和。
        else:  # 原L3522：缺索引的回退分支。
            rew_leg_joint_pair_pos_diff = torch.zeros(self.num_envs, dtype=torch.float, device=self.device)  # 原L3523：该项0。
        rew_wheel_vel = torch.sum(torch.square(self.joint_vel[:,self._wheel_idx]), dim=-1)  # 原L3524：两轮实际角速度平方和。
        rew_wheel_com_vel = torch.square(0.5*(self.joint_vel[:,self._wheel_idx[0]]+self.joint_vel[:,self._wheel_idx[1]]))  # 原L3525：两轮平均角速度平方。
        rew_wheel_diff_vel = torch.square(0.5*(self.joint_vel[:,self._wheel_idx[0]]-self.joint_vel[:,self._wheel_idx[1]]))  # 原L3526：两轮差动角速度平方。
        applied_torque = self.robot.data.applied_torque  # 原L3527：读取实际施加扭矩。
        rew_joint_torque = torch.sum(torch.square(applied_torque[:,self._actuate_idx]), dim=1)  # 原L3528：全部驱动关节扭矩平方和，腿和轮均在_actuate_idx中时均计入。
        torque_rate = applied_torque - self._previous_applied_torque  # 原L3529：本拍减上一拍扭矩的一阶差，不除dt。
        torque_second_diff = (  # 原L3530：本拍-2×上一拍+上上拍扭矩，二阶离散差分，不除dt²。
            applied_torque  # 原L3531：本拍-2×上一拍+上上拍扭矩，二阶离散差分，不除dt²。
            - 2.0 * self._previous_applied_torque  # 原L3532：本拍-2×上一拍+上上拍扭矩，二阶离散差分，不除dt²。
            + self._before_previous_applied_torque  # 原L3533：本拍-2×上一拍+上上拍扭矩，二阶离散差分，不除dt²。
        )  # 原L3534：本拍-2×上一拍+上上拍扭矩，二阶离散差分，不除dt²。
        rew_torque_rate = torch.sum(torch.square(torque_rate[:, self._actuate_idx]), dim=-1)  # 原L3535：扭矩一阶差平方和。
        rew_torque_smoothness_leg = torch.sum(  # 原L3536：腿扭矩二阶差平方和。
            torch.square(torque_second_diff[:, self._legs_act_idx]), dim=-1  # 原L3537：腿扭矩二阶差平方和。
        )  # 原L3538：腿扭矩二阶差平方和。
        rew_torque_smoothness_wheel = torch.sum(  # 原L3539：轮扭矩二阶差平方和。
            torch.square(torque_second_diff[:, self._wheel_idx]), dim=-1  # 原L3540：轮扭矩二阶差平方和。
        )  # 原L3541：轮扭矩二阶差平方和。
        self._before_previous_applied_torque.copy_(self._previous_applied_torque)  # 原L3542：上一拍扭矩移到上上拍缓存。
        self._previous_applied_torque.copy_(applied_torque)  # 原L3543：本拍扭矩写入上一拍缓存。
        wheel_power = applied_torque[:,self._wheel_idx]*self.joint_vel[:,self._wheel_idx]  # 原L3544：每轮扭矩×角速度，重新计算功率。
        comsume_wheel_power = torch.clamp(wheel_power,min=0)  # 原L3545：仅取正机械功率。
        rew_wheel_power = torch.sum(comsume_wheel_power, dim=-1)  # 原L3546：左右正功率相加；公开模型负权重-1e-5。
        # if self.cfg.use_leg_length_as_height:  [原L3547：原作者注释，不执行]
        #     rew_lin_vel_z = torch.square(left_leg_length_dot+right_leg_length_dot)  [原L3548：原作者注释，不执行]
        # else:  [原L3549：原作者注释，不执行]
        rew_leg_len_vel = torch.square(left_leg_length_dot) + torch.square(right_leg_length_dot)  # 原L3550：左右腿伸缩速度各平方后相加。
        rew_lin_vel_z = torch.square(self.robot.data.root_lin_vel_b[:, 2])  # 原L3551：身体坐标vz平方；不同于世界坐标上升速度。
        rew_lin_vel_z_exp = torch.exp(-rew_lin_vel_z / self.cfg.lin_vel_z_sigma)  # 原L3552：近零身体vz指数分，公开模型没有启用此正奖励项。
        rew_ang_vel_xy = torch.sum(torch.square(self.robot.data.root_ang_vel_b[:, :2]), dim=1)  # 原L3553：身体x/y角速度平方和，限制roll/pitch快速转动。
        rew_action_rate = torch.sum(torch.square(self._actions - self._previous_actions), dim=1)  # 原L3554：全动作一阶差平方和，命令变化代价。
        action_second_diff = self._actions - 2 * self._previous_actions + self._before_previous_actions  # 原L3555：动作二阶差分。
        rew_action_smoothness = torch.sum(torch.square(action_second_diff), dim=-1)  # 原L3556：全动作二阶差平方和。
        leg_action_slice, wheel_action_slice = self._get_policy_action_slices()  # 原L3557：按真实策略动作布局分离腿/轮通道。
        rew_action_rate_leg = torch.sum(torch.square(self._actions[:, leg_action_slice] - self._previous_actions[:, leg_action_slice]), dim=1)  # 原L3558：腿动作一阶差平方和。
        rew_action_rate_wheel = torch.sum(torch.square(self._actions[:, wheel_action_slice] - self._previous_actions[:, wheel_action_slice]), dim=1)  # 原L3559：轮动作一阶差平方和。
        rew_action_smoothness_leg = torch.sum(torch.square(action_second_diff[:, leg_action_slice]), dim=-1)  # 原L3560：腿动作二阶差平方和，公开模型启用。
        rew_action_smoothness_wheel = torch.sum(torch.square(action_second_diff[:, wheel_action_slice]), dim=-1)  # 原L3561：轮动作二阶差平方和，公开模型启用。
        # rew_joint_deviation_l2 = torch.sum(torch.square(self.joint_pos[:,self._deviation_joint_idx]-deviation_joints),dim=-1)  [原L3562：原作者注释，不执行]
        # rew_joint_deviation_l1 = torch.sum(torch.abs(self.joint_pos[:,self._deviation_joint_idx]-deviation_joints),dim=-1)  [原L3563：原作者注释，不执行]

        # print(self.robot.data.root_lin_vel_b[:, 0])  [原L3565：原作者注释，不执行]
        # print(self.robot.data.applied_torque[:,self._wheel_idx])  [原L3566：原作者注释，不执行]

        # tasks  [原L3568：原作者注释，不执行]
        reward_command = self.command  # 原L3569：读取本step评分用命令。
        tracking_command = reward_command  # 原L3570：初始追踪命令和原命令一致。
        stand_still_lin_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)  # 原L3571：初始化静止前向/yaw命令mask。
        stand_still_yaw_mask = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)  # 原L3572：初始化静止前向/yaw命令mask。
        if bool(getattr(self.cfg, "stand_still_deadzone_enabled", False)):  # 原L3573：可选静止死区，公开模型开启。
            stand_still_threshold = max(  # 原L3574：死区阈值，源码兜底0.2，公开保存配置覆盖0.1。
                float(getattr(self.cfg, "stand_still_deadzone_threshold", 0.2)),  # 原L3575：死区阈值，源码兜底0.2，公开保存配置覆盖0.1。
                0.0,  # 原L3576：死区阈值，源码兜底0.2，公开保存配置覆盖0.1。
            )  # 原L3577：死区阈值，源码兜底0.2，公开保存配置覆盖0.1。
            stand_still_lin_mask = torch.abs(reward_command[:, 0]) < stand_still_threshold  # 原L3578：前向命令绝对值小于阈值就当静止平移。
            stand_still_yaw_mask = torch.abs(reward_command[:, 2]) < stand_still_threshold  # 原L3579：yaw rate命令绝对值小于阈值就当静止旋转。
            tracking_command = reward_command.clone()  # 原L3580：复制命令，避免改原命令。
            tracking_command[stand_still_lin_mask, 0] = 0.0  # 原L3581：死区内前向追踪目标设0。
            tracking_command[stand_still_yaw_mask, 2] = 0.0  # 原L3582：死区内yaw rate目标设0。

        pgb = self.robot.data.projected_gravity_b[:, :2]  # 原L3584：取机体系重力投影的水平xy分量，近水平时接近0。
        # pgb[:,0] = pgb[:,0]-0.02  [原L3585：原作者注释，不执行]
        # rew_flat_orientation = torch.sum(torch.square(self.robot.data.projected_gravity_b[:, :2]), dim=1)  [原L3586：原作者注释，不执行]
        rew_flat_orientation = torch.sum(torch.square(pgb), dim=-1)  # 原L3587：两个水平重力投影平方和作为总体倾斜量。
        rew_flat_orientation_y = torch.square(self.cfg.orientation_y_square_sigma*pgb[:,0])  # 原L3588：pitch相关pgb_x乘系数后平方。
        rew_flat_orientation_x = torch.square(self.cfg.orientation_x_square_sigma*pgb[:,1])  # 原L3589：roll相关pgb_y乘系数后平方。
        rew_flat_orientation_y_exp = torch.exp(-torch.square(pgb[:,0]) / self.cfg.orientation_y_exp_sigma)  # 原L3590：pitch相关指数分exp(-pgb_x²/sigma_y)，sigma直接作分母。
        rew_flat_orientation_x_exp = torch.exp(-torch.square(pgb[:,1]) / self.cfg.orientation_x_exp_sigma)  # 原L3591：roll相关指数分exp(-pgb_y²/sigma_x)。
        lin_vel_x_cmd = torch.square(reward_command[:,0])  # 原L3592：前进速度命令平方，下面调姿态代价系数。
        rew_flat_orientation_y_v = torch.square(  # 原L3593：pitch代价=[(A*exp(-cmd_x²/sigma)+bias)*pgb_x]²；低速系数更大。
            (  # 原L3594：pitch代价=[(A*exp(-cmd_x²/sigma)+bias)*pgb_x]²；低速系数更大。
                self.cfg.orientation_y_A * torch.exp(-lin_vel_x_cmd / self.cfg.orientation_y_sigma)  # 原L3595：pitch代价=[(A*exp(-cmd_x²/sigma)+bias)*pgb_x]²；低速系数更大。
                + self.cfg.orientation_y_bias  # 原L3596：pitch代价=[(A*exp(-cmd_x²/sigma)+bias)*pgb_x]²；低速系数更大。
            )  # 原L3597：pitch代价=[(A*exp(-cmd_x²/sigma)+bias)*pgb_x]²；低速系数更大。
            * pgb[:, 0]  # 原L3598：pitch代价=[(A*exp(-cmd_x²/sigma)+bias)*pgb_x]²；低速系数更大。
        )  # 原L3599：pitch代价=[(A*exp(-cmd_x²/sigma)+bias)*pgb_x]²；低速系数更大。
        rew_flat_orientation_x_v = torch.square((self.cfg.orientation_x_A * torch.exp(-lin_vel_x_cmd/self.cfg.orientation_x_sigma) + self.cfg.orientation_x_bias)*pgb[:,1])  # 原L3600：roll同样随速度命令调系数；不是相对任意参考四元数的姿态误差。
        # rew_flat_orientation = torch.square(self.robot.data.projected_gravity_b[:, 1])  [原L3601：原作者注释，不执行]

        # ========== 姿态门控：只有接近水平时速度/角速度 tracking 奖励才高 ==========  [原L3603：原作者注释，不执行]
        # upright_err: projected_gravity_b 的水平分量平方和，越小越水平  [原L3604：原作者注释，不执行]
        upright_err = rew_flat_orientation  # 原L3605：总重力水平投影误差作为upright_err。
        if bool(getattr(self.cfg, "vel_upright_gate_enabled", False)):  # 原L3606：可选速度奖励水平姿态门控。
            sigma = float(getattr(self.cfg, "vel_upright_gate_sigma", 0.02))  # 原L3607：读指数分母并防0。
            sigma = max(sigma, 1e-6)  # 原L3608：读指数分母并防0。
            vel_upright_gate = torch.exp(-upright_err / sigma)  # 原L3609：越倾斜，速度追踪项乘的门控越小。
        else:  # 原L3610：不开启则门控1；公开保存配置false。
            vel_upright_gate = 1.0  # 原L3611：不开启则门控1；公开保存配置false。

        vel_orientation_x_gate_enabled = self._get_vel_orientation_x_gate_enabled()  # 原L3613：读取roll方向速度奖励门控开关，可为逐环境tensor。
        if torch.is_tensor(vel_orientation_x_gate_enabled) or bool(vel_orientation_x_gate_enabled):  # 原L3614：tensor或全局true时计算门控。
            orientation_x_angle = torch.asin(torch.clamp(torch.abs(pgb[:, 1]), max=1.0))  # 原L3615：从abs(pgb_y)取asin，作为roll方向倾斜角，限制最大1。
            full_angle_deg = torch.clamp(  # 原L3616：读取全分角度阈值，转逐环境tensor并至少0。
                self._as_reward_gate_tensor(self._get_vel_orientation_x_gate_full_deg(), orientation_x_angle),  # 原L3617：读取全分角度阈值，转逐环境tensor并至少0。
                min=0.0,  # 原L3618：读取全分角度阈值，转逐环境tensor并至少0。
            )  # 原L3619：读取全分角度阈值，转逐环境tensor并至少0。
            zero_angle_deg = torch.maximum(  # 原L3620：读取零分角度阈值并保证不低于全分阈值。
                torch.clamp(  # 原L3621：读取零分角度阈值并保证不低于全分阈值。
                    self._as_reward_gate_tensor(self._get_vel_orientation_x_gate_zero_deg(), orientation_x_angle),  # 原L3622：读取零分角度阈值并保证不低于全分阈值。
                    min=0.0,  # 原L3623：读取零分角度阈值并保证不低于全分阈值。
                ),  # 原L3624：读取零分角度阈值并保证不低于全分阈值。
                full_angle_deg,  # 原L3625：读取零分角度阈值并保证不低于全分阈值。
            )  # 原L3626：读取零分角度阈值并保证不低于全分阈值。
            full_angle = torch.deg2rad(full_angle_deg)  # 原L3627：角度转弧度。
            zero_angle = torch.deg2rad(zero_angle_deg)  # 原L3628：角度转弧度。
            angle_band = zero_angle - full_angle  # 原L3629：过渡带宽。
            vel_orientation_x_gate = torch.where(  # 原L3630：带宽为0时使用硬阈值。
                angle_band <= 0.0,  # 原L3631：带宽为0时使用硬阈值。
                (orientation_x_angle <= full_angle).float(),  # 原L3632：带宽为0时使用硬阈值。
                torch.clamp(  # 原L3633：有过渡带时，从全分角到零分角线性降为0并截0到1。
                    (zero_angle - orientation_x_angle) / torch.clamp(angle_band, min=1.0e-6),  # 原L3634：有过渡带时，从全分角到零分角线性降为0并截0到1。
                    min=0.0,  # 原L3635：有过渡带时，从全分角到零分角线性降为0并截0到1。
                    max=1.0,  # 原L3636：有过渡带时，从全分角到零分角线性降为0并截0到1。
                ),  # 原L3637：有过渡带时，从全分角到零分角线性降为0并截0到1。
            )  # 原L3638：闭合上面的跨行表达式；不另产生奖励。
            if torch.is_tensor(vel_orientation_x_gate_enabled):  # 原L3639：开关是逐环境tensor。
                vel_orientation_x_gate = torch.where(  # 原L3640：只对启用环境使用门控，其余给1。
                    self._as_reward_gate_bool_tensor(vel_orientation_x_gate_enabled, orientation_x_angle),  # 原L3641：只对启用环境使用门控，其余给1。
                    vel_orientation_x_gate,  # 原L3642：只对启用环境使用门控，其余给1。
                    torch.ones_like(vel_orientation_x_gate),  # 原L3643：只对启用环境使用门控，其余给1。
                )  # 原L3644：只对启用环境使用门控，其余给1。
        else:  # 原L3645：全局关闭则门控1。
            vel_orientation_x_gate = 1.0  # 原L3646：全局关闭则门控1。

        vel_orientation_y_gate_enabled = self._get_vel_orientation_y_gate_enabled()  # 原L3648：读取pitch方向速度奖励门控开关。
        if torch.is_tensor(vel_orientation_y_gate_enabled) or bool(vel_orientation_y_gate_enabled):  # 原L3649：开关为逐环境tensor或true。
            orientation_y_angle = torch.asin(torch.clamp(torch.abs(pgb[:, 0]), max=1.0))  # 原L3650：从abs(pgb_x)取asin作为pitch方向角。
            full_angle_deg = torch.clamp(  # 原L3651：读全分角度阈值。
                self._as_reward_gate_tensor(self._get_vel_orientation_y_gate_full_deg(), orientation_y_angle),  # 原L3652：读全分角度阈值。
                min=0.0,  # 原L3653：读全分角度阈值。
            )  # 原L3654：读全分角度阈值。
            zero_angle_deg = torch.maximum(  # 原L3655：读零分阈值并保证>=全分阈值。
                torch.clamp(  # 原L3656：读零分阈值并保证>=全分阈值。
                    self._as_reward_gate_tensor(self._get_vel_orientation_y_gate_zero_deg(), orientation_y_angle),  # 原L3657：读零分阈值并保证>=全分阈值。
                    min=0.0,  # 原L3658：读零分阈值并保证>=全分阈值。
                ),  # 原L3659：读零分阈值并保证>=全分阈值。
                full_angle_deg,  # 原L3660：读零分阈值并保证>=全分阈值。
            )  # 原L3661：读零分阈值并保证>=全分阈值。
            full_angle = torch.deg2rad(full_angle_deg)  # 原L3662：转弧度。
            zero_angle = torch.deg2rad(zero_angle_deg)  # 原L3663：转弧度。
            angle_band = zero_angle - full_angle  # 原L3664：过渡带宽。
            vel_orientation_y_gate = torch.where(  # 原L3665：零带宽则硬阈值。
                angle_band <= 0.0,  # 原L3666：零带宽则硬阈值。
                (orientation_y_angle <= full_angle).float(),  # 原L3667：零带宽则硬阈值。
                torch.clamp(  # 原L3668：否则做0到1线性衰减。
                    (zero_angle - orientation_y_angle) / torch.clamp(angle_band, min=1.0e-6),  # 原L3669：否则做0到1线性衰减。
                    min=0.0,  # 原L3670：否则做0到1线性衰减。
                    max=1.0,  # 原L3671：否则做0到1线性衰减。
                ),  # 原L3672：否则做0到1线性衰减。
            )  # 原L3673：闭合上面的跨行表达式；不另产生奖励。
            if torch.is_tensor(vel_orientation_y_gate_enabled):  # 原L3674：开关为tensor。
                vel_orientation_y_gate = torch.where(  # 原L3675：未启用的环境门控置1。
                    self._as_reward_gate_bool_tensor(vel_orientation_y_gate_enabled, orientation_y_angle),  # 原L3676：未启用的环境门控置1。
                    vel_orientation_y_gate,  # 原L3677：未启用的环境门控置1。
                    torch.ones_like(vel_orientation_y_gate),  # 原L3678：未启用的环境门控置1。
                )  # 原L3679：未启用的环境门控置1。
        else:  # 原L3680：关闭时门控1；公开保存配置false。
            vel_orientation_y_gate = 1.0  # 原L3681：关闭时门控1；公开保存配置false。

        if bool(getattr(self.cfg, "height_upright_gate_enabled", False)):  # 原L3683：可选高度指数奖励姿态门控。
            height_sigma = float(getattr(self.cfg, "height_upright_gate_sigma", 0.02))  # 原L3684：读分母并防0。
            height_sigma = max(height_sigma, 1e-6)  # 原L3685：读分母并防0。
            height_upright_gate = torch.exp(-upright_err / height_sigma)  # 原L3686：高度奖励乘exp(-upright_err/sigma)。
        else:  # 原L3687：关闭时1；公开保存配置false。
            height_upright_gate = 1.0  # 原L3688：关闭时1；公开保存配置false。

        # 相对地面高度（默认模式）/ 绝对或腿长高度模式（按当前 cfg 保持原定义）  [原L3690：原作者注释，不执行]
        obs_height = self._get_observed_height(wheel_pos_b)  # 原L3691：读取实际高度信号，普通模式为root世界z。
        if self._use_absolute_height() or self._use_leg_length_height():  # 原L3692：绝对高度或腿长模式不用再减估计地面。
            relative_obs_height = obs_height  # 原L3693：这两种模式直接用obs_height。
        else:  # 原L3694：普通模式。
            relative_obs_height = obs_height - self.ground_z_est  # 原L3695：rootz-ground_z_est得到身体相对估计地面高度。
        wheel_relative_ground_heights = self._get_wheel_relative_ground_heights_raw()  # 原L3696：读取每轮相对地面高度。
        self.wheel_relative_ground_heights = wheel_relative_ground_heights  # 原L3697：缓存这一测量。
        wheel_height_w = self.robot.data.body_pos_w[:, self._wheel_link_idx, 2]  # 原L3698：取各轮轮心世界z。
        height_reward_ref = self._get_height_reward_reference_height(relative_obs_height, wheel_height_w)  # 原L3699：经状态机可改高度奖励测量口径，关闭状态机则保持普通相对高度。
        # print(height_reward_ref)  [原L3700：原作者注释，不执行]
        # 普通速度 tracking 仍按“水平前进速度”计算：  [原L3701：原作者注释，不执行]
        # 使用机体系前向 x 速度，再通过机身 pitch 投影到水平面，避免直接拿机体系 x 导致冲坡时高估水平速度。  [原L3702：原作者注释，不执行]
        root_rpy = euler_xyz_from_quat(self.robot.data.root_quat_w)  # 原L3703：从根四元数转roll/pitch/yaw。
        pitch = wrap_to_pi(root_rpy[1])  # 原L3704：pitch包裹到[-pi,pi]。
        roll = wrap_to_pi(root_rpy[0])  # 原L3705：roll包裹到[-pi,pi]。
        rew_flat_pitch_l1 = torch.abs(pitch*self.cfg.flat_pitch_l1_sigma)  # 原L3706：可选pitch绝对值代价，系数在绝对值里面。
        rew_flat_pitch_tanh = 1 - torch.tanh(torch.abs(pitch)/self.cfg.flat_pitch_tanh_sigma)  # 原L3707：可选pitch tanh奖励。
        rew_flat_roll_l1 = torch.abs(roll*self.cfg.flat_roll_l1_sigma)  # 原L3708：可选roll绝对值代价。
        rew_flat_roll_tanh = 1 - torch.tanh(torch.abs(roll)/self.cfg.flat_roll_tanh_sigma)  # 原L3709：可选roll tanh奖励。

        forward_lin_vel_horizontal = self.robot.data.root_lin_vel_b[:, 0] * torch.cos(pitch)  # 原L3711：机体系前向速度乘cos(pitch)作水平投影；按作者此实现，不直接用世界vx。
        lin_vel_err = tracking_command[:, 0] - forward_lin_vel_horizontal  # 原L3712：命令前向速度减实际水平投影速度；名字xy但这里没有直接累加y误差。
        if self.cfg.lin_vel_err_constraint is not None:  # 原L3713：配置速度指数误差限幅。
            track_lin_vel_err = torch.square(torch.clamp(lin_vel_err,  # 原L3714：先截±constraint再平方，公开constraint=1m/s。
                                                         min=-self.cfg.lin_vel_err_constraint,  # 原L3715：先截±constraint再平方，公开constraint=1m/s。
                                                         max=self.cfg.lin_vel_err_constraint))  # 原L3716：先截±constraint再平方，公开constraint=1m/s。
        else:  # 原L3717：无constraint时直接平方。
            track_lin_vel_err = torch.square(lin_vel_err)  # 原L3718：无constraint时直接平方。
        rew_track_lin_vel_xy = torch.exp(-track_lin_vel_err / self.cfg.lin_vel_xy_sigma)  # 原L3719：普通前向追踪分exp(-截断误差²/0.5)，公开权重1。
        rew_track_lin_vel_xy_soft = torch.exp(-track_lin_vel_err / self.cfg.lin_vel_xy_soft_sigma)  # 原L3720：宽前向追踪分。
        rew_track_lin_vel_xy_tight = torch.exp(-track_lin_vel_err / self.cfg.lin_vel_xy_tight_sigma)  # 原L3721：紧前向追踪分；公开权重0。
        rew_track_lin_vel_xy_huge_gap = track_lin_vel_err>self.cfg.lin_vel_xy_torlarance_gap  # 原L3722：误差平方是否大于配置gap的布尔项，未必是速度绝对误差阈值。
        rew_track_lin_vel_xy_square = torch.square(  # 原L3723：未截断速度误差乘square_sigma后平方，公开0.25，负权重-0.1。
            lin_vel_err * self.cfg.lin_vel_xy_square_sigma  # 原L3724：未截断速度误差乘square_sigma后平方，公开0.25，负权重-0.1。
        )  # 原L3725：未截断速度误差乘square_sigma后平方，公开0.25，负权重-0.1。
        lin_vel_abs_err = torch.abs(tracking_command[:, 0]) - torch.abs(forward_lin_vel_horizontal)  # 原L3726：命令速度绝对值减实际速度绝对值。
        rew_pen_high_speed = torch.square(torch.clamp(lin_vel_abs_err, max=0.)*self.cfg.high_speed_pen_sigma)  # 原L3727：只保留实际过快的负差后平方，构成可选超速代价。

        ang_vel_err = tracking_command[:, 2] - self.robot.data.root_ang_vel_b[:, 2]  # 原L3729：命令yaw rate减实际身体z轴角速度，不是yaw角误差。
        if self.cfg.ang_vel_err_constraint is not None:  # 原L3730：yaw rate指数误差限幅开关。
            track_yaw_rate_err = torch.square(torch.clamp(ang_vel_err,  # 原L3731：截±constraint再平方，公开constraint=0.8rad/s。
                                                         min=-self.cfg.ang_vel_err_constraint,  # 原L3732：截±constraint再平方，公开constraint=0.8rad/s。
                                                         max=self.cfg.ang_vel_err_constraint))  # 原L3733：截±constraint再平方，公开constraint=0.8rad/s。
        else:  # 原L3734：不限幅则直接平方。
            track_yaw_rate_err = torch.square(ang_vel_err)  # 原L3735：不限幅则直接平方。
        rew_track_ang_vel_z = torch.exp(-track_yaw_rate_err / self.cfg.ang_vel_z_sigma)  # 原L3736：普通yaw rate指数分，公开分母0.25、权重1。
        rew_track_ang_vel_z_soft = torch.exp(-track_yaw_rate_err / self.cfg.amg_vel_z_soft_sigma)  # 原L3737：宽yaw rate指数分。
        rew_track_ang_vel_z_huge_gap = track_yaw_rate_err>self.cfg.ang_vel_z_torlarance_gap  # 原L3738：误差平方是否过gap的布尔项。
        rew_track_ang_vel_z_square = torch.square(ang_vel_err*self.cfg.ang_vel_z_square_sigma)  # 原L3739：未截断yaw rate误差乘square_sigma再平方，公开0.5，权重-0.1。
        ang_vel_abs_err = torch.abs(tracking_command[:, 2]) - torch.abs(self.robot.data.root_ang_vel_b[:, 2])  # 原L3740：命令与实际yaw rate绝对值之差。
        rew_pen_high_angVel = torch.square(torch.clamp(ang_vel_abs_err, max=0.)*self.cfg.high_angVel_pen_sigma)  # 原L3741：仅实际过快部分的平方代价。

        rew_stand_still = (  # 原L3743：静止指令下平移速度平方和加yaw rate平方；公开此项0权重。
            torch.sum(torch.square(self.robot.data.root_lin_vel_b[:, :2]), dim=1)  # 原L3744：静止指令下平移速度平方和加yaw rate平方；公开此项0权重。
            * stand_still_lin_mask.float()  # 原L3745：静止指令下平移速度平方和加yaw rate平方；公开此项0权重。
            + torch.square(self.robot.data.root_ang_vel_b[:, 2]) * stand_still_yaw_mask.float()  # 原L3746：静止指令下平移速度平方和加yaw rate平方；公开此项0权重。
        )  # 原L3747：静止指令下平移速度平方和加yaw rate平方；公开此项0权重。
        rew_stand_still_lin_vel = (  # 原L3748：静止平移命令下身体xy速度绝对值和，公开权重-1。
            torch.sum(torch.abs(self.robot.data.root_lin_vel_b[:, :2]), dim=1)  # 原L3749：静止平移命令下身体xy速度绝对值和，公开权重-1。
            * stand_still_lin_mask.float()  # 原L3750：静止平移命令下身体xy速度绝对值和，公开权重-1。
        )  # 原L3751：静止平移命令下身体xy速度绝对值和，公开权重-1。

        # 约束加减速足端位置  [原L3753：原作者注释，不执行]
        # foot_bound_square = torch.square(wheel_pos_heading_b[:,:,0])  [原L3754：原作者注释，不执行]
        # rew_foot_bound = torch.sum(torch.abs(wheel_pos_heading_b[:,:,0])>self.cfg.foot_bound_dist,dim=1)  [原L3755：原作者注释，不执行]
        # rew_foot_bound_square = torch.sum(torch.square(wheel_pos_heading_b[:,:,0]*self.cfg.foot_bound_square_sigma),dim=1)  [原L3756：原作者注释，不执行]
        # rew_foot_bound_exp_pen = torch.sum(1-torch.exp(-foot_bound_square/self.cfg.foot_bound_exp_pen_sigma),dim=1)  [原L3757：原作者注释，不执行]
        # rew_foot_bound_exp = torch.sum(torch.exp(-foot_bound_square/self.cfg.foot_bound_sigma),dim=1)  [原L3758：原作者注释，不执行]
        # rew_foot_bound_ssquare = torch.sum(torch.square(foot_bound_square*self.cfg.foot_bound_ssquare_sigma),dim=1)  [原L3759：原作者注释，不执行]

        rew_stand_nice = torch.sum(torch.square(wheel_pos_heading_b[:,:,0]),dim=-1)  # 原L3761：可选轮子heading x距身体0的平方和。
        rew_no_fork_raw = torch.abs(wheel_pos_b[:,0,0]-wheel_pos_b[:,1,0])>self.cfg.no_fork_distance  # 原L3762：左右轮身体x错位是否超过no_fork_distance，公开5cm。
        rew_no_fork = rew_no_fork_raw.float()  # 原L3763：转成0/1二值代价。
        # exp 平滑的 no_fork 约束：仅在超过阈值后逐渐加大惩罚（与 no_fork 的硬阈值互补）  [原L3764：原作者注释，不执行]
        no_fork_dist = torch.abs(wheel_pos_b[:,0,0]-wheel_pos_b[:,1,0])  # 原L3765：实际左右轮x错位绝对值。
        no_fork_over = torch.clamp(no_fork_dist - self.cfg.no_fork_distance, min=0.0)  # 原L3766：超过阈值的正超量。
        rew_no_fork_exp = 1.0 - torch.exp(-no_fork_over / self.cfg.no_fork_exp_sigma)  # 原L3767：1-exp(-超量/sigma)平滑代价，公开0权重。
        no_fork_z_distance = float(getattr(self.cfg, "no_fork_z_distance", self.cfg.no_fork_distance))  # 原L3768：左右轮z错位阈值，默认复用x阈值。
        rew_no_fork_z_raw = torch.abs(wheel_pos_b[:,0,2]-wheel_pos_b[:,1,2]) > no_fork_z_distance  # 原L3769：z错位过阈值的二值代价。
        rew_no_fork_z = rew_no_fork_z_raw.float()  # 原L3770：z错位过阈值的二值代价。
        no_fork_z_dist = torch.abs(wheel_pos_b[:,0,2]-wheel_pos_b[:,1,2])  # 原L3771：z错位绝对值。
        no_fork_z_over = torch.clamp(no_fork_z_dist - no_fork_z_distance, min=0.0)  # 原L3772：z错位超量。
        no_fork_z_exp_sigma = float(getattr(self.cfg, "no_fork_z_exp_sigma", self.cfg.no_fork_exp_sigma))  # 原L3773：z平滑代价尺度。
        rew_no_fork_z_exp = 1.0 - torch.exp(-no_fork_z_over / no_fork_z_exp_sigma)  # 原L3774：z错位平滑代价，公开关闭。
        # 起身训练：落地阶段 no_fork 惩罚缩小  [原L3775：原作者注释，不执行]
        # if getattr(self.cfg, 'enable_standup_training', False):  [原L3776：原作者注释，不执行]
        #     landing_mask = (self._standup_phase == 0).float()  [原L3777：原作者注释，不执行]
        #     no_fork_landing_scale = getattr(self.cfg, 'no_fork_landing_scale', 0.1)  [原L3778：原作者注释，不执行]
        #     rew_no_fork = rew_no_fork_raw.float() * (1.0 - landing_mask * (1.0 - no_fork_landing_scale))  [原L3779：原作者注释，不执行]
        # else:  [原L3780：原作者注释，不执行]
        #     rew_no_fork = rew_no_fork_raw  [原L3781：原作者注释，不执行]
        rew_no_fork_square = torch.square((wheel_pos_b[:,0,0]-wheel_pos_b[:,1,0])*self.cfg.no_fork_square_sigma)  # 原L3782：左右轮身体x差乘系数5后平方，公开负权重-1。
        no_fork_z_square_sigma = float(getattr(self.cfg, "no_fork_z_square_sigma", self.cfg.no_fork_square_sigma))  # 原L3783：z错位平方项系数。
        rew_no_fork_z_square = torch.square((wheel_pos_b[:,0,2]-wheel_pos_b[:,1,2]) * no_fork_z_square_sigma)  # 原L3784：z错位平方项；是否生效仍看权重。
        # 兼容旧 reward key 名称：实际约束的是左右腿向量与世界重力方向对齐。  [原L3785：原作者注释，不执行]
        wheel_motor_z_axis_align_err_sq = self._get_wheel_motor_z_axis_align_error_sq()  # 原L3786：调用轮腿轴相对重力方向误差，不只凭旧key名字解释成电机z轴。
        wheel_motor_z_axis_align_sigma = max(  # 原L3787：读取普通轮腿对齐指数分母，可回退旧参数名，至少1e-6。
            float(  # 原L3788：读取普通轮腿对齐指数分母，可回退旧参数名，至少1e-6。
                getattr(  # 原L3789：读取普通轮腿对齐指数分母，可回退旧参数名，至少1e-6。
                    self.cfg,  # 原L3790：读取普通轮腿对齐指数分母，可回退旧参数名，至少1e-6。
                    "wheel_motor_z_axis_align_sigma",  # 原L3791：读取普通轮腿对齐指数分母，可回退旧参数名，至少1e-6。
                    getattr(self.cfg, "wheel_body_x_zero_sigma", 0.02),  # 原L3792：读取普通轮腿对齐指数分母，可回退旧参数名，至少1e-6。
                )  # 原L3793：读取普通轮腿对齐指数分母，可回退旧参数名，至少1e-6。
            ),  # 原L3794：读取普通轮腿对齐指数分母，可回退旧参数名，至少1e-6。
            1e-6,  # 原L3795：读取普通轮腿对齐指数分母，可回退旧参数名，至少1e-6。
        )  # 原L3796：读取普通轮腿对齐指数分母，可回退旧参数名，至少1e-6。
        wheel_motor_z_axis_align_tight_sigma = max(  # 原L3797：读取更紧的对齐指数分母，同样防0。
            float(  # 原L3798：读取更紧的对齐指数分母，同样防0。
                getattr(  # 原L3799：读取更紧的对齐指数分母，同样防0。
                    self.cfg,  # 原L3800：读取更紧的对齐指数分母，同样防0。
                    "wheel_motor_z_axis_align_tight_sigma",  # 原L3801：读取更紧的对齐指数分母，同样防0。
                    getattr(self.cfg, "wheel_body_x_zero_tight_sigma", 0.002),  # 原L3802：读取更紧的对齐指数分母，同样防0。
                )  # 原L3803：读取更紧的对齐指数分母，同样防0。
            ),  # 原L3804：读取更紧的对齐指数分母，同样防0。
            1e-6,  # 原L3805：读取更紧的对齐指数分母，同样防0。
        )  # 原L3806：读取更紧的对齐指数分母，同样防0。
        rew_wheel_motor_z_axis_align_exp = torch.exp(  # 原L3807：普通对齐指数奖励，公开权重表未启用。
            -wheel_motor_z_axis_align_err_sq / wheel_motor_z_axis_align_sigma  # 原L3808：普通对齐指数奖励，公开权重表未启用。
        )  # 原L3809：普通对齐指数奖励，公开权重表未启用。
        rew_wheel_motor_z_axis_align_exp_tight = torch.exp(  # 原L3810：更紧对齐指数奖励，公开未启用。
            -wheel_motor_z_axis_align_err_sq / wheel_motor_z_axis_align_tight_sigma  # 原L3811：更紧对齐指数奖励，公开未启用。
        )  # 原L3812：更紧对齐指数奖励，公开未启用。
        # rew_leg_end_vel = torch.sum(torch.square(wheel_lin_vel_b[:,:,0]),dim=-1)  [原L3813：原作者注释，不执行]
        # rew_leg_angle_l2 = torch.sum(torch.square(torch.stack([left_leg_angle,right_leg_angle],dim=-1)),dim=-1)  [原L3814：原作者注释，不执行]
        # rew_leg_angle_l1 = torch.sum(torch.abs(torch.stack([left_leg_angle,right_leg_angle],dim=-1)),dim=-1)  [原L3815：原作者注释，不执行]
        # rew_leg_ang_vel_l2 = torch.sum(torch.square(leg_ang_vel),dim=-1)  [原L3816：原作者注释，不执行]
        # rew_leg_ang_vel_l1 = torch.sum(torch.abs(leg_ang_vel),dim=-1)  [原L3817：原作者注释，不执行]
        rew_l_leg_ang_exp = torch.exp(-torch.square(left_leg_angle)/self.cfg.l_leg_ang_exp_sigma)  # 原L3818：左腿角接近0的可选指数奖励。
        rew_r_leg_ang_exp = torch.exp(-torch.square(right_leg_angle)/self.cfg.r_leg_ang_exp_sigma)  # 原L3819：右腿角接近0的可选指数奖励。

        height_reward_target = self._get_height_reward_target_height()  # 原L3821：获取最终生效高度目标，状态机可以覆盖。
        height_err = height_reward_ref - height_reward_target  # 原L3822：实际高度信号减高度目标。
        if self.cfg.height_err_constraint is not None:  # 原L3823：高度指数误差限幅开关。
            track_height_err = torch.square(torch.clamp(height_err,  # 原L3824：截到±height_err_constraint再平方，公开±0.15m。
                                                         min=-self.cfg.height_err_constraint,  # 原L3825：截到±height_err_constraint再平方，公开±0.15m。
                                                         max=self.cfg.height_err_constraint))  # 原L3826：截到±height_err_constraint再平方，公开±0.15m。
        else:  # 原L3827：无约束时直接平方。
            track_height_err = torch.square(height_err)  # 原L3828：无约束时直接平方。
        rew_track_height_square = torch.square(self.cfg.height_square_sigma * (height_err))  # 原L3829：未截断height_err×height_square_sigma后平方，公开系数10，权重-1。
        rew_track_height_l1 = torch.abs(self.cfg.height_l1_sigma * (height_err))  # 原L3830：高度L1代价。
        rew_track_height_exp = torch.exp(-track_height_err / self.cfg.height_sigma)  # 原L3831：普通高度指数分，公开0权重。
        rew_track_height_exp_soft = torch.exp(-track_height_err / self.cfg.height_soft_sigma)  # 原L3832：宽高度指数分，公开0权重。
        rew_track_height_exp_tight = torch.exp(-track_height_err / self.cfg.height_tight_sigma)  # 原L3833：紧高度指数分，公开分母0.001、权重1。
        rew_track_height_tanh = 1 - torch.tanh(torch.abs(height_err)/self.cfg.height_tanh_sigma)  # 原L3834：可选高度tanh分。
        rew_pen_base_too_low = torch.square(torch.clamp((self.cfg.base_height_bound-height_reward_ref), min=0.)*self.cfg.pen_base_too_low_sigma)  # 原L3835：身体低于base_height_bound的额外平方代价，是否生效看配置。

        # 速度高度门控：高度没跟住时降低速度/角速度 tracking 奖励，避免 policy 为了追速度牺牲高度。  [原L3837：原作者注释，不执行]
        vel_height_gate_enabled = self._get_vel_height_gate_enabled()  # 原L3838：读取速度奖励高度门控开关，可逐环境。
        # enabled 可以是全局 bool，也可以是 per-env bool tensor；tensor 用于不同任务/状态单独开关。  [原L3839：原作者注释，不执行]
        if torch.is_tensor(vel_height_gate_enabled) or bool(vel_height_gate_enabled):  # 原L3840：开关为tensor或true。
            vel_height_gate_mode = str(getattr(self.cfg, "vel_height_gate_mode", "exp")).lower()  # 原L3841：选择线性带或指数门控。
            if vel_height_gate_mode in ("linear_band", "band", "piecewise_linear"):  # 原L3842：线性带模式。
                height_abs_err = torch.abs(height_reward_ref - height_reward_target)  # 原L3843：高度绝对误差。
                # full_error 内门控为 1；zero_error 外门控为 0；中间线性衰减。  [原L3844：原作者注释，不执行]
                full_error = torch.clamp(  # 原L3845：读取全分误差界，至少0。
                    self._as_reward_gate_tensor(self._get_vel_height_gate_full_error(), height_abs_err),  # 原L3846：读取全分误差界，至少0。
                    min=0.0,  # 原L3847：读取全分误差界，至少0。
                )  # 原L3848：读取全分误差界，至少0。
                zero_error = torch.maximum(  # 原L3849：读取零分误差界且保证>=全分界。
                    torch.clamp(  # 原L3850：读取零分误差界且保证>=全分界。
                        self._as_reward_gate_tensor(self._get_vel_height_gate_zero_error(), height_abs_err),  # 原L3851：读取零分误差界且保证>=全分界。
                        min=0.0,  # 原L3852：读取零分误差界且保证>=全分界。
                    ),  # 原L3853：读取零分误差界且保证>=全分界。
                    full_error,  # 原L3854：读取零分误差界且保证>=全分界。
                )  # 原L3855：读取零分误差界且保证>=全分界。
                height_band = zero_error - full_error  # 原L3856：误差过渡带宽。
                vel_height_gate = torch.where(  # 原L3857：逐环境选退化或连续门控。
                    # 若 full_error == zero_error，则退化为硬阈值，避免除以 0。  [原L3858：原作者注释，不执行]
                    height_band <= 0.0,  # 原L3859：带宽0时用硬阈值。
                    (height_abs_err <= full_error).float(),  # 原L3860：带宽0时用硬阈值。
                    torch.clamp(  # 原L3861：否则误差从full_error到zero_error时门控从1降到0。
                        (zero_error - height_abs_err) / torch.clamp(height_band, min=1.0e-6),  # 原L3862：否则误差从full_error到zero_error时门控从1降到0。
                        min=0.0,  # 原L3863：否则误差从full_error到zero_error时门控从1降到0。
                        max=1.0,  # 原L3864：否则误差从full_error到zero_error时门控从1降到0。
                    ),  # 原L3865：否则误差从full_error到zero_error时门控从1降到0。
                )  # 原L3866：闭合上面的跨行表达式；不另产生奖励。
            else:  # 原L3867：指数门控模式。
                # 指数模式：默认复用高度 tracking reward，也可单独配置 tracker sigma。  [原L3868：原作者注释，不执行]
                vel_gate_sigma_cfg = getattr(self.cfg, "vel_height_gate_tracker_sigma", None)  # 原L3869：可单独指定tracker_sigma。
                if vel_gate_sigma_cfg is None:  # 原L3870：不指定则复用普通高度指数分。
                    vel_height_gate = rew_track_height_exp  # 原L3871：不指定则复用普通高度指数分。
                else:  # 原L3872：指定分母。
                    vel_gate_sigma = max(float(vel_gate_sigma_cfg), 1e-6)  # 原L3873：防0。
                    vel_height_gate = torch.exp(-track_height_err / vel_gate_sigma)  # 原L3874：高度误差越大速度奖励门控越低。
            if torch.is_tensor(vel_height_gate_enabled):  # 原L3875：逐环境开关。
                # 对未启用高度门控的 env，门控置 1，相当于不影响速度 tracking 奖励。  [原L3876：原作者注释，不执行]
                vel_height_gate = torch.where(  # 原L3877：未开启环境仍给门控1。
                    self._as_reward_gate_bool_tensor(vel_height_gate_enabled, height_reward_ref),  # 原L3878：未开启环境仍给门控1。
                    vel_height_gate,  # 原L3879：未开启环境仍给门控1。
                    torch.ones_like(vel_height_gate),  # 原L3880：未开启环境仍给门控1。
                )  # 原L3881：未开启环境仍给门控1。
        else:  # 原L3882：全局关闭时1，公开保存配置关闭。
            vel_height_gate = 1.0  # 原L3883：全局关闭时1，公开保存配置关闭。

        # 叠加门控  [原L3885：原作者注释，不执行]
        vel_reward_gate = vel_upright_gate * vel_orientation_x_gate * vel_orientation_y_gate * vel_height_gate  # 原L3886：四种速度门控相乘，任何一个为0就将追踪项压到0。
        rew_track_lin_vel_xy = rew_track_lin_vel_xy * vel_reward_gate  # 原L3887：门控作用于普通、宽、紧前向速度指数奖励。
        rew_track_lin_vel_xy_soft = rew_track_lin_vel_xy_soft * vel_reward_gate  # 原L3888：门控作用于普通、宽、紧前向速度指数奖励。
        rew_track_lin_vel_xy_tight = rew_track_lin_vel_xy_tight * vel_reward_gate  # 原L3889：门控作用于普通、宽、紧前向速度指数奖励。
        rew_track_lin_vel_xy_square = rew_track_lin_vel_xy_square * vel_reward_gate  # 原L3890：也作用于前向速度平方代价：门控低时连代价也会减小。
        rew_track_ang_vel_z = rew_track_ang_vel_z * vel_reward_gate  # 原L3891：门控作用于yaw rate指数奖励。
        rew_track_ang_vel_z_soft = rew_track_ang_vel_z_soft * vel_reward_gate  # 原L3892：门控作用于yaw rate指数奖励。
        rew_track_ang_vel_z_square = rew_track_ang_vel_z_square * vel_reward_gate  # 原L3893：也作用于yaw rate平方代价。
        rew_track_lin_vel_xy_huge_gap = rew_track_lin_vel_xy_huge_gap.float()  # 原L3894：把huge_gap布尔量转浮点。
        rew_track_ang_vel_z_huge_gap = rew_track_ang_vel_z_huge_gap.float()  # 原L3895：把huge_gap布尔量转浮点。

        rew_track_height_exp = rew_track_height_exp * height_upright_gate  # 原L3897：三种高度指数分乘高度姿态门控；高度平方代价未在这里乘这个门控。
        rew_track_height_exp_soft = rew_track_height_exp_soft * height_upright_gate  # 原L3898：三种高度指数分乘高度姿态门控；高度平方代价未在这里乘这个门控。
        rew_track_height_exp_tight = rew_track_height_exp_tight * height_upright_gate  # 原L3899：三种高度指数分乘高度姿态门控；高度平方代价未在这里乘这个门控。
        rew_track_height_huge_gap = height_reward_target - obs_height > self.cfg.height_torlarance_gap  # 原L3900：高度目标减obs_height过gap的布尔项；这里用obs_height而非height_reward_ref。
        # print(torch.abs(wheel_pos_b[:,0,0]-wheel_pos_b[:,1,0]))  [原L3901：原作者注释，不执行]
        # print('tar',self.height_cmd)  [原L3902：原作者注释，不执行]
        # print('cur',obs_height)  [原L3903：原作者注释，不执行]

        # undesired contacts  [原L3905：原作者注释，不执行]
        net_contact_forces = self.contact_sensor.data.net_forces_w_history  # 原L3906：读取世界接触力历史。
        undesired_contact_force_threshold = float(  # 原L3907：非期望部位接触阈值，兜底5N。
            getattr(self.cfg, "undesired_contact_force_threshold", 5.0)  # 原L3908：非期望部位接触阈值，兜底5N。
        )  # 原L3909：非期望部位接触阈值，兜底5N。
        desired_contact_force_threshold = float(  # 原L3910：期望轮接触阈值，兜底1N。
            getattr(self.cfg, "desired_contact_force_threshold", 1.0)  # 原L3911：期望轮接触阈值，兜底1N。
        )  # 原L3912：期望轮接触阈值，兜底1N。
        wheel_contact_force_peaks = self._get_wheel_contact_force_peaks(net_contact_forces)  # 原L3913：取各轮历史合力峰值。
        if wheel_contact_force_peaks.shape[1] >= 2:  # 原L3914：至少两轮数据。
            both_wheels_contact = torch.all(  # 原L3915：两轮各自历史峰值过阈值即both_wheels_contact，不限定台顶或同一physics拍。
                wheel_contact_force_peaks > desired_contact_force_threshold, dim=1  # 原L3916：两轮各自历史峰值过阈值即both_wheels_contact，不限定台顶或同一physics拍。
            )  # 原L3917：两轮各自历史峰值过阈值即both_wheels_contact，不限定台顶或同一physics拍。
        else:  # 原L3918：无双轮数据时给false。
            both_wheels_contact = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)  # 原L3919：无双轮数据时给false。
        rew_wheel_air_spin = self._get_wheel_air_spin_reward(  # 原L3920：调用可选轮空转代价函数，公开weight0。
            wheel_contact_force_peaks,  # 原L3921：调用可选轮空转代价函数，公开weight0。
            desired_contact_force_threshold,  # 原L3922：调用可选轮空转代价函数，公开weight0。
        )  # 原L3923：调用可选轮空转代价函数，公开weight0。
        rew_track_height_exp_both_wheels_contact = (  # 原L3924：宽高度指数分乘双轮接触mask，公开weight0。
            rew_track_height_exp_soft * both_wheels_contact.float()  # 原L3925：宽高度指数分乘双轮接触mask，公开weight0。
        )  # 原L3926：宽高度指数分乘双轮接触mask，公开weight0。

        # 计算总的有害接触奖励 (用于训练)  [原L3928：原作者注释，不执行]
        if net_contact_forces is not None:  # 原L3929：非期望部位接触力历史存在。
            harmful_contact_mask = (  # 原L3930：每个历史采样、每个非期望部位，合力范数是否超阈值。
                torch.norm(net_contact_forces[:, :, self._undesired_contact_link_idx], dim=-1)  # 原L3931：每个历史采样、每个非期望部位，合力范数是否超阈值。
                > undesired_contact_force_threshold  # 原L3932：每个历史采样、每个非期望部位，合力范数是否超阈值。
            )  # 原L3933：每个历史采样、每个非期望部位，合力范数是否超阈值。
            is_contact = torch.max(torch.max(harmful_contact_mask, dim=1)[0], dim=1)[0]  # 原L3934：沿时间和部位取any效果，只要一次过阈值就是true。
            rew_undesired_contact = is_contact.float()  # 原L3935：转0/1代价，公开weight-2，不是接触力大小本身。
        else:  # 原L3936：无数据时0。
            rew_undesired_contact = torch.zeros(self.num_envs, device=self.device)  # 原L3937：无数据时0。

        self._debug_print_undesired_contacts(net_contact_forces)  # 原L3939：调试输出，不新增奖励。

        # [内置] 实时终端打印 (已移除)  [原L3941：原作者注释，不执行]

        # desired contacts (车轮触地奖励/惩罚)  [原L3943：原作者注释，不执行]
        if wheel_contact_force_peaks.shape[1] > 0:  # 原L3944：轮峰值数据存在。
            # 检查车轮是否在历史窗口内有接触  [原L3945：原作者注释，不执行]
            is_not_contact = wheel_contact_force_peaks < desired_contact_force_threshold  # 原L3946：每轮历史峰值低于阈值表示未接触。
            rew_desired_contact = torch.sum(is_not_contact.float(), dim=1)  # 原L3947：数未接触轮数；虽然名字desired_contact，返回的是正代价而非接触正奖励。
        else:  # 原L3948：无轮数据时0。
            rew_desired_contact = torch.zeros(self.num_envs, device=self.device)  # 原L3949：无轮数据时0。

        # dof limits  [原L3951：原作者注释，不执行]
        if bool(getattr(self.cfg, "front_rear_joint_limit_rewards_enabled", True)):  # 原L3952：可选前后腿相对关节限位项开关。
            limits_actions_joint_error = [(self.leg_actions[:,0]-self.leg_actions[:,1]).unsqueeze(-1),  # 原L3953：每侧前/后腿动作差，拼成两侧张量。
                                  (self.leg_actions[:,2]-self.leg_actions[:,3]).unsqueeze(-1)]  # 原L3954：每侧前/后腿动作差，拼成两侧张量。
            limits_actions_joint_error = torch.cat(limits_actions_joint_error,dim=-1)  # 原L3955：每侧前/后腿动作差，拼成两侧张量。
            upper_error = limits_actions_joint_error > self.cfg.leg_front_rear_range[1]  # 原L3956：动作差是否超过配置上下界。
            lower_error = limits_actions_joint_error < self.cfg.leg_front_rear_range[0]  # 原L3957：动作差是否超过配置上下界。
            rew_actions_joint_limits = torch.sum(upper_error+lower_error,dim=-1)  # 原L3958：数越界的侧数，不是越界距离。

            limits_joint_error = self.joint_pos[:,self._legs_front_idx] - self.joint_pos[:,self._legs_rear_idx]  # 原L3960：实际前后腿关节角差。
            soft_range = [0.,0.]  # 原L3961：初始化软区间。
            scale_range = abs(self.cfg.leg_front_rear_range[1]-self.cfg.leg_front_rear_range[0])*(1-self.cfg.soft_range_scale)  # 原L3962：按硬区间跨度与soft_range_scale求软边界缩量。
            soft_range[0] = self.cfg.leg_front_rear_range[0] + scale_range  # 原L3963：从两端缩进得到软下/上界。
            soft_range[1] = self.cfg.leg_front_rear_range[1] - scale_range  # 原L3964：从两端缩进得到软下/上界。
            upper_error = limits_joint_error > soft_range[1]  # 原L3965：实际角差是否超软边界。
            lower_error = limits_joint_error < soft_range[0]  # 原L3966：实际角差是否超软边界。
            rew_current_joint_limits = torch.sum(upper_error+lower_error,dim=-1)  # 原L3967：数越界侧数。
        else:  # 原L3968：关闭时相关两项0。
            rew_actions_joint_limits = torch.zeros(self.num_envs, device=self.device)  # 原L3969：关闭时相关两项0。
            rew_current_joint_limits = torch.zeros(self.num_envs, device=self.device)  # 原L3970：关闭时相关两项0。

        (  # 原L3972：另一个环境辅助函数返回rear2/rear1相对关节位置、扭矩和速度约束代价；公开权重表没列这些项。
            rew_rear2_rear1_joint_pos_limits,  # 原L3973：另一个环境辅助函数返回rear2/rear1相对关节位置、扭矩和速度约束代价；公开权重表没列这些项。
            rew_rear2_rear1_joint_pos_limits_torque,  # 原L3974：另一个环境辅助函数返回rear2/rear1相对关节位置、扭矩和速度约束代价；公开权重表没列这些项。
            rew_rear2_rear1_joint_pos_limits_vel,  # 原L3975：另一个环境辅助函数返回rear2/rear1相对关节位置、扭矩和速度约束代价；公开权重表没列这些项。
        ) = self._get_rear2_rear1_joint_limit_terms()  # 原L3976：另一个环境辅助函数返回rear2/rear1相对关节位置、扭矩和速度约束代价；公开权重表没列这些项。

        # 起身训练奖励（仅 phase=1 起身阶段非零）  [原L3978：原作者注释，不执行]
        # in_standup = (self._standup_phase == 1) if getattr(self.cfg, 'enable_standup_training', False) else False  [原L3979：原作者注释，不执行]
        # if getattr(self.cfg, 'enable_standup_training', False):  [原L3980：原作者注释，不执行]
        #     standup_mask = in_standup.float()  [原L3981：原作者注释，不执行]
        #     rew_standup_height = obs_height * standup_mask  [原L3982：原作者注释，不执行]
        #     rew_standup_vel_z = torch.clamp(self.robot.data.root_lin_vel_b[:, 2], min=0.0) * standup_mask  [原L3983：原作者注释，不执行]
        #     rew_standup_smoothness = rew_action_smoothness * standup_mask  [原L3984：原作者注释，不执行]
        #     rew_standup_joint_torque = rew_joint_torque * standup_mask  [原L3985：原作者注释，不执行]
        #     rew_standup_wheel_power = rew_wheel_power * standup_mask  [原L3986：原作者注释，不执行]
        #     rew_standup_leg_joint_acc = rew_leg_joint_acc * standup_mask  [原L3987：原作者注释，不执行]
        #     rew_standup_wheel_vel = rew_wheel_vel * standup_mask  [原L3988：原作者注释，不执行]
        # else:  [原L3989：原作者注释，不执行]
        #     rew_standup_height = torch.zeros(self.num_envs, device=self.device)  [原L3990：原作者注释，不执行]
        #     rew_standup_vel_z = torch.zeros(self.num_envs, device=self.device)  [原L3991：原作者注释，不执行]
        #     rew_standup_smoothness = torch.zeros(self.num_envs, device=self.device)  [原L3992：原作者注释，不执行]
        #     rew_standup_joint_torque = torch.zeros(self.num_envs, device=self.device)  [原L3993：原作者注释，不执行]
        #     rew_standup_wheel_power = torch.zeros(self.num_envs, device=self.device)  [原L3994：原作者注释，不执行]
        #     rew_standup_leg_joint_acc = torch.zeros(self.num_envs, device=self.device)  [原L3995：原作者注释，不执行]
        #     rew_standup_wheel_vel = torch.zeros(self.num_envs, device=self.device)  [原L3996：原作者注释，不执行]

        reward_terms = {k[4:]: v for k, v in locals().items() if k.startswith("rew_")}  # 原L3998：收集当前作用域所有rew_变量，去掉前缀成为key；变量存在不代表被启用。
        reward_terms = self._postprocess_reward_terms(reward_terms)  # 原L3999：调用状态机及派生环境后处理，仍未乘权重和dt。

        # gather rewards  [原L4001：原作者注释，不执行]
        rewards = {k: v * self.step_dt for k, v in reward_terms.items()}  # 原L4002：每个原始项都乘控制step_dt，包括成功/终止等事件项。
        # 用 .get() 防止 cfg.rewards 里存在但对应 rew_* 变量被注释掉的键（如 standup 相关）  [原L4003：原作者注释，不执行]
        _zero_rew = torch.zeros(self.num_envs, device=self.device)  # 原L4004：创建缺失项的0回退。
        rewards = {k: w * rewards.get(k, _zero_rew) for k, w in self.cfg.rewards.items()}  # 原L4005：只遍历cfg.rewards中的key并乘各自w；未列入的新增项被过滤掉。

        # 数值保护：  [原L4007：原作者注释，不执行]
        # 1. 将每个 reward term 内部产生的 NaN/Inf 直接归零，防止污染 rollout。  [原L4008：原作者注释，不执行]
        # 2. 对本 step 已判定物理爆炸的 env，整条 reward 置零，避免坏状态参与 PPO 更新。  [原L4009：原作者注释，不执行]
        bad_reward_envs = self._numerical_safety_reset_buf  # 原L4010：已判定数值异常需要重置的环境mask。
        if bad_reward_envs.any():  # 原L4011：存在数值坏环境。
            bad_reward_envs_f = bad_reward_envs.float()  # 原L4012：把坏环境mask转浮点，本行变量后面未用于额外奖励。
            keep_reward_envs_f = (~bad_reward_envs).float()  # 原L4013：正常环境保留mask。
        for key, value in rewards.items():  # 原L4014：遍历每个加权项。
            sanitized_value = torch.nan_to_num(value, nan=0.0, posinf=0.0, neginf=0.0)  # 原L4015：NaN/正负Inf归0，防止污染rollout。
            if bad_reward_envs.any():  # 原L4016：坏环境整条奖励乘0。
                sanitized_value = sanitized_value * keep_reward_envs_f  # 原L4017：坏环境整条奖励乘0。
            rewards[key] = sanitized_value  # 原L4018：写回清理后的项。
        self._last_reward_terms = {key: value.detach() for key, value in rewards.items()}  # 原L4019：分离梯度保存本拍各项作日志，不另改变奖励。

        if bool(getattr(self.cfg, "reward_groups_enabled", False)):  # 原L4021：可选按task/safety/energy分组输出日志。
            group_names = tuple(getattr(self.cfg, "reward_group_names", ("task", "safety", "energy")))  # 原L4022：读取分组名字。
            group_index = {name: idx for idx, name in enumerate(group_names)}  # 原L4023：建立名字到列号的映射。
            term_groups = dict(getattr(self.cfg, "reward_term_groups", {}))  # 原L4024：读取每项的分组配置。
            reward_groups = torch.zeros(  # 原L4025：创建[N,group_count]的0日志张量。
                self.num_envs,  # 原L4026：创建[N,group_count]的0日志张量。
                len(group_names),  # 原L4027：创建[N,group_count]的0日志张量。
                dtype=torch.float,  # 原L4028：创建[N,group_count]的0日志张量。
                device=self.device,  # 原L4029：创建[N,group_count]的0日志张量。
            )  # 原L4030：创建[N,group_count]的0日志张量。
            default_group = group_index.get("task", 0)  # 原L4031：未指定组默认task或第一组。
            for key, value in rewards.items():  # 原L4032：逐项遍历已经加权的奖励。
                group_name = term_groups.get(key, "task")  # 原L4033：查询其所属组及组号。
                group_id = group_index.get(group_name, default_group)  # 原L4034：查询其所属组及组号。
                reward_groups[:, group_id] += value  # 原L4035：该项加到组日志，不再乘一次权重。
            self.extras["reward_groups"] = torch.nan_to_num(  # 原L4036：清理非有限组日志并放到extras，不替代后面的总奖励。
                reward_groups,  # 原L4037：清理非有限组日志并放到extras，不替代后面的总奖励。
                nan=0.0,  # 原L4038：清理非有限组日志并放到extras，不替代后面的总奖励。
                posinf=0.0,  # 原L4039：清理非有限组日志并放到extras，不替代后面的总奖励。
                neginf=0.0,  # 原L4040：清理非有限组日志并放到extras，不替代后面的总奖励。
            )  # 原L4041：清理非有限组日志并放到extras，不替代后面的总奖励。

        # Stepping command  [原L4043：原作者注释，不执行]
        sync_cmd_iteration = getattr(self, "_sync_command_generator_training_iteration", None)  # 原L4044：查找可选命令生成器训练迭代同步函数。
        if sync_cmd_iteration is not None:  # 原L4045：存在就同步；不是本步额外奖励。
            sync_cmd_iteration()  # 原L4046：存在就同步；不是本步额外奖励。
        self.command_generator.compute(self.step_dt)  # 原L4047：推进命令生成器一个控制dt。
        self._resample_custom_cmd(self.command_generator.command_counter)  # 原L4048：重采样定制命令。
        self.command = self.command_generator.command.clone()  # 原L4049：保存新命令副本。
        self._on_command_updated()  # 原L4050：调用命令更新钩子，状态机事件也在此产生；上方奖励使用更新前已缓存状态/事件。
        self._apply_predefined_reset_air_command_limits()  # 原L4051：应用预设空中reset的命令范围。

        # Logging rewards  [原L4053：原作者注释，不执行]
        for key, value in rewards.items():  # 原L4054：对每项做episode累计。
            if key not in self._episode_sums:  # 原L4055：新项首次出现则初始化累计缓存。
                self._episode_sums[key] = torch.zeros(self.num_envs, dtype=torch.float, device=self.device)  # 原L4056：新项首次出现则初始化累计缓存。
            self._episode_sums[key] += value  # 原L4057：把本拍加权项计入episode日志。
        rewards_tensor = torch.stack([rewards[k] for k in self.cfg.rewards.keys()], dim=-1)  # 原L4058：按cfg.rewards顺序堆成[N,term_count]。
        total_reward = torch.sum(rewards_tensor, dim=-1)  # 原L4059：沿项维度求和，得到每环境一个标量回报。
        total_reward = torch.nan_to_num(total_reward, nan=0.0, posinf=0.0, neginf=0.0)  # 原L4060：最后总分再做非有限清理。
        self._last_total_reward = total_reward.detach()  # 原L4061：保存总分日志副本。
        self._debug_print_reward_and_state_stats(rewards, total_reward)  # 原L4062：可选打印统计，不给额外分。
        return total_reward  # 原L4063：交给RL rollout的实际每环境回报。

    def _postprocess_reward_terms(self, reward_terms: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:  # 原L4065：普通环境奖励后处理钩子。
        """Hook for task-specific reward shaping before weights and logs are applied."""  # 原L4066：说明：权重和日志之前做任务塑形。
        return self.state_machine_manager.apply_reward_term_scales(self, reward_terms)  # 原L4067：将字典交给状态机管理器。
```
