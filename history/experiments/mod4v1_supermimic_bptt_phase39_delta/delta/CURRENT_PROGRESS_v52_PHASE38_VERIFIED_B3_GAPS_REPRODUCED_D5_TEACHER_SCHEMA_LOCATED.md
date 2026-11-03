# 接续v52：Phase38远端核验；B3两项绑定缺口已复现；D5 teacher schema错配已精确定位

## 状态与约束

Goal `goal-1c14ef7d-c888-4287-83bf-c008d54545fb` 最近实读rev17/active/armed/round10/48；原五阶段顺序不变。仍Stage1，Gate1 UNKNOWN、exact=false、Stage2_GO=false；本轮无新policy BPTT/技能通过。H1/mothers/Registryv12和旧失败不改；physics/fullDR/速度/原接受门、C single-writer/authority/privateEX/finiteSH-EX/reserve86412.86069250107/3900-3600-300/1800-900-2400全不变。无own SDK/GPU/资源observer/未收hostjob。

环境：workspace F:/RMPOLAR-RL；repo F:/RMPOLAR-RL/repo-lqr；R=mod4v1_supermimic_bptt_20261102；connector仅原project_connector.connect72 RAM凭据。remote `/home/lc01/Zonglin Li/zonglin2/run-python.sh` 会重置cwd/PYTHONPATH；任何remote Python都用该原launcher，不假设裸`python`。Office/ACL无RL技能对应，采用FS/CLI/原project connector，无扩权请求。

## 1. Phase38已经实际remote verified，不是v51的prepared状态

archive job94ade8…与push70195…均RC0并收output。

- feature：mod4v1-experts-fulldr-rm70
- commit：`a5988b35814a13bc3bde6e4f2353436a1dcb5440`
- trial：`trial-20261104-mod4v1-supermimic-phase1-typed-codec-cpu-good-input-diagnosis-phase38`
- annotated object：`46715464dd631fd8cc7dfece57399367df1d176d`
- actual remote branch/tag object/peeled全部一致、working tree clean；7711 entries/7023 prior refs/233 new texts。
- main readonly `f483c4ef9a26e6cae07b0d823917c345bcfc91d9`，未push/reset main。

见[remote receipt](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE38_FEATURE_AND_ANNOTATED_TRIAL_REMOTE_VERIFY_V1.json>)。旧record/CPU/SDK/model/raw不为Git重放；之后所有本v52事实、D5final/actualpreflight、B3review/repro、未来B4/D6/CFF传播需Phase39点时及晚期append。

## 2. B3独立STATIC完成与父NEW stdlib实际复现

[BAC报告](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_b3_parent_source_review_v1/SOURCE_REVIEW.md>)11717/a0ad4c1570b98bb0b3f8cd04ee15d1a91298e649b6946400c4a247d926d5af44；[JSON](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_b3_parent_source_review_v1/SOURCE_REVIEW.json>)28891/5f4b011c2b94033356222e0660f636733dec73daeb78dc351da5584c35f9fd57。47 SOURCE pre/post同bytes、22AST/16JSON；项目imports/tests/entries/actualreports/Torch/SDK/PT/C/Git0。已全文read报告。

确认：B3默认fixed JSON17codec+5Field/3codec classes/3constants完整，但public override直接采用caller树，空/删集合可跳过遍历；defaults/kwdefaults用Python普通等值，bool/int/float等价未严格区分；source_api signature只回执非比对。旧6callback/严格B2四层reset/source_api、完整668 diff/10immutable AST等没有第三项已确认数学/物理缺陷。现有真实冻结V4**无B3 begin/end**；README不是installed integration，未来用原bridge sole.step返回的flags与actor，不能补observe/reset。

父另NEW [V2 reproduction](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_B3_BINDING_NEGATIVE_REPRODUCTION_V2.json>)已实际stdlib5cases：默认22func/3class；override四集合空仍accepted/0func/0class；published default int0临时换False、0.0均accepted并直接回执对应signature；最后恢复默认22func。27原members/seals unchanged、finally恢复live defaults，旧30未执行、Torch/SDK/model/raw/C0。这是真SOURCE preinstall checker复现，不是native exploit/物理因果。

[原V1失败](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/PHASE1_B3_BINDING_REPRODUCTION_PRECASE_FAILURE_AND_V2_SOURCE_V1.json>)保留：错误假设codec_constants有scalar int，StopIteration在首case/任何default变动前，0cases；新V2只保留两个真实审阅问题，不造该constant案例，旧script/marker不重放。

当前 **0ad8300a-6e15-43f7-ad90-657780f697bf** NEW `source_phase1_passive_sensor_capture_v4`：固定原CODEC_SOURCE_PINS bytes/SHA权威、完整确切keysets、override仅type-aware完整相同仍用fresh fixed tree、recursive literal types strict、只明确outer tuple表示和None归一。原passive/field/source_api整字节/6hooks/B2 MRO/codec不动；NEW11小stdlib tests，不跑旧30/不SDK/Torch/SSH。final未到，不使用未封代码。

## 3. D5封件父核验、NEW实际预检已到完整runtime metadata门

[D5seal](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_stage_good_expert_holdout_v5/SOURCE_SEAL.json>)1700/bf9c6dcfa98e2efe47844e13f55763aadfb20915361a139c0b87e564d4f84bad；root5e44c1870c0dc11fbe325194a12ddafd2715c977599f601c6a136353943db608。8members/外部mirror127=原92不改+35，唯一语义改root canonical_rel，其他28完整func同D4。父全文readREADME/diff/build和prepare421–486；`build_source_v5.py --verify` 实际只读PASS8/127、entry_executedFalse；没重跑12或旧36。

