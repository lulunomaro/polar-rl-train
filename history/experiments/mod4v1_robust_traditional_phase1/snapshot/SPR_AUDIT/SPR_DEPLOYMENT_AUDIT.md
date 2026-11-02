# SPR Balanced-infantry 源码与 MOD4v1 部署适配审计

**模式：SRC_ONLY；日期：2026-11-02；结论等级：源码证据 + 静态算术检查。**

## 1. 关键结论

1. **SPR 参考底盘是作者声明的“妙板02”，工程目标为 STM32H723VGTx / Cortex-M7；另一个云台工程才是作者声明的 DJI C 板，目标 STM32F407IGHx / Cortex-M4。** 作者声明和 MCU/外设工程相互印证，但这不是对当前 MOD4v1 实物主板的识别。DJI 版权注释也不是“该底盘使用 DJI C 板”的证据。[外层说明:1](<reference_selected/SPR Balanced-infantry/readme.txt#L1>)、[底盘工程:10–21](<reference_selected/chassis/chassis/MDK-ARM/Balanced-infantry.uvprojx#L10-L21>)、[云台工程:10–21](<reference_selected/gimbal/gimbal/MDK-ARM/sentry.uvprojx#L10-L21>)。
2. **SPR 主链为四个 DM_J8009 关节 + 两个 3508 协议轮毂；目标 MOD4v1 的全达妙要求是另一套硬件契约。** 原参考的 3508 电流映射、轮半径、减速比、关节零位和限值均不应直接移入目标 DM3519/DM8009P。[协议声明:6–22](<reference_selected/chassis/chassis/application/CAN_receive.h#L6-L22>)、[轮毂反馈:32–58](<reference_selected/chassis/chassis/application/CAN_receive.c#L32-L58>)。
3. **可复用的是分层思路与接口，不是未经校准的整份固件。** 源码确有腿长调度 LQR、VMC、BMI088/QEKF、速度 KF、倒地/起立、跳跃/落地、台阶、离地/撞击分类和功率管理分支；其中有明确的域限制及静态缺陷。
4. **当前底盘的 MPC 只是 A/B 矩阵初始化文件。** 独立 LinearMPC 包确有上游模板和生成说明，作者也写过板上部署经历；三者不等于“这份底盘主链已运行完整 MPC”。TinyMPC 仅是作者尚未实现的想法。[底盘 MPC:1–31](<reference_selected/chassis/chassis/algorithm/MPC.c#L1-L31>)、[说明:3–9](<reference_selected/SPR Balanced-infantry/readme.txt#L3-L9>)。
5. **自转源码不是固定连续 4π rad/s 资格证据。** 实际命令按循环计数切换 −13/−9/−5/−9 rad/s；没有本轮实测的恒定 4π、自转起停/反向、与 2m/s 平动或跳跃组合的功率/速度包络。[自转设定:249–284](<reference_selected/chassis/chassis/application/chassis_behaviour.c#L249-L284>)。
6. **本轮没有编译/运行固件、烧录、SSH、仿真或训练；没有操作父运行任务或 Git。** 独立 [HAL 接口建议](<portable_hal_proposal.h>) 只有声明；[15 项编解码/算术检查](<codec_vectors_spr.json>) 是 Python 标准库对已读公式的复算，不是 C ABI、总线、台架或实物验证。

## 2. 范围、原包与可追溯性

遵循 [本轮范围](<../TASK_SCOPE.md>)。本会话技能目录只有 Office/PDF 与 Windows ACL；本任务无匹配动作、无 ACL 异常，因此使用已有 filesystem/read/glob/grep、PowerShell 与 Python 标准库 `zipfile`，未虚构专用技能。

| 对象 | 字节数 | SHA256 |
|---|---:|---|
| 原 ZIP（仅只读） | 192,257,143 | `59254da5a2e8d480fee109022e9586c029a566024eda33e7b6c21477de866047` |
| 外层成员 `code/chassis.zip`（只在内存打开） | 122,201,554 | `e8850d0d7b47929b428b967899f76ef010eb4e86100ef922f2146c40d119f133` |
| 外层成员 `code/gimbal.zip`（只在内存打开） | 6,068,702 | `7f76d5fe788f0d37608f2d9e7514defab04fe65ae1fdf99037a889ab31f63617` |
| 外层成员 `Futile/LinearMPC.jl-main.zip`（只在内存打开） | 184,254 | `33f33f4be90abddf02eeab11b88b769bcd3a412653e4a9417a5d72cbae38c6cf` |

- 原包路径：`C:\Users\lulu\Downloads\SPR Balanced-infantry (1).zip`。先列外层中央索引，再列必要嵌套索引；外层 **21** 条、底盘 **2,140** 条、云台 **450** 条、LinearMPC **76** 条，包含目录条目。
- 只选择 **72 个文本成员**，原成员合计 **627,982 bytes**，UTF-8 引用副本 **639,356 bytes**。仅约 0.33% 原 ZIP 大小的选中文本落盘；没有保存嵌套大 ZIP 或全量工程。[完整成员/哈希索引](<SPR_SOURCE_INDEX.json>)、[外层中央索引](<zip_central_index.json>)、[底盘中央索引](<chassis_central_index.json>)、[云台中央索引](<gimbal_central_index.json>)、[MPC 中央索引](<LinearMPC.jl-main_central_index.json>)。
- 每个选中成员保留原成员字节数/SHA256/CRC32、原编码、UTF-8 副本字节数/SHA256、行数、完整行链接；重要结论另有 **76 个已核验行区间**。GB18030→UTF-8 只转编码，保留换行结构，故原/副本 SHA 不同是有记录的转换而非源码修订。
- 提取器只接受精确白名单的文本成员，并校验相对路径、上级穿越、盘符/反斜杠、符号链接、文件类型/大小、目标根目录与 NUL；`zipfile.read` 校验所选成员 CRC。没有执行压缩包中的脚本、编译命令、清理脚本或说明里的命令。
- 学习数据头 `knn_model.h`、`knn_impact_model.h` 仅保留中央索引元数据，**不提取训练样本/聚类中心**。未打开 KNN/LESO/MATLAB 子包；未读取 PCB/epro2、草稿图、预编译固件/调试大件、凭据或无关目录。
- 末次复核原 ZIP 字节数/SHA 未变，72 个副本哈希全部相符；操作错误原样日志为 [ERRORS.jsonl](<ERRORS.jsonl>)，目前 0 bytes，摘要见 [审计错误记录](<AUDIT_ERRORS.md>)。校验结果见 [validation_results.json](<validation_results.json>)。

## 3. 板型与硬件绑定证据

### 3.1 参考板与目标板严格分开

| 层次 | 已取得的证据 | 结论边界 |
|---|---|---|
| SPR 底盘板 | 外层说明直接写妙板02；底盘 MCU 为 STM32H723VGTx，LQFP100，三路 FDCAN；调试笔记多处提及 DM02 电源/温控 | **参考工程的目标与 DM02 叙述相符**，没有本轮实物读板/引脚测量 |
| SPR 云台板 | 外层说明写 C 板；独立云台 Keil 工程为 STM32F407IGHx、Cortex-M4 | 说明与典型 DJI C 板 MCU 家族一致，不代表该云台工程可直接成为轮腿底盘 BSP |
| MOD4v1 最终板 | 用户允许 DJI C 板或达妙主板；尚无本轮实物/BSP 绑定 | **候选仍为两种**，达妙电机品牌不确定主控品牌/型号 |

附证：[底盘 MCU/外设:317–386](<reference_selected/chassis/chassis/Balanced-infantry.ioc#L317-L386>)、[DM02 笔记:138–145](<reference_selected/chassis/chassis/user/readme.txt#L138-L145>)、[DM02 电源笔记:202–211](<reference_selected/chassis/chassis/user/readme.txt#L202-L211>)。云台的[通用功能说明:14–23](<reference_selected/gimbal/gimbal/README.md#L14-L23>)还写着麦克纳姆轮，属于继承说明，优先级低于当前底盘调用链。

### 3.2 SPR 中可确定的总线与单位

| 角色 | 发送路径/标识 | 接收标识 | 单位/范围/说明 |
|---|---|---|---|
| 右后关节 | FDCAN2，`0x01` | `0x001` | J8009，MIT 风格扭矩帧 |
| 右前关节 | FDCAN2，`0x02` | `0x002` | 同上 |
| 左前关节 | FDCAN1，`0x03` | `0x003` | 同上 |
| 左后关节 | FDCAN1，`0x04` | `0x004` | 同上 |
| 左轮 | FDCAN1，`0x200` 第 1 电流槽 | `0x201` | 3508 格式，ECD/RPM/raw current |
| 右轮 | FDCAN2，`0x200` 第 2 电流槽 | `0x202` | 3508 格式，独立总线 |
| 底盘→云台 | FDCAN3，`0x031` | 云台→底盘 `0x081/0x082` | 量化指令、腿长、相对 yaw、功率限值 |
| 超电容反馈 | 未见此选中发送函数 | `0x051` | float 功率、限值和能量百分数形式 |

发送总线映射见 [关节/轮毂发送:198–347](<reference_selected/chassis/chassis/application/CAN_receive.c#L198-L347>)、[发送任务角色:70–75](<reference_selected/chassis/chassis/Task/send_task.c#L70-L75>)。**接收回调自身不分总线，只按 Identifier 分派**；上表 bus 是发送路径推导的预期拓扑，而不是经运行抓包验证的 Rx 约束。

- 三路配置为 **Classic CAN、1 Mbps**；FDCAN 时钟 96MHz，`96e6/(3*(1+23+8))=1e6`。引脚：CAN1 PD0/PD1；CAN2 PB5/PB6；CAN3 PD12/PD13。[配置:255–307](<reference_selected/chassis/chassis/Balanced-infantry.ioc#L255-L307>)、[时钟:597–610](<reference_selected/chassis/chassis/Balanced-infantry.ioc#L597-L610>)、[引脚:194–267](<reference_selected/chassis/chassis/Core/Src/fdcan.c#L194-L267>)。不是 CAN-FD/BRS 带宽资格。
- DM 源码字段为位置 rad /速度 rad·s⁻¹ /扭矩 N·m，量化分别 16/12/12 bits；**实际位置常量 ±3.14，旁注却仍称 ±12.5**；速度 ±45，扭矩 ±54。应以电机实际固件参数匹配，既不靠注释推断，也不自动映射到目标 ±40Nm。[范围:8–22](<reference_selected/chassis/chassis/application/CAN_receive.h#L8-L22>)、[解码:60–109](<reference_selected/chassis/chassis/application/CAN_receive.c#L60-L109>)。
- 关节扭矩帧前 6 字节为零，末 12 位填扭矩；位置/速度目标编码也是零码，但因 Kp/Kd=0 不贡献反馈项。源码发送全 `FF...FC` 初始化、`FF...FB` 状态恢复；没有读回协议模式、位置范围、CAN 主从 ID 寄存器的过程。其确切语义仍应按目标型号/固件绑定。[量化/发送:175–222](<reference_selected/chassis/chassis/application/CAN_receive.c#L175-L222>)、[初始化:398–442](<reference_selected/chassis/chassis/application/CAN_receive.c#L398-L442>)、[重试:586–615](<reference_selected/chassis/chassis/application/CAN_receive.c#L586-L615>)。
- 轮半径是 **0.065m**；输出扭矩限值宏 **3.3**；控制到 raw current 的系数是 `3608.020604302*(268/17)/13.94`。反馈用 `rpm*pi/30/268*17`，扭矩反馈包含 `20/16384`、0.3、3591/187 和 268/17。源码没有可信的单一减速域契约；这些不是目标 DM3519 驱动参数。[常量:47–55](<reference_selected/chassis/chassis/Task/chassis_task.h#L47-L55>)、[反馈:32–55](<reference_selected/chassis/chassis/application/CAN_receive.c#L32-L55>)、[控制映射:652–656](<reference_selected/chassis/chassis/Task/chassis_task.c#L652-L656>)。

### 3.3 零位、极性与减速域

实际参考零位/符号：左后 `wrap(P−0.54)`；左前 `wrap(P−3.78+1.28)`；右前 `−wrap(P+4.25)`；右后 `−wrap(P−2.4)`。左速度取正、右速度取负；VMC 左侧关节扭矩直接用 T，右侧取 −T；轮速计算左 `+speed_rads`、右 `−speed_rads`。[零位/速度:226–254](<reference_selected/chassis/chassis/Task/chassis_task.c#L226-L254>)、[VMC 输出极性:737–745](<reference_selected/chassis/chassis/Task/chassis_task.c#L737-L745>)、[轮速符号:522–535](<reference_selected/chassis/chassis/Task/chassis_task.c#L522-L535>)。

没有发现主动设置电机零点的完整校准流程，现有方式是软件偏置。关节数值看似已在减速器输出域使用，源码没有据此确认其内部减速比。目标适配应将编码器域、减速器输出域和机械关节域分清，保证减速比只转换一次。

### 3.4 父代理提供的目标 MOD4v1 参数（不是 SPR 事实）

以下由父代理在本轮消息中转述其已读旧模型与历史确认，**本子代理没有另读旧文件或验证实物**：

| 目标项 | 父代理转述值 | 与 SPR 的差异 |
|---|---|---|
| 关节 | DM8009P×4，24V，peak 40Nm / continuous 20Nm，内部 9:1 | SPR 写 DM_J8009，通信范围 ±54Nm；不可混用扭矩限值或重复乘 9 |
| 轮毂 | DM3519×2，替换总减速箱 15.8:1 | SPR 主链为 3508 格式；不可照搬 raw current 映射 |
| 轮扭矩 | peak 5.775909774Nm / continuous 2.59175Nm | 仍应区分轴侧、输出侧与持续时间 |
| 轮半径 | 0.0625m | SPR 为 0.065m |
| 尚估算项 | 转矩—转速曲线、armature 等 | 历史参数/用户要求不等于完整实物辨识 |

## 4. 主控制链：真实存在与缺口

### 4.1 估计与 IMU

- 活跃入口是 **BMI088 SPI**，加速度配置 3g/800Hz，陀螺仪 2000°/s 档/1000Hz 带宽配置，读数依标量转 SI；没有同频同步采样时间戳。[BMI 配置:64–89](<reference_selected/chassis/chassis/boards/BMI088driver.c#L64-L89>)、[SI 系数:9–18](<reference_selected/chassis/chassis/boards/BMI088driver.h#L9-L18>)、[读取:226–259](<reference_selected/chassis/chassis/boards/BMI088driver.c#L226-L259>)。
- QEKF、重力扣除、body↔earth 变换真实存在；dt 固定 0.001s，运动加速度 LPF=0.0085。最终 `INS_data` 又做了轴交换与负号映射：yaw/pitch 取负，roll 取正，ax 取 `−MotionAccel_n[1]`，wy 取 `−Gyro[0]`，wz 取 `−Gyro[2]`。[主流程/符号:77–125](<reference_selected/chassis/chassis/Task/INS_task.c#L77-L125>)、[LPF:156–175](<reference_selected/chassis/chassis/Task/INS_task.c#L156-L175>)。
- **未在已审计估计链中找到 IMU 杆臂 `alpha×r` 与 `omega×(omega×r)` 修正。** 世界系加速度通过固定轴映射进入前向速度 KF，持续 yaw 时应重新审核与机体前向轴的一致性。仅有姿态重力补偿不覆盖偏置安装的切向/向心加速度。
- 速度 KF 状态 `[v,a]`、H=I，轮/腿运动学速度与 IMU 加速度作为量测；R 为 `diag(100,1e12)`，因此加速度量测被极强降权，不能按“已充分融合 IMU 防滑”记账。位置仅在 `|v|≤0.1` 时积分，否则清零。[KF 参数:32–43](<reference_selected/chassis/chassis/Task/chassis_task.c#L32-L43>)、[融合/积分:258–288](<reference_selected/chassis/chassis/Task/chassis_task.c#L258-L288>)、[运动学速度:522–535](<reference_selected/chassis/chassis/Task/chassis_task.c#L522-L535>)。
- QEKF 注释称没用卡方检测，但后面真实存在残差/卡方更新分支；应依函数内容而非简化注释判断。同样，旧调试笔记称温控 36°C，活跃函数实际目标 **45°C**、48°C 截断。[QEKF 更新:499–554](<reference_selected/chassis/chassis/Task/INS_task.c#L499-L554>)、[温控:129–142](<reference_selected/chassis/chassis/Task/INS_task.c#L129-L142>)。这些值不应抄到未确认的目标板。

### 4.2 LQR/VMC、接触与 FSM

- 主任务顺序：模式→反馈→设定→控制→轮发送；关节另由发送线程发送。[主任务:96–158](<reference_selected/chassis/chassis/Task/chassis_task.c#L96-L158>)、[RTOS 线程:117–130](<reference_selected/chassis/chassis/Core/Src/freertos.c#L117-L130>)。
- LQR 是腿长平均值调度的 2×6 增益，12 项按交错顺序使用；有效系数是 `if(0)` 后的 else 分支，前一组/注释示例不是活跃控制参数。[增益选择:131–219](<reference_selected/chassis/chassis/algorithm/LQR_K.c#L131-L219>)、[应用:588–623](<reference_selected/chassis/chassis/Task/chassis_task.c#L588-L623>)。
- VMC 的 forward kinematics/Jacobian/force mapping 为生成 C，硬编码 0.21/0.25m 等参考机械尺寸；不能自动代表新 MOD4v1 闭链几何。[腿位置:92–113](<reference_selected/chassis/chassis/algorithm/leg_position.c#L92-L113>)、[腿力:54–111](<reference_selected/chassis/chassis/algorithm/leg_force.c#L54-L111>)。
- FSM 实际分散在模式函数和任务 `switch/if-else`，不是只有一个“stateMachine”标签：`FALLING_DOWN→FALLING_TO_STANDING→STANDING`、`ZERO_FORCE`、调试模式、`CLIMB_THE_STAIRS`；跳跃有蹲/伸/收/软落地/返回；台阶有倒地/转腿/收腿。[枚举:75–84](<reference_selected/chassis/chassis/Task/chassis_task.h#L75-L84>)、[状态枚举:163–190](<reference_selected/chassis/chassis/Task/chassis_task.h#L163-L190>)、[恢复状态:404–518](<reference_selected/chassis/chassis/Task/chassis_task.c#L404-L518>)。
- 接触支持力估计、离地 KNN 调用、时间窗撞击 KNN 确有实现；源注释承认采样域限制和误判。学习表未提取，故不报告分类器样本量、泛化率或鲁棒性合格。[支持力:537–570](<reference_selected/chassis/chassis/Task/chassis_task.c#L537-L570>)、[离地调用:666–731](<reference_selected/chassis/chassis/Task/chassis_task.c#L666-L731>)、[撞击窗口:10–77](<reference_selected/chassis/chassis/algorithm/ClimbKNN.c#L10-L77>)。
- 台阶触发门限有腿长≥0.29、计数400、前进指令≥0.2和撞击分类器；跳跃软落地有计数220。均是**循环次数**，不是经过时间戳计量的 400ms/220ms 保证。[台阶触发:372–400](<reference_selected/chassis/chassis/Task/chassis_task.c#L372-L400>)、[跳跃:827–896](<reference_selected/chassis/chassis/Task/chassis_task.c#L827-L896>)、[台阶动作:977–1062](<reference_selected/chassis/chassis/Task/chassis_task.c#L977-L1062>)。
- 未得到“270mm 台阶 + 落地恢复”本轮数据证据。源码注释提及 150/200mm 阈值难共用，不能据此外推 270mm。[限制说明:375–380](<reference_selected/chassis/chassis/Task/chassis_task.c#L375-L380>)。
- 有积分分离、积分/输出夹紧，但未见统一的执行器饱和反馈抗饱和链；普通模式 vx 直接赋值，自转指令阶跃，未形成统一加速度/jerk/防倾翻命令整形。[PID:63–95](<reference_selected/chassis/chassis/algorithm/PID.c#L63-L95>)、[速度设定:165–174](<reference_selected/chassis/chassis/application/chassis_behaviour.c#L165-L174>)。

### 4.3 MPC 与遗留文件辨别

| 项目 | 实际存在 | 本次证据等级 |
|---|---|---|
| 活跃底盘 LQR/VMC | Keil 文件项和真实调用均有 | `SRC_PRESENT / ACTIVE_SOURCE` |
| 底盘 MPC | 31 行 A/B 与 `MPC_Init`，Keil列入文件项；所读主链无该初始化/求解调用 | `MATRIX_STUB`，不是完整 MPC |
| 独立 LinearMPC | Julia 上游包、C模板、`mpc_compute_control`/DAQP 引用与使用笔记 | `REFERENCE_PACKAGE`，未生成/链接本机控制器 |
| 作者“上妙板部署”经历 | 外层说明中的陈述 | `AUTHOR_DESCRIPTION`，无本轮时延/二进制/台架证据 |
| TinyMPC | 作者说明尚未实现 | `IDEA_ONLY` |
| Unitree A1 RS485/WIT UART IMU | 源码文件确实在 ZIP；当前 Keil文件项未列入，主入口未启用 | `PRESENT_LEGACY`，不据此推断当前电机/传感器 |

证据：[Keil 文件项:423–509](<reference_selected/chassis/chassis/MDK-ARM/Balanced-infantry.uvprojx#L423-L509>)、[MPC 模板:24–53](<reference_selected/LinearMPC.jl-main/LinearMPC.jl-main/codegen/mpc_update_qp.c#L24-L53>)、[生成说明:42–71](<reference_selected/LinearMPC.jl-main/LinearMPC.jl-main/使用linerMPC.txt#L42-L71>)、[上游支持说明:49–55](<reference_selected/LinearMPC.jl-main/LinearMPC.jl-main/README.md#L49-L55>)、[A1 遗留:22–58](<reference_selected/chassis/chassis/application/RS485_Receive.c#L22-L58>)、[WIT 遗留:1–13](<reference_selected/chassis/chassis/application/IMU_Receive.c#L1-L13>)。使用笔记中的 Python `lmpc` 代码与包名 Julia 还需区分；未执行这些说明命令。

## 5. 移植前应隔离的静态问题

以下是源码层发现，不冒充已经实物复现；原选中文本未修订。

| ID / 优先级 | 源码事实与影响 | 适配动作 |
|---|---|---|
| FAULT-01 / 高 | 电机离线时先发关节零扭矩，随后进入独立 DBUS 分支；DBUS正常且非ZERO模式时又发正常扭矩，同轮保护被覆盖 | 单一输出仲裁，fault后整轮锁存，清空/失效旧队列；禁止故障分支跌落正常发送 |
| POWER-01 / 高 | 功率衰减右侧写 `Right_Leg.Tp` 而非 `Wheel_Right.Tp`；`MovePower+TurnPower` 无零分母保护；预算用预测总功率减平衡功率，不是严格可用功率减平衡功率 | 重写为包括六个执行器和损耗的有界预算，零/负余量保护，平衡优先，过期超电容信息降级 |
| CAN-02 / 高 | `rx_data[0]>>8|rx_data[1]` 丢高字节；Rx不校验bus/DLC/读消息返回值；共享全局 Header/payload 跨线程使用且无单一发送者 | 显式大小端/长度/总线/ID/状态检查；帧私有快照；唯一队列所有者；检查enqueue与总线完成 |
| GEOM-01 / 高 | IK的 `acos` 不限域；0.50m宏超过该IK约0.459121m可达长度；生成Jacobian含sqrt/除法无奇异保护 | 基于实际闭链再生成/验证；可达域+支路+有限值保护；奇异时降级，禁止NaN转电机整数 |
| EST-01 / 高 | 无杆臂补偿；世界/机体前向轴混用需审查；加速度R=1e12；固定dt | 统一坐标和SI，量测时间戳、杆臂修正、接触/滑移门控、噪声标定及创新统计 |
| GEAR-01 / 中高 | 命令中 `(268/17)` 是整数15，比实数小4.850746%；反馈比与13.94修正也不一致 | 单一有类型的总减速域配置；去3508映射，按目标DM3519协议/输出域重新标定 |
| YAW-01 / 中高 | `YawTotalAngle=YawRoundCount+Yaw`，计数未乘2π；z零偏固定0 | 连续yaw使用正确unwrap/积分与漂移处理；测试跨±π、多圈、起停与反向 |
| TIME-01 / 中高 | 1000Hz tick +相对delay +200us忙等；错误恢复还HAL_Delay20；共享测量快照无一致性保障 | 用单调时钟/绝对调度、非阻塞恢复、快照/队列时间戳，测WCET/排队/实际发送尾延迟 |
| FSM-01 / 中 | 部分状态等待角度/腿长无统一时间上限，初始化可无限等电机状态；220/400等是循环计数 | 每状态明确前置条件/超时/退出/故障恢复；command freshness与观测有效性一同门控 |
| CONTACT-01 / 中 | `wheel_dx`为左右求和乘r，命名avg却未除2；分类器数据可能依赖该旧尺度，注释示例特征顺序与调用顺序不同 | 先定义特征契约再重采样校准；不要只改/2后假定旧分类器仍适用 |
| MAP-01 / 中 | 自救左腿设定取 `LeftLength` 而非接收的 `LeftLengthSet`；气弹簧补偿左右交叉引用 | 分清command/telemetry，按物理左右侧复核，独立小算例后再集成 |

精确行证：[离线后落入正常分支:29–78](<reference_selected/chassis/chassis/Task/send_task.c#L29-L78>)、[功率预测:1064–1085](<reference_selected/chassis/chassis/Task/chassis_task.c#L1064-L1085>)、[功率错误字段/分母:1145–1165](<reference_selected/chassis/chassis/Task/chassis_task.c#L1145-L1165>)、[高字节:123–130](<reference_selected/chassis/chassis/application/CAN_receive.c#L123-L130>)、[Rx入口:9–30](<reference_selected/chassis/chassis/application/CAN_receive.c#L9-L30>)、[IK:138–150](<reference_selected/chassis/chassis/algorithm/leg_position.c#L138-L150>)、[yaw累计:298–313](<reference_selected/chassis/chassis/Task/INS_task.c#L298-L313>)、[轮速度尺度:527–534](<reference_selected/chassis/chassis/Task/chassis_task.c#L527-L534>)、[自救字段:288–299](<reference_selected/chassis/chassis/application/chassis_behaviour.c#L288-L299>)、[气弹簧分配:956–974](<reference_selected/chassis/chassis/Task/chassis_task.c#L956-L974>)。

附：[离线监测:215–232](<reference_selected/chassis/chassis/Task/detect_task.c#L215-L232>)的DBUS离线阈值500tick、各电机100tick是参考设置，不自动成为新目标的故障响应要求。接收 `0x081/0x082` 都刷新同一DBUS钩子，功率/模式数据应分别带年龄。

### 5.1 本轮纯算术 test vectors

[检查程序](<codec_vectors_spr.py>)仅复写已读公式，没有读取并执行源码。**15 checks pass / 0 fail**：

- 扭矩 −54/0/+54Nm → raw12 `0 / 2047 / 4095` → payload `00 00 00 00 00 00 00 00` / `00 00 00 00 00 00 07 ff` / `00 00 00 00 00 00 0f ff`；越界±108按源码夹到±54。
- 零扭矩量化返回约 −0.0131868Nm，是12位有符号区间截断的半格偏差，不是代码发了精确浮点0。
- `0x12,0x34` 的功率字段，原表达式得52，按大端合成应4660；C整数 `268/17` 得15，实数比15.76470588。
- IK在0.50m时 `acos` 参数约1.10494569；可达上界约0.45912127m。

完整输入/输出和行证见 [向量结果](<codec_vectors_spr.json>)。Python为float64，只对这些代表点复核算术；未证明所有float32边界、目标固件配置或真实电机行为。

## 6. 可复用模块与纯 C/C++ 适配边界

| 引用模块 | 可借鉴部分 | 迁移条件 |
|---|---|---|
| [leg_position](<reference_selected/chassis/chassis/algorithm/leg_position.c#L74-L114>) / [leg_speed](<reference_selected/chassis/chassis/algorithm/leg_speed.c#L25-L111>) / [leg_force](<reference_selected/chassis/chassis/algorithm/leg_force.c#L24-L112>) | FK/Jacobian/VMC纯计算函数形式 | 用新模型的几何/闭链分支再生成；有限值/可达/奇异保护；不复用有未初始化L1的遗留JointToLeg |
| [LQR_K](<reference_selected/chassis/chassis/algorithm/LQR_K.c#L131-L219>) | 腿长调度增益接口、2×6状态顺序 | 新质量/惯量/电机/延迟模型重新设计；剥离main/HAL/全局状态依赖 |
| [PID](<reference_selected/chassis/chassis/algorithm/PID.c#L40-L95>) | 显式state对象、积分分离 | 实测dt、抗饱和、滤波、完整reset，分清单位与输入/输出符号 |
| [KalmanFilter](<reference_selected/chassis/chassis/algorithm/kalman_filter.h#L25-L45>) | 矩阵/估计器抽象 | 原实现依CMSIS矩阵和malloc/pvPortMalloc；换固定存储或调用方arena，检查矩阵状态/分配失败 |
| [INS主流程](<reference_selected/chassis/chassis/Task/INS_task.c#L62-L125>) | 采样→姿态→重力补偿→导航加速度分层 | 与SPI/PWM/RTOS拆分；传感器旋转/杆臂/时间戳/重力定义参数化 |
| [FSM实现](<reference_selected/chassis/chassis/Task/chassis_task.c#L345-L518>) | 分离ground/recovery/jump/flight/landing/step思路 | 纯输入/输出FSM，所有持续窗口用时间；统一输出仲裁，参数重新验证 |
| [CAN编解码](<reference_selected/chassis/chassis/application/CAN_receive.c#L175-L222>) | 显式量化位宽/字节顺序 | 依目标型号绑定MIT范围/ID/反馈域；静态配置≠电机实际配置；不复用3508映射 |
| [MPC上游模板](<reference_selected/LinearMPC.jl-main/LinearMPC.jl-main/codegen/mpc_update_qp.c#L24-L53>) | allocation-free生成器/返回exitflag接口 | 需完整DAQP及生成常量、模型/约束、迭代/时间预算、求解失败/超时LQR降级；当前不算部署完成 |

独立新增 [portable_hal_proposal.h](<portable_hal_proposal.h>) 约定：

- **核心只用SI/机械输出域**：rad、rad/s、N·m、m、s、W；统一x前/y左/z上、右手正向。电机position/velocity/torque的符号、零点、减速域分别显式配置。
- **硬件边界**：`capture_snapshot`、`monotonic_now_us`、`enqueue_torques`、`latch_output_gate`、watchdog；候选主板保留DJI C/达妙两条，均不含确认的pin map或默认驱动。
- **原始IMU语义**：specific force与角速度进入估计器；旋转矩阵 `R_body_sensor`、参考点→IMU杆臂独立配置。修正 `a_ref=R*f+g−alpha×r−omega×(omega×r)`，各量在同一body系计算，再投影所需控制轴。
- **时序与可观测性**：每个输入带sample timestamp/sequence/valid/clipped；指令带expiry；输出带compute/deadline/sequence；收据分queue accepted/on-bus，均不冒充实际电机扭矩生效时刻。
- **统一门控与求解器预算**：未知绑定不使能；fault锁存先于发送；MPC迭代/时延/非有限值超限走有界LQR或失能，记录真实原因。核心不接收仿真world-position/world-velocity/contact truth作为部署输入。
- 头文件**仅设计接口，不含实现、BSP、调参结果、烧录镜像或已完成硬件声明**。

## 7. 编译入口、依赖与 license

### 编译入口与状态

- 底盘入口为 [Keil工程](<reference_selected/chassis/chassis/MDK-ARM/Balanced-infantry.uvprojx#L10-L21>)，ARMCC **5.06 update7 build960**，`uAC6=0`，H7 DFP4.0.0；C99与`ARM_MATH_CM7`等宏见[编译选项:328–342](<reference_selected/chassis/chassis/MDK-ARM/Balanced-infantry.uvprojx#L328-L342>)。scatter map覆盖Flash/DTCM/AXI/SRAM区，见[链接布局:5–30](<reference_selected/chassis/chassis/MDK-ARM/Balanced-infantry/Balanced-infantry.sct#L5-L30>)。
- 主入口外设/RTOS创建见[main:104–132](<reference_selected/chassis/chassis/Core/Src/main.c#L104-L132>)； `.ioc`仅自动生成defaultTask配置，手写RTOS还含INS/chassis/send/detect/referee，单靠重新生成 `.ioc` 不保证保留控制线程。[ioc任务项:308–310](<reference_selected/chassis/chassis/Balanced-infantry.ioc#L308-L310>)、[实际线程:117–130](<reference_selected/chassis/chassis/Core/Src/freertos.c#L117-L130>)。
- [工程文件清单核对](<build_entry_map.json>)：底盘93项、云台121项，相对路径在各嵌套ZIP中央索引均可找到（Windows大小写不敏感比较）。这只证明所列文件存在；不证明链接/内存/ABI/运行通过。通用CMSIS子目录的CMake不等于完整底盘CMake入口。
- 本地只查询PATH中已装工具，找到 **MinGW GCC 6.3.0**；未在PATH发现ARMCC/armclang/arm-none-eabi-gcc/UV4。没有遍历安装目录，也没安装或触发构建。[工具清单](<toolchain_inventory.json>)、[版本原文](<gcc_version.txt>)。
- 原包内已有对象/映像/调试材料未提取或执行，不拿它们当当前目标可部署性证明。ARMCC5→ARMCLANG/GCC、M7→M4还涉及浮点、CMSIS库、RTOS port、DMA/cache/内存区和三总线→两总线重新规划。

### License 证据

| 组件 | 本地证据 | 复用注意 |
|---|---|---|
| CMSIS、DSP | [Apache 2.0](<reference_selected/chassis/chassis/Drivers/CMSIS/LICENSE.txt#L1-L5>)、[DSP license](<reference_selected/chassis/chassis/Middlewares/Third_Party/ARM/DSP/LICENSE.txt#L1-L5>) | 随组件保留文本/声明 |
| ST H7 HAL | [Package_license/BSD-3-Clause fallback](<reference_selected/chassis/chassis/Drivers/STM32H7xx_HAL_Driver/LICENSE.txt#L1-L6>) | 按实际发放组件条件核对 |
| ST H7 CMSIS device | [Apache-2.0 fallback](<reference_selected/chassis/chassis/Drivers/CMSIS/Device/ST/STM32H7xx/LICENSE.txt#L1-L6>) | 与HAL条款不同 |
| FreeRTOS | [MIT风格授权原文](<reference_selected/chassis/chassis/Middlewares/Third_Party/FreeRTOS/Source/LICENSE#L1-L17>) | 保留copyright/notice |
| LinearMPC.jl | [MIT](<reference_selected/LinearMPC.jl-main/LinearMPC.jl-main/LICENSE#L1-L21>) | 其DAQP依赖另核来源/版本/条款 |
| SPR自定义业务代码 / DJI继承代码 / MATLAB生成函数 | [SPR版权注释](<reference_selected/chassis/chassis/application/chassis_behaviour.h#L1-L10>)、[DJI头部](<reference_selected/chassis/chassis/Task/chassis_task.h#L1-L17>)、[生成来源](<reference_selected/chassis/chassis/algorithm/LQR_K.c#L1-L6>)；已索引根目录未见统一项目LICENSE | 源码可见不自动补成统一MIT/Apache项目许可；继续保留出处并在分发前确认具体许可 |

## 8. 下一步绑定清单与验收证据分层

1. **板与总线**：实物型号/PCB修订、MCU、IMU型号、供电使能/加热、bus数/引脚/时钟、终端/负载、收发队列、watchdog与输出断电路径；DJI C和达妙候选分别有BSP，不以电机品牌选板。
2. **电机**：目标每轴型号/固件、MIT或其他模式、命令ID/反馈ID/bus、量化P/V/T范围、反馈和命令的轴侧/输出侧、全传动比、极性/零位、温度、连续/峰值扭矩及持续时间、转速/电压/回馈边界。
3. **估计**：传感器可访问输入、采样时刻/延迟、R_BS与杆臂、偏置/噪声、轮地滑移/飞行门控、KF残差、连续yaw误差；真值仅供父任务评分/辨识，与部署输入分离。
4. **控制**：当前MOD4v1几何/惯量/闭链约束、可达/奇异域、真实执行器饱和、命令整形、FSM全状态超时、全六轴电功率/速度包络、MPC时限与LQR降级。
5. **证据台阶**：`SRC_PRESENT → BUILD_PASS → HOST_ALGEBRA/UNIT_PASS → BENCH_PASS → HIL_PASS → PHYSICAL_QUALIFIED`分开记账。当前仅有源码/构建配置存在，以及独立Python算术15项通过；后四项均无本轮结果。接口声明本身也未编译。
6. 2m/s、恒定4π rad/s起停/反向、RM粗糙地形、270mm台阶/落地与组合技能仍由父任务后续验证；成功率/时间/超调/功率门槛若另提议，应标注工程建议，不写成人类已批准验收。

**最终交付**：[本报告](<SPR_DEPLOYMENT_AUDIT.md>)、[机器可读源码索引](<SPR_SOURCE_INDEX.json>)、[独立HAL接口](<portable_hal_proposal.h>)、[算术检查结果](<codec_vectors_spr.json>)。所有本代理新增物均位于本目录，原 ZIP、父代码、Git与运行任务保持原状。
