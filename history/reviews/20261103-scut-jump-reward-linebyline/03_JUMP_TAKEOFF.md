# JumpTakeoff 起跳奖励逐行注释

IDLE=0、PUSH=1、TUCK=2。此模块是可配置垂直跳跃预训练辅助；公开七月上阶模型没有启用它。所有奖励分支如下，随后解释被调用的窗口、测量和弹道函数。

同文件 L301–454 还有独立可选assist：force路径调用set_external_force_and_torque，velocity路径调用write_root_velocity_to_sim；这是物理外力/状态写入，不是奖励。要声明纯策略起跳，必须检查实际assist关闭。L574–738按弹道时间、身体高度或离地高度切换PUSH/TUCK并发出事件；并不检测轮子水平越沿。

### 全部起跳奖励分支

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/jump_takeoff.py`，L824–L1044。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def apply_reward_term_scales(  # 原L824：起跳奖励钩子，修改原始奖励项；最后总函数才乘dt和配置权重。
        self, env, reward_terms: dict[str, torch.Tensor]  # 原L825：起跳奖励钩子，修改原始奖励项；最后总函数才乘dt和配置权重。
    ) -> dict[str, torch.Tensor]:  # 原L826：起跳奖励钩子，修改原始奖励项；最后总函数才乘dt和配置权重。
        cfg = self._cfg(env)  # 原L827：取jump_takeoff配置。
        phase = env.jump_takeoff_phase  # 原L828：取每个环境当前阶段：0待机、1蹬伸、2收腿。
        active_f = (phase != self.PHASE_IDLE).float()  # 原L829：非待机的0/1mask。
        push_f = (phase == self.PHASE_PUSH).float()  # 原L830：仅蹬伸阶段的mask。
        tuck_f = (phase == self.PHASE_TUCK).float()  # 原L831：仅收腿阶段的mask。
        if not hasattr(env, "jump_takeoff_prev_vel_z"):  # 原L832：首次调用时没有上一拍垂直速度缓存。
            env.jump_takeoff_prev_vel_z = env.robot.data.root_lin_vel_w[:, 2].detach().clone()  # 原L833：用当前世界垂直速度初始化，首拍差分加速度因此为0。
        current_vel_z = env.robot.data.root_lin_vel_w[:, 2]  # 原L834：读取当前世界垂直速度，上为正。

        for term_name, scale_cfg in cfg.get("reward_scales", {}).items():  # 原L836：遍历普通奖励的阶段倍率。
            if term_name not in reward_terms:  # 原L837：待缩放的原始项不存在。
                continue  # 原L838：跳过，不能靠倍率新建该项。
            if isinstance(scale_cfg, dict):  # 原L839：倍率可按阶段写成字典。
                active_scale = float(scale_cfg.get("active", 1.0))  # 原L840：活动期缺省倍率1。
                push_scale = float(scale_cfg.get("push", active_scale))  # 原L841：蹬伸缺省沿用活动期倍率。
                tuck_scale = float(scale_cfg.get("tuck", active_scale))  # 原L842：收腿缺省沿用活动期倍率。
            else:  # 原L843：直接数值配置。
                active_scale = push_scale = tuck_scale = float(scale_cfg)  # 原L844：活动、蹬伸、收腿全部用同一倍率。
            scale = torch.ones(env.num_envs, dtype=torch.float, device=env.device)  # 原L845：每个环境先给倍率1。
            scale = torch.where(active_f.bool(), torch.full_like(scale, active_scale), scale)  # 原L846：活动环境换成active_scale。
            scale = torch.where(push_f.bool(), torch.full_like(scale, push_scale), scale)  # 原L847：蹬伸环境再覆盖push_scale。
            scale = torch.where(tuck_f.bool(), torch.full_like(scale, tuck_scale), scale)  # 原L848：收腿环境再覆盖tuck_scale。
            reward_terms[term_name] = reward_terms[term_name] * scale  # 原L849：应用到原始奖励，不直接操作最终总分。

        addition_items = []  # 原L851：建立本次要算的新增奖励列表。
        for term_name, addition_cfg in cfg.get("reward_additions", {}).items():  # 原L852：读取跨阶段的新增项。
            addition_items.append((term_name, addition_cfg, active_f))  # 原L853：这些项默认在整个活动期有效。
        for phase_name, phase_mask in (("push", push_f), ("tuck", tuck_f)):  # 原L854：依次遍历蹬伸和收腿两阶段。
            phase_cfg = cfg.get(phase_name, {})  # 原L855：取该阶段配置。
            for term_name, addition_cfg in phase_cfg.get("reward_additions", {}).items():  # 原L856：取阶段新增项。
                addition_items.append((term_name, addition_cfg, phase_mask))  # 原L857：给它附上对应阶段mask；同名多项后面可累加。

        for term_name, addition_cfg, default_mask in addition_items:  # 原L859：逐条计算配置与默认mask。
            if not isinstance(addition_cfg, dict):  # 原L860：配置直接是数字。
                added_reward = default_mask * float(addition_cfg)  # 原L861：数字乘阶段mask就是该项原始值。
            else:  # 原L862：字典配置。
                default_mask = self._get_reward_addition_mask(env, cfg, addition_cfg, default_mask)  # 原L863：允许window改写默认mask，具体窗口见后面函数。
                addition_type = addition_cfg.get("type", "constant")  # 原L864：读取type，缺省constant。
                if addition_type == "constant":  # 原L865：活动期常数类型。
                    added_reward = default_mask * float(addition_cfg.get("value", 0.0))  # 原L866：给mask×value，缺省value0。
                elif addition_type == "takeoff_vel_z":  # 原L867：向上速度类型。
                    vel_z = torch.clamp(current_vel_z, min=0.0)  # 原L868：仅保留当前垂直速度正值，下落给0。
                    max_vel = addition_cfg.get("max", None)  # 原L869：读取可选速度奖励上限。
                    if max_vel is not None:  # 原L870：设置了上限。
                        vel_z = torch.clamp(vel_z, max=float(max_vel))  # 原L871：截断向上速度，避免无限追高速度。
                    added_reward = default_mask * vel_z  # 原L872：乘当前奖励窗口；若最终正权重，鼓励窗口中向上。
                elif addition_type == "upward_accel_z":  # 原L873：正向垂直加速度类型。
                    accel_z = torch.clamp(  # 原L874：开始算非负加速度。
                        (current_vel_z - env.jump_takeoff_prev_vel_z) / max(env.step_dt, 1.0e-6),  # 原L875：用相邻控制拍世界vz差除控制dt，不是减去重力后的推力加速度。
                        min=0.0,  # 原L876：向下加速度给0。
                    )  # 原L877：闭合上面的跨行表达式；不另产生奖励。
                    max_accel = addition_cfg.get("max", None)  # 原L878：可选加速度奖励上限。
                    if max_accel is not None:  # 原L879：配置了上限。
                        accel_z = torch.clamp(accel_z, max=float(max_accel))  # 原L880：把正加速度截到max_accel。
                    added_reward = default_mask * accel_z  # 原L881：窗口内返回该非负加速度。
                elif addition_type == "push_max_vel_z":  # 原L882：蹬伸期已达到的最大向上速度。
                    max_vel_z = env.jump_takeoff_push_max_vel_z  # 原L883：读取运行期维护的历史最大值，而不是当前速度。
                    max_vel = addition_cfg.get("max", None)  # 原L884：可选最大值上限。
                    if max_vel is not None:  # 原L885：上限存在。
                        max_vel_z = torch.clamp(max_vel_z, max=float(max_vel))  # 原L886：截断最大速度。
                    added_reward = default_mask * max_vel_z  # 原L887：在窗口中重复使用已达到的最大值；未必仅在离地瞬间给一次。
                elif addition_type == "push_release_vel_z_threshold":  # 原L888：释放速度超过参考的奖励。
                    margin = float(addition_cfg.get("margin", 0.0))  # 原L889：超出参考后再留一段margin。
                    max_bonus = addition_cfg.get("max", None)  # 原L890：可选奖励上限。
                    exceed = torch.clamp(  # 原L891：开始计算参考之上的超量。
                        env.jump_takeoff_push_max_vel_z - env.jump_takeoff_ref_release_vel_z - margin,  # 原L892：蹬伸最大速度减弹道参考释放速度再减margin。
                        min=0.0,  # 原L893：没有超过则0，不处罚不足。
                    )  # 原L894：闭合上面的跨行表达式；不另产生奖励。
                    if bool(addition_cfg.get("normalized", False)):  # 原L895：可选无量纲归一化。
                        exceed = exceed / torch.clamp(env.jump_takeoff_ref_release_vel_z, min=1.0e-6)  # 原L896：除参考释放速度，分母保护为至少1e-6。
                    if max_bonus is not None:  # 原L897：配置了上限。
                        exceed = torch.clamp(exceed, max=float(max_bonus))  # 原L898：截断超量奖励。
                    event = addition_cfg.get("event", "tuck")  # 原L899：读取触发时机，缺省tuck事件。
                    if event == "tuck":  # 原L900：选择收腿开始的单步事件。
                        reward_mask = env.jump_takeoff_tuck_event.float()  # 原L901：收腿事件为1才给分；它直接替换前面的default_mask。
                    elif event == "window":  # 原L902：选择整个窗口重复奖励。
                        reward_mask = default_mask  # 原L903：采用前面的window或阶段mask。
                    else:  # 原L904：其它event非法。
                        raise ValueError(f"Unsupported push_release_vel_z_threshold event: {event}")  # 原L905：抛出配置错误。
                    added_reward = reward_mask * exceed  # 原L906：事件/窗口mask乘速度超量。
                elif addition_type == "release_vel_z_shortfall":  # 原L907：释放速度不足的代价。
                    offset = max(float(addition_cfg.get("offset", 0.0)), 0.0)  # 原L908：免罚不足带宽offset，至少0。
                    max_penalty = addition_cfg.get("max", None)  # 原L909：可选代价上限。
                    measured_vel_z = env.robot.data.root_lin_vel_w[:, 2]  # 原L910：默认先取当前世界vz。
                    if addition_cfg.get("measure", "push_max") == "push_max":  # 原L911：measure缺省push_max。
                        measured_vel_z = env.jump_takeoff_push_max_vel_z  # 原L912：在push_max模式下改为整个蹬伸期最大vz。
                    shortfall = torch.clamp(  # 原L913：构造速度不足量。
                        env.jump_takeoff_ref_release_vel_z - measured_vel_z - offset,  # 原L914：参考速度-测得速度-offset。
                        min=0.0,  # 原L915：只罚不足，超过参考不给负代价。
                    )  # 原L916：闭合上面的跨行表达式；不另产生奖励。
                    if bool(addition_cfg.get("normalized", False)):  # 原L917：可选按参考速度归一化。
                        shortfall = shortfall / torch.clamp(env.jump_takeoff_ref_release_vel_z, min=1.0e-6)  # 原L918：除参考速度，保护分母。
                    if max_penalty is not None:  # 原L919：可选上限存在。
                        shortfall = torch.clamp(shortfall, max=float(max_penalty))  # 原L920：截断代价。
                    added_reward = default_mask * shortfall  # 原L921：返回窗口内正的不足量；最终负权重才在惩罚。
                elif addition_type == "release_vel_z_tracking_l1":  # 原L922：释放速度L1追踪。
                    offset = max(float(addition_cfg.get("offset", 0.0)), 0.0)  # 原L923：速度绝对误差的免罚区间。
                    error = torch.abs(env.robot.data.root_lin_vel_w[:, 2] - env.jump_takeoff_ref_release_vel_z)  # 原L924：当前世界vz与参考释放速度的绝对差。
                    added_reward = default_mask * torch.clamp(error - offset, min=0.0)  # 原L925：误差超过offset的部分才返回正代价。
                elif addition_type == "release_vel_z_tracking_exp":  # 原L926：释放速度指数追踪。
                    sigma = max(float(addition_cfg.get("sigma", 1.0)), 1.0e-6)  # 原L927：误差平方的直接分母，缺省1。
                    error = env.robot.data.root_lin_vel_w[:, 2] - env.jump_takeoff_ref_release_vel_z  # 原L928：当前vz减参考释放速度。
                    added_reward = default_mask * torch.exp(-torch.square(error) / sigma)  # 原L929：窗口内误差越小奖励越接近1。
                elif addition_type == "push_height_tracking_exp":  # 原L930：蹬伸阶段高度指数追踪。
                    ref_height, _ = self._get_ballistic_push_reference(env, cfg)  # 原L931：调用弹道蹬伸参考函数取本时刻参考高度。
                    body_height = self._get_body_relative_height(env)  # 原L932：实际身体高度=rootz-ground_z_est，不是轮底净空。
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L933：直接分母sigma缺省0.01。
                    added_reward = default_mask * torch.exp(  # 原L934：窗口内给指数奖励。
                        -torch.square(body_height - ref_height) / sigma  # 原L935：实际高度与参考高度的平方误差。
                    )  # 原L936：闭合上面的跨行表达式；不另产生奖励。
                elif addition_type == "push_vel_z_tracking_exp":  # 原L937：蹬伸阶段垂直速度追踪。
                    _, ref_vel_z = self._get_ballistic_push_reference(env, cfg)  # 原L938：从同一个参考函数取参考vz。
                    sigma = max(float(addition_cfg.get("sigma", 1.0)), 1.0e-6)  # 原L939：直接分母sigma缺省1。
                    error = env.robot.data.root_lin_vel_w[:, 2] - ref_vel_z  # 原L940：当前世界vz与蹬伸参考vz之差。
                    added_reward = default_mask * torch.exp(-torch.square(error) / sigma)  # 原L941：窗口内指数追踪分。
                elif addition_type == "peak_height_tracking_exp":  # 原L942：本次跳跃最高身体高度追踪。
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L943：直接分母sigma缺省0.01。
                    error = env.jump_takeoff_episode_max_height - env.jump_takeoff_ref_target_height  # 原L944：已达到的最高身体相对地面高度减目标峰值；不代表轮子达到目标。
                    reward_mask = default_mask  # 原L945：先用默认奖励窗口。
                    event = addition_cfg.get("event", "exit")  # 原L946：event缺省exit。
                    if event == "exit":  # 原L947：选择起跳状态退出事件。
                        reward_mask = env.jump_takeoff_exit_event.float()  # 原L948：只在退出这一拍算峰值分；此事件mask替换default_mask。
                    elif event == "active":  # 原L949：选择活动期持续计算。
                        reward_mask = default_mask  # 原L950：保留默认窗口。
                    else:  # 原L951：非法事件。
                        raise ValueError(f"Unsupported peak_height_tracking_exp event: {event}")  # 原L952：抛出错误。
                    added_reward = reward_mask * torch.exp(-torch.square(error) / sigma)  # 原L953：峰值越靠近目标分越高；超过目标同样会降分。
                elif addition_type == "height_tracking_exp":  # 原L954：身体高度追踪当前jump命令。
                    body_height = self._get_body_relative_height(env)  # 原L955：读取身体相对估计地面高度。
                    target_height = env.jump_takeoff_height_cmd  # 原L956：目标取jump_takeoff_height_cmd。
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L957：指数直接分母。
                    added_reward = default_mask * torch.exp(  # 原L958：窗口内给高度追踪分。
                        -torch.square(body_height - target_height) / sigma  # 原L959：实际身体高度减该命令的平方误差。
                    )  # 原L960：闭合上面的跨行表达式；不另产生奖励。
                elif addition_type == "trajectory_height_tracking_exp":  # 原L961：轨迹高度追踪分支。
                    body_height = self._get_body_relative_height(env)  # 原L962：实际身体相对地面高度。
                    if bool(addition_cfg.get("use_ballistic_reference", False)):  # 原L963：可选显式弹道参考。
                        target_height, _, _ = self._get_ballistic_reference(env, cfg)  # 原L964：开启时计算垂直弹道目标高度。
                    else:  # 原L965：不使用弹道参考时。
                        target_height = env.jump_takeoff_height_cmd  # 原L966：目标仍是jump_takeoff_height_cmd，不凭函数名假定在追抛物线。
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L967：指数分母，缺省0.01。
                    added_reward = default_mask * torch.exp(  # 原L968：窗口内给指数分。
                        -torch.square(body_height - target_height) / sigma  # 原L969：实际与所选目标高度的平方误差。
                    )  # 原L970：闭合上面的跨行表达式；不另产生奖励。
                elif addition_type == "trajectory_vel_z_tracking_l1":  # 原L971：轨迹垂直速度L1代价。
                    offset = max(float(addition_cfg.get("offset", 0.0)), 0.0)  # 原L972：误差免罚offset。
                    error = torch.abs(env.robot.data.root_lin_vel_w[:, 2] - env.jump_takeoff_ref_vel_z)  # 原L973：当前vz与缓存jump_takeoff_ref_vel_z的绝对误差。
                    added_reward = default_mask * torch.clamp(error - offset, min=0.0)  # 原L974：只返回超过免罚带的正代价，需要负权重。
                elif addition_type == "trajectory_vel_z_tracking_exp":  # 原L975：轨迹垂直速度指数奖励。
                    sigma = max(float(addition_cfg.get("sigma", 1.0)), 1.0e-6)  # 原L976：指数直接分母。
                    if bool(addition_cfg.get("use_ballistic_reference", False)):  # 原L977：选择是否重新计算弹道参考。
                        _, target_vel_z, _ = self._get_ballistic_reference(env, cfg)  # 原L978：开启时取当前弹道参考vz。
                    else:  # 原L979：不开启。
                        target_vel_z = env.jump_takeoff_ref_vel_z  # 原L980：取状态更新中保存的参考vz。
                    error = env.robot.data.root_lin_vel_w[:, 2] - target_vel_z  # 原L981：当前世界vz减目标vz。
                    added_reward = default_mask * torch.exp(-torch.square(error) / sigma)  # 原L982：窗口内速度误差越小分越高。
                elif addition_type == "leg_retraction":  # 原L983：名为收腿的奖励族，必须结合mode与最终权重读。
                    _, _, wheel_pos_heading_b, _, _ = env._get_root_quat_inv_and_wheel_pos_b()  # 原L984：获取相对根部的heading坐标轮位置。
                    leg_lengths = torch.norm(wheel_pos_heading_b, dim=-1)  # 原L985：逐轮heading向量范数当腿长；辅助函数已把y置0，所以是平面投影长度，不是单个关节角。
                    mean_leg_length = leg_lengths.mean(dim=1)  # 原L986：左右腿长的均值。
                    target = float(addition_cfg.get("target", 0.22))  # 原L987：目标腿长缺省0.22m。
                    mode = addition_cfg.get("mode", "above_target")  # 原L988：模式缺省above_target。
                    if mode == "raw":  # 原L989：raw模式。
                        added_reward = default_mask * mean_leg_length  # 原L990：直接给平均腿长；正权重鼓励更长，负权重才鼓励更短。
                    elif mode == "above_target":  # 原L991：above_target模式。
                        added_reward = default_mask * torch.clamp(mean_leg_length - target, min=0.0)  # 原L992：平均腿长超过目标才有正代价；通常配负权重鼓励收腿。
                    elif mode == "above_target_per_leg":  # 原L993：逐腿above_target模式。
                        added_reward = default_mask * torch.clamp(leg_lengths - target, min=0.0).mean(dim=1)  # 原L994：各腿超长量先截正再均值；不会让一腿过短抵消另一腿过长。
                    elif mode == "exp":  # 原L995：exp模式。
                        sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L996：指数直接分母。
                        added_reward = default_mask * torch.exp(  # 原L997：指数追踪平均腿长。
                            -torch.square(mean_leg_length - target) / sigma  # 原L998：均值接近目标给高分，可能存在左右误差互相抵消。
                        )  # 原L999：闭合上面的跨行表达式；不另产生奖励。
                    elif mode == "exp_per_leg":  # 原L1000：逐腿指数模式。
                        sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L1001：指数直接分母。
                        added_reward = default_mask * torch.exp(  # 原L1002：给每条腿分别算指数分。
                            -torch.square(leg_lengths - target) / sigma  # 原L1003：每腿对目标误差平方。
                        ).mean(dim=1)  # 原L1004：然后左右均值，比先平均腿长更限制不对称。
                    else:  # 原L1005：非法mode。
                        raise ValueError(f"Unsupported leg_retraction reward mode: {mode}")  # 原L1006：抛出错误。
                elif addition_type == "leg_length_tracking_exp":  # 原L1007：另外一组腿长指数追踪接口。
                    _, _, wheel_pos_heading_b, _, _ = env._get_root_quat_inv_and_wheel_pos_b()  # 原L1008：取heading相对轮位置。
                    leg_lengths = torch.norm(wheel_pos_heading_b, dim=-1)  # 原L1009：算逐腿投影长度，y已在辅助函数置0。
                    target = float(addition_cfg.get("target", 0.16))  # 原L1010：目标缺省0.16m，不能与前一族0.22m混用。
                    sigma = max(float(addition_cfg.get("sigma", 0.005)), 1.0e-6)  # 原L1011：直接分母缺省0.005。
                    per_leg = bool(addition_cfg.get("per_leg", True))  # 原L1012：缺省逐腿计算。
                    if per_leg:  # 原L1013：逐腿模式。
                        error = leg_lengths - target  # 原L1014：计算每腿误差。
                        added_reward = default_mask * torch.exp(-torch.square(error) / sigma).mean(dim=1)  # 原L1015：逐腿指数后平均。
                    else:  # 原L1016：先平均模式。
                        mean_leg_length = leg_lengths.mean(dim=1)  # 原L1017：平均两腿长度。
                        added_reward = default_mask * torch.exp(  # 原L1018：对平均长度给指数分。
                            -torch.square(mean_leg_length - target) / sigma  # 原L1019：平均长度减目标的平方误差。
                        )  # 原L1020：闭合上面的跨行表达式；不另产生奖励。
                elif addition_type == "wheel_airtime":  # 原L1021：名称wheel_airtime的分支。
                    margin = max(float(addition_cfg.get("wheel_air_margin", 0.03)), 0.0)  # 原L1022：轮底高出估计地面阈值，缺省3cm。
                    added_reward = default_mask * self._get_wheel_air_mask(env, margin).float()  # 原L1023：双轮高度同时超过半径+margin则给1；没有累计飞行秒数。
                elif addition_type == "wheel_height_below_base_exp":  # 原L1024：轮底相对身体高度追踪。
                    target = float(addition_cfg.get("target", 0.22))  # 原L1025：目标轮底在身体下方多远，缺省0.22m。
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L1026：指数直接分母。
                    wheel_bottom_z = (  # 原L1027：计算近似世界轮底z。
                        env.robot.data.body_pos_w[:, env._wheel_link_idx, 2]  # 原L1028：实际轮心世界z。
                        - self._get_wheel_radius(env)  # 原L1029：减轮半径。
                    )  # 原L1030：闭合上面的跨行表达式；不另产生奖励。
                    rel_wheel_bottom_z = wheel_bottom_z - env.robot.data.root_pos_w[:, 2].unsqueeze(-1)  # 原L1031：再减身体世界z，得到每轮相对身体的竖直高度。
                    target_rel_wheel_bottom_z = -target  # 原L1032：目标设为-target，即身体下方target米。
                    added_reward = default_mask * torch.exp(  # 原L1033：窗口内给指数分。
                        -torch.square(rel_wheel_bottom_z - target_rel_wheel_bottom_z) / sigma  # 原L1034：每轮相对竖直高度的平方误差。
                    ).mean(dim=1)  # 原L1035：左右分数平均；它不直接检测台沿净空。
                else:  # 原L1036：未知type。
                    raise ValueError(f"Unsupported jump_takeoff reward addition type: {addition_type}")  # 原L1037：抛出错误。

            if term_name in reward_terms:  # 原L1039：若原始奖励里已有同名项。
                reward_terms[term_name] = reward_terms[term_name] + added_reward  # 原L1040：累加新增值。
            else:  # 原L1041：新名字。
                reward_terms[term_name] = added_reward  # 原L1042：创建原始项；最终还要经过cfg.rewards过滤。
        env.jump_takeoff_prev_vel_z.copy_(current_vel_z.detach())  # 原L1043：保存本拍vz并断开梯度，供下一拍差分加速度使用。
        return reward_terms  # 原L1044：返回原始奖励字典。
```

