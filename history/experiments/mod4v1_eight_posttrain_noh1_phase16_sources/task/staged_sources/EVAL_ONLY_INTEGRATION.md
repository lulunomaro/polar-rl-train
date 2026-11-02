# W35 新MOD4v1入口的无优化器 fullDR 回放：源码核查

**结论：可共用新 trainer 的 build_env / 原完整 fullrestore / ONE fresh reset；不需要另一套学习框架。**这里只列需另建新 EVAL_ONLY source 的最少派生点，没有读取源 PT、创建评测 Task、执行 SDK 或启动回放。

## 已有机制（不是新实验结果）

原入口：[evaluate_latest32481_full32s_ROOT_ONLY_once.py](<C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/W35_LATEST32481_FULL32S_AUTHORITY240_SOURCE_V2_20261101/evaluate_latest32481_full32s_ROOT_ONLY_once.py>)。

- 59–85行：runpy载 trainer，但在调用其 main 前替换 `rescue_training.learn=work`；`actor.eval()/critic.eval()`，`alg.update` 与 `optimizer.step` 改为抛错。
- 97–110行：20k环境、最多1600控制步×20ms=32s；每控制步一次 mean actor 和一次 vec.step；原D0–D7/命令/RNG完整恢复。原GPU runtime source-cache一次物理byte-open/hash/decode，不是本次子任务读PT。
- 75–77、110行：源iteration32481、17Adam651260、LR及actor/critic/STD/optimizer在前后不变；旧完整helper仍负责保存态/新回合恢复证明。
- 66、83、88–91、100–118行：RM70Intervals227挂自然command/episode UID及pre-reset terminal；保留全部partial/failure prefixes，不挑片段或以32s窗口冒称技能毕业。

## 最少派生点（父另建新unused版本）

建议新kind标识符：`MOD4V1_W35_32481_FULL32S_10MM_SAMEUID_EVAL_ONLY_V1`，这里只是命名建议，不是已签发任务。

1. **拆开 source ROOT 与新 runtime ROOT。**原30–31行把 `qualified_latest227D_job_root/runtime` 与原 `production/model_final_complete.pt` 绑在一起。原PT仍钉227D/2d0…/17619333/32481/651260/77/LR.0002562890625000001；runtime切为 [V2_FINAL新源](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/staged_sources/W35_MOD4V1_SOURCE_V2_FINAL/README.md>)所在的新job，不能把原PT路径谎报为新job产物。
2. 原38–44行恢复旧RM环境后，在任何task import前绑定新asset目录2c/bae。`MOD4V1_ASSET_DIR`供新trainer；`MOD4_NEW208_JOB_ROOT`须指含新 `MOD4V1_ASSET_DIFF.json` 的新runtime job；CAD/root依赖及安装receipt要真实可用。评测输出job可独立，但这些路径不能混淆。
3. 原53行入口改为新 `runtime/isaac/mod4/train_mod4v1_w35.py` 并绑定其实际SHA；不再硬验旧train_full214 SHA。
4. **不调用旧 guard_latest32。**它24–38行硬断言closure2mm/旧mimic.05，且44–46行要求config214_training模块名。新trainer已经显式在constructor前把closure/mimic均设.01，保存旧cfg仅作历史，且FreshDRNominalGuard包住原ONE reset。新评测核实际cfg/新guard receipt，不伪造旧projection pass。
5. 原72/95/106/115/117行所有closure `.002` 断言/2mm条件描述和receipt值改为 `.01`/10mm；mimic `.01`保持。新body/COM/I身份由新asset compat和父已完成的nominal Native0PT加实际fullrestore/readback绑定，不能拿旧517/bce四scalar asset pass代替。
6. 原contract_latest32及父caller里的固定ACTIVE240/PID/GPU/old GO快照需新purpose绑定**当前真实**known-owner/只读canonical/本次GPU私锁+原shared-finite lease与资源。保留EVAL_ONLY、`no_new_learning_or_GO`和无canonical写；不能用训练worker的生产GO假跑评测，也不复用旧已消费caller/once。
7. 原work callback保留 `actor.eval/critic.eval/inference_mode`、两个优化入口禁用、首尾whole-core+17Adam不变、20k不slice/repeat、1600control上限、完整原reward/command/clock。原追加迭代参数仅是generic trainer参数，不进入learning callback。
8. 新FreshGuard/原D1–D7 helper startup receipts按new source/asset/run身份检查；可复用新worker的八类startup receipt集合。仅复用已自然计算的obs核35/38，勿额外计算传感器。新asset参数getter/原audit验证不是全部DR动态能力毕业证明。
9. observer/writer/decoder227的lossless positional schema与同UID前缀逻辑可原样复用并核SHA；在新Task/场景元数据记录asset2c/bae/10mm，不擅自修改其列顺序/编码或把旧active plant标签冒充新资产。

## 报告范围

本说明属于SOURCE/CPU核查。父已报告GPU0 nominal Native0PT实测成功，这仅证明新资产名义导入、所报告质量COM及8个physics steps等探针范围，不外推动态闭链稳定性；本子任务不把它扩成完整D0–D7专家适配或技能验收。D6仍为原gas damping，不是全部joint friction。

原health代码把closure列ordinary，不因有限closure peak全局停；V2_FINAL只把旧2mm报告label同步成当前cfg的10mm及历史诊断名，原stop逻辑不变。Generic trainer旧mode文字如为train，须在新EVAL Task/结果中明确实际execution_scope=EVAL_ONLY_NO_OPTIMIZER，不能当学习记录。

评测真正闭合后，再按原完整技能/UID/失败前缀标准独立判断是否微调；预算/owner/private lease/保存退出/回放评测/Git由父统一协调。本说明没有新增评测器、Task/GO或调度器。
