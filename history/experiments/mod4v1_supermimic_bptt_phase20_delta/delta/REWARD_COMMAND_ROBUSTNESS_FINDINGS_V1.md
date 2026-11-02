# MOD4v1：奖励与指令跟踪的鲁棒性审计

## 结论

**有明确可测试的改进方向；优先修指令/观测/参考系一致性，再做逐项奖励消融。当前证据证明了实现风险与候选软件机制，尚未证明新方案提高实际技能通过率。**

范围为八条非H1谱系，H1继续冻结。原MOD4v1资产、400N/k2000/d3、50Hz控制/100Hz反馈、0.0025s物理、TGS32/4、闭链/模仿约束、D0–D7、命令速度分布与原接受阈值保持。原模型、全部候选和失败证据保留。

## 1. 优先处理的确定问题

| 优先级 | 发现 | 处理与证据边界 |
|---|---|---|
| P0 | 当前新residual除了原35维teacher，还读取真实物理state、DR参数、接触与延迟队列等特权量。冻结teacher并未隔离residual的部署输入。 | 新候选actor仅接收原noisy/delayed raw35、history与已知command；WM/critic可用特权状态。旧full-context残差/normalizer/Adam维度与raw35不兼容，新fresh谱系从0计数，不切旧权重或拼更新数。 |
| P0 | E2的真实nonholonomic命令是 `vx=clamp(2V*cos(heading-axis))，vy=0`；H16 imagination当前却近似held command。 | V=.5、yaw=4rad/s、H16×.02=.32s，方向扫过73.3386°。最大解析held误差1.1943908827m/s，heading0例误差.7132847904m/s。这是公式反例，不是实测误差；原along目标.5±.05是cycle速度，不是每圈.5m位移。 |
| P0 | W35当前all-rough使用BODY vx[-.3,.3]，短H内可held；自然resample边缘、负速度参考轴与standing布尔需独立记录。 | 不把旧高速度逻辑套入当前W35，不把站立混进运动分母。未知timer/resample/sample时钟保留unknown。 |
| P0 | 新worker遗漏CURB113原after-restore inward-axis绑定；这是任务协议问题，不是奖励权重问题。 | 备用修复仅在ONE fresh reset后、first action前调用原函数；只同步无noise command[:3]，不额外reset/computeobs/RNG。真实CPU13项通过，尚未部署；本轮C113在更早bridge guard失败，未开始实际策略动作或BPTT。 |
| P0 | 50Hz endpoint不足以证明精确重建两个100Hz noisy/delayed sample。 | 新strict投影缺sample/cache/clock receipt时报unknown，不用当前干净state替代原反馈，不筛掉难边界以造提升。CPU双sample oracle仅为明确标注的合成软件夹具。 |
| P1 | `.05*MLP_logits`不是硬.05残差界，也没有默认teacher-anchor。 | `.05*tanh`、anchor、uncertainty各自单独消融，避免与指令修复混杂。 |

完整证据：[指令与观测源审计](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_command_review_v1/SOURCE_COMMAND_REWARD_AUDIT_V1.md>)、[机器证据与缺件](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_command_review_v1/SOURCE_EVIDENCE_AND_GAPS_V1.json>)。

## 2. 奖励审计：适合改什么，不先归因什么

- 八角色实际配置的velocity-height gate为off，alive/termination/base-contact/height-square reward权重为0。直接注册的SCUT tracking项也未被height gate包裹。**当前问题不宜归因为“存活奖励刷站立”或“高度门统一压掉越障速度奖励”。**
- 实际指数核是 `exp(-error²/std)`，不是除以std²；std=.25/.01对应e-fold半径.5/.1。大误差时指数项饱和，但原quadratic仍可提供梯度，不等于总奖励零梯度。
- 存在tracking、height、action的权衡反例：cmd=.3时静止与理想跟踪的相关子项rate差约.507924；高度误差.1m的损失约.771020，足以覆盖这一差额。这说明值得采集真实term-rate分布，尚不证明实际策略已选择站立刷分。
- E3的pitch/roll_velocity项实际是projected-gravity姿态代价，并非角速度。恢复过程可能与姿态代价对冲；倒置重力轴的局部零代价也是公式反例。先保留原request/credit/连续稳定/终止掩码，再单独试request期有限姿态代价倍率。
- CURB878/113、S135可试有向、有界progress potential，仍用各自原wheel-link有序端点与正Fz接受谓词。root越线、无跌倒、shaping升高均不代替成功。
- W35先修interval/参考轴/UID与自然resample测量，再试单一progress或phase项。S50原binary accepted predicate缺口继续为null，不借S135阈值。
- SDK源确认weighted term rate乘.02积分一次；shaping若使用transition增量，应以rate=增量/.02接入，避免重复积分。

[奖励审计与62项测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/REWARD_COMMAND_AUDIT_SOURCE_V1.md>)给出全部量纲、反例与PBRS条件。Potential公式 `F=gamma*c*Phi1-Phi0`，需匹配continuation、terminal/timeout、critic变换及reset边界；学习型WM/奖励头和有限H并不自动保证真实策略不变。

