# Stair 上阶奖励逐行注释

这里讲模块实现，不宣称公开七月模型启用它。先看奖励函数，再追事件来源。函数默认值和实际配置值分开解释。

### Stair 全部奖励分支

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/stair.py`，L328–L442。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def apply_reward_term_scales(  # 原L328：奖励后处理钩子：输入每个环境的原始奖励字典，输出改好的字典，尚未乘最终权重和dt。
        self, env, reward_terms: dict[str, torch.Tensor]  # 原L329：奖励后处理钩子：输入每个环境的原始奖励字典，输出改好的字典，尚未乘最终权重和dt。
    ) -> dict[str, torch.Tensor]:  # 原L330：奖励后处理钩子：输入每个环境的原始奖励字典，输出改好的字典，尚未乘最终权重和dt。
        stair_mask_f = env.wheel_forward_stair_state.float()  # 原L331：上阶状态转成0/1浮点mask，每个环境独立。
        reward_scales = self._cfg(env).get("reward_scales", {})  # 原L332：从stair配置读取普通奖励的倍率表，缺省为空。
        for term_name, boost_scale in reward_scales.items():  # 原L333：逐项取奖励名和上阶期倍率。
            if term_name not in reward_terms:  # 原L334：只缩放已经存在的原始奖励项。
                continue  # 原L335：没有该项则跳过，不凭空补出奖励。
            scale = 1.0 + stair_mask_f * (float(boost_scale) - 1.0)  # 原L336：不在上阶时倍率1；上阶时倍率boost_scale，0可暂停该项。
            reward_terms[term_name] = reward_terms[term_name] * scale  # 原L337：把倍率乘到原始项；正奖励/负权重代价都会一起被放大或缩小。

        reward_additions = self._cfg(env).get("reward_additions", {})  # 原L339：读取要额外增加的上阶奖励定义。
        for term_name, addition_cfg in reward_additions.items():  # 原L340：逐个处理新增项。
            if isinstance(addition_cfg, dict):  # 原L341：字典配置按type选择公式，数值配置走活动期常数。
                addition_type = addition_cfg.get("type", "success_event")  # 原L342：缺省类型为成功事件，不是缺省成功判定。
                if addition_type == "success_event":  # 原L343：选择成功事件分支。
                    added_reward = env.wheel_forward_stair_success_exit_event.float()  # 原L344：只有本次上阶成功退出的那一步给1，其余为0；事件来源见状态更新。
                elif addition_type == "failure_event":  # 原L345：选择失败事件分支。
                    added_reward = env.wheel_forward_stair_failure_exit_event.float()  # 原L346：失败退出给正1；要成为惩罚，需要cfg.rewards对应权重为负。
                elif addition_type == "fast_success":  # 原L347：选择越快成功越高分的事件奖励。
                    time_sigma = max(float(addition_cfg.get("time_sigma", 1.0)), 1.0e-6)  # 原L348：时间衰减分母，至少1e-6秒，缺省1秒。
                    max_reward = float(addition_cfg.get("max_reward", 1.0))  # 原L349：快速成功原始奖励的最大幅度，缺省1。
                    success_duration = max(  # 原L350：读取成功保持时间用于从计时里扣除；这里的兜底值是0，不同于状态判定处0.3秒。
                        float(self._cfg(env).get("success", {}).get("duration_s", 0.0)),  # 原L351：读取成功保持时间用于从计时里扣除；这里的兜底值是0，不同于状态判定处0.3秒。
                        0.0,  # 原L352：读取成功保持时间用于从计时里扣除；这里的兜底值是0，不同于状态判定处0.3秒。
                    )  # 原L353：读取成功保持时间用于从计时里扣除；这里的兜底值是0，不同于状态判定处0.3秒。
                    effective_success_time = torch.clamp(  # 原L354：计算真正计入快慢的有效耗时。
                        env.wheel_forward_stair_fast_success_time_event - success_duration,  # 原L355：从记录的快速成功耗时减去规定保持时间。
                        min=0.0,  # 原L356：负时间截成0，不会得到大于最大幅度的指数奖励。
                    )  # 原L357：闭合上面的跨行表达式；不另产生奖励。
                    added_reward = (  # 原L358：组装单次快速成功奖励。
                        env.wheel_forward_stair_success_exit_event.float()  # 原L359：必须发生成功退出事件。
                        * env.wheel_forward_stair_fast_success_started_event.float()  # 原L360：必须实际启动过快速计时；计时来自轮子水平接触力阈值。
                        * max_reward  # 原L361：乘用户配置的原始最大幅度。
                        * torch.exp(-effective_success_time / time_sigma)  # 原L362：有效耗时越长按exp(-t/time_sigma)衰减。
                    )  # 原L363：闭合上面的跨行表达式；不另产生奖励。
                elif addition_type == "height_track_exp":  # 原L364：选择相对台面身体高度追踪。
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L365：高度误差平方的直接分母，缺省0.01；代码没有再平方sigma。
                    height_error = (  # 原L366：开始构造有符号高度误差。
                        env.robot.data.root_pos_w[:, 2]  # 原L367：机器人根部世界z。
                        - env.wheel_forward_stair_reference_height  # 原L368：减扫描时锁定的台面世界高度。
                        - env.wheel_forward_stair_height_cmd  # 原L369：再减期望的身体相对台面高度，目标不是台阶高度本身。
                    )  # 原L370：闭合上面的跨行表达式；不另产生奖励。
                    if bool(addition_cfg.get("only_below_target", False)):  # 原L371：可选仅惩罚低于目标。
                        height_error = torch.clamp(height_error, max=0.0)  # 原L372：把正误差变0；高过目标也拿满分，低于目标才扣分。
                    added_reward = env.wheel_forward_stair_state.float() * torch.exp(  # 原L373：只在上阶状态给指数分。
                        -torch.square(height_error) / sigma  # 原L374：误差平方越小分越高，正负误差在默认模式下对称。
                    )  # 原L375：闭合上面的跨行表达式；不另产生奖励。
                elif addition_type == "height_progress":  # 原L376：选择每步上升进度。
                    max_progress = max(float(addition_cfg.get("max_progress", 0.05)), 1.0e-6)  # 原L377：单步进度归一化上限，缺省5cm，不是要求台高5cm。
                    progress = torch.clamp(  # 原L378：截断已保存的单步身体抬升量。
                        env.wheel_forward_stair_body_relative_height_progress,  # 原L379：此量在状态更新中按本步相对台面高度减上步计算，并仅保留正增量。
                        min=0.0,  # 原L380：下降给0；此分支自身不扣下降分。
                        max=max_progress,  # 原L381：每步最多按max_progress计分。
                    )  # 原L382：闭合上面的跨行表达式；不另产生奖励。
                    added_reward = env.wheel_forward_stair_state.float() * (progress / max_progress)  # 原L383：上阶mask乘归一化进度，取值0到1；不是除dt的垂直速度。
                elif addition_type == "wheel_above_reference_height":  # 原L384：选择轮子高于扫描台面参考的奖励。
                    margin = float(addition_cfg.get("margin", 0.0))  # 原L385：要求额外超过参考高度的margin，缺省0。
                    sigma = max(float(addition_cfg.get("sigma", 0.01)), 1.0e-6)  # 原L386：缺省指数模式的高度误差平方分母。
                    wheel_z = env.robot.data.body_pos_w[:, env._wheel_link_idx, 2]  # 原L387：取两轮刚体中心世界z，形状[N,2]。
                    if bool(addition_cfg.get("use_wheel_bottom", False)):  # 原L388：配置允许把轮心改成近似轮底高度。
                        wheel_z = wheel_z - self._get_wheel_radius(env)  # 原L389：若启用则减轮半径；这是竖直半径近似，不是完整旋转轮胎几何最低点。
                    wheel_height_error = wheel_z - env.wheel_forward_stair_reference_height.unsqueeze(-1) - margin  # 原L390：每轮高度减台面参考和margin；负数表示不够高。
                    if bool(addition_cfg.get("exp", True)):  # 原L391：默认使用指数映射。
                        per_wheel_reward = torch.exp(-torch.square(torch.clamp(wheel_height_error, max=0.0)) / sigma)  # 原L392：只平方负的高度不足量；达到高度后基础分饱和为1，不惩罚继续抬高。
                    else:  # 原L393：非指数分支。
                        max_error = max(float(addition_cfg.get("max_error", 0.2)), 1.0e-6)  # 原L394：线性分的最大不足量，缺省20cm。
                        per_wheel_reward = 1.0 - torch.clamp(-wheel_height_error, min=0.0, max=max_error) / max_error  # 原L395：高度不足从0到max_error时，分数由1线性降到0。
                    above_bonus_scale = float(addition_cfg.get("above_bonus_scale", 0.0))  # 原L396：可选超过目标后的额外奖励系数，缺省0关闭。
                    if above_bonus_scale != 0.0:  # 原L397：非零时才计算额外超过高度的分。
                        above_bonus_margin = max(float(addition_cfg.get("above_bonus_margin", 0.05)), 1.0e-6)  # 原L398：每above_bonus_margin高度对应一个归一化单位，缺省5cm。
                        above_bonus_max = max(float(addition_cfg.get("above_bonus_max", 1.0)), 0.0)  # 原L399：额外奖励归一化值上限，至少0，缺省1。
                        above_bonus = torch.clamp(  # 原L400：截断额外越高分。
                            torch.clamp(wheel_height_error, min=0.0) / above_bonus_margin,  # 原L401：只奖励高于参考部分，并除额外高度尺度。
                            max=above_bonus_max,  # 原L402：限制额外归一化高度的最大值。
                        )  # 原L403：闭合上面的跨行表达式；不另产生奖励。
                        per_wheel_reward = per_wheel_reward + above_bonus_scale * above_bonus  # 原L404：把基础分与可选超过高度分相加。
                    added_reward = env.wheel_forward_stair_state.float() * per_wheel_reward.mean(dim=1)  # 原L405：两轮取平均再乘上阶mask；平均分不是双轮都过高度的逻辑AND。
                elif addition_type == "wheel_xy_contact_force":  # 原L406：选择轮子水平接触力超阈值代价。
                    net_contact_forces = getattr(  # 原L407：从接触传感器读取世界力历史，缺失时得到None。
                        getattr(getattr(env, "contact_sensor", None), "data", None),  # 原L408：从接触传感器读取世界力历史，缺失时得到None。
                        "net_forces_w_history",  # 原L409：从接触传感器读取世界力历史，缺失时得到None。
                        None,  # 原L410：从接触传感器读取世界力历史，缺失时得到None。
                    )  # 原L411：从接触传感器读取世界力历史，缺失时得到None。
                    if net_contact_forces is None or len(getattr(env, "_desired_contact_link_idx", [])) == 0:  # 原L412：传感器或期望接触的轮子索引缺失时，没有可用力数据。
                        added_reward = torch.zeros(env.num_envs, dtype=torch.float, device=env.device)  # 原L413：此时该项给0；不是证明没有碰撞。
                    else:  # 原L414：数据存在时计算代价。
                        threshold = float(addition_cfg.get("force_threshold", 20.0))  # 原L415：水平接触力免罚阈值，缺省20N。
                        mode = addition_cfg.get("mode", "l2")  # 原L416：L1或L2模式，缺省L2。
                        square_sigma = float(addition_cfg.get("square_sigma", 1.0))  # 原L417：L2先乘的尺度，随后会平方，区别于Airborne的L2实现。
                        wheel_xy_force = torch.amax(  # 原L418：取每轮历史窗口内最大的水平合力。
                            torch.norm(  # 原L419：计算每个历史采样的水平向量长度。
                                net_contact_forces[:, :, env._desired_contact_link_idx, :2],  # 原L420：只取轮子接触力的世界x/y两个分量。
                                dim=-1,  # 原L421：沿xy分量求范数。
                            ),  # 原L422：闭合上面的跨行表达式；不另产生奖励。
                            dim=1,  # 原L423：沿历史时间轴取最大；并非只看当前瞬时力。
                        )  # 原L424：闭合上面的跨行表达式；不另产生奖励。
                        force_over = torch.clamp(wheel_xy_force - threshold, min=0.0)  # 原L425：只保留超过阈值的非负力。
                        if mode == "l1":  # 原L426：L1模式。
                            penalty = torch.sum(force_over, dim=1)  # 原L427：两轮超阈值量相加，单位随原始力，后续负权重才扣分。
                        elif mode == "l2":  # 原L428：L2模式。
                            penalty = torch.sum(torch.square(force_over * square_sigma), dim=1)  # 原L429：两轮(excess*square_sigma)^2相加，尺度也被平方。
                        else:  # 原L430：其它模式不静默替代。
                            raise ValueError(f"Unsupported wheel_xy_contact_force reward mode: {mode}")  # 原L431：抛出配置错误。
                        added_reward = env.wheel_forward_stair_state.float() * penalty  # 原L432：上阶期间返回正代价；负权重才表示减少顶撞。
                else:  # 原L433：未识别的奖励type。
                    raise ValueError(f"Unsupported stair reward addition type: {addition_type}")  # 原L434：抛出类型错误，不生成假奖励。
            else:  # 原L435：新增项配置若直接是一个数值。
                added_reward = env.wheel_forward_stair_state.float() * float(addition_cfg)  # 原L436：上阶期间给该数值，非上阶给0。

            if term_name in reward_terms:  # 原L438：若新增项和普通项同名。
                reward_terms[term_name] = reward_terms[term_name] + added_reward  # 原L439：在原始值上相加，之后共用同一个最终权重。
            else:  # 原L440：若是新名字。
                reward_terms[term_name] = added_reward  # 原L441：建立新的原始项；最终仍必须列在cfg.rewards才被求和。
        return reward_terms  # 原L442：返回原始奖励字典。
```

