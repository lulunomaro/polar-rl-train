# 最新v19：四条各20与原scope评估已完成，E2保母本，第三批实际GO

承接[v18](<CURRENT_PROGRESS_v18_PAIR2_EVAL_CLOSED_ASSESS_SOURCE_PENDING.md>)、[v17](<CURRENT_PROGRESS_v17_FOUR_TRAIN20_PAIR2_FROZEN_EVAL_ACTIVE.md>)，本页覆盖second-assessor pending及pair3尚未派发状态。Goal `goal-1348948b-8b3e-4e93-85ec-317e88962347` revision8 active/armed（rounds2/max12 lastread），不新建/complete/blocked，H1始终冻结排除。

## 实际完成4/8各20 +原scope冻结评估，三个新best一个保母本

[四专家报告](<FOUR_EXPERTS_MOD4V1_POSTTRAIN_RESULTS_V1.md>) · [Registry_v10](<EXPERT_NORMALIZATION_REGISTRY_v10.json>) · [第二批实际best](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR2_FROZEN_RETENTION_BEST_SELECTION_V1.json>)。

- E0：新候选6cdac1e4...iter32004/17Adam641600/LR.0002562890625，原fresh80诊断vx/vy/yaw全降、普通fail/closure/mimic0，选Candidate。
- C878：新候选db3d5a6a...iter32959/17Adam660800/LR7.59375009996e-05，原上22/27→26/27、下27/27站26/26保持，选Candidate。
- E2：新候选68e1df12...iter42842/17Adam859700/LR.00050625，24s1200controls原scope两RC0/EXreleased，bodyvx .04551603938→.04418453622/yaw .11879300680→.11113409602改善，vy .07317019432→.07322813410微增**.00005793977m/s**。按既定三诊断Pareto非更差+普通fail非增+原acceptedtrue非降保守规则，**FROZEN_MOTHER b3ae94...**，新candidate完整保留；不冒统计显著退化。原complete187/false187/true0/incomplete43→44，已知world getterphase/referencegap明确保，0/187不毕业/不盲调。观察器producer仍旧b3SHA标签是谱系，不是actualactor；actor/cache确实68e1，不改写旧记录/不读JSONL修标签。
- C113：新候选04bc3a49...iter32194/17Adam645500/LR.00011390625000000006，原sameepisode两轮endpoint/contact上22/27、下27/27、stand26/26保持，ordinary/closure/mimic0，boundary34→46单列；选Candidate，旧083b母本留。

四PPO各20真实计数/full20k/fullstate/原learn(True)/onehelperreset/原D0-D7/RNG/historyqueues/unknownroot/learnedSTD17AdamLRiter/400-k2000-d3/.0025TGS32,4/50-100Hz/.01m/.01rad完全保留。四RC0/完整atomic保存/原envAppclose/父actualwait/原leases释放/原singleC charge_values成本结算；错误[]；原GO至父terminal派生成本合计**4758.068796873093专家秒**，非新账本/refund/扩预算，完整20k保存不slice。Curb原lastloop标签差19仍actual20，不填造+1。

二批真实eval14:06:30共同开始、14:11:18closed、实际控制交集215.0590374469757s，0PPO/整20kCPUcache不apply/slice到80/criticopt不live，各候选purpose一次byte/hash/decode，closedstdout容量错误[]。四条单seedfresh80scope，不宣full20k总体/硬件/全技能毕业；原selected_formals冻结源不改，Registry仅附scopedbest。

assessorjob `pwsh-d58730f5b0814d40`、报告/Registryjob `pwsh-88357565b3b14d31`已完成已收。旧second evalcollector `pwsh-0082f8e223d74247`亦已收，别再当live/re-eval或读旧raw。

## 第三批当前actual原双卡GO，别重复派发

