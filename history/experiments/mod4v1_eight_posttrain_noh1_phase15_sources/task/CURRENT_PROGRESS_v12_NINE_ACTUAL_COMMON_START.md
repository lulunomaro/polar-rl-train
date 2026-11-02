# 最新：9×80 同一4090实际共同启动，等待当前V8全部终末（10:23后）

承接[详细进度v11](<CURRENT_PROGRESS_v11_SINGLE_GPU_NINE_EVAL.md>)，**当前任务尚未完成，别重跑V8或另开新组**。Goal原id r6 active/armed、round1/12，9条全20k恢复/native24旧proof独立，本轮是新N80fresh-fullDR技能筛查而非20k历史切片。

## 当前唯一仍相关后台job

**`pwsh-b34fd6abd754440d`**：运行[唯一V8闭合collector](<collect_nine_single_gpu_v8_until_closed_once.py>)，已在后台读小published JSON每15秒，phase变化才打印；wait最大4500秒，不读模型/技能raw/NPZ/driver/SDK/canonical；闭合后会copy9stdout全部原byte+SHA/FINAL/ERROR/Ready/Task/PreClose，写`reports/NINE_SINGLE_GPU_V8_CLOSED_<stamp>/CLOSED_RESULT.json`和`reports/NINE_SINGLE_GPU_V8_LATEST_CLOSED_RESULT_PATH.json`。consumed marker已写，不再起第二collector。

