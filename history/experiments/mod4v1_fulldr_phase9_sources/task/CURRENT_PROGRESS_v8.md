# 接续增量：2026-11-02 07:05前后

以[进度v7](<CURRENT_PROGRESS_v7.md>)、[v6](<CURRENT_PROGRESS_v6.md>)为全技术背景。Goal active armed id `goal-1348948b-8b3e-4e93-85ec-317e88962347` revision2/max12，未完成/未blocked。

## W35原续训窗口已真实保存结账，不再训练

[完整原终末](<reports/W35_resume89aca_wait_exit_watch_20261102_070034.json>)：owner1431521/原GPU0，root `MOD4V1_W35_RESUME89ACA_WAIT_V4_20261102_054158_1793569318385718000`，RC0/wait/原两EX+privateEX+finiteSH全部释放/error null。

- **82** 次新PPO，**39,360,000** 新转换；并非猜又80。此前80次，累计162次/77,760,000转换（这是两次实际记录求和，不反推源counter）。
- 完整新checkpoint **`8d6a9ab5fae3fd2689c59bcfc1f1e776eb162b8eef671417df0fc88150285c54` /17,620,037B/iter32643/17Adam654500**，path `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_RESUME89ACA_WAIT_V4_20261102_054158_1793569318385718000/production/model_final_complete.pt`，parent89aca/32561/652860。完整coreSTDoptimizer目标DR/coursecommand存好；新LR等新SDK缓存读取，未额外开PT。新模型还未RM70毕业，旧89aca/2d不改，不开自动额外PPO。
- [原账只读实际结算V2](<reports/W35_RESUME82_ORIGINAL_SETTLEMENT_V2_20261102_070439.json>)：own实际扣 **3644.470574617386s**；charged1895619.010973692/remaining **372380.98902630806**/authorized2268000，historicalextensions9/new0/refund0。generation原、原reserve86412.86/charge_values未改。SHA snapshotdf5fcac2…，activeNone只当时快照，不永久假定资源空闲，无local账副本/账写。
- 原metadata-reader V1误用total_authorized_training_seconds导致KeyError，原authority源码49确切键authorized_training_seconds。V1保留，[错误说明](<reports/W35_RESUME82_SETTLEMENT_METADATA_READER_V1_ERROR_PRESERVED.json>)，新V2只reader修字段后读真结算，没重跑训练/模型/SDK，不当原PPO失败。
- 原watch **pwsh-7a6beae95c0b49c2** 已done/collected；保存后单次派发 **pwsh-f9f2c8ab84b74533** 已done/collected；结算V2 job **pwsh-567ae44c2ea845a2** done/collected。不要重开。

## 新8d6a独立full32已一次派发，不能当执行PASS

[派发报告](<reports/W35_after_resume89aca_eval_dispatch_20261102_070117.json>) /[单次依赖链报告](<reports/W35_AUTO_AFTER_RESUME_FULL32_BOUNDARY_RESULT_V1.json>)：root **`MOD4V1_W35_AFTER_RESUME89ACA_EVAL_20261102_070117_1793574077925312000`** parent **1438355** creation1793574078.91，GPU0 uuid16828…；源新8d6a，iter32643/654500/N82/新bytes。plannedsourcekindV3，workerSHA0091a0a4… /originaltrainerbbda08…；Task pending=falseadmission，实际sourcePT0/模型copies0，必须等原privateEX+globalfiniteEX+fresh资源actual准入。

旧budgetwriter已自然释放，但GPU1最后SLOPE50原finiteSH可能仍运行；evalparent按原bounded600s/释放全部partiallocks/零SDKPT等待，不改mode/抢锁。SL50先7:01:11持SH，evalparent7:01:18后派，预期自然队列；如果资源超时保原失败/0源目的，不盲重试。

**唯一仍相关父后台 `pwsh-10095bd3705b4d24`**：[依赖链](<run_once_after_resumed_eval_closed_own_raw_cpu.py>) 正只看上述own evalroot；原1600ctrl/12800phys/3200feedback32s新source1read、STD17Adam不变/0opt、RC0/App/envclosewaitrelease真成功后，自动最多一次新ownraw/schema CPU真实1read各、全byteSHA/行数校验/PT0/不读旧raw。然后读该job输出和`reports/W35_AFTER_RESUME_EVAL_AND_OWN_CPU_ONCE_RESULT_V1.json`，运行已准备[三代processedJSON比较器](<compare_w35_three_actual_full32_generations_v1.py>)。原bounds/未paired/cohort与yexposure边界保持，无新毕业率。尚未完成前别开同once或运行比较器。