### 台阶检测

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/stair.py`，L79–L89。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def _get_step_detect_masks(  # 原L79：台阶检测函数，输入每轮扫描高度的时间差，返回逐轮与逐环境布尔量。
        self, env, height_diffs: torch.Tensor  # 原L80：台阶检测函数，输入每轮扫描高度的时间差，返回逐轮与逐环境布尔量。
    ) -> tuple[torch.Tensor, torch.Tensor]:  # 原L81：台阶检测函数，输入每轮扫描高度的时间差，返回逐轮与逐环境布尔量。
        if height_diffs.shape[1] == 0:  # 原L82：没有有效轮扫描通道。
            empty_env = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)  # 原L83：建立所有环境均false的布尔量。
            return empty_env.unsqueeze(-1).expand(-1, 0), empty_env  # 原L84：返回空逐轮结果与全false逐环境结果。
        detect_cfg = env._get_wheel_forward_scan_cfg().get("detect", {})  # 原L85：检测参数来自wheel_forward_scan_cfg，不是stair自己的独立台高常数。
        step_min = float(detect_cfg.get("step_height_min", 0.15))  # 原L86：可跨越的最小高度差兜底15cm，实际以配置覆盖值为准。
        step_max = float(detect_cfg.get("step_height_max", 0.25))  # 原L87：最大高度差兜底25cm，实际以配置覆盖值为准。
        per_wheel = (height_diffs > step_min) & (height_diffs < step_max)  # 原L88：严格大于min且严格小于max；端点不算。
        return per_wheel, torch.any(per_wheel, dim=1)  # 原L89：任一轮检测到即认为这个环境有台阶。
```