root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR3_GENERIC_V2_20261102_131153_1793596313729480700`

首次launcher `pwsh-7cfd6397febe4f74`在fresh card gate失败，**未Popen/未GO/PT/SDK/C写**，并不是新训练失败。14:22:57只读snapshot：CownerNone/remaining364018.99313402176/reserve86412.86069250107，卡0free24203util0，卡1另compute1464722占3394MiB，private/finite文件由项目PID1464714打开（fuser只引用不独立证明锁模式）。不kill/清锁/共享卡、不改门槛。随后新launcher只启动**原unchanged parent自己的1800s preGO wait**，所有原EX/SH/gpu/host/budget仍必须实际满足。

实际parent **1465093**，E3worker **1465108** /GPU0，S135worker **1465117** /GPU1。
**原GO** E3 **1793600742.590924（14:25:42.590924+08）**；S135 **1793600743.7008855（14:25:43.7008855）**。
[真实首准入snapshot](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR3_GENERIC_V2_ACTUAL_FIRST_ADMISSION_SNAPSHOT.json>)：原两authorityEX fd3,4、私卡EX fd5/6、finiteSH fd7、actualroot/resource/当前C唯一writer绑定1465093、源E3 1cd.../S135 f2b...都真实，num_env20000/24steps/max20、save+3600/nominal+3900/headroom300。14:31:09ownerCurrent两PIDlive/parenterrorNone/preGOwaitNone/pending[]/blockedfamilies[]，remaining363366.78670310974；这是加载/恢复的实际成本，不从消耗猜PPO完成数。sourcePPO fullrestore/更新/完整新save以自己producer为准。

**唯一当前相关在跑背景job `pwsh-b2118f91c37b4353`**，[generic PPO collector](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/collect_generic_training_pair_once.py>) --pair3；6000s/15s只publishedmetadata/phase变化stdout，0models/raw/C/SDK，完成pointer`PAIR3_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json`。先job_output，不启动第二watch/PPO。parentdispatchjob `pwsh-b73b6f989aa94f9b`、只读diagnose `pwsh-a3447d1b87aa475f`、admissionsnapshot `pwsh-d51a77fcfffc4094`已全部收终末。

## 下一步与两SOURCE children

1. 收pair3 actualfinitefullPPO/save/closewait/costsettled/原锁释放，运行`summarize_generic_training_pair_closed_metadata_once.py --pair3`（只meta），然后`stage_dispatch_generic_pair_retention_once.py --pair3`+`collect_generic_pair_retention_once.py --pair3`。原E3 80/3.2s160controls，S13580/15s750controls，原DR/physics/seed/predicates无改，无重评当前四条。
2. child **32baa298-9c0c-4efb-b8ee-1cef9f2cbd3d** 当前 SOURCE_ONLY 写 source_assess_pair3_v1（无actualprocessor/SSH/PT/raw/SDK/C/Git）：E3 V8真实有**13recipe行，0–11为12rescue初始74；12是normal6 original_requestFalse排除**，credited=`recovery.credited & first_episode_live`，stable50public100Hz=.5s/25policycontrols/request300=3s。同recipe初始分母相同、每recipecredit不降+普通term不增；双方credit都0无改善证据选Mother，gap明列不造毕业。S135从自己baseline25/27up、27/27down、stand26/26与ROLEcontract取。真实closedassessment完成就可nextbatch，退化选Mother不假PASS。等其final命令/hash，未来真实evalclosed后父才执行，输出PAIR3_FROZEN_RETENTION_BEST_SELECTION_V1.json给nextdispatcher --pair4。
3. child **c3baa770-cbb7-4dc7-82b2-dc0f03f1dd52** 当前 SOURCE_ONLY 写 source_assess_pair4_v1。W35 FINAL book原publishedaggregate只complete87/true44/false43，compact原未拆moving61/true18与stand26/true26；既有published reports/NINE_V8_W35_OWN_NEW_ROWS_CPU_ONCE.json可作旧reference，不读旧JSONL/NPZ。若future新FINAL仍不publishsplit，则MOVING_STANDING_DENOMINATORS_UNPUBLISHED+reference/cohortgap，默认Mother且candidate留；不从44/87伪推moving，不拿goal0作新fail。S50原fullrampacceptedcohort/predicate缺项，保Mother+新artifact并报20s ownaxisboundary/timeouts/ordinary，无借S135endpoint。
4. 给c3一个**可选极窄新观测SOURCE补丁**：未来W35尚未实际eval，若原writer row确有existingmoving/standing分类与原acceptedbool，可以在**原row写出同一时刻**累加moving/standing分组count/true并finish发布metadata；不改谓词/interval界/reset/RNG/动作/reward/时钟/技能，不再读任何raw/模型。只有源中严格有标签才做，否则留gap/Mother，先交assessor，新增unusedsource/最小diff，原V8不动。父采用前read审查与记录确切字段；当前四条/未来pair3不重评。W35worldgetterphase/root-vsCOM/referencegap仍保，不用.04cap或×8修补。别把观测补齐当物理或技能通过。

## 第四批W35+S50未训练

root `.../MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR4_GENERIC_V2_20261102_133324_1793597604238711100`，511+446非PT源码/runtime/metadata已stage、原verify_sources+8dconstants/dedicatedindex/proof绑定预检passed，**无owner/GO/PT/SDK/PPO**。必须在真实pair3评估完成后nextdispatcher --pair4（fresh资源变了尊重原actualgate）。source_w35_v2九白名单/8d17620037/32643/654500/LR1.0000000000000004e-05/priorcum162，logger边界save、无iter/LR/STD覆写、先knownLIVE后union、原unknownroot/nested保；自然rawlabel差1如实，无第21。原parent/预算/锁不改。别用旧source_w35或旧89aca母本当latest。

## Git待phase15，phase14已remoteverified

已push **c60be1ae6c343e7323294bdcbcc2d77a96f9a799** /trial-20261102-mod4v1-firstpair-keep-skills-pair2-live-phase14 /annobj **5aba1f6a87bd63528f596ec757dc03af32a6f1ea** /11929entries11887texts，feature mod4v1-experts-fulldr-rm70。main lastreadonly **f0705ed2366481a6c512449afa9a513a173980a1** 可独立推进，没push/reset它，不硬绑历史值。

**phase15待**：pair2实际20closed/summary/冻结新scope/sourcegeneric77tests/实际E2保母本+C113新candidate/sourceassessor22tests/Registry_v10+四专家报告、pair3首次preParentGPUbusy/sourceerror/实际originalwaitdispatch→双卡GO/准入snapshot、本v17-v19、新childSOURCEpointtime。晚pair3训练/评测/第四批输出appendphase16，所有失败/unknown都保。不为Git读PT/raw/replaySDK或改旧once/新ledger。Goal仍active直到剩四真实后训练+原scopefreeze有证据。
