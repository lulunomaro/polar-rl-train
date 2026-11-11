# 从 Git 取回模型并继续 DR 训练

2026-11-12 当前：**R2首轮40分钟及配对评测已完成**。5–10cm低落高能力已具备；综合保留r1round2_005m（iter22959/SHA0dcc15f5…），本轮R2新权重未晋升，005m保留实验备选；40m不作默认接续。28阶段/138完整PT文件索引，R2的10个PT实体均保留。[结果与选择](../sources/local/MOD4V3_ROUGH_R2_20261112/DECISION.md)。


2026-11-11的R1第二轮记录：当时训练及全部同批评测已完成；本轮较均衡候选r1round2_005m，10m为最高实测L3穿越对照。最新结果见文末更新与MOD4V3_ROUGH_R1_ROUND2_20261111/DECISION.md；旧阶段记录保留。

日期2026-11-11。先看 [阶段总表](DR_TRAINING_INDEX_20261111.md) 和 [精确索引](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODEL_REGISTRY.json)。本页是后续操作说明；本次整理没有执行下面的训练命令。

追加更新：剩余DR合并轮已完成，查本轮完整DR配方与前进诊断候选，从 **remaining_010m** 查起，Git路径`sources/local/MOD4V3_STEP7_REMAINING_DR_20261111/weights/model_010m.pt`，iter22265，SHA`978994b2614f4454f96bfd0ac264f00cbe3ffd219a5372487c558435503dbd15`；配套使用`MOD4V3_STEP7_REMAINING_DR_20261111/support`、PLAN、实际STARTUP/PPO_EFFECTIVE/RESTORE和RECIPE_CLARIFICATION。完整记录见[本轮报告](../sources/local/MOD4V3_STEP7_REMAINING_DR_20261111/FINAL_REPORT.md)，原push020仍作确切父与回退。本页下方旧示例绑定初次目录，不能直接作为新合并DR运行命令。新父路径和profile必须一起更新。

## 1. 取哪份 `.pt`

当前累计 DR 接训候选：

```text
模型ID: push_020m
Git内路径: sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/weights/push_020m.pt
iteration: 22141
SHA256: b3eec7bae3045b24a95ea7cd2940a3e1f0b062841cc47ab1785a627bea36408a
本机保留副本: D:\claude2\fangzhen\frozen_models\step7_velocity_push_020m_candidate_20261111\model_020m.pt
目标机保留副本: /mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107/frozen/step7_velocity_push_020m_candidate_20261111/model_020m.pt
原训练检查点: /mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107/step7_velocity_push_20261111_r1/train040m_velocity_push_r1/model_020m.pt
```

原主冻结对照：`mass_040m.pt`，iter21754，SHA `23c112b16e9629215c7265124925daaf0f9b6bbbb62be61689c714ba1fc7a772`。不要用推扰40m/final代替选中的20m；40m后段已掉速。旧Step6冻结状态保持。

本档案使用普通Git完整二进制，61个模型均有实体，**无需Git LFS**。默认私有仓库使用用户已有Git登录。标签固定为`trial-20261111-dr-training-catalog-pt-01`。

在已有checkout中取回（如果有稀疏检出）：

```powershell
git -c http.proxy=http://127.0.0.1:7897 fetch origin tag trial-20261111-dr-training-catalog-pt-01
git restore --source=trial-20261111-dr-training-catalog-pt-01 --worktree --ignore-skip-worktree-bits -- sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/weights/push_020m.pt
Get-FileHash -Algorithm SHA256 -LiteralPath sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/weights/push_020m.pt
```

`restore`只针对所需归档模型文件；不要用它覆盖正在修改的训练源代码。其它阶段从 [模型表](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/MODELS.md) 选路径。普通clone也会得到这些模型实体；在另一台主机上配置其可用代理地址，不假设本机127.0.0.1端口能从目标机访问。

## 2. 必须配套哪套源代码

推扰候选对应的是 [MOD4V3_STEP7_VELOCITY_PUSH_20261111](../sources/local/MOD4V3_STEP7_VELOCITY_PUSH_20261111/)，包括：

