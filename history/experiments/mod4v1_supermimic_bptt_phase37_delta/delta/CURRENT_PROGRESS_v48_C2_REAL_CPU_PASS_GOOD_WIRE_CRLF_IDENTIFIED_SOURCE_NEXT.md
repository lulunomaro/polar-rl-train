# 当前接续v48：C2真实CPU合约通过；好专家两次preflight输入问题已实定位

## 当前状态与Goal

最近实际Goal rev17/active/armed/round10/48，id `goal-1c14ef7d-c888-4287-83bf-c008d54545fb`；仍Stage1。五阶段顺序、H1冻结/母本Registryv12、原物理/fullDR/速度/接受阈值、C single-writer/authority/privateGPU_EX/trainSH-evalEX、reserve86412.86069250107与3900/3600/300、1800/900/2400不变。没有新policy训练、旧候选晋升、foreign信号/清锁/退款/新ledger。Stage2未放行。

[上个v47](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/CURRENT_PROGRESS_v47_PHASE36_VERIFIED_QUEUE_FIRST_SCALAR_LOCATED_NEW_CLOCK_SCOPE_SOURCE.md>)保留真实64/512/128 capture、单worker功能locator、原CONTRADICTED与Source/Git36详情。该capture已实际关闭/双wait RC0/两EX释放，不重放。旧actual scientific report保持CONTRADICTED/Gate1Unknown；首异常是control0 seq0 target_write/legs 的int tick=-1，来自C1通用counter-1元数据规则；不是实际queue.apply(-1)证据，也不指定actual caller为gas。

## C2 SOURCE与真实原队列CPU已完成

[NEW C2 seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_actuation_clock_scope_v2/SOURCE_SEAL.json>)5938/105df1f6e47b82061aae729878a12874f731dd34b7cb0feeb75724028298469b；core20859/ec10b09b77548c560611e641d685e2cee029c9778ff8c8852a8bf070243bd95d；5member root56f6e326acbe362752ce375e8c1b0b7fa64a75a530a7120db5b5d7c25628e598。仅_patch和module docstring改；其余20完整函数AST同C1。无parent setter保留rawcounter、N/A物理tick、UNKNOWN group；parented同asset仅证明动态context，DOF/target仍需独立join。没有启用、没有接worker、没有完整新schema consumer。

父已读C2 _patch/84行diff/35README/175seal/228tests；[父NEW12](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_C2_CLOCK_SCOPE_PARENT_SOURCE_VERIFY_V1.json>) 12/12 PASS、.0347s，old seals不变。原C1/pure/所有失败保持。

NEW [C2 CPU fixture seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_c2_real_cpu_fixture_v1/SOURCE_SEAL.json>)4983/e2642cfb5731a83438c963202d3b07d034952795e67dfc16438fbdf4954a74b1；完整359行fixture19928/51aba475…只doc+TAP pin改、全部原函数AST同；新wrapper94行7290/eb092789…已父完整read，旧件不改。

[NEW实际CPU报告](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_C2_ACTUAL_REAL_QUEUE_CPU_V1.json>)已执行并收取job `pwsh-58db8243b5e64783`，RC0/PASS：真实Torch2.10CPU、真实原a423… PhysicsActionQueue、N2/N3各9lags/432组apply，合计864；各N另8非term setter probes（4 normal+4原exception identity、16owned Tensor检查、8完整queue/private/global RNG检查）。原normal/reset/idempotence/overflow计数与新非term计数分开；global Python/TorchCPU RNG不变。没有SDK/GPU/模型/C/资源操作，**不是实际C2 SDK/DOF/物理readback/技能证明**。原once均已消费，不重跑。

## row/clock证明设计与新薄实现任务

[565设计](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_capture_row_clock_provenance_design_v1/README.md>)18933/2ae8ab97…与schema58537/6f1e63…、seal1229/37cb8c86…已完成；8/8自有stdlib/AST，首轮一own AST名称失败保留。它未实现worker或触C2目录。

已确认：B2通用shape80 selector会截K80 reset IDs；observer.materialize tolist丢dtype/shape/axis；mixed first32/last32与独立term/reset last4会丢自然pair。原SDK早已算fullN80bool term/trunc与实际int32 reset IDs，可直接保留，不新增nonzero/getter。原D4自己每apply已经读取target/error≤1e-6并更新calls/formula_max_error，可只从存储字典快照，不说observer额外readback。term._joint_ids若原存Python list/tuple/slice可保留；Tensor值未知，不新取GPU值。准确verify_actuation_binding在observer:129–170，现缺该DOF记录。

当前并行SOURCE：
- **565 `565b1562-3c38-4864-8a0f-ed68a3526f7c`** → NEW `source_phase1_typed_capture_codec_v1`，独立小typed codec+bounded atomic control-ledger，ENV_ROWS_WITNESS≤8 /ENV_IDS_FULL≤80 /TERMINAL_BOOL_FULL80 /QUEUE_GROUP_FULL80明确分域；真实dtype/shape/映射先记录，源tensor同device clone，outside-loop才materialize；最多128控制pack，不额外采样/新getter。须先发真实API给父再转B3，finalpins稳定后绑定。
- **0ad `0ad8300a-6e15-43f7-ad90-657780f697bf`** → NEW `source_phase1_passive_sensor_capture_v3`薄接点，保留B2严格四层reset/source API/原函数一次返回/噪声cache/RNG，等565 API/pins；normal原MID/END五channel clean16，MID另19/clean0不造；full flags+原IDs atomic关联，未观察标NOT_OBSERVED非empty。无SDK/worker/stager。父尚未接线。

