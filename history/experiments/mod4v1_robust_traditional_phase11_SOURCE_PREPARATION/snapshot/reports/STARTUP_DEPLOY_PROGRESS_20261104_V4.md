# 摊卧起立与真实旧工程接入：V5／首次 ARM 链接进展

## 结论

- **旧 BSP／Stage1 底座首次真实 ARM 诊断链接通过，armlink 返回 0。** 162 个 C 源与 1 个启动汇编的分段产物已共同参与本次链接；这不是单次 clean build，也不是最新 MOD4v1 的 C3＋起立控制器一体化固件。
- **V5 前倾摊卧起立首案未达到原验收门。** 实际 188 次控制、3,760 步 MuJoCo 物理积分，因原俯仰保护停止；未进入 BALANCE。软件执行和结果生成正常，保留失败结果。
- Goal 保持 active／armed；当前优先项仍为摊卧起立与真实工程接入。旧 H1/H2/H4/H5、模型、增益、Stage1 交付及 PH10 归档保持原状。

## 1. V5 实际起立结果

[原始小结果](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/results/startup_front065_lift_pose_v5_nominal1/result.json>)使用与此前候选相同的自然落稳前倾初态，一次性载入初始 qpos/qvel；控制过程中没有 root 辅助、直立重置或真值反馈。

| 项目 | 实测 |
|---|---:|
| 初始真实 pitch／root Z | 0.383687 rad／0.237139 m |
| 实际控制／物理步 | 188／3,760 |
| 计划时长／实际终态时刻 | 10 s／1.88 s |
| 停止原因 | `limited startup pitch/roll envelope exceeded` |
| 末真实 POST pitch | 0.974531 rad，约 55.84° |
| 末 root Z／高度增加 | 0.305322 m／0.068183 m |
| 最大真实水平位移 | 0.352945 m |
| BALANCE／末连续稳定 | 未进入／0 s |
| 原起立验收门 | False |
| 全过程 guide／hard 接触物理 ticks | 3,710／0 |

高度增加超过 5 cm 不代表起立成功：俯仰、退出非主轮支撑、完整时长和末连续 3 s 稳定条件同时保留。私有支撑门仍检查每个 100 Hz bin 内全部 20 个 2 kHz 子采样；姿态、速度、关节门为 100 Hz，不声称采样间连续时间证明。

当前累计 **6 次受控起立尝试，2,482 次控制／49,640 步物理积分**。其中 5 次有正式失败结果，另 1 次 V1 在控制停止后遇到报告 API 错误并保留 601／12,020 前缀；没有补造结果。尚无完整 10 s 起立完成轨迹，这些数目不包装为独立完备试验通过率。另 3 次被动落稳共 12,000 步，独立列项，不算起立技能成功。

## 2. V5 的实际分支诊断

[18 行诊断报告](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_STAND_V5/front_saved_analysis001/REPORT.md>)与[收据](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_STAND_V5/front_saved_analysis001/RECEIPT.json>)已封存。唯一新 control 流读取一次、188 行；没有读取 physics raw 或旧 V4 raw，也没有重算 raw SHA。

- `lift_pose_active=True` 是功能标志，不等于每周期施加姿态轮请求。156 个 LIFT 周期中，**38 个实际 pose REQUEST、118 个 quiet**；全部 156 条请求公式复核误差为 0。
- 首次 pose 请求在 0.31 s，左右轮 REQUEST 为 3 Nm；首次关闭在 0.40 s，首先是 proper norm 14.4347 m/s² 超过当前资格上界 11.772，而不是关节速度。
- 失格分区为 proper-only 11、qd-only 37、qd＋qerror 70。最后 pose 在 0.83 s；**0.84–1.86 s 连续 103 周期为 quiet**。
- qd>.4 是 107 周期中的充分排除项，但不是唯一动态失效原因。fresh 本身未独立记录；age=0 不替代完整 fresh 证明。
- 最大轮转 proxy 为 0.381835 m，未触 0.50 m 保护；其数值不等于真实位移。REQUEST／window-held 编码器量也不替代实际 2 kHz 驱动力矩、DC clipping mask、接触身份或瞬时驱动速度。

结论限于：**保留原资格门的时序前移不足以完成本次起立，且多数 moving LIFT 周期没有持续 body-feedback。** 不据此推断单一 wheel 因果，也不把旧／新闭环腿参考轨迹称为相同。