### 奖励使用的身体高度、腿长和离地判据

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/jump_takeoff.py`，L92–L115。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def _get_body_relative_height(self, env) -> torch.Tensor:  # 原L92：读取身体相对地面高度的辅助函数。
        return env.robot.data.root_pos_w[:, 2] - env.ground_z_est  # 原L93：root世界z减估计地面z；不是对目标台面的轮底高度。

    def _get_mean_leg_length(self, env) -> torch.Tensor:  # 原L95：获取平均腿长。
        _, _, wheel_pos_heading_b, _, _ = env._get_root_quat_inv_and_wheel_pos_b()  # 原L96：取heading坐标轮相对根位置。
        return torch.norm(wheel_pos_heading_b, dim=-1).mean(dim=1)  # 原L97：逐轮heading平面投影向量范数后左右平均，辅助函数已经将y置0。

    def _get_wheel_radius(self, env) -> float:  # 原L99：轮半径优先使用jump enter配置，再用环境高度测量半径，最后兜底0.06m。
        return float(  # 原L100：轮半径优先使用jump enter配置，再用环境高度测量半径，最后兜底0.06m。
            self._cfg(env).get("enter", {}).get(  # 原L101：轮半径优先使用jump enter配置，再用环境高度测量半径，最后兜底0.06m。
                "wheel_radius",  # 原L102：轮半径优先使用jump enter配置，再用环境高度测量半径，最后兜底0.06m。
                env._get_height_measure_wheel_radius()  # 原L103：轮半径优先使用jump enter配置，再用环境高度测量半径，最后兜底0.06m。
                if getattr(env, "_get_height_measure_wheel_radius", None) is not None  # 原L104：轮半径优先使用jump enter配置，再用环境高度测量半径，最后兜底0.06m。
                else 0.06,  # 原L105：轮半径优先使用jump enter配置，再用环境高度测量半径，最后兜底0.06m。
            )  # 原L106：轮半径优先使用jump enter配置，再用环境高度测量半径，最后兜底0.06m。
        )  # 原L107：轮半径优先使用jump enter配置，再用环境高度测量半径，最后兜底0.06m。

    def _get_wheel_air_mask(self, env, margin: float) -> torch.Tensor:  # 原L109：双轮离地高度布尔判断。
        wheel_heights = env._get_wheel_relative_ground_heights_raw()  # 原L110：读取每轮相对估计地面的轮心高度。
        wheel_radius = self._get_wheel_radius(env)  # 原L111：取半径。
        return torch.all(wheel_heights > wheel_radius + margin, dim=1)  # 原L112：要求两轮都高于半径+margin；与真实接触力为0并不等价。

    def _trajectory_enabled(self, cfg: dict) -> bool:  # 原L114：弹道模式开关。
        return bool(cfg.get("trajectory", {}).get("enabled", False))  # 原L115：trajectory.enabled缺省false；关着时后面的弹道状态更新不运行。
```

