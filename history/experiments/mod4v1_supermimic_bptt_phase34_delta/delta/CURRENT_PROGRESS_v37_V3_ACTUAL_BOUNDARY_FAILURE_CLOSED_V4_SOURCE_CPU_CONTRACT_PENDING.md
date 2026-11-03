# v37：V3实际边界接口失败已双wait/EX闭合；V4最窄SOURCE和CPU合同待完成

2026-11-03 22:49 +08:00。最新实际Goal rev15/active/armed/round9/48，ID `goal-1c14ef7d-c888-4287-83bf-c008d54545fb`；仍阶段1，无合格capture/exact/Stage2训练/新技能评测。H1/母本/Registryv12/原2c-bae physics/fullDR/accepted/资源/C/期限保持。[本次人类可读报告](<PHASE1_V3_NATIVE_EPISODE_BOUNDARY_FAILURE_FINDINGS_V1.md>)。

## 实际V3（已消费）

- 全新root `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_PHASE1_E3_PASSIVE_CAPTURE_V1_RESET_BINDING_V3_20261103_223416_1793716456364954400`，INPUT sibling在相同名字加`_SOURCE_INPUT`。
- final worker13/index124202/bdeea3f…/seal80b27…、materializer11/38e530…、collector9/2f618…都已固定。父独立回归44/42/43+pure27通过，SOURCE非native证明；[父mat42](<reports/PHASE1_MATERIALIZER_V3_PARENT_SOURCE_VERIFY_V1.json>)和[父collector43](<reports/PHASE1_COLLECTOR_V3_PARENT_SOURCE_VERIFY_V1.json>)已落盘。完整source镜像313件、payload331/4,316,793B。
- 实际Linux[preflight](<reports/PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_PREFLIGHT.json>)RC0，原B2源码435/155+4routingJSON+diagnostic5完整重建精确相等；[stage](<reports/PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_STAGE.json>)RC0，共3839件/独立原static3592/3冲突retained，receipt SHA `7c3614a215e976ec75a58770951164073a4f89ad6747020ef21149d86926c6d0`。stage/uploader均已once消费。
- 同原d557 parent+9595 controller [实际dispatch](<reports/PHASE1_E3_CAPTURE_RESET_BINDING_V3_ORIGINAL_PARENT_DISPATCH_ONCE.json>)：controller1547510/ticks145812863，parent1547517/ticks145812889；Popen epoch1793716744.851046。worker1547526。
- 实际原准入、READY/GO后到了worker159 original bridge.step返回后的boundary处理，错误 `separate original bool term/trunc N80 required`。worker RC0 fastclose仍有WORKER_ERROR，原parent/outer均RC1；父实际wait唯一子、private GPU EX/global finite EX释放、exit1793716765.8408022/wall20.373003244400024s/errors[]/canonicalwrites0。**没有自己的live scene**。
- [本次collector CLOSED](<reports/PHASE1_E3_CAPTURE_RESET_BINDING_V3_ACTUAL_CLOSED_20261103_224036/CLOSED_RESULT.json>)正确FAIL；[pointer](<PHASE1_E3_CAPTURE_RESET_BINDING_V3_LATEST_CLOSED_RESULT_PATH.json>)保留fullmetadata字节SHA，controls:null。不能用RC0/已step反推完整control数。原producer grade和fast-intent/fullFINAL hash错误保留，不修原件。
- [单次失败分析](<reports/PHASE1_CAPTURE_V3_CLOSED_BOUNDARY_FAILURE_FACTS_V1.json>)保存原ERROR/outerwait/EX证据，未读新trace/PT/SDK。所有V3 preflight/stage/dispatcher/collector和所有父测试/hostjob均结束收取，不重跑。job d2f32…RC1是实际failure非工具故障。

## NEW source工作（没有新native）

强SOURCE候选：原boundary构造直接保存device并比较Tensor.device，V3 worker126传env.device，bridge86已另有规范 `torch.device(env.device)`；SDKenv.device属性仅转sim.device。**实际env/flags类型shape/device未录，原因未native证实。**