实际root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_NINE_N80_SINGLE_GPU_PARALLEL_V8_20261102_101426_1793585666425343700`，parent **1451767**，GPU1 **GPU-c27eecbd-6838-7290-1cd2-37e34522213d**，[派发回执](<NINE_SINGLE_GPU_GROUP_DISPATCH_ONCE_V8.json>)。真实原GPUprivateEX+globalfiniteEX/emptycard/host/canonical准入。source root[当前V8父源](<NINE_N80_PARALLEL_SOURCE_V8/>)，child[当前E1运行源](<E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/>)。

### 真实共同屏障已过（不是单纯dispatch）

Collector真实记录 **epoch1793585770.866674 = 2026-11-02 10:16:10+08** `GROUP_EVAL_START.json`，九个names全员Ready、all_members_ready=true，**9SDKscenes/liveA0actors+STD/每80fresh-fullDR已真实就绪/0控制步**；统一放行进入评测。用户已被告知这条真实进展，未再报猜测ETA。

[10:23一次实际进度快照](<reports/NINE_V8_ACTUAL_PROGRESS_20261102_102304.json>)：E3已FINAL+PRE_CLOSE、160controls/3.2s/1280physics/320feedback、passed_execution true，start1793585770.9030588/end1793585910.3809946（墙时139.48s）；E0/E2/H1/W35还没FINAL/error。**E1四个started文件缺失不等于没step**：child原wait_group_start不写WORKER_EVAL_STARTED.json，放行后实际 `_run_loop`将wall_start_epoch及group_barrier入FINAL；最终必须以它的FINAL+originalwait证明开始和完成，不能用父5专用marker给E1误判未启动。终末分析另列actual_started_evidence并保原collector布尔不覆盖。

当前模拟在单卡并发，3.2s E3墙时139s，不用“32秒仿真=32秒墙时”估计。最久W351600controls32s，绝对worker截止是在准入后2400秒（约10:55），当前其余有用计算仍在进行，不额外kill/retry/开PPO/BPTT/新GPU。全9要等原各Appclose+parentwait+两个原EX释放再汇总。核心缓存全root/未知字段/STD/critic17AdamLRiter前后保持；原20k histories/RNG只是保在CPU cache，不live施到80、不slice；各worker本新目的byte/hash/decode各1。只有actual_live_actor_loaded后STDflag才True（早V4literal已勘误）。

## v11以后实际纠错（均独立unused once/root，旧source/错误不覆盖）

所有V1–V7 **共同技能窗口均未启动，零controlledsteps，不是九专家技能failed**。它们的Task/ERROR/stdout/manifest/关闭回执均落盘，phase10待Git。

- **V4** root `...V4_20261102_093945_1793583585913070900` parent1444848，原资源准入成功、H1 Ready；E0/E2/E3/W35 ONEreset在原asset-bank compat helper读`MOD4V1_ASSET_DIFF.json`时FileNotFound。原stager白名单漏immutable rootDIFF，不是physics/model错误。all9原wait/release，见[闭合V4](<reports/NINE_SINGLE_GPU_V4_CLOSED_20261102_094314/CLOSED_RESULT.json>)与[错误完整末段](<reports/NINE_V4_ERROR_TAILS_PROCESSED_ONLY.json>)。实际4sourcecache各1+wholeidentity passed。其`live_actor_STD_strict=True`当时是receipt literal，failed4尚未actor构造，已[appendonly勘误](<reports/NINE_V4_SOURCE_CACHE_LIVE_STD_LITERAL_ERRATUM.json>)，不改旧回执/不为标签重跑。
- **V5**补DIFF原字节到runtime root及case owner，先验证new2c/bae+changed3body+geometryunchanged再SDK，不改helperguard；父5全Ready。S50在SimContext初始化Warp root_link_pose TimestampedBuffer 2240bytes末次申请失败，stdoutL31–50连续 **Warp CUDA error2 out ofmemory**，不是只差2240byte。all9scopeabort/zero controlled/allwait/EXreleased；[V5闭合](<reports/NINE_SINGLE_GPU_V5_CLOSED_20261102_095308/CLOSED_RESULT.json>)。
- **V6**allocation-only：所有9保持80env、原actor/DR/几何/积分/.0025/TGS32,4/50Hz100Hz/10mmclosure/10mradmimic；父5/S135/S50显式采用**原两条Curb N80**既有GPUcap字典：contacts2^20/patch2^16/foundlost2^18/foundlostaggregate2^22/totalaggregate2^20，保同一个PhysxCfg对象的solver/external-force设定；真实envCTOR之前赋值不被postinit覆写。9Ready前`torch.cuda.empty_cache`仅放未引用reserved，不丢live缓存/DR/RNG。SDK原默认值未知不编“20k默认”，Ready保存原SDKcapacity及新preset值。旧S135也没有preset，只有两个Curb原本有，早console“original3”是文字错误，不是三条都原有；当前source与机器索引写清。**容量/接触overflow若有必须排除技能资格**，不能降接触/solver掩盖。无新OOM报告；CURB113走完freshreset/实际geometryquery，在lazyimport curbaux→g4时ModuleNotFound，9zero commonstart；[V6闭合](<reports/NINE_SINGLE_GPU_V6_CLOSED_20261102_100350/CLOSED_RESULT.json>)。
- **V7**补exact原G4两个数学函数`canonical_triangles/downward_triangle_heights`（AST逐节点同、原878/113g4整byte同2975B/SHA67bbebe...）；新runtime `g4_worldmesh_query_contract.py`仅原两function源段+numpy，省略未用g3CADgenerator导入与wave expected_ground，无几何替代/无triangle predicate改写；full原file保存.txt+sourceSHA供追证。child同时出可直接用整originalg4的ADDON（g3和profile原已在runtime里），两方案都有效，但**已消费V7不再换整file为标签重跑**。Stage14deps闭合。这次S135在descriptor `assignments()`读`FeedbackDelay.lag_steps`字段失败，真实API是`.delay`，仍zero controlled，见[V7闭合](<reports/NINE_SINGLE_GPU_V7_CLOSED_20261102_100958/CLOSED_RESULT.json>)。
- **当前V8**只把discarded descriptor reader accessor改`.delay`并标单位original100Hz sample ticks0/1=0/10000us，四role真实feedback_delay_mild.py源码一致检查；不修改任何delay/RNG/队列/物理/判据。之后全9实际Ready且共同开始，后续等待本次终末，不用另起V9为收据标签或补Git。

## 子source交付晚补（均尚待phase10）

唯一子32baa298… inactive/done，未做PT/SDK/GPU/SSH/parent文件修改。
- [五源API审查](<NINE_FIVE_WORKER_V2_SOURCE_API_REVIEW_V1/FINAL_FIVE_SOURCE_API_REVIEW_INDEX_V1.json>)、[D4真实形状](<NINE_FIVE_WORKER_V2_SOURCE_API_REVIEW_V1/FOUR_E1_D4_ACTIVE_SOURCE_SHAPES_CONFIRMATION_V1.json>)：pending80x4/80x2，lag_steps各80（leg4/wheel2 coherent perenv独立组lag，不是perDOF），不可扩缩。
- [allocation审查](<NINE_E1_ALLOCATION_ONLY_SOURCE_REVIEW_V1/FINAL_ALLOCATION_ONLY_SOURCE_REVIEW_INDEX_V1.json>)：仅Curb2原有preset，S135/S50未设；SDK defaults具体数值未见不猜；OOM末次2240不是总缺口；emptycache不保证fits。含UTF8/GBK reader错误保原。
- [原G4 addon](<E1_ORIGINAL_G4_DEPENDENCY_ADDON_SOURCE_V1/FINAL_G4_DEPENDENCY_ADDON_SOURCE_INDEX_V1.json>)：原13‘complete runtime’不等于闭合imports，lazyCurb分支漏g4，四原nonPT Stage表g4均0不是只缺B sys.path。g3 .py2705B SHA8b0f15.../profile121914B SHA59d585...均原runtime/isaac/mod4；原g4无topSDK。old13声明appendonlyerratum/source-smoke external numpy/trimesh明确stub，非数值/SDK验证。当前父选择exact AST两function派生与原filebyte留存，见[派生证明](<E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V4_G4_MATH/G4_MATH_SOURCE_DERIVATION.json>)。

## 下一步具体执行

1. 保留当前V8运行，不再读旧20kraw/模型，不盲重复status/新SDK。唯一collector会收原终末，工具job_output适度wait或等通知；所有后台job除它均已collected。
2. 取得`reports/NINE_SINGLE_GPU_V8_LATEST_CLOSED_RESULT_PATH.json`后按9角色FINAL/ERROR+originalwait+PRE_CLOSE判执行是否完整，区分commonStart/真实控制步/技能谓词。E1实际start证据用FINAL.wall_start_epoch+group_barrier，非缺少父5marker。
3. 真正单卡并行证据：全9sameUUID+globalallReady/commonStart+每workerwallstart/end交集（预计与E3短窗口重叠），实际numenv80/allScope；不要宣整20kresume或原acceptedpopulation配对。
4. 从FINAL提原技能事实：E0 20s诊断无原globalgrade；E2 24s原Cycles213同UID2pi完整/阈值，缺overallgrade；E3 13recipes初同episode **credited** 稳定50pub100Hz/3s request，normal12非rescue；H1true270 goal.success/launched/landed自然flags、20s原cfgdefault不是已接受cohort；Curb878/113/S135原15s同episode两轮端点+接触1N+stand26原scope（S135仅5°2m），S50 owntraining-axis20s描述无原acceptedpredicate。
5. W35 32s latest8d。FINAL `skill.original_RM70_interval_route_facts`events包含站/动混合，不把总kinmet当高速。可对 **本V8新own**W35 positional JSONL+schema做唯一新CPU pass（manifestbytesSHA绑定，无PT/旧raw/SDK）；字段source rm70_intervals227.close L151–168：record_type same_UID_original_RM70_command；standing/nominal_speed/natural_complete_nonterminal_interval/complete_interval_bounds_fact/along_speed/BODY_reference...。Schema解码常量+positionalfields原样，按moving/standing/nominal~.3 bin分列，goal只是observer非trainedtarget，old沿速不×8。
6. 检查9新stdout原logs的CUDA OOM/contact/pair/buffer capacity overflow等真实错误，不用降低新gate误扔旧合法样本。stagepreset不能自动证明无overflow/新plant完整技能毕业。
7. 生成逐专家结果表+机器index/Registry_v8追加新fresh80scope，旧v7/已冻结source/错误不改；然后phase10归档所有晚Source/错误/V1–V8完整actualmetadata/SDKlogs/当前progress/新结果，originalrecord_experiment+exactdiradapter（参考archive_phase9.py）。只feature+uniqueannotated trial，main只读；不为Git重跑任何评测。当前Git仍phase9 remote83df839.../trial cb79...main27ee...；phase10未做，不说已推。

政策已再次实际读repo-lqr/AGENTS.md、docs/ALL_TRIALS_AND_REPORTS_GIT_POLICY.md、docs/NEXT_AI_GIT_WORKFLOW.md。保凭据不入Git，PT/USD/NPZ/原telemetry等大原件仅已知path/bytesSHAmetadata；Git与预算/训练完全隔离。源扫描redact复用已验证archiver。新Git验证若仅工具输出可止无限回执递归；若落盘正式报告则append下一补档或标pending。
