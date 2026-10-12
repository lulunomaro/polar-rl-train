# 华南虎官方模型：3060实际50mm起伏参考回放

人类明确要求用华南虎的模型和策略在3060跑我们的门槛。本轮两个公开最终model_1000均实际完整回放、无学习，源权重前后exact不变。官方模型和原机器人配套运行，没有把SCUT动作或参数塞进MOD4机器人。

| 官方模型 | 正向完整路线 | 倒退完整路线 | 仅位置判据 正/倒 | 去掉末端200mm 正/倒 | 额外2mm闭环影子判据 正/倒 |
|---|---:|---:|---:|---:|---:|
| 2026-07-23_16-23-21 / model_1000 | 5/27 | 0/27 | 5/0 | 5/0 | 0/0 |
| 2026-07-30_09-16-27 / model_1000 | 6/27 | 0/27 | 6/0 | 6/0 | 0/0 |

共80环境：正27、倒27、站立26；站立无需通行。50mm是峰谷高差，完整十波长2.406422727m，沿用实际MOD4保存的80格float32世界三角面，80格顶点/三角面byteexact、独立期待值射线误差3.077315561695465e-7m，原1e-6容差未放松。根起点前接近0.4m，固定BODYvx正负0.3m/s、vy/yaw0，15s。逐物理episode审查两轮先在前方支撑→全十波→后方200mm支撑，垂直正接触力按原SCUT四物理回调积分/控制时间平均，双轮各>1N。有效普通失败前缀和所有未完成前缀保留，reset teleport不计进度。

本轮去掉1N接触要求或末端200mm要求都未增加完成数，因此这些细项不能解释本轮大部分未完成。两个官方模型在这个固定低速协议下也未全程完成。结果不能证明MOD4评估过严，更不能声称作者机器人在官方赛道表现差；这是特定速度/地形/时间窗口、当前SDK兼容回放的结果。

此前助手把正反27/27说成机械晋级硬线，表述过头，正式纠正并保留历史。RM003批准计划明确“不造90/95/100晋级线”；全样本完成是强观察证据，进度决定应结合方向覆盖、失败严重度、有效轨迹及用途，不另造百分比线。完整路线、同episode、真实支撑和原物理/数据完整性检查保持。没有改生产validator、DR、reward、reset、预算、训练源或已保存false。

2mm闭环列是额外影子诊断，没有实际新增终止或干预SCUT原dones。已从全raw核对MOD4源的控制端点与10个100Hz控制步=.1s出生宽限；旧“任意物理子步且无宽限”统计原样保留为诊断，不能套成精确MOD4控制门。SCUT原机器人/约束、5ms×4/50Hz、TGS12/6与原保存DR保持；MOD4为2.5ms×4/100Hz、TGS32/4及自己的机器人/DR。跨机器人影子2mm不替代同机器人硬件或机构认证，也不据此下调MOD4闭环健康阈值。完整SCUT mimic/整机硬件范围没有等价认证。

公开来源固定b8ff79f3df855faf9dc92f4a282bd80c42649466，114个源码/资产/模型/参数文件实际SHA核验。July23模型SHA d19492be858ffd431a67e5aa40afb4a4c51dc9a1c914c5c92022ed46d5868db7；July30模型SHA4a46713f133a63ade7bd249c1aba8e1b7cb135e8fd7296219837dc1c7042315b。配套wheelbipeV14_2 USD SHA48f2d53ac589391a37f3df550e8e537af3ecb5bdb6ebb632fb8c7b83fa9af325。原网络均35输入/6输出/ELU，严格加载原actor，empirical_normalization=false，原策略/PD/气弹簧/质量摩擦/延迟/噪声/推力DR按保存配置运行。测试seed20260928并非作者原RNG状态复现。当前IsaacSim6.0.1/Lab6.1.14的API适配，不冒作者原引擎benchmark。

先前尝试全部保留：SSH子进程寿命拒绝在GPU/借锁前；TaskService模板token引号SyntaxError在执行前；触发器null误计独立只续receipt；已知network_retry无jobs字段导致只读协调器拒绝在借锁/GPU前。最初两份GPU全raw保存但rough高度射线旧wxyz offset未全转换为当前xyzw，不能作为合格比较，原分数与raw未改。独立rayABI范围实际向下射线通过，固定命令仍被原后处理修改，控制0的严格actor输入检查拒绝，未学习/未进入控制。最终独立command-hook范围保留原hook一次执行，仅在原观测构建前绑定固定测试命令；向下射线/finite hits/每步实际actor前三维缩放命令/无special mode均实际通过。其余模型、机器人、DR、时钟、route和容差不变。新范围各模型750controls/3000callbacks/15s已完整保存和独立全raw审查，不重任何旧MOD4评测。

原3060服务仅在所有当前队列完成、实际无GPU孩子、fresh polling及PID/creation/argv核验后借用idle demand槽；完整结束后原两源SHA、原task action/zero triggers、实际新worker CIM、无reference进程、原shared OSlock held均核验恢复。四个临时oneoff无周期/boot/trigger；没有新增驻守。未停/热改/重启4090训练、未写canonical预算、未运行旧main/resume/once或干预WASD播放器。正常训练按原完整保存/评测/接续流程独立推进，对比和Git不是训练依赖。

完整raw/queryNPZ原件实际path-size-SHA索引在SCUT_REFERENCE_COLLECTED与ELIGIBLE_SCUT_REFERENCE_FULLRAW_REVIEW，逐env有效失败prefix保留；大weights/USD/ZIP/NPZ仅索引进Git，原件保持，凭据不输出不Git。所有source/error/false/成本/未采用准备/同步/监控/Git回执按项目政策持续归档。
