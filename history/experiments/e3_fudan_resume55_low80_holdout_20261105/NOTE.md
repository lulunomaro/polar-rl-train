# V33 — 冻结8e27三seed原生低姿实际holdout

- Goal c490 rev3 active/armed/round7/14，H1/其它专家/Registryv12/1cd不变。无新训练，仅冻结8e27完整Root8输入。
- 首episode连续25信用22/240；严格终点当前连续25 0/240；曾信用＋末帧good 12/240；物理终止0/240。旧21/240不同seed，严格终点null，不假配对。原E3仍0/74单列。
- [主要结果](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_RESUME55_LOW80_HOLDOUT_RESULTS_V1.md>) / [分析](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_RESUME55_LOW80_HOLDOUT_ANALYSIS_V1.json>)，实际原父资格+innerouterwait/SDKclose/private-finite释放全部核验，模型每case一次/组三次，0优化。
- 未自动晋升/未goal complete，源码/失败/实测与报告待meaningful feature-only唯一annotated归档，main只读；不得重跑旧once或为状态/Git重开模型。


# 冻结8e27：三seed原生fullDR低姿holdout

**首episode连续0.5秒信用 22/240（9.17%）；终点当前连续≥0.5秒 0/240（0.00%）；曾获信用且末帧good 12/240。**

| Seed | 首episode连续25信用 | 严格终点当前连续25 | 曾信用＋末帧good | 首episode物理终止 |
|---|---:|---:|---:|---:|
| 20261002 | 9/80 | 0/80 | 3/80 | 0/80 |
| 20261003 | 7/80 | 0/80 | 5/80 | 0/80 |
| 20261004 | 6/80 | 0/80 | 4/80 | 0/80 |

## 五个原合法姿态，每姿跨seed分母48

| Pose | 首episode连续信用 | 严格终点连续25 | 曾信用＋末帧good |
|---|---:|---:|---:|
| 0 | 8/48 | 0/48 | 3/48 |
| 1 | 7/48 | 0/48 | 6/48 |
| 2 | 3/48 | 0/48 | 2/48 |
| 3 | 1/48 | 0/48 | 0/48 |
| 4 | 3/48 | 0/48 | 1/48 |

## 语义与边界

Strict terminal = first_episode_ever_credit AND first_episode_physically_live_at400 AND terminal_current_good_streak_controls>=25。current_streak在第400控制同原pre-reset hook保存，逐步原good更新，不拼reset。旧兼容字段ever+末帧good单列，不当严格终点。原55afa历史21/240使用不同三个seed，旧严格终点未记录仍null；两批不是配对因果。

末帧仍第一episode的失败分量：`{"height_ok": 0, "upright_ok": 0, "speed_ok": 113, "angular_ok": 15, "wheels_ok": 0, "chassis_ok": 0, "joint_good": 121}`（可重叠）。根速mean=0.03188907208483822、median=0.029258464463055134m/s；历史最长good中位14.0控制，当前末段good中位0.0控制。物理未终止不等于联合连续通过；不从这些观测强推某一DR、reward或optimizer的因果根。

三独立constructor cfg.seed=20261002/03/04；每80=五legalpose各16、400控制8秒、原sole fresh reset/fullD0D7/2c-bae/31体/50policy100feedback/.0025/TGS32,4/400N-k2000-d3/closure.01m per-env reset/mimic.01不变。每case整份Root8 N20000源一次物理read/hash/CPUdecode/whole未知根CPU缓存，只有14pi/82505scalar frozen mean GPU；组实际3次，无learner/optimizer/newPPO或source DR/history投影。

原实际privateGPU_EX/finite_EX/ownerNone+reserve/fresh资源/1800门控、SDKclose/actual child+outer wait及cleanup释放均通过。母版native参考未运行，paired差值null，不以同seed或名义MuJoCo5/5声称native因果。原E3上轮0/74单列未重测，不并入240；H1/其它专家/Registryv12/1cd保持，保留完整8e27，不作整专家毕业或硬件/视频整腿同端宣称。

