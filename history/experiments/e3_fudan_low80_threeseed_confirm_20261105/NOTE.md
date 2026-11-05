# V26 — 三seed fullDR low80确认已真实收口，稳健性不足

- goal c490 rev3 active/armed/round5/14；无新训练、全部Native/collector/handoff已收口。
- 第一批1800原门控zero-start/nullscore原样保留，后actual只读release再新Admission2；本轮3独立seed80/400/five16/fullDR/原门限全qualified。
- 首episode连续.5s信用 21/240；曾获信用且400末帧good 7/240；终点连续25streak未序列化，严格末段连续计数null，原producer标签与读者解释边界均保留。原74仍0/74，不合并分母，不晋升Registry，55afa保留/H1其它专家不改。
- 实测三seed均已actual qualified：20260929为8/80首次信用、3/80 ever+末帧good；20260930为8/80与2/80；20261001为5/80与2/80。物理终止0/240不当接受；末帧h/upright/wheels/chassis失败各0、root_speed失败124/240、angular12/240、joint129/240（可重叠），根速均值.034450/中位.030714，最长good streak中位15ctrl=.3s。仅观测连续低速不足，不猜XYZ分量或因果reward/DR根。
- 第一批controller1641981/parent1641988原1800自然过期后实际innerouterwait/双EXrelease/空child_waits，全case/null/信用null，不改pass；summary watcher1793838539.2548356实际ownerNone（remaining196743.7411711216历史read），才新root FDNLOW80_CONFIRM_ADMISSION2_THREE_SEED_N80_20261105_082859_1793838539228363300，controller1643951/parent1643958/原相同13source，3fresh成员由原父全fresh门控/common barrier/400ctrl/3200physics/800feedback/实际wait-close-releases qualified。workerPID没有另查/不虚构；job41c7533d6f324ae4已completed0/fulloutput collected，原f4db8d44c7814d5b也completed0/collected，没有新增Native/observer任务。源55afa每case一次physical/hash/CPU decode，组实际3，无optimizer/母版参考/source20kDR/history恢复，原fullDR不改。
- [下一项有限验证文字计划](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/NEXT_SINGLE_INTERVENTION_CONTINUE55AFA_FINITE25_PLAN_V1.md>)：若继续，只从真实55afa whole learner精确续≤25、base25/两Adam500/24m与新window分开，保留mutable实际LR2.562890625e-6/两Adam/encoder/logSTD/privategenerator，不重warm1cd、不改reward/STD/LR/core/DR/阈值。新env20k fresh stream cut不恢复source DR/history/queues/pending/globalenvRNG，输入一次CPU immutable，未知根保留。可加仅被动root速度XYZ/终点当前streak诊断，预留20261002/03/04新seed质量确认。当前只是计划，无新续接source/准入/物理，goal仍未达到。
- [主要结果](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOW80_THREESEED_CONFIRMATION_RESULTS_V1.md>) / [完整分析](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOW80_THREESEED_CONFIRMATION_ANALYSIS_V1.json>)，原first source/metadata与新source不重放/不重开模型。源与报告等待本轮一次meaningful feature-only Git，当前latest7e0245；goal质量尚未完成。


# 冻结55afa：三seed原生fullDR低姿确认结果

**实际资格通过；首episode连续.5秒联合信用 21/240（8.75%），曾获信用且8秒末帧全部条件满足 7/240（2.92%）。**

这没有证实稳健起身：原E3评分仍沿用0/74，本轮不改分母/门限、不自动晋升，Registryv12/1cd/H1/其它专家不变。

| Seed | 首episode连续25控制信用 | 曾获信用且末帧good | 首episode物理终止 |
|---|---:|---:|---:|
| 20260929 | 8/80 | 3/80 | 0/80 |
| 20260930 | 8/80 | 2/80 | 0/80 |
| 20261001 | 5/80 | 2/80 | 0/80 |

## 五个原合法姿态（跨三seed，分母各48）

| Pose | 连续信用 | 曾获信用且末帧good |
|---|---:|---:|
| 0 | 3/48 | 0/48 |
| 1 | 5/48 | 1/48 |
| 2 | 3/48 | 1/48 |
| 3 | 7/48 | 3/48 |
| 4 | 3/48 | 2/48 |

## 终点标签边界与失败反馈

旧producer字段 `credited_and_stable_at_end=7` 的实际公式是『此前曾获连续25控制信用 AND 第一episode仍存活 AND 第400控制单帧joint_good』；**它不是最后.5秒连续满足的计数**。末帧streak未序列化，严格末段连续25信用记null，不伪造为7或0。原JSON、实际物理、资格及门限不变；原自动报告标签备份保留，单列[读者语义澄清](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLOW80_CONFIRM_ADMISSION2_ENDPOINT_READER_CLARIFICATION_V1.json>)。

首episode物理终止 0/240。仅在第400控制仍属第一episode且无物理终止的样本统计端点失败分量：`{"height_ok": 0, "upright_ok": 0, "speed_ok": 124, "angular_ok": 12, "wheels_ok": 0, "chassis_ok": 0, "joint_good": 129}`；分量可重叠。末态根速均值 0.034450m/s、中位 0.030714m/s；最长good streak的跨env中位 15.0控制。它们是本轮观测，不是奖励/优化器/DR单项的因果根诊断。

## 实际协议、保留与边界

