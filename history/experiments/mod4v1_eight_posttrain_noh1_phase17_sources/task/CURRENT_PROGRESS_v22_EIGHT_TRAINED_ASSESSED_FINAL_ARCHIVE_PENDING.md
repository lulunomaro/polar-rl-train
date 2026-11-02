# 最新v22：本轮8条后训练与8条原scope评估实证全完成，最终归档后关闭Goal

继承[v21](<CURRENT_PROGRESS_v21_LASTPAIR_TRUE_PPO_FUTURE_SPLIT_SEALED.md>)。Goal id `goal-1348948b-8b3e-4e93-85ec-317e88962347` revision8 active/armed（last rounds2/max12），**数据objective已实现本轮有限20/专家+保守best+原scope评价；尚待phase17最终Gitpushremote验真后get_goal→complete**。H1始终冻结，未改其原Registry字段，不训练/覆盖。不是全部技能或真实硬件毕业。

## 最终文件已生成且metadata完整性通过

- [最终中文报告](<MOD4V1_EIGHT_EXPERTS_POSTTRAIN_FINAL_V1.md>)：8角色scope表、训练/评测与毕业分开、改善/回退、原物理与DR、所有缺项。
- [Registry_v12](<EXPERT_NORMALIZATION_REGISTRY_v12.json>)：原Registry_v8除schema外字段（包括H1与原selected_formals）逐项完全相同；追加8条posttrain/fullsave/frozen/best。
- [全部候选与保留源目录](<MOD4V1_EIGHT_POSTTRAIN_CHECKPOINT_CATALOG_V1.json>)：8条新completecheckpoint原producer path/bytes/SHA/iter/17Adam/LR +当前scopedbest、候选/母本双保。
- [完整metadata核验](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/EIGHT_POSTTRAIN_FINAL_METADATA_INTEGRITY_V1.json>)：8窗口各**actual20**、总160专家更新、8原scopefreeze、训练8RC0+评测8RC0、全部SDK/Appclose/父actualwait/原leases释放/原成本结算、独立17Adam+400交叉核验、sourceH1unchanged/8candidate+8mother保留、0报告模型/raw/SDK/C写/重跑。
- [原canonical最后最小只读回执](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/EIGHT_POSTTRAIN_ORIGINAL_FINAL_BUDGET_READONLY_RECEIPT_V1.json>)：15:32:21epoch1793604741.118854，原generation MOD4_SINGLE_WRITER72_20261026，charged1908983.6888906956+remaining359016.3111093044=**2268000.0原总额不变**，reserve86412.86069250107；activeNone、四个原owner segments均completed。只最小metadata读不是新账本/复制ledger/no C写。无需重复读预算/模型。

四对原PPO20/whole20000/24steps/allactorcriticSTD17AdamLRiter+D0-D7/RNG/historyqueue+unknownroot保持，原onehelperreset/learn(True)/2c-bae/400-k2000-d3/50-100Hz/.0025TGS32,4/.01m-.01rad/原rewardskill界，原两authorityEX+各privateGPU EX+finiteSH/唯一C/charge_values全生命周期含加载尾段无refund/扩预算。本轮原GO→父terminal派生**9760.750821590424专家秒**（非墙钟，约2.7113专家小时）。N80只是原scopefresh独立cohort，整20kCPUcache不apply/slice历史、原meanclip6、criticoptimizer不live/0evalPPO，Source只该目的onebyte/hash/decode，不为状态/Git再开PT/raw。

## 八角色最终scope选择（模型都保，不宣全毕业）

| Role | 新PPO | 新savediter/Adam | 本次scope事实 | 选择 |
|---|---:|---|---|---|
| E0 |20|32004/641600|vx/vy/yaw abs误差全改善、普通/closure/mimic0|Candidate6cdac1e4...|
| C878 |20|32959/660800|上22/27→26/27，下27/27站26/26|Candidatedb3d5a6a...|
| C113 |20|32194/645500|上22/27下27/27站26/26保持普通0|Candidate04bc3a49...|
| S135 |20|32088/643380|上25/27→27/27下27/27站26/26普通0|Candidateec5b4956...|
| E2 |20|42842/859700|vx/yaw改善但vy+.00005794m/s，world0/187既有gap|Motherb3...，Candidate68e1...保留|
| E3 |20|43110/866460|firstepisodecredit0/74→1/74，ordinary25→27|Mother1cd...，Candidate67ee...保留|
| W35 |20|32662/654900|原moving18/61→18/64，stand26/26，分母/参考系/UIDpopulation gap|Mother8d...，Candidatec435...保留|
| S50 |20|32137/644380|原ownaxis20s普通0，boundary41→46/timeout47→43；fullacceptedgap|Mother4a5...，Candidate34ee...保留|

E3 normalrecipe12六个排除初始rescue74/12recipe，不用delta或跨reset credit；stable50public100Hz=.5s。W35goal0不是原trainedtargetfail，无.04cap/x8改。S50不借S135endpoint。母本与新candidate各8全部保，原selected_formals冻结不改、onlyscopedbest新4+母4，不拿执行RC0冒技能通过。Curb/W35原lastlooplabel差19仍actual20，原savediter实值不回填。

## 最后pair4真闭合与全部observability