- 565 `565b1562-3c38-4864-8a0f-ed68a3526f7c` active NEW boundary_device_contract_v1：原完整canonical7a092/37927的待父实际TorchCPU fixture（不由子执行），synthetic str/torch.device差异、true flags/mask、shape/dtype negatives/RNG输入不变；并NEW workerV4最窄仅worker126实参→现有bridge.device。其他4candidate、B2/bridge/core/DR/flags/predicate/SDK/资源/close/loops保持。先源/CPU证明、实际flags仍未知；尚无V4 final13/index。
- D664 `d66482f4-bbf6-4ad6-a2b4-231a32e6bf8a` active NEW materializerV4传播，等待565固定finalpins；保V3全164B2/4JSON/隔离mirror/root-normalize/原8static/banks/27/vendor7/origin-retained-stream/bootstrap/AppBase/资源。只worker4来源/pins/source版/必要标签，不猜PIN，未封不能用。
- CFF `cffddedf-0c4e-4a0f-bffd-8b2d48a6785b` active NEW collectorV4传播，同等候final4；保50+extra174独立库存/生产AST仅report尾/wholeFINAL一次cache和traceparsed实话/producer grade/双wait/EX。无actual calls/读reports。
- A194 `a194a451-f51b-471a-bcbd-765d5e40093e` active NEW actual_capture_application_v1，纯decoded API+synthetic/文档，无actual读取/fetch。确认collector投影剥五大trace字段，不能拿projection当whole；真正成功后需要NEW科学用途原whole worker+group FINAL各一次read/hash/decode cache，原task/lifecycle可用完整发布件。原pure17pins只是schema不是V3/V4 producer证据。V3缺FINAL→NOT_EVALUABLE/counts/execution null，绝不造数据。Brief曾误提45s，已明确撤销，不存在该期限；原1800/900/2400全部保留。

下一步优先565最小真实TorchCPU合同，若Source/数值证据支持，再sealed NEW V4闭包/新root原准入；原失败root与三代封件均不改/不重放。Stage1真实信息充分之前不训练Stage2。

## Good holdout已封、尚未父review/native

[source_stage_good_expert_holdout_v2/README](<source_stage_good_expert_holdout_v2/README.md>)：seal1874/`efee47debc71f12b9eed123283e08e34dcec757893cbff5532056db08657d75c`，9members root`eb8b7b9ea06bbac56132eb0a761da35780547cc35ff9f9c1fb0166838a6b7d42`；entry47717/`f7638e1f24e416780d6124df5fea2492a63d5daac73984470b96a32132ca242d`，index22432/120bfd…，mirror17502/4a3c95…，**67 WORKSPACE-relative依赖含R/T siblings，不是V3 R-relative**。NEW18/18（非旧18replay）实跑未改完整metadata_validate+oldoverlay两seed29/30接受extra/retained，原27独立wholeplanraw、3真实冲突origin/stream/sidecar，22原函数AST不动。sourceflags全false/actualbindingUNKNOWN。未actual prepare/preflight/stage/native；仍接口优先。

## Git

Phase33已远端exact：HEAD097024aa31ae01194f7e1ff1fcbbca162d8f0bc2 / annotated311217da9027402c18c067e6a9bf95f873e96e40，main只观测f9afab…；无main写。NEW [Phase34 creator](<prepare_archive_phase34_v3_interface_outcome_once.py>)已只生成[archive源](<archive_phase34_v3_interface_outcome_delta.py>)18851/a378286e66d3c2e4b839f7111366bbd45400a0d94472d56f3dc5236fc8c2b605，[准备回执](<reports/PHASE34_ARCHIVE_PREP_SOURCE_V1.json>)；**尚未实际record/commit/push**。其guard要求本次真实closed双wait/EX，可记录失败而不升级pass。应先archive34收齐finalV3源/CPU/source回归/实际闭合/V37/失败+新SOURCE点时状态并exact pushverify；所有后续sealed4/真实CPU/新native/handoff随后append。

模型/raw不为Git或标签重开，旧once不重跑，所有真实失败/未知保留。Goal仍active，有实质工作不标blocked/complete。
