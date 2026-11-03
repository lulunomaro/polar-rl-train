# StepUp 扫描辅助与状态机准入逐行注释

当前V14 Rough-v1调用cfg_utils.py的_apply_v14_rough_runtime_cfg，开启Airborne与wheel_forward_scan。实际StepUp阈值为0.12<差分高度<0.14m，>0.14m当墙；bias0.16m、hold2秒、max0.40m。它不是一个直接输出关节轨迹的传统控制器，核心作用是改高度命令，交给策略与普通高度奖励。也不能把此窄差分阈值原封不动说成270mm单阶保证。

状态机管理器按构造列表顺序依次传递奖励字典；通用manager的同源文件已经在history/evidence/MOD4_E1_G3_MATCHED_REVIEW_20261010/scut/source/agent_tasks/agent_tasks/manager/mdp/state_machine/manager.py L86–92归档，未另复制。

### 扫描、保持与结束分类

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/step_up.py`，L25–L108。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def _cfg(self, env) -> dict:  # 原L25：StepUp读wheel_forward_scan_cfg，不是Stair的奖励字典。
        return env._get_wheel_forward_scan_cfg()  # 原L26：StepUp读wheel_forward_scan_cfg，不是Stair的奖励字典。

    def get_effective_height_cmd(self, env, height_cmd: torch.Tensor) -> torch.Tensor:  # 原L28：计算实际生效的高度命令。
        # 台阶事件触发后，height command 会被保持为一个抬高后的值；计时结束后恢复原始命令。  [原L29：原作者注释，不执行]
        hold_active = env.wheel_forward_height_cmd_hold_remaining_time > 0.0  # 原L30：抬高命令剩余保持时间大于0。
        return torch.where(hold_active, env.wheel_forward_height_cmd_hold_value, height_cmd)  # 原L31：活动环境返回保持的抬高值，其它返回原命令。

    def on_command_updated(self, env) -> None:  # 原L33：命令更新时推进StepUp检测。
        # 没启用轮前向扫描时，清空本状态机维护的运行时状态，避免旧 episode 残留。  [原L34：原作者注释，不执行]
        cfg = self._cfg(env)  # 原L35：读扫描配置。
        if not bool(cfg.get("enabled", False)):  # 原L36：扫描辅助未开启。
            env.wheel_forward_height_cmd_hold_remaining_time.zero_()  # 原L37：清空保持时间、保持值、墙重置和检测事件。
            env.wheel_forward_height_cmd_hold_value.zero_()  # 原L38：清空保持时间、保持值、墙重置和检测事件。
            env.wheel_forward_wall_reset.zero_()  # 原L39：清空保持时间、保持值、墙重置和检测事件。
            env.wheel_forward_step_detect_event.zero_()  # 原L40：清空保持时间、保持值、墙重置和检测事件。
            return  # 原L41：退出。

        # hold 是一个持续时间状态：每个 control step 递减，直到自动失效。  [原L43：原作者注释，不执行]
        env.wheel_forward_height_cmd_hold_remaining_time = torch.clamp(  # 原L44：每个控制拍保持倒计时减dt且不小于0。
            env.wheel_forward_height_cmd_hold_remaining_time - env.step_dt,  # 原L45：每个控制拍保持倒计时减dt且不小于0。
            min=0.0,  # 原L46：每个控制拍保持倒计时减dt且不小于0。
        )  # 原L47：每个控制拍保持倒计时减dt且不小于0。
        # step/wall 事件是单步检测结果，每次 command 更新前先清空再重新计算。  [原L48：原作者注释，不执行]
        env.wheel_forward_wall_reset.zero_()  # 原L49：清空上一拍检测事件和墙标志。
        env.wheel_forward_step_detect_event.zero_()  # 原L50：清空上一拍检测事件和墙标志。

        # 使用轮前方 raycast 的时间差分高度：当前前方地面高度 - 上一步前方地面高度。  [原L52：原作者注释，不执行]
        # 这样可以识别“前方突然抬高”的台阶/墙，而不是单纯依赖绝对高度。  [原L53：原作者注释，不执行]
        wheel_forward_height_diffs = env._get_wheel_forward_temporal_height_diffs_raw()  # 原L54：扫描高度时间差=本次前方命中z-上一拍命中z，不是机身与台面的高度差。
        if wheel_forward_height_diffs.shape[1] == 0:  # 原L55：没有通道则退出。
            return  # 原L56：没有通道则退出。

        # 高度差在 step_min 和 step_max 之间视为可跨越台阶；超过 wall_threshold 视为墙。  [原L58：原作者注释，不执行]
        detect_cfg = cfg.get("detect", {})  # 原L59：读取检测阈值。
        height_cmd_cfg = cfg.get("height_cmd", {})  # 原L60：读取抬高命令参数。
        step_min = float(detect_cfg.get("step_height_min", 0.15))  # 原L61：源码最小台阶差默认0.15m，当前V14覆盖0.12。
        step_max = float(detect_cfg.get("step_height_max", 0.25))  # 原L62：源码最大台阶差默认0.25m，当前V14覆盖0.14。
        wall_threshold = float(detect_cfg.get("wall_height", step_max))  # 原L63：墙阈值缺省最大台阶差，当前V14显式0.14m。
        height_cmd_bias = float(height_cmd_cfg.get("bias", 0.05))  # 原L64：抬高bias兜底0.05m，当前V14覆盖0.16。
        hold_duration_s = max(float(height_cmd_cfg.get("hold_s", 2.0)), 0.0)  # 原L65：保持时间兜底2秒，至少0。

        # 墙优先级高于台阶：如果高度差过大，不再触发 step_up assist，而是结束该 episode。  [原L67：原作者注释，不执行]
        wall_reset_mask = torch.any(wheel_forward_height_diffs > wall_threshold, dim=1)  # 原L68：任一轮差分高度超过墙阈值就wall_reset。
        step_detect_mask = torch.any(  # 原L69：任一轮差分严格在台阶区间内且不是wall，才触发step。
            (wheel_forward_height_diffs > step_min)  # 原L70：任一轮差分严格在台阶区间内且不是wall，才触发step。
            & (wheel_forward_height_diffs < step_max),  # 原L71：任一轮差分严格在台阶区间内且不是wall，才触发step。
            dim=1,  # 原L72：任一轮差分严格在台阶区间内且不是wall，才触发step。
        ) & (~wall_reset_mask)  # 原L73：任一轮差分严格在台阶区间内且不是wall，才触发step。

        env.wheel_forward_wall_reset.copy_(wall_reset_mask)  # 原L75：保存墙标志。
        env.wheel_forward_step_detect_event.copy_(step_detect_mask)  # 原L76：保存单步step检测事件。
        if torch.any(wall_reset_mask):  # 原L77：有墙环境。
            # 碰到墙时取消任何已保持的抬高命令，避免下一次 reset/可视化继续显示旧状态。  [原L78：原作者注释，不执行]
            env.wheel_forward_height_cmd_hold_remaining_time[wall_reset_mask] = 0.0  # 原L79：取消原先保持的抬高命令。
            env.wheel_forward_height_cmd_hold_value[wall_reset_mask] = 0.0  # 原L80：取消原先保持的抬高命令。

        if torch.any(step_detect_mask) and hold_duration_s > 0.0:  # 原L82：检测到台阶且hold时间有效。
            # 检测到台阶后，在原始 height_cmd 上加 bias，并按配置或 height_range 上限截断。  [原L83：原作者注释，不执行]
            wheel_forward_cmd_max = height_cmd_cfg.get("max", None)  # 原L84：读取可选高度命令上限。
            if wheel_forward_cmd_max is not None:  # 原L85：显式上限优先。
                max_height_target = float(wheel_forward_cmd_max)  # 原L86：显式上限优先。
            else:  # 原L87：没显式上限。
                height_range = getattr(env.cfg, "height_range", None)  # 原L88：用高度区间最后一个值作上限。
                if height_range is not None and len(height_range) > 0:  # 原L89：用高度区间最后一个值作上限。
                    max_height_target = float(height_range[-1])  # 原L90：用高度区间最后一个值作上限。
                else:  # 原L91：连高度区间也无则无穷上限。
                    max_height_target = float("inf")  # 原L92：连高度区间也无则无穷上限。
            env.wheel_forward_height_cmd_hold_value[step_detect_mask] = torch.clamp(  # 原L93：原height_cmd加bias后截上限；不按每拍前一保持值反复累加。
                env.height_cmd[step_detect_mask] + height_cmd_bias,  # 原L94：原height_cmd加bias后截上限；不按每拍前一保持值反复累加。
                max=max_height_target,  # 原L95：原height_cmd加bias后截上限；不按每拍前一保持值反复累加。
            )  # 原L96：原height_cmd加bias后截上限；不按每拍前一保持值反复累加。
            env.wheel_forward_height_cmd_hold_remaining_time[step_detect_mask] = hold_duration_s  # 原L97：重新设定保持倒计时。

    def apply_done_masks(  # 原L99：修改该episode的结束分类。
        self,  # 原L100：修改该episode的结束分类。
        env,  # 原L101：修改该episode的结束分类。
        terminate: torch.Tensor,  # 原L102：修改该episode的结束分类。
        time_out: torch.Tensor,  # 原L103：修改该episode的结束分类。
    ) -> tuple[torch.Tensor, torch.Tensor]:  # 原L104：修改该episode的结束分类。
        # 墙阻挡不是策略失败，而是地形不可通过/需要换环境，因此转成 time_out 而非 terminate。  [原L105：原作者注释，不执行]
        time_out = time_out | env.wheel_forward_wall_reset  # 原L106：墙重置记time_out。
        terminate = terminate & (~env.wheel_forward_wall_reset)  # 原L107：并从真实terminate中清掉。
        return terminate, time_out  # 原L108：返回结束mask；StepUp本身没有新增奖励函数，靠高度命令进入普通高度追踪产生引导。
```

