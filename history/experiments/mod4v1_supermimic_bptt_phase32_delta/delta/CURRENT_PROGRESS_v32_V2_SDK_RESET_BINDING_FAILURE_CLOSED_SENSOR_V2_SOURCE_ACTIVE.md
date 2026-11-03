# v32：V2实际SDK路径推进后reset identity preflight失败；已双层wait释放；严格B2源码中

2026-11-03 21:20 +08:00。最新get Goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` **rev15 / active / armed / 9/48**。仍阶段1，没有阶段2native训练，不能把两次启动尝试当技能评测或计数通过。H1/母本/Registryv12/原2c-bae资产、400-k2000-d3、50/100/.0025/TGS32,4/闭链.01/mimic.01/全DR及原接受/C/锁/期限保持。质量80/90及E0/S50 authority gaps不变。

## 已闭合V1与已完成的SOURCE/CPU层

[V31](<CURRENT_PROGRESS_v31_PHASE31_VERIFIED_V1_CLOSED_FAILURE_WORKER_V2_96_PASS_MATERIALIZER_PENDING.md>)保存V1完整MissingModule closed truth、原sensor/Delay/queue真实CPU及全部source pins。V1 source13和实际root不改/不复用。

V2 worker13 seal caacf… / root83cb…，index cdb2…；三个窄修复为真实bootstrap路径、nonfast传helper、binding文件不额外加epoch。[父独立96回归](<reports/PHASE1_WORKER_V2_PARENT_SOURCE_VERIFY_V1.json>)已执行PASS，未当SDK证明。

V2 materializer10 seal399b18… / root3be49…，33stdlib；entry34834/e39fc8…。父read四处增量+验证全部263引用mirror／原17helper AST／其余完整函数不变：[280-file payload](<PAPER_ALIGNED_REBUILD_20261103/PHASE1_CAPTURE_SOURCE_PAYLOAD_V2.json>)共3,445,048B。V2 collector9 seal8a0dfd… / rootf810…，33stdlib，父read新pins136行及生产元数据增量，复用完整V1核心read。全部old封件不改。

## V2真实Linux preflight与完整文件stage已执行一次

[实际preflight](<reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_PREFLIGHT.json>) RC0：**同一个worker.bootstrap_original_helpers(group)**在Linux正常导入两个完整原helper，校验actual origin/code/PIN，无storage/SDK constructor调用。

[实际stage](<reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_STAGE.json>) RC0，3675stream-hash files／3592独立原baseline／三冲突原bytes保全，stage receipt SHA：

```text
31656d597f8ed70588b65a60d869caffae3809613aff3806126722a37c575218
```

完整原8runtime/static banks/NPY/NPZ/assets/vendor7以及AppV6→fullBase/canonical7a092均保留。新root已消耗，后续不复用：

```text
/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_BOOTSTRAP_FIX_V2_20261103_210419_1793711059317188800
```

## V2实际原parent/SDK尝试与完整闭合

[实际dispatch](<reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ORIGINAL_PARENT_DISPATCH_ONCE.json>) epoch1793711202.064033；controller1543093/ticks145258584、parent1543101/ticks145258609，只1次原parent。实际资源门在collector原件保留，GPU0/private EX/finite EX/C ownerNone/read-only不变。

仅worker1543111，已经越过bootstrap、进入E3 env构造、原唯一reset/DR检查/原obs/bridge初始化，然后在worker138 sensor安装的preflight173/source_api176报错：

```text
ValueError: Function identity mismatch: RecoveryEnv._reset_idx
```

这不是再次MissingModule，也不是物理技能或恢复通过率。

- worker真实wait RC0（原fast App close），但有WORKER_ERROR，因此parent和外actualwait RC1，失败绝不按RC0冒成功。
- PARENT_EXIT_SCOPE epoch1793711219.033531、wall16.380154609680176；allownchild waited、privateGPU EX和finite EX释放、canonical writes0、foreign untouched。外层Popen.wait同pid/startticks独立回执。
- READY／共同GO／FINAL均缺失；observed controls/physics/PT/training/optimizer等producer计数保持null。由source错误位置可推断SDK env构造已走到，但不伪造实测callback数量或分数。
- [最新closed指针](<PHASE1_E3_CAPTURE_BOOTSTRAP_V2_LATEST_CLOSED_RESULT_PATH.json>)→[完整结果](<reports/PHASE1_E3_CAPTURE_BOOTSTRAP_V2_ACTUAL_CLOSED_20261103_210748/CLOSED_RESULT.json>)；collector job fad679…实际RC1、已调查，`FAIL_CLOSED_CAPTURE_EXECUTION`。
- [紧凑原事实](<reports/PHASE1_CAPTURE_V2_CLOSED_LIVE_BINDING_FAILURE_FACTS_V1.json>)和[人类结果](<PHASE1_V2_NATIVE_RESET_BINDING_FAILURE_FINDINGS_V1.md>)。

SDK已使用真实时间，未把PT0说成zero-cost；原finite validation read-only协议保留、external settlement reference还是producer Unknown，不新增账本/审批gate/退款。阶段1capture/exact/Stage2仍False/Unknown。

## 当前确定SOURCE缺口与未知现场身份

B旧preflight env_reset直接固定到class RecoveryEnv descriptor，但原完整DR constructor安装四层无__wrapped__的instance MethodType reset wrappers。父已read原四source对应constructor，0ad独立确认E3 SOURCE外→内固定顺序：

```text
ExplicitPDSDK.__init__.<locals>.reset_idx
→ ChassisCOMSDK.__init__.<locals>.reset_idx
→ GasDampingSDK.__init__.<locals>.reset_idx
→ SpringPressureSDK.__init__.<locals>.reset_idx
→ RecoveryEnv._reset_idx
```

closure均adapter/original、boundself同env；_spring_pressure实际LearningSpringPressure继承原SpringPressureSDK，adapter MRO需真实核对。SOURCE链与现场mismatch一致，但原error没有发布actual outer module/qualname/source/code/closure，**实际outer和全链仍UNKNOWN**，不得把固定SOURCE顺序冒现场观测。

源排除：FreshDRNominalGuard实际路径未进入临时reset context；getter.capture_initial不包reset；OriginalEpisodeBoundary无env；bridge只包termination.compute；本syntheticzero probe未用frozen history policy。0ad继续审查其余scene.update/feedback/termination preflight条目，避免只修一点再盲native；不改原DR wrapper、不额外getter/reset/obs/RNG。

## Active SOURCE任务（下一步依赖）

1. **0ad8300a-6e15-43f7-ad90-657780f697bf**：[NEW reset身份诊断](<source_phase1_sensor_reset_identity_diagnosis_v1/>)及NEW passive sensor B2。保留原class descriptor，固定原published四wrapper source/hash/bytecode及顺序，逐层验证MethodType self、closure.original/adapter与实际env实例属性/MRO；错层/重复/未知/外env/污染皆失败，不删校验、不动态pin expected。用真实已发布wrapper函数composition做stdlib正反例；增加失败observed metadata，现场未知不填猜测。旧B13/manifest/seal不动；暂无最终B2 pins，等待final source。
2. **565b1562-3c38-4864-8a0f-ed68a3526f7c**：NEW worker V3未封模板，只逐bytes继承V2五candidate sources；待父转B2固定13seal/manifest/API才最窄传递新sensor dependency/source index，不另写reset verifier、不改main/DR。没有可误跑浮动pinsealer，不自行stage。

D664 materializerV2及CFF collectorV2已完成inactive；等B2和workerV3稳定后父再发最窄pins propagation SOURCE任务，避免先封浮动值。typed wire/API V1保持，future全新root将RESET_BINDING_V3尾缀，无旧purpose自动重跑。

现在所有hostjobs已完成且收取：4b09 preflight／1ae9 stage／f9f5 dispatch／fad679 collector（RC1=原失败），自己的native parent/worker双层wait已闭合、GPU/EX释放。没有资源observer忙轮询、没有native在后台继续。不把Source-only工作或GPU空闲等待修复当Goal blocked。

## Git与pending

Phase31远端exact已核验：featureHEAD `bf55ab9313816b43d98b69ddf5c951b1d39a27f1`，annotated obj `dcf3ef1fb452f2d5b022dc3de8b7962698ff9091`、trial尾phase31。main上次仅读8654c630…，独立变化不回写；绝不推main。

**Phase32待新source归档执行**：V1 collector最终9seal和actual closed、V1 findings；V2 worker13及父96回执、materializer10/263 mirror/payload及新once callers、real preflight/stage/dispatch/closed失败、collector9seal、此v31/v32/两篇人类findings/source诊断及B2/V3 point-in-time。新真实失败都保持独立root/原件，不因归档重跑SDK/模型/raw/旧once。捕获之后的B2/V3 final封件/新native/交接继续pending下一append。
