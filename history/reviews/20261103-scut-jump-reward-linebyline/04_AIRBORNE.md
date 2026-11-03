# Airborne 空中与落地奖励逐行注释

当前V14 Rough-v1启用的新增权重为轮扭矩指数+20、顺行轮速+10、触地初期轮速不足-10、空中关节位置软限位-10、轮x居中+10。配置中的其它候选项不自动启用。普通undesired_contact倍率25、termination倍率6、flat_orientation_y_v和track_height_square倍率0；原始项的最终符号仍由普通权重决定。target_height.enabled=false，landing_trajectory.enabled=false。

进入空中要求身体高度与双轮高度达到enter阈值并满足duration，或配置请求强制进入。退出可由任一轮接触计时、base接触计时、最大持续时间或Stair状态触发。轮计时在近地且有足够力时增加；仍近地但力短暂消失时保持，轮抬高才清0；base计时也会保持。所以不要把它们描述成严格连续接触计时。详见原文件L712–909。

### 全部空中和落地奖励分支

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/airborne.py`，L983–L1292。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def apply_reward_term_scales(  # 原L983：空中/落地阶段奖励后处理钩子，输入输出都是尚未加权的逐环境原始项。
        self, env, reward_terms: dict[str, torch.Tensor]  # 原L984：空中/落地阶段奖励后处理钩子，输入输出都是尚未加权的逐环境原始项。
    ) -> dict[str, torch.Tensor]:  # 原L985：空中/落地阶段奖励后处理钩子，输入输出都是尚未加权的逐环境原始项。
        airborne_mask_f = env.height_reward_airborne_state.float()  # 原L986：空中状态转为0/1，落地初期可仍处在此状态，不能只按字面理解纯飞行。
        reward_full = self._cfg(env).get("reward_full", {})  # 原L987：读取空中阶段原始奖励替换表。
        for term_name, full_value in reward_full.items():  # 原L988：逐个读取要替换的原始项与固定值。
            if term_name not in reward_terms:  # 原L989：只替换已有项。
                continue  # 原L990：不存在则跳过。
            reward_terms[term_name] = torch.where(  # 原L991：逐环境选值。
                env.height_reward_airborne_state,  # 原L992：空中环境选择固定值。
                torch.full_like(reward_terms[term_name], float(full_value)),  # 原L993：构造同形状常数张量，数值仍未乘最终权重。
                reward_terms[term_name],  # 原L994：其它环境保留普通值。
            )  # 原L995：闭合上面的跨行表达式；不另产生奖励。

        reward_scales = self._cfg(env).get("reward_scales", {})  # 原L997：读取空中倍率表。
        for term_name, boost_scale in reward_scales.items():  # 原L998：逐项处理倍率。
            if term_name not in reward_terms:  # 原L999：不存在的普通项。
                continue  # 原L1000：跳过。
            if term_name in reward_full:  # 原L1001：已被reward_full替换的项。
                continue  # 原L1002：不再乘reward_scales，替换优先于缩放。
            scale = 1.0 + airborne_mask_f * (float(boost_scale) - 1.0)  # 原L1003：空中时boost_scale，非空中1。
            reward_terms[term_name] = reward_terms[term_name] * scale  # 原L1004：缩放原始项。

        reward_additions = self._cfg(env).get("reward_additions", {})  # 原L1006：读取空中新增项。
        reward_weights = getattr(env.cfg, "rewards", {})  # 原L1007：读取最终权重字典。
        for term_name, addition_cfg in reward_additions.items():  # 原L1008：逐个新增项。
            # reward_additions are materialized before cfg.rewards filters terms.  [原L1009：原作者注释，不执行]
            # Skip disabled additions here so expensive contact/kinematics terms do  [原L1010：原作者注释，不执行]
            # not run every step when their final reward weight is zero or absent.  [原L1011：原作者注释，不执行]
            reward_weight = reward_weights.get(term_name, None)  # 原L1012：查询该新增项最终权重。
            if reward_weight is None or float(reward_weight) == 0.0:  # 原L1013：没有权重或者权重为0。
                continue  # 原L1014：直接不计算，避免无用接触/运动学运算；不是配置中有定义就生效。
            if isinstance(addition_cfg, dict):  # 原L1015：字典定义走type公式。
                addition_type = addition_cfg.get("type", "constant")  # 原L1016：缺省constant。
                if addition_type == "constant":  # 原L1017：活动期常数。
                    added_reward = airborne_mask_f * float(addition_cfg["value"])  # 原L1018：空中mask乘配置value。
                elif addition_type == "body_height_below":  # 原L1019：身体低于阈值代价。
                    threshold = float(addition_cfg["threshold"])  # 原L1020：读高度阈值。
                    mode = addition_cfg.get("mode", "l1")  # 原L1021：L1/L2/binary模式，缺省L1。
                    square_sigma = float(addition_cfg.get("square_sigma", 1.0))  # 原L1022：L2代价系数。
                    body_relative_ground_height = env.robot.data.root_pos_w[:, 2] - env.ground_z_est  # 原L1023：身体高度是rootz-ground_z_est。
                    height_deficit = torch.clamp(  # 原L1024：高度不足=max(threshold-actual_height,0)。
                        threshold - body_relative_ground_height,  # 原L1025：高度不足=max(threshold-actual_height,0)。
                        min=0.0,  # 原L1026：高度不足=max(threshold-actual_height,0)。
                    )  # 原L1027：高度不足=max(threshold-actual_height,0)。
                    if mode == "l1":  # 原L1028：L1模式。
                        added_reward = airborne_mask_f * height_deficit  # 原L1029：空中时返回不足量，负权重才扣分。
                    elif mode == "l2":  # 原L1030：L2模式。
                        added_reward = airborne_mask_f * square_sigma * torch.square(height_deficit)  # 原L1031：square_sigma×不足²；这里系数不平方，区别于Stair水平力L2。
                    elif mode == "binary":  # 原L1032：二值模式。
                        added_reward = airborne_mask_f * (height_deficit > 0.0).float()  # 原L1033：只要低了就给正1代价。
                    else:  # 原L1034：非法模式报错。
                        raise ValueError(f"Unsupported body_height_below reward mode: {mode}")  # 原L1035：非法模式报错。
                elif addition_type == "undesired_contact_force":  # 原L1036：非期望部位接触力超量代价。
                    net_contact_forces = getattr(  # 原L1037：读取世界接触力历史，缺失为None。
                        getattr(getattr(env, "contact_sensor", None), "data", None),  # 原L1038：读取世界接触力历史，缺失为None。
                        "net_forces_w_history",  # 原L1039：读取世界接触力历史，缺失为None。
                        None,  # 原L1040：读取世界接触力历史，缺失为None。
                    )  # 原L1041：读取世界接触力历史，缺失为None。
                    if net_contact_forces is None or len(getattr(env, "_undesired_contact_link_idx", [])) == 0:  # 原L1042：没有力数据或没有非期望部位索引。
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)  # 原L1043：此项给0，不是证明没接触。
                    else:  # 原L1044：有数据。
                        force_threshold = float(  # 原L1045：读免罚力阈值，回退全局阈值，最后5N。
                            addition_cfg.get(  # 原L1046：读免罚力阈值，回退全局阈值，最后5N。
                                "force_threshold",  # 原L1047：读免罚力阈值，回退全局阈值，最后5N。
                                getattr(env.cfg, "undesired_contact_force_threshold", 5.0),  # 原L1048：读免罚力阈值，回退全局阈值，最后5N。
                            )  # 原L1049：读免罚力阈值，回退全局阈值，最后5N。
                        )  # 原L1050：读免罚力阈值，回退全局阈值，最后5N。
                        mode = addition_cfg.get("mode", "l2")  # 原L1051：代价形状缺省L2。
                        square_sigma = float(addition_cfg.get("square_sigma", 1.0))  # 原L1052：L2系数。
                        contact_forces = torch.norm(  # 原L1053：把所有选定部位和历史采样力向量展平，再整体求范数；不是每个部位只取瞬时最大。
                            net_contact_forces[:, :, env._undesired_contact_link_idx].flatten(start_dim=1),  # 原L1054：把所有选定部位和历史采样力向量展平，再整体求范数；不是每个部位只取瞬时最大。
                            dim=-1,  # 原L1055：把所有选定部位和历史采样力向量展平，再整体求范数；不是每个部位只取瞬时最大。
                        )  # 原L1056：把所有选定部位和历史采样力向量展平，再整体求范数；不是每个部位只取瞬时最大。
                        force_over = torch.clamp(  # 原L1057：只保留该范数超过阈值的部分。
                            contact_forces - force_threshold,  # 原L1058：只保留该范数超过阈值的部分。
                            min=0.0,  # 原L1059：只保留该范数超过阈值的部分。
                        )  # 原L1060：只保留该范数超过阈值的部分。
                        added_reward = airborne_mask_f * self._shape_penalty(  # 原L1061：乘空中mask并按binary/L1/L2塑形。
                            force_over, mode, square_sigma=square_sigma  # 原L1062：乘空中mask并按binary/L1/L2塑形。
                        )  # 原L1063：乘空中mask并按binary/L1/L2塑形。
                elif addition_type == "wheel_contact_force_over":  # 原L1064：每轮接触力超阈值代价。
                    net_contact_forces = getattr(  # 原L1065：读取历史力数据。
                        getattr(getattr(env, "contact_sensor", None), "data", None),  # 原L1066：读取历史力数据。
                        "net_forces_w_history",  # 原L1067：读取历史力数据。
                        None,  # 原L1068：读取历史力数据。
                    )  # 原L1069：读取历史力数据。
                    if net_contact_forces is None or len(getattr(env, "_desired_contact_link_idx", [])) == 0:  # 原L1070：缺数据或轮索引。
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)  # 原L1071：该项0。
                    else:  # 原L1072：有数据。
                        force_threshold = float(  # 原L1073：取力阈值，优先本项，再全局desired阈值，最后兜底5N。
                            addition_cfg.get(  # 原L1074：取力阈值，优先本项，再全局desired阈值，最后兜底5N。
                                "force_threshold",  # 原L1075：取力阈值，优先本项，再全局desired阈值，最后兜底5N。
                                getattr(env.cfg, "desired_contact_force_threshold", 5.0),  # 原L1076：取力阈值，优先本项，再全局desired阈值，最后兜底5N。
                            )  # 原L1077：取力阈值，优先本项，再全局desired阈值，最后兜底5N。
                        )  # 原L1078：取力阈值，优先本项，再全局desired阈值，最后兜底5N。
                        mode = addition_cfg.get("mode", "l1")  # 原L1079：形状缺省L1。
                        square_sigma = float(addition_cfg.get("square_sigma", 1.0))  # 原L1080：L2系数。
                        reduce = addition_cfg.get("reduce", "sum")  # 原L1081：两轮汇总模式缺省sum。
                        wheel_forces = torch.amax(  # 原L1082：各轮世界合力先求范数，再沿历史时间取峰值。
                            torch.norm(net_contact_forces[:, :, env._desired_contact_link_idx], dim=-1),  # 原L1083：各轮世界合力先求范数，再沿历史时间取峰值。
                            dim=1,  # 原L1084：各轮世界合力先求范数，再沿历史时间取峰值。
                        )  # 原L1085：各轮世界合力先求范数，再沿历史时间取峰值。
                        force_over = torch.clamp(wheel_forces - force_threshold, min=0.0)  # 原L1086：每轮只取超过阈值的量。
                        wheel_penalty = self._shape_penalty(  # 原L1087：各轮独立塑形为代价。
                            force_over, mode, square_sigma=square_sigma  # 原L1088：各轮独立塑形为代价。
                        )  # 原L1089：各轮独立塑形为代价。
                        if reduce == "mean":  # 原L1090：mean汇总。
                            added_reward = airborne_mask_f * wheel_penalty.mean(dim=1)  # 原L1091：左右代价平均。
                        elif reduce == "max":  # 原L1092：max汇总。
                            added_reward = airborne_mask_f * wheel_penalty.max(dim=1).values  # 原L1093：只取更大的轮代价。
                        elif reduce == "sum":  # 原L1094：sum汇总。
                            added_reward = airborne_mask_f * wheel_penalty.sum(dim=1)  # 原L1095：左右代价相加。
                        else:  # 原L1096：非法汇总方式报错。
                            raise ValueError(f"Unsupported wheel_contact_force_over reduce mode: {reduce}")  # 原L1097：非法汇总方式报错。
                elif addition_type == "landing_wheel_max_contact_force":  # 原L1098：落地最大轮接触力的归一化量。
                    contact_forces_w = self._get_current_contact_forces(env)  # 原L1099：取当前接触力，不是历史峰值。
                    if contact_forces_w is None or len(getattr(env, "_desired_contact_link_idx", [])) == 0:  # 原L1100：无数据或轮索引。
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)  # 原L1101：此项0。
                    else:  # 原L1102：有数据。
                        reward_mask = self._get_wheel_contact_started_mask(env, addition_cfg)  # 原L1103：要求轮接触计时达到配置时长。
                        reward_mask &= self._get_wheel_contact_force_mask(env, addition_cfg)  # 原L1104：再要求当前接触力达到配置阈值。
                        force_start = float(addition_cfg.get("force_start", 200.0))  # 原L1105：力评分起点，兜底200N。
                        force_full = float(addition_cfg.get("force_full", 400.0))  # 原L1106：力评分达到1的值，兜底400N。
                        denom = max(force_full - force_start, 1.0e-6)  # 原L1107：归一化区间至少1e-6。
                        wheel_forces = torch.norm(  # 原L1108：当前各轮世界合力大小。
                            contact_forces_w[:, env._desired_contact_link_idx], dim=-1  # 原L1109：当前各轮世界合力大小。
                        )  # 原L1110：当前各轮世界合力大小。
                        max_wheel_force = wheel_forces.max(dim=1).values  # 原L1111：取两轮最大力。
                        added_reward = reward_mask.float() * torch.clamp(  # 原L1112：把(maxforce-start)/(full-start)截到0..1并乘窗口；负权重才惩罚大冲击。
                            (max_wheel_force - force_start) / denom,  # 原L1113：把(maxforce-start)/(full-start)截到0..1并乘窗口；负权重才惩罚大冲击。
                            0.0,  # 原L1114：把(maxforce-start)/(full-start)截到0..1并乘窗口；负权重才惩罚大冲击。
                            1.0,  # 原L1115：把(maxforce-start)/(full-start)截到0..1并乘窗口；负权重才惩罚大冲击。
                        )  # 原L1116：把(maxforce-start)/(full-start)截到0..1并乘窗口；负权重才惩罚大冲击。
                elif addition_type == "landing_wheel_body_x_positive":  # 原L1117：落地时轮子放在身体前方的单边指数分。
                    reward_mask = self._get_wheel_contact_started_mask(env, addition_cfg)  # 原L1118：接触计时开始窗口。
                    reward_mask &= self._get_wheel_contact_force_mask(env, addition_cfg)  # 原L1119：当前力阈值门控。
                    command_x_min = float(addition_cfg.get("command_x_min", 1.0))  # 原L1120：只在前向命令超过阈值时，兜底1m/s。
                    command_x = self._get_reward_command_lin_vel_x(env, addition_cfg)  # 原L1121：按use_entry_command选进入空中时的命令或当前命令。
                    reward_mask &= command_x > command_x_min  # 原L1122：只保留命令x>阈值的环境；此分支不自动对称支持后退。
                    target_x = float(addition_cfg.get("target_x", 0.03))  # 原L1123：最靠后轮也至少在身体前方target_x，兜底3cm。
                    sigma = max(float(addition_cfg.get("sigma", target_x)), 1.0e-6)  # 原L1124：L1指数分母，兜底target_x。
                    _, _, wheel_pos_heading_b, _, _ = env._get_root_quat_inv_and_wheel_pos_b()  # 原L1125：取heading相对轮坐标。
                    wheel_x_min = wheel_pos_heading_b[:, :, 0].min(dim=1).values  # 原L1126：取两轮中较小的x，限制靠后的那一轮。
                    deficit = torch.clamp(target_x - wheel_x_min, min=0.0)  # 原L1127：不足量=max(target_x-min_x,0)。
                    added_reward = reward_mask.float() * torch.exp(-deficit / sigma)  # 原L1128：exp(-deficit/sigma)，这里不是误差平方。
                elif addition_type == "wheel_zero_torque_exp":  # 原L1129：空中轮扭矩接近0的指数奖励。
                    wheel_idx = getattr(env, "_wheel_idx", [])  # 原L1130：取轮电机索引。
                    if len(wheel_idx) == 0:  # 原L1131：没有轮索引。
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)  # 原L1132：返回0。
                    else:  # 原L1133：索引可用。
                        reward_mask_f = self._get_reward_window_mask(env, addition_cfg).float()  # 原L1134：取空中/触地前有效窗口。
                        sigma = max(float(addition_cfg.get("sigma", 1.5)), 1.0e-6)  # 原L1135：扭矩尺度，兜底1.5。
                        wheel_torque = env.robot.data.applied_torque[:, wheel_idx]  # 原L1136：读取实际施加的轮扭矩。
                        max_wheel_torque = torch.abs(wheel_torque).max(dim=1).values  # 原L1137：取左右轮绝对扭矩最大值，防一轮大一轮小平均抵消。
                        added_reward = reward_mask_f * torch.exp(  # 原L1138：exp(-(max_abs_torque/sigma)^2)；此处sigma先除再平方。
                            -torch.square(max_wheel_torque / sigma)  # 原L1139：exp(-(max_abs_torque/sigma)^2)；此处sigma先除再平方。
                        )  # 原L1140：exp(-(max_abs_torque/sigma)^2)；此处sigma先除再平方。
                elif addition_type == "wheel_directional_speed":  # 原L1141：顺行方向轮角速度奖励。
                    speed_score, _ = self._get_directional_wheel_speed_score(env, addition_cfg)  # 原L1142：调用辅助函数得到已经乘窗口/方向门控的score。
                    added_reward = speed_score  # 原L1143：直接使用这个score。
                elif addition_type == "wheel_directional_speed_shortfall":  # 原L1144：轮角速度不足代价。
                    speed_score, gate_f = self._get_directional_wheel_speed_score(env, addition_cfg)  # 原L1145：得到同类得分以及本次有效gate。
                    added_reward = gate_f * (1.0 - speed_score)  # 原L1146：gate×(1-score)，最终负权重鼓励补足轮速；gate关闭时不是扣1。
                elif addition_type == "landing_traj_height_exp":  # 原L1147：落地缓冲轨迹高度追踪。
                    self._ensure_landing_trajectory_buffers(env)  # 原L1148：确保缓冲轨迹缓存存在。
                    active_f = env.airborne_landing_traj_active.float()  # 原L1149：仅缓冲轨迹活动的环境。
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L1150：高度误差平方的直接分母。
                    h_ref, _ = self._get_landing_trajectory_reference(env)  # 原L1151：取缓冲轨迹参考高度。
                    height = self._get_body_relative_ground_height(env)  # 原L1152：实际身体相对地面高度。
                    added_reward = active_f * torch.exp(-torch.square(height - h_ref) / sigma)  # 原L1153：轨迹活动时指数追踪高度；当前V14配置关闭landing_trajectory。
                elif addition_type == "landing_traj_vel_z_exp":  # 原L1154：落地缓冲轨迹vz追踪。
                    self._ensure_landing_trajectory_buffers(env)  # 原L1155：确保缓存。
                    active_f = env.airborne_landing_traj_active.float()  # 原L1156：仅轨迹活动环境。
                    sigma = max(float(addition_cfg.get("sigma", 0.25)), 1.0e-6)  # 原L1157：vz误差平方的分母，兜底0.25。
                    _, v_ref = self._get_landing_trajectory_reference(env)  # 原L1158：取缓冲参考vz。
                    vel_z = env.robot.data.root_lin_vel_w[:, 2]  # 原L1159：取当前世界vz。
                    added_reward = active_f * torch.exp(-torch.square(vel_z - v_ref) / sigma)  # 原L1160：指数速度追踪；配置关闭时不能把它说成已用的缓冲奖励。
                elif addition_type == "negative_lin_vel_z_after_wheel_contact":  # 原L1161：触地后继续向下的速度代价。
                    wheel_exit_time = getattr(env, "airborne_wheel_contact_exit_time", None)  # 原L1162：取轮接触计时缓存。
                    if wheel_exit_time is None:  # 原L1163：没有缓存。
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)  # 原L1164：返回0。
                    else:  # 原L1165：有缓存。
                        start_duration_s = max(float(addition_cfg.get("start_duration_s", 0.02)), 0.0)  # 原L1166：开始计分的接触时间阈值，兜底0.02秒。
                        use_world_frame = bool(addition_cfg.get("use_world_frame", True))  # 原L1167：缺省使用世界vz，可改身体vz。
                        mode = addition_cfg.get("mode", "l2")  # 原L1168：缺省L2。
                        square_sigma = float(addition_cfg.get("square_sigma", 1.0))  # 原L1169：L2系数。
                        wheel_contact_started = torch.any(wheel_exit_time >= start_duration_s, dim=1)  # 原L1170：任一轮接触计时达到阈值就开始，而不是强制双轮。
                        if use_world_frame:  # 原L1171：使用世界坐标分支。
                            lin_vel_z = env.robot.data.root_lin_vel_w[:, 2]  # 原L1172：取世界vz。
                        else:  # 原L1173：使用身体坐标分支。
                            lin_vel_z = env.robot.data.root_lin_vel_b[:, 2]  # 原L1174：取身体vz，两种量在倾斜时不相同。
                        down_vel = torch.clamp(-lin_vel_z, min=0.0)  # 原L1175：down_vel=max(-vz,0)，上升不罚。
                        added_reward = (  # 原L1176：空中状态×已触地×非负下落速度代价；需要负权重。
                            airborne_mask_f  # 原L1177：空中状态×已触地×非负下落速度代价；需要负权重。
                            * wheel_contact_started.float()  # 原L1178：空中状态×已触地×非负下落速度代价；需要负权重。
                            * self._shape_penalty(down_vel, mode, square_sigma=square_sigma)  # 原L1179：空中状态×已触地×非负下落速度代价；需要负权重。
                        )  # 原L1180：空中状态×已触地×非负下落速度代价；需要负权重。
                elif addition_type == "negative_lin_vel_z_after_wheel_contact_exp":  # 原L1181：触地后竖直速度指数项，虽然名字带negative，公式上下对称。
                    wheel_exit_time = getattr(env, "airborne_wheel_contact_exit_time", None)  # 原L1182：取轮接触计时。
                    if wheel_exit_time is None:  # 原L1183：没有缓存。
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)  # 原L1184：返回0。
                    else:  # 原L1185：有缓存。
                        start_duration_s = max(float(addition_cfg.get("start_duration_s", 0.02)), 0.0)  # 原L1186：开始阈值。
                        use_world_frame = bool(addition_cfg.get("use_world_frame", True))  # 原L1187：世界或身体坐标开关。
                        sigma = max(float(addition_cfg.get("sigma", 1.0)), 1.0e-6)  # 原L1188：指数直接分母。
                        wheel_contact_started = torch.any(wheel_exit_time >= start_duration_s, dim=1)  # 原L1189：任一轮计时过阈值。
                        if use_world_frame:  # 原L1190：按开关取世界或身体vz，再组装奖励。
                            lin_vel_z = env.robot.data.root_lin_vel_w[:, 2]  # 原L1191：按开关取世界或身体vz，再组装奖励。
                        else:  # 原L1192：按开关取世界或身体vz，再组装奖励。
                            lin_vel_z = env.robot.data.root_lin_vel_b[:, 2]  # 原L1193：按开关取世界或身体vz，再组装奖励。
                        added_reward = (  # 原L1194：按开关取世界或身体vz，再组装奖励。
                            airborne_mask_f  # 原L1195：空中且已触地时exp(-vz²/sigma)，正/负vz同样降低分数。
                            * wheel_contact_started.float()  # 原L1196：空中且已触地时exp(-vz²/sigma)，正/负vz同样降低分数。
                            * torch.exp(-torch.square(lin_vel_z) / sigma)  # 原L1197：空中且已触地时exp(-vz²/sigma)，正/负vz同样降低分数。
                        )  # 原L1198：空中且已触地时exp(-vz²/sigma)，正/负vz同样降低分数。
                elif addition_type == "leg_retraction":  # 原L1199：收腿/腿长奖励族。
                    reward_mask_f = self._get_reward_window_mask(env, addition_cfg).float()  # 原L1200：空中与触地窗口mask。
                    leg_lengths = self._get_leg_lengths(env)  # 原L1201：取每腿相对轮向量长度。
                    mean_leg_length = leg_lengths.mean(dim=1)  # 原L1202：平均两腿长度。
                    target = float(addition_cfg.get("target", 0.22))  # 原L1203：目标腿长缺省0.22m。
                    mode = addition_cfg.get("mode", "above_target")  # 原L1204：模式缺省above_target。
                    if mode == "raw":  # 原L1205：raw模式。
                        added_reward = reward_mask_f * mean_leg_length  # 原L1206：直接平均腿长；权重正负决定鼓励长还是短。
                    elif mode == "above_target":  # 原L1207：平均腿长超过目标的代价。
                        added_reward = reward_mask_f * torch.clamp(mean_leg_length - target, min=0.0)  # 原L1208：只保留平均长度超过目标部分。
                    elif mode == "above_target_per_leg":  # 原L1209：逐腿超长模式。
                        added_reward = reward_mask_f * torch.clamp(leg_lengths - target, min=0.0).mean(dim=1)  # 原L1210：先各腿超量截正，再平均。
                    elif mode == "below_target":  # 原L1211：below_target模式。
                        added_reward = reward_mask_f * torch.clamp(target - mean_leg_length, min=0.0)  # 原L1212：只保留目标减平均腿长的正值；负权重鼓励别过短。
                    elif mode == "below_target_per_leg":  # 原L1213：逐腿过短模式。
                        added_reward = reward_mask_f * torch.clamp(target - leg_lengths, min=0.0).mean(dim=1)  # 原L1214：每腿过短量独立截正再平均。
                    elif mode == "exp":  # 原L1215：平均长度指数模式。
                        sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L1216：指数直接分母。
                        added_reward = reward_mask_f * torch.exp(  # 原L1217：平均腿长对目标的平方误差指数分。
                            -torch.square(mean_leg_length - target) / sigma  # 原L1218：平均腿长对目标的平方误差指数分。
                        )  # 原L1219：平均腿长对目标的平方误差指数分。
                    elif mode == "exp_per_leg":  # 原L1220：逐腿指数模式。
                        sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L1221：指数直接分母。
                        added_reward = reward_mask_f * torch.exp(  # 原L1222：逐腿指数后平均，不把左右误差先平均抵消。
                            -torch.square(leg_lengths - target) / sigma  # 原L1223：逐腿指数后平均，不把左右误差先平均抵消。
                        ).mean(dim=1)  # 原L1224：逐腿指数后平均，不把左右误差先平均抵消。
                    else:  # 原L1225：未知mode报错。
                        raise ValueError(f"Unsupported airborne leg_retraction reward mode: {mode}")  # 原L1226：未知mode报错。
                elif addition_type == "wheel_height_below_base_exp":  # 原L1227：轮底相对身体竖直高度指数追踪。
                    reward_mask_f = self._get_reward_window_mask(env, addition_cfg).float()  # 原L1228：取空中/触地奖励窗口。
                    target = float(addition_cfg.get("target", 0.22))  # 原L1229：轮底在身体下方的目标距离。
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L1230：指数直接分母。
                    rel_wheel_bottom_z = self._get_wheel_bottom_relative_to_base_z(env)  # 原L1231：调用轮心世界z-半径-rootz辅助函数。
                    target_rel_wheel_bottom_z = -target  # 原L1232：目标相对z为负target。
                    added_reward = reward_mask_f * torch.exp(  # 原L1233：逐轮高度误差指数后平均并乘mask。
                        -torch.square(rel_wheel_bottom_z - target_rel_wheel_bottom_z) / sigma  # 原L1234：逐轮高度误差指数后平均并乘mask。
                    ).mean(dim=1)  # 原L1235：逐轮高度误差指数后平均并乘mask。
                elif addition_type == "wheel_heading_x_centering":  # 原L1236：空中轮子前后居中奖励。
                    reward_mask_f = self._get_contact_timer_below_mask(env, addition_cfg).float()  # 原L1237：要求轮接触计时和base接触计时仍低于配置阈值。
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L1238：轮x误差平方的直接分母。
                    _, _, wheel_pos_heading_b, _, _ = env._get_root_quat_inv_and_wheel_pos_b()  # 原L1239：取heading坐标下轮相对根位置。
                    wheel_heading_z_max = addition_cfg.get("wheel_heading_z_max", None)  # 原L1240：可选要求轮子仍低于身体一定距离。
                    if wheel_heading_z_max is not None:  # 原L1241：该条件配置了。
                        wheel_z_below = torch.all(  # 原L1242：两轮heading坐标z都低于阈值才允许居中分。
                            wheel_pos_heading_b[:, :, 2] < float(wheel_heading_z_max),  # 原L1243：两轮heading坐标z都低于阈值才允许居中分。
                            dim=1,  # 原L1244：两轮heading坐标z都低于阈值才允许居中分。
                        )  # 原L1245：两轮heading坐标z都低于阈值才允许居中分。
                        reward_mask_f = reward_mask_f * wheel_z_below.float()  # 原L1246：把此条件乘到奖励mask。
                    wheel_x = wheel_pos_heading_b[:, :, 0]  # 原L1247：取两轮heading x。
                    added_reward = reward_mask_f * torch.exp(-torch.square(wheel_x) / sigma).mean(dim=1)  # 原L1248：两轮分别exp(-x²/sigma)再均值；不是到台阶落点的世界x距离。
                elif addition_type == "wheel_bottom_slip_exp":  # 原L1249：轮底水平滑移速度指数奖励。
                    reward_mask_f = self._get_contact_timer_below_mask(env, addition_cfg).float()  # 原L1250：接触计时窗口。
                    sigma = max(float(addition_cfg.get("sigma", 0.25)), 1.0e-6)  # 原L1251：水平速度平方的直接分母，兜底0.25。
                    wheel_radius = float(addition_cfg.get("wheel_radius", self._get_wheel_radius(env)))  # 原L1252：轮半径。
                    wheel_lin_vel_w = env.robot.data.body_lin_vel_w[:, env._wheel_link_idx]  # 原L1253：取轮心世界线速度。
                    wheel_ang_vel_w = env.robot.data.body_ang_vel_w[:, env._wheel_link_idx]  # 原L1254：取轮刚体世界角速度。
                    bottom_offset_w = torch.zeros_like(wheel_lin_vel_w)  # 原L1255：建立轮心到近似最低点的世界向量。
                    bottom_offset_w[..., 2] = -wheel_radius  # 原L1256：偏移量为世界竖直向下半径；未求倾斜轮的精确接触点。
                    wheel_bottom_vel_w = wheel_lin_vel_w + torch.cross(  # 原L1257：刚体点速度v_bottom=v_center+omega×offset。
                        wheel_ang_vel_w, bottom_offset_w, dim=-1  # 原L1258：刚体点速度v_bottom=v_center+omega×offset。
                    )  # 原L1259：刚体点速度v_bottom=v_center+omega×offset。
                    slip_speed = torch.linalg.norm(wheel_bottom_vel_w[..., :2], dim=-1)  # 原L1260：取该点世界xy速度范数。
                    wheel_reward = torch.exp(-torch.square(slip_speed) / sigma)  # 原L1261：滑移越小指数分越高。

                    wheel_height_threshold = addition_cfg.get("wheel_height_threshold", None)  # 原L1263：可选仅统计接近地面的轮子。
                    if wheel_height_threshold is not None:  # 原L1264：配置阈值存在。
                        wheel_heights = env._get_wheel_relative_ground_heights_raw()  # 原L1265：读逐轮相对地面高度。
                        near_ground = wheel_heights < float(wheel_height_threshold)  # 原L1266：低于阈值的轮视为近地。
                        near_ground_f = near_ground.float()  # 原L1267：转0/1mask。
                        near_ground_count = torch.clamp(near_ground_f.sum(dim=1), min=1.0)  # 原L1268：近地轮数至少按1作分母防除0。
                        added_reward = reward_mask_f * (  # 原L1269：仅对近地轮平均指数分；没有近地轮时整体给0。
                            (wheel_reward * near_ground_f).sum(dim=1) / near_ground_count  # 原L1270：仅对近地轮平均指数分；没有近地轮时整体给0。
                        ) * torch.any(near_ground, dim=1).float()  # 原L1271：仅对近地轮平均指数分；没有近地轮时整体给0。
                    else:  # 原L1272：不限制近地。
                        added_reward = reward_mask_f * wheel_reward.mean(dim=1)  # 原L1273：直接平均两轮分数。
                elif addition_type in (  # 原L1274：关节相对位置或向限位外运动的速度代价两种类型。
                    "rear2_rear1_joint_pos_limits",  # 原L1275：关节相对位置或向限位外运动的速度代价两种类型。
                    "rear2_rear1_joint_pos_limits_vel_reg",  # 原L1276：关节相对位置或向限位外运动的速度代价两种类型。
                ):  # 原L1277：关节相对位置或向限位外运动的速度代价两种类型。
                    pos_penalty, vel_penalty = self._get_rear2_rear1_joint_limit_terms(env)  # 原L1278：读取同文件辅助函数计算的两种正代价。
                    if addition_type == "rear2_rear1_joint_pos_limits":  # 原L1279：位置类型。
                        added_reward = airborne_mask_f * pos_penalty  # 原L1280：空中时返回软限位外距离和。
                    else:  # 原L1281：速度类型。
                        added_reward = airborne_mask_f * vel_penalty  # 原L1282：空中时返回向限位外高速运动的关节个数。
                else:  # 原L1283：未知type报错。
                    raise ValueError(f"Unsupported airborne reward addition type: {addition_type}")  # 原L1284：未知type报错。
            else:  # 原L1285：数值形式新增项。
                added_reward = airborne_mask_f * float(addition_cfg)  # 原L1286：空中状态给该常数。
            if term_name in reward_terms:  # 原L1287：同名普通项已存在。
                reward_terms[term_name] = reward_terms[term_name] + added_reward  # 原L1288：加到普通项上。
            else:  # 原L1289：新名字。
                reward_terms[term_name] = added_reward  # 原L1290：创建原始项。

        return reward_terms  # 原L1292：返回，后面仍要乘dt、最终权重并求和。
```