[完整分析](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_RESUME55_LOW80_HOLDOUT_ANALYSIS_V1.json>) / [实际scope与资格](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_SCOPE_RESULT.json>) / [原闭环](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_CLOSED_RESULT.json>)。本阶段全部源码、旧静态定位失败与最小修复、实际原生结果/报告待meaningful feature-only唯一annotated trial及远端核验；main只读，不为Git重开模型/raw/旧物理/once。Goal active，未完成。


# 冻结55afa：独立原生low80 × 三seed确认（不是原74评分）

执行资格：**True**；aggregate信用 **22/240**；获得过信用且400控制末帧稳定 **12/240**。

| Seed | 第一episode连续.5s信用 | 8秒曾获信用且末帧good（非连续25） | 物理终止 |
|---|---:|---:|---:|
| 20261002 | 9/80 | 3/80 | 0 |
| 20261003 | 7/80 | 5/80 | 0 |
| 20261004 | 6/80 | 4/80 | 0 |

每个case是独立process/constructor seed/原fullD0D7与sole fresh reset，五个原合法pose各16、400控制/8秒；无learner/optimizer或checkpoint环境状态恢复。所有第一episode信用在reset前冻结，不移除物理失败样本或拼接多episode。原门限h≥.23/gz<−.984807753/v<.03/omega<.2/双wheel>1N/chassis<1N，连续25控制；终点另列。

本组是candidate-only第一批fullDR确认，**母版native配对参考尚未运行，差值null，不声称matched因果**。三个case各source一次physical/hash/CPU decode、wholeN20000未知根CPU保留、14pi上线；组预期三次真实输入，而非全组一次。原E3 74+6仍沿用上一真实0/74/normal物理0/6，不被新80分母覆盖或合并，Registryv12/1cd/H1/其它专家不动，goal保持active。

执行失败/未启动时分数null；真实原父privateEX/finiteEX/CownerNone/reserve、actual child/outer wait、App原close、错误和释放由原链闭环，collector只读自身JSON，不重跑资格或SDK、不开模型/raw/C。

[完整结果](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_SCOPE_RESULT.json>) / [实际闭环元数据](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNRESUME55_LOW80_HOLDOUT_ADMISSION2_CLOSED_RESULT.json>)。本轮全部代码/成功失败/报告待一次有意义feature-only唯一annotated trial归档，main只读，不为Git开模型/旧raw/物理。


## Archive boundary
Three explicit independent constructor-seed low80 candidate-only frozen confirmation cases, five legal poses x16 and400controls8seconds/fullD0D7/originaljointthreshold25controls. No new training/learner/optimizer. Candidate8e27 wholeN20000 CPU/raw/unknowns retained once per real case,14pi only; expected aggregate3sourceIO, not false whole-group1. Reference native cohorts not run and paired difference null. Original74plus6 score remains prior0of74, not overwritten or combined. Strict terminal current controls>=25 is serialized and distinct from loose ever+final-frame-good; first episode credits/max good/first time/physical endings/endpoint conditions separated, no reset stitching or deleted failed denominators. Preserve original privateGPU_EX/globalfiniteEX/CownerNone/reserve/1800wait/ready900/2400worker and actual child+outerwait/error/SDKclose/release. Prior zero-start/metadata errors and any conditional new-purpose resource-release continuation remain separate evidence, not relabeled as scores or samepurpose model retries. Whole original runtime/lib/assets/staticNPZ kept. Registryv12/1cd/H1/otherexperts unchanged, goalactive. Full original record validation/redaction/hashes and exact staged set retained; two short add scopes only; feature-only and readonly main, no model/raw/oldonce/physics for Git.


## Same prepared archive precommit continuation
Original recorder stopped before metadata/staging/commit on archive-copy source placeholder detection. Original capture_history.redact now applied to archive copies; original/source SHA and archive SHA/count/reason indexed, no matched values emitted and workspace originals untouched. All original validation/redaction/hash checks retained; same unique trial, no physics/model/old record-source replay. Failure and continuation included.