- `support/`：实际训练环境、35D/6D/78D接口、修复的DR/时序/奖励实现。
- `PLAN.json`、`launch.py`：固定依赖、父权重、profile与环境变量。
- `evidence/train040m_velocity_push_r1_STARTUP.json`、`..._PPO_EFFECTIVE.json`、`..._RESTORE.json`：实际运行的范围、PPO参数和恢复范围。
- `CHECKPOINT_EVAL_TEMPLATE.json`、`replay_delay_diagnostic.py`所在的延迟诊断目录：五分钟本机MuJoCo回放。
- `checkpoint_velocity_push_replay.py`、`FINAL_MODELS_TEMPLATE.json`：末轮同源PhysX受扰配对。
- [已选模型配方逐字副本](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/selected_recipes/step7_velocity_push_020m_candidate_20261111/RECIPE.json)、[补充澄清](../sources/local/MOD4V3_STEP7_VELOCITY_PUSH_20261111/evidence/RECIPE_CLARIFICATION.json)：一起读，不只看文件名。

不要用旧`MOD4V3_SCUT_INCREMENTAL_DR_20261109/support`工作目录中的未提交实验改动替代这一冻结快照。原目录历史source与当前实际文件可能不同，精确版本按tag/commit取回。

目标机既有依赖根目录：

```text
ROOT=/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107
PYTHON=/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python
runtime: ROOT/runtime
shared_package: ROOT/dependencies/shared
package: ROOT/package
source_paths: ROOT/SOURCE_PATHS_LOCAL.json
reset_bank: ROOT/dependencies/reset_bank.json
```

实际plant、resetbank、pinned脚本的路径/大小/SHA见 [EXTERNAL_DEPENDENCIES.json](../sources/local/MOD4V3_DR_TRAINING_RECORDS_20261111/EXTERNAL_DEPENDENCIES.json)。本次Git包含训练support和checkpoint，不是完整IsaacSim运行时安装包；搬到新主机时应迁移已有依赖/plant，按记录核身份，不能通用导入重建资产再声称兼容旧权重。无需为了本次归档重新做物理验收。

## 3. 续训会恢复什么

使用原`flat_velocity_push`profile与完整`.pt`，原`scut_flat_train.py`的非rough分支执行：

1. 按预期SHA读取父模型，严格恢复actor、critic、std和Adam。
2. 恢复global Python/NumPy/CPU/CUDA RNG及reset generator；保留iteration计数。
3. 新建物理episode，重新调用当前命令/DR采样；不把保存的旧reward tensors/命令当作新环境状态恢复。
4. 显式覆盖学习率fixed3e-5、clip0.1、3epochs；其它PPO参数沿用实际配方。

D5/D10历史checkpoint缺少额外材质样本及推扰timer/count/delta字段，见 [状态范围说明](../sources/local/MOD4V3_STEP7_VELOCITY_PUSH_20261111/evidence/CHECKPOINT_STATE_SCOPE.json)。质量/输出倍率相关保存字段及完整PPO存在，但恢复函数也不承诺逐物理状态回灌；这条路线始终是fresh physical episode。启动DR seed相同可重建相同startup分布，不等于精确恢复停止瞬间。缺失字段的未来补丁单独保存于原evidence，历史代码没有热改。

旧rough_v0是另一恢复分支：只载actor，重建critic/optimizer/RNG。当前未启动Rough，不能把本页完整PPO续训方法直接套成rough毕业或直接改profile丢失累计DR。

## 4. 后续一轮的准备方式

准备一个全新的运行目录，复制选定阶段的support、PLAN、launcher和对应检查/回放脚本；原冻结目录和旧run不覆盖。将Git中的父`.pt`复制到目标机新目录或继续引用上面的只读保留副本，核完整SHA。只接入本轮已经选定的DR变化项，累计保留当前延迟、质量、输出倍率、材质、推扰及其它轻量DR。

新的PLAN中至少明确这些字段：

```json
{
  "support": "<NEW_RUN_ROOT>/support",
  "parent": "<父.pt实际绝对路径>",
  "parent_sha256": "b3eec7bae3045b24a95ea7cd2940a3e1f0b062841cc47ab1785a627bea36408a",
  "training_round": {
    "job": "<全新job名>",
    "seconds": 2400,
    "num_envs": 4096,
    "checkpoint_interval_seconds": 300,
    "inspection_interval_seconds": 300,
    "learning_rate": 0.00003,
    "schedule": "fixed",
    "clip_param": 0.1,
    "num_learning_epochs": 3
  }
}
```

`root/python/runtime/shared_package/package/source_paths/reset_bank`对应同一目标安装；搬目录时逐项改真实路径。`training_round`其它继承字段、实际本轮新增DR、旧/新父关系也要写明。复制旧PLAN而未改`support`会从旧位置导入代码；复制旧launcher不传checkpoint会继续取旧的材质010m父，不会自动识别本轮最优权重。

完成上述准备后，在新目录执行的原launcher形式为：

