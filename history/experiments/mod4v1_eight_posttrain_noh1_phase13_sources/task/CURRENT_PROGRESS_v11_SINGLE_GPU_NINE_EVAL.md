# 当前优先任务：单GPU并行评测9个归一化专家（2026-11-02 09:40前后）

承接[进度v10](<CURRENT_PROGRESS_v10.md>)与既有[Registryv7](<EXPERT_NORMALIZATION_REGISTRY_v7.json>)：9条可取得谱系新MOD4v1完整20k恢复/native24已经实际PASS≠新版完整技能毕业；W35两窗口162PPO/7776万转换/最新8d32643Adam654500真LR1.0000000000000004e-05，独立20k32秒高速8948段met0/noCADgoal，均已原closed+CPU一次校验。原7b CURB141 source端timeout尚无字节不可用878代替。

## 用户新增直接要求与Goal

用户问归一化用BPTT还是PPO，已真实答：迁移多数不训练，只有W35原PPO162更新，没用BPTT；尚无新版完整技能确认。随后用户明确 **“跑一下通过后专家的评测，所有专家并行跑起来在一张卡给我结果”**，再问何时、最后 **“$stop-that-shit change 继续任务”**。

当前按公开说明 **9×80 fresh fullDR技能筛查/总720环境，同一张GPU1 4090**。没有切片或投影原20k保存历史；整checkpoint缓存1次保所有root/权重STD/critic/17Adam/LR/iter，但本N80只live actor+STD、criticAdam仅CPU缓存不新造runner，fresh80各自原factory/DR recipes/seeds/ONEreset，新plant2c/bae+400N2000d3/50Hzpolicy100Hzfeedback/.0025/TGS32,4/.01closure/.01mimic，源Full20k协议证据独立引用。单父持原GPUprivateEX+globalfiniteEX，9独立headlessSDK/不同HOME/Kit/Warp，共同Ready/Start屏障后才step。无PPO/BPTT/GO/预算写/第三GPU/清锁/杀其他任务。

Goal `goal-1348948b-8b3e-4e93-85ec-317e88962347` **revision6 active/armed**，roundsStarted1/max12，09:24 get_goal确认。此前r4paused+模型resume工具返回“model cannotresume”，父没绕过另造Goal；后来用户明确继续，host已重臂active r6。目标内容已编辑为当前单卡9评测。

## 最新实际运行：V4部署刚发，尚无技能结果，下一步收stage job再开唯一collector

- **V4阶段job `pwsh-be3c3a56232c41ac` 刚start，未收output**：运行[单卡V4派发器](<stage_and_dispatch_nine_single_gpu_eval_v4_once.py>)。先本地实际4E1 Task crossvalidator+FDstub/envUUID验证，再nonPTstage4021runtimefiles+精确workerfiles，原selectedPT路径仅传metadata不copy/read，启动新总parent。
- V4 source根[运行源码V4](<NINE_N80_PARALLEL_SOURCE_V4/>)，worker物理/actor/metric代码与V3逐字同；仅总parent加**最多1800秒原资源有界等待**，每15秒重新尝试原两个EX，任一busy释放全部partials/closeFD、无SDK/model/GO/账写/foreign actions，原CPUloopwait不是重复实验。真正admit后worker绝对截止2400秒；9场景ready barrier900s。
- V4未来locator **[一次派发回执V4](<NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V4.json>)**（stagejob成功才存在，不要先读不存在就重新派发）。将写newroot `MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V4_<stamp>` /parentpid。
- stage完成后只执行一次 **[V4闭合collector](<collect_nine_single_gpu_v4_until_closed_once.py>)**；local consumed marker `NINE_GROUP_V4_COLLECTOR_CONSUMED.json`、远端小JSON每15s bounded4500s、仅phase变化打印，无driver/PT/NPZ/技能raw/SDK/账读取。最终收originalparentexit及9wait，copy9闭合stdout原bytes+SHA及FINAL/ERROR/Ready/Task/Start/PreClose，输出`reports/NINE_SINGLE_GPU_V4_CLOSED_<stamp>/CLOSED_RESULT.json`与`reports/NINE_SINGLE_GPU_V4_LATEST_CLOSED_RESULT_PATH.json`。
- **不要自动复用V1–V3 once/root**。目前前三组全zero skill window；没有任何本轮专家技能成功/失败可以报，只能报实际启动/准入错误。结果要区别未运行/执行错/原谓词成功/原接受scope缺失。

