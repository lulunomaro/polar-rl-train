# 新Goal r8：除H1外八专家后训练；首批E0+CURB878原两卡已准入

## 直接用户新任务与Goal

用户最新：**“现在你的任务是专家归一化后的mod4v1最新的其他专家进行后训练，除了h1，其他专家尽量保持技能通过，切换goal”**。
原goal id `goal-1348948b-8b3e-4e93-85ec-317e88962347` 已 `update_goal edit` 为 **revision8 active/armed**，roundsStarted2/max12。不要另建goal，不完成本后训练Goal直到8专家都有实际保存与复评证据。H1冻结排除；范围E0/E2/E3/W35(W25)/Curb878/Curb113/S135/S50。沿原PPO完整actor/critic/STD/17Adam/LR/iter及D0-D7/history/RNG/queue，原20k，不是N80actor-only；不引BPTT/不改奖励/solver/动作/技能界，保持2c/bae新asset和批准时钟/门槛。

[八专家intent](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/POSTTRAIN_INTENT_V1.json>)已钉八最新冻结完整source，第一window计划最多20实际新PPOupdates、parent3900/save3600/headroom300，时间/预算提前停实际少于20实记；不覆母本，完整新候选保存后按原skill冻结复评，退化不推广并保留best。H1无new训练/模型操作。原CURB141 exact7b缺源仍独立，不用878替换。

## 已完成旧单卡评测（非当前后训练完成）

[最终报告](<NINE_SINGLE_GPU_SKILL_RESULTS_V1.md>)、[机器汇总](<reports/SINGLE_GPU_NINE_FINAL_SUMMARY_V1.json>)、[Registry_v8](<EXPERT_NORMALIZATION_REGISTRY_v8.json>)：V8单GPU9x80均RC0/allwait/EX释放，真正9控制窗交集139.439s，10:16:10–10:32:08；E0 bodyvxMAE.0395/yaw.1059普通跌倒0；E2原worldsigned2pi联合0/187（getter相位/参考点gap保留，别盲按有疑点指标训）；E3初始74跌倒 stablecredited0/74+normal6不计；H1launched42/80 landed/success0；Curb878和113均up22/27 down27/27 stand无普通失败26/26；S1355°2m up25/27 down27/27 stand26/26；S50完整原接受谓词仍缺，只training-axis诊断；W35moving18/61 stand26/26、routegoal0/228为observer非trained目标，尚未RM70毕业。
W35新N80raw171547B543行/schema13125B实际各一次CPU/SHA核对，[报告](<reports/NINE_V8_W35_OWN_NEW_ROWS_CPU_ONCE.json>)已出，别重读raw。固定.30bin0不是整个高速人口，不声明0/0pass。旧20kfull32高速0/8948是独立旧cohort，不拿来填新N80、不×8。各原全20k完整恢复/native24证据此前已actual，与fresh80分开。

## 当前唯一实际运行首批（别重复启动）

[PAIR1 V4派发回执](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/PAIR1_V4_STAGE_DISPATCH_RESULT.json>)；root：
`/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_POSTTRAIN_EIGHT_NOH1_PAIR1_V4_20261102_120158_1793592118216803700`

- Originalparent **1457086**，E0worker **1457100** / GPU0 `GPU-16828f91-2b45-b646-8dc0-9481138e2842`。
- CURB878worker **1457109** / GPU1 `GPU-c27eecbd-6838-7290-1cd2-37e34522213d`。
- 真实GO epoch1793592135.4534883 /1793592136.5230076（约12:02:15/16），各num_env20000、24steps/update、max20；saveDeadline1793595735/36（13:02:15/16）和nominalend1793596035/36（13:07:15/16）。原parent持b.LOCKS双EX +两GPUprivateEX +原finiteSH，只一个原C writer/charge_values，按两个expertseconds计包括load/learn/save/Appclose/wait，无refund/clamp/新ledger。
- [12:06实际准入快照](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/reports/PAIR1_V4_ADMISSION_STATUS_20261102_120602.json>)：没有PREGO wait/parenterror，两个身份与GO均存在，Cremaining371928.301235199（比初始372380.989少452.68779，正是两专家加载约226.5s×2），不是只派发。**尚未取得首次update/livefullrestore回执，不把GO当已训练。**两worker在完整加载/SDK流程中。
- 唯一相关运行后台job **`pwsh-2c6dbaae45e648cd`**，[bounded唯一collector](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/collect_pair1_v4_until_closed_once.py>)。它每15s看本组publishedmetadata，phase变化才打印；4500s上限，不读模型/raw/SDK/GPU/C。源restore标记：E0 production/LIVE_WHOLE20K_FULLRESTORE_BEFORE_PPO.json；E1 production/POSTTRAIN_FULL20K_FULLSTATE_BEFORE_LEARN.json；最终各production/FINAL.json。E1没latest_complete.json不等于没保存（完整指针在FINAL.new_fullstate_checkpoint等）。收终末后一次copy已闭合stdout/JSON，输出`POSTTRAIN_EIGHT.../reports/PAIR1_V4_CLOSED_<stamp>/CLOSED_RESULT.json`与`PAIR1_V4_LATEST_CLOSED_RESULT_PATH.json`。
- 其余6未消费后训练：E2/E3/W35/Curb113/S135/S50。首批保存/关闭/原wait/结算释放→冻结按原scope复评→继续新pair/新once；别在现持finiteSH时硬挤globalEX评测，不干扰当前训练。

