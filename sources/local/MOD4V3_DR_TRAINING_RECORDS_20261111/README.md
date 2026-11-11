# MOD4 DR 阶段配方与模型归档（2026-11-11）

长期入口：[阶段总表](../../../docs/DR_TRAINING_INDEX_20261111.md)；[取回与续训方法](../../../docs/DR_TRAINING_RESUME_20261111.md)。

- [MODELS.md](MODELS.md)：61份完整PPO检查点及全部SHA，点模型ID直接取Git内`.pt`。
- [MODEL_REGISTRY.json](MODEL_REGISTRY.json)：17阶段/分支、实际父子关系、保留/失败模型、全部原路径、配方、源commit和原tag。
- `weights/`：59份新增`.pt`实体。另两份Stage4/5沿用原归档路径，索引直接指向已有实体。所有文件均为普通Git二进制blob。
- [COLLECTED_EVIDENCE_INDEX.json](COLLECTED_EVIDENCE_INDEX.json)：本次补收的原始记录、脚本、日志和配方的路径/字节/SHA；不含凭据。
- `early_evidence/`、`early_launchers/`、`early_logs/`、`early_replays/`：旧动作延迟6/6b/6c、7/7a、Stage3续段、Stage2回取等实际收据和当时脚本/回放；没有FINAL的运行不补造FINAL。
- `historical_runtime/`：当时PLAN、固定trained_agent、runner配置和source路径；共享依赖来自目标机既有安装，不是新仿真安装包。
- `selected_recipes/`：原输出倍率020m和推扰020m本地RECIPE的逐字副本；Step7主冻结配方仍用原冻结目录RECIPE，材质配方用原PLAN及实际STARTUP。
- [LOCAL_MODEL_READBACK.json](LOCAL_MODEL_READBACK.json)、[SUPPLEMENTAL_MODEL_READBACK.json](SUPPLEMENTAL_MODEL_READBACK.json)：本机模型SHA/大小/iteration实读。
- [REMOTE_RETAINED_MODEL_READBACK.json](REMOTE_RETAINED_MODEL_READBACK.json)：目标机四份保留模型SHA/大小/0444读回。
- [EXTERNAL_DEPENDENCIES.json](EXTERNAL_DEPENDENCIES.json)：实际模型package、resetbank和pinned runtime依赖索引；本次未改plant。

当前累计接训候选`push_020m`，SHA`b3eec7bae3045b24a95ea7cd2940a3e1f0b062841cc47ab1785a627bea36408a`；原主冻结`mass_040m`继续保留。用户确认Step6晋升冻结的状态不变，旧文件名不替代明确身份。

本次用户明确要求权重本体Git保存，覆盖旧路径索引规则在本次归档中的适用范围。没有开训练、重跑评测、改奖励或solver；旧失败和报告未覆盖。新归档标签`trial-20261111-dr-training-catalog-pt-01`。


后续追加：剩余DR合并轮已完成，新增9份完整PT在独立轮目录，总模型索引现为70份。本轮诊断候选remaining_010m、综合备用remaining_030m；当前已接受范围接续仍为push020m，原主冻结保持；[结果](../MOD4V3_STEP7_REMAINING_DR_20261111/FINAL_REPORT.md)、[精确配方](../MOD4V3_STEP7_REMAINING_DR_20261111/evidence/SELECTED_RECIPE.json)。初次档案tag和原始61份历史说明不回写。


第二轮更新：fixed20%名义/80%完整DR的40分钟轮已完成，同源配对与全部完整PT已归档。保留mixed2_020m（iter22502，SHA`15775671f430cda69b1f268a230d85c5d1a74878760d26625afefb759e792c20`）供检查；结果与使用范围见`sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/FINAL_REPORT.md`，原已接受候选/主冻结未自动替换。总索引现为19阶段/分支、79份检查点。


2026-11-11回放复核：同一mixed2_020m在MuJoCo名义超速、PhysX名义欠速；0/5ms复测保留方向，原训练actor观测与paired包装逐帧最大差0。尚无新确认的输入回放bug，物理/执行差异未定位，不能只凭跨引擎差异定为策略退化。完整DR同时有欠速和超速样本。详见`sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/replay_environment_check/REPORT.md`；未启动第三轮训练。