```bash
/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -B -u <NEW_RUN_ROOT>/launch.py <NEW_JOB_NAME>   --kind train --seconds 2400 --num-envs 4096 --learning-rate 0.00003   --checkpoint /mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107/frozen/step7_velocity_push_020m_candidate_20261111/model_020m.pt
```

这是未来启动模板，本次没有执行。新DR若新增profile，应同步新run内factory/launcher/PLAN，按当前任务核实际范围；不能只改记录而让执行仍是旧profile。

原launcher已有compute owner检查与拒绝复用job保护。正常一轮40min、300s完整保存并检查，选择最好的已评测检查点；不因为最后一份叫`final`就覆盖主冻结。

## 5. 运行期间与轮末怎样查

每5min：检查`PERIODIC_005M.json`等的实际path/iteration/SHA和`.pt`一致，保存`LATEST_PROGRESS`及done计数，下载完整checkpoint；按原模板做MuJoCo名义7任务×10初态CPU回放。名义过冲与真实DR欠速分开记录。原`monitor_round.py`是当轮路径固定脚本，后续新轮必须同步其TRIAL/JOB/本地下载目录，不能直接运行旧脚本重查旧轮。

轮末：用相同初态和相同DR样本对比父权重、主冻结以及本轮各检查点。材质/质量/倍率协议是300策略步、末120统计；速度推扰协议是600步=12s、6s一次同增量推扰，3.6～5.98s为推扰前段、8～12s为恢复后段，恢复定义为第一次连续0.5s回到原任务误差范围。每env的正式任务reset与额外2.7诊断reset分开记。

跟踪/高度沿用原任务误差判据；闭链2mm是单环境episode reset，不是单次峰值整批停训。保持原MOD4闭链与电机包络：腿40/53.333/16.755；轮5.7759/28.185/55.3557。导出动作顺序仍为left_crank、left_hip、right_crank、right_hip、left_wheel_spin、right_wheel_spin。

新一轮结束后保留实际父SHA、每5min的完整PT、STARTUP/RESTORE/PPO_EFFECTIVE/FINAL/SAFE_CLOSED、名义与实际DR报告和选择依据，再在新trial提交；归档不占额外训练预算。Git网络操作走7897代理。凭据不写入仓库。


第二轮更新：fixed20%名义/80%完整DR的40分钟轮已完成，同源配对与全部完整PT已归档。保留mixed2_020m（iter22502，SHA`15775671f430cda69b1f268a230d85c5d1a74878760d26625afefb759e792c20`）供检查；结果与使用范围见`sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/FINAL_REPORT.md`，原已接受候选/主冻结未自动替换。总索引现为19阶段/分支、79份检查点。


2026-11-11回放复核：同一mixed2_020m在MuJoCo名义超速、PhysX名义欠速；0/5ms复测保留方向，原训练actor观测与paired包装逐帧最大差0。尚无新确认的输入回放bug，物理/执行差异未定位，不能只凭跨引擎差异定为策略退化。完整DR同时有欠速和超速样本。详见`sources/local/MOD4V3_STEP7_MIXED_DR_R2_20261111/replay_environment_check/REPORT.md`；未启动第三轮训练。


2026-11-11新授权：从与第二轮相同的remaining_010m父检查点（iter22265，978994b2…）单开40分钟，将超速/欠速对称平方惩罚−0.5e²→−1.0e²。其余沿用20%名义/80%完整DR，5分钟保存并检查。独立源与计划：`sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/README.md`，不覆盖旧轮或冻结模型。


双侧平方惩罚加倍实验已完成2400.870s，−1.0e²，其余同第二轮。保留square1_030m（iter22618，SHA`d5e176401c20dd1b88a74003f7d4993aadc9a9cda301f042953de08fb6108851`）供检查；原始结果见`sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/FINAL_REPORT.md`，全部PT实体归档。总20阶段/分支、88完整PT；不自动覆盖原冻结或开下一轮。


2026-11-11 R0首轮完成：2405.700s，保留rough_r0_020m（iter22785，SHA`64affb5794f5518f2b84611ab7d3904aef95b7e1ea660e1efd87820102cc14d6`）为R0实验候选；完整DR level0浅地形越障119→120/120，Flat正式44→40/60。此为同批诊断，不代表Rough全课程毕业；原Flat主冻结保留，R1未启动。报告与全PT见`sources/local/MOD4V3_ROUGH_R0_20261111/FINAL_REPORT.md`，当前总21阶段/分支、97完整PT。


