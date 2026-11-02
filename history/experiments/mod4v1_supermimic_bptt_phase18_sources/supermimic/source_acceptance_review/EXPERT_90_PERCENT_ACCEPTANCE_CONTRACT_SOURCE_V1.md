# 八条非H1专家：原source接受口径与90%可测性

**SOURCE_ONLY；没有新训练、物理回放或新接受结果；没有发布90%或全技能通过。**

机器合同：[JSON](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json>)。逐专家包含原predicate、原分母、必要group、失败/不完整处理、缺口与确切函数/行号；`sources`固定33个本地源码或已发布metadata的路径/bytes/SHA。H1排除。

## 1. 父训练期间优先保留的mask

1. **BPTT按真实episode边界切断。** 实际terminal transition的奖励仍有效；任意reset、terminated、truncated、缺失tick或不兼容UID均阻止跨episode串接与梯度传播。timeout是否bootstrap遵循原算法，使用真实pre-reset终态，而非autoreset后的观察。
2. **E3软mask不是done。** 原rescue `recipe!=12 & age<300`已经mask `bad_orientation/base_contact`，相关height奖励也按原request屏蔽。世界模型done取真实masked `tm.terminated/time_outs`；`recovery_original_soft`只诊断。计分读`recovery.credited & first_episode_live`，不是含upright-peak增量的`delta`。
3. **E2/W35先固定getter参考点和相位，别用指标反调真值。** begin与第8个2.5ms物理步后的pre-reset终态须同一物理参考点；root-link/root-COM、heading/位置cache时相、四元数顺序须父在未来实际scope独立验证。当前源码足以定位采样位置，尚不足证明现有getter具体错误。保持原数值predicate；无x8修正、无新加速度cap、无body-MAE替代world接受。
4. **E0/E2历史门槛分域。** 历史closure `.002`/mimic `.05`与当前批准`.01`/`.01`不是相同物理gate。历史比较保留first-original-boundary prefix和current-first censor；真实训练done仍用当前原运行逻辑，不热改来模拟历史gate。
5. **原消费者与消费过的V8/pair源码均保持。** 修复方案只描述未来、独立来源绑定的observation adapter；本审计未实施runtime补丁。

