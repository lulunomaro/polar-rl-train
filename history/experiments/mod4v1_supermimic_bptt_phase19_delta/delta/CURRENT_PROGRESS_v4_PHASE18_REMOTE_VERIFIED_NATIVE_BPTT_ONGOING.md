# Phase18已远端核验；E0/E2真实BPTT持续推进；低占用共享GPU future准入已准备

2026-11-02本轮继续，Goal **goal-1c14ef7d-c888-4287-83bf-c008d54545fb revision9 active/armed**（人类18:48新增GPU低占用共享指令后已edit，后续用get_goal）。目标尚未完成，H1冻结。协议/firstGO/teacher和freshDR完整证据见 CURRENT_PROGRESS_v3_NATIVE_E0_E2_STARTED_SHARED_GPU_FUTURE_POLICY.md；不要重放任何已消费stager/repair/CPUcheck/record。

## 实际运行及唯一观察器

既有原parent1475630于约18:47:28/29自然准入E0 worker1477022/GPU0、E2 worker1477031/GPU1；root仍 MOD4V1_SUPERMIMIC_BPTT8_V1_20261102_181251_1793614371303119100。无抢锁、无新账本/extension/refund/foreignsignal。原有限3900/3600save/300headroom及私EX/finiteSH/唯一Cwriter保留。

