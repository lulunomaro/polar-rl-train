# MOD4v3：四个 DM8009 关节＋两个 DM3519/独立 DM3520＋R1 策略

本目录是从旧 `StandardRobotpp-balance1(3).zip` 提取的独立移植工程。用户最终选择：**只更换两个轮电机，四个关节保留；电机按模型默认初始姿态标零位。**

策略使用既有交付包选中的 `r1round2_005m / iteration 22959`，35 维观测、6 维动作。STM32F407 上以 C 运行冻结策略，策略计划周期 20 ms，软件 PD 计划周期 10 ms；上位机通过 USB CDC 发送前进速度、转向速度和腿高。没有新增训练或实车烧录。

旧 LQR 底盘实现已由编译开关切出，传感器、FreeRTOS、CAN、USB 和原板级工程继续使用原 ZIP 的基础设施。独立的 `rmcs_mod4_chassis` 包提供真实 ROS 2 话题和 RMCS 插件，可与 `rmcs_auto_aim_v2` 同时运行。

## 从哪里开始

| 内容 | 位置 |
|---|---|
| Keil 工程 | `firmware/MDK-ARM/standard_robot.uvprojx` |
| 六电机 ID、方向、零偏和 IMU 安装变换 | `firmware/application/mod4_rl/mod4_hardware_config.h` |
| 模型零位图及标定方法 | `docs/ZERO_AND_WIRING.md`、`docs/model_zero_side.png` |
| 冻结 C 策略与权重 | `firmware/application/mod4_rl/mod4_runtime.c`、`policy_weights.h` |
| 上位机源码 | `upper/ros2_ws/src/rmcs_mod4_chassis` |
| 上位机使用 | `docs/UPPER_COMPUTER.md` |
| USB/CAN 单位、帧定义 | `docs/PROTOCOL.md` |
| 实际构建、失败和修复 | `reports/`、`docs/ATTEMPTS.md` |

**`MOD4_HARDWARE_CALIBRATION_VERIFIED` 当前为 0。** ID、正反方向、编码器读数和 IMU 安装方向尚未在这台实车上测量，因此交付配置拒绝使能输出。软件已准备好接受这些实测值；不要把模板里的 `+1` 方向、`0` 编码器读数当成已测量结果。

## 模型零位的含义

采用 MOD4v3 模型默认初始姿态，即 Newton 关节位移为 0。对应绝对 MJCF 关节角：前关节 `+0.7783382074 rad`，后关节 `−0.4806332577 rad`，左右相同。把实车摆到这幅模型姿态后，记录四个编码器读数到 `encoder_zero`。

固件转换为 `q_model = model_reference + sign × (p_encoder − encoder_zero) / internal_ratio / external_reduction`。策略里的 `mod4_q0` 保持原值；这样在标定姿态，策略看到的腿部相对位置约为 0，不需要为修改编码器参考而重训。详见零位说明。

此前的“气弹簧 200 mm、后折贴地”继续作为已测试的起立姿态。它对应不同的模型关节角，不再作为电机零位。

## 已有验证与边界

冻结 C 策略与原交付包的 16 组参考向量对比：观测一致，动作最大绝对误差约 `2.15e-6`，目标最大绝对误差约 `2.29e-5`。CAN 编解码、3519 速度单位、驱动参数回读、使能/急停、数据超时和 USB 流解析均有离线测试。

完整 STM32 工程使用 ARMCC 5.06 update 6 编译，具体最终尺寸、ROS/RMCS 构建及回环结果以 `reports/` 和阶段验证记录为准。主机测试不能测得 STM32 实际推理耗时；上机仍需测量 20/10 ms 调度、栈余量与 CAN 延迟。

旧的起立结果来自原标称执行器模型，不是换装 DM3519 后的实车证明。3519 原厂额定转矩 3.5 N·m、峰值 7.8 N·m、24 V 标称空载 435 rpm；当前策略原标称轮电机包络不同。实车的转矩响应、电压、外置传动比和热负荷需要实测后确认，不能仅凭通信接通就宣称 sim2real 完成。

原始 ZIP、模型资产、策略交付包、上游自瞄代码及运行中的训练目录均未原地修改。来源哈希、实际尝试和阶段归档索引随工程保存。