### 状态机是否真的实例化

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/state_machines/manager.py`，L49–L65。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def from_env(cls, env) -> "WheelbipeStateMachineManager":  # 原L49：从环境配置创建实际状态机列表。
        """Create the default wheelbipe state-machine stack for an environment."""  # 原L50：函数说明。
        if not bool(getattr(env.cfg, "enable_state_machines", True)):  # 原L51：总开关关闭的判断。
            return cls([])  # 原L52：返回空管理器，专项奖励都不运行。
        machines = []  # 原L53：初始化有序列表。
        airborne_cfg = getattr(env.cfg, "airborne_state_machine_cfg", {})  # 原L54：读Airborne配置。
        if bool(airborne_cfg.get("enabled", False)):  # 原L55：Airborne enabled判断。
            machines.append(AirborneStateMachine())  # 原L56：启用则加入Airborne。
        jump_takeoff_cfg = getattr(env.cfg, "jump_takeoff_state_machine_cfg", {})  # 原L57：读JumpTakeoff配置。
        if bool(jump_takeoff_cfg.get("enabled", False)):  # 原L58：JumpTakeoff enabled判断。
            machines.append(JumpTakeoffStateMachine())  # 原L59：启用则加入JumpTakeoff。
        if bool(env._get_wheel_forward_scan_cfg().get("enabled", False)):  # 原L60：wheel_forward_scan enabled判断。
            machines.append(StepUpStateMachine())  # 原L61：启用则加入StepUp。
        stair_cfg = getattr(env.cfg, "stair_state_machine_cfg", {})  # 原L62：读Stair配置。
        if bool(stair_cfg.get("enabled", False)):  # 原L63：Stair enabled判断。
            machines.append(StairStateMachine())  # 原L64：启用则加入Stair。
        return cls(machines)  # 原L65：返回实际运行列表。
```

