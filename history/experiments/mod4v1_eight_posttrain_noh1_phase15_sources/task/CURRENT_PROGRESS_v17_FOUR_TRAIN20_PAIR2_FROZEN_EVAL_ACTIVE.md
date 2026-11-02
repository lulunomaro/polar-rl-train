# 最新v17：4/8各20真实PPO已闭合，首批保技能改善新best，第二批原scope已共同控制

在[v16](<CURRENT_PROGRESS_v16_FIRSTPAIR_BEST_PAIR2_GO_SIX_STAGED.md>)及其v15/v13背景上继续，不复跑旧window/once。Goal `goal-1348948b-8b3e-4e93-85ec-317e88962347` revision8 active/armed，上次roundsStarted2/max12；原八谱系exH1。**H1冻结，Goal未完成，不blocked**。物理/DR/原PPO/原singleC唯一writer/charge_values/完整state/原锁规范完全不变。两个4090授权，源模型/旧best/失败候选保留，N80能力不套20k训练。

## 已实际完成：E0/C878/E2/C113各20新原PPO

原完整actorcriticlearnedSTD17AdamLRiter/所有D0–D7RNGhistoryqueue/unknownroot恢复；ONEhelperreset→原learn(True)→完整atomic liveknown+oldunknown save→env/Appclose→父actualwait→原账expertseconds结算→原authorityEX/GPUprivateEX/finiteSH释放。四个worker均RC0、两个父closed无错误，没有新增账本/扩展/refund/clamp/未计尾段。

| Role | actual updates | actual saved iter | Adam17 unique | actual saved LR | candidate SHA |
|---|---:|---:|---:|---:|---|
| E0 |20|32004|641600|0.0002562890625000001|6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693|
| C878 |20|32959|660800|0.00007593750099961956|db3d5a6a2a81fb71f6f4e3ca0ee18c09785ddff80b990787960ffc3d8d376d68|
| E2 |20|42842|859700|0.00050625|68e1df12c95276a8be00e2b684589a54a4765b258f61f4e43184a13f7e9a12c7|
| C113 |20|32194|645500|0.00011390625000000006|04bc3a49a5e0f6e1c4aff8a7f85de171922a78e87e692673f345a8fe8a29d05a|

Curb原RSLlastlooplabel差19仍20actualupdates，不回填标签。E0/E2原nextnewlabel+1语义不同，实际计数独立，不只用iteration差推。C113 savedSTD6=[23.524396896362305,.05211487412452698,.05395934358239174,.06021666154265404,.07222707569599152,.07879020273685455]；E2 FINAL无STD6元数据，不为此另开PT/编旧STD，原eval唯一CPUcache严格加载新STD。第一pair成本2418.8572309专家秒；第二pairE21115.9538209438324+C1131223.2577450275421=2339.2115659713745专家秒（producerGO→父actualterminal派生，非新账）。

[首批训练汇总](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json>) · [第二批真实闭合汇总](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR2_GENERIC_V2_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json>) · [第二批全部closed producer](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR2_GENERIC_V2_TRAIN_CLOSED_20261102_133959/CLOSED_RESULT.json>)。

pair2原parent1462128/worker1462142+1462151 13:38:05/06GO，**13:58:30epoch1793599110.2106261 allclosewait/原costsettled/原leases释放/errors[]**。旧generic训练collector `pwsh-281df56546f740cd`已完成已收，别再收当live或重新启动PPO。summaryjob `pwsh-1b7ece6f4e5a4e10`也已收。

## 首批实际复评已保留改善新候选

[完整用户报告](<FIRST_PAIR_MOD4V1_POSTTRAIN_RETENTION_RESULTS_V1.md>) · [真实best](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_FROZEN_RETENTION_BEST_SELECTION_V1.json>) · [Registry_v9](<EXPERT_NORMALIZATION_REGISTRY_v9.json>)。
E0三轴body绝对平均误差.03950337/.04763822/.10586448→.03828474/.04751152/.10110792，普通/closure/mimic0；C878sameepisode两轮端点/接触上22/27→26/27，下27/27、站立26/26保持、普通失败0，路径boundary36→49单列。保守选择两个新候选、母本不覆；只单seed原fresh80scope，不是full20k/hardware/全技能毕业。原V3资源wait1800零SDK闭合，389owner13:30:21真释放后新V4原准入，真实控制重叠215.177s/两RC0/allEX释放，旧once未重用。

## 当前实际live：第二批候选原fresh80冻结评测

