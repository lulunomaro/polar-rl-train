# 当前固定提交的V14 Rough-v1实际奖励配置

这页解释当前源码配置，不把它倒填为七月已发布上阶模型的配置。下面所有被#注释的权重仅为候选；注释行保留原样并标不执行。

### 落地候选与三项实际权重

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py`，L1368–L1460。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
def _apply_v14_airborne_landing_precontact_cfg(cfg) -> None:  # 原L1368：给Flat-v1与Rough-v1共用的空中落地配置函数。
    """Apply the airborne landing/pre-contact additions shared by flat-v1 and rough-v1."""  # 原L1369：函数说明。

    cfg.airborne_state_machine_cfg = copy.deepcopy(cfg.airborne_state_machine_cfg)  # 原L1371：深拷贝空中配置，避免修改其它任务共享的类字典。

    landing_trajectory = copy.deepcopy(  # 原L1373：深拷贝原缓冲轨迹配置。
        cfg.airborne_state_machine_cfg.get("landing_trajectory", {})  # 原L1374：深拷贝原缓冲轨迹配置。
    )  # 原L1375：深拷贝原缓冲轨迹配置。
    landing_trajectory.update(  # 原L1376：更新这组参数。
        {  # 原L1377：更新这组参数。
            "enabled": False,  # 原L1378：明确关闭缓冲轨迹；下面数值保留不等于实际生效。
            "start_wheel_contact_duration_s": 0.02,  # 原L1379：若开启，任一轮接触计时达到0.02秒后才考虑缓冲。
            "target_height": 0.24,  # 原L1380：缓冲末端身体相对地面高度0.24m。
            "end_vel_z": 0.0,  # 原L1381：缓冲末端vz目标0。
            "min_height_margin": 0.02,  # 原L1382：起始高度必须比终点高至少0.02m。
            "min_down_vel": 0.2,  # 原L1383：仅下落速度超过0.2m/s才考虑触发。
            "duration_s": 0.3,  # 原L1384：规划缓冲段0.3秒。
            "max_abs_acc": 30.0,  # 原L1385：所需参考加速度绝对值上限30。
        }  # 原L1386：闭合上面的跨行表达式；不另产生奖励。
    )  # 原L1387：闭合上面的跨行表达式；不另产生奖励。
    cfg.airborne_state_machine_cfg["landing_trajectory"] = landing_trajectory  # 原L1388：保存仍处于enabled=false的缓冲配置。

    reward_additions = dict(cfg.airborne_state_machine_cfg.get("reward_additions", {}))  # 原L1390：拷贝已有新增奖励字典。
    reward_additions["airborne_wheel_contact_force_over"] = {  # 原L1391：定义轮接触力超量候选。
        "type": "wheel_contact_force_over",  # 原L1392：绑定到airborne.py对应type。
        "force_threshold": 300.0,  # 原L1393：免罚阈值300N。
        "mode": "l1",  # 原L1394：超量使用L1。
        "reduce": "sum",  # 原L1395：两轮超量相加。
    }  # 原L1396：闭合上面的跨行表达式；不另产生奖励。
    reward_additions["airborne_landing_wheel_body_x_positive"] = {  # 原L1397：定义落地轮在身体前方的候选。
        "type": "landing_wheel_body_x_positive",  # 原L1398：绑定单边轮x指数分支。
        "target_x": 0.03,  # 原L1399：最靠后的轮目标也在身体前方0.03m。
        "sigma": 0.03,  # 原L1400：L1指数分母0.03m。
        "command_x_min": 1.0,  # 原L1401：只在前向命令>1m/s时。
        "start_wheel_contact_duration_s": 0.02,  # 原L1402：轮接触计时达到0.02秒后。
        "contact_force_threshold": 1.0,  # 原L1403：当前轮接触力>1N。
        "contact_mode": "any_wheel",  # 原L1404：任一轮满足计时/力门控即可。
        "use_entry_command": True,  # 原L1405：使用进入空中时保存的命令。
    }  # 原L1406：闭合上面的跨行表达式；不另产生奖励。
    reward_additions["airborne_air_wheel_zero_torque_exp"] = {  # 原L1407：定义空中轮零扭矩指数奖励。
        "type": "wheel_zero_torque_exp",  # 原L1408：绑定到wheel_zero_torque_exp。
        "sigma": 1.5,  # 原L1409：扭矩尺度1.5，实际公式exp(-(maxabsτ/1.5)^2)。
        "before_wheel_contact_duration_s": 0.02,  # 原L1410：任一轮接触计时达到0.02秒前有效。
        "contact_mode": "any_wheel",  # 原L1411：门控按任一轮达到阈值则停止。
    }  # 原L1412：闭合上面的跨行表达式；不另产生奖励。
    reward_additions["airborne_precontact_wheel_directional_speed"] = {  # 原L1413：定义落地前顺行轮速奖励。
        "type": "wheel_directional_speed",  # 原L1414：绑定到wheel_directional_speed。
        "start": 0.0,  # 原L1415：从顺行角速度0开始计分。
        "full": 10.0,  # 原L1416：10rad/s及以上为1。
        "command_x_threshold": 1.0,  # 原L1417：命令x绝对值需>1m/s。
        "root_x_threshold": 1.0,  # 原L1418：身体实际vx绝对值也>1m/s且同向。
        "reduce": "min",  # 原L1419：取两轮较小分，不能一轮转快补另一轮。
        "before_wheel_contact_duration_s": 0.02,  # 原L1420：任一轮接触计时达到0.02秒前有效。
        "contact_mode": "any_wheel",  # 原L1421：任一轮停止条件。
    }  # 原L1422：闭合上面的跨行表达式；不另产生奖励。
    reward_additions["airborne_precontact_wheel_directional_speed_shortfall"] = {  # 原L1423：定义触地初期轮速不足代价。
        "type": "wheel_directional_speed_shortfall",  # 原L1424：绑定到wheel_directional_speed_shortfall。
        "start": 0.0,  # 原L1425：评分起点0rad/s。
        "full": 10.0,  # 原L1426：满分10rad/s。
        "command_x_threshold": 1.0,  # 原L1427：命令与实际vx阈值均1m/s且要同向。
        "root_x_threshold": 1.0,  # 原L1428：命令与实际vx阈值均1m/s且要同向。
        "reduce": "min",  # 原L1429：依然按较慢轮。
        "require_wheel_contact_timer_started": True,  # 原L1430：必须已有任一轮接触计时>0。
        "before_wheel_contact_duration_s": 0.05,  # 原L1431：任一轮接触计时达到0.05秒就停止。
        "contact_mode": "any_wheel",  # 原L1432：因此这里是触地初期窗口，不能把名字precontact理解成绝对未接触。
    }  # 原L1433：闭合上面的跨行表达式；不另产生奖励。
    reward_additions["airborne_landing_wheel_max_contact_force"] = {  # 原L1434：定义最大轮落地力候选。
        "type": "landing_wheel_max_contact_force",  # 原L1435：绑定到当前最大轮力评分。
        "force_start": 200.0,  # 原L1436：200N开始。
        "force_full": 400.0,  # 原L1437：400N到1。
        "start_wheel_contact_duration_s": 0.02,  # 原L1438：任一轮接触计时至少0.02秒。
        "contact_force_threshold": 1.0,  # 原L1439：当前轮力阈值1N。
        "contact_mode": "any_wheel",  # 原L1440：任一轮模式。
    }  # 原L1441：闭合上面的跨行表达式；不另产生奖励。
    reward_additions["airborne_landing_traj_height"] = {  # 原L1442：定义落地缓冲高度候选。
        "type": "landing_traj_height_exp",  # 原L1443：绑定轨迹高度指数分支。
        "sigma": 0.01,  # 原L1444：直接分母0.01。
    }  # 原L1445：闭合上面的跨行表达式；不另产生奖励。
    reward_additions["airborne_landing_traj_vel_z"] = {  # 原L1446：定义落地缓冲vz候选。
        "type": "landing_traj_vel_z_exp",  # 原L1447：绑定轨迹vz指数分支。
        "sigma": 0.25,  # 原L1448：直接分母0.25。
    }  # 原L1449：闭合上面的跨行表达式；不另产生奖励。
    cfg.airborne_state_machine_cfg["reward_additions"] = reward_additions  # 原L1450：保存所有定义；最终权重未开启的仍不会计算。

    # 保持 Rough-v1 当前启用的 airborne 权重；其它候选项仅保留 reward_additions，按需再开。  [原L1452：原作者注释，不执行]
    # cfg.rewards["airborne_wheel_contact_force_over"] = -0.1  [原L1453：原作者注释，不执行]
    # cfg.rewards["airborne_landing_wheel_body_x_positive"] = 5.0  [原L1454：原作者注释，不执行]
    cfg.rewards["airborne_air_wheel_zero_torque_exp"] = 20.0  # 原L1455：零轮扭矩项实际最终权重+20。
    cfg.rewards["airborne_precontact_wheel_directional_speed"] = 10.0  # 原L1456：顺行轮速项实际最终权重+10。
    cfg.rewards["airborne_precontact_wheel_directional_speed_shortfall"] = -10.0  # 原L1457：触地初期轮速不足项实际最终权重-10。
    # cfg.rewards["airborne_landing_wheel_max_contact_force"] = -10.0  [原L1458：原作者注释，不执行]
    # cfg.rewards["airborne_landing_traj_height"] = 20.0  [原L1459：原作者注释，不执行]
    # cfg.rewards["airborne_landing_traj_vel_z"] = 2.0  [原L1460：原作者注释，不执行]
```