### V14派生环境后处理

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py`，L1151–L1171。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
    def _postprocess_reward_terms(self, reward_terms: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:  # 原L1151：V14派生环境的奖励后处理入口。
        reward_terms = super()._postprocess_reward_terms(reward_terms)  # 原L1152：先调用基类状态机后处理。
        if hasattr(self, "_gimbal_spin_translate_active") and torch.any(self._gimbal_spin_translate_active):  # 原L1153：可选小陀螺平移模式有活动环境。
            keep_mask = (~self._gimbal_spin_translate_active).float()  # 原L1154：非该模式环境保留，活动环境给0。
            suppressed_terms = getattr(  # 原L1155：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
                self.cfg,  # 原L1156：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
                "gimbal_spin_suppressed_reward_terms",  # 原L1157：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
                (  # 原L1158：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
                    "track_lin_vel_xy",  # 原L1159：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
                    "track_lin_vel_xy_soft",  # 原L1160：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
                    "track_lin_vel_xy_tight",  # 原L1161：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
                    "track_lin_vel_xy_huge_gap",  # 原L1162：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
                    "track_lin_vel_xy_square",  # 原L1163：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
                    "stand_still_lin_vel",  # 原L1164：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
                ),  # 原L1165：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
            )  # 原L1166：读取要在该模式中压低的普通追踪项名单，默认含前向追踪与静止项。
            for name in suppressed_terms:  # 原L1167：逐项处理。
                if name in reward_terms:  # 原L1168：原始项存在。
                    reward_terms[name] = reward_terms[name] * keep_mask  # 原L1169：在小陀螺平移活动环境抑制这些原始项。
        reward_terms.update(self._get_gimbal_spin_translate_reward_terms())  # 原L1170：增加/更新该模式的专用奖励，最终仍受cfg.rewards键与权重过滤。
        return reward_terms  # 原L1171：返回原始字典。
```
