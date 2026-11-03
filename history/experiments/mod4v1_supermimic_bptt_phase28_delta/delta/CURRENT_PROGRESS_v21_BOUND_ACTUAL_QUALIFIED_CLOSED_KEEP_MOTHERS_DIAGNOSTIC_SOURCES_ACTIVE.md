# 当前交接 v21：bound真正准入、合格关闭并评分；保持母本，转模型/激励诊断

2026-11-03 14:02 +08:00。Goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` 最近revision13/activearmed/round8/max48；质量优先，训练次数不是完成条件。H1/所有母本/Registryv12、原2c/bae物理/fullD0D7/速度/接受口径/预算及锁不变。原80%中间/90%独立多seed未达，E0/S50原binary authority仍null；Goal不complete/不blocked。v20尚未Popen的状态已由本文件真实结果追加。

## 新Admission2实际执行而非旧timeout翻案

[只读释放witness](<reports/BOUND_PROBE_V1_RESOURCES_RELEASED_AFTER_ZERO_GO_TIMEOUT_V1.json>) epoch1793684418.6680818（13:40:18）确认原C.active_segment=null、所需kernel锁清、GPU0 free24203MiB/util0/computeempty以及RAM/disk/reserve门。它不是租约；原新父实际重新检查门后准入。

```text
new root /home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_BOUND_ONLY_E3_W35_PROBE_V1_ADMISSION2_20261103_131547_1793682947729489800
source17 indexd051 / stageb1d88c0084f3219051f4e8a28c395bed990e65fd25934ab98570ec5b5b31eaa1
actual Popen1793684451.15605
controller1527965/ticks142583493
originalparent1527972/ticks142583516
actualparent exit1793685012.9502265（13:50:12）
external Popen.wait returned1793685013.0188835 / RC0 / controller_errors[]
original privateGPU_EX/finiteEX released / all own child p.wait / canonical writes0
E3 N80 160ctrl / W35 N80 1600ctrl / optimizer_updates0
qualified_bound_probe_execution = true
```

原parent63ea/controller818e/17闭包保持；原raw35噪声延迟/history10/knowncmd3/trueTTr/frozen norm/wholeCPUcache+teacher+pi guard、原RSL6219源码门、原close/wait/sourcegrade都通过。**这是同权重 `.05*delta→.05*tanh(delta)` 总clip6的零更新部署约束探针，不是新训练。** 原首root0GOtimeout/RC1/SDK模型0保留，不重放、改判或扩deadline。

实际新 [闭环元数据](<reports/ACTUAL_BOUND_ONLY_E3_W35_V1_ADMISSION2_20261103_134126/CLOSED_RESULT.json>)，dispatch `pwsh-f4dc523ead834831`、唯一observer `pwsh-f15cd58ee2f7489d` 均RC0/已收取。**当前没有自己的GPU训练/评测、原资源observer或未收取的运行job。**

## 实际原口径评分与选择

[NEW W35单次原分组评分](<reports/BOUND_ONLY_E3_W35_V1_ADMISSION2_W35_ORIGINAL_SPLIT_ACTUAL_GRADE_V1.json>) 的脚本仅在合格关闭后对这个NEW artifact remotely单次stream+schema/FINAL绑定，不下载raw/不读旧raw/不打开模型/C/SDK；`pwsh-67ed5e48d88a4a02` RC0/已收取。原natural-complete/nonterminal/standingBoolean/UID接受不变，数据完整性true/unknown0，partial/reset/term/trunc全保留。

| 原条件 | 原教师 | 未约束候选 | 新bound零更新 |
|---|---:|---:|---:|
| E3 requested firstepisode原stable credit |0/74|0/74|0/74|
| W35 moving |19/63 (30.16%)|10/69 (14.49%)|14/60 (23.33%)|
| W35 standing |26/26 (100%)|16/17 (94.12%)|13/22 (59.09%)|
| E3正常recipe12首次物理term，排除74恢复分母 |0/6|6/6|0/6|

bound moving partial178/reset118/物理term0/trunc118、standing partial36/reset16/物理term0/trunc16，Wilson95分别[.1443956174,.3543627038]与[.3873481848,.7674418380]。**无物理终止并不等于原技能通过**。原teacher/unbounded各partial和完整分母也保留。single seed20260928/独立自然cohort，matched UID/pose、relative、统计因果提升均null。

[三组机器筛选](<reports/BOUND_ONLY_E3_W35_ORIGINAL_QUALITY_SCREEN_V1.json>) 与 [人读报告](<BOUND_ONLY_E3_W35_ORIGINAL_QUALITY_SCREEN_V1.md>) 来自metadata only、`pwsh-4baf2c62e340493a` RC0/已收取。结论 **KEEP_REGISTRY_V12_SCOPED_BEST_NO_CANDIDATE_PROMOTION**；恢复仍0、standing保持欠佳，不为凑3000盲目扩大任一旧方案/不调度新训练。当前判据不接受用零更新约束效果冒新训练收益。

## 下一轮有用的SOURCE任务（均独立新dir、当前未上CPU/SDK/native）

旧82/405在03:34失败并已由独立源码恢复审阅处理，不能再当活跃resident。当前3个新独立agent:

1. `efbd16d5-715d-4031-8af2-ea024bd53095` → `source_replay_consistency_diagnostic_v1`。读真实vendor/bridge/core API开发CPU只读saved-WM/aux/actor回放一致性诊断，不开真实PT/raw/SSH/SDK/GPU/C/Git。父以后才可在**新的实际模型诊断用途**对E3a4/W35b2 own fullcheckpoint各一次bytes/hash/CPU weights_only decode，保全root值/版本/raw，不restore optimizer/RNG/env或改原source；不是status/表格重读。采样有界，ring/done/streamcut/xi1_valid/history严格，H16沿真实动作true-xi条件state openloop与可行的state+context free-chain分开。**saved replay曾参与训练，所以仅resubstitution一致性，不称heldout/因果/技能**。teacher来自同pi不重开mother。代码封SHA/父审阅后才执行，当前尚无诊断结果/真实模型新打开。
2. `a194a451-f51b-471a-bcbd-765d5e40093e` → `source_e3_signed_upright_reward_review_v1`。仅disabled单因子learner reward候选/stdlib反例，不造nativeexecutor。真实source证明g_z=-1upright、+1inverted，u=(1-g_z)/2；原peak本已signed，不能说TOTAL无signed/倒立总reward0或根因已证明。prestep request age298→after300时仍按request_t；originalreward/peak+stable保留，normal6新项0、r_original/r_shaping/r_learning分开，不变termination/接受。默认κ_NEW=null/enabled:false，非PBRS不作policy-invariance保证；数学κ80/64仅原orientation单步小角代数尺度，不是建议/历史权重。没有新训练/效果证据。
3. `d66482f4-bbf6-4ad6-a2b4-231a32e6bf8a` → `source_good_expert_holdout_subset_v1`。对历史较好的C87826/27up与S13527/27up、其down27/27/stand26/26，准备独立seed20260929/20260930的原N80/750ctrl保持评测SOURCE，而不是扰动母本再训练。复用actual0update A1 captures内的原teacher均值（身份/冻结/原E1one reset/done/source闭包不弱化），只2角色其余deferred，母PT不再开。先分析actualE1factory、seed硬pin、subset schema/barrier，精确最小源码+fake/AST，不做大框架/不stage/不claim已测。E0/S50missing authority不虚构。

## Git与后续

Phase27 remote exact verified：HEADb2c500f91a3bc9c351065bd1bdd0bee0b11bb77c，annotated e2f5e17208a4e2082d1cd05dacc46ecbb29e3b4e；main仅读163aee…独立推进。NEW [Phase28准备器](<prepare_archive_phase28_actual_bound_screen_once.py>) 已执行仅生成source，NEW [Archive28脚本](<archive_phase28_actual_zero_update_bound_screen_delta.py>) 尚未执行：门必须绑定本次真实外层p.wait+原EX释放，note根据qualified/error/实际quality metadata，不将旧0GO翻案；保留所有源/方法/失败及点时刻partial，跳selected模型于stat前、raw/binary大文件仅producer引用，不为Git重跑physical/CPU/评分。此h21/本次真实quality/释放/新source任务将在Phase28追加。归档后推**既有feature+唯一annotated trial**并核验remote branch/tag object/peeled/currentmain，不能reset/push main；迟到新源/诊断另后续append。