**pwsh-0628d778d2fa4b85** 仍相关在跑：唯一 ownpublishedmetadata观察器，pointer SUPERMIMIC_EIGHT_V1_LATEST_METADATA_WATCH.json。最近一次已收job_output发布E0 iteration420/**verified actualH16 BPTT320**、E2 iteration400/**verified actualH16 BPTT300**，实际非CPU合成。输出可能已继续，下一次以producer为准；不要把固定快照20或历史WAIT文件当当前状态。WM/aux/critic与warmup不算policy数量。未闭合，未宣3000/未宣技能80/90。

观察器当前不收在跑latest_complete checkpoint metadata：达到原iter500会有第一个原生产fullcheckpoint（预期BPTT400，不假数）。若需实证保存，针对一次新purpose只读自身production/latest_complete.json/COMPLETE_CHECKPOINT_RECEIPT，不开新旧模型。不另开SDK/worker，不因归档重跑。原parent闭合后观察器一次收GO/ownstdout/closewait/成本/lease并出CLOSED_RESULT；若host重启job_list无job，先核实local原collector确实不live，再恢复一个observer，不假remote已结束。

## 用户GPU共享新指令

后续unused窗口使用新源 source_runtime/shared_gpu_admission_v1.py + supermimic_original_owner_shared_v2.py，source tests8项passed；保留free>15669MiB/util<=30/RAM>64GiB/disk>50GiB，只移除computeapp非空硬阻挡；实际已有进程列表+显存会进admission证据。原项目canonical/private/finite锁保持；当前active原owner/source/manifest未热改，**未来v2尚未上传/执行**。目前两卡已实际使用，不将本窗口回填成共享卡实验。

## Phase18 Git实证（已完成）

- feature mod4v1-experts-fulldr-rm70 commit **8e6160b8747af162b5a486b3f3aa1ad4782223fd**。
- annotated trial **trial-20261102-mod4v1-supermimic-bptt-original-wait-phase18**，tag object **5d36089e5be76616b4c2dbae12014467f6769b28**，peeled commit同上。
- 107source entries/109text files，索引 `repo-lqr/history/experiments/mod4v1_supermimic_bptt_phase18_sources/SOURCE_INDEX.json`。包含全部新SuperMimic封版source/reviews、缺SCHEDULE import错误+preGO修复、原资源等待/hostobserver恢复、DR确认/CPU梯度3软件检查、firstactualE0E2 each20快照和共享futurepolicy源码+8测试、v1/v2/v3handoff、旧PPOlatev23handoff。source_only和native证据口径分别保。
- archive job pwsh-787bb8c89a6446ae RC0输出已收；push+verify job **pwsh-712e940ec24b46fb** RC0输出已收，atomic只feature+trial，没有main写入。
- 远端branch/tag object/peeled逐项完全匹配；当时remote main只读 **1044a69fef42ace2dee82f2dcb229538dc029a9b**，独立变化，不能硬绑此旧main。

## 新的CPU complete-resume软件检查：已真实通过但尚待下阶段Git

为下一有限窗口需要完整新learner续训，独立执行新purpose：`source_runtime/synthetic_cpu_full_resume_check_v1.py` / `run_cpu_full_resume_check_v1_once.py`，job **pwsh-cdabdfdd31ce43ea RC0**已收；`reports/SYNTHETIC_CPU_FULL_RESUME_V1.json`。

10项合成检查pass：自然train2verified policy后完整weights_only保存读取（含NumPy RNG）；无声明环境reset load被挡；Python/NumPy/TorchCPU RNG恢复；WM/pi/critic/aux及normalizers全部相同；4optimizer全部相同；counter/iteration/collect_fraction/transaction恢复；replay原样除声明stream_cut且obs_history fresh；load后从2继续到3不重置0；CUDA未初始化。只own newlycreated synthetic checkpoint，退出自动清temp；**native专家计数增加0，无SDK/源teacherPT/GPU/C/GO**，没有重跑旧CPUcheck主体。真实native保存/恢复仍需actualproducer和后续窗口验证。

这两个新CPUsource/JSON、**本v4handoff**，以及measurement agent晚于phase18 capture产生的所有内容，目前**待后续phase19补档**，不谎称已在phase18。不得为了补档重跑once/GPU。尽量与首个实际完整保存/测量agent封版证据一起追加唯一trial；若只是后续收据可补充归档而非无限新tag。

## 测量agent仍进行中

agent **d9af2e50-3e24-4eb6-8177-72271f9d0ac2**，source_measurement_review_v1，目前已创建observer_uid_ledger_v1.py/native_validation_observer_entry_v1.py/test_cpu_synthetic_v1.py/CPU_SYNTHETIC_TEST_RESULT_V1.json；等其最终SHA/封版消息再把源结果当完成。不得派它碰remote/model/raw/SDK/GO/canonical或修改activeworker。关注root_pos_w alias root_link_pos_w（actorframe），root_state_w linkpose+COMvelocity，实际backend/cache仍待runtime；E2/W35 UID和reference命令cohort不能从xi缺字段猜。所有runtime acceptance状态保持null，原阈值保留，E0/S50 binary原谓词仍缺。

## 19:00首个实际原生完整保存实证

新增独立900秒/20秒一次目标仅首个producer latest_complete的reader `collect_first_native_complete_receipts_once.py`，非重复counter/close collector；job **pwsh-306e57b49e804cb5 RC0**已收并结束。报告 **reports/FIRST_E0_E2_NATIVE_COMPLETE_CHECKPOINT_RECEIPTS_V1.json**：

- E0实际epoch1793617116.129：verifiedBPTT400/iter500，新完整checkpoint247769249B，producer SHA **acab98ca2e58bb262fbb358a06ac373ed613fa68ac530fefe1861663e31de33f**。
- E2实际epoch1793617164.774：verifiedBPTT400/iter500，新完整checkpoint247769185B，producer SHA **cb5f227c493c51eaa655cd96886cfc7a3b867c93dbdcca41e8688a60a01809a4**。
- 文件均角色production/checkpoints/model_BPTT000400_I000500_S0001_complete.pt；各WM2000/aux2000/critic1600，unverified/nonfinite/zero0；H16跨时/WM-path有限非零、参数实际变化；teacher仍原source open/hash/decode各1、teacher未变；原producer证明新models/critic/aux/4optimizer/replay/RNG/history齐全。reader不stat/open模型、不再算其SHA、不触GPU/SDK/C/GO。
- 各400已完整保存不等于窗口结束/成本结算/技能通过；训练继续，后续计数看原observer。

该新增reader/STARTED/receipt报告与CPU完整恢复软件结果、measurement封版源将一起进入新phase19 delta补档（准备中，勿重跑phase18）。

## 下一步

保持实际两卡BPTT进行，后续fullsave仅读producer receipt（不读模型）；新窗口若未达3000需用实际完整新learner/replay/RNG恢复+明示freshEnv reset，不能只反复teacher bootstrap再合计或伪总步。补齐futureworker ownBPTT resume接口前保持原在跑源，原core已有load(allow_environment_reset=True)且CPU软件验证过。每专家>=90仍需独立多seed原谓词验证，数量达到不等于通过。Goal保持active，不因原暂等/未完成paperwork宣blocked。
