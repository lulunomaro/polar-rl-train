# 华南虎手动跳跃及上阶状态机实际测试

2026-11-06，北京时间。人类要求“你去找手动跳跃出发和上台阶状态机去试试”。已完成4批、每批16环境×11s首次episode的原SCUT机器人实际物理评测，原公开model1000/导出policy逐tensor误差0，0训练/优化器/SSH。不能再笼统说华南虎上不了台阶：上阶状态机适配200mm检测后，8组中1组真实双轮登顶并连续支撑7.39s；尚无满足MOD4严格200mm自主跳跃验收的教师。

## 实际结果

| 条件 | 13cm直角台阶双轮登顶 | 20cm直角台阶双轮登顶 | 触发证据 |
|---|---:|---:|---|
| manual_trigger02，手动请求 | 未测 | 0/12设置；8组实际触发 | 4/4平地及8/12台阶进入push/tuck和jump观测；其余4组未到触发位置 |
| stair_saved01，原检测范围 | 6/8 | 0/8；8组均触发墙重置 | 13cm7/8进入stair；20cm终止控制块明确wall标记 |
| stair200_01，适配检测到20cm | 7/8 | 1/8 | 13cm8/8、20cm7/8内部stair激活，真实有效高度命令0.40–0.43m |
| manual_stair200_01，两者开启 | 3/8 | 0/8 | 两个高度各8/8手动请求进入jump；20cm7/8进入stair |

表中登顶是双轮整轮越沿并真实台顶支撑，不要求停车，不等于自主跳跃成功。全部20cm测试严格静止0.5s通过数均0。single200成功env13命令vx1.8m/s、基础height.38m，台沿x1.6m，2.99s先接触立面，3.27s整轮越沿并双轮台顶接触，最长连续支撑7.39s；最大全条件静止.045s。它先碰台阶再收腿离开接触并登顶，不是台前地面提前起跳、无立面接触跳过的实证。新原USD保存姿态图已由当前模型原生审阅，0新物理回放。

## 公开接口与配置缺口

固定作者commit `1a26356d6f591734d4f6f666f5cead1a6925da67`。原始Q键回调在实际V14对象上输出“不支持手动跳跃触发”：调用的`trigger_manual_jump`不存在，可用公开方法是`request_jump_takeoff`。此次实际测试后者，不修改作者仓库。

公开保存env.yaml的state machine总开关、jump_takeoff、stair均为false；CPU检查12套保存配置也未找到jump_takeoff或stair启用的对应训练权重，rough_dash仅启用step_up扫描。因此本次在原model1000上启用状态机是新控制条件，不能称已找到作者训练好的手动跳跃专家。35维输入/6动作及原权重不变，jump观测实际置位；当前源stair onehot仍写0，但有效高度命令确实被状态机覆盖。没有偷偷修该观测接口。

原wheel_forward_scan检测范围为0.12–0.14m，wall_height.14m，20cm直接判墙结束。原配置先实测保留，再仅把检测上界/墙阈值改.25m，记录为独立条件；状态机高度范围仍.40–.43m。手动ballistic目标.70m、tracking条件关闭以发出操作者请求，push/tuck真实生效；jump外力/速度注入辅助均关闭，原DR的5–10s区间扰动仍保留。上阶成功发生在3.27s。

## 协议与边界

原SCUT机器人USD、原公开policy、IsaacSim5.1/PhysX200Hz、50Hzpolicy、本地5070TiLaptop、seed66。20cm/13cm用显式竖直阶面和水平台顶，并把实际台阶加入raycast相同地形mesh。原观测噪声、传感/动作延迟、动力学与DR保留。评测仅改场地/初始化/命令和明确列出的控制开关；不是MOD4蒸馏或MOD4已通过。

64组设置中16组13/20cm原检测、16组适配、16组组合、另4平地+12手动200mm；每组11s，首次episode，终止的整个控制块与全部后续episode从技能统计排除。400Hz MOD4验收未改；本次SCUT为200Hz，静止.5s按100实际物理tick计。saved quaternionwxyz不换序。

原快速`RESULT.json`分析器非平地台顶高度写死.2m，不能用于13cm成绩，已保留并由新`CONTROLLER_RESULT.json`按实际阶高重新分析。物理快照发生在控制更新前，单步triggerpulse不可据0值否定触发；阶段/jump观测明确，后两批另记录postcontrol脉冲。没有重跑原评测弥补日志。

首次manual_trigger01传未注册seed参数，在解析阶段退出，0物理；原日志保留，随后显式支持seed并启动02。其它4实际批次完整退出，全部root/body/force有限，保留PhysX警告及原DR扰动。原检查点SHA `d19492be858ffd431a67e5aa40afb4a4c51dc9a1c914c5c92022ed46d5868db7`；policy SHA `7a2ba09cb1d61ae59467bdba12f97f5b0f26f7565a2ad68ea88446da7eadfa15`。作者源/资产对固定commit差异为空。

证据根`N/scut_teacher_verify`：`CONTROLLER_VERIFICATION.json`、`CONTROLLER_SUMMARY.json`、`CONTROLLER_ACTUAL_NATIVE_REVIEW.json`、`CONTROLLER_CHECKPOINT_INVENTORY.json`和4批目录。各批冻结RUNNER_SOURCE、完整有效配置、调用、首次episode轨迹/接触、请求和原始日志保留；PT/NPZ/图片仅真实路径/大小/SHA索引。之前零成功测试按原条件保留，不改成成功。本次支持把它作为接触上阶候选教师继续讨论，不能把它称为已验证200mm自主跳跃专家或无依据自动蒸馏。