### 代价塑形

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/airborne.py`，L467–L481。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def _shape_penalty(  # 原L467：通用正代价塑形函数。
        self,  # 原L468：通用正代价塑形函数。
        value: torch.Tensor,  # 原L469：通用正代价塑形函数。
        mode: str,  # 原L470：通用正代价塑形函数。
        *,  # 原L471：通用正代价塑形函数。
        square_sigma: float = 1.0,  # 原L472：通用正代价塑形函数。
    ) -> torch.Tensor:  # 原L473：通用正代价塑形函数。
        mode = mode.lower()  # 原L474：模式名转小写。
        if mode == "binary":  # 原L475：binary模式。
            return (value > 0.0).float()  # 原L476：有正超量就给1。
        if mode == "l1":  # 原L477：L1模式。
            return value  # 原L478：直接返回超量。
        if mode == "l2":  # 原L479：L2模式。
            return square_sigma * torch.square(value)  # 原L480：square_sigma×超量²，系数不跟着平方。
        raise ValueError(f"Unsupported airborne reward penalty mode: {mode}")  # 原L481：未知mode报错。
```

### 窗口、接触与轮速辅助函数

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/airborne.py`，L493–L637。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def _get_reward_window_mask(self, env, addition_cfg: dict) -> torch.Tensor:  # 原L493：返回空中新增项有效窗口。
        active_mask = env.height_reward_airborne_state  # 原L494：从空中状态mask开始。
        max_contact_duration_s = addition_cfg.get("before_wheel_contact_duration_s", None)  # 原L495：可选触地计时达到此值前有效。
        min_contact_duration_s = addition_cfg.get("after_wheel_contact_duration_s", None)  # 原L496：可选触地计时达到此值后有效。
        require_contact_started = bool(addition_cfg.get("require_wheel_contact_timer_started", False))  # 原L497：是否要求计时至少已开始。
        if max_contact_duration_s is None and min_contact_duration_s is None and not require_contact_started:  # 原L498：三种限制都没配置。
            return active_mask  # 原L499：直接使用空中状态。

        wheel_exit_time = getattr(env, "airborne_wheel_contact_exit_time", None)  # 原L501：取每轮接触计时。
        if wheel_exit_time is None:  # 原L502：计时不存在。
            if require_contact_started or min_contact_duration_s is not None:  # 原L503：若要求已触地。
                return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)  # 原L504：没有证据就给全false。
            return active_mask  # 原L505：只要求触地前则仍用空中mask。

        contact_mode = addition_cfg.get("contact_mode", "any_wheel")  # 原L507：选择any_wheel或both_wheels。
        if contact_mode not in ("any_wheel", "both_wheels"):  # 原L508：其它模式报错。
            raise ValueError(f"Unsupported airborne reward contact_mode: {contact_mode}")  # 原L509：其它模式报错。

        def _reduce_contact_mask(contact_mask: torch.Tensor) -> torch.Tensor:  # 原L511：定义两轮布尔汇总辅助函数。
            if contact_mode == "any_wheel":  # 原L512：任一轮模式。
                return torch.any(contact_mask, dim=1)  # 原L513：两轮取any。
            return torch.all(contact_mask, dim=1)  # 原L514：否则两轮取all。

        if require_contact_started:  # 原L516：要求接触计时已开始。
            active_mask = active_mask & _reduce_contact_mask(wheel_exit_time > 0.0)  # 原L517：计时>0才进入奖励窗口；计时可暂停保留，不等于当前一定有接触力。

        if min_contact_duration_s is not None:  # 原L519：配置了最小接触时间。
            min_contact_duration_s = max(float(min_contact_duration_s), 0.0)  # 原L520：阈值至少0。
            active_mask = active_mask & _reduce_contact_mask(wheel_exit_time >= min_contact_duration_s)  # 原L521：要求计时达到阈值。

        if max_contact_duration_s is not None:  # 原L523：配置了最大接触时间。
            max_contact_duration_s = max(float(max_contact_duration_s), 0.0)  # 原L524：阈值至少0。
            stop_mask = _reduce_contact_mask(wheel_exit_time >= max_contact_duration_s)  # 原L525：任一/两轮达到停止阈值。
            active_mask = active_mask & (~stop_mask)  # 原L526：停止条件取反，与活动mask相交。

        return active_mask  # 原L528：返回窗口。

    def _get_wheel_contact_started_mask(  # 原L530：给落地项使用的接触开始窗口函数。
        self,  # 原L531：给落地项使用的接触开始窗口函数。
        env,  # 原L532：给落地项使用的接触开始窗口函数。
        addition_cfg: dict,  # 原L533：给落地项使用的接触开始窗口函数。
    ) -> torch.Tensor:  # 原L534：给落地项使用的接触开始窗口函数。
        active_mask = env.height_reward_airborne_state  # 原L535：从空中状态开始。
        wheel_exit_time = getattr(env, "airborne_wheel_contact_exit_time", None)  # 原L536：读取逐轮计时。
        if wheel_exit_time is None:  # 原L537：没有缓存给全false。
            return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)  # 原L538：没有缓存给全false。

        start_duration_s = max(  # 原L540：读取开始时长，优先start_wheel_contact_duration_s，再wheel_contact_duration_s，兜底0.02秒。
            float(  # 原L541：读取开始时长，优先start_wheel_contact_duration_s，再wheel_contact_duration_s，兜底0.02秒。
                addition_cfg.get(  # 原L542：读取开始时长，优先start_wheel_contact_duration_s，再wheel_contact_duration_s，兜底0.02秒。
                    "start_wheel_contact_duration_s",  # 原L543：读取开始时长，优先start_wheel_contact_duration_s，再wheel_contact_duration_s，兜底0.02秒。
                    addition_cfg.get("wheel_contact_duration_s", 0.02),  # 原L544：读取开始时长，优先start_wheel_contact_duration_s，再wheel_contact_duration_s，兜底0.02秒。
                )  # 原L545：读取开始时长，优先start_wheel_contact_duration_s，再wheel_contact_duration_s，兜底0.02秒。
            ),  # 原L546：读取开始时长，优先start_wheel_contact_duration_s，再wheel_contact_duration_s，兜底0.02秒。
            0.0,  # 原L547：读取开始时长，优先start_wheel_contact_duration_s，再wheel_contact_duration_s，兜底0.02秒。
        )  # 原L548：读取开始时长，优先start_wheel_contact_duration_s，再wheel_contact_duration_s，兜底0.02秒。
        contact_reached = wheel_exit_time >= start_duration_s  # 原L549：每轮计时是否达到阈值。
        contact_mode = addition_cfg.get("contact_mode", "any_wheel")  # 原L550：汇总模式。
        if contact_mode == "any_wheel":  # 原L551：任一轮满足。
            contact_started = torch.any(contact_reached, dim=1)  # 原L552：任一轮满足。
        elif contact_mode == "both_wheels":  # 原L553：两轮都满足。
            contact_started = torch.all(contact_reached, dim=1)  # 原L554：两轮都满足。
        else:  # 原L555：非法模式报错。
            raise ValueError(f"Unsupported airborne reward contact_mode: {contact_mode}")  # 原L556：非法模式报错。
        return active_mask & contact_started  # 原L557：仍需处在空中状态中才有效。

    def _get_wheel_contact_force_mask(  # 原L559：当前轮接触力阈值窗口函数。
        self,  # 原L560：当前轮接触力阈值窗口函数。
        env,  # 原L561：当前轮接触力阈值窗口函数。
        addition_cfg: dict,  # 原L562：当前轮接触力阈值窗口函数。
    ) -> torch.Tensor:  # 原L563：当前轮接触力阈值窗口函数。
        contact_force_threshold = addition_cfg.get("contact_force_threshold", None)  # 原L564：可选力阈值。
        if contact_force_threshold is None:  # 原L565：未配置力阈值则此门控全true，不意味着测得接触。
            return torch.ones(env.num_envs, dtype=torch.bool, device=env.device)  # 原L566：未配置力阈值则此门控全true，不意味着测得接触。

        contact_forces_w = self._get_current_contact_forces(env)  # 原L568：取当前力。
        if contact_forces_w is None or len(getattr(env, "_desired_contact_link_idx", [])) == 0:  # 原L569：缺数据/轮索引则全false。
            return torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)  # 原L570：缺数据/轮索引则全false。

        wheel_forces = torch.norm(contact_forces_w[:, env._desired_contact_link_idx], dim=-1)  # 原L572：每轮当前合力范数。
        contact_reached = wheel_forces > float(contact_force_threshold)  # 原L573：严格超过力阈值。
        contact_mode = addition_cfg.get("contact_mode", "any_wheel")  # 原L574：读汇总方式。
        if contact_mode == "any_wheel":  # 原L575：任一轮过阈值。
            return torch.any(contact_reached, dim=1)  # 原L576：任一轮过阈值。
        if contact_mode == "both_wheels":  # 原L577：两轮过阈值。
            return torch.all(contact_reached, dim=1)  # 原L578：两轮过阈值。
        raise ValueError(f"Unsupported airborne reward contact_mode: {contact_mode}")  # 原L579：非法方式报错。

    def _get_reward_command_lin_vel_x(self, env, addition_cfg: dict) -> torch.Tensor:  # 原L581：选奖励用的前向速度命令。
        if bool(addition_cfg.get("use_entry_command", False)):  # 原L582：配置要求使用进入空中时保存的命令。
            entry_command = getattr(env, "airborne_entry_command", None)  # 原L583：缓存存在则返回当时命令x，避免途中重采样改变评分方向。
            if entry_command is not None:  # 原L584：缓存存在则返回当时命令x，避免途中重采样改变评分方向。
                return entry_command[:, 0]  # 原L585：缓存存在则返回当时命令x，避免途中重采样改变评分方向。
        return env.command[:, 0]  # 原L586：否则用当前命令x。

    def _get_directional_wheel_speed_score(  # 原L588：返回轮速归一化score以及有效gate。
        self,  # 原L589：返回轮速归一化score以及有效gate。
        env,  # 原L590：返回轮速归一化score以及有效gate。
        addition_cfg: dict,  # 原L591：返回轮速归一化score以及有效gate。
    ) -> tuple[torch.Tensor, torch.Tensor]:  # 原L592：返回轮速归一化score以及有效gate。
        zero = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)  # 原L593：每环境0向量。
        wheel_idx = getattr(env, "_wheel_idx", [])  # 原L594：轮关节索引。
        if len(wheel_idx) == 0:  # 原L595：无轮索引则score和gate都0。
            return zero, zero  # 原L596：无轮索引则score和gate都0。

        reward_mask = self._get_reward_window_mask(env, addition_cfg)  # 原L598：先取时间/接触窗口。
        command_x = self._get_reward_command_lin_vel_x(env, addition_cfg)  # 原L599：取当前或进入时命令。
        root_vel_x = env.robot.data.root_lin_vel_b[:, 0]  # 原L600：取身体坐标根部前向速度。
        command_threshold = max(float(addition_cfg.get("command_x_threshold", 1.0)), 0.0)  # 原L601：命令方向判定阈值，至少0，兜底1m/s。
        root_vel_threshold = max(float(addition_cfg.get("root_x_threshold", 1.0)), 0.0)  # 原L602：身体实际前向速度阈值，至少0，兜底1m/s。

        positive_mask = (command_x > command_threshold) & (root_vel_x > root_vel_threshold)  # 原L604：命令和实际都足够向前。
        negative_mask = (command_x < -command_threshold) & (root_vel_x < -root_vel_threshold)  # 原L605：命令和实际都足够向后。
        direction_gate = positive_mask | negative_mask  # 原L606：允许两个同向条件中的一个。
        direction = torch.zeros_like(command_x)  # 原L607：初始化方向0。
        direction[positive_mask] = 1.0  # 原L608：前进记+1。
        direction[negative_mask] = -1.0  # 原L609：后退记-1。

        speed_start = float(addition_cfg.get("start", 0.0))  # 原L611：轮角速度评分起点，缺省0rad/s。
        speed_full = float(addition_cfg.get("full", 10.0))  # 原L612：满分轮角速度，缺省10rad/s，未直接换算成线速度匹配。
        denom = max(speed_full - speed_start, 1.0e-6)  # 原L613：区间长度保护。
        wheel_vel = env.joint_vel[:, wheel_idx]  # 原L614：取实际轮角速度。
        directional_speed = wheel_vel * direction.unsqueeze(-1)  # 原L615：乘方向，把顺行角速度变成正值。
        wheel_scores = torch.clamp((directional_speed - speed_start) / denom, 0.0, 1.0)  # 原L616：各轮按区间线性映射并截0到1。

        reduce = addition_cfg.get("reduce", "min")  # 原L618：两轮汇总方式缺省min。
        if reduce == "min":  # 原L619：取较慢轮的分数；一轮很快不能补另一轮慢。
            score = wheel_scores.min(dim=1).values  # 原L620：取较慢轮的分数；一轮很快不能补另一轮慢。
        elif reduce == "mean":  # 原L621：mean模式平均两轮。
            score = wheel_scores.mean(dim=1)  # 原L622：mean模式平均两轮。
        elif reduce == "max":  # 原L623：max模式取较快轮。
            score = wheel_scores.max(dim=1).values  # 原L624：max模式取较快轮。
        else:  # 原L625：未知汇总方式报错。
            raise ValueError(f"Unsupported directional wheel speed reduce mode: {reduce}")  # 原L626：未知汇总方式报错。

        gate_f = (reward_mask & direction_gate).float()  # 原L628：时间窗与同向门控同时满足才gate1。
        return gate_f * score, gate_f  # 原L629：score已乘gate，另返回gate供shortfall使用。

    def _get_leg_lengths(self, env) -> torch.Tensor:  # 原L631：从heading相对轮位置范数得到逐腿长度；辅助函数已把y置0，实际是平面投影长度。
        _, _, wheel_pos_heading_b, _, _ = env._get_root_quat_inv_and_wheel_pos_b()  # 原L632：从heading相对轮位置范数得到逐腿长度；辅助函数已把y置0，实际是平面投影长度。
        return torch.norm(wheel_pos_heading_b, dim=-1)  # 原L633：从heading相对轮位置范数得到逐腿长度；辅助函数已把y置0，实际是平面投影长度。

    def _get_wheel_bottom_relative_to_base_z(self, env) -> torch.Tensor:  # 原L635：轮心世界z减半径再减rootz，得到近似轮底相对身体竖直距离。
        wheel_bottom_z = env.robot.data.body_pos_w[:, env._wheel_link_idx, 2] - self._get_wheel_radius(env)  # 原L636：轮心世界z减半径再减rootz，得到近似轮底相对身体竖直距离。
        return wheel_bottom_z - env.robot.data.root_pos_w[:, 2].unsqueeze(-1)  # 原L637：轮心世界z减半径再减rootz，得到近似轮底相对身体竖直距离。
```

