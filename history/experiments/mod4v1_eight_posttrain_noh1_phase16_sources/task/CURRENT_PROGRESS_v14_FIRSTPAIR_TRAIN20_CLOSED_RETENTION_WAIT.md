# Goal r8仍active：首批两专家真实PPO各20完成，复评在原锁等待

用户新请求仍为除H1外8专家MOD4v1后训练、尽量保原技能。Goal id `goal-1348948b-8b3e-4e93-85ec-317e88962347` revision8 active/armed（原2/max12rounds），不要新goal/不markcomplete。其余背景/冻结8源/原C/DR/物理/先前N80评测见[v13](<CURRENT_PROGRESS_v13_EIGHT_POSTTRAIN_NOH1_PAIR1_ACTIVE.md>)。H1从未进新PPO/候选操作；其余6尚无新window：E2/E3/W35/Curb113/S135/S50。所有母本/旧best保留。第一窗最多20不是技能通过，后面仍须原scope复评、回退/保best，再推进新未消费pair。

## 真实首批已完整闭合，不重启

训练root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR1_V4_20261102_120158_1793592118216803700`，原parent1457086/E0worker1457100/Curb878worker1457109。双4090、每role20000env/24steps、原PPO/STD可学习不手冻、全actorcritic17Adam/LR/iter/D0-D7/history/queue/RNG/unknownroot恢复→ONE原reset→原learn(True)→atomic完整save。原C唯一writer原charge_values，实际load/learn/save/envclose/Appclose/parentwait expertseconds计到终末；无新ledger/refund/extensions。**12:23:29+08** allwait、原private/finite/authority leases全释放，原costsettled/errors[]，两个RC0，别再用先前v13“仍在训练”状态。

[Closed全部producer回执](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_V4_CLOSED_20261102_120320/CLOSED_RESULT.json>)和同目录roles原FINAL/wait/stdout。唯一旧训练collectorjob `pwsh-2c6dbaae45e648cd`已完成/已读输出，不再watch或复用once。

| Role | 实际新updates | optimizer事实 | saved iteration | saved LR | 完整新候选 |
|---|---:|---|---:|---:|---|
| E0 |20|400实际stepcalls；17Adam都641600；960万transitions|32004|0.0002562890625000001|root/roles/E0/production/model_final_complete.pt；14035411B SHA6cdac1e4b84df407d41a38444b87eaa91309ed898af05fe95a6c80f6ac3fd693|
| CURB878 |20|17Adam都660800；自然学习STD6（25.630088806/0.0496428013/0.0518412031/0.0569962598/0.0673355162/0.0727365389）|32959|0.00007593750099961956|root/roles/CURB_PROTECTED878/production/model_posttrain_final_complete_U020.pt；17621306B SHAdb3d5a6a2a81fb71f6f4e3ca0ee18c09785ddff80b990787960ffc3d8d376d68|

Curb原runner last-loop label从32940跑20次保存32959，**iteration差19不等于19updates**，不回填成32960，不从标签推造PPO次数；真实completed_actual_updates20与optimizer17实值/FINAL为准。E0沿原nextnewupdatelabel+1约定真实20到32004。E0 sourcecache仍physical byteopen1/decode1，fullRAMtruth allroots unchanged；unknownroot/source字段全部保留，liveknownleaf获胜。两checkpoint暂属新完整候选，技能未获通过，不覆盖best。SDK Appclose有桥接sys.exit0路径，E0 APP_CLOSED.json缺失不反推失败，以ENVclose+parentwaitRC0为准。

已汇总器[assemble_pair1_summary](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/assemble_pair1_actual_training_closed_summary_v1.py>)，job `pwsh-93fe64ada9bd4c1b`待收结果（若已完成先job_output），目标[汇总JSON](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_ACTUAL_FULLSTATE_TRAINING_CLOSED_SUMMARY_V1.json>)；只处理已收producer metadata，不开PT/raw/复跑。成本用各GO开始至实际parentterminal timestamps派生，非复制账本。

## 冻结新候选复评已派发，**尚在资源等待，无新候选PT/SDK打开**

- root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_PAIR1_POSTTRAIN_RETENTION_N80_V3_20261102_123301_1793593981516967400`，parent **1458948**。12:33:06派发；单GPU1原privateEX+globalfiniteEX，原C只读activeNone/remaining>reserve，没有PPO/GO/新writer。
- [派发报告](<reports/PAIR1_POSTTRAIN_RETENTION_GROUP_STAGE_20261102_123301_1793593981516967400.json>)、[once](<PAIR1_POSTTRAIN_RETENTION_GROUP_DISPATCH_ONCE_V3.json>)。已stage905nonPTfiles，新candidate path/bytesSHA/真实iter/17Adam/LR绑定；不复用旧49f/源计数。
- [实际准入状态](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_RETENTION_V3_ADMISSION_STATUS.json>)：PARENT_STARTED存在，**BOUNDED_ORIGINAL_RESOURCE_WAIT reason Errno11**，partial locks0、SDK_or_selected_model_openedFalse、canonicalwrites0；ACTUAL_GROUP_ADMISSION/CHILDREN/barrier均未生成。只说原锁忙，不猜是谁、哪张卡在跑，不清锁/kill foreign。每15s原boundedwait，最多1800s（约13:03），期间sourcecache未创建不是候选失败。若等待耗尽先收原error/exit，别重复Model读取或复用once；资源条件变了才新目的/新root重试。
- 唯一相关**在跑背景collector `pwsh-48098626586548ec`**，[collect_pair1_retention_v3_once](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/collect_pair1_retention_v3_once.py>)；每15s只看publishedmetadata，4500s上限，phase变化打印；完成收caseJSON/stdout不读模型/raw，生成`POSTTRAIN.../reports/PAIR1_RETENTION_V3_CLOSED_<stamp>/CLOSED_RESULT.json`与`PAIR1_RETENTION_V3_LATEST_CLOSED_RESULT_PATH.json`。先job_output，不启动第二collector/SDK。新相关job只有这个与待收summary；其他stage/archive/diagnosisjobs都已收终末。
- 准入后原fresh80factory，E0 20s/1000controls与Curb15s/750controls并行，seed20260928/原D0-D7/物理/Fz/两轮端点/原技能谓词不变，整20kstate只CPUcache保留、不apply/slice到80；严格actor+learnedSTD加载，critic/optimizer/oldhistory不上env。历史baseline同V8 E0bodyvxMAE.03950337/yaw.10586448/noordinaryfall；Curbup22/27down27/27stand26/26。接actualFINAL事实后比较，不把40updates称技能pass，不猜全局E0毕业阈值。