### 成功用的轮接触

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/stair.py`，L98–L115。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def _get_wheel_contact_mask(self, env) -> torch.Tensor:  # 原L98：获取每个轮子的接触布尔值。
        contact_forces = getattr(getattr(env.contact_sensor, "data", None), "net_forces_w_history", None)  # 原L99：读取接触力历史而不是指定台顶的接触manifold。
        wheel_contact = torch.zeros(env.num_envs, 2, dtype=torch.bool, device=env.device)  # 原L100：初始化[N,2]左右轮接触为false。
        if contact_forces is None:  # 原L101：缺传感器历史。
            return wheel_contact  # 原L102：返回全false，不凭视觉补接触。
        wheel_force_peaks = env._get_wheel_contact_force_peaks(contact_forces)  # 原L103：调用环境函数取每轮历史接触力峰值。
        if wheel_force_peaks.shape[1] == 0:  # 原L104：无轮数据。
            return wheel_contact  # 原L105：返回全false。
        wheel_count = min(2, wheel_force_peaks.shape[1])  # 原L106：最多处理两个轮子。
        success_cfg = self._cfg(env).get("success", {})  # 原L107：读取上阶成功配置。
        threshold = float(  # 原L108：接触阈值优先success.contact_force_threshold，再用全局desired_contact_force_threshold，最后兜底1N。
            success_cfg.get(  # 原L109：接触阈值优先success.contact_force_threshold，再用全局desired_contact_force_threshold，最后兜底1N。
                "contact_force_threshold",  # 原L110：接触阈值优先success.contact_force_threshold，再用全局desired_contact_force_threshold，最后兜底1N。
                getattr(env.cfg, "desired_contact_force_threshold", 1.0),  # 原L111：接触阈值优先success.contact_force_threshold，再用全局desired_contact_force_threshold，最后兜底1N。
            )  # 原L112：接触阈值优先success.contact_force_threshold，再用全局desired_contact_force_threshold，最后兜底1N。
        )  # 原L113：接触阈值优先success.contact_force_threshold，再用全局desired_contact_force_threshold，最后兜底1N。
        wheel_contact[:, :wheel_count] = wheel_force_peaks[:, :wheel_count] > threshold  # 原L114：各轮历史峰值过阈值就记true，没有识别支撑面。
        return wheel_contact  # 原L115：返回逐轮接触mask。
```