三独立process，各constructor cfg.seed=20260929/20260930/20261001；N80=五pose各16，400控制8秒，sole explicit fresh reset，原50/100/.0025/TGS32,4/400N-k2000-d3/2c-bae/fullD0D7/闭链.01m与mimic.01保留。第一episode在原pre-reset hook冻结，物理失败不删除/reset不拼接。传感噪声/lag仍原链，无额外观测采样。全部callbacks3200与feedback800/actor400，权重前后不变、无优化器更新。

候选only，本批母版native参考没有运行，paired差值null；不能拿同seed或旧名义5/5声称native因果改善。名义MuJoCo此前5/5曾达标而终点0/5，与本轮fullDR三seed分列，不迁移分母。保留完整55afa，不证明整腿同端视频/硬件/原74专家毕业。

第一批原1800资源等待自然过期，全case/null、无admission/SDK/模型，分数null；实际inner+outer wait/原双EX释放后，独立只读summary watcher真实观察ownerNone，才新Admission2。新原父再做全部fresh资源与reserve检查，实际common barrier/三worker/close/child+outer wait/释放全qualified；不清外国锁、不signal、不改账/复制预算/退款/延长父或重放旧once。每case整份N20000 checkpoint一次physical/hash/CPU decode/whole未知根CPU保留，只14pi上线；组实际三次，不谎称全组一次。

[完整分析](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOW80_THREESEED_CONFIRMATION_ANALYSIS_V1.json>) / [实际资格与scope](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLOW80_CONFIRM_ADMISSION2_SCOPE_RESULT.json>) / [原闭环metadata](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLOW80_CONFIRM_ADMISSION2_CLOSED_RESULT.json>)。本轮所有源码/失败/澄清/报告待一次有意义feature-only annotated trial与远端核验；main只读，模型/raw/旧物理不为Git重跑。goal保持active。


# 冻结55afa：独立原生low80 × 三seed确认（不是原74评分）

执行资格：**True**；aggregate信用 **21/240**；此前获过连续信用且第400控制单帧联合good **7/240**（未证明最后.5秒连续）。

| Seed | 第一episode连续.5s信用 | 曾达标且8秒末帧good | 物理终止 |
|---|---:|---:|---:|
| 20260929 | 8/80 | 3/80 | 0 |
| 20260930 | 8/80 | 2/80 | 0 |
| 20261001 | 5/80 | 2/80 | 0 |

读者语义更正：producer 的 `credited_and_stable_at_end` 实际是“此前曾连续达标且最后一帧全部条件good”，不是“末段连续.5秒”。原末帧streak未序列化，严格末段连续25信用计数为null；原JSON/资格/物理不变，原自动报告标签备份及[澄清记录](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLOW80_CONFIRM_ADMISSION2_ENDPOINT_READER_CLARIFICATION_V1.json>)保留。主要[完整分析报告](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOW80_THREESEED_CONFIRMATION_RESULTS_V1.md>)另列速度/角速失败分量。

每个case是独立process/constructor seed/原fullD0D7与sole fresh reset，五个原合法pose各16、400控制/8秒；无learner/optimizer或checkpoint环境状态恢复。所有第一episode信用在reset前冻结，不移除物理失败样本或拼接多episode。原门限h≥.23/gz<−.984807753/v<.03/omega<.2/双wheel>1N/chassis<1N，连续25控制；终点另列。

本组是candidate-only第一批fullDR确认，**母版native配对参考尚未运行，差值null，不声称matched因果**。三个case各source一次physical/hash/CPU decode、wholeN20000未知根CPU保留、14pi上线；组预期三次真实输入，而非全组一次。原E3 74+6仍沿用上一真实0/74/normal物理0/6，不被新80分母覆盖或合并，Registryv12/1cd/H1/其它专家不动，goal保持active。

执行失败/未启动时分数null；真实原父privateEX/finiteEX/CownerNone/reserve、actual child/outer wait、App原close、错误和释放由原链闭环，collector只读自身JSON，不重跑资格或SDK、不开模型/raw/C。

[完整结果](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLOW80_CONFIRM_ADMISSION2_SCOPE_RESULT.json>) / [实际闭环元数据](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNLOW80_CONFIRM_ADMISSION2_CLOSED_RESULT.json>)。本轮全部代码/成功失败/报告待一次有意义feature-only唯一annotated trial归档，main只读，不为Git开模型/旧raw/物理。


## Archive boundary
Three explicit independent constructor-seed low80 candidate-only frozen confirmation cases, five legal poses x16 and400controls8seconds/fullD0D7/originaljointthreshold25controls. No new training/learner/optimizer. Candidate55afa wholeN20000 CPU/raw/unknowns retained once per real case,14pi only; expected aggregate3sourceIO, not false whole-group1. Reference native cohorts not run and paired difference null. Original74plus6 score remains prior0of74, not overwritten or combined. First episode credits/max good/first time/physical endings/endpoint conditions separated, no reset stitching or deleted failed denominators. Preserve original privateGPU_EX/globalfiniteEX/CownerNone/reserve/1800wait/ready900/2400worker and actual child+outerwait/error/SDKclose/release. Prior zero-start/metadata errors and any conditional new-purpose resource-release continuation remain separate evidence, not relabeled as scores or samepurpose model retries. Whole original runtime/lib/assets/staticNPZ kept. Registryv12/1cd/H1/otherexperts unchanged, goalactive. Full original record validation/redaction/hashes and exact staged set retained; two short add scopes only; feature-only and readonly main, no model/raw/oldonce/physics for Git.
