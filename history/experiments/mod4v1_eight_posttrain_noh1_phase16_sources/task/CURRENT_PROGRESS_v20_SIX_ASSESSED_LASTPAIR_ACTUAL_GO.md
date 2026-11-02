# 最新v20：六条actual20+原scope评估闭合，最后W35+S50实际GO

继承[v19](<CURRENT_PROGRESS_v19_FOUR_BEST_DECIDED_PAIR3_ACTUAL_GO.md>)全部原源/20k状态/原singleC/预算/锁/物理与DR规范。Goal `goal-1348948b-8b3e-4e93-85ec-317e88962347` revision8 active/armed（last rounds2/max12），H1始终冻结，**尚未8条实际完成，不complete/blocked/新goal**。

## 6/8各20真实PPO及原scope评估已完成

[六专家结果](<ASSESSED_MOD4V1_POSTTRAIN_6_EXPERTS_RESULTS_V1.md>) · [Registry_v11](<EXPERT_NORMALIZATION_REGISTRY_v11.json>)。
E0/C878/C113/S135选新Candidate；E2/E3保FrozenMother，所有newcompletecheckpoints与mothers都保、原selected_formals不改。E0三诊断改善；C878上22/27→26/27下27站26；E2vy+0.00005794虽vx/yaw改善仍保母本/原world0/187gap；C113原上22下27站26保持。全部单seedfresh80原scope，不宣完整20k接受总体/硬件/全技能毕业。

第三批原parent1465093/E31465108+S1351465117，14:25:42/43真实GO；**14:45:54epoch1793601954.3717823 两RC0/完整新save/envAppclose/父actualwait/原costsettled/原EX+SHreleased/errors[]**。[训练summary](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR3_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json>)：
- E3 actual20/400optcalls/960万transitions，iter43110/17Adam866460/LR.0002562890625，**67ee37cf39a9b82f7e45eab68f2fa0e46bd0eec95ffbe063bedfd7bfe810d81a**，14718611B。
- S135 actual20，原RSLlastloopiter32088/17Adam643380/LR.0003375，**ec5b495691e10bf4ef6587e7fad99df02a18ff48e44f6b70d5170aaa7b641b05**，17620922B。STD6真实saved[23.27964401245,.04192166403,.04260904714,.04961208627,.05852594227,.06277318299]。
- 原GO→parentterminal派生expertseconds1154.8189311027527+1209.8845801353455=2364.703511238098，非新账本；六条总原派生成本7122.772308111191。Curb标签差19仍20actualupdates，不回填。

第三批frozeneval root `.../MOD4V1_PAIR3_FROZEN_RETENTION_V1_20261102_144639_1793601999302137400`，parent1466371/worker1466380+1466381，14:47:53两ready共同控制；E3 160controls3.2s/S135750controls15s、交集43.11795425415039s，**14:50:47epoch1793602247.8156497 两RC0/allwait/privateGPU1EX+globalfiniteEXreleased/errors[]/stdout容量错误[]**。actualoneCPUcache/新STDstrict/allunknownrootidentity/no20kapplyslice/0PPO不变。
[真实Pair3 best](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR3_FROZEN_RETENTION_BEST_SELECTION_V1.json>)由source_assess_pair3_v1真实processor运行，job `pwsh-76ec76602d9a4b73`已收：
- E3 12requestedrecipe0..11初始74，normalrecipe12的6排除。firstepisode originalstable credit **0/74→1/74**（recipe1加1），普通bad_orientation/basecontact原事件**25→27**（18+7→19+8），closure/mimic0。sameRecipe分母与credit比有改善但ordinary非增规则未满足，因此**Mother1cd**，67ee新候选完整保留；不把1credit当毕业，50public100Hz=.5s/25controls，request3003s，不用delta泛指credit。
- S135自己原两轮endpoint/contact **上25/27→27/27**，下27/27站26/26无普通失败保持，ordinary/closure/mimic0，boundary16→8单列，**Candidateec5b**，旧f2b母本留。

所有第三批PPO/eval/metadata/report jobs已收：`pwsh-b2118f91c37b4353`、`pwsh-44ba92f1ca9c415a`、`pwsh-f70a2a4793e14174`、`pwsh-4f45b1dfb76e4dbb`、`pwsh-4a010f73e4334268`，别再当live/复跑权重或原raw。

## 当前实际live最后pair4 W35最新8d+S50，别重复启动