### 高度命令覆盖

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/stair.py`，L140–L141。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def get_effective_height_cmd(self, env, height_cmd: torch.Tensor) -> torch.Tensor:  # 原L140：活动期将普通高度命令替换成上阶专用的相对台面身体高度命令。
        return torch.where(env.wheel_forward_stair_state, env.wheel_forward_stair_height_cmd, height_cmd)  # 原L141：活动期将普通高度命令替换成上阶专用的相对台面身体高度命令。
```

### 完整上阶状态与事件生成

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/stair.py`，L143–L326。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def on_command_updated(self, env) -> None:  # 原L143：每次命令更新时推进状态机，事件和奖励依赖这一更新顺序。
        cfg = self._cfg(env)  # 原L144：读取stair配置。
        if not bool(cfg.get("enabled", False)):  # 原L145：未开启时。
            self._zero_state(env)  # 原L146：清理本状态机全部缓存。
            return  # 原L147：立即返回。

        env.wheel_forward_stair_wall_reset.zero_()  # 原L149：每次更新前清空上次的单步事件、失败标志与快速成功事件记录。
        env.wheel_forward_stair_failure_reset.zero_()  # 原L150：每次更新前清空上次的单步事件、失败标志与快速成功事件记录。
        env.wheel_forward_stair_detect_event.zero_()  # 原L151：每次更新前清空上次的单步事件、失败标志与快速成功事件记录。
        env.wheel_forward_stair_success_exit_event.zero_()  # 原L152：每次更新前清空上次的单步事件、失败标志与快速成功事件记录。
        env.wheel_forward_stair_failure_exit_event.zero_()  # 原L153：每次更新前清空上次的单步事件、失败标志与快速成功事件记录。
        env.wheel_forward_stair_timeout_exit_event.zero_()  # 原L154：每次更新前清空上次的单步事件、失败标志与快速成功事件记录。
        env.wheel_forward_stair_fast_success_time_event.zero_()  # 原L155：每次更新前清空上次的单步事件、失败标志与快速成功事件记录。
        env.wheel_forward_stair_fast_success_started_event.zero_()  # 原L156：每次更新前清空上次的单步事件、失败标志与快速成功事件记录。

        stair_diffs = env._get_wheel_forward_stair_temporal_height_diffs_raw()  # 原L158：读取更靠近轮子的上阶扫描高度时间差。
        if stair_diffs.shape[1] == 0:  # 原L159：扫描通道不存在。
            return  # 原L160：不检测、不进入状态。
        stair_per_wheel, stair_detect = self._get_step_detect_masks(env, stair_diffs)  # 原L161：计算逐轮台阶与任一轮检测结果。
        forward_diffs = env._get_wheel_forward_temporal_height_diffs_raw()  # 原L162：读取更远前方的扫描差分。
        _, forward_detect = self._get_step_detect_masks(env, forward_diffs)  # 原L163：也计算远处台阶检测；本函数后面没有拿forward_detect单独奖励水平进度。
        allowed_terrain_names = self._as_name_tuple(cfg.get("allowed_terrain_names", ()))  # 原L164：构造允许地形mask。
        allowed_terrain_mask = env.get_terrain_name_mask(allowed_terrain_names)  # 原L165：构造允许地形mask。
        not_allowed_terrain_names = self._as_name_tuple(cfg.get("not_allowed_terrain_names", ()))  # 原L166：读取排除地形名。
        if len(not_allowed_terrain_names) > 0:  # 原L167：有排除名单则去掉这些环境。
            allowed_terrain_mask &= ~env.get_terrain_name_mask(not_allowed_terrain_names)  # 原L168：有排除名单则去掉这些环境。
        stair_detect = stair_detect & allowed_terrain_mask  # 原L169：将地形许可作用到近/远检测和逐轮近检测。
        forward_detect = forward_detect & allowed_terrain_mask  # 原L170：将地形许可作用到近/远检测和逐轮近检测。
        stair_per_wheel = stair_per_wheel & allowed_terrain_mask.unsqueeze(-1)  # 原L171：将地形许可作用到近/远检测和逐轮近检测。

        query_points_w, hit_points_w = env._get_wheel_forward_stair_scan_points()  # 原L173：取近处扫描射线的世界命中点。
        if hit_points_w is None:  # 原L174：没有命中点则返回。
            return  # 原L175：没有命中点则返回。

        env.wheel_forward_stair_detect_event.copy_(stair_detect)  # 原L177：保存本次检测事件。
        wall_reset = torch.zeros_like(stair_detect)  # 原L178：这里wall_reset明确置全false；不要把StepUp的墙阈值处理直接套进Stair。
        env.wheel_forward_stair_wall_reset.copy_(wall_reset)  # 原L179：这里wall_reset明确置全false；不要把StepUp的墙阈值处理直接套进Stair。

        enter_mask = stair_detect & (~env.wheel_forward_stair_state) & (~wall_reset)  # 原L181：检测到台阶、当前不在上阶、未墙重置才进入。
        if torch.any(enter_mask):  # 原L182：至少有一个环境新进入。
            hit_z = hit_points_w[:, :, 2]  # 原L183：读取扫描命中点世界z。
            reference_candidates = torch.where(  # 原L184：只保留触发台阶的轮扫描高度，其余用负无穷排除。
                stair_per_wheel,  # 原L185：只保留触发台阶的轮扫描高度，其余用负无穷排除。
                hit_z,  # 原L186：只保留触发台阶的轮扫描高度，其余用负无穷排除。
                torch.full_like(hit_z, -torch.inf),  # 原L187：只保留触发台阶的轮扫描高度，其余用负无穷排除。
            )  # 原L188：只保留触发台阶的轮扫描高度，其余用负无穷排除。
            reference_height = torch.amax(reference_candidates, dim=1)  # 原L189：从触发轮中取最高命中高度。
            reference_height = torch.where(torch.isfinite(reference_height), reference_height, hit_z[:, 0])  # 原L190：若非有限则回退首个命中高度，不做新的物理测量。
            target_range = cfg.get("height_cmd", {}).get("range", (0.37, 0.40))  # 原L191：身体相对台面高度目标区间，函数兜底0.37到0.40m。
            target_min = float(target_range[0])  # 原L192：读区间端点并保证low<=high。
            target_max = float(target_range[-1])  # 原L193：读区间端点并保证low<=high。
            target_low, target_high = min(target_min, target_max), max(target_min, target_max)  # 原L194：读区间端点并保证low<=high。
            env.wheel_forward_stair_reference_height[enter_mask] = reference_height[enter_mask]  # 原L195：锁定这次上阶的台面参考高度。
            env.wheel_forward_stair_height_cmd[enter_mask] = (  # 原L196：对新进入的环境独立均匀采样身体相对台面高度命令。
                torch.rand(  # 原L197：对新进入的环境独立均匀采样身体相对台面高度命令。
                    int(torch.count_nonzero(enter_mask).item()),  # 原L198：对新进入的环境独立均匀采样身体相对台面高度命令。
                    dtype=torch.float,  # 原L199：对新进入的环境独立均匀采样身体相对台面高度命令。
                    device=env.device,  # 原L200：对新进入的环境独立均匀采样身体相对台面高度命令。
                )  # 原L201：对新进入的环境独立均匀采样身体相对台面高度命令。
                * (target_high - target_low)  # 原L202：对新进入的环境独立均匀采样身体相对台面高度命令。
                + target_low  # 原L203：对新进入的环境独立均匀采样身体相对台面高度命令。
            )  # 原L204：对新进入的环境独立均匀采样身体相对台面高度命令。
            env.wheel_forward_stair_success_time[enter_mask] = 0.0  # 原L205：新进入时成功保持计时归零。

        active = (env.wheel_forward_stair_state | enter_mask) & (~wall_reset)  # 原L207：当前旧状态或新进入者为active。
        prev_active = env.wheel_forward_stair_state & (~wall_reset)  # 原L208：prev_active只包括上一拍已经活动的环境，用于避免首次虚假进度。
        env.wheel_forward_stair_state_time.copy_(  # 原L209：active计时增加dt，否则归零，作为超时依据。
            torch.where(  # 原L210：active计时增加dt，否则归零，作为超时依据。
                active,  # 原L211：active计时增加dt，否则归零，作为超时依据。
                env.wheel_forward_stair_state_time + env.step_dt,  # 原L212：active计时增加dt，否则归零，作为超时依据。
                torch.zeros_like(env.wheel_forward_stair_state_time),  # 原L213：active计时增加dt，否则归零，作为超时依据。
            )  # 原L214：active计时增加dt，否则归零，作为超时依据。
        )  # 原L215：active计时增加dt，否则归零，作为超时依据。
        wheel_contact = self._get_wheel_contact_mask(env)  # 原L216：取逐轮历史接触阈值判断。
        both_wheel_contact = torch.all(wheel_contact, dim=1)  # 原L217：两轮都true才满足接触部分。
        fast_cfg = cfg.get("fast_success", {})  # 原L218：读取启动快速计时的水平接触力阈值，依次回退到success阈值、全局阈值、1N。
        xy_contact_threshold = float(  # 原L219：读取启动快速计时的水平接触力阈值，依次回退到success阈值、全局阈值、1N。
            fast_cfg.get(  # 原L220：读取启动快速计时的水平接触力阈值，依次回退到success阈值、全局阈值、1N。
                "xy_contact_force_threshold",  # 原L221：读取启动快速计时的水平接触力阈值，依次回退到success阈值、全局阈值、1N。
                cfg.get("success", {}).get(  # 原L222：读取启动快速计时的水平接触力阈值，依次回退到success阈值、全局阈值、1N。
                    "contact_force_threshold",  # 原L223：读取启动快速计时的水平接触力阈值，依次回退到success阈值、全局阈值、1N。
                    getattr(env.cfg, "desired_contact_force_threshold", 1.0),  # 原L224：读取启动快速计时的水平接触力阈值，依次回退到success阈值、全局阈值、1N。
                ),  # 原L225：读取启动快速计时的水平接触力阈值，依次回退到success阈值、全局阈值、1N。
            )  # 原L226：读取启动快速计时的水平接触力阈值，依次回退到success阈值、全局阈值、1N。
        )  # 原L227：读取启动快速计时的水平接触力阈值，依次回退到success阈值、全局阈值、1N。
        wheel_xy_contact = self._get_wheel_xy_contact_mask(env, xy_contact_threshold)  # 原L228：另取各轮历史水平接触力是否超阈值。
        fast_timer_started = active & (  # 原L229：上阶期间任一轮触发水平接触，或以前已经启动，则保持计时启动。
            env.wheel_forward_stair_fast_timer_started | torch.any(wheel_xy_contact, dim=1)  # 原L230：上阶期间任一轮触发水平接触，或以前已经启动，则保持计时启动。
        )  # 原L231：上阶期间任一轮触发水平接触，或以前已经启动，则保持计时启动。
        env.wheel_forward_stair_fast_timer_started.copy_(fast_timer_started)  # 原L232：保存启动标志。
        env.wheel_forward_stair_fast_timer.copy_(  # 原L233：快速计时启动后加dt，否则归零。
            torch.where(  # 原L234：快速计时启动后加dt，否则归零。
                fast_timer_started,  # 原L235：快速计时启动后加dt，否则归零。
                env.wheel_forward_stair_fast_timer + env.step_dt,  # 原L236：快速计时启动后加dt，否则归零。
                torch.zeros_like(env.wheel_forward_stair_fast_timer),  # 原L237：快速计时启动后加dt，否则归零。
            )  # 原L238：快速计时启动后加dt，否则归零。
        )  # 原L239：快速计时启动后加dt，否则归零。
        body_relative_step_height = (  # 原L240：身体相对锁定台面高度=root世界z-参考台面z。
            env.robot.data.root_pos_w[:, 2] - env.wheel_forward_stair_reference_height  # 原L241：身体相对锁定台面高度=root世界z-参考台面z。
        )  # 原L242：身体相对锁定台面高度=root世界z-参考台面z。
        env.wheel_forward_stair_body_relative_height_progress.copy_(  # 原L243：已在上阶的环境计算本步相对高度减上步，仅取正；首次进入给0。
            torch.where(  # 原L244：已在上阶的环境计算本步相对高度减上步，仅取正；首次进入给0。
                prev_active,  # 原L245：已在上阶的环境计算本步相对高度减上步，仅取正；首次进入给0。
                torch.clamp(  # 原L246：已在上阶的环境计算本步相对高度减上步，仅取正；首次进入给0。
                    body_relative_step_height - env.wheel_forward_stair_prev_body_relative_height,  # 原L247：已在上阶的环境计算本步相对高度减上步，仅取正；首次进入给0。
                    min=0.0,  # 原L248：已在上阶的环境计算本步相对高度减上步，仅取正；首次进入给0。
                ),  # 原L249：已在上阶的环境计算本步相对高度减上步，仅取正；首次进入给0。
                torch.zeros_like(body_relative_step_height),  # 原L250：已在上阶的环境计算本步相对高度减上步，仅取正；首次进入给0。
            )  # 原L251：已在上阶的环境计算本步相对高度减上步，仅取正；首次进入给0。
        )  # 原L252：已在上阶的环境计算本步相对高度减上步，仅取正；首次进入给0。
        env.wheel_forward_stair_prev_body_relative_height.copy_(  # 原L253：保存当前高度作为下次增量基准，非活动给0。
            torch.where(  # 原L254：保存当前高度作为下次增量基准，非活动给0。
                active,  # 原L255：保存当前高度作为下次增量基准，非活动给0。
                body_relative_step_height,  # 原L256：保存当前高度作为下次增量基准，非活动给0。
                torch.zeros_like(env.wheel_forward_stair_prev_body_relative_height),  # 原L257：保存当前高度作为下次增量基准，非活动给0。
            )  # 原L258：保存当前高度作为下次增量基准，非活动给0。
        )  # 原L259：保存当前高度作为下次增量基准，非活动给0。
        success_cfg = cfg.get("success", {})  # 原L260：读取成功规则。
        success_error = max(float(success_cfg.get("height_error", 0.05)), 0.0)  # 原L261：可低于目标的高度容差，兜底5cm。
        success_cond = (  # 原L262：成功候选=活动且两轮历史力过阈值且身体相对台面高度>=目标-容差。
            active  # 原L263：成功候选=活动且两轮历史力过阈值且身体相对台面高度>=目标-容差。
            & both_wheel_contact  # 原L264：成功候选=活动且两轮历史力过阈值且身体相对台面高度>=目标-容差。
            & (body_relative_step_height >= env.wheel_forward_stair_height_cmd - success_error)  # 原L265：成功候选=活动且两轮历史力过阈值且身体相对台面高度>=目标-容差。
        )  # 原L266：成功候选=活动且两轮历史力过阈值且身体相对台面高度>=目标-容差。
        env.wheel_forward_stair_success_time.copy_(  # 原L267：候选连续满足则加dt；不满足立即清零，这是成功保持时间。
            torch.where(  # 原L268：候选连续满足则加dt；不满足立即清零，这是成功保持时间。
                success_cond,  # 原L269：候选连续满足则加dt；不满足立即清零，这是成功保持时间。
                env.wheel_forward_stair_success_time + env.step_dt,  # 原L270：候选连续满足则加dt；不满足立即清零，这是成功保持时间。
                torch.zeros_like(env.wheel_forward_stair_success_time),  # 原L271：候选连续满足则加dt；不满足立即清零，这是成功保持时间。
            )  # 原L272：候选连续满足则加dt；不满足立即清零，这是成功保持时间。
        )  # 原L273：候选连续满足则加dt；不满足立即清零，这是成功保持时间。
        success_duration = max(  # 原L274：成功保持时间兜底0.3秒，注意显式配置可覆盖。
            float(success_cfg.get("duration_s", 0.3)),  # 原L275：成功保持时间兜底0.3秒，注意显式配置可覆盖。
            0.0,  # 原L276：成功保持时间兜底0.3秒，注意显式配置可覆盖。
        )  # 原L277：成功保持时间兜底0.3秒，注意显式配置可覆盖。
        success_exit = active & (env.wheel_forward_stair_success_time >= success_duration)  # 原L278：计时达到阈值产生成功退出；不是直接宣称270mm技能验收。

        failure_cfg = cfg.get("failure", {})  # 原L280：读取失败规则。
        fail_drop = max(  # 原L281：扫描台面跌落容差，兜底10cm。
            float(failure_cfg.get("drop_threshold", 0.10)),  # 原L282：扫描台面跌落容差，兜底10cm。
            0.0,  # 原L283：扫描台面跌落容差，兜底10cm。
        )  # 原L284：扫描台面跌落容差，兜底10cm。
        stair_hit_z = hit_points_w[:, :, 2]  # 原L285：读当前近扫描命中高度。
        failure_exit = active & torch.all(  # 原L286：活动且所有轮扫描点低于锁定台面减drop时失败；不是身体自由落体高度判定。
            stair_hit_z < (env.wheel_forward_stair_reference_height.unsqueeze(-1) - fail_drop),  # 原L287：活动且所有轮扫描点低于锁定台面减drop时失败；不是身体自由落体高度判定。
            dim=1,  # 原L288：活动且所有轮扫描点低于锁定台面减drop时失败；不是身体自由落体高度判定。
        )  # 原L289：活动且所有轮扫描点低于锁定台面减drop时失败；不是身体自由落体高度判定。
        timeout_cfg = cfg.get("timeout", {})  # 原L290：读取上阶超时，兜底5秒，0表示禁用时间上限。
        timeout_duration_s = max(float(timeout_cfg.get("duration_s", 5.0)), 0.0)  # 原L291：读取上阶超时，兜底5秒，0表示禁用时间上限。
        timeout_exit = (  # 原L292：活动计时达到正的超时阈值时超时。
            active  # 原L293：活动计时达到正的超时阈值时超时。
            & (timeout_duration_s > 0.0)  # 原L294：活动计时达到正的超时阈值时超时。
            & (env.wheel_forward_stair_state_time >= timeout_duration_s)  # 原L295：活动计时达到正的超时阈值时超时。
        )  # 原L296：活动计时达到正的超时阈值时超时。

        failure_exit = failure_exit | timeout_exit  # 原L298：超时并入failure_exit，因此failure_event也会包含超时。
        next_state = active & (~success_exit) & (~failure_exit)  # 原L299：成功或失败就退出；否则维持上阶。
        env.wheel_forward_stair_success_exit_event.copy_(success_exit)  # 原L300：保存单步成功事件，即奖励读取的success_event。
        env.wheel_forward_stair_failure_exit_event.copy_(failure_exit)  # 原L301：保存单步失败事件。
        env.wheel_forward_stair_timeout_exit_event.copy_(timeout_exit)  # 原L302：另外保存超时事件便于日志区别。
        env.wheel_forward_stair_fast_success_started_event.copy_(  # 原L303：只在成功且快速计时确实启动过时记录启动事件。
            success_exit & env.wheel_forward_stair_fast_timer_started  # 原L304：只在成功且快速计时确实启动过时记录启动事件。
        )  # 原L305：只在成功且快速计时确实启动过时记录启动事件。
        env.wheel_forward_stair_fast_success_time_event.copy_(  # 原L306：成功时拷贝快速耗时，否则事件耗时置0。
            torch.where(  # 原L307：成功时拷贝快速耗时，否则事件耗时置0。
                success_exit,  # 原L308：成功时拷贝快速耗时，否则事件耗时置0。
                env.wheel_forward_stair_fast_timer,  # 原L309：成功时拷贝快速耗时，否则事件耗时置0。
                torch.zeros_like(env.wheel_forward_stair_fast_timer),  # 原L310：成功时拷贝快速耗时，否则事件耗时置0。
            )  # 原L311：成功时拷贝快速耗时，否则事件耗时置0。
        )  # 原L312：成功时拷贝快速耗时，否则事件耗时置0。
        env.wheel_forward_stair_failure_reset.copy_(failure_exit)  # 原L313：失败标志供终止分类函数读取。
        env.wheel_forward_stair_state.copy_(next_state)  # 原L314：写入更新后的活动状态；因此持续型奖励在退出后为0，事件项仍读单步事件。
        self._clear_airborne_state(env, next_state)  # 原L315：仍在上阶的环境清空Airborne状态，避免两套活动期冲突。

        clear_mask = wall_reset | success_exit | failure_exit | timeout_exit  # 原L317：本次退出/墙重置的环境需要清缓存。
        if torch.any(clear_mask):  # 原L318：存在待清理的环境。
            env.wheel_forward_stair_success_time[clear_mask] = 0.0  # 原L319：清理保持时间、目标、台面参考与进度缓存；单步成功/失败事件已单独保存。
            env.wheel_forward_stair_state_time[clear_mask] = 0.0  # 原L320：清理保持时间、目标、台面参考与进度缓存；单步成功/失败事件已单独保存。
            env.wheel_forward_stair_height_cmd[clear_mask] = 0.0  # 原L321：清理保持时间、目标、台面参考与进度缓存；单步成功/失败事件已单独保存。
            env.wheel_forward_stair_reference_height[clear_mask] = 0.0  # 原L322：清理保持时间、目标、台面参考与进度缓存；单步成功/失败事件已单独保存。
            env.wheel_forward_stair_fast_timer[clear_mask] = 0.0  # 原L323：清理保持时间、目标、台面参考与进度缓存；单步成功/失败事件已单独保存。
            env.wheel_forward_stair_fast_timer_started[clear_mask] = False  # 原L324：清理保持时间、目标、台面参考与进度缓存；单步成功/失败事件已单独保存。
            env.wheel_forward_stair_prev_body_relative_height[clear_mask] = 0.0  # 原L325：清理保持时间、目标、台面参考与进度缓存；单步成功/失败事件已单独保存。
            env.wheel_forward_stair_body_relative_height_progress[clear_mask] = 0.0  # 原L326：清理保持时间、目标、台面参考与进度缓存；单步成功/失败事件已单独保存。
```