## good holdout lifecycle SOURCE复核通过，但实际preflight未通过

[独立review V2](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_holdout_lifecycle_parent_review_v2/SOURCE_REVIEW.json>)8953/4c91f5cc…：先own guard5/5，再完整NEW40一次40/40、3.482s，82profile/FS检查点、五audit全0；same whole CodeType绑定两个fake watch，实际native/network0。104 SOURCE未改。V1的39/1、counter1对象UNKNOWN与profile缺口永久保留；不是旧失败转绿。父已读MD53/JSON210。D3独立32、CFF12封件仍原样，无quality结果。

### 第一真实preflight：父logical镜像不是flat20

[第一次报告](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_V3_SEED20260929_ACTUAL_PREFLIGHT_V1.json>) job0c427…已RC1/收取。在D3 source_mappings:173，source-dir只有logical subset5文件，缺canonical a1_frozen_eval_runtime_v2.py等15个flat basenames。原103文件/79完整R-T镜像没丢字节，但没有按原CLI要求组装flat20。尚未stage/parent/SDK，不是技能失败。

父NEW [flat20 payload修复](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_SOURCE_PAYLOAD_V3_FLAT20_FIX_V1.json>)：保留旧103，新镜像123/1,708,075B、另20flat；完整未改原D3 source_mappings本地20实际通过。旧caller/root/payload不改、不复用。新preflight root：

```text
/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_GOOD_TEACHER_HOLDOUT_20260929_V3_FLAT20_FIX_V1_20261104_024446_1793731486964044800
```

### 第二真实preflight：缓存CRLF identity被当成原wire

[第二报告](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_V3_SEED20260929_FLAT20_FIX_ACTUAL_PREFLIGHT_V1.json>) job9f127…已RC1/收取；flat20通过，D3.prepare:394 `fixed published original GROUP_PLAN bytes differ`，仍未stage/parent/SDK。

父NEW功能诊断仅原wire读取/hash/decode一次：[wire/cached比较](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_ORIGINAL_PLAN_WIRE_VS_PUBLISHED_DIAGNOSIS_V1.json>)，job5fdee…RC0/已收：

```text
actual wire=14112 / a78cbaf8961264f16bdd1007dbab72a0fb442fae080978f057e52fef1dfd7fd1
published cache=14385 / 54172e4ff8fcd502602d60dfa3c35c9ed5acc02d871691e231637e59123795a0
both canonical=8c3b55e059c82de8113d4c7a19395c079981b31ffab51266161037b86f1ab51a
whole decoded equality=true / diff=[]
```

实际raw源只保存于[新wire源件](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/good_holdout_original_plan_wire_v1/ACTUAL_ORIGINAL_GROUP_PLAN_WIRE.json>)。D664独立源码复核确认cached有273 CRLF，CRLF→LF恰等actual，无字段差异。不改远端原GROUP_PLAN，不放宽成canonical-only，不改两次失败。

当前SOURCE：
- **D664 `d66482f4-bbf6-4ad6-a2b4-231a32e6bf8a`** → NEW `source_stage_good_expert_holdout_v4`，严格actual wire14112/a78 +固定canonical；published cache14385/54172另存SOURCE reference，原required27/retained/fsync/fullmetadata/资源/原publisher规则不变，version4/receipt kind V4/COMPLETE仍V1；actual original_plan_SHA自然H(old_raw)=a78。未实际prepare/stage。
- **CFF `cffddedf-0c4e-4a0f-bffd-8b2d48a6785b`** → NEW `source_good_holdout_lifecycle_routes_v2`，最小typed pins/version4传播，严格拆runtime actual ORIGINAL_PLAN_PIN与PUBLISHED_SOURCE_PIN；旧mirror声明不能偷换a78；完整controller/reader/collector主体预计不改，原parentfc445/runtime4ea1不改。等D4 finalpins后seal，不猜库存数，无native。

实际good-holdout仍0次、无parent/controller/quality；未为seed30构造虚假结果。下一次只有D4/V2正式封存与父审阅、实际preflight/物化通过后再走原资源门。两次失败源码与回执将原样归档。

## Git/接续

Phase36 HEAD99a85ed22f96d156c501fd9c590f54b0163af490、annotated0f670f673f3abd455a8f191429ab8feb39b63493已remote feature/tag/peeled核验+clean；main readonly a00b710…未改。

Phase37 [archive源码](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/archive_phase37_queue_clock_diagnosis_delta.py>)已准备并在首次执行前增C2 parent12/真实CPU864、独立driver40与wire诊断guards/NOTE。初始prepared SHA caa159…保留于准备收据；需记录preexec最终SHA后只执行一次，再exact feature/tag/peeled核验。**截至本v48写入尚未执行Phase37**。本v48/所有实际diag、CPU、两个preflight失败、最终C2/independent source audits/driver失败与修复、现有codec/B3/D4/routes point-in-time文件可在Phase37收录；late封件/实际后续和handoff追加38。模型先于stat/read跳过、raw/binary只producer refs，不为Git重跑once/物理/CPU。

目前所有host后台job已收取、无own SDK/GPU/资源observer；四个SOURCE child继续。Goal有实质工作，active，未complete/blocked；Stage2保持False。
