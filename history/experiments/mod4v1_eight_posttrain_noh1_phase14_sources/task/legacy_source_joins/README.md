# 历史 H1 / CURB20 / SLOPE5 源谱系 join

**本轮仅本地源/已保存元数据；不代表新 MOD4v1 适配完成。** PT/NPZ/USD原件未打开、stat、复哈希或导入；未SSH/SDK/GPU/预算操作，未建立运行根、Ready/GO，也未改actor或Recipe。全部检查点路径/大小/SHA均引用原producer报告。

## 分别保留的变体

|Alias|来源SHA前缀|原policy/physics/feedback|原证据与后续状态|
|---|---|---|---|
|H1 normal PPO86B138|0c1edb96|100Hz / 2.5ms / 100Hz|原20k完整PPO save；非native H1、非当前student。后来typed为71db。|
|H1 typed400N50|71db5543|50Hz / 2.5ms / 100Hz|后续真实targetCPU + CUDA20k fullrestore/native24：24控制/192物理/48反馈，零更新；不是新2c/bae资产证据，也不是技能毕业。|
|CURB133 review-only|df0c141d|100Hz / 2.5ms / 100Hz|显式仅冻结审阅；上行22/27，未选qualified。保留原false。|
|CURB141 accepted scope|7b70032f|100Hz / 2.5ms / 100Hz|显式冻结原20mm/150mm镜像scope，上/下27/27；不是完整RM/MoE毕业。独立424源包见补充。|
|CURB shared878 protected|26896794|100Hz / 2.5ms / 100Hz|后续protected参考，原20mm上/下27/27；17Adam660400。三个rank仅一个CURB actor，不算三个专家。|
|CURB independent113 frozen|3d2b0b6d|100Hz / 2.5ms / 100Hz|G3祖源另开独立分支，完整close；26/27上行、27/27下行后冻结。不是从protected878继续训练。|
|SLOPE135 old5° frozen|24b18846|100Hz / 2.5ms / 100Hz|显式冻结5°/2m镜像scope。8°/10°只是同一5°存档冻结评测，不是新训练。|
|SLOPE independent50 frozen|aab6fb4b|100Hz / 2.5ms / 100Hz|确由24b/Adam642980继承，50更新后完整close，SHA/大小/Adam643980和后续frozen声明齐备；不借旧scope毕业。|

旧E1各变体的3500N/m gas刚度/700N名义力、3Ns/m gas damping、D0–D7、35/38/6/learnedSTD/原17Adam事实原样保留；D6不扩称全关节摩擦。TGS32/4。原20k histories/queues不切片、不重建。

## 入口

- [逐变体机器行](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/legacy_source_joins/LEGACY_FROZEN_VARIANT_ROWS_v1.json>)：每行alias/scope/SHA/后续producer/selection证据、clock、helpers、包路径、UNKNOWN。
- [H1 join](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/legacy_source_joins/H1_NORMAL_PPO86B_SOURCE_JOIN_v1.json>)：0c→71db typed、451→453输入、50Hz/phase/feedback overlay和后续真实target进程/报告SHA。
- [CURB20 join](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/legacy_source_joins/E1_CURB20_SOURCE_JOIN_v1.json>)；[CURB141精确原包补充](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/legacy_source_joins/CURB141_EXACT_RUNTIME_PACKAGE_SUPPLEMENT_v1.json>)：完整direction→entry→原D0–D7/terrain/retention恢复链，19个实际源码SHA核对无差异。此精确loader优先于主join中宽泛base-entry标签。
- [SLOPE5 join](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/legacy_source_joins/E1_SLOPE5_SOURCE_JOIN_v1.json>)：旧24b完整404源与新独立50分开，原warmstart3c97不冒称SLOPE final。
- [84份原文本/报告SHA](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/legacy_source_joins/TEXT_SOURCE_AND_REPORT_SHA_INDEX_v1.json>)；[补充文本SHA](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/legacy_source_joins/SUPPLEMENT_TEXT_SHA_INDEX_v1.json>)；[读者错误保留](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/legacy_source_joins/METADATA_READER_ERRORS_v1.json>)。

## 未闭合项

1. 没有按maxiter、rank或某个目录latest擅自选当前迁移母源。各独立frozen变体均保留；全历史/current-selection闭合标志为false。
2. **旧E1→50Hz/400N** 与 **旧资产→新2c/bae增强资产** 是两层独立迁移；这里无其实际证据，均pending。H1已有的是旧400N50目标准入，不跨层继承到新MOD4v1。
3. 保存报告未给出的精确LR、stored iteration、Adam字段和后续producer明确UNKNOWN；未用算术、最大更新或开PT补齐。
4. 仅源/元数据权限仍有效；本轮没有训练或执行迁移。父任务新W35独评与原once/raw未触碰。

## 归档

全部新JSON、两份仅元数据builder、两份原console与本索引待父任务追加归档；子任务无Git commit/push。旧报告/原false/raw不覆盖。最终交付文件文本SHA见父交接索引。