### Flat-v1空中倍率、候选与实际权重

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py`，L1549–L1670。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
        reward_scales = dict(self.airborne_state_machine_cfg.get("reward_scales", {}))  # 原L1549：读取父配置的普通奖励空中倍率。
        reward_scales["undesired_contact"] = 25.0  # 原L1550：非期望接触原始项空中乘25；若原权重负则惩罚放大25倍。
        reward_scales["flat_orientation_y_v"] = 0.0  # 原L1551：空中取消随前进命令变化的pitch代价，不等于取消全部姿态奖励。
        # reward_scales["flat_orientation_x_v"] = 0.0  [原L1552：原作者注释，不执行]
        # reward_scales["flat_orientation_y_exp"] = 0.1  [原L1553：原作者注释，不执行]
        reward_scales["termination"] = 6.0  # 原L1554：空中真实终止项倍率6。
        # reward_scales["lin_vel_z"] = 0.1  [原L1555：原作者注释，不执行]
        # extra  [原L1556：原作者注释，不执行]
        # reward_scales["leg_joint_acc"] = 0.1  [原L1557：原作者注释，不执行]
        # reward_scales["leg_joint_vel"] = 0.1  [原L1558：原作者注释，不执行]
        # reward_scales["track_height_exp_tight"] = 0.1  [原L1559：原作者注释，不执行]
        reward_scales["track_height_square"] = 0.0  # 原L1560：空中取消普通高度平方代价。
        reward_scales["foot_bound_square"] = 0.0  # 原L1561：foot_bound_square倍率0；对应原始项若不存在则直接跳过。
        self.airborne_state_machine_cfg["reward_scales"] = reward_scales  # 原L1562：保存倍率表。
        reward_full = dict(self.airborne_state_machine_cfg.get("reward_full", {}))  # 原L1563：读取固定原始值替换表。
        reward_full.update(  # 原L1564：准备更新该表。
            {  # 原L1565：准备更新该表。
                # "track_lin_vel_xy": 0.8,  [原L1566：原作者注释，不执行]
                # "track_lin_vel_xy_square": 0.0,  [原L1567：原作者注释，不执行]
                # "track_ang_vel_z": 0.8,  [原L1568：原作者注释，不执行]
                # "track_ang_vel_z_square": 0.0,  [原L1569：原作者注释，不执行]
                # "track_height_exp_tight": 0.8,  [原L1570：原作者注释，不执行]
                # "track_height_square": 0.0,  [原L1571：原作者注释，不执行]
            }  # 原L1572：此update字典只有注释，没有实际替换值。
        )  # 原L1573：此update字典只有注释，没有实际替换值。
        self.airborne_state_machine_cfg["reward_full"] = reward_full  # 原L1574：保存原表，不能把注释当已替换。
        reward_additions = dict(self.airborne_state_machine_cfg.get("reward_additions", {}))  # 原L1575：读取新增项表。
        reward_additions.update(  # 原L1576：更新候选定义。
            {  # 原L1577：更新候选定义。
                "airborne_undesired_contact_force": {  # 原L1578：非期望部位接触力候选名。
                    "type": "undesired_contact_force",  # 原L1579：绑定力超量代价。
                    "force_threshold": self.undesired_contact_force_threshold,  # 原L1580：使用全局非期望接触力阈值。
                    "mode": "l1",  # 原L1581：L1形状。
                },  # 原L1582：闭合上面的跨行表达式；不另产生奖励。
                "airborne_landing_down_vel": {  # 原L1583：触地后下落速度候选名。
                    "type": "negative_lin_vel_z_after_wheel_contact",  # 原L1584：绑定只罚向下速度的分支。
                    "start_duration_s": 0.02,  # 原L1585：接触计时至少0.02秒。
                    "use_world_frame": True,  # 原L1586：使用世界vz。
                    "mode": "l2",  # 原L1587：L2。
                    "square_sigma": 2.0,  # 原L1588：2×down_vz²。
                },  # 原L1589：闭合上面的跨行表达式；不另产生奖励。
                "airborne_landing_down_vel_exp": {  # 原L1590：触地后vz指数候选名。
                    "type": "negative_lin_vel_z_after_wheel_contact_exp",  # 原L1591：绑定上下对称的vz²指数分支。
                    "start_duration_s": 0.02,  # 原L1592：计时至少0.02秒。
                    "use_world_frame": True,  # 原L1593：世界vz。
                    "sigma": 0.25,  # 原L1594：指数分母0.25。
                },  # 原L1595：闭合上面的跨行表达式；不另产生奖励。
                "airborne_joint_pos_limits": {  # 原L1596：空中关节位置软限位项名称。
                    "type": "rear2_rear1_joint_pos_limits",  # 原L1597：绑定rear2实际角位置超软界的距离和。
                },  # 原L1598：闭合上面的跨行表达式；不另产生奖励。
                "airborne_joint_pos_limits_vel_reg": {  # 原L1599：空中关节外向速度候选名。
                    "type": "rear2_rear1_joint_pos_limits_vel_reg",  # 原L1600：绑定越界且继续向外高速运动的关节计数。
                },  # 原L1601：闭合上面的跨行表达式；不另产生奖励。
                "airborne_leg_length_min": {  # 原L1602：腿过短代价候选名称，不能只按min字面猜符号。
                    "type": "leg_retraction",  # 原L1603：使用leg_retraction奖励族。
                    "mode": "below_target_per_leg",  # 原L1604：先逐腿计算短于目标的不足量再平均。
                    "target": 0.25,  # 原L1605：最短目标0.25m。
                    "before_wheel_contact_duration_s": 0.02,  # 原L1606：触地计时达到0.02秒前。
                    "contact_mode": "any_wheel",  # 原L1607：任一轮截止。
                },  # 原L1608：闭合上面的跨行表达式；不另产生奖励。
                "airborne_wheel_height_below_base": {  # 原L1609：轮底相对身体距离候选名称。
                    "type": "wheel_height_below_base_exp",  # 原L1610：绑定轮底竖直距离指数分支。
                    # target 表示轮子底部相对 base 低多少米，不是轮心高度。  [原L1611：原作者注释，不执行]
                    "target": 0.34,  # 原L1612：期望轮底在身体下0.34m，不是期望轮心世界高度0.34。
                    "sigma": 0.025,  # 原L1613：误差平方直接分母0.025。
                    "before_wheel_contact_duration_s": 0.02,  # 原L1614：任一轮接触计时达到0.02秒前有效。
                    "contact_mode": "any_wheel",  # 原L1615：任一轮接触计时达到0.02秒前有效。
                },  # 原L1616：闭合上面的跨行表达式；不另产生奖励。
                "airborne_wheel_heading_x_centering": {  # 原L1617：空中轮前后居中奖励名称。
                    "type": "wheel_heading_x_centering",  # 原L1618：绑定heading轮x指数分。
                    "wheel_contact_duration_s": 0.02,  # 原L1619：两轮接触计时都必须<0.02秒。
                    "base_contact_duration_s": 0.02,  # 原L1620：base接触计时也必须<0.02秒。
                    "wheel_heading_z_max": -0.1,  # 原L1621：两轮heading z均<-0.1m，即仍在身体下方至少10cm。
                    "sigma": 0.02,  # 原L1622：轮x误差平方的直接分母0.02。
                },  # 原L1623：闭合上面的跨行表达式；不另产生奖励。
                # "airborne_wheel_height_below_base_tight": {  [原L1624：原作者注释，不执行]
                #     "type": "wheel_height_below_base_exp",  [原L1625：原作者注释，不执行]
                #     # target 表示轮子底部相对 base 低多少米，不是轮心高度。  [原L1626：原作者注释，不执行]
                #     "target": 0.22,  [原L1627：原作者注释，不执行]
                #     "sigma": 0.005,  [原L1628：原作者注释，不执行]
                #     "before_wheel_contact_duration_s": 0.02,  [原L1629：原作者注释，不执行]
                #     "contact_mode": "any_wheel",  [原L1630：原作者注释，不执行]
                # },  [原L1631：原作者注释，不执行]
                "airborne_low_body_height": {  # 原L1632：空中身体过低的L2候选。
                    "type": "body_height_below",  # 原L1633：绑定body_height_below。
                    "threshold": 0.3,  # 原L1634：身体高度阈值0.3m。
                    "mode": "l2",  # 原L1635：L2。
                    "square_sigma": 5.0,  # 原L1636：5×高度不足²。
                },  # 原L1637：闭合上面的跨行表达式；不另产生奖励。
                "airborne_body_height_below_binary": {  # 原L1638：身体过低的二值候选。
                    "type": "body_height_below",  # 原L1639：绑定同一奖励族。
                    "threshold": 0.25,  # 原L1640：阈值0.25m。
                    "mode": "binary",  # 原L1641：只计是否低于阈值。
                },  # 原L1642：闭合上面的跨行表达式；不另产生奖励。
            }  # 原L1643：闭合上面的跨行表达式；不另产生奖励。
        )  # 原L1644：闭合上面的跨行表达式；不另产生奖励。
        self.airborne_state_machine_cfg["reward_additions"] = reward_additions  # 原L1645：保存更新后的所有定义。
        # self.rewards['foot_bound_square'] = -1.0  [原L1646：原作者注释，不执行]
        self.rewards['rear2_rear1_joint_pos_limits'] = 0.0  # 原L1647：普通rear2/rear1位置、扭矩、速度项权重0关闭，另有下面空中专用位置项。
        self.rewards['rear2_rear1_joint_pos_limits_torque'] = 0.0  # 原L1648：普通rear2/rear1位置、扭矩、速度项权重0关闭，另有下面空中专用位置项。
        self.rewards['rear2_rear1_joint_pos_limits_vel'] = 0.0  # 原L1649：普通rear2/rear1位置、扭矩、速度项权重0关闭，另有下面空中专用位置项。
        # self.rewards['airborne_undesired_contact_force'] = -1.0  [原L1650：原作者注释，不执行]
        # self.rewards['airborne_landing_down_vel'] = -1.0  [原L1651：原作者注释，不执行]
        # self.rewards['airborne_landing_down_vel_exp'] = 1.0  [原L1652：原作者注释，不执行]
        self.rewards['airborne_joint_pos_limits'] = -10.0  # 原L1653：实际启用空中软限位位置项，最终权重-10。
        # self.rewards['airborne_joint_pos_limits_vel_reg'] = -100.0  [原L1654：原作者注释，不执行]
        # self.rewards["airborne_leg_length_min"] = -40.0  [原L1655：原作者注释，不执行]
        # self.rewards["airborne_wheel_height_below_base"] = 40.0  [原L1656：原作者注释，不执行]
        self.rewards["airborne_wheel_heading_x_centering"] = 10.0  # 原L1657：实际启用空中轮x居中指数项，最终权重+10。
        # self.rewards["airborne_wheel_height_below_base_tight"] = 10.0  [原L1658：原作者注释，不执行]
        # self.rewards["airborne_low_body_height"] = -10.0  [原L1659：原作者注释，不执行]
        # self.rewards["airborne_body_height_below_binary"] = -10.0  [原L1660：原作者注释，不执行]

        self.rewards["action_rate"] = -0.002  # 原L1662：动作一阶差分权重减为-0.002。
        self.rewards["action_smoothness_leg"] = -0.005  # 原L1663：腿动作二阶差分权重-0.005。
        self.rewards["action_smoothness_wheel"] = -0.001  # 原L1664：轮动作二阶差分权重-0.001。
        self.rewards["leg_joint_acc"] = -1e-7  # 原L1665：腿关节加速度平方权重-1e-7。
        self.rewards["leg_joint_vel"] = -1e-3  # 原L1666：腿关节速度平方权重-0.001。
        self.rewards["wheel_acc"] = -2e-9  # 原L1667：轮加速度平方权重-2e-9。
        self.rewards["wheel_vel"] = -2e-6  # 原L1668：轮速度平方权重-2e-6。

        _apply_v14_airborne_landing_precontact_cfg(self)  # 原L1670：调用上面的落地配置函数，实际开启+20/+10/-10三项。
```