## 新unused复评源与纯metadata（不碰旧V8）

[SourceV3](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/PAIR1_RETENTION_EVAL_SOURCE_V3/>)由成功V8新copy，只有：supervisor精确两role/children/ready集合、task.eval_members=['E0','CURB_PROTECTED878']、E0 parallel_eval_safe wait_start硬9→精确task成员；不改物理/actor/观测/技能。原task inheritedfds恰2（evalEX+privateEX），不要塞训练4fds。E1barrier本无硬9保持。

Curb新ROLE_CONTRACTS.source与activecore四值（iter/LR/17Adam/STD6）来自实际FINAL producer，不复用旧RNGhash/原rootkey声称候选事实；旧contract整体移historicalbaseline。E0原cache不要求预先STD6，保持从同次全candidate CPUcache严格核newSTD，不为统一formatter编造旧STD，也不为metadata单独重读PT。[纯producer/兼容map/15stdlibchecks](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e1/pair1_candidate_eval_source_v1/FINAL_PAIR1_CANDIDATE_EVAL_SOURCE_INDEX_V1.json>)，child仅SOURCE已inactive，无任何PT/SSH/SDK/GPU/Git动作。

复评V1/V2为**本地源码构造失败**，没有实际Eval模型/SDK/进程/锁/C动作；V1硬字符串锚点没匹配原source1space，V2换精确line后新插入2space导致ASTunexpectedindent，V3保持原main1space/forbody2space后AST+staging通过。旧partialsource/pins目录保，错误[锚点](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_RETENTION_V1_SOURCE_ANCHOR_ERROR.json>)/[缩进](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_RETENTION_V2_SOURCE_INDENT_ERROR.json>)。它们不是物理回放失败，不重用旧once。

## 后6未消费Source与后续顺序

已生成但**未执行/未stage/未dispatch**：[pair2 E2+Curb113](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/stage_dispatch_pair2_v1_e2_curb113_once.py>)、[pair3 E3+S135](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/stage_dispatch_pair3_v1_e3_slope135_once.py>)。它们由pair1已实际成功V4source派生，更新各原full20k mother/proof/schema/pin，实跑前先检查Role source_family仍为e0_e2_e3、proof Collection.new_nominal_guard字段存在、S135原handoff schema未必与Curb完全相同（Source尚未做实际metadata执行，不宣可直接PPO）。严禁复跑已完成E0/Curb20窗来“测试脚本”。

W35新8d有限20worker/protocol已[源码生成](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_w35/W35_POSTTRAIN_SOURCE_DESCRIPTOR_V1.json>)，尚未接parentPlan/stage/新derivation/manifest/Ready历史证据，不能直接拿旧89aca母源。source8d/17620037/32643/654500/LR1.0000000000000004e-05/priorcum162已钉，完整旧原restore/save/one reset/PPO保持，未知root保存合并。原CURB141 exact7b缺源仍独立条件，不用878替代。

下一步：先收复评资源wait/actualFINAL/closed/zeroPPO/cachecalls，真实同scope技能比较保best/回退候选；然后仅未消费6角色新pair/新once/原singlewriter budget/finiteSH训练。若源bug/半update失败保错和上个complete，0completed不能当0optimizerstep或refund。H1仍排除。至少阶段结果与任务总完成分开，Goal保持active。

## Git已推与待phase13

phase12 **6d04141cb75c83220c60033c7e56b4f8174e507a** 已originalrecord_experiment+unique annotatedtrial `trial-20261102-mod4v1-eight-posttrain-noh1-firstpair-phase12`；annobj **5d5eafba36df03e226fd2a4c78ffc8258512bbfc** peeled6d04141c，feature remote exact实际核验。11561sourceentries/11530textfiles，statusclean；main只读仍4b571616ef945c14c12578e87cb205bffe4d898f，没pushmain（它可独立推进，不硬绑旧值）。phase12是pointtime firstGO/source/packagingfailedV1-V3+firstlivefullrestore/startupsave，不包含后来20actual及复评源/错/等待报告。

**phase13待归档**：本v14、20updates×2 terminal回执/summary、latecount9报告、sourcepair2/3/复评producer与V1-V3源码/两个sourceerrors/V3真实dispatch与锁wait/后续actualskill结果。用原archive脚本/stagedset不重跑任何物理/CPUraw/开PT只为Git；大型PT/NPZ只原producerpath/bytesSHA索引，运行collector晚生成终末留后续appendphase。
