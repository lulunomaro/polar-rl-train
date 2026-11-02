# MOD4v1专家统一：当前进度与下一步

## 目标与身份

用户确认W25就是W35/E1_WAVE35。全部新派生目标是刚生成的MOD4v1：USD SHA `2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3`，契约SHA `bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755`。旧权重和框架只作来源，不把旧资产改名当新模型。

## 已有实际证据

- 新资产GPU0真实PhysX加载：31刚体、30坐标、6闭链；质量/COM与新JSON差0；8物理步；App.close桥、父waitRC0、全部自有子进程wait、私锁释放。只是nominal资产导入，不是技能毕业。
- RM70 fresh80新模型full D0–D7构造和参数读回通过：35/38观测、6动作，24控制/192物理/48反馈，dt2.5ms、策略50Hz、反馈100Hz、closure/mimic各.01。真实MildDR参数audit通过，全部getter字段有限。PTopens/actor/optimizer/canonical写均0。它不是2万环境旧checkpoint完整恢复，更不是专家技能通过。
- fullDR80实际结果：`reports/fullDR80_snapshot_20261102_005626.json`；remote job `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_FRESH80_FULLDR_V2_20261102_005108_1793551868560739200`。

## 正在执行

- 新W35 full DR/20k完整恢复/32s SAMEUID无优化器评测已派发。
- remote job `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_FULLDR_EVAL_20261102_010506_1793552706521956800`。
- parent PID1418833，worker1418842；一次source byte/hash/decode，源2d0bc7b8/iter32481/Adam651260/原LR，禁止optimizer/update；target2c/bae。
- 快照 `reports/W35_eval_snapshot_20261102_011546.json` 已有实际20k完整恢复PASS：actor/critic/STD/17Adam/源LR exact，原D0-D7恢复后ONE fresh reset，source1物理byteopen/1decode；新nominal m/I/COM缓存保留且35/38/6已验。原24-control native门槛通过，仍无32s最终技能结论。GPU0实际进程运行，GPU1当次空闲。
- 正在运行的元数据terminal watcher本地job `pwsh-7b1503bf4a7d4993`，只45s一次stat/读本新任务FINAL或父退出回执，绝不重复执行/读模型；后续收job_output并snapshot完整事实。
- 调用 `snapshot_w35_eval.py` 读取本任务receipt与日志尾，不打开源模型/raw轨迹。若失败另建新purpose/source版本，保留全部原始错误，不重放旧once。
- 单一子代理32baa298-9c0c-4efb-b8ee-1cef9f2cbd3d已交付原E0专属新资产派生 `staged_sources/E0_MOD4V1_SOURCE_FINAL`（22文件/15py，CPU_STATIC_ONLY）。实际入口原89D `train_chassis_pd_resume_ppo.py`，不是qualified240的H1混合jump或W35/RM70。source remote为 `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0/adaptation/final_valid_update82.pt`，原随机133/height筛74 bank保留；new index SHA b9c261027cea3d89df239186de64b39880c1f8bd0a39e1fbd4590d783e5e9943，worker ef2b3b4b0e8d410982376f7ca1ae279a86654a1648c26b984e4735938b0c4b57。目标SDK/完整恢复/真实评测尚未执行。勿新增第二子代理。

## 源码

- W35采用 `staged_sources/W35_MOD4V1_SOURCE_V2_FINAL`；旧V1/pre-final V2全部保留。9py静态/输入输出SHA已核，仅CPU_STATIC_ONLY。
- EVAL新源实际采用 `staged_sources/W35_MOD4V1_EVAL_V3`，由父从旧Full32协议派生：分开原PT root与新runtime root，移除旧2mm/legacy guard，显式10mm+原SI接口，新FreshGuard包原ONE reset；仍未宣告完整恢复通过。
- 原恢复链本身从新constructor取m/I/COM，并无已知“旧PT覆盖默认质量”bug；sidecar只是新身份与缓存检查，别创造旧版bug。
- D6只是gas damping，不是全部关节摩擦覆盖。候选新CAD整组回填仍未完成。

## 资源和预算

- 72有两张4090：GPU0 `GPU-16828f91-2b45-b646-8dc0-9481138e2842`；GPU1 `GPU-c27eecbd-6838-7290-1cd2-37e34522213d`。占用依据fresh compute-apps/原private GPU锁和调度，不以低利用率当空闲。另一旧Linux节点SSH超时，本机5070Ti不是可用空闲4090。
- 唯一canonical `/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json`；generation `MOD4_SINGLE_WRITER72_20261026`；原finite授权2268000s，23:17余额386875.298s为历史快照，不是当前GO；strict reserve86412.861s。
- 原canonical已有约17MB，不要本地复制/新建/改预算；用原位摘要reader。学习必须原single-writer/两fcntl/实际Task-GO、有限3900/save3600/headroom300、完整save-close-wait后回放独评再决定继续；新无人干预目标不新增预算/不热改旧任务。
- 本轮native和no-optimizer评测无canonical写或生产GO。未来PPO不得并立第二writer。

## Git与待补清单

- 第一阶段盘点/auth/native0PT/全部前置失败、sidecar及根AGENTS协调事实已推私库独立分支 `mod4v1-experts-fulldr-rm70`：commit `0b0073f1f383bfe3bc48badf0b24041f6105def3`，tag `trial-20261102-mod4v1-experts-native-phase1`，远端branch/tag/peeled已核；main未推。
- 第二阶段已推并核远端：commit `2bdd2ee975efa97892275e9332138a783ef796c3`，tag `trial-20261102-mod4v1-fulldr-w35-e0-phase2`（tag object `edd0ad4be0fe4ec8d9d3741c633ea79281c72c95`），branch `mod4v1-experts-fulldr-rm70`，main未改。180source entries/182text files包含W35/E0各版本源、fresh80安装/Kit错误/actualDR与20k实际恢复、所有静态/reader错误；捕获时尚在跑的eval不冒称完成。
- 待第三阶段追加：此后W35最终32s/错误/终止watcher与决策、E0实际target执行/资源等待/错误、E2/E3新增源/读者检查、最新注册表和本进度；任何权重/raw/USD只索引。
- 不为Git重跑实验、复制canonical、改已消费once。大权重/USD/NPZ/raw只索引真实路径大小SHA；凭据不输出不归档。

## 下一步顺序

1. 读取正在运行的W35新模型评测结果；必要仅修真实SDK/恢复错误，保留source/version/purpose/错误，不扩大数值门槛。
2. 若执行完成，审原SAMEUID/完整32s/telemetry/exposure/技能条件，不把执行通过当技能毕业。按结果决定是否PPO适配。
3. 接收并验证E0专属新源，GPU1可用时安排相同新模型fullDR/原任务保留验证；继而E2/E3，legacy H1/curb/slope继续join精确producer，不悄悄排除。
4. 任何学习用新unused Task/Ready/GO和原唯一owner，2卡可并行但不得第二账本/新预算，完成每轮保存后立即回放独评。
5. 第二阶段完成后将所有已保存源/报告/错误追加Git并核远端，再更新注册表，目标尚未完成，保持goal active。