root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_PAIR2_FROZEN_RETENTION_V1_20261102_140451_1793599491951189200`
parent **1463738**，已source_schema crossvalidate并stage867nonPTfiles；只两当前完整新候选metadata，不复制旧源/PT。不改原2EX/privateGPU1+globalfinite、原reserve/CownerNone新读、原twoFD、policy50/feedback100/.0025TGS32,4、2c/bae/.01/.01/400-k2000-d3、原DR/clip6/技能界。

**14:06:30 epoch1793599590.119388 E2与C113两场景ready，共同控制已实际开始**，parent_errorFalse。
- E2原80/24s/**1200controls**，原signed2pi+worldbounds observer保持。world getterphase/referencegap仍在，不盲目优化疑点指标。
- C113原80/15s/**750controls**，原自有endpoint/contact/stand，不借878技能数据。
- newwhole20kCPUcache只完整身份保存/actorstrict载入，原20kDRhistory不apply/slice到80，不建livecriticoptimizer/0evalPPO；每个新评测目的只一byte/hash/decode。源pinLR/iter/Adam由真实FINAL producer而非旧083b/b3基线。

**唯一当前相关live背景job `pwsh-0082f8e223d74247`**，[collector](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/collect_generic_pair_retention_once.py>) --pair2，4500s15s自身publishedmetadata，phase变化才打印，不触model/raw/C/SDK，不重复启动。完成输出`reports/PAIR2_FROZEN_RETENTION_V1_CLOSED_<stamp>/CLOSED_RESULT.json`及`PAIR2_FROZEN_RETENTION_V1_LATEST_CLOSED_RESULT_PATH.json`，先job_output。

[Generic metadata与supervisor源](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_eval_generic_pair_v1/FINAL_GENERIC_TWO_MEMBER_EVAL_SOURCE_INDEX_V1.json>)已77stdlib正负/28两成员组合；supervisor从plan.eval_members精确len2/unique/subset八非H1、角色/ready集合完全一致，原2EX/资源/wait1800/closewait逐字不改。正式系无假STD6，E1各自实际liveCore4值替换，旧RNG/rootcore搬historical。此源部分晚于phase14pointtime，下一phase再归档全字节；不宣其MOCK是新SDKproof。

## 下一步判定与后4角色

子agent **32baa298-9c0c-4efb-b8ee-1cef9f2cbd3d**当前短SOURCE-only在写**pair2 best评估processor**：参考firstpair源码但数据驱动E2+C113，读未来实际closed FINAL/原已收baseline metadata/closedstdout，不SSH/PT/raw/SDK/C/Git、不实际发布假best。必须sourceCache指当前候选/原seedcounts/两RC0allwaitEX释放。E2报告body3诊断与complete/false/true/incomplete原signed2pi，knownworldgap明确不是全skillpass；保守bodyPareto非更差+普通失败不增+原acceptedtrue不降（基线0/187强标gap）选择Candidate，否则保持Mother；C113原上/下完整与contact、stand不退化才选，E1Final无top num_envs用原group总和80。任何选择都保存母本+候选、不是原新毕业阈值。输出予定`reports/PAIR2_FROZEN_RETENTION_BEST_SELECTION_V1.json`，retention_assessment_complete/H1_excluded/rows selection与do_not_overwrite字段给nextdispatcher用。**等childfinal收到确切命令/sha、真实evalclosed后才执行**，不要编passed让nextbatchGO。

然后[原nextdispatcher](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/dispatch_staged_training_pair_after_retention_once.py>) --pair3 --prior-assessment <真实pair2bestJSON>，原parentfreshCownerNone/reserve/授权两卡查+实际4FD与unique writer/原charge_values。nextPPO窗仍每条max20而非继续第一pair。

- pair3 **E3+S135** root `.../MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR3_GENERIC_V2_20261102_131153_1793596313729480700`，453+433nonPTfiles，原verify_sources通过，**未owner/未GO/未训练**。
- pair4 **W35最新8d+S50** root `.../MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR4_GENERIC_V2_20261102_133324_1793597604238711100`，511+446nonPTfiles+actual8d常量/dedicatedindex与historicalproof绑定通过，**未owner/未GO/未训练**。source_w35_v2三关键修复logger保存/无iter算术写/先live后union与fieldjoin已封，取九白名单，不覆旧source或原parent生命周期。W35自然rawlabel可能-1不回填。S50原完整技能接受谓词gap仍记录，不套S135。

通用评测stager [stage_dispatch_generic_pair_retention_once](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/stage_dispatch_generic_pair_retention_once.py>) --pair2/3/4，必须各自实际training closed后才能运行；model metadata由pure builder读取实际PPO FINAL，基线controls从成功V8保持W35 1600/32s（不是unused18s），软件clone实际V8runtime，子actor只新purpose一次cache。已消费pair2 marker别重用。

## Git已归档与待phase15

**phase14已push+remote exact核验**：commit **c60be1ae6c343e7323294bdcbcc2d77a96f9a799**，trial `trial-20261102-mod4v1-firstpair-keep-skills-pair2-live-phase14`，annotatedobj **5aba1f6a87bd63528f596ec757dc03af32a6f1ea**，peeled同commit；11929sourceentries/11887textfiles，feature mod4v1-experts-fulldr-rm70 clean。pushjob `pwsh-df376ca9c97a4ec8`已收终末；readonlymain当前 **f0705ed2366481a6c512449afa9a513a173980a1** 可独立推进，未push/resetmain，不硬绑旧main。

phase14覆盖首批真实复评改善+Registry_v9、V3waitclosed→389真释放watch→V4准入、data-driven所有六源码/runtime/preflight、旧native2/3pt键erratum、W35v2 source三错修+真实whole20k历史closedjoin、pair2真实GO/加载snapshot/v16。**后来pair2实际20closed/summary、通用eval最后source与metadata/stager/运行/结果/本v17待phase15append**。不为Git重跑PPO/打开PT/raw/改旧once或新账。Goal保持active，剩四角色训练与后续原scope评测完前不完成。