## 最新只读资源/原账本（不是准入替代）

[只读快照](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/READONLY_ORIGINAL_RESOURCES_20261102_V1.json>)（约11:12）：两4090各24203MiBfree/0%、compute空，RAM532GB；C original path `/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json`，authority_generation MOD4_SINGLE_WRITER72_20261026，authorized2268000，charged1895619.010973692，remaining372380.98902630806，strictreserve86412.86069250107，activeNone。原新window只能fresh锁准入后writer；**现已由pair1写账，别拿旧activeNone覆盖。**
已从真实部署旧W35source root readonly取回[原预算helper及实际资产证据index](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/parent_source/original_budget_and_asset_refs/INDEX.json>)：three_slot_common_v1.py2444B SHAeaf6aa...，authority_source4547B SHAceba80...；Native0PT22378B fb62...、targetSDK11598B073c...、geometryreuse660B23e...。没复制C/没PT/SDK动作。b.charge_values支持多keys，固定总2268000，用原函数不自己做新账。

## Source交付与实际stager

- [E0/E2/E3最小bundle](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/RUNTIME_MINIMAL_DEPLOY_BUNDLE_SOURCE_INDEX_V1.json>)、[完整handoff](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e0_e2_e3/FINAL_SOURCE_HANDOFF_INDEX_V1.json>)，sourcecommonSHAfa76348f...41989B，三wrapper/descriptor；pure `construct_source_task_go_v1.py::build_task_go(...)` 构造完整dict，别手填漏seed。kind沿原role.kind，posttrain_kind三role统一SOURCE_V1；admit用ROOT_MOD4V1_EIGHT_POSTTRAIN_ACTUAL_ADMISSION_V1，实际父PID/原C/源/资产/时间/哈希绑定。原rescue_training.learn/install保True init、最多20alg.update返回实际计数+optimizer.step计数，save读真实iter/17Adam/LR，只断言不回填。原native24不额外重放。cache source.load是copy.deepcopy整root，避免CPUstep alias；八组stdlibAST/MOCK通过，不冒实际SDK。
- [四E1最终source](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e1/FINAL_FOUR_E1_POSTTRAIN_SOURCE_INDEX_V1.json>) SHA2429d...；runtime_bundle3文件085cef.../327791.../fe93b4...。116stdlib checks通过，47requiredfields；pure e1_posttrain_make_task.make_task可在父actualROOT/GO dict之后validate，输入actual4fds/UUIDenv。child不实现Budgethook，不read/write C。source native root与proof/source pin/CLI/结算[map](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e1/PARENT_RUNTIME_CLONE_MAP_V1.json>)、[补充](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_e1/POST_SEAL_PARENT_CLONE_MAP_SUPPLEMENT_V1.json>)。E1Cache也对每logical load deepcopy整个truth，不需再新增alias修复；unknownroot merge以原truth与currentliveknownleaf并保存。源dependency静态图不作全SDKclosure；full originalruntime clone，勿裁剪/套80capacity。E1FINAL `completed_actual_updates`、`new_fullstate_checkpoint.checkpoint`、`all_complete_checkpoints`；实际filename用FINAL指针，不猜U020。异常0complete不代表0optimizerstep，错误boundarysave/17Adam实记。
- [W35新8d posttrain20源](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_w35/W35_POSTTRAIN_SOURCE_DESCRIPTOR_V1.json>)已生成（AST only，未stage/启动）：原workerV4派生，仅source换latest8d17620037B/32643/654500/LR1.0000000000000004e-05/priorcumulative162；最大20，完整helper/ONEreset/原native24暖起（原W35worker流程）/原PPO保留，保存union源unknownroot/currentliveleaf。独立newprotocol不hotpatch旧模块，后续须把其新Derivation/manifest/Ready历史proof结合实际父admission，**还没接实际parentPlan/stage**。actual8dGPUrestore3571B证书 [FULLRESTORE227](<staged_sources/W35_NEW8D_GPU_FULLRESTORE_CERTIFICATE_V1/FULLRESTORE227_BEFORE_CONTROL.json>) SHAeb7818...来自旧full32，非N80；不重开PT只为新证书。
- 父[八范围通用原owner源码](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/parent_source/eight_posttrain_original_owner_v1.py>)，实际pair1已快照到remote，后面任何修改必须新source/newjob。支持未消费subset1..8、两个原UUIDslots、singleCowner+原charge_values、fullclosewait末端结算；family0completed错误不重放未修源，不以0complete当0partialstep。STOP路径E0生产目录/STOP_AFTER_SAVE.json，E1task.rescue_stop_file由父指定root，plan e.stop_relative区分。b.charge_values末端行保持所有已GO keys，terminal再计dt0，不refund。Cactive只在全部自身child实际wait后清并release原EX/SH。
- 实际stager[stage_dispatch_pair1_v4](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/stage_dispatch_pair1_v4_e0_curb878_once.py>)只clone各实际full20k母根的runtime/lib/original_field/new_assets和原immutable root metadata、源代码；不copy任何checkpoint/log/oldTaskGO/once/缓存。E0要sealed overlay根DIFF+DERV；E1用自己的canonical元数据，不强造不存在DERV。每role显式stageexact2c/bae到Task.asset_dir=runtime/assets。保必要runtime bank NPZ/NPY，不是旧telemetry；软件manifest不是权重拷贝。Rootcase新增helper/fullWorker，不改旧sealed源。