证据：[原五角色worker:67–116](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/worker_five_original_n80.py#L67-L116>) · [E3原runtime:9–25、39–66](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/e3_recovery_runtime_v1.py#L9-L66>)。

## 2. 八专家原predicate与分母

下表旧数值仅引自[已发布最终报告](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/MOD4V1_EIGHT_EXPERTS_POSTTRAIN_FINAL_V1.md#L11-L20>)，不是本次新结果。

| 专家 | 原接受/计分原子及必要group | 原分母、失败/不完整处理 | 当前90%可测性 |
|---|---|---|---|
| E0 | 原standing、正/负straight、正/负pure/transition/moving及transition全12s相位；原源码报告body/yaw/height MAE、sampled signed2π/progress，未给完整binary接受谓词 | 诊断为profile×phase population-controls；完整resample→resample命令实例与reset-ended、window-ended、zero-control分开。无binary成功分母 | **原binary规则缺口，rate=null。** 三项MAE改善或无跌倒均不替代原通过 |
| E2 | key8/9 moving±4；同profile/episode/commandUID/world-direction/yawsign、连续8substeps；实际signed turn≥2π；完整且非term/非timeout，并联`abs(along-.5)≤.05`、`abs(cross)≤.05`、`abs((turn-∫yawcmd)/seconds)≤.2` | **完整sampled cycle事件**，不是80env。完整端点同刻term/timeout仍入分母且false；2π前reset/resample/UID改变/窗口尾为incomplete，另报。warmup/steady切换只记录，不break cycle | 原逐cycle数值规则已找到；getter参考点/phase及分group覆盖待证。旧0/187，不能拿body误差当通过 |
| E3 | 固定recipe0–11 rescue；`gravity_z<-.984807753`、**3D root速度norm**<.03、角速度norm<.2且request；stable每50Hz控制+2达到50；request age<300 | **74个初始rescue环境**；12个recipe分别报告。normal recipe12的6个排除。首episode未credit的初始环境仍留分母，后reset credit不拼接；原credit prefix和之后终止事件分别保留 | 原owner-credit可测，但不是已证明的全E3毕业规则。旧0/74→1/74；stable50=.5s=25controls，request300=3s |
| W35/W25 | 原采样`_command_heading+(BODYvx<0)*π`为固定轴，`v=abs(BODYvx)`；`abs(along-v),abs(cross)≤max(.03,.1v)`、yaw误差≤.2；原natural timer到期、start-observed、非term/非timeout；moving/standing按原bool分开 | **自然完整非终止指令区间**；partial/reset/unknown-start/source-break/窗口尾不在原条件分母，逐类保留。随机`cmd.direction`未被原BODY任务使用 | 原规则已找到；参考点/phase和policy-dependent UID population待证。旧moving18/61→18/64，stand26/26。总44/90及catalog goal0均不替代moving接受 |
| C878 | 自己的20mm垂直curb/150mm strip；双轮canonical link-x从`max(u)<-.275`到`min(u)>.275`，下行反向；同episode有序，前后两端双轮均正Fz均值>1N | **上27/下27初始环境**，失败/未完成都留分母；只能首ordinary之前的同episode prefix计分；stand26独立，无cross要求 | 原scope predicate可测。旧上22/27→26/27、下27/27；不是全curb/hardware毕业 |
| C113 | 独立113 own geometry/starts/reset方向；与上行列相同原endpoint/contact算式，但来源/actor独立 | 上27/下27；stand26分开；不跨reset拼endpoint，未完成不删分母 | 原scope predicate可测。旧上22/27、下27/27；源选择非退化不等于≥90 |
| S135 | **单独5°/2m连续坡道**，双轮canonical endpoint为±1.2m（坡段±1m外各.2m支撑）；sameepisode ordered endpoints+双轮正Fz>1N | 自己的上27/下27；stand26独立。保留首ordinary前prefix，窗口/timeout不足完整route仍留原环境分母 | 原scope predicate可测。自己旧上25/27→27/27、下27/27。历史accepted scope的27/27事实不被新90目标改写 |
| S50 | own `SLOPE5_full_ramp_and_both_flat_supports`训练轴；target family4的boundary为tile-center `abs(dx)>3.5 or abs(dy)>3`、20s、自然command/DR/RNG；**这些不是接受谓词** | own accepted完整fullramp cohort/原binary规则未join；故原成功分母null。boundary/timeouts/无跌倒仍为描述性事件 | **原binary与accepted-cohort缺口，rate=null。** 旧ordinary0、boundary41→46/timeout47→43都不是fullramp通过；不借S135±1.2或27/27 |

E1 contact按**8个physics callback**的`sum(max(Fz,0))*.0025/.02>1N`，不是force-norm、单个瞬时力或误用100Hz控制。名为`COM_link_pos`的旧字段在当前worker读取的是`body_link_pos_w`，保持真实点语义。

E1原prefix predicate允许“先完整通过、后来终止”的完整prefix仍计credit；晚失败独立报告，避免把新全窗无失败AND条件偷接到旧predicate里。stand的ordinary-free仅是原standing保留事实，既不算crossing，也不证明整体专家技能通过。

## 3. 精确可接入的原source点

- **E2 getter**：[bridge:15–18](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/minimal_e2_cycles_bridge.py#L15-L18>)，begin读`root_pos_w/heading_w`，terminal在termination wrapper内读相同getter；[cycle:44–127](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/e2_cycles213.py#L44-L127>)负责UID/完整性/原joint。未来adapter先绑定参考点、cache/tick、四元数与pre-reset顺序；在同writer追加正负group complete/false/incomplete和close-reason计数，predicate不变。旧producer的b3标签是谱系，不覆盖实际actor SHA。
- **W35 getter/目标**：[open/begin/terminal/close:76–170](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py#L76-L170>)与[worker:103](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/worker_five_original_n80.py#L103>)：before `root_pos_w/heading_w`对after `_e1_pre_reset_frame['root']`必须独立证明同参考点/phase；root-COM偏移不能猜。已有[future split:11–36](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_assess_pair4_v1/observer_w35_split_v1/rm70_published_split_observer_v1.py#L11-L36>)直接读取原standing/complete/accepted bool，满足分拆但不修复getter/UID证据缺口。
- **E3计数**：[phase:6–10](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E3_MOD4V1_SOURCE_FINAL/runtime/isaac/mod4/e3_public_recovery_phase_v1.py#L6-L10>)与[worker:85–112](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/worker_five_original_n80.py#L85-L112>)；未来同writer补初始recipe/episode、firstcredit/firstterm/firsttimeout/deadline与缺失数，保留原source更新先后。
- **C878/C113/S135**：[endpoint:5–31](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_endpoint_predicate.py#L5-L31>)、[worker:62–97](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_parallel_worker_safe.py#L62-L97>)；按wheel名称、own tile center/orientation、真实episode和8步Fz消费。自己的factory/starts/40+40 mirrors与原command保持，不按root位移替代双轮endpoint。
- **E0补观测**：[E0Panel.begin/terminal/finish:161–206](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/acceptance_contract_sourceonly_v1/original_reference_text/E0_METRICS__e0_long_command_domain_telemetry_v1.py#L161-L206>)已具profile/phase/UID book；可补same-writer完整命令aggregate。原binary接受authority仍须从原文本join，E2阈值不可直接借用。
- **S50原规则寻找结论**：检查了own [producer axis:16–43](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/E1_SLOPE_INDEPENDENT50_40050_MOD4V1_SOURCE_V2/producer/independent_expert_axis_v1.py#L16-L43>)、geometry、retention、pre-reset trace、own canonical metadata，以及[ROLE_CONTRACTS:998–1011](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/ROLE_CONTRACTS.json#L998-L1011>)。它明确是`DEFAULT_TRAINING_AXIS_DESCRIPTIVE_SCREEN_NO_ORIGINAL_ACCEPTED_COHORT`；[现worker:23–42、103–105](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_parallel_worker_safe.py#L23-L105>)没有fullramp accepted branch。未来先从**原own已发布task-contract/scope authority**接入真正判据，再挂pre-reset observer；此处源码查找结论仅覆盖已列33份证据，不声称搜尽所有远端/历史文件。没有重开checkpoint或旧raw补表。

## 4. 80%中间目标与≥90%最终目标如何报告

**80/90是本次用户新增外层目标，不是旧source已有总体毕业规则。** 原原子predicate与物理gate保留。E0/S50缺原binary时保持pending，八条整体目标也保持pending。

- endpoint/rescue固定初始cohort：所有合格初始环境在分母内，失败/不完整/缺记录不给成功；E3 normal6不进入rescue74。
- E2/W35事件：原complete条件分母与incomplete总数同时给出。早失败/窗口尾均不抹掉；不要只报幸存完整事件的漂亮比例。
- 若需要覆盖所有启动尝试的保守外层credit，**先**固定attempt单位和唯一ledger，再另报`source_true/(true+false+incomplete+unknown)`。它不是原complete-event rate；同UID的多段partial也不能直接当多个独立attempt。
- 不汇总八专家成一个百分比；moving/standing、E2正负、E3十二recipe、上/下行分别给分子/分母及缺失。无暴露=待证，`0/0`为null，不是100%。stand不补moving不足。
- scope技术缺陷、retention-limited、missing ticks、unknown-reset或未验证getter均让证据待补；不删异常行后发布新通过率。

## 5. 多seed建议（未执行）

1. 父继续拥有双卡、原canonical owner、真实WM/BPTT训练与后续实际验证。每条至少几千**真实policy optimizer更新**；建议排程下限3000仅为计划，不是本审计结果。WM-only更新、minibatch数、想象rollout数和旧20PPO均不充当policy更新达标。
2. 开发seed与最终holdout分开；先固定最终policy SHA，再读holdout。机器合同建议3个开发seed、10个固定holdout seed，数字均为seed值而非执行日期。所有建议运行数=0。
3. 每seed保留own N80/window/DR/commands：E3 74+6，E1 27/27/26及40/40镜像。E2/W35另外交付原事件分母、partial close-reasons、group暴露和episode/UID来源。
4. 每专家/必要group/seed分别给point estimate、Wilson95%和seed间变化。重复command事件有env/seed相关性，event-count Wilson不是独立环境可靠性证明。若要置信地证明总体≥90%，额外预注册更强下界规则并增加独立样本；不事后把90%点估计改解释成置信下界。
5. 最终真实接受来自父拥有的原物理评估与原predicate，世界模型预测成功、训练reward或无跌倒都不替代。

## 6. 本地纯CPU工具与保留记录

- [聚合器源码](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_acceptance_review/acceptance_aggregate_cpu_source_v1.py>)：仅stdlib `math`、内存参数；严格bool/唯一unit/固定分母；区分原条件分母和另名all-started credit；缺predicate或未验证getter时rate=null；始终没有毕业/目标达成裁决。scalar helper仅合成语义演示，真实适配优先读取原writer bool，避免CPU float64与GPU float32边界差异。
- [54项合成测试源码](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_acceptance_review/test_acceptance_aggregate_synthetic_v1.py>)与[测试回执](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_acceptance_review/SYNTHETIC_TEST_RECEIPT_V1.json>)：54项、0 errors、0 failures。覆盖跨reset、term/timeout完整cycle、normal排除、25控制stable、双轮Fz、S50禁借S135、group缺失/重复、未验证getter、零分母、source SHA不变及纯原EndpointPredicate合成等价。**这只是软件测试，不是54次真实技能通过。**
- [合同生成源码](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_acceptance_review/build_contract_source_v1.py>)保留显式文本allowlist；JSON的`lookup_notes`保留缺路径、错误basename、空源副本等查找试错。原文件不删不改；本次未出现合成测试失败。

本次计数：**新policy更新0，新物理运行0，新接受结果0，PT/raw/NPZ/JSONL内容读取0，SSH/SDK/GPU/Git操作0，C盘任务文件打开/写入0，原消费源码修改0。**
