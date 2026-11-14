# MOD4 DR 阶段配方与模型归档（2026-11-11）

## 2026-11-12 台阶抬高底盘20分钟接续：末段待收

当前共31阶段、193完整PT文件记录。本轮已取回首次/5m/10m的3个PT，原父120m保持；15/20/final与原生fullDR待目标SSH恢复取回。[配方与实际报告](../MOD4V3_SCUT_STAIR_LIFT_20M_20261112/REPORT.md)。


2026-11-12 当前：**R2首轮40分钟及配对评测已完成**。5–10cm低落高能力已具备；综合保留r1round2_005m（iter22959/SHA0dcc15f5…），本轮R2新权重未晋升，005m保留实验备选；40m不作默认接续。28阶段/138完整PT文件索引，R2的10个PT实体均保留。[结果与选择](../MOD4V3_ROUGH_R2_20261112/DECISION.md)。


最新：R1第二轮及同批评测已完成，现27阶段、128个完整PT文件索引；本轮9种不同字节＋40m/final同字节别名。较均衡实验候选r1round2_005m，10m为最高实测L3穿越对照，未替换主冻结。[结果与选择](../MOD4V3_ROUGH_R1_ROUND2_20261111/DECISION.md) · [全地形图](../MOD4V3_ROUGH_R1_ROUND2_20261111/terrain_all/README.md)。

当前R1首轮已结束：三段PPO合计2400.031s，三组同批评测完成；三次项改善名义PhysX跟踪但fullDR偏速未解决。Flat1.5_020m保留回退，R1_010m实验候选、三次005m名义备用；[最终结果与选择](../MOD4V3_ROUGH_R1_ABSCUBIC_20261111/DECISION.md)。总26阶段/118份完整PT实体；不自动R2或追加训练。

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


2026-11-11用户进一步要求下一检查点试三次项：平方2.0段在015m/iter23027/SHA22513a6e…完整保存后结束。实际903.074s，无FINAL/SAFE_CLOSED；原R1段756.803s＋本段903.074s已计入同一40min。新接续MOD4V3_ROUGH_R1_ABSCUBIC_20261111，余740s，奖励−2e²(1+|e|/1m/s)，二次基础保留、加绝对三次项，超/欠速对称；其余配方保留。直接有符号e³会奖励一侧，纯|e|³在误差小于1m/s时同系数更轻，不如此改。


统一SCUT Rough-v0两小时与8组验收已完成；本轮26份完整PT均归档，综合接续保留r1round2_005m，100m/120m未晋升。[本轮模型选择](../MOD4V3_SCUT_ROUGH_V0_2H_20261112/DECISION.md)。当前29阶段/164完整训练PT记录。


## 2026-11-12：统一华南虎 Rough-v1 两小时正在训练

按用户后续选择，从Rough-v0 100m完整PPO（iter23665/SHA0010283962…）直接接续，保留其粗糙地形成果；R1第二轮005m和原实车调试包保留作基线。本轮11类地形/10难度并行，增加宽阶、较陡坡与落差、内部腾空落地，不再拆分R0/R1/R2短课。4096环境、单7200s、每300s完整PT保存下载检查；完整DR、20%平地与20%名义独立交叉、35/78/6、2.5/10/20ms、TGS32/4、2mm单env保护、−1.5e²及指数1.2、2.2m/s上限保留；主动跳跃关闭。模型未因开训自动晋升。

[本轮配方与PT](../MOD4V3_SCUT_ROUGH_V1_2H_20261112/README.md)。


## 2026-11-12：统一Rough-v1两小时PPO完成，验收5/10

从用户选择的Rough-v0 100m/iter23665/SHA0010283962…接续，实际PPO7206.600s、817更新、80,314,368环境策略步；24定时点加首次/final，共26完整PT、25种字节。11族/10级统一训练及完整DR、原物理/接口/奖励保留。总模型索引30阶段、190个完整训练PT记录。

已收齐同批PhysX5组：完整DR最高档穿越父/105m/120m=170/162/169（各200），高速162/154/154（各180）；宽阶上行未稳定掌握。名义平地34/41/40，完整DR35/32/34（各60）。Rough线保留原Rough-v0 100m，本轮105m/120m实验候选，未晋升，也未回退R1重训。原实车包保留。