## 8条谱系新plant协议实PASS；最后SLOPE50在实际运行

前6 E0/W35/E2/E3/H1normal/SLOPE135，新增protected878和独立CURB113。只是fullDR/full20k/native24协议，非所有历史/技能毕业；Curb141原7b网络条件仍pending，无取代。

- Protected878 [完整交接](<CURB_PROTECTED878_ACTUAL_CPU_FRESH_NATIVE24_PROTOCOL_HANDOFF_V1.json>) SHA f8bcfe74…：typed49f5/17614805B/iter32940/LR.00011390625149942935/17Adam660400；rank0完整20k，不宣整60k，历史world3/60k contract保/noNCCLmergefork，8原helpers+extra真装载、1byte/hash/decode/0retype、ONEreset、24/192/48、0update-step-learn/coretree250b1815…/STD17AdamLRsame/RC0wait/error[]/EXSH释放548.07s。
- 原extra receipt有original_axis_writer_semantics_preserved=false，因为[定义源码:68](<staged_sources/E1_CURB_PROTECTED878_40050_MOD4V1_SOURCE_V2/runtime/isaac/mod4/variant_extra_state_runtime_v2.py#L62-L68>)该flag实际等于variant==CURB_INDEPENDENT113（只针对113专属writer），878不适用，不能误作泛axis失败。已[追加解释](<reports/PROTECTED878_EXTRA_AXIS_FLAG_APPLICABILITY_NOTE_V1.json>)，原case/source/handoff未改，未重跑。
- 独立CURB113 [完整交接](<CURB_INDEPENDENT113_ACTUAL_CPU_FRESH_NATIVE24_PROTOCOL_HANDOFF_V1.json>) SHA d941a5c8…：fresh80真PASS67.73s；typed083b全20k parent1436861/child1436870/c27，RC0wait/515.11s/24,192,48/ONE原reset/0update-step-learn/error[]/EXSH全部释放。savedreset_direction原writer兼容load→ONEreset→exact after实审计，coretree0d1d35fa…/STD17AdamLRiter同，1byte/hash/decode/0retype。
- SLOPE50 fresh80 parent1437589/child1437598真PASS70.72s/无PTactoropt/24,192,48/ONEreset/RC0wait/error[]/EXSH释放。[collection](<reports/SLOPE_INDEPENDENT50_actual_case_collect_20261102_070100/COLLECTION.json>)。
- 最后新typed4a5a全20k root **`MOD4V1_E1_SLOPE_INDEPENDENT50_GPU1_N20K_20261102_070105_1793574065642853200`** parent **1438135** creation1793574070.83，child **1438144** creation1793574071.28/c27，actual7:01:11 GPU1privateEX+finiteSH/freshGPU-host真实取，resourcewait_checks0，未只停dispatch。typed17955663B/iter32118/LR3.3750000000000014e-05/17Adam643980/原STD23.347…，stage源0/SDK目的1read typed-only，不重迁移。07:03本case元数据无FINAL/EXIT。等唯一子原collector真结尾，不重复SDK。
- 唯一子32baa...本地terminal依赖续接器已顺序全部派出，禁止新agent/同卡并发/碰GPU0/W35/globalEX。后续必须等50closewaitlease事实，seal3CPU+3fresh+3native/所有旧sourceV1/V2/原JSON/log/error索引，子不commit/push。

## 不要遗忘原技能边界与归档

E3原13姿态3.2s实际133/18462原credit、recipe0/5/11为0，未全技能毕业；完整恢复执行PASS与技能分开。见[原技能判断](<reports/E3_RECOVERY13_ACTUAL_SKILL_DECISION_V1.json>)。旧asset无paired baseline，不能归因MCI。

Phase7 feature/remote eaf5ae9e…/trial tag8596adba…peeled eaf5已核，main只读27ee661e…本会话没push main。Phase8 pending：本增量、原82 PPO全证据与fee、只读readerKeyError+修复、后续eval/CPU、8th/9th actualsource helpers、所有三变体CPU/rootowner/source/errors、E3技能真实与reader、futureCPU source/MOCK、前phase sync receipt。用原record_experiment+exactdirectoryadapter/stagedset避Win206；大weights/USD/NPZ/raw/canonical metadata-only、不为归档重跑。

最前下一步：收唯一子50真实终末；刷新统一registry（原v5只6，别拿其过时计数冒当前）；给pwsh-10095…读新进展/终末一次，真eval+ownraw完成后processed比较并按原指标判断8d6a，不盲发第三PPO。全冻结名单仍7b精确源网络条件未解，保存具体条件不伪closed，亦不globalblocked（仍有有用工作）。
