# 八非 H1 专家：原奖励—命令—终止—接受谓词对齐审计

## 0. 结论及证据边界

**下一窗口顺序：先原协议/坐标/命令语义，后单因素 reward A/B。没有训练或真实通过率提升结论。**

- E0/E2 当前原生 SuperMimic H16 保持原样；本审计没有编辑任何 active、封版或历史任务源，没有 SSH、SDK/torch 导入、GPU、PT/模型、旧 raw/JSONL、C 盘任务数据、GO、锁、Git 或训练操作。
- 本 session skills 仅 Office/ACL，与 RL 审计不匹配；host 检索亦无任务匹配的 RL 工具。实际采用 read/glob/grep、显式小源 SHA、stdlib CPU。Bundled Python 位于 C 盘仅作为解释器，未读取 C 盘任务数据。
- 八份元数据分别 join 自己的 entry/import 链，而非把 class 默认值当 livecfg。共 89 个显式小源输入 SHA；八份主任务和 skills 文件相同，SCUT 整文件因身份内容不同而不同，但本审计涉及的 11 个 SCUT reward 函数 AST 完全一致。结果是 **source join，不是实际运行后的 cfg 或 reward 测量**。
- 当前 `alive=0`、`termination=0`、`height_square=0`、`wheel_contact=0`、`base_contact=0`；各角色 `RM_VEL_HEIGHT_GATE=off`、gyro curriculum off。SCUT linear/yaw exp 本来直接注册、未走 height gate。因此“当前越障/恢复被 velocity-height gate 压成零”没有源证据；实际值得排查的是正高度奖励、姿态/动作平滑/能量代价与任务进展的对冲。
- **CURB_INDEPENDENT113：P0 原协议接线缺口，不归为 reward 缺陷。** 新 SM worker 只 build_env + ONE fresh reset，未走独立 CURB axis 的 after-restore bind；父代理已确认并另写备用候选，尚未部署。该角色当前未启动，不声称它已经错跑。
- E0 与 SLOPE_INDEPENDENT50 的原 binary predicate / accepted cohort 缺口继续保留 `null`；无新 proxy、无借用 E2 或 S135 规则。

主交付：[各角色参数与来源](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/ROLE_EFFECTIVE_REWARD_PARAMS_SOURCE_V1.json>)、[标量反例](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/FORMULA_COUNTEREXAMPLES_CPU_V1.json>)、[纯 CPU 候选函数](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/reward_command_candidates_v1.py>)、[62 项测试结果](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/CPU_TEST_RESULTS_V1.json>)。

## 1. 核心源与控制时序