## V1–V3实际错误与关闭证明（全部保，phase10待归档）

### V1：09:06:39–41 metadata缺键，全9zeroReady/start/physics

root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_20261102_090632_1793581592519074100` parent1442799。实际取GPU1privateEX/globalEX/empty24203/canonicalNone，不账写；9worker同秒created（1442809/10/13/16/19/24/30/35/42）。4E1 `validate_group_task`早期 **KeyError:'seed'**，父Task producer漏seed/optimupdates/clock/DRscope/physicscounts字段，未入App/PT；5父worker被scope取消-15，不是SDK失败，PT在SIGTERM前unknown不冒0；all9wait/2locks released wall2.47s，原stdout/metadata完整在[状态回执](<reports/NINE_SINGLE_GPU_STATUS_20261102_090951.json>)与远端。

- V1 OrderedDict另一个SOURCE proofgap被child发现：`cache._freeze(type(x)isdict)`未深核dict子类OrderedDict，落opaque identity；不意味着真实mutation，V1 liveactor strict9tensor加载+前后逐tensor仍有，cachedoptimizer若普通dict依然强，不泛称全部弱。因V1zero skill，不需为标签重跑物理。
- 子新4E1 **[运行sourceV2](<E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V2/>)**改isinstance字典递归与same immutableNaN，60stdlibMOCK含OrderedDict变异负例passed，未读PT/SDK。[V2交接](<E1_N80_PARALLEL_FOUR_WORKERS_SOURCE_CORRECTION_HANDOFF_V2.json>) SHAf8b98449…/indexb9131138…。13runtime文件含ROLE_CONTRACTS，别stage原V1缓存。

### V2：09:14:11–17原Kit owner guard，全9zeroReady/start/physics

root `MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V2_20261102_091404_1793582044937064000` parent1443104。
[stage metadata](<reports/NINE_SINGLE_GPU_GROUP_STAGE_20261102_091404_1793582044937064000.json>)，4实际生成Task已纯stdlib跨端validator passed，9SDK worker同卡spawn。4父E0/E2/E3/W35在AppLauncher `_create_app` 原guard **storage!=job/'kit_isolation'** ValueError（父job root为runtime_root，storage却case sibling，纯调度隔离路径错，不是physic/skill失败）。5其他scope取消；all9wait/locks全释。**本地已全收**[V2闭合结果](<reports/NINE_SINGLE_GPU_V2_CLOSED_20261102_091553/CLOSED_RESULT.json>)及9stdout原byte/sha/ERROR。源cacheCPU ctor在runpy前完成，4报错liveTrace说明已到actorcache之后，但没receipt，不把SDK模型读0；zero actor-step确定。

V2新父源还修前版directenv.step漏原RSL clip6（V1 zeroStep未有行为偏差）：现实际meanraw6→clamp(-6,6)→env.step，与原RslRlVec wrapper同；记录maxraw/maxapplied。Task生产已抽纯stdlibmake_task（source/supervisor共享），每次stage真实4Task对 `e1_group_scope.validate_group_task`+FDstub/envUUID通过才SSH，不仅模板MOCK。

### V3：09:32:18原锁busy，0child/0SDK/PT/Ready/start/physics

root `MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V3_20261102_093212_1793583132536330700` parent1444592，stage完试originalEX时 **BlockingIOError11 resource unavailable**，没有开始任何worker。allOwnwait(empty)/已释放partials，No foreign action/账写。已收[闭合结果](<reports/NINE_SINGLE_GPU_V3_CLOSED_20261102_093404/CLOSED_RESULT.json>)，stagejob `pwsh-f954f1c865964baa`与collector `pwsh-91054362c87d47fb`都done/collected。

09:36:49一次真实只读exactinode锁占用与两卡snapshot：[原锁回执](<reports/NINE_EVAL_EXACT_LOCK_HOLDER_20261102_093649.json>)，three_expert private0/1+finite lock当前holders[]，两卡24203MiB/0%、canonicalNone/remaining372380.98902630806、generation原值，未干扰。故前次busy已是历史瞬时，不宣现在仍占用；V4必须自fresh原EX+process+mem核而非依此快照，busy才等待1800s，不改锁模式/清锁。

## V3已完成的具体源码修复/干跑，V4保留不变

[生成器](<prepare_nine_v3_launcher_bound_sources.py>) 真实纯stdlib执行原launcher类（isaaclab.app仅Stub，不importSDK）：9positive +4原错误sibling路径负例复现，全部PASS，见[原路径契约proof](<NINE_N80_PARALLEL_SOURCE_V3/PARENT_FIVE_SOURCE_INDEX_V4.json>)。父5Kit现 **runtime_root/kit_isolation**；E1 child本来case==jobRoot、kit case/kit_isolation自洽不改。

实际部署源从V2自身runtime只source收集[launcher origin](<diagnostics/NINE_V3_EXACT_LAUNCHER_SOURCES/INDEX.json>)：
- E0/E2/E3原launcher检查`MOD4V1_E*_KIT_STORAGE_ROOT == MOD4V1_E*_JOB_ROOT/'kit_isolation'`。
- W35 `MOD4_W35_OWN_KIT_STORAGE_ROOT == MOD4_NEW208_JOB_ROOT/'kit_isolation'`；copy1034B SHA99aa2f29…。
- H1 actualtrainer `train_H1_ground_prelaunch_fullstate_v2.py` SHA086a48…在line49导入`zonglin2_app_launcher.Zonglin2AppLauncher`（不是launcher*.py所以首collector没列），精确B/lib复制391B SHA9178b2…。[H1原source](<diagnostics/NINE_V3_EXACT_LAUNCHER_SOURCES/H1_normal/lib/zonglin2_app_launcher.py>)仅disablecrash+renderer，无portableRoot guard；本9parent已经每case独有HOME/XDG/TMP/CUDA/WARP cache，因此别声称H1有未实现portableRoot guard。

另两处具体observer修复已在未消费V3源完成，V4同：
1. **E3 firststablecredit用 `env.recovery.credited & first_episode_live`**，不是delta>0（delta包含普通upright进度，不能冒0.5s稳定事件）。阈值仍stable50public100Hz=.5s/25policycontrols、request300age3s，normalrecipe12非rescue，同initialepisode不resetstitch。
2. **W35 originalIntervals227 book.install在既有ONE env.reset前**、reset后arm，保存原first-resample packet/tick0，避免把fresh首12–16s leftcensor。无新增reset/resample/RNGcalls，原actorreward/commands/rootstate不改。E2 Cycles213 sameUID/sign/episode/worlddir/2pi/.5±.05/cross±.05/yaw±.2/no term-timeout原代码，MODEL constant b3和source相符。

## Sole子已完成，不要另开agent

子 `32baa298-9c0c-4efb-b8ee-1cef9f2cbd3d` done/inactive；若需要仅send_message续。无PT/stat模型/hash/decode/SDK/SSH/GPU/canonical/PPO/parent改动，所有source任务review已seal：
- W35三代failure机制[handoff](<W35_THREE_GENERATIONS_MECHANISM_SOURCE_ONLY_HANDOFF_V1.json>) SHA15f04068…/46text34refs50func14mothers。原signedBODY ±.3/.2standing/12–16s；reset偶左5.85 yaw0/奇右9.15 yawpi/wholecoursex5.5–9.5/y5.4050–7.4959外端仅.35m余量，catalog goal opposite3.3m是observer不是命令/奖励目标，目标非等价；goal0不独证执行器失败。boundary25520/time14749可重叠union40256，16route样本不泛全体，不能臆断卡地形。初1s highcmd7samplebodyvx.247方向正，不证明全程也不支持固定.04软件cap。
- W35最小18s/900control/N20k futureobserver-onlyspec未执行。实际getter同根linkCOM/cachephase/自然heading与xyzw/wxyz同帧数值是明确gap；Python累积dP/(n*.02)+8ticks无明显8倍错，不×8补旧量。当前优先9N80评测，不自动另开W35诊断/PPO。
- E1四源码V2+[完整Task/证明scope说明](<E1_PARALLEL_V1_PROOF_SCOPE_ERRATUM_AND_V2_TASK_CONTRACT_V1.json>) SHAde877c06…；runtime来源delta[原stage白名单](<E1_FOUR_WORKERS_REMOTE_NONPT_ORIGIN_DELTA_V1.json>) SHA67a7cb20…/1.33MB/4roles873/879/443/867nonPTmetadata；**native/fresh父root才runtime，/gpu1是结果层**，不要再错层。
- 父五workerSOURCE API审查[最终索引](<NINE_FIVE_WORKER_V2_SOURCE_API_REVIEW_V1/FINAL_FIVE_SOURCE_API_REVIEW_INDEX_V1.json>) SHA3afe171…，31精确textRefs，所有构造/guard/getter/H1true270400Hzgoal/E2Cycle/actorA0/6clip/8phys2feedback已对原source/已实际fresh80probe，不能推ABI全面pass。
- [D4形状源证据](<NINE_FIVE_WORKER_V2_SOURCE_API_REVIEW_V1/FOUR_E1_D4_ACTIVE_SOURCE_SHAPES_CONFIRMATION_V1.json>) SHAfa73a1…：active四role queue/adapter原SHA逐字同；legs4targets与wheels2targets coherent各一组lag，pending80x4/80x2，lag_steps每组(80,)合法原source分配/reset/statevalidate证明，不是每DOF独立lag，不要扩缩物理数组。
- CRCRLF本地sourcecarrier artifact保错：父source collector remoteCRLF decode后Windows write_text又加CR，localmod4_task108499B SHA2e803…/1896CRCRLF，内存CRCRLF→CRLF106603B恰安装30ce411…ASTpass。只reader修，原carrier/receipt不改、不说运行源坏，后续sourcecopy都write_bytes。

## 各role本轮评测与接收范围

Parent5 worker [当前源码](<NINE_N80_PARALLEL_SOURCE_V4/worker_five_original_n80.py>)：E0 20s1000ctrl，E2 24s1200ctrl原Cycles213，E3 3.2s160ctrl13recipes，H1normal20s1000ctrl（20仅原cfg default、无原已接受cohort/horizon，不冒完整验收），W35新8d32s1600ctrl原sameUID intervals/routes并分站/动/高速，不把generic training1.0当技能。

Child4 [sourceV2](<E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V2/>)：CURB_PROTECTED878/ind113/SLOPE135各15s750ctrl，原80cohort27up27down26stand/40+40orient、原contact-confirmed同episodeordered两轮端点/1N；Slope135仅5°2maccepted scope。SLOPE_INDEPENDENT50 20s1000ctrlowntrainingaxis自然command描述，原accepted80cohort/predicateGAP不借135毕业。原a92/b3/1cd frozen但full_skill_accepted=false，其他scope也勿泛化。

模型源均existingremote路径与CPU/native元数据绑定无新迁移/retype。W35选8d最新不是2d/89aca，真LR1.0000000000000004e-05；H1typed71db /source453 true270不是BPTTstudent。源17Adam/cachedcritic字段保完整；本80livecritic不construct、无optimizerstep。旧20kcuda16byteRNG/history retainedincache未施到80，禁止切片后宣fullrestore。

## 归档/待办

Git phase9已完成推送remote核：feature commit **83df839ecbde65355e5c1e13e22d551db64befdf**，trial `trial-20261102-mod4v1-new8dfull32-sourcecontracts-phase9` tagobjcb79bf02…peeled83df，10537sourceentries/10530texts，main只读27ee661e…。已保存[remote核验](<reports/GIT_PHASE9_REMOTE_VERIFICATION.json>)，main没push。

**Phase10 pending**：phase9receipt/当前v11、late W35source mechanism/E2scope contracts、E1fourV1/V2所有source+MOCK/OrderedDict/正误scope/API review/activeSDKsourceorigin+stale direct_url与preApp backend findSpec错误、单卡V1seed/V2Kit/V3resourcebusy全部原错误stdout以及将来V4真实输出。按repo AGENTS/policy record_experiment+exactdirectoryadapter stagedset避Win206；大PT/USD/NPZ/新旧skillraw/canonical仅路径bytesSHAmetadata，不再读模型或旧raw归档，不为归档重放试验。只feature+uniqueannotatedtag，不pushmain。

Todo当前：资源/9worker实现done或等待actual；真正单卡并行启动、收完整结果、archive并给用户逐专家表尚未完成。用户已被告知早次ETA20–30m需要顺延：前两次zeroSkill，第三次原锁busy不是专家失败；没有保证当前已有有效成绩。**下一步先收pwsh-be3c3a56232c41ac，取得V4实际parent后launch一次V4collector并监控；不可把dispatch当all9开始，更不可填旧24step结果。**