目标机SSH超时，第6组gyro末段和后续落地/原Rough-v0保留测量待收齐；训练及全部PT已在本机完整核验。不能称验收全部完成或GPU已确认释放。未自动开下一轮。

[本轮记录](../MOD4V3_SCUT_ROUGH_V1_2H_20261112/README.md)。

## 2026-11-13 综合父冻结与独立台阶教师

综合最优db6e9ccf/iter25331完整PT冻结在相邻`MOD4V3_STAIRS_SPECIALIST_TEACHER_40M_20261113/frozen_parent/`。专项教师715c40b6/iter25432：本机正向5/5、真实斜向10/20；原生名义14/100、fullDR1/100，不能称fullDR毕业。737秒专项与44秒短对照的全部PT和失败保留。当前独立学生配方见`MOD4V3_STAIRS_SPECIALIST_DISTILL_40M_20261113/PLAN.json`，从原父而非教师权重初始化。

## 台阶教师迁移学生完成

stairs_specialist_student_20261113_010m；平地60/60、正向1/5、真实斜向0/20；全PT与原生保留结果见相邻MOD4V3_STAIRS_SPECIALIST_DISTILL_40M_20261113/FINAL_REPORT.md。原冻结父保持。

## 完整台阶示范＋上阶约束修复2小时已结束

实际PPO 7204.53080534935秒；实验候选stairs_parent_complete_20261113_095m，原综合父保持。源码、完整PT、配方和逐项结果：sources/local/MOD4V3_STAIRS_PARENT_COMPLETE_2H_20261113/FINAL_REPORT.md。

## 2026-11-14 高站姿保留与连续登阶修复：已开训两小时

实际PPO 2026-11-14T00:32:44.468226+08:00至预算约2026-11-14T02:32:44.468226+08:00。完整PPO接续上一轮95m（SHA de57c6dc）；健康综合父db6继续作为冻结保留教师。高站姿4腿单独保留、运动后成功示范阶段/角度均衡、单轮真实落轮及时分配原有0.5奖励。819台阶/717rough/512平地，原fullDR和速度奖励沿用。每5分钟完整PT和固定验收，预算7200秒不自动加时。完整配方、问题和负面诊断：sources/local/MOD4V3_STAIRS_PHASE_HEIGHT_REPAIR_2H_20261113/README.md、DIAGNOSIS.md、PLAN.json。

## 2026-11-14 高站姿追加两小时已排队

当前00:32开训的7200秒窗口继续，预算约到02:32；完成该轮训练和验收后，单次追加7200秒，完整PPO/Adam/STD与20组成功回放接续。每5分钟完整PT和检查。0.40m指令最新20m实际0.388021m，差约1.2cm；沿用原0.40/0.42m目标和现有配方。下一轮来源、排队状态和实际开训回执：sources/local/MOD4V3_HIGH_STANCE_CONTINUE_2H_20261114/README.md。

## 2026-11-14 原生验收与追加两小时排队状态更正

核实于2026-11-14T11:43:06.139951+08:00：高站姿修复首轮PPO已完成7206秒，最终高站姿0.38869m（指令0.40m）。固定回放所选15m完整检查点：平地60/60、正向连续登阶4/5、实际斜向7/20、下阶5/5。该固定回放不等同fullDR台阶毕业。原生验收曾将训练起点de57误当冻结综合对照db6的SHA，尚未动作即中断，连带追加队列退出；追加两小时未启动且消耗0秒。现按r2显式分别校验参考/学生身份，补跑原生验收后接续同配方7200秒。原错误、日志、源码和所有完整PT保留。恢复目录：sources/local/MOD4V3_STAIRS_PHASE_HEIGHT_REPAIR_2H_20261113/evidence/post_native_recovery_r2；接训入口：sources/local/MOD4V3_HIGH_STANCE_CONTINUE_2H_20261114/continue_after_current_r2.py。

## 完整台阶示范＋上阶约束修复2小时已结束

实际PPO 7206.379692316055秒；实验候选stairs_phase_height_repair_20261114_015m，原综合父保持。源码、完整PT、配方和逐项结果：sources/local/MOD4V3_STAIRS_PHASE_HEIGHT_REPAIR_2H_20261113/FINAL_REPORT.md。

