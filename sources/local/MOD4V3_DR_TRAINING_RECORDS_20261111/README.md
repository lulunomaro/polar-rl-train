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