## 3. 下一轮对照必须拆开

以下为父层统一的试验顺序；两份子审计中的arm名称仅作局部建议，不直接合并编号。

1. **历史A0保留**：本轮full-context、held-model baseline，不作为部署35维或纯tracking因果对照。
2. **协议一致基线**：先验证真实backend/pose-cache/命令轴/采样时钟，保留原任务与奖励。缺件保持unknown。
3. **A1 fresh raw35控制组**：同teacher、同种子/预算/DR/命令分布，actor仅raw35+history，原reward与原unbounded .05 residual保持；legacy imagination近似明确标注。新的网络/Adam/计数从0，不把历史A0计数算入。
4. **B指令组**：在A1上单独修E2 body-command随预测heading/phase演化；sensor一致性单列或在其后单列，未知resample/feedback边缘不得默默删样本。
5. **C奖励组**：各角色各自一次只改变一个因素：tracking核、E3 request期姿态代价、有向potential、W35 interval项。原标签、阈值、速度和运动/站立分母保留。
6. **D约束组**：hard-bound、anchor、uncertainty分别测试，不把多项同时改变的收益归因于某一项。

验收使用各专家原接受谓词、完整conditional denominator及单列all-started ledger；分组报告ordinary failures、成功后失败、partial/censor和实际命令暴露。配对训练种子之外另设独立holdout，多seed报告比例及不确定性；E0/S50原binary定义未补齐前保持null。任何loss、imagined reward或无跌倒改善都不等同于80%/90%达标。

[逐角色disabled奖励消融候选](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/NEXT_WINDOW_AB_PLAN_V1.json>)、[命令候选源码差异](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_command_review_v1/SOURCE_TO_CANDIDATE_DIFF_V1.patch>)可复核。候选未替换任何已准入窗口。

## 4. 已完成的软件验证与实际训练分开记

- 奖励源公式/反例：62/62 stdlib CPU通过；源输入89个明确小文件SHA复核。
- 指令公式/AST：37/37 stdlib CPU通过。
- Raw35/command/sensor projection/H16链：真实Torch CPU组件22/22通过，future→s1→a0 VJP非零；**optimizer步数0、native专家步数0**。
- C113原axis绑定：真实Torch CPU13项通过；无额外reset、sensor重采或RNG抽取；**native步数0**。
- 新candidate actual-core集成V3：真实Torch CPU、原vendor与冻结新core，H16/hist10，WM/aux各20次、policy/critic各3次；三个future→s1→a0 VJP及参数变化均非零，teacher冻结、actor严格35维。**这3步仅合成软件优化，native专家计数仍0**，不证明实际技能提升。V1/V2因日志依赖bootstrap缺rich而失败，均保留；V3在launcher启动后显式加入已封存sm_deps路径，未改冻结候选源码。[actual-core CPU V3收据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/COMMAND_CANDIDATE_CORE_INTEGRATION_CPU_V3.json>)。合成噪声tape不验证真实幅值、反馈采样或backend binding。

[CPU22收据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/COMMAND_CANDIDATE_TORCH_CPU_V1.json>)、[C113 CPU13收据](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/ORIGINAL_C113_AXIS_BINDING_CPU_V2.json>)。

## 5. 同期真实native窗口已收尾

| 谱系 | 真实verified policy BPTT | 当前状态 |
|---|---:|---|
| E0 | 2520 | 原3600s保存边界完整保存，未到3000，技能率尚待冻结评估 |
| E2 | 2392 | 原3600s保存边界完整保存，未到3000，技能率尚待冻结评估 |
| E3/W35/CURB878/CURB113/S135/S50 | 0 | bridge首次动作前quaternion/gravity一致性guard异常；计数未创建，0由失败位置推断 |

全队列已实际wait、原成本结算、原锁释放。原GO到terminal合计7603.138181686401 expert-seconds。六条虽进程RC0，却有WORKER_ERROR且缺成功FINAL，已按真实失败重新分类；原worker源码会raise，App.close是否覆盖退出状态仍待证。未来owner需同时检查rc/error sidefile/success FINAL，不能只看RC0。

倾斜reset后的root quaternion与derived gravity/heading缓存时间戳不一致是新调查方向；相关PhysX源已发现pose setter遗漏derived缓存失效的源码链，**过去worker实际binding/缓存stamps的根因仍未实证**。不降1e-3阈值、不盲改quat order、不重跑原失败用途。当前没有本任务GPU worker在训练；正在准备新版本接口修复/恢复，Goal继续active。

[真实闭合窗口与错误重判](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/FIRST_NATIVE_WINDOW_CLOSED_TRUTH_V1.json>)保留两份完整checkpoint的原producer路径/bytes/SHA和全部六条失败。状态更新以新阶段收据为准，旧“正在跑”的时间点记录保持原样。