Flat1.5实验从square1_030m恢复，配套新目录`MOD4V3_FLAT_SQUARE15_20261111/support`、PLAN和实际STARTUP/RESTORE使用。新奖励−1.5e²，当前训练中；R0候选不作为此轮父。新权重未经同批评测不作默认晋升。


2026-11-11用户中途要求下个检查点切Rough：Flat平方项1.5段在020m/iter22856完整保存后结束，SHA`a5102af62938f6bf472855edba34c5f10efce061eecaeb3aebee34815fe7cf87`，已接续`MOD4V3_ROUGH_R0_SQUARE15_20261111`的R0余下20min。保留−1.5e²/fullDR/20%名义/20%平地；本轮预算按Flat20＋Rough20分配。新结果待同批PhysX配对，原冻结保持。


2026-11-11 Flat1.5→RoughR0接续已结束：Flat1204.923s后按用户要求在020m完整保存点切Rough，Rough再1201.085s，均每5min完整PT保存。保留Flat020m（iter22856，a5102af6…）回退，Rough010m（iter22941，ece8c411…）作实验候选；同批fullDR前进MAE分别0.12165/0.13866，正式44/60(reset0)/41/60(reset0)，Rough010m额外2.7诊断3reset如实保留。R0浅地形均120/120，未测出新增越障能力，Rough训练累计numerical1。原主冻结保留，未自动R1或追加训练。两段10份不同字节完整PT在各自weights目录，候选配方/本机目标机只读存档已完成；[最终报告](../sources/local/MOD4V3_ROUGH_R0_SQUARE15_20261111/FINAL_REPORT.md)。总索引23阶段、107完整PT。


2026-11-11 R1首轮40分钟已获用户授权并启动：父Flat1.5_020m/iter22856/a5102af6…，新增中级正反阶梯及完整计划难度范围；Rough低速起步课程，平地组原技能继续；−1.5e²/fullDR/PPO/2.5ms/TGS32/4/2mm保留，每5min完整PT。训练和真实失败计数见[本轮记录](../sources/local/MOD4V3_ROUGH_R1_20261111/PLAN.json)。未自动R2。


2026-11-11偏速处理切段：用户要求加强速度平方惩罚。010m完整检查点iter22925/SHA959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022已核验保存，旧训练SIGINT退出，无FINAL/SAFE_CLOSED，不能写成正常40分钟完成。原段总消耗756.803s（010m后未保存更新也计入），接续−2.0e²用1643s，仍为同一轮40min；新目录MOD4V3_ROUGH_R1_SQUARE2_20261111。保存R1等级、地形分组、偏移和累计计数，重新物理episode。
[接续配方](../sources/local/MOD4V3_ROUGH_R1_SQUARE2_20261111/PLAN.json)


2026-11-11用户进一步要求下一检查点试三次项：平方2.0段在015m/iter23027/SHA22513a6e…完整保存后结束。实际903.074s，无FINAL/SAFE_CLOSED；原R1段756.803s＋本段903.074s已计入同一40min。新接续MOD4V3_ROUGH_R1_ABSCUBIC_20261111，余740s，奖励−2e²(1+|e|/1m/s)，二次基础保留、加绝对三次项，超/欠速对称；其余配方保留。直接有符号e³会奖励一侧，纯|e|³在误差小于1m/s时同系数更轻，不如此改。


2026-11-11 R1本轮最终记录：当前R1首轮已结束：三段PPO合计2400.031s，三组同批评测完成；三次项改善名义PhysX跟踪但fullDR偏速未解决。Flat1.5_020m保留回退，R1_010m实验候选、三次005m名义备用；[最终结果与选择](../sources/local/MOD4V3_ROUGH_R1_ABSCUBIC_20261111/DECISION.md)。总26阶段/118份完整PT实体；不自动R2或追加训练。


## 2026-11-11：R1坡面起步/轮胎摩擦原因归档与原奖励接续建议

两组固定权重配对回放已完成，每组2880环境×5s，numerical均0。原0.5–3s窗口含坡面零速起步/爬阶/重新加速，不能直接当稳态退化。相同R1 level3中级正阶、+1m/s、10初态下，仅恢复轮胎静/动摩擦到0.9，Flat1.5_020m均速−0.2055→+0.4627m/s，R1三次005m−0.0609→+0.7426m/s；其它初始DR输入和未目标材质通道差均0。仅去轮胎恢复系数没有同量级改善。这是在该条件下定位的主要影响因素，不是全部地形的唯一根因，也未证明DR实现错误或低摩擦不可学习。