### 失败与超时分类

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/stair.py`，L444–L457。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def apply_done_masks(  # 原L444：修改episode的terminate和time_out分类。
        self,  # 原L445：修改episode的terminate和time_out分类。
        env,  # 原L446：修改episode的terminate和time_out分类。
        terminate: torch.Tensor,  # 原L447：修改episode的terminate和time_out分类。
        time_out: torch.Tensor,  # 原L448：修改episode的terminate和time_out分类。
    ) -> tuple[torch.Tensor, torch.Tensor]:  # 原L449：修改episode的terminate和time_out分类。
        time_out = time_out | env.wheel_forward_stair_wall_reset  # 原L450：墙重置进入time_out。
        terminate = terminate & (~env.wheel_forward_stair_wall_reset)  # 原L451：墙重置从terminate中去掉。
        if bool(self._cfg(env).get("failure", {}).get("terminate", True)):  # 原L452：failure.terminate决定失败算真实终止还是超时截断，兜底true。
            terminate = terminate | env.wheel_forward_stair_failure_reset  # 原L453：开启时上阶失败进入terminate。
        else:  # 原L454：关闭时。
            time_out = time_out | env.wheel_forward_stair_failure_reset  # 原L455：上阶失败进入time_out。
            terminate = terminate & (~env.wheel_forward_stair_failure_reset)  # 原L456：并从terminate中去掉。
        return terminate, time_out  # 原L457：返回两个分类mask，对后续价值bootstrap有影响。
```