## 3. 真实旧工程：启动汇编与首次链接

### 已实际执行

1. [V14 启动汇编结果](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_STARTUP_ASSEMBLE_V14/RESULT.json>)：唯一启动源首次 ARMASM 返回 0，物件 6,880 B。实际 FILE tag27=1、tag28=1；这是观察到的 public VFP 编码，不是由 CPU FP 能力推定，更不等于完整运行时 ABI 资格。
2. [V15 静态报告](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_LINK_PREP_V15/REPORT.md>)：163 个 source ID 的 object＋两库 registry、真实项目 memory 选择、完整 argv 已核。原收尾 checker 将固定参数数目误计 13，原失败保存；新 checker 仅一处 13→12 后收尾通过，没有重做 native query 或输入扫描。
3. [V16 首次链接结果](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_FIRST_LINK_V16/RESULT.json>)：**一次 armlink，返回 0，用时约 0.210 s；提取到的 Warning／Error diagnostic 行数为 0。** 实际 first-link 前，163 个物件及两份 opaque 用户库各核当前 SHA 一次，匹配 producer；这是链接完整性检查，不是归档重复读取。

### 链接图中的容量

[链接图原文：9976–9986](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_FIRST_LINK_V16/link.stdout.txt#L9976-L9986>)：

| 项目 | 链接图值 | 源项目选中容量 |
|---|---:|---:|
| RO：Code＋RO Data | 118,140 B | Flash 1,048,576 B |
| ROM：含压缩后 RW 初值 | **118,512 B，约 11.3%** | Flash 1,048,576 B |
| RW：RW Data＋ZI Data | **66,352 B，约 50.6%** | SRAM 131,072 B |
| 诊断 AXF 文件大小 | 629,048 B | 含 ELF／debug 等，非 ROM／RAM 占用 |

源项目配置为 STM32F407IGHx；Flash `0x08000000`／1 MiB、SRAM `0x20000000`／128 KiB。CCM 虽在配置表列出但未选，本次没有搬移数据到 CCM 或放宽 region limit。安装工具为 AC5.06u6.750，不声称复现项目请求的 u4 选择器。

新映像基本观察：vector `0x08000000`、初始 SP `0x20010330`（8 字节对齐并位于选中 SRAM）、Reset／ELF entry `0x080003dd`（Thumb）。链接图将 SVC/PendSV 指向 FreeRTOS port、SysTick 指向 C 中断源、SystemInit 指向 system 源；这是图中的定义来源，不替代中断运行证据。

### 仍需分项完成的接入

- 当前是**旧 BSP／Stage1 gate 底座**：旧机械控制与 MF9025 轮接口仍在，MOD4 达妙标定／协议绑定默认 UNBOUND；新 C3、起立 FSM、功率—驱动和 sole-send transaction 尚未接成完整实机链。
- 图中存在 `__use_no_semihosting_swi`、`__semihosting_library_function` 等相关符号；需另核实际可达路径及 retarget 行为，既不据字符串宣称执行了半主机调用，也不据名字宣称已验证独立 I/O。
- 映像未运行、未刷写。CRT／RTOS、FPSCR／denormal、栈堆真实余量、BMI088 异步采样与六电机时间戳、GPIO/CAN/达妙单位标定、WCET/HIL/实机起立均另列资格。

## 4. 下一候选与归档

下一候选准备测试“**先收至已有公开蹲姿，再回到名义站姿**”，而不是继续沿在线 `-pitch` 平移的同一路径微调。采用既有公开 crouch 点，body-fixed hip=0.454174 rad、delta=-0.495684 rad，其绝对 crank 由 hip＋delta 得到；这是尚待新轨迹验证的路径假说，不是已有起立能力。原力矩、关节、速度、0.50 m proxy、6 s、pitch/roll 保护和私有验收门保持不变。

新候选当前仅授权源码与有限新合成测试准备；没有在本报告中提前计入物理成功。新链接图的 saved-metadata 审查亦独立进行，不追加 native 或读取旧物件／库 payload。

PH10 已实际归档到 commit `e176d2a6401fafb9d618a042acba8190023c3273`；其 tag、旧失败与旧包不改。本次 V4/V5、C7–C16 及后续 saved-map 审查属于 PH11 pending。Goal 继续保持 active。