2026-11-11新授权：从与第二轮相同的remaining_010m父检查点（iter22265，978994b2…）单开40分钟，将超速/欠速对称平方惩罚−0.5e²→−1.0e²。其余沿用20%名义/80%完整DR，5分钟保存并检查。独立源与计划：`sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/README.md`，不覆盖旧轮或冻结模型。


双侧平方惩罚加倍实验已完成2400.870s，−1.0e²，其余同第二轮。保留square1_030m（iter22618，SHA`d5e176401c20dd1b88a74003f7d4993aadc9a9cda301f042953de08fb6108851`）供检查；原始结果见`sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/FINAL_REPORT.md`，全部PT实体归档。总20阶段/分支、88完整PT；不自动覆盖原冻结或开下一轮。


2026-11-11 R0首轮完成：2405.700s，保留rough_r0_020m（iter22785，SHA`64affb5794f5518f2b84611ab7d3904aef95b7e1ea660e1efd87820102cc14d6`）为R0实验候选；完整DR level0浅地形越障119→120/120，Flat正式44→40/60。此为同批诊断，不代表Rough全课程毕业；原Flat主冻结保留，R1未启动。报告与全PT见`sources/local/MOD4V3_ROUGH_R0_20261111/FINAL_REPORT.md`，当前总21阶段/分支、97完整PT。


追加Flat平方项1.5实验：父square1_030m，完整DR及20%名义参数，40min/5min检查点。本轮完整PT保存在`../MOD4V3_FLAT_SQUARE15_20261111/weights/`；结果待评测，原冻结与R0候选保留。


2026-11-11用户中途要求下个检查点切Rough：Flat平方项1.5段在020m/iter22856完整保存后结束，SHA`a5102af62938f6bf472855edba34c5f10efce061eecaeb3aebee34815fe7cf87`，已接续`MOD4V3_ROUGH_R0_SQUARE15_20261111`的R0余下20min。保留−1.5e²/fullDR/20%名义/20%平地；本轮预算按Flat20＋Rough20分配。新结果待同批PhysX配对，原冻结保持。


2026-11-11 Flat1.5→RoughR0接续已结束：Flat1204.923s后按用户要求在020m完整保存点切Rough，Rough再1201.085s，均每5min完整PT保存。保留Flat020m（iter22856，a5102af6…）回退，Rough010m（iter22941，ece8c411…）作实验候选；同批fullDR前进MAE分别0.12165/0.13866，正式44/60(reset0)/41/60(reset0)，Rough010m额外2.7诊断3reset如实保留。R0浅地形均120/120，未测出新增越障能力，Rough训练累计numerical1。原主冻结保留，未自动R1或追加训练。两段10份不同字节完整PT在各自weights目录，候选配方/本机目标机只读存档已完成；[最终报告](../MOD4V3_ROUGH_R0_SQUARE15_20261111/FINAL_REPORT.md)。总索引23阶段、107完整PT。


2026-11-11 R1首轮40分钟已获用户授权并启动：父Flat1.5_020m/iter22856/a5102af6…，新增中级正反阶梯及完整计划难度范围；Rough低速起步课程，平地组原技能继续；−1.5e²/fullDR/PPO/2.5ms/TGS32/4/2mm保留，每5min完整PT。训练和真实失败计数见[本轮记录](../MOD4V3_ROUGH_R1_20261111/README.md)。未自动R2。


2026-11-11偏速处理切段：用户要求加强速度平方惩罚。010m完整检查点iter22925/SHA959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022已核验保存，旧训练SIGINT退出，无FINAL/SAFE_CLOSED，不能写成正常40分钟完成。原段总消耗756.803s（010m后未保存更新也计入），接续−2.0e²用1643s，仍为同一轮40min；新目录MOD4V3_ROUGH_R1_SQUARE2_20261111。保存R1等级、地形分组、偏移和累计计数，重新物理episode。