### Rough-v1继承与覆盖

原文件 `source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py`，L1785–L1807。注释中的行号对应本地原始字节，不使用网页渲染时压缩空行的行号。

```python
class WheelbipeV14RoughEnvCfg_v1(WheelbipeV14FlatEnvCfg_v1):  # 原L1785：Rough-v1继承Flat-v1，因此继承上面的空中奖励配置。
    rough_terrain_boundary_reset_cfg = {  # 原L1786：粗糙地形边界重置配置。
        "enabled": True,  # 原L1787：开启边界检测。
        "margin": 0.5,  # 原L1788：边缘留0.5m。
        "use_inner_terrain_area": False,  # 原L1789：不用inner区域模式。
    }  # 原L1790：闭合上面的跨行表达式；不另产生奖励。
    def __post_init__(self):  # 原L1791：组合类初始化。
        super().__post_init__()  # 原L1792：先执行父类，包含全部Flat-v1奖励设置。
        # self.predefined_reset_ground['prob'] = 0.3  [原L1793：原作者注释，不执行]
        self.predefined_reset_air = copy.deepcopy(self.predefined_reset_air)  # 原L1794：拷贝预设空中reset配置。
        self.predefined_reset_air["enabled"] = True  # 原L1795：开启预设空中reset；训练可从空中状态练落地，不等于每次都自己起跳。
        _apply_v14_rough_runtime_cfg(self)  # 原L1796：应用粗糙地形配置，打开Airborne/StepUp。
        # self.commands.resampling_time_range = (3.0, 7.0)  [原L1797：原作者注释，不执行]
        self.airborne_state_machine_cfg = copy.deepcopy(self.airborne_state_machine_cfg)  # 原L1798：再次复制空中配置用于地形命令覆盖。
        terrain_command_resample = copy.deepcopy(  # 原L1799：取原地形命令重采样配置。
            self.airborne_state_machine_cfg.get("terrain_command_resample", {})  # 原L1800：取原地形命令重采样配置。
        )  # 原L1801：取原地形命令重采样配置。
        terrain_command_resample["enabled"] = True  # 原L1802：开启进入空中时按地形采样临时命令。
        terrain_command_resample["lin_vel_x_sign_from_current"] = True  # 原L1803：保持当前前向命令符号。
        self.airborne_state_machine_cfg["terrain_command_resample"] = terrain_command_resample  # 原L1804：保存命令采样配置。
        self.rewards['wheel_power'] = -1e-5  # 原L1805：轮正机械功率代价权重-1e-5。
        self.rewards['joint_torque'] = -1e-5  # 原L1806：驱动关节扭矩平方权重-1e-5。
        self.rewards['track_lin_vel_xy'] = 1.25  # 原L1807：普通前向速度指数项权重+1.25。
```
