# 最新接管：phase19远端精确核验；真实BPTT E0>=700/E2>=630，已各完整保存400

2026-11-02 19:06，Goal goal-1c14ef7d-c888-4287-83bf-c008d54545fb **revision9 active/armed**（get_goal已复核），目标尚未达，H1冻结。所有启动/协议/producer完整保存SHA和CPU检查细节见 CURRENT_PROGRESS_v4_PHASE18_REMOTE_VERIFIED_NATIVE_BPTT_ONGOING.md，后续以实际producer为准。

## 真实在跑

唯一原parent1475630，E0 worker1477022/GPU0、E2 worker1477031/GPU1；八角色同一原source root MOD4V1_SUPERMIMIC_BPTT8_V1_20261102_181251_1793614371303119100。原budget/唯一Cwriter/authority+privateEX/finiteSH不变；后六条尚未实际GO，不提前报训练数量。

唯一相关live hostjob **pwsh-0628d778d2fa4b85**，collect_actual_supermimic_run_metadata_once.py；最后已收输出E0iter800/**verified H16 BPTT700**，E2iter730/**verified H16 BPTT630**；无parent error/未closed。源GPU完整保存各BPTT400/iter500已实际producer证明（报告reports/FIRST_E0_E2_NATIVE_COMPLETE_CHECKPOINT_RECEIPTS_V1.json），不是把CPU合成软件计入原生。计数继续上涨，0.9技能尚待独立原谓词验证。

第一保存reader pwsh-306e57b49e804cb5与CPU完整恢复软件test pwsh-cdabdfdd31ce43ea都已RC0/收输出/结束，别再跑once。CPU完整restore10项pass，native专家增加0。当前observer不会在跑时跟踪latest_complete，第一保存已获，后续只为新实际purpose读producerJSON，无模型stat/hash/decode。

## 用户低占用共享GPU新指令已入Goal/source

低占用/显存充足，有别人的进程也可用；future新窗口移除compute-app非空硬阻挡，原free>15669MiB/util<=30/RAM>64GiB/disk>50GiB及项目原锁/计费保持。source_runtime/shared_gpu_admission_v1.py和supermimic_original_owner_shared_v2.py源8tests pass且已phase18归档；**未上传/未执行新owner，当前active窗口没有hotpatch**。当前两卡已在跑，不将原已准入窗口回填成共享卡实验。

## Phase19已完成远端核验，不重跑record

- feature **mod4v1-experts-fulldr-rm70** HEAD **57626b09cbed02b5b2efabbfd0c0b632383bdce0**。
- trial **trial-20261102-mod4v1-supermimic-native-firstsave-measurement-phase19**，annotated object **06d6a8f95a2f67e958a2cfa9a17e125786546094**，peeled同HEAD。
- capture121entries，103unchanged SHA引用phase18，20new/changedtexts；SOURCE_INDEX见 repo-lqr/history/experiments/mod4v1_supermimic_bptt_phase19_delta/SOURCE_INDEX.json。包括原生首个400fullsave receipts+reader、CPU complete-resume source+10软件检查、v4handoff和capture时已有measurement源/历史43tests；后生成/变化的封版不算已归档。
- archive job pwsh-8d9bdf376d894297与push/verify job **pwsh-b3df5caaae404dfa** RC0输出均已收；remote feature/tagobject/peeled严格匹配；working tree clean；remote main当时只读1044a69fef42ace2dee82f2dcb229538dc029a9b独立变化，无main push。

## Measurement agent刚封版：真实最终46tests，后续补档pending

agent **d9af2e50-3e24-4eb6-8177-72271f9d0ac2** 已inactive并发最终结果；本v1从此不改，改动另建v2。目录 source_measurement_review_v1。

- SOURCE_MEASUREMENT_REVIEW_MANIFEST_V1.json **4244B SHA68d5177d67fcae191ea3c747627b808a185b0c0b6f65488ccc507186a5b08165**，列8件源码/证据；manifest自身另计。
- observer_uid_ledger_v1.py **30636B SHA4c9c8463e6afd39876b0d0a72fdc01a849f021a42d65f17ffb256ea580a6d08c**。
- native_validation_observer_entry_v1.py **4606B SHA9191c104eee09b1b4a3fd1b8628be0110b6cbaf13d60f7571ab51908dc60ce33**。
- test_cpu_synthetic_v1.py **22825B SHAeb5d9391189e719148f8de62186dad91047f43627fc89a121033f8010466ebc3**；CPU_SYNTHETIC_TEST_RESULT_V1_FINAL.json **6358B SHA84852c93d0c197cf00e810a4975e1a0d0e96a2fa0da9fb17bdbf065b6320d0ba**：**46/46 stdlib CPU合成pass**（历史首轮43receipt保留，不绑定最终源）。
- MEASUREMENT_IMPLEMENTATION_PLAN_V1.md **18404B SHA30b8a548c1f26f7c3a705befcfa8a8a70a8e07991980eb164b5133ee769fa3fd**。
- SOURCE_EVIDENCE_AND_GAPS_V1.json **10885B SHAf065ad6b5283d9ebabcaade4ef916d182e5843e61fbb5b6a71925e58daaaeb61**；SOURCE_PROVENANCE_MANIFEST_V1.json **4740B SHA56338693335cc695e9281cafe22edc3c706d935f6ea21115d56b342d0d7ed70a**，13关键原源metadata快照，不是全任务前后hash基线。

E2 .5±.05/cross.05/yaw.2和W35max(.03,.1|BODYvx|)/yaw.2不变；E2 complete+terminal留分母false，W35terminal/unknownstart/partial在条件分母外而全attempt仍留，moving/standing原Boolean分开。独立入口submit(event)只接标量，future验证owner在before_control/pre-reset termination endpoint/resample前后/reset前显式递送，无自动hook，无额外step/RNG。**尚未安装/未运行native frozen验证**；实际getter/backend/cachephase/activeE2projection/matchedUIDcohort/真实专家pass均null，非runtime已修复。

基类root_pos_w alias root_link_pos_w（actor），root_state_w linkpose+COMvelocity，尚不足以归因COM错位；W35混合getter/frame xyzw必须采实际frame capturetick非readtick；训练xi缺原UID/flags，别从它猜标签。原E0/S50 binary accepted谓词缺口仍在。

**本v5handoff以及measurement最终封版晚于phase19 capture新增/修改的文件，待后续phase20补充归档**。不声称它们已在phase19；不为补档重跑CPU/physical/record once。phase18/19已远端核验的对象不改不重造。

下一步持续真实BPTT/原有限保存closewait成本/锁释放、后六角色原队列；若有限窗口未够3000，新unused future窗口需完整新BPTTlearner恢复并明示freshEnv reset，不能重复teacher bootstrap后把独立学生计数相加。core.load(allow_environment_reset=True)CPU软件已验证，worker续训接口仍需新版本再启用。各角色最终>=90与多seed/原完整分母尚未实证，Goal维持active。