### 接触计时上限与关节软限位

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/airborne.py`，L639–L710。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def _get_contact_timer_below_mask(  # 原L639：用于轮居中/滑移的接触计时上限窗口。
        self,  # 原L640：用于轮居中/滑移的接触计时上限窗口。
        env,  # 原L641：用于轮居中/滑移的接触计时上限窗口。
        addition_cfg: dict,  # 原L642：用于轮居中/滑移的接触计时上限窗口。
    ) -> torch.Tensor:  # 原L643：用于轮居中/滑移的接触计时上限窗口。
        active_mask = env.height_reward_airborne_state.clone()  # 原L644：从空中状态克隆mask。
        wheel_exit_time = getattr(env, "airborne_wheel_contact_exit_time", None)  # 原L645：取轮计时。
        if wheel_exit_time is not None:  # 原L646：缓存存在。
            wheel_duration_s = max(float(addition_cfg.get("wheel_contact_duration_s", 0.02)), 0.0)  # 原L647：轮计时上限，兜底0.02秒。
            active_mask = active_mask & torch.all(wheel_exit_time < wheel_duration_s, dim=1)  # 原L648：要求两轮计时均小于上限，相当于任一轮超上限就停止。

        base_exit_time = getattr(env, "airborne_base_contact_exit_time", None)  # 原L650：取base接触计时。
        if base_exit_time is not None:  # 原L651：缓存存在。
            base_duration_s = max(float(addition_cfg.get("base_contact_duration_s", 0.02)), 0.0)  # 原L652：base计时上限，兜底0.02秒。
            active_mask = active_mask & (base_exit_time < base_duration_s)  # 原L653：base也必须未达到上限。
        return active_mask  # 原L654：返回窗口。

    def _get_rear2_rear1_joint_limit_terms(  # 原L656：空中关节软限位位置与外向速度代价。
        self, env  # 原L657：空中关节软限位位置与外向速度代价。
    ) -> tuple[torch.Tensor, torch.Tensor]:  # 原L658：空中关节软限位位置与外向速度代价。
        zeros = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)  # 原L659：全0回退向量。
        rear2_joint_idx = getattr(env, "_rear2_joint_idx", [])  # 原L660：取rear2关节索引；需按机器模型定义理解该相对关节，不能套成我们的hip目标。
        if len(rear2_joint_idx) == 0:  # 原L661：无索引则两种代价为0。
            return zeros, zeros  # 原L662：无索引则两种代价为0。

        lower = float(getattr(env.cfg, "rear2_rear1_joint_limit_lower", -3.0 / 180.0 * torch.pi))  # 原L664：下界兜底-3度，转换成弧度。
        upper = float(getattr(env.cfg, "rear2_rear1_joint_limit_upper", 60.0 / 180.0 * torch.pi))  # 原L665：上界兜底60度。
        lower, upper = min(lower, upper), max(lower, upper)  # 原L666：保证上下界顺序。
        if upper <= lower:  # 原L667：无有效区间返回0。
            return zeros, zeros  # 原L668：无有效区间返回0。

        default_boundary_ratio = float(getattr(env.cfg, "rear2_rear1_joint_limit_boundary_ratio", 0.03))  # 原L670：总边界比例兜底0.03。
        lower_boundary_ratio = float(  # 原L671：可独立覆盖下界软边界比例。
            getattr(  # 原L672：可独立覆盖下界软边界比例。
                env.cfg,  # 原L673：可独立覆盖下界软边界比例。
                "rear2_rear1_joint_limit_lower_boundary_ratio",  # 原L674：可独立覆盖下界软边界比例。
                default_boundary_ratio,  # 原L675：可独立覆盖下界软边界比例。
            )  # 原L676：可独立覆盖下界软边界比例。
        )  # 原L677：可独立覆盖下界软边界比例。
        upper_boundary_ratio = float(  # 原L678：可独立覆盖上界软边界比例。
            getattr(  # 原L679：可独立覆盖上界软边界比例。
                env.cfg,  # 原L680：可独立覆盖上界软边界比例。
                "rear2_rear1_joint_limit_upper_boundary_ratio",  # 原L681：可独立覆盖上界软边界比例。
                default_boundary_ratio,  # 原L682：可独立覆盖上界软边界比例。
            )  # 原L683：可独立覆盖上界软边界比例。
        )  # 原L684：可独立覆盖上界软边界比例。
        lower_boundary_ratio = min(max(lower_boundary_ratio, 0.0), 0.49)  # 原L685：各比例限制0到0.49，避免软区间倒置。
        upper_boundary_ratio = min(max(upper_boundary_ratio, 0.0), 0.49)  # 原L686：各比例限制0到0.49，避免软区间倒置。
        limit_span = upper - lower  # 原L687：硬上下界跨度。
        lower_margin = limit_span * lower_boundary_ratio  # 原L688：按跨度求两端软裕量。
        upper_margin = limit_span * upper_boundary_ratio  # 原L689：按跨度求两端软裕量。
        soft_lower = lower + lower_margin  # 原L690：下软界=下界+裕量。
        soft_upper = upper - upper_margin  # 原L691：上软界=上界-裕量。

        rear2_pos = wrap_to_pi(env.joint_pos[:, rear2_joint_idx])  # 原L693：实际关节角包裹到[-pi,pi]；不是动作目标角。
        lower_over = torch.clamp(soft_lower - rear2_pos, min=0.0)  # 原L694：低于软下界的超量。
        upper_over = torch.clamp(rear2_pos - soft_upper, min=0.0)  # 原L695：高于软上界的超量。
        pos_penalty = torch.sum(lower_over + upper_over, dim=-1)  # 原L696：所有关节两端超量相加为位置代价。

        vel_threshold = max(  # 原L698：向外运动速度阈值，兜底10rad/s，至少0。
            float(getattr(env.cfg, "rear2_rear1_joint_limit_vel_threshold", 10.0)),  # 原L699：向外运动速度阈值，兜底10rad/s，至少0。
            0.0,  # 原L700：向外运动速度阈值，兜底10rad/s，至少0。
        )  # 原L701：向外运动速度阈值，兜底10rad/s，至少0。
        rear2_vel = env.joint_vel[:, rear2_joint_idx]  # 原L702：实际关节角速度。
        lower_vel_violation = (rear2_pos < soft_lower) & (rear2_vel < -vel_threshold)  # 原L703：已经低于下软界且继续足够快向下。
        upper_vel_violation = (rear2_pos > soft_upper) & (rear2_vel > vel_threshold)  # 原L704：已经高于上软界且继续足够快向上。
        vel_penalty = torch.sum(  # 原L705：数违反条件的关节数量，不是角速度平方和。
            (lower_vel_violation | upper_vel_violation).float(),  # 原L706：数违反条件的关节数量，不是角速度平方和。
            dim=-1,  # 原L707：数违反条件的关节数量，不是角速度平方和。
        )  # 原L708：数违反条件的关节数量，不是角速度平方和。

        return pos_penalty, vel_penalty  # 原L710：返回两种正代价，最终负权重才处罚。
```