完整报告、原始NPZ、失败、输入数组、执行源码和MuJoCo名义回放记录见[原因归档](../sources/local/MOD4V3_ROUGH_START_DIAG_20261111/README.md)。后续建议恢复R1原−1.5e²、指数速度奖励权重1.2，从R1_010m/iter22925/SHA959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022接着推进R1，完整DR、20%名义/20%平地保留；Flat1.5_020m继续作对照。精确建议见[下一轮配方](../sources/local/MOD4V3_ROUGH_START_DIAG_20261111/NEXT_ROUND_RECOMMENDATION.json)，40分钟/每5分钟完整保存和检查；当前状态为建议未启动。按越障进度、通过耗时、重置与有实际恢复机会的跟踪段评判，不增加新毕业门槛，不依据这一窗口继续加罚。


## 2026-11-11：R1第二轮已授权并启动

用户授权新40分钟，从R1_010m（iter22925，SHA959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022）接续。启动收据确认原速度项−1.5e²、指数1.2、4096env/LR3e-5 fixed/clip0.1/epochs3，完整PPO与R1课程levels/types/offsets/累计计数恢复；新物理episode。完整DR、20%名义/20%平地、MOD4接口/时序/solver/2mm单env重置保持，每5min完整PT和检查。原因诊断中的recommendation_not_launched是历史当时状态，本轮已获新授权。详见[本轮README](../sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/README.md)与PLAN。仍推进R1，R2腾空落地待本轮判断。


## 2026-11-11：R1第二轮训练与同批评测完成

实际2404.901s，8个5分钟保存点、9份不同字节完整PT及final同字节别名保留。较均衡实验候选r1round2_005m/iter22959/SHA0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f；10m是本批L3最高142/160对照，40m非全面最优。原父/5m/10m/40m的L3穿越139/140/142/139，fullDR平地前进MAE0.22453/0.21035/0.27251/0.16980；名义原六项57/60、60/60、57/60、21/60。5m名义及fullDR整段正式任务均有1reset，不能把窗口通过写成全段稳定。旧六类低档首次穿越均120/120，最高档仍有中阶与反坡未完成样本。

[最终结果](../sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/FINAL_REPORT.md)、[选择与边界](../sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/DECISION.md)、[完整PT](../sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/evidence/MODEL_ARCHIVE_INDEX.json)、[全部实际地形图](../sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/terrain_all/README.md)。主冻结未覆盖；没有继续训练或自动R2。


## 2026-11-12：按用户新指令统一推进 SCUT Rough-v0，2小时

用户明确要求直接训练华南虎Rough-v0科目，不再分R0/R1/R2逐个短轮。本次从综合接续父R1第二轮005m（iter22959，SHA0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f）恢复完整PPO/RNG，统一使用保存rough_rotation_stair的全部9地形族与10级难度，同时训练行进、小陀螺与组合指令。7200秒PPO，每300秒完整PT保存、下载核验和检查；本条是授权与执行计划，尚非训练成绩。

参考的top-level curriculum为空、height-offset curriculum关闭，所有地形行从启动一起采样；不再要求独立15cm落高探针作为此科目前置门槛。当前MOD435/78/6、2.5/10/20ms、TGS32/4、2mm单env保护、完整DR、20%名义/20%平地、−1.5e²和指数1.2保留；沿用2.2m/s上限和机身坐标语义，无云台观测。为4096env分散出生点，参考14列复制为70列，所有地形族仍在同一科目覆盖。

新目录：[统一科目README](../sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/README.md)。原阶段历史、冻结及实车包保留；本轮新检查点未经比较不自动晋升。


## 2026-11-12：统一SCUT Rough-v0两小时已完成

按用户新指令，统一全部9地形族/10难度行和行进/小陀螺/组合指令，一次连续PPO7206.137秒，848更新；每5分钟保存，26份完整训练PT/25种不同字节，8组同批固定权重PhysX对照全部完成。完整DR最高代表档±1m/s穿越：父/100m/120m为134/133/131（各160），±2.2指令为145/148/144；旋转角速MAE为1.7066/1.8705/1.8548rad/s；PhysX名义Flat58/36/30（各60）。综合继续R1第二轮005m/iter22959/0dcc15f5…，本轮100m仅实验候选、120m未晋升。原冻结/实车包未替换，没有自动下一轮，也未重新引入拆分课准入。

[最终报告](../sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/FINAL_REPORT.md) · [配方/全PT入口](../sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/README.md)。本轮当前总索引29阶段、164个完整训练PT记录；短探针原件另保留。