### 奖励使用的两种弹道参考

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/jump_takeoff.py`，L168–L267。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def _get_ballistic_push_reference(  # 原L168：返回蹬伸期的参考高度与参考vz。
        self, env, cfg: dict  # 原L169：返回蹬伸期的参考高度与参考vz。
    ) -> tuple[torch.Tensor, torch.Tensor]:  # 原L170：返回蹬伸期的参考高度与参考vz。
        traj_cfg = cfg.get("trajectory", {})  # 原L171：取垂直轨迹配置。
        gravity = max(float(traj_cfg.get("gravity", 9.81)), 1.0e-6)  # 原L172：参考重力加速度，至少1e-6，兜底9.81。
        push_start_height = float(traj_cfg.get("push_start_height", 0.20))  # 原L173：蹬伸起始身体相对地面高度，兜底0.20m。
        release_height = float(traj_cfg.get("release_height", 0.38))  # 原L174：释放高度，兜底0.38m。
        peak_height = env.jump_takeoff_ref_target_height  # 原L175：取每环境采样的目标峰值高度。
        timing_mode = traj_cfg.get("tuck_timing_mode", "dynamic_push_time")  # 原L176：选择固定收腿时间或动态蹬伸时长。
        if timing_mode == "fixed_tuck_time":  # 原L177：固定时长模式。
            push_time = torch.full_like(  # 原L178：蹬伸时长固定为配置值，兜底0.14秒且至少一个控制dt。
                peak_height, max(float(traj_cfg.get("fixed_tuck_time_s", 0.14)), env.step_dt)  # 原L179：蹬伸时长固定为配置值，兜底0.14秒且至少一个控制dt。
            )  # 原L180：蹬伸时长固定为配置值，兜底0.14秒且至少一个控制dt。
            discriminant = torch.square(gravity * push_time) + 8.0 * gravity * torch.clamp(  # 原L181：根据峰值与起点构造求解释放速度的一元二次式判别量。
                peak_height - push_start_height, min=0.0  # 原L182：根据峰值与起点构造求解释放速度的一元二次式判别量。
            )  # 原L183：根据峰值与起点构造求解释放速度的一元二次式判别量。
            release_vel_z = 0.5 * (-gravity * push_time + torch.sqrt(discriminant))  # 原L184：解正根得到初步释放速度。
            raw_release_height = push_start_height + 0.5 * release_vel_z * push_time  # 原L185：按从静止匀加速的平均速度估计释放高度。
            max_release_height = float(traj_cfg.get("max_release_height", release_height))  # 原L186：取释放高度上限。
            release_height_for_flight = torch.clamp(raw_release_height, max=max_release_height)  # 原L187：将估计释放高度限制到上限。
            release_vel_z = torch.sqrt(  # 原L188：再按剩余飞行高度v=sqrt(2gΔh)重新计算释放速度；这是参考生成，不是动力学可达性证明。
                torch.clamp(2.0 * gravity * (peak_height - release_height_for_flight), min=0.0)  # 原L189：再按剩余飞行高度v=sqrt(2gΔh)重新计算释放速度；这是参考生成，不是动力学可达性证明。
            )  # 原L190：再按剩余飞行高度v=sqrt(2gΔh)重新计算释放速度；这是参考生成，不是动力学可达性证明。
        else:  # 原L191：动态时长模式。
            flight_peak_time = torch.sqrt(  # 原L192：从释放高度到峰值的上升时间sqrt(2Δh/g)。
                torch.clamp(2.0 * (peak_height - release_height) / gravity, min=0.0)  # 原L193：从释放高度到峰值的上升时间sqrt(2Δh/g)。
            )  # 原L194：从释放高度到峰值的上升时间sqrt(2Δh/g)。
            release_vel_z = gravity * flight_peak_time  # 原L195：释放速度=g×到峰值时间。
            push_distance = max(release_height - push_start_height, 0.0)  # 原L196：非负蹬伸距离。
            push_time = torch.where(  # 原L197：匀加速从静止模型下push_time=2×distance/v；速度很小时给0。
                release_vel_z > 1.0e-6,  # 原L198：匀加速从静止模型下push_time=2×distance/v；速度很小时给0。
                2.0 * push_distance / release_vel_z,  # 原L199：匀加速从静止模型下push_time=2×distance/v；速度很小时给0。
                torch.zeros_like(release_vel_z),  # 原L200：匀加速从静止模型下push_time=2×distance/v；速度很小时给0。
            )  # 原L201：匀加速从静止模型下push_time=2×distance/v；速度很小时给0。
        push_accel = torch.where(  # 原L202：参考蹬伸加速度=v_release/push_time，零时长保护。
            push_time > 1.0e-6,  # 原L203：参考蹬伸加速度=v_release/push_time，零时长保护。
            release_vel_z / push_time,  # 原L204：参考蹬伸加速度=v_release/push_time，零时长保护。
            torch.zeros_like(release_vel_z),  # 原L205：参考蹬伸加速度=v_release/push_time，零时长保护。
        )  # 原L206：参考蹬伸加速度=v_release/push_time，零时长保护。
        push_elapsed = torch.clamp(env.jump_takeoff_phase_time, min=0.0)  # 原L207：已过时间截为非负。
        push_elapsed = torch.minimum(push_elapsed, torch.clamp(push_time, min=0.0))  # 原L208：限制在蹬伸时间段内。
        ref_height = push_start_height + 0.5 * push_accel * torch.square(push_elapsed)  # 原L209：h_ref=h_start+0.5*a*t²。
        ref_vel_z = push_accel * push_elapsed  # 原L210：vz_ref=a*t。
        return ref_height, ref_vel_z  # 原L211：返回两条垂直参考，没有水平落点或轮台接触规划。

    def _get_ballistic_reference(  # 原L213：返回完整蹬伸+抛物飞行参考高度、vz与蹬伸时长。
        self, env, cfg: dict  # 原L214：返回完整蹬伸+抛物飞行参考高度、vz与蹬伸时长。
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:  # 原L215：返回完整蹬伸+抛物飞行参考高度、vz与蹬伸时长。
        traj_cfg = cfg.get("trajectory", {})  # 原L216：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
        gravity = max(float(traj_cfg.get("gravity", 9.81)), 1.0e-6)  # 原L217：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
        push_start_height = float(traj_cfg.get("push_start_height", 0.20))  # 原L218：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
        release_height = float(traj_cfg.get("release_height", 0.38))  # 原L219：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
        peak_height = env.jump_takeoff_ref_target_height  # 原L220：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
        timing_mode = traj_cfg.get("tuck_timing_mode", "dynamic_push_time")  # 原L221：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
        if timing_mode == "fixed_tuck_time":  # 原L222：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
            push_time = torch.full_like(  # 原L223：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
                peak_height, max(float(traj_cfg.get("fixed_tuck_time_s", 0.14)), env.step_dt)  # 原L224：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
            )  # 原L225：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
            discriminant = torch.square(gravity * push_time) + 8.0 * gravity * torch.clamp(  # 原L226：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
                peak_height - push_start_height, min=0.0  # 原L227：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
            )  # 原L228：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
            release_vel_z = 0.5 * (-gravity * push_time + torch.sqrt(discriminant))  # 原L229：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
            raw_release_height = push_start_height + 0.5 * release_vel_z * push_time  # 原L230：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
            max_release_height = float(traj_cfg.get("max_release_height", release_height))  # 原L231：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
            release_height_for_flight = torch.clamp(raw_release_height, max=max_release_height)  # 原L232：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
            release_vel_z = torch.sqrt(  # 原L233：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
                torch.clamp(2.0 * gravity * (peak_height - release_height_for_flight), min=0.0)  # 原L234：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
            )  # 原L235：与上一函数同样的固定时间求解，读取峰值、起点、释放高度、重力并修正释放高度上限。
        else:  # 原L236：动态蹬伸时间分支。
            flight_peak_time = torch.sqrt(  # 原L237：由目标峰值-释放高度求到峰值时间与释放速度。
                torch.clamp(2.0 * (peak_height - release_height) / gravity, min=0.0)  # 原L238：由目标峰值-释放高度求到峰值时间与释放速度。
            )  # 原L239：由目标峰值-释放高度求到峰值时间与释放速度。
            release_vel_z = gravity * flight_peak_time  # 原L240：由目标峰值-释放高度求到峰值时间与释放速度。
            push_distance = max(release_height - push_start_height, 0.0)  # 原L241：由蹬伸距离和释放速度算动态蹬伸时长。
            push_time = torch.where(  # 原L242：由蹬伸距离和释放速度算动态蹬伸时长。
                release_vel_z > 1.0e-6,  # 原L243：由蹬伸距离和释放速度算动态蹬伸时长。
                2.0 * push_distance / release_vel_z,  # 原L244：由蹬伸距离和释放速度算动态蹬伸时长。
                torch.zeros_like(release_vel_z),  # 原L245：由蹬伸距离和释放速度算动态蹬伸时长。
            )  # 原L246：由蹬伸距离和释放速度算动态蹬伸时长。
            release_height_for_flight = torch.full_like(peak_height, release_height)  # 原L247：动态模式的飞行起点高度取配置release_height。

        push_accel = torch.where(  # 原L249：参考匀加速度，带零时长保护。
            push_time > 1.0e-6,  # 原L250：参考匀加速度，带零时长保护。
            release_vel_z / push_time,  # 原L251：参考匀加速度，带零时长保护。
            torch.zeros_like(release_vel_z),  # 原L252：参考匀加速度，带零时长保护。
        )  # 原L253：参考匀加速度，带零时长保护。
        elapsed = torch.clamp(env.jump_takeoff_phase_time, min=0.0)  # 原L254：当前起跳状态经过时间，不是仿真绝对时间。
        push_elapsed = torch.minimum(elapsed, torch.clamp(push_time, min=0.0))  # 原L255：蹬伸内时间截断。
        push_height = push_start_height + 0.5 * push_accel * torch.square(push_elapsed)  # 原L256：匀加速参考高度。
        push_vel_z = push_accel * push_elapsed  # 原L257：匀加速参考vz。
        flight_elapsed = torch.clamp(elapsed - push_time, min=0.0)  # 原L258：飞行阶段时间=max(elapsed-push_time,0)。
        flight_height = (  # 原L259：飞行高度=h_release+v_release*t-0.5*g*t²。
            release_height_for_flight  # 原L260：飞行高度=h_release+v_release*t-0.5*g*t²。
            + release_vel_z * flight_elapsed  # 原L261：飞行高度=h_release+v_release*t-0.5*g*t²。
            - 0.5 * gravity * torch.square(flight_elapsed)  # 原L262：飞行高度=h_release+v_release*t-0.5*g*t²。
        )  # 原L263：飞行高度=h_release+v_release*t-0.5*g*t²。
        flight_vel_z = release_vel_z - gravity * flight_elapsed  # 原L264：飞行vz=v_release-g*t。
        ref_height = torch.where(elapsed <= push_time, push_height, flight_height)  # 原L265：时间尚未过push_time选蹬伸高度，否则选飞行高度。
        ref_vel_z = torch.where(elapsed <= push_time, push_vel_z, flight_vel_z)  # 原L266：同样选择vz。
        return ref_height, ref_vel_z, push_time  # 原L267：返回参考；此函数本身既不写仿真速度也不控制电机。
```

