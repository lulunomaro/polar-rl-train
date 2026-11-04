# MOD4v1 两项优先任务：本轮实际进展

## 结论

**自然摊卧启动起立尚未通过；旧实装工程的162个C源文件已取得成功ARM编译记录；PH10有限历史归档已提交并推送。** 这三项分别报告，编译与归档成功不替代起立、完整固件或实机验证。

## 一、自然摊卧起立：V4首案失败，失效已记录

本轮从原自然落稳前倾姿态启动，不使用直立初始化替代。初始真实pitch为0.383686829rad，rootZ为0.237138704m；控制器只接收原100Hz传感器链，物理仍为完整接触/闭链模型、0.5ms步长，初始状态仅设置一次，之后无root辅助或重置。

V4尝试“世界系支撑腿参考→捕获姿态→回原名义腿型→平衡”：原有公共支撑姿态与`-estimatedPitch`共移参考，参考限速；不增加新LQR增益，不修改原6s超时、0.50m编码器转动量保护和起立验收。

| 本轮新病例实际结果 | 数值 |
|---|---:|
| 控制／物理步数 | 193／3860 |
| 控制阶段 | OBSERVE 31帧，LIFT 161帧，INHIBIT 1帧 |
| 停止原因 | 估计姿态超出原起立pitch/roll包络 |
| 最终真实pitch | 0.991339657rad，约56.80° |
| 最终rootZ／相对初态抬高 | 0.305914938m／0.068776234m |
| 最大水平位移 | 0.076305426m |
| 原起立验收／末段稳定 | False／0s |

**抬高约6.88cm，同时进一步前倾，未进入捕获或平衡阶段。** 没有把高度增加记为起立成功。

新增已存数据诊断只读这条新控制流一次、193行，未重跑物理：
- 193个控制bin的全部20个2kHz采样，双主轮法向承重都超过1N。
- **没有一个完整控制bin**同时满足guide/hard接触力全程≤1N；guide接触累计3815个物理采样，hard为0。
- 轮速峰值约0.629rad/s，轮请求力矩峰值约0.189Nm；这些是传感/请求量，不据此推断实际力矩、DC限幅或唯一失效原因。
- 静态支撑几何的可行端点尚未转化为动态起立能力。下一项要隔离的是抬升期间的姿态控制与支撑转移，而非放宽原验收门槛。

本轮前的V1—V3失败保留。本分支已有5次受控起立尝试，共2294个控制周期、45880个物理步：4份正式失败结果和1份V1报告API错误下的真实部分轨迹；全部没有完成原10s目标。另有3次无控制被动落稳、12000步，单列为初始化研究，不作为起立技能或独立姿态覆盖。当前尚无后倾、侧卧或完整DR起立通过证据。

证据：[本次实际结果](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/results/startup_front065_world_support_v4_nominal1/result.json>) · [一次已存流诊断](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_STAND_V4/front_saved_analysis001/REPORT.md>) · [诊断数字与事件](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_STAND_V4/front_saved_analysis001/RESULT_MIN.json>)。

### 准入中实际修复的缺项

独立复核发现V4最初54源预发锁漏了实际读取的支撑q/tau数据。旧准入保留为HOLD；当前数据本身与首次合成proof一致，没有观测到篡改。新的57源准入补入该数据和两个修订元数据脚本，重新独立复核后才运行上述首案。原控制代码、合成proof与旧阴性审查均未重写。

证据：[旧阴性复核](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_STAND_V4/front_admission001/FINAL_ENTRY_REVIEW_001.json>) · [新补锁复核](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/STARTUP_STAND_V4/front_admission002/FINAL_ENTRY_REVIEW_001.json>)。

## 二、真实旧工程：162个C源已覆盖，尚非完整target

剩余122个C翻译单元已执行一个真实串行波次：
- **122／122编译成功、122个非空物件、122次新ABI scope解析全部通过。**
- 2906项type检查及1342项原non-type检查通过；没有静默改源、补头文件、改警告或重编旧成功物件。
- 三段原始成功记录覆盖原工程162个不同C源ID：名义main 1个＋前波39个＋本波122个。
- 旧main缺依赖的失败、原FILE解析门停止、旧容量停止均保留；后续独立静态评定与当前编译记录分列，不改写历史。

这是明确的AC5u6/O1-time诊断构建变体，不冒充旧u4/原IDE全部数值选项的逐字复现。当前仍有1个startup汇编未执行；完整链接、两库整体ABI、ROM/RAM、启动运行、ISR/WCET、CAN/IMU实测及MOD4机械/电机绑定仍未完成。本轮没有链接、烧录或实机输出。

后续已开始独立的startup汇编**静态**源/参数核对；首个汇编调用仍待另行确定，不会自动进入链接。旧工程的原轮电机/标定与最新MOD4达妙体系差异继续保留，现有门控适配也不等于C3或起立控制已经在旧BSP闭环运行。

证据：[C11实际编译报告](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_TARGET_COMPILE_V11/REPORT_V11.md>) · [C11封存收据](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MOD4_DEPLOYMENT_TARGET_COMPILE_V11/RECEIPT_V11_FINAL.json>)。

## 三、PH10历史归档已完成

按原Git策略完成一次原helper记录、annotated tag及仅自身分支/新tag的非force原子推送：

- Commit：`e176d2a6401fafb9d618a042acba8190023c3273`
- Parent：`7b7d2633a25dad356809a56ddfa2d546f1cded10`
- Branch：`mod4v1-lqr-mpc-robust`
- Tag：`trial-20261104-mod4v1-robust-traditional-phase10`
- **1638个路径全部新增**，提交前后逐路径/逐blob身份检查通过，远端分支、tag对象及peeled commit核验一致。

截止范围是此前已关闭的V3B/C6及旧实装工程材料。**本轮V4、支撑几何、C7以后构建工作未混入PH10**，留待下一有限截止归档。所有原失败、缺失result、编码身份与未知SHA保留；未触碰其他RL工作树索引、main或旧tags。正式后置收据放在PH11_PENDING，避免递归重提。

证据：[实验record](<F:/RMPOLAR-RL/repo-lqr-robust/history/experiments/20261104-mod4v1-robust-traditional-phase10.json>) · [远端核验收据](<F:/RMPOLAR-RL/repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase11_PENDING/ARCHIVE_PHASE10_RECEIPT.json>)。

## 接续顺序

1. 以V4已保存的时间顺序为依据，提出并单独验证“抬升期间的姿态控制/支撑转移”最小新干预；不据单名义病例修改旧冻结包或宣称完整DR。
2. 完成startup汇编参数与ABI核对，再处理完整链接、内存布局和实际BSP控制接入；当前物理板型/电机协议未绑定，保持无烧录。
3. 传统控制整体Goal继续active。既有H1/H2/H4/H5以及270mm、转停换向、全地形和实机验证的原边界不变。