## 2026-11-14 高站姿追加两小时：实际接续

实际PPO 2026-11-14T11:56:41.346864+08:00至预算约2026-11-14T13:56:41.346864+08:00；完整PPO/Adam/STD与20组成功池恢复。原高站姿指导、fullDR、平地/rough配比及速度奖励沿用；每5分钟完整PT和检查。记录：sources/local/MOD4V3_HIGH_STANCE_CONTINUE_2H_20261114/README.md。

## 2026-11-14 参考视频：低速登阶的后摆抬轮

用户视频已全片解码并按首次两级的关键原始连续帧核对：底盘先搭阶，轮轴留在后下方，随后向后上方摆动，再收回台面、伸腿站立。当前lift×retract项没有显式后摆方向或底盘支撑门控；这是需受控回放验证的配方差别，尚非唯一根因结论。记录及标注关键帧：sources/local/MOD4V3_VIDEO_LOW_SPEED_STAIRS_20261114/README.md。该诊断未修改训练配方，也未增加训练预算。

## 完整台阶示范＋上阶约束修复2小时已结束

实际PPO 7205.239659786224秒；实验候选high_stance_continue_20261114_035m，原综合父保持。源码、完整PT、配方和逐项结果：sources/local/MOD4V3_HIGH_STANCE_CONTINUE_2H_20261114/FINAL_REPORT.md。

## 2026-11-14 视频式底盘搭阶后摆抬轮：40分钟独立实验

从冻结综合最优父db6e9ccf/iter25331完整恢复，实际PPO 2026-11-14T14:19:07.587175+08:00；预算约到2026-11-14T14:59:07.587175+08:00。上行0.35–0.75m/s，局部真实台面支撑后奖励后摆抬轮；辅助搭阶30%单列；原fullDR和40%台阶/35%rough/25%平地保留，旧高速台阶BC停用，父能力及高站姿教师保留。每5分钟完整PT和检查。源码、配方、证据：sources/local/MOD4V3_REARWARD_SUPPORTED_STAIRS_40M_20261114/README.md。

## 视频式底盘搭阶后摆抬轮40分钟已结束

实际PPO 2406.6362285614014秒；实验候选rearward_supported_stairs_20261114_010m，原综合父保持。源码、完整PT、配方和逐项结果：sources/local/MOD4V3_REARWARD_SUPPORTED_STAIRS_40M_20261114/FINAL_REPORT.md。

## 2026-11-14 后摆收腿修复独立40分钟已开训

原生64环境功能探针完成；从综合父db6e9ccf/iter25331恢复。原乘积改为独立后摆/抬升进展，加入3个后摆中段辅助姿态及4条真实单阶恢复的194帧腿参考，保留完整DR、40/35/25、原教师和高站姿锚。每5分钟完整PT与纯策略固定回放。PPO 2026-11-14T15:43:54.395436+08:00，计划到2026-11-14T16:23:54.395436+08:00；不自动晋升。见sources/local/MOD4V3_REARWARD_RECOVERY_40M_20261114/README.md。

## 2026-11-14 后摆参考首阶段提前停止

PPO 1055.1810894012451秒完整保存；5m平地30/60、10m恢复60/60，低速新技能未形成，未晋升。余下原40分钟预算用于真实搭阶支撑/腾空奖励冲突及参考起始欠拟合修复；见sources/local/MOD4V3_REARWARD_RECOVERY_40M_20261114/FINAL_REPORT.md。

## 2026-11-14 后摆收腿修复独立40分钟已开训

原生64环境功能探针完成；从综合父db6e9ccf/iter25331恢复，继续原40分钟剩余1344秒。仅真实搭阶受力行不再套用腾空奖励；参考四阶段均衡采样，父保留系数1.0。完整DR、40/35/25、高站姿锚不变。每5分钟完整PT与纯策略固定回放。PPO 2026-11-14T16:10:04.917998+08:00，计划到2026-11-14T16:32:28.917998+08:00；不自动晋升。见sources/local/MOD4V3_REARWARD_CONTACT_REPAIR_40M_20261114/README.md。