| 证据 | 源及已核对行 | 支持的判断 |
|---|---|---|
| S1 | [原进度封条](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/CURRENT_PROGRESS_v5_PHASE19_REMOTE_VERIFIED_MEASUREMENT_SEAL_PENDING_APPEND.md#L1-L41>) | 活跃 E0/E2 与真实测量尚待验证；本工作不干预 |
| S2 | [原接受合同](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json#L105-L582>) | 八角色接受单位、数值、缺口、分组及 censor 语义 |
| S3 | [SCUT kernel](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/scut_flat_rescue.py#L13-L81>) | exp 分母、forward-only tracking、姿态、fork、leg、功率 |
| S4 | [主奖励注册](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/mod4_task.py#L1654-L1718>) | 实际函数接线；注释中的 gate 不等于实际接线 |
| S5 | [高度与 gate 实现](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/mod4_task.py#L560-L708>) | 高度相对地面、接触 history-norm、gate off/exp/linear |
| S6 | [RewardManager](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reward_scale_v1/managers/reward_manager.py#L129-L159>) | `r_step=sum(func*weight*dt)`；零权重跳过；`_step_reward=value/dt` 是 rate |
| S7 | [SDK step 顺序](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py#L231-L273>) | 物理后 termination → reward → reset → command.compute → observation |
| S8 | [SM worker](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/worker_supermimic_bptt.py#L23-L74>) | 原 env 恢复、固定 .0025/.02×8、held command/DR、H16、fresh reset |
| S9 | [native bridge](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L51-L145>) | 原 scalar r/done；terminal reward 保留；物理 pre-reset s1 与 reset state 分开 |

S7 意味着物理转移与 reward 用产生该转移的旧 command；返回 observation 中的 command 可以是已经更新/重采样的新 command。审计、WM 标签、未来 command evolution 必须区分 `command_used_t` 与 `command_next_t1`。不应用 reset 后 pose 或返回 observation 的新 command 为上一转移补标签。每次8物理子步、20ms控制步及 UID/phase 必须一致。

## 2. 各角色实际元数据与 entry 链

| 角色 | 原 metadata env / entry 来源 | 实际 wrapper 重点 |
|---|---|---|
| E0 | [metadata:6–105](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/original_run_manifest.json#L6-L105>)；[entry:79–147](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/train_mod4v1_e0.py#L79-L147>) | FreshDR + ChassisPD；动态 world-directional command |
| E2 | [metadata:6–102](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E2/original_run_manifest.json#L6-L102>)；[entry:79–151](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/train_mod4v1_e2.py#L79-L151>) | 模块替换为 E2 directional command；moving yaw 固定 ±4 |
| E3 | [metadata:6–102](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/original_run_manifest.json#L6-L102>)；[entry:134–153](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/train_mod4v1_e3.py#L134-L153>) | recovery mask/event；manual BODY twist 为零 |
| W35 | [metadata:6–105](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/original_run_manifest.json#L6-L105>)；[entry:79–149](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/train_mod4v1_w35.py#L79-L149>) | full RM70 208 lesson；不是保留平地模式 |
| CURB_PROTECTED878 | [metadata:7–107](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/CURB_PROTECTED878/E1_CANONICAL_SOURCE_METADATA.json#L7-L107>)；[entry:80–141](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/CURB_PROTECTED878/runtime/isaac/mod4/train_host72_backend_admission_v1.py#L80-L141>) | curb reset/geometry wrapper 保留 command class，rolling reward 置零 |
| CURB_INDEPENDENT113 | [metadata:7–107](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/CURB_INDEPENDENT113/E1_CANONICAL_SOURCE_METADATA.json#L7-L107>)；[entry:80–141](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/CURB_INDEPENDENT113/runtime/isaac/mod4/train_independent_owned_axis_v1.py#L80-L141>) | 自己的 113 源，不与878合并；after-restore axis bind 在新 worker 缺失 |
| SLOPE135 | [metadata:5–111](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/SLOPE135/E1_CANONICAL_SOURCE_METADATA.json#L5-L111>)；[entry:80–141](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/SLOPE135/runtime/isaac/mod4/train_slope5_snapshot_reviewed_resume_ppo.py#L80-L141>) | own reviewed5°/2m连续坡，rolling置零 |
| SLOPE_INDEPENDENT50 | [metadata:7–106](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/SLOPE_INDEPENDENT50/E1_CANONICAL_SOURCE_METADATA.json#L7-L106>)；[entry:80–141](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/SLOPE_INDEPENDENT50/runtime/isaac/mod4/train_independent_owned_axis_v1.py#L80-L141>) | own full-ramp family4 axis；边界/超时不是通过谓词 |

所有角色 metadata 中 height command 固定 .25；八份主任务 import 的 episode 默认20s，与接受窗口 E2=24s、W35=32s、固定E1=15s是不同层的协议。未来验证应复用原接受入口，而不是静默把训练限时或测量窗改成同一个值。

## 3. 真实 tracking 公式、饱和与 gate

令 `e_f = cmd_vx - root_lin_vel_b.x*sqrt(clamp(1-g_b.x²,0))`，`e_w=cmd_wz-root_ang_vel_b.z`，`h=root_z-ground_z-height_cmd`。源 S3、S4 和各自 metadata 得：

```text
lin_rate = exp(-e_f²/.25) + .2 exp(-e_f²/.01)
           - 1[e_f²>.5] - (.25 e_f)²
 yaw_rate = .5 exp(-e_w²/.25) - (.25 e_w)²   # gate off
height_rate = .7 exp(-h²/.01) + .3 exp(-h²/.001)
              + .3 exp(-h²/.1)*both_wheel_history_norm_gt1
r_step = .02 * sum(all weighted rates)       # terminal reward也保留
```

- `std` 在 SCUT 是 exp 的**直接分母**，不是需要再平方的标准差。`.25/.01/.001/.1` 的 e^-1 误差半径分别 `.5/.1/.0316228/.316228`；若写成常规高斯 `exp(-.5e²/σ²)`，σ才是 `sqrt(d/2)`。不要套 Isaac 通用 mdp kernel 的另一种 std 约定。
- derivative `dr_exp/de=-2e/d*exp(-e²/d)`。yaw error4 的 exp仅 `1.60381e-28`；但原 square 的导数仍 `-.125*4=-.5`，所以总 tracking 并非“无梯度”。tight error1.5 的值低于float32最小subnormal（纯CPU数值比较，不是实际GPU精度测试）。
- huge_gap 是硬指示、阈值在 `|e_f|>sqrt(.5)≈.707107`，不是 speed>.5，几乎处处局部导数0。fork 同样硬阈值；现有 square 仍提供尾部梯度。
- forward kernel 不接收 vy，既非完整 BODY-XY 跟踪，更非 world-vector 跟踪。用于moving时必须先尊重原非完整约束的命令定义。
- S5:620–637 的 linear height gate 在 |h|≥.10 可为0，但八份 actual metadata 均off；S4的linear exp/tight/gap/square、yaw exp直连SCUT，只有yaw square和run-error wrapper显式gated，而run-error权重0。把gate改成on会改变部分项而非注释声称的全部项。
- actual height_square=0、height_deficit=0、height_L1=0、未注册的heightL2=0；不要按class注释加出“−25h²”。

**BPTT特别限制：** 上述是原标量函数对输入误差的解析斜率；当前 SuperMimic 在 imagined rollout 用 learned scalar reward head，其对 actor 的梯度还经过 WM/Jacobian，并不等于这些解析导数。原exp饱和既不证明 learned head 零梯度，也不证明其梯度正确。

### 3.1 原终止与课程：不应由reward候选暗改

- [原termination配置:1782–1805](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/mod4_task.py#L1782-L1805>)：time_out、bad_orientation=.75rad、floor/field过滤后的chassis接触50N、closure、mimic；low_base minimum=−1属原名义禁用阈值。当前MOD4v1 entry/SM外层把closure/mimic配置为.01/.01，历史class .002/.05仅作原域比较，不拿来热改实际done。
- [Spawn grace:814–826](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/mod4_task.py#L814-L826>) 只在closure/mimic检测路径用episode_length_buf判断；SM worker明确给E2/E3设5 controls。其他角色沿各自env/entry，不应拿默认10当八角色livecfg；本次候选不改grace。
- 地形wrapper额外的rough_route_boundary仍为原timeout。W35使用[原course范围:8–16,38–39](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/course_math208.py#L8-L39>)；S50只对自己family4替换为abs tile-center xy>3.5/>3，不应把timeout、边界计数等同于成功。
- [gyro课程与post_init:1823–1862](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/mod4_task.py#L1823-L1862>) 默认可注册gyro_window，但八份元数据均RM_GYRO_CURRICULUM=0，实际source join移除该项；pure/moving/transition采样比例是固定command分布，不是证实有自适应课程。terrain/reset/DR与原recipe分布完整保留。
- E3唯一恢复request内的软termination mask见5.2；它不扩大到其他物理/机制失败。reward中的termination权重0也不等于done无影响：它仍切断未来return与BPTT，并影响完整cycle/interval数量，必须同时报告失败和incomplete以防分母选择效应。

## 4. 站立高分、进展与约束代价的反例

以下为故意简化的代数反例，不是物理可达轨迹、实测刷分或占优策略证明；数值见[反例输出:117–150](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/FORMULA_COUNTEREXAMPLES_CPU_V1.json#L117-L150>)。

1. `cmd_vx=.3`、其他项理想、站住时 linear rate=.692076，完美跟踪1.2，优势仅 **.507924 rate**。计入yaw=.5、高度=1.3、两leg对齐=.2，理想静止总rate=**2.692076**，完美移动=**3.2**；对应20ms step .0538415 与 .064。alive为0，仍有正的每时间奖励，长生存可能有吸引力。
2. 同样理想移动但高度误差.1，height损失 **.771020 rate**，总rate=2.428980，低于上述站立反例；.02高度误差亦损失约.12755。越障时需要暂时改变高度，收益结构可能对冲，但实际relative-ground getter/ground cache仍须验证。
3. [action_acc:571–583](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/skills_isaac.py#L571-L583>) 是 `a_t-2a_t-1+a_t-2` 的平方和。六通道一次单位阶跃在两个控制步可产生总−.6 rate的示例（再各乘dt），并非每秒二阶物理导数。原 [action_rate:257–259](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reward_scale_v1/envs/mdp/rewards.py#L257-L259>) 也是离散差分，不除dt。固定dt保持不变；先量各项而非直接降权。
4. S3:44–49 的 `pitch_velocity/roll_velocity` 名称容易误读：实际是 `(gain*projected_gravity_axis)²`，`gain=2exp(-cmd_vx²)+2`，不是角速度罚。另有 [ang_vel_xy 与 lin_vel_z](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reward_scale_v1/envs/mdp/rewards.py#L77-L88>) 的真实速度平方项。不可重复解释。
5. wheel_contact/base_contact reward权重0不等于接触不重要：base_contact termination仍在；height_both_wheels 用history最大**力范数**，与E1 endpoint每轮8子步平均**正Fz>1N**不是同一谓词。大切向/负Fz的norm反例可使前者真、后者假。
6. [rolling:12–25,79–88](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/rolling_consistency.py#L12-L99>) 仅零平移command且|yaw|≥3.5；load=clamp(meanFz/10,0,1)，speed/.15平方clip4，support deficit权重.25。|point speed|≥.3m/s的尾部平；高slip加载cost4，完全卸载cost.25。不是材料slip验证或endpoint接触验收；E1/W35 wrapper已禁用此项。无需为这些角色再“修rolling门控”。
7. [world-cycle cross:39–93](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/world_drift_reward.py#L39-L93>) 扣除理想partial-cycle cross波纹后归一，cost=(cross/.1)²clip4，|cross|≥.2m/s饱和。它不是沿向进展奖励，也不等于E2接受的未插值采样cycle；tracker的恒定requested-yaw模型仍待实际运动验证。
8. S4:1723起的route_progress2/route_success20只在MAP_MODE=rmuc2026；八角色这些flat/E1 lesson不是这个分支。不要把该奖励当原越障完成信号。

## 5. 角色对齐、优先级与源候选

| 角色/优先级 | 原成功接受单位，保持原样 | 对齐风险与下一窗口首选 |
|---|---|---|
| E2 **P0命令 / P1奖励** | 同UID采样signed2π cycle；along **speed** .5±.05、cross≤.05、yaw均误差≤.2，完整且非term/trunc；±4分开 | 先验证同物理点/phase与imagined command演化，再考虑只替换broad tracking kernel；不把.5当每cycle位移，不降速 |
| E0 **P0语义 / P2奖励** | 原多profile diagnostics；binary=null | 动态world/transition reference优先。纯转、直行、transition、moving和standing各自保留；无二值90%结论 |
| E3 **P1恢复对冲** | recipe0..11首次episode累计credited；recipe12normal排除；25连续good controls/0.5s | 优先量恢复期姿态/动作惩罚与事件；候选只对外生request内的姿态代价做有限phase gate，保留event、termination和接受条件 |
| W35 **P0测量 / P1相位** | BODY自然command完整interval；sample `_command_heading`，负vx加π，v=abs(vx)，沿/横界max(.03,.1v)，yaw≤.2 | 先修观察reference/负命令轴、interval UID；后评估有边界的相位高度代价或进展。不是将BODY interval换成任意world恒定向量 |
| CURB_PROTECTED878 **P1进展/支撑** | own20mm竖沿/150mm平台；ordered wheel endpoints ±.275，正Fz，15s，27up/27down/26stand分开 | 先确认body-link/每轮Fz/方向；候选有向有界potential + phase，不触动DR/physics、不用root越线替代验收 |
| CURB_INDEPENDENT113 **P0原协议** | 自己的同类原endpoint合同，不和878合池 | 先由父验证one-fresh-reset后且first-action前axis bind、无noise command slots同步；随后才做相同候选。未运行，未修复声明 |
| SLOPE135 **P1坡上权衡** | own5°连续2m坡，±1.2 endpoint，原分组/接触/先后顺序 | 先相对地面高度与坡向语义；有向potential候选优于一刀切取消平衡代价；坡不是20mm竖沿 |
| SLOPE_INDEPENDENT50 **P0接受缺口 / P2诊断** | own family4 full-ramp训练轴，±3.5/±3 boundary timeout；binary=null | 保留自然commands/DR/RNG；先补原accepted predicate/cohort；只做诊断/源候选，禁止借S135的1.2/27/27或boundary/no-fall proxy |

### 5.1 命令语义的具体证据

- [E0 directional:66–104](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/directional_spin_runtime.py#L66-L104>)：standing .1、pure .3（其中1/3 transition）、moving .2；12..16s自然resample；moving yawabs1..2，pure1..4π。 [E2 directional:66–119](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/e2_directional_spin_runtime_v1.py#L66-L119>) 只将moving yaw固定±4，transition按12s阶段演化。
- [原 nonholonomic translation:12–32](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/spin_translation_math.py#L12-L32>)：BODY vx=clamp(2Vcos(heading−direction),±1.5)，vy=0。无clip的完整cycle平均world速度才是V=.5；瞬时world向量并不恒等于(Vcosd,Vsind)。因此用恒定world-vector追踪误差直接替换，属于改任务。
- S8 held command H16=.32s；E2 yaw4扫过1.28rad=**73.3386°**。初始heading对齐时末端BODY vx差=.713285m/s，最坏phase差=**1.194391m/s**。这比先调reward更值得修正；新路径应按原source公式/预测heading/command-clock逐步演化，resample边界切段，不消费新的RNG，不在实际env重采样。
- [W35 command:16–61](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/command208_v3.py#L16-L61>) 全部eligible=False/family4，vx均匀[-.3,.3]、stand.2、vy/yaw0，自然12..16s；旧retained RNG仍消费但未选中平地模式。 [W35配置:14–48](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/config_mod4v1_w35.py#L14-L48>) 替换该命令并禁rolling。
- [原 E1 retention:42–105,131–136](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/SLOPE135/runtime/isaac/mod4/retention_flat_runtime.py#L42-L136>) 只对真实平地、clearance足够的样本选择直行/世界moving；非eligible目标地形使用gentle BODY命令。保留模式失支撑会转stand；这是原command规则，先做曝光统计，不静默取消。
- [独立axis:16–43](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/CURB_INDEPENDENT113/runtime/isaac/mod4/independent_expert_axis_v1.py#L16-L43>) 的CURB bind只在manual=False、target非stand时覆盖vx=.3*reset_direction。S8没有调用它。父代理负责备用接线及实际验证；当前报告不部署。

### 5.2 E3的已对齐部分与残余对冲

[Recovery runtime:9–66](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/e3_recovery_runtime_v1.py#L9-L66>) 已在request内mask height/height_tight/both_wheels/square/deficit/L1/lin_vel_z，并只mask bad_orientation/base_contact软终止；closure/mimic等未被这层取消。termination callback之后更新phase、reward随后读取事件，event函数返回delta/dt，S6乘dt后每事件恰为delta。

[Phase:3–19](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/e3_public_recovery_phase_v1.py#L3-L19>)：request=recipe!=12 & age<300，age每50Hz控制步+2即3s；upright peak只增不减；good要求gz<−.984807753、rootspeed<.03、angspeed<.2，stable每次+2，>=50且未credited才事件。credit是累计状态，不是当前delta。峰值改善、normal recipe、reset后第二episode都不应冒充原首episodecredit。

残余：恢复期orientation/actionacc仍在；零twist tracking提供1.7rate。倒立gx=gy=0时orientation cost0，而90°pitch、cmd0代数cost20即每步−.4；leg alignment使用cos²也不区分正反。这说明中间恢复动作可能受对冲，未证明实际倒立策略可稳定刷分。优先有限phase诊断，不增大恢复速度阈值，不延长3s、不改25good、不扩大软终止mask。

## 6. 候选公式及 learned-WM objective 限制

所有函数仅在[新候选模块](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/reward_command_candidates_v1.py>)，没有安装到环境。

1. **Bounded/rational tracking** `1/(1+(e/s)²)`，选择s=sqrt(d)可匹配原exp中心二阶曲率。非零尾梯度衰减更慢，但坏tracking得到的正reward也更高，可能加剧站立高分；保留原square/gap、只换一个broad项对照，先做rate/scale校准。不是必升方案。
2. **Huber penalty** `H_delta(e/s)` 在中心二次、尾部线性；未截断时有界斜率但代价**无界**。clip会重新引入零斜率尾。替代原square会减弱大误差校正（原square已有梯度），仅作单因素候选，不应“Huber一定解决exp饱和”。
3. **外生任务phase gate**：保留原term/done，先以已有request或预先定义的route phase为状态、有限floor/有限降权；例如E3只在原request内给姿态cost乘.5，正常期乘1。不要用将来是否成功、人工pass label、修改command speed或碰撞力来gate；别给当前已经off的height gate再次“开闸修复”。
4. **有界有向进展potential**：例如`Phi=tanh(signed_progress/L)`，方向/route origin/command UID/phase要属于增广状态。E1真正endpoint仍用wheel-link与正Fz验收；无接触的大位移不等于成功。command切换与reset不得串接。

### Potential-based 的精确条件

[SM配置gamma:31–49](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/learner.py#L31-L49>) 默认gamma=.99，worker未覆盖；原PPO的.9801不是本objective的gamma。 [ctx learned head:135–175,337–353](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L135-L175>) 用原**总scalar reward**、非terminal xi1 delta、done BCE监督，并不精确分解所有reward。

[Imagined objective:388–420](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L388-L420>) 用soft done，`D_t=gamma^t*prod_{k<t}(1-d_k)`，r在本步保留，后续与bootstrap按continuation折扣。令c_t为**同一objective的**continuation：

```text
F_t = gamma*c_t*Phi(s_t+1) - Phi(s_t)
r'_t = r_t + eta*F_t
V'(s_H) = V(s_H) - eta*Phi(s_H)
sum D_t*r'_t + D_H*V' = sum D_t*r_t + D_H*V - eta*Phi(s_0)
```

- terminal应使用原c=0，terminal transition原reward仍保留；absorbing potential与bootstrap一致，预reset物理状态和reset状态严分。当前实现把term|trunc作为done，候选先继承这一语义，不借shaping改timeout bootstrap。
- 若作为manager term输出，rate应`eta*F/dt`，S6再乘dt；若直接增广bridge中的已积分r，则只加`eta*F`，不要再乘/除一次dt。
- `Phi1-Phi0`在gamma=.99一般不等价，E3原record-peak delta本身也不是声称具有PBRS不变性的公式。漏gamma、漏continuation、漏bootstrap shift或串reset都有CPU反例。
- 同一imagined轨迹、同一soft c和正确bootstrap可以得到有限H的**代数**telescoping；这不证明真实物理策略不变。learned WM误差、scalar reward拟合、soft-done失准、critic近似、初始state/reference变化、command held近似均影响实际优化。任意shaping或任意新phase gate没有等价性保证。
- 优先保留原r标签/分项诊断；若下一窗口学习shaped总r，必须单独记录base r与F、重校准head/critic，固定holdout覆盖standing/moving/terminal/censored/越障/恢复，检查reward residual、done校准、多步偏差与优化后exploitation。imagined return上升不是成功证据。

## 7. 下一窗口可执行 A/B（本审计不执行）

[机器可读计划](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/NEXT_WINDOW_AB_PLAN_V1.json>) 与本节一致，所有arm默认disabled/undeployed。

### P0门槛：未过前只做来源与观察验证

1. 父代理先封存当前E0/E2 baseline结果；新source身份、独立输出目录、实际actor/source/配置SHA，原冻结对象不改。
2. 同一物理reference/tick：pre-command、8子步、terminal pre-reset、reward、post-command/obs各自timestamp；确认root-link/COM/quaternion和backend，而非先假定某getter错。
3. 新路径恢复原command演化：E2按predicted heading逐步动态BODY映射，phase/timer按源更新、boundary切段，不重采RNG；C113原axis在ONE fresh reset后、首action前bind，cmd[:3]只做无noise同步（父候选验证），无额外reset/obs compute/RNG。保留DR/physics与原速率。
4. 原接受observer先通过：E2 sampled cycle、W35完整interval、E3累计firstepisodecredit、E1 wheel/Fz/order。E0/S50保持binary gap，不用便捷proxy过门槛。

### 成对arm

- **A0**：冻结语义baseline，原reward、原command sampler、原DR/physics；仅追加有界观察。
- **A1 vs A0**：仅下一窗口coordinate/command语义修正，**原reward不变**。这是协议修正对照，不叫reward改良。E0/E2现行baseline不热换。
- **B1 vs A1**：仅E2/E0的一项broad kernel换rational，scale=sqrt(.25)=.5，原权重/原tight/gap/square保持。先对照误差分布和standing/moving differential，若坏tracking正reward提高却原谓词不升则淘汰。
- **B2 vs A1**：仅E3在已有request内orientation cost乘.5（正常期1），其他奖励、3s/25good、term mask、commands全部原样；比累计credit、recipe分层、ordinaryfail与动作代价，不看当前delta当credit。
- **B3 vs A1**：CURB878、协议修复后的CURB113、S135分别试bounded directed potential；建议eta初值.05（这是新候选，不是原值），L由自己原几何跨度固定，按gamma/c/dt/critic shift条件实现。先单独一角色，up/down/stand/镜像分组；无point/Fz协议则只保留公式不启动。
- **B4 vs A1（较后）**：W35基于原BODY自然interval的bounded progress/phase候选，先确定负vx轴、interval起点和terminal，不使用future pass gate。
- **B5（诊断优先）**：S50仅base reward/command/实际边界曝光与候选公式；原accepted predicate/cohort补齐之前不输出成功率。

每个arm：同等父批准预算、同原角色初态/DR分布、固定原command/RNG规则，配对seed且另留独立seed holdout；不得缩speed、stand拼moving、跨角色pool、改DR/physics或放松原接受阈值。一次只改一个因素，避免kernel+phase+potential同时叠加。

**报告与停止条件**：各原单位真/假/complete/incomplete/close reason、原必要组及ordinary failure分别报告；原条件分母照抄，另加所有已开始attempt ledger防止靠早死减少complete分母。先验冻结比较规则，原group通过未提升或ordinary fail恶化、速度曝光收缩、standing代替moving、head exploitation、getter/UID断裂即不晋级。90%只是外层目标，不应改变历史谓词；E0/S50不填90%。固定E1原27/27/26的小样本也应报告不确定性，而非将standing汇总稀释crossing失败。

## 8. 真实 unknown / 最小补件

已补齐八角色小源、env metadata及SDK reward乘dt；**无需再大范围收集历史源/模型/raw**。剩余是：

1. 八角色实例化wrapper之后最终函数/权重/params、实际term mask、episode clock的bounded livecfg receipt；本报告只source join。
2. 同一backend的getter/frame/cache phase、实际command_used_t/next_t1、root/body-link及每轮8子步正Fz、E3 phase更新与terminal前slot验证。父代理已有观察候选，尚待实际数据。
3. E0所有原profile的binary authority/accepted cohort；S50自己full-ramp的binary authority/cohort（检查范围限已join源）。无这些文本则保持null，不开模型推断。
4. C113 after-fresh-reset axis与无noise obs同步的真实receipt，父代理处理；不将源候选写成已经修复。
5. learned reward/done/WM的独立holdout校准与优化后失真检查；纯CPU公式测试并不提供这些测量。

## 9. 复现与交付

- [候选函数](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/reward_command_candidates_v1.py>) 无IO，仅math；[源join生成器](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/build_source_audit_v1.py>) 只读取89个显式小源并写当前新目录；[测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/test_reward_command_candidates_v1.py>) 只stdlib CPU，不导入被审计模块。
- 最终 **62/62 PASS，0 failures/0 errors，约.025s**。首轮60项有两个fixture键名错误：`KeyError: 'lin_vel_xy'`、`KeyError: 'roles'`；核对真实source后改成track_lin_vel / experts并加两项SDK scale测试。不是隐藏原任务错误；见[执行历史](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/CPU_TEST_EXECUTION_HISTORY_V1.json>)。
- [输入SHA清单](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/AUDIT_INPUTS_SHA256_V1.json>) 与[交付SHA封条](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_reward_review_v1/DELIVERABLES_SHA256_V1.json>) 分开；后者不自引用。父代理管理实际验证与Git。

```powershell
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' -S -B .\build_source_audit_v1.py
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' -S -B .\test_reward_command_candidates_v1.py
```