root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR4_GENERIC_V2_20261102_133324_1793597604238711100`
parent **1466964**；W35worker **1466977/GPU0**，S50worker **1466988/GPU1**。
**真实GO W35 1793602320.1817293（14:52:00.1817293+08），S50 1793602321.251975（14:52:01.251975）**；原两authorityEX3,4/privateEX5,6/finiteSH7、canonical原generation唯一owner1466964、actualfreshGPUhost/sourcehistoricalproof/2c-bae原native0PT/full20k证书绑定。
[实际首准入snapshot](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR4_GENERIC_V2_ACTUAL_FIRST_ADMISSION_SNAPSHOT.json>)：14:55:33两PIDlive/parenterrorNone/PREGOwaitNone/pending[]/blocked[]，remaining361229.5064468384；是加载/恢复阶段实际成本，不推PPO完成。W35source **8d6a9ab5...17620037/32643/654500/LR1.0000000000000004e-05**不是89aca，S50source4a5...17955663/32118/643980/LR3.3750000000000014e-05；whole20000/24steps/max20/save+3600/nominal3900/headroom300。

**唯一当前相关在跑背景job `pwsh-6938955d1f9d4b14`**，[generic PPO collector](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/collect_generic_training_pair_once.py>) --pair4，6000s/15s自身publishedmetadata，模型/raw/C/SDK0。完成`PAIR4_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json`和reports/PAIR4_GENERIC_V2_TRAIN_CLOSED_<stamp>/CLOSED_RESULT.json，先job_output，不重复PPO/collector。新W35V2 knownLIVE前置/原logger边界save/无raw或savediter/LRSTD算术覆写/fullrootunknown保/完整历史20000/ONEreset/原learn(True)保持；rawRSLlabel可能logical-1，实际producer原值不填+20。任何error/部分optstep留原证据/账不refund，不“0completed=0steps”。

## 接下来直接走最后冻结原scope与真实assess

pair4 actualfullPPOclosed后：
1. `summarize_generic_training_pair_closed_metadata_once.py --pair4`（metadata only，producerpin读真实savediter/LR/Adamminmax）。
2. `stage_dispatch_generic_pair_retention_once.py --pair4`，原W35 **80/32s1600controls**、S50 **80/20s1000controls**，原D0-D7/physics/skill原界/meanclip6/onewholeCPUcache不sliceapply、原EX/actualtwoFD/完整closewait。别误旧unused18s、别再eval当前6条。
3. `collect_generic_pair_retention_once.py --pair4`唯一watch，closed后运行已交source_assess_pair4_v1。

已交**Pair4 assessor SOURCE_READY**（还未实际执行/无fakebest）：
```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -S -B 'F:\RMPOLAR-RL\mod4v1_experts_fulldr_rm70_20261101\POSTTRAIN_EIGHT_EXCLUDING_H1_20261102\source_assess_pair4_v1\assess_pair4_retention_closed_metadata_v1.py'
```
23056B SHA2601ddab89f18583ba1b07bbc51bbd8a607b6d9d2d71432d6a28684ad83e89d1，20synthetic stdlib tests（非SDK）。读取未来真实closed+pair4training summary+旧compact+自己ROLEcontract+已publishedCPU汇总，Task/FINAL/stdout与collector bytesSHA/actualsource/原clock/RC0waitEX/newactorSTD identity等严格检查。默认x写reports/PAIR4_FROZEN_RETENTION_BEST_SELECTION_V1.json，不覆盖。

W35 oldbook publishedaggregate complete87/true44/false43，**不自行从44/87推moving**；旧18/61moving+26/26stand reference只读已published reports/NINE_V8_W35_OWN_NEW_ROWS_CPU_ONCE.json，元数据同group/producer SHA/schema绑定，不重读JSONL/NPZ。缺split/reference-phase/UID-population/predicate证据强标gap且Mother+candidate均留；split非退化也不伪硬件/技能卒业，goal0不是原训练targetfail。S50原acceptedfullramp完整cohort/predicategap：保Mother，ownaxis20s boundary/timeouts/ordinary事实单列，不借S135endpoint。

child **c3baa770-cbb7-4dc7-82b2-dc0f03f1dd52**当前只追加**可选极窄未来W35观测SOURCE**：read原rm70_intervals227.py与book.finish，若source确有moving/standing分类和原acceptedbool，可同writer原row写出时累加moving/stand count/true→finishpublishedmetadata，无reset/RNG/clock/action/reward/interval/predicate改，无原raw/模型读。先交assessor已完成，optional新unuseddiff/source+stdlibtests/provenance随后，**必须收到后父read确认字段/方法与实际stager软件hash再采用，仅未来pair4eval，不动currenttrain/oldV8/当前已消费源**；若无严格标签留gap/Mother，不造proxy。禁止source再读旧raw/JSONL/NPZ作表格，所有actoridentity来自actualTask/cache/producer，不把oldbook source-label当actualactor。Source_assess_pair3 child32已inactive。

4. 实际最后assess后`publish_assessed_posttrain_pairs_registry_once.py --through-pair 4`生成Registry_v12及8条results（只metadata）。必要补human摘要，显式八条训练/评测执行结果与scopedbest、回退和未解决技能/硬件资格分开；原mothers/失败候选/unknowns全部保。最后真实cost/locks/complete artifacts+归档remoteverified再Goal complete，不把未获完整接受判定称全通过。

## Git

**phase15已push+exactremote核验** commit **c03bc4a1b8781f01ef6168b0e07fa760d7f0a838**，trial `trial-20261102-mod4v1-four-train20-secondpair-best-pair3-go-phase15`，annotatedobj **b5c005860bb8ba203303c7b06a3abe45043ff7ca**，peeled同commit，12077entries12033texts，feature mod4v1-experts-fulldr-rm70。lastreadonlymain **f0705ed2366481a6c512449afa9a513a173980a1** 可独立进，不push/resetmain/不硬绑旧值。pushjob `pwsh-29acfd9ee2a74a48`已收，所有archivejobs已收。

**phase16待**：P3 actual20/完整闭合/summary/进度save20+17原回执/真实frozen147..+评估E3credit1却ordinary27保Mother/S13527候选/Registry_v11+六报告/最后pair4实际GO与admission、本v20、sourceassess3/4 final与W35optionalobservationpointtime。未来最后P4实际训练/冻结/全部结果appendphase17；不为Git重跑任何SDK/PPO/模型hash/raw/新账/已消费once。Goal仍active直到最后2条实证。