## 本后训练phase的真实失败（均在SOURCE stage，未parent/模型/SDK/GO/C）

PAIR1 V1 root115553...：native clone根未带完整E0sealed DIFF/DERV，加上对E1无需要的DERV blanketassert；源stage line13失败，零modelSDKbudget，保[原错误](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/PAIR1_STAGE_V1_DEPENDENCY_ONLY_ERROR.json>)。
V2 root115856...：Curb原资产在owner-root assets，新Task统一runtime/assets而未显式copy，FileNotFound；[原错误](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/PAIR1_STAGE_V2_ASSET_LAYOUT_ERROR.json>)。
V3 root前manifest扫描：已copy必要runtime-bank NPZ/NPY，却沿旧assert禁止NPZ，source stage line23失败；[原错误](<POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/PAIR1_STAGE_V3_STATIC_ASSET_FILTER_ERROR.json>)。
V4修正合法源bank资产过滤并显式pin新asset，487+458 nonPTfiles实际stage通过，之后真实parent1457086实际准入，两worker如上在跑；不把V1-V3叫训练失败或更新/退化，不重用旧once。

## Git与未完工作

旧eval/source全archive phase10 **aafe69f5eb8644d6ed5d6ace0d33f9b929d01e4c**，trial-20261102-mod4v1-single-gpu-nine-n80-eval-phase10，annobjacf96ef2...，11366entries/11339texts。phase11补充**d2bf76d09b11130a28a4abde179f6733675ecc28** annobjcc346176... 两远端tag/peeled与feature均actual核验。首verifier错把旧main27ee当固定值已[补充更正](<../repo-lqr/history/experiments/mod4v1_phase10_remote_ref_supplement/NOTE.md>)；main被独立其他任务推进，最新readonly4b571616...，本任务从未pushmain，不覆盖/回退它。以后只核main真实readonly快照不硬固定旧值。
**本后训练Goal r8的新source/intent/resources/PAIR1V1-V4失败/当前实际运行receipt尚待phase12 Git归档**。用已原record_experiment+exactdiradapter/stagedset，不为Git重跑GPU或开PT/raw；大件只producerpath/bytesSHA。训练不中断，归档pointtime；在跑/未生成终末的报告明记pending下一phase。

下一步：1.collect唯一job结果/phase；2.首个真实fullrestore/save0/newupdate与错误严格分列，别从GO宣PPO完成；3.全部原save/Appclose/wait/成本结算/锁释放后用真实新checkpoint冻结原skillcase；4.与当前V8声明条件/DRcohort核对再保best，E2/W35观测gap不盲调奖励；5.继续其他6新pair/newonce，W35接新8d source而非旧89aca；6.全部后训练源/失败及晚报告Git。两个子agents32baa298…/c3baa770…现均source交付完成inactive，无实际PT/SSH/SDK/GPU/Git操作。