NEW[本地payload](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/PAPER_ALIGNED_REBUILD_20261103/GOOD_HOLDOUT_D5_ROOT_SOURCE_PAYLOAD_V1.json>)169texts/2,919,286B，mirror127、原完整flat20 mapping20PASS，旧136/所有历史失败不改。

NEW caller已一次消费，job7e34815bced94ef6 RC1且output收取，见[实际D5preflight](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_D5_SEED20260929_ACTUAL_PREFLIGHT_V1.json>)：

```text
/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_GOOD_TEACHER_HOLDOUT_20260929_D5_ROOT_V1_20261104_041134_1793736694473597000
```

原ROOT metadata、producer/vendor/完整copy-source/origin等prepare前置已过；481完整metadata_validate576→runtime.select_requested_roles343→_validate_zero_update_baseline147失败 `source-container/motherteacher identity distinction required`。仍before-stage，无group物化/parent/SDK/model/锁/质量。不是第四次现场评测失败，也不把preflight成功部分当完整PASS。不可重用这个purpose/root/caller。

## 4. 精确功能诊断：原teacher同源，stager丢了五个回执字段

首次NEW诊断用裸remote python，RC127 `bash: python: command not found`，原metadata未打开；该失败与marker保留，[launcher erratum](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_TEACHER_DIAGNOSTIC_LAUNCHER_PREEXEC_ERRATUM_V1.json>)单列。之后NEW V2只改为原run-python.sh并独立marker/result，原V1不重放。

[实际schema诊断V2](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/GOOD_HOLDOUT_ACTUAL_TEACHER_IDENTITY_SCHEMA_DIAGNOSIS_V2.json>)RC0，各original producer FINAL仅1read/hash/decode，严格已知6534/6724e1…与6507/7ca2a…；无group/model/SDK/C/资源。明确不是status或Git用途而是本次对象equality功能定位：

- 两role的`checkpoint.teacher_source == FINAL.teacher`均**True**；teacher_frozen is True；四身份字段 type/value全相同。
- D5 row来自`guard.teacher_identity(FINAL.teacher)`只4keys，故`row.original_bootstrap_teacher == FINAL.teacher`均**False**。
- 原九key中的五个额外原回执键被projection丢弃：physical_byte_opens、SHA_calculations、decodes、whole_bootstrap_checkpoint_retained、original_PPO_optimizer_preserved_not_restored_to_new_BPTT。并非母模型SHA/路径冲突。

当前 **D664 d66482f4-bbf6-4ad6-a2b4-231a32e6bf8a** NEW `source_stage_good_expert_holdout_v6`，仅prepare452 row采用`copy.deepcopy(producers[role]['FINAL']['teacher'])`保全原完整九key、必要SourceV6 labels；原完整derive_producer_guard453仍检查四身份/实际tensor freeze证明，原runtime147完整对象equality/冻结要求**不改不降**，其余28完整func/source/copy/fsync/metadata/27+3/资源不动。只5–8小内存/AST/source回归，先核剩余同类投影假设，不调用prepare/stage/main/SSH/Torch。不改原producer数据或D5失败。

**CFF cffddedf-0c4e-4a0f-bffd-8b2d48a6785b** V3(D5)仅最小pins/type传播，自有NEW8已PASS，final README/seal待；原controller/reader/collector整字节不变。收到D5失败告知，只作PARENT_REPORTED，不扩scope，不提前猜D6pins。现有V2(D4)/V1(D3)均完整保留，无good parent或质量实测。

## 下一步

等B4 strictbinding和D6最小metadata封件；父read/hash/新窄回归、CFF精确传播，再新的明确purpose预检。无成功完整good preflight前不启动good SDK；无B4实际Sensor/Delay/typed CPU与新caller接入前不启动typed SDK。Source、实际CPU、metadata preflight、SDK执行、科学接口和原技能质量六层分开。E0原保守诊断选择并非whole-profile≥90；独立多seed保持仍待，Goal不complete/blocked。

Phase38之后上述所有新事实及本v52待Phase39归档；晚期封件/后续真实事件按下一append，不为Git重跑旧records/模型/原raw/physical/CPU。

### 04:25–04:28 后续精确SOURCE结论（更新上面D6单行方案）

D664进一步核对实际active guard8902/855e…、runtime58硬pin及344调用，确认原guard.validate_reference_row130要求row等于四key projection，而原runtime147要求同一row等于实际九key。两role实际数据已由纯内存源码谓词复核：row4过guard/不过runtime；row9过runtime/不过guard。**只改stager452不足，父不再要求不可能的双重对象相等。**

父已明确允许NEW兼容teacher-schema Source：仅guard.validate_reference_row改为要求row保全原FINAL.teacher九key且四身份严格相等；原derive_producer_guard/allstate Source证明与原runtime147完整raw equality/teacherFrozen不变。必要NEW runtime guard hash literal及NEW20overlay index严格传播；父parent无硬runtime SHA、仍原bytes；canonical7a092/AppV6→Base/原资源/actor/原技能条件不改。D664尚未派生，先核最小active依赖；所有旧D5/guard/runtime/JSON不改，不绕过source hash。

CFF V3/D5已final：seal2819/715b7e8c68b749755308a1a009a9e0a4a7c83c06255f9c1babe5da8da15e31d3，12member rootc22982e6996a6f46ea8a033a8373190a4bcb99c096b742001f64d0165ac1c78d；三生产文件wholeV2字节不变，8新Source cases通过。Source127诚实121全文+6报告仅declared。当前inactive，等D6 FINAL后再NEW明确传播，不先猜pin。
