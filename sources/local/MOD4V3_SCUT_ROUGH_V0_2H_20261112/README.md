# SCUT Rough-v0统一科目：两小时已完成（2026-11-12）

用户授权的统一科目PPO已完成 **7206.137秒**，每5分钟完整保存检查，26份完整训练PT本体/25种不同字节均保留。8组正式PhysX同批对照已完成，当前没有训练或验收在运行。

**综合接续继续使用R1第二轮005m，未晋升本轮100m/120m。** 100m是本轮已做PhysX细评的实验候选，不能只凭名义MuJoCo60/60把它当成综合最优；具体差异见[模型选择](DECISION.md)。原Step6/Step7冻结、原实车调试包保持原身份。

| 用途 | 文件 | iteration | SHA256 |
|---|---|---:|---|
| 综合继续父 | [R1第二轮005m](../MOD4V3_ROUGH_R1_ROUND2_20261111/weights/model_005m.pt) |22959|`0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f`|
| 本轮实验候选，未晋升 | [100m完整PPO](weights/model_100m.pt) |23665|`001028396205e7d44d69ac5af36cdbb638cc26b97daeea29439f84952a58f6e9`|
| 末点，未晋升 | [120m完整PPO](weights/model_120m.pt) |23807|`87537baddfbecef424db219e7b86ea140ec4e767c67668b8c7a2cc0849995c09`|

统一课程：保存的SCUT rough_rotation_stair全部9地形族、10难度行并行，包含浅栅格/坡面/正反小阶与中阶/随机起伏/平地，同时训练行进、小陀螺与组合指令；没有R0/R1分段准入或能力毕业线。14列扩成70列分散4096出生点。保留当前完整DR、20%名义/20%平地独立交叉、2.2m/s上限、35/78/6、2.5/10/20ms、TGS32/4、2mm单env保护、−1.5e²和指数1.2；无云台/air reset/airborne新增。

- [实际完整配方](EFFECTIVE_RECIPE.json)、[训练方法与入口](TRAINING_RECIPE.md)、[原始启动PLAN](PLAN.json)；PLAN继承描述字段的订正在实际配方中，CLI/STARTUP反映实际运行。
- [最终报告](FINAL_REPORT.md)、[PhysX同批原表](PAIRED_COMPARISON.md)、[全部24个保存点MuJoCo回放](CHECKPOINT_COMPARISON.md)。两引擎数据分开，首次穿越、首段旋转和Flat窗口统计分开。
- [全部26个完整PT索引](evidence/MODEL_ARCHIVE_INDEX.json)、[实际保存时刻/回放明细](evidence/CHECKPOINT_INVENTORY.json)、[目标机源校核](evidence/EXECUTED_SOURCE_VERIFIED.json)。不是只保存路径或LFS指针。
- [精确接续记录](NEXT_RECOMMENDATION.json)、[同步回执](SYNC_REPORT.md)。新预算或下一课程没有自动启动。

复现本轮以本目录support/和launch.py为入口：4096env/LR3e-5 fixed/clip0.1/epochs3/rollout24/seed66，父为上述R1点，--kind train --seconds7200。完整参数及目标机Python/package/support路径见实际配方。独立新试验使用新job名和独立记录目录；显式--checkpoint可选已保存PT，恢复同4096env的统一十级状态时需保留本目录环境实现。模型没有实时求解器状态，物理episode重新开始。

## 逐地形完成报告与后续选择（2026-11-12补充）

[行走与小陀螺逐地形完成报告](COURSE_COMPLETION_REPORT.md)整理原始同批成绩。后续用户认可本轮已有能力，指定继续推进Rough-v1；新实验采用本轮100m作为完整PPO父，不回退R1。原轮末测量、未晋升结论及原实车包保留。