### 新增奖励窗口的全部分支

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/jump_takeoff.py`，L269–L299。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def _get_reward_addition_mask(  # 原L269：根据新增项window选择生效窗口，可能覆盖原阶段mask。
        self,  # 原L270：根据新增项window选择生效窗口，可能覆盖原阶段mask。
        env,  # 原L271：根据新增项window选择生效窗口，可能覆盖原阶段mask。
        cfg: dict,  # 原L272：根据新增项window选择生效窗口，可能覆盖原阶段mask。
        addition_cfg: dict,  # 原L273：根据新增项window选择生效窗口，可能覆盖原阶段mask。
        default_mask: torch.Tensor,  # 原L274：根据新增项window选择生效窗口，可能覆盖原阶段mask。
    ) -> torch.Tensor:  # 原L275：根据新增项window选择生效窗口，可能覆盖原阶段mask。
        window = addition_cfg.get("window", None)  # 原L276：读取window名称。
        if window is None:  # 原L277：未显式设置窗口。
            return default_mask  # 原L278：沿用默认活动/蹬伸/收腿mask。
        phase = env.jump_takeoff_phase  # 原L279：读取当前阶段。
        if window == "active":  # 原L280：active窗口。
            return (phase != self.PHASE_IDLE).float()  # 原L281：所有非待机环境有效。
        if window == "push":  # 原L282：push窗口。
            return (phase == self.PHASE_PUSH).float()  # 原L283：仅蹬伸阶段。
        if window == "tuck":  # 原L284：tuck窗口。
            return (phase == self.PHASE_TUCK).float()  # 原L285：仅收腿阶段。
        if window == "pre_release":  # 原L286：pre_release窗口。
            release_height = float(cfg.get("trajectory", {}).get("release_height", 0.38))  # 原L287：取释放身体高度。
            body_height = self._get_body_relative_height(env)  # 原L288：读当前身体相对估计地面高度。
            return ((phase == self.PHASE_PUSH) & (body_height < release_height)).float()  # 原L289：蹬伸且身体低于释放高度，未使用真实轮接触定义释放。
        if window == "post_release":  # 原L290：post_release窗口。
            release_height = float(cfg.get("trajectory", {}).get("release_height", 0.38))  # 原L291：同样读释放高度和当前身体高度。
            body_height = self._get_body_relative_height(env)  # 原L292：同样读释放高度和当前身体高度。
            return ((phase != self.PHASE_IDLE) & (body_height >= release_height)).float()  # 原L293：活动且身体达到释放高度；这也不等于已真实离地。
        _, _, push_time = self._get_ballistic_reference(env, cfg)  # 原L294：剩余窗口需算参考蹬伸时长。
        if window == "push_accel":  # 原L295：push_accel窗口。
            return ((phase == self.PHASE_PUSH) & (env.jump_takeoff_phase_time <= push_time)).float()  # 原L296：蹬伸阶段且计时尚未过参考蹬伸时长。
        if window == "rise_to_tuck":  # 原L297：rise_to_tuck窗口。
            return ((phase == self.PHASE_PUSH) & (env.jump_takeoff_phase_time > push_time)).float()  # 原L298：仍在蹬伸阶段且计时已过参考蹬伸时长。
        raise ValueError(f"Unsupported jump_takeoff reward addition window: {window}")  # 原L299：未知窗口直接报错。
```