lasttrainroot `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR4_GENERIC_V2_20261102_133324_1793597604238711100`，原parent1466964/workerW351466977+S501466988，14:52:00/01GO，**15:14:30epoch1793603670.4363 两RC0/allwait/原costsettled/原leasesreleased/errors[]**。
- W35 actual20完整**c4357c2c70bb044e7c0360e34cacf728721c9ec331fe57484250da1c516b750a**17621715B/rawiter32662/17Adam654900/LR.00017085937500000006。自然lastlooplabel，不强填32663；input8d/32643/654500/LR1e-5/priorcum162，原cachetruth/knownLIVEbeforeunion/loggercounter后save/noiterLRSTDwrites/unknownroot保。真native24与full20krestore marker旧带V3名字不是错源。
- S50actual20完整**34ee25ddd2d8de2d5068115a35a7265801b44a7e38cc29a8c9ca91c7b34c2a42**17962257B/rawiter32137/17Adam644380/LR.00011390625000000003。两成本1289.6591539382935+1348.3193595409393=2637.978513479233expertseconds。
- 旧PPOcollector `pwsh-6938955d1f9d4b14`已完成已收；stager `pwsh-f617c8800bda4073`、training summary `pwsh-10a5827048a24fb2`已收。

lasteval root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_PAIR4_FROZEN_RETENTION_V1_20261102_151501_1793603701481560300`，parent1468292/workerW351468301+S501468302，source928nonPTfiles，真实原2EX/80/seed20260928，15:16:18epoch1793603778.2536113两readycommonstart，W35原32s1600controls+S50原20s1000controls；**15:23:08epoch1793604188.9410195两RC0/allwait/privateGPU1EX+globalfiniteEXreleased/errors[]/stdoutcapacity[]，0C写/父PTSDK0**。collector `pwsh-368670521e9440d6`已收，不重跑。

W35原row同writer追加split已真实生效：旧complete87/true44/false43→新complete90/true44/false46，moving原18/61→新18/64，standing26/26同。新metadata直接原standing/complete/accepted bool计数，不改predicate/reset/RNG/clock/action/reward，原close/其它方法AST、原每row字典/顺序/sha不改，分组计数和等原events；未读原raw/JSONL/NPZ，不把split当新毕业资格。原匹配UID/参考相位/root-vsCOM/worldgetter/acceptedcohort gap仍在，Mother。Futureoverlay的三源SHA b914.../edfdd.../d33ec...已sealed写worker_files与OBSERVATION_ONLY_OVERLAY_PROVENANCE，原V8/消费pair2/3/所有train根不改。

## 最后assessor兼容性修复记录（都是CPU metadata，没有物理失败/重跑）

封版source_assess_pair4_v1（SHA2601...）期待uppercaseTASK、topDRpass/topbarrier字段，与原实际task.json/nested actual_parameters/barrier_start envelope不符。父先v2只修小写Task与commonmetadataaliases（selected_source/candidate_preserved、actualRC由闭合行导出），比较/selection5函数AST完全相同；sourceonly负fixture deepcopy保留共享mother-selected对象引用导致反例改两者，testv2失败并保erratum，v3 fixture仅换selecteddict，6synthetic过，assessor本体不改。

actualmetadata v2（job `pwsh-56d439bdc8224840`）KeyError actual_parameters_pass，v3修到原fresh_fullDR_x.actual_parameters.actual_parameters_pass且fresh_N80_D0_D7_enabled真；actualv3（job `pwsh-16dce0522de94cfd`）KeyError all_members_ready，v4修到原wait_group_start返回group_barrier.barrier_start，并额外严格group_id/GPU/members/allready/noextraactorphysicsRNG证据。原compare_w35/compare_s50/split/scanstdout/aliases AST不变，所有旧源/失败全保。**actualv4 job `pwsh-57eff4e41af84db0`成功**，source_assess_pair4_v4/assess_pair4_retention_closed_metadata_v4.py 25790B SHA829e590b1a7b98f931d20d414a1f9d6f9427fd1ebcc983889a48467e844c2c46，唯一x输出真实PAIR4_FROZEN_RETENTION_BEST_SELECTION_V1.json（Mother两条），未有fakebest/新SDK目的。

[最终metadata核验](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/EIGHT_POSTTRAIN_FINAL_METADATA_INTEGRITY_V1.json>)及最终reportpublisher `pwsh-413cd5519dfa4a7a`、`pwsh-cde58b354440449b`、budgetread `pwsh-b6f6f1e73897455e`都已完成已收。**当前无仍相关在跑shelljob/子agent，c3/32均inactive。不要再自动训练/评测。** 唯一待工作是最终归档/验remote/Goal完成与present。

## 最终phase17与Goal收尾

phase16已push+exactremote：**2fe0a3b1f247c612e42d6067540704e523c4571a** /trial-20261102-mod4v1-six-train20-thirdpair-best-lastpair-go-phase16 /annobj **8ad10b8612c9da21c6a1165c36bb9de68fec790a** /12207entries12162texts。main lastreadonly412d5d5dcc12d725502849c0dc109367c61452bc可独立推进，不push/reset或绑旧main。

**phase17待**：lasttrain20/full20krestore/native24/complete+20summary/真实frozenRNGidentity+W35samewriter新分拆+原limits/所有sourceassessorV1–V4字段错误和fixture失败/metadata真实修复/最终Mother两条/Registry_v12/8过程表/最终报告/完整checkpoint目录/metadataIntegrity/原finalBudgetReceipt/v21-v22。使用原record_experiment/exactdirstagedadapter+唯一annotatedtrialfeatureonly，模型和原raw只producerpath/bytesSHA，不能为Git重开原模型/轨迹/SDK或任何物理重跑，不复制ledger或改预算。

Git最终remote feature/tagobject/peeled/currentreadonlymain验真完→get_goal并complete本轮eightposttrain/frozenassessmentobjective；若push网络失败只处理Git对象/不重做record或物理。然后present最终报告/Registry12/目录（最多3卡），最终聊天清楚：8×20和8原scope完成，4newbest/4mother；H1冻结；技能缺项仍在。不是“所有技能全通过”，也不是追加不限PPO。
