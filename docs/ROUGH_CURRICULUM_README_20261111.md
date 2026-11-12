# MOD4 Rough 课程计划：对照华南虎配置与预训练记录

当前R1第二轮及全部同批评测已完成；本轮较均衡候选r1round2_005m，10m为最高实测L3穿越对照。最新结果见文末更新与MOD4V3_ROUGH_R1_ROUND2_20261111/DECISION.md；旧阶段记录保留。

更新：2026-11-11。状态：**R0和R1首轮已完成；R1奖励加强实验未解决fullDR偏速，原Flat回退保留，R2尚未启动。**

原计划从 full DR Flat 候选进入低难度 Rough；R0/R1现已执行。接下来先固定模型定位DR速度敏感项。先保持现有策略、DR、奖励与控制时序，把变化集中在地形；保留平地样本和原有技能检查，再逐步增加台阶、腾空落地及旋转平移组合。

本页是后续执行与记录依据。各阶段按 40 分钟一轮规划，每 5 分钟完整保存并检查；本页不把计划写成运行结果，也不自动连续启动全部阶段。

## 1. 华南虎的版本与任务线究竟是什么

核对了本机 `refs/wheeled-legged_RL-main` 的任务注册、配置继承、地形、课程实现，以及三类预训练运行实际保存的 `env.yaml`。原件已按字节复制到 [reference](../sources/local/MOD4V3_ROUGH_PLAN_20261111/reference)，保留原版权声明，仅作参考，不作为 MOD4 训练入口。

| 参考对象 | 实际配置与继承 | 主要任务 | 对 MOD4 的用途 |
|---|---|---|---|
| Flat v0 | `WheelbipeV14FlatEnvCfg` | 基础平地速度、旋转、高度 | 当前 Flat 基础能力已具备，继续保留回归 |
| Flat v1 | `WheelbipeV14FlatEnvCfg_v1(FlatEnvCfg)` | 源码标注“腾空落地预训练”；启用 air reset 与 airborne 奖励 | 后续腾空落地阶段的参考 |
| Flat v2 | `WheelbipeV14FlatEnvCfg_v2(FlatEnvCfg)` | 云台方向控制、云台坐标系旋转平移 | 仅借鉴组合运动任务，MOD4 无云台，不直接移植观测和控制 |
| Rough v0 | `WheelbipeV14RoughEnvCfg(FlatEnvCfg_v2)` | `RM_ROTATION_TERRAINS_CFG_99` 上的旋转、平移、浅地形适应；其 post-init 关闭 airborne 状态机与前向扫描 | 当前最先接入的地形族 |
| Rough v1 | `WheelbipeV14RoughEnvCfg_v1(FlatEnvCfg_v1)` | 源码标注“跑场训练”；混合地形、air reset、腾空落地、按地形重采样指令 | 台阶与跑场阶段的参考 |
| `rough_rotation_stair` 预训练记录 | 采用 2026-07-30 09:16:27 保存配置；35D actor，9×9 m 瓦片，10 行×14 列；airborne/air reset 关闭 | 浅台阶、坡地、旋转兼容 | MOD4-R0/R1 的主要地形依据 |
| `rough_dash` 预训练记录 | 采用 2026-07-19 19:15:07 保存配置；35D actor，9×9 m，10 行×13 列；airborne/air reset 开启 | 冲坡、较高台阶、下台阶与落地 | MOD4-R2/R3 的主要依据 |
| `rotation_translation` 预训练记录 | 采用 2026-07-30 14:44:58 保存配置；35D actor，9×9 m，10 行×10 列；云台旋转平移模式开启 | 旋转和平移组合 | MOD4-R4 的任务参考 |

**这份 V14 参考实际注册 Rough v0、Rough v1，没有注册 Rough v2。** `Flat v2`、`V14_ROTATION_TERRAIN_COMMAND_OVERRIDES_2` 都不是 Rough v2 课程；各预训练目录也不能仅凭日期认定为严格的父子续训顺序。下文的 **MOD4-R0～R4 是本项目拟定阶段名**，不是声称华南虎存在同名课程。

参考源存在版本差异：当前源码 Rough v0 默认 10×10 地形网格；保存的 `rough_rotation_stair` 运行是 10×14，含中级正/反阶梯。本项目现有 `support/rough_terrain.py` 对应后者。地形复用以该保存配置为依据，不能把新源码默认值和旧运行结果拼成一个“完全一致”的配方。

## 2. 已确定的接续起点

| 用途 | 文件 | iteration | SHA256 |
|---|---|---:|---|
| 首选 Rough 父候选 | [square1_030m 完整 PPO](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_030m.pt) | 22618 | `d5e176401c20dd1b88a74003f7d4993aadc9a9cda301f042953de08fb6108851` |
| 备用父候选 | [square1_020m 完整 PPO](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/weights/model_020m.pt) | 22503 | `6aafe9ed4b88e0d27d0380bbc83b2f6d1b31a471ef284f74bb758f83467740fc` |

首选依据见 [Flat 最终报告](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/FINAL_REPORT.md)：30m 完整 DR 下 2.0/2.2 m/s 实际均速 1.9282/2.2052，两项各 7/10；后退 7/10，旋转 4/10，高度两项各 10/10，正式合计 45/60、reset=0。额外 2.7 m/s 诊断有 1 次 reset；20m 全部诊断 reset=0，作备用。

用户已接受当前完整 DR 旋转精度作为阶段可用表现：目标 14.1372 rad/s，均值 13.7271，平均欠速约 2.9%；原 ±2% 统计仍是 4/10，保留原结果。**Rough 入门不重新要求 Flat 全部 10/10。**

名义 PhysX 前进仍为 1.7668/1.9169 m/s，原精度统计 0/20；MuJoCo 名义回放偏超速。后续继续分引擎、分分布跟踪，不把此问题写成已修复，也不因此无限延长相同 Flat 配方。原 Step6、Step7 主冻结和已接受 push020 都保留，Rough 父候选不自动替换原冻结。

## 3. 从 Flat 继承什么

| 项目 | Rough 初期固定配方 |
|---|---|
| 资产与接口 | 当前 MOD4 资产及来源合同；35D actor / 78D critic / 6D action；原动作顺序与电机包络 |
| 控制时序 | 2.5 ms 物理步 / 10 ms PD / 20 ms 策略步；TGS 32/4，保持当前实际生效的 PhysX 设置 |
| 闭链 | 2 mm 单环境 episode reset；mimic、非有限保护照旧。记录事件和失败样本，不抬容差，不因单次峰值停止整批 |
| 质量与惯量 | base 0.9～1.3×；原选中的腿部连杆与轮子逐刚体独立 0.9～1.1×，惯量随本刚体质量调整 |
| COM、摩擦与弹簧 | base COM x±0.04 m、y/z±0.02 m；base/guide/wheel 分材质；关节摩擦全范围；气弹簧阻尼 0.5～1.5×，MOD4 刚度保持 2000 |
| 执行器 | PD 0.75～1.25×；输出倍率腿 0.8～1.1×、轮 0.9～1.1×，保留原采样时机 |
| 外界扰动 | 外力各轴±10 N、力矩各轴±1 Nm；速度推扰每 5～10 s、world XY 增量各±0.25 m/s；沿用现有持续时长与定时器 |
| 感知与延迟 | 全范围观测噪声；动作延迟 {5,10} ms、指定传感器组 {5,10,15} ms；物理子步推进，reset 采样、episode 内固定，actions 槽仍是原始策略动作 |
| reset | 继承 MOD4 可行 normal/ground 随机分布，ground 概率 0.5；按地形表面计算根高度、避免穿模；air reset 在后续 R2 单独加入 |
| 奖励 | R0/R1 沿用当前指数项及对称速度平方项；`e=cmd_vx−root_lin_vel_b_x×cos(pitch)`，reward rate 为 `−1.0e²`，每 20 ms 步乘 0.02；欠速、超速都罚 |
| 指令 | 保留现有 2.2 m/s 上限、后退/旋转/高度分布；Rough 按地形约束任务，平地仍保留 2.0/2.2、−1.5、4.5π 与 0.20/0.40 m 能力；2.7 只作额外诊断 |
| PPO | 初期沿用 LR=3e−5 fixed、clip=0.1、3 epochs、4 minibatches、24 steps/env、entropy=0.005，其余取父配方 |

### 两种混合分布独立分配

- 参数分布保持 **819 名义 + 3277 完整 DR**；完整 DR 的范围不缩减。
- 地形初期安排 **819 平地 + 3277 Rough**。这是新增地形采样建议，不是华南虎强制比例；其保存旋转地形的 plane 权重 0.3 / 全部权重 1.5 也相当于 20%。
- 两者交叉分配，不能把所有名义环境都放平地、所有 DR 环境都放 Rough。4096 env 建议：名义平地 164、名义 Rough 655、DR 平地 655、DR Rough 2622；四组分别统计。
- R0/R1 内平地组保留原完整任务分布，Rough 组按当前地形安排直行、转向和旋转。调比例时在下一轮 PLAN 明记，不在运行中热改。

## 4. 分阶段计划

每阶段先规划一轮 40 分钟，轮末根据检查点实际表现决定接续、留在当前难度或回退；不预先规定“训满多少小时就算通过”。第一轮只实现并执行 R0，不一次启动下面整张表。

| 阶段 | 对照华南虎 | 本阶段新增内容 | 起步与范围 | 主要看什么 | 当前状态 |
|---|---|---|---|---|---|
| **MOD4-R0：浅地形接入** | Rough v0 / 保存的 rough_rotation_stair | 在当前 full DR 环境接入平地、小栅格、缓坡、浅正反阶梯、随机起伏 | 先最低地形等级 0；栅格从 1 cm、坡度从 0.05、浅阶梯从 5 mm、随机起伏从低幅值开始；先不加入中级阶梯 | 正负指令方向正确、能实际跨障、无持续站住刷分；原 Flat 能力可用 | 首轮完成，见最终报告 |
| **MOD4-R1：粗糙地形旋转与浅阶梯** | 同一保存的旋转地形族 | 加入中级正/反阶梯，扩大浅地形难度；维持旋转、前后行进与高度控制 | 栅格 1～3 cm；坡度 0.05～0.15；浅阶梯 5～15 mm，中级 25～40 mm；随机起伏 0～3 cm；按课程升降级 | 分地形通过率与进度；旋转不倒、扰动后恢复；Flat 回归 | R1两轮完成，见文末结果 |
| **MOD4-R2：腾空落地预训练** | Flat v1 → Rough v1 的准备内容 | 在平地/已适应浅地形增加可行 air reset，分开评估离地、落地与恢复；接入所需 airborne 奖励 | MOD4 建议先从局部地面上方额外 5～10 cm 落高起步，再到参考 Flat v1 的 12～42 cm 范围；这是落高/参考 pose z，需按模型根高度语义换算，不能当绝对世界 z | 落地后能恢复姿态和指令运动；冲击、闭链事件与动作饱和；不是只看空中回报 | 首轮完成，5–10cm落地已具备；新PT未综合晋升 |
| **MOD4-R3：台阶、冲坡与上下落差** | Rough v1 / 保存的 rough_dash | 按地形配指令，增加较陡坡、宽台阶与下台阶；复用 R2 的落地能力 | 坡度 0.15～0.35；宽台阶 MOD4 先从 5 cm 递增到 15 cm，再依据能力向保存配置 15～35 cm（high-speed 最高 40 cm）推进；参考落差 30～40 cm 是后续目标，不是开局参数 | 双方向真实越障，避免绕平地、卡边或反向；过障后继续跟踪；保留浅地形样本 | 待 R2 结果 |
| **MOD4-R4：旋转平移与混合巩固** | Flat v2 / rotation_translation 的任务思想 | 在已适应地形组合旋转与平移、前后切换、速度推扰与高度变化；不增加新 DR 项 | 从现有 vx=0.9、wz=1.2 组合回归起；再扩展当前接口可表达的组合；35D/6D 保持 | 组合运动方向、速度、转向误差及受扰恢复；同时复测 Flat 和各地形阶段 | 待 R3 结果 |

上述低起点与阶段顺序是 **MOD4 迁移安排**。华南虎参考中的范围是目标对照，不保证 MOD4 不经适应就能完成，也不把版本号当难度等级。

### R0/R1 复用的具体地形

| 瓦片键 | 华南虎保存配置 | MOD4 初期处理 |
|---|---|---|
| `tiny_step_rot` | 栅格高 0.01～0.03 m，宽 0.05～0.20 m | 复用现有网格实现，从低高度/低难度开始 |
| `slope_for_rm_low` / `inv_slope_for_rm_low` | slope 0.05～0.15 | 同范围低等级起步；这里是坡度，不是弧度 |
| `stair_slope_for_rm_low` / `inv_stair_slope_for_rm_low` | 阶高 0.005～0.015 m，踏面 0.10 m | R0 低端，R1 扩至目标范围 |
| `stair_slope_for_rm_mid` / `inv_stair_slope_for_rm_mid` | 阶高 0.025～0.040 m，踏面 0.10 m | R1 再加；不能因为名称 low 就同时把 mid 混进第一轮 |
| `random_uniform_for_rm` | noise 0～0.03 m，量化步长 0.005 m | 以 5 mm 量化递增，不能设低于分辨率的“有效难度” |
| `plane_for_rm_rot` | 权重 0.3，全组权重合计 1.5 | 保留约 20% 平地；其它启用地形按其权重归一化 |

只启用部分地形时重新归一化比例，写出实际 env 数及瓦片分布。加入中级/高级地形后，已经学过的低难度与平地仍保留。

## 5. 课程如何真正升降级

华南虎 Rough 在运行时设置顶层 `curriculum=None`、地形生成器 `curriculum=True`；可选的 `rough_height_offset_curriculum_cfg` 默认为关闭。其打开后的逻辑是按训练 iteration 推进 level/height-offset（默认每 500 iter、最多 5000 iter、11 级），不是按成功率自动升降。保存的三类参考运行也均记录 height-offset curriculum 关闭。不能把“有地形难度行”写成“已经按能力逐步升难度”。

**MOD4 采用以下拟定能力课程，需在 R0 接入时实现：**

1. `max_init_terrain_level=0`；R0 暂只分配低难度地形，不能沿用旧入口 `None` 让环境随机出生在全等级。
2. 只在 episode reset 边界更新环境等级与瓦片 origin，不在 episode 中途抬高地面。同步 spawn 射线命中高度、env origin 和高度统计。
3. 对行进任务记录沿指令方向的净位移、是否跨过指定障碍、episode 终止原因。直行有效指令建议 `|vx_cmd|≥0.5 m/s`；完成本瓦片预定跨越目标且无失败时升一级，摔倒/安全终止时降一级；低指令、纯旋转或单纯超时不按行进距离升级。
4. 平地和旋转环境保留对应任务分布；旋转能力按旋转任务检查，不套行进距离公式。高级落差与 air-reset 任务按各自越障/落地结果判断。
5. 课程进度使用本次 Rough 的局部 iteration/episode 统计；父权重 iter22618 只是谱系，不能导致课程开局直接跳到最高级。保存全局 PPO iter 与 Rough 局部课程进度两个值。
6. 每 5 分钟报告每类地形各等级的环境数、有效尝试数、通过/失败原因、净行进进度与 reset 数；完整检查点保存地形等级、类型、分组及相关 RNG 状态。

这里的升降级规则用于采样难度，不新增一个所有任务必须 10/10 的毕业门槛。阶段接续依据同协议实际改善、能力保留和用户对误差的接受范围；少数精度未达标如实保留。

## 6. R0 接入时需要改的具体位置

本节是待实施清单，不代表代码已修改。

| 现有位置 | 已核到的行为 | R0 的处理 |
|---|---|---|
| `support/mod4v3_ppo_v1/scut_rough_v0_env.py` | 继承旧 `ScutFlatV2Env`；含 `enforce_closure_reset=False` | 新 Rough 类从当前 `ScutFlatMixedRemainingDREnv` 链接入地形，保留全部 DR 与 2 mm reset；旧快照不热改 |
| `scut_flat_env.configuration(..., terrain_selection='rough')` | 旧 rough 分支切到 5 ms 物理步、decimation=4，PhysX max solver 255/255 | 地形选择与时序/solver 解耦；新 Rough 保持 2.5/10/20 ms 与 TGS 32/4，实际 STARTUP 回读 |
| `support/rough_terrain.py` | 保存版旋转地形，包含低/中级与平地，但现有入口未实现能力升降级 | 复用几何生成代码，增加初始等级、启用地形选择、课程更新与四组分配 |
| `scut_flat_remaining_dr_env.py` 等 reset 链 | 可行 normal/ground reset，部分高度原为 Flat 写法 | 根高度改为当地地面高度加同语义 offset，关节闭链可行性与 reset 随机分布保持；相对地面高度可沿用现有扫描计算但不增加 actor 维度；R2 才改 air 分布 |
| `scut_flat_train.py` 的 `rough_v0` 分支 | 只恢复 actor，critic/optimizer/RNG/iteration 重新开始 | 新 R0 默认恢复当前完整 actor/critic/STD/Adam/RNG，另建新物理 episode 与 level0 课程；RESTORE 明记恢复项 |
| `scut_flat_rewards.configuration_rough_v0()` | 旧 rough 奖励/辅助参数与当前 Flat 不同，函数说明也混有历史“完全对齐”说法 | R0/R1 沿当前有效奖励，尤其保留 sigma=1、`−1.0e²`；不能切 profile 后悄悄回到旧小平方项 |

Rough 任务接口仍为 35D/78D/6D。华南虎的云台 PD、云台坐标系指令与附加控制标志不能直接塞入本模型；R2 可先用接触与内部状态做奖励分段，不新增 actor 输入。后续若确实需要改变接口，应单列设计与权重兼容方案，本计划不把它作为 R0 的依赖。

R0 只做与上述接入直接相关的短探针：少量环境检查地形出生、接触、高度与课程更新，再检查目标 4096 环境的少数 rollout 能否稳定执行；两者均不优化权重。既有 full DR 范围与时序证据复用，避免重跑整套旧 Flat 准入。短探针结果与实际消耗另记，不能伪装成 40 分钟训练。

## 7. 奖励如何对照，而不重演前进退化

参考 YAML 的同名系数不等于同一实际强度。`rough_rotation_stair` 保存值为 square weight=−0.1、sigma=0.25，实际为 `−0.00625e²`；`rough_dash` / `rotation_translation` 的 weight=−1、sigma=0.25，实际为 `−0.0625e²`。当前 MOD4 已核实为 weight=−1、sigma=1，即 `−1.0e²`，每步再乘 dt。

R0/R1 保持当前公式与其它奖励，不把新增地形、换奖励、换 PPO、换控制时序一起做。分坡地记录当前速度误差与地形方向进度；若坡度引起投影误差，先固定权重验证速度定义，再决定后续独立修改，不在 R0 顺手改公式。R2 再单独接入腾空/落地所需的状态奖励，R3 再接按地形分配指令。参考中的接触力阈值、关节限位和云台相关项须按 MOD4 对应物理量适配，不原样复制 20/10 等 airborne 权重后宣称对齐完成。

已有 `lin_vel_err_constraint`、高度 sigma 是奖励辅助参数；±2% 是既有 Flat 旋转精度统计。两类数值不互相充当验收线。地形瞬时腾空、被推后掉速与落地恢复按时间过程评估，不以单帧速度低直接判能力退化。

## 8. 每 5 分钟检查与轮末选择

### 固定回归

- Flat 正式六项仍按原协议各 10 初态：前进 2.0/2.2 m/s（误差≤0.15），后退 −1.5（≤0.20），旋转 4.5π（≤2%），高度 0.20/0.40 m（≤0.02）。保留原通过数，不改旧 raw。
- 固定 vx=0.9、wz=1.2 组合诊断；2.7 m/s 继续只作额外诊断，与正式任务分开。
- PhysX 名义、PhysX 完整 DR、MuJoCo 名义分别报告。每 5 分钟优先检查训练健康、完整 PT、当前地形表现与同源 Flat 回归；现有 MuJoCo 回放继续保留，不用其分数替代训练环境表现。
- 受扰回归沿现有 12 s 配对模板：同初态/DR/扰动，6 s 速度推扰，报告扰动前与 8～12 s 恢复后，恢复需连续 0.5 s 回到原误差范围。

### Rough 新增任务

按启用的地形类型×等级×正反行进分别记录，固定每项 10 初态并与父模型同 seed、同 DR 样本、同起点/方向/扰动配对。直行先采用 ±0.5、±1.0、±1.5 m/s 档，平缓和已适应地形再覆盖 ±2.0/±2.2；纯旋转、组合与高度任务单独安排，避免在高台阶同时随机要求最高旋转。

每个评测 episode 最长 20 s。记录指定障碍是否实际跨过、沿指令净位移、速度误差/MAE、姿态与接触、reset 原因；spawn 平台内站满时间不算越障成功。可行任务边界须在评测前写进协议，不能看完结果才调通过线。空中状态允许失去轮接触；落地后看恢复，不把正常离地记成失败。

R2 加落地后姿态和速度恢复、触地冲击；R3 加上下台阶和平台落差通过；R4 加组合运动及受推恢复。新地形的合理瞬态偏差与平地稳态精度分开报告，不要求所有障碍全程保持平地的速度容差。

### 保存和接续

- 每轮 2400 s；完整保存首检查点及 `model_005m.pt` 到 `model_040m.pt`，不中途覆盖同名旧轮。
- 每次检查包括 numerical、closure、mimic、fall/timeout、动作/电机包络及完整文件 SHA。训练已有 closure 终止不被 numerical=0 掩盖；Flat 父轮记录 episodes=57722、closure=8201、fall=80、numerical=0，用于对照，不作新容差。
- 轮末同批比较父与本轮候选，选实际较好的中间检查点；不因名称 final 就默认续它。原 Flat 六项通过数和用户已接受的旋转偏差作为保留能力基线，不把每项必须 10/10 当课程推进条件。
- 有持续数值异常、闭链终止显著集中或任务方向持续错误时，先保存并定位相应样本/实现；保持 2 mm 约束，不靠加大阈值、绕过 guard 或只堆时长处理。
- 若新地形改善且原能力可用，接续当前课程或下一阶段；若没有改善，比较已存较早检查点，回到上个可用难度。额外训练轮按后续授权执行。

## 9. 目录、记录与下一项工作

新执行轮独立建目录，例如 `MOD4V3_ROUGH_R0_20261111`（以实际开工日期命名）；从已冻结的当前 support 复制并修改，不动旧源快照。PLAN 记录真实父路径/SHA、恢复方式、地形参数、四组比例、局部课程进度、奖励公式、DR 范围、PPO、时钟和 solver；STARTUP 读回实际值。

每轮保存原流程的 STARTUP、RESTORE、PPO_EFFECTIVE、周期检查、FINAL、SAFE_CLOSED，以及课程状态与分地形结果。**完整 `.pt` 本体继续入 Git，不只存路径。** 所有实际失败、回退和最终选择均追加记录，原失败不能改成 pass；Git 网络使用 `127.0.0.1:7897` 代理。归档不改变原训练预算。

当前执行：[MOD4V3_ROUGH_R0_20261111](../sources/local/MOD4V3_ROUGH_R0_20261111/README.md)。80env×200步及4096env×48步无优化探针已完成，numerical均0、rawaction槽误差0；4096探针closure564/810 episode事件，最大3.08mm，按2mm单envreset保留。2026-11-11 15:36:57（Asia/Shanghai）启动首轮，job=train040m_rough_r0_r1、PID1152439；实际PPO计时从环境与完整恢复之后开始。R1～R4没有执行。

## 10. 可追溯参考

以下是本次实际核对并原样保存的文件。参考仓库根目录为 `D:/claude2/fangzhen/refs/wheeled-legged_RL-main`；源相对路径与 SHA256 逐项列出，之后本机参考更新也能复核此计划依据。

| 本次保存 | 原相对路径 | SHA256 |
|---|---|---|
| [v14_tasks.py](../sources/local/MOD4V3_ROUGH_PLAN_20261111/reference/v14_tasks.py) | `source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/__init__.py` | `2b66f56d7936d0b478169fa37e7f52486d6e46bc158f04b8d93079be6d03bd46` |
| [v14_env_cfg.py](../sources/local/MOD4V3_ROUGH_PLAN_20261111/reference/v14_env_cfg.py) | `source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env_cfg.py` | `e287a0dda7124dda6526a9a6f351f00d2ac0e1774ad390b9e2eebf077b9efc93` |
| [v14_cfg_utils.py](../sources/local/MOD4V3_ROUGH_PLAN_20261111/reference/v14_cfg_utils.py) | `source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/cfg_utils.py` | `60dbc341079a3a26bd57a94bb5cfbbe740efa565652b18f926e765de7a782d69` |
| [v14_env.py](../sources/local/MOD4V3_ROUGH_PLAN_20261111/reference/v14_env.py) | `source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe_V14/env.py` | `71388264b7db94d02bd2c906eae0387bbe5175504187b97575c09894faf58853` |
| [terrains.py](../sources/local/MOD4V3_ROUGH_PLAN_20261111/reference/terrains.py) | `source/agent_tasks/agent_tasks/manager/mdp/isaaclab/terrains.py` | `b7554813116bc032dad333b11add50344bb2f70b6979b0473cbac9b714711dc6` |
| [rsl_rl_ppo_cfg.py](../sources/local/MOD4V3_ROUGH_PLAN_20261111/reference/rsl_rl_ppo_cfg.py) | `source/agent_tasks/agent_tasks/direct/wheelbipe/agents/rsl_rl_ppo_cfg.py` | `fbfe7b45a043241275fce6529bc3fcc6a63bddfb93919e2d10f8bd159eeff9c4` |
| [rough_rotation_stair_env.yaml](../sources/local/MOD4V3_ROUGH_PLAN_20261111/reference/rough_rotation_stair_env.yaml) | `pretrained/26_infantry/rough_rotation_stair/2026-07-30_09-16-27/params/env.yaml` | `a6117e55b3ebb5a03870981bd2d65d889c38850063008a9341d8346b997bb1ee` |
| [rough_dash_env.yaml](../sources/local/MOD4V3_ROUGH_PLAN_20261111/reference/rough_dash_env.yaml) | `pretrained/26_infantry/rough_dash/2026-07-19_19-15-07/params/env.yaml` | `da26c974517564480c8900b6adf339d1648c99902ea3d9bb86fa48387df302c4` |
| [rotation_translation_env.yaml](../sources/local/MOD4V3_ROUGH_PLAN_20261111/reference/rotation_translation_env.yaml) | `pretrained/26_infantry/rotation_translation/2026-07-30_14-44-58/params/env.yaml` | `cfbb0f192e25cb4e6af5c704721e817a83ee131683d883bbeea4fd49cd018611` |

当前 MOD4 实现与证据：

- [当前 Flat 配方](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/PLAN.json)、[实际启动回读](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/evidence/train040m_square_double_r1_STARTUP.json)、[最终评测](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/FINAL_REPORT.md)。
- [当前完整 DR＋名义混合环境](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/support/mod4v3_ppo_v1/scut_flat_mixed_dr_env.py)、[完整 DR reset 实现](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/support/mod4v3_ppo_v1/scut_flat_remaining_dr_env.py)。
- [现存旋转地形生成器](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/support/rough_terrain.py)、[旧 Rough 环境](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/support/mod4v3_ppo_v1/scut_rough_v0_env.py)、[训练恢复分支](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/support/mod4v3_ppo_v1/scut_flat_train.py)、[地形/时序入口](../sources/local/MOD4V3_STEP7_SQUARE_DOUBLE_20261111/support/mod4v3_ppo_v1/scut_flat_env.py)。
- [DR 阶段总索引](DR_TRAINING_INDEX_20261111.md)、[既有续训与保存方法](DR_TRAINING_RESUME_20261111.md)。本页为后续 Rough 规划补充，不改写旧轮的状态与结果。


## 11. R0首轮实际结果与接续判断

[完整报告](../sources/local/MOD4V3_ROUGH_R0_20261111/FINAL_REPORT.md)：实际2405.700s，完整DR范围/奖励/时序保持。浅level0父119/120、本轮各检查点120/120；补评本轮实际训练level3正反1.5m/s，父与全部检查点均120/120。因此R0浅地形已有能力，本轮没有测出显著新增越障收益，不应继续原样堆R0时间。

同批PhysX fullDR Flat父44/60，R0保留20m为40/60、正式reset0；其前进1.8953/2.2262、MAE0.16101。5m前进1.9555/2.2516更近父，正式41/60但2.2任务1fall，另存备用。35/40m名义MuJoCo60/60而同源fullDR欠速更大，不默认续末权重。原Flat父与既有冻结继续保留，不由R0候选覆盖。

下一步建议进入本页R1的小中级阶梯/较宽地形范围，先对原Flat父、R0的20m/5m做同任务比较再确定接续；这是下一阶段建议，本轮没有开R1。训练numerical0、closure7093；level0评测30m后续episode出现1次numerical，level3评测numerical0，原始失败均保留。


2026-11-11用户中途要求下个检查点切Rough：Flat平方项1.5段在020m/iter22856完整保存后结束，SHA`a5102af62938f6bf472855edba34c5f10efce061eecaeb3aebee34815fe7cf87`，已接续`MOD4V3_ROUGH_R0_SQUARE15_20261111`的R0余下20min。保留−1.5e²/fullDR/20%名义/20%平地；本轮预算按Flat20＋Rough20分配。新结果待同批PhysX配对，原冻结保持。


2026-11-11 Flat1.5→RoughR0接续已结束：Flat1204.923s后按用户要求在020m完整保存点切Rough，Rough再1201.085s，均每5min完整PT保存。保留Flat020m（iter22856，a5102af6…）回退，Rough010m（iter22941，ece8c411…）作实验候选；同批fullDR前进MAE分别0.12165/0.13866，正式44/60(reset0)/41/60(reset0)，Rough010m额外2.7诊断3reset如实保留。R0浅地形均120/120，未测出新增越障能力，Rough训练累计numerical1。原主冻结保留，未自动R1或追加训练。两段10份不同字节完整PT在各自weights目录，候选配方/本机目标机只读存档已完成；[最终报告](../sources/local/MOD4V3_ROUGH_R0_SQUARE15_20261111/FINAL_REPORT.md)。总索引23阶段、107完整PT。


2026-11-11 R1首轮40分钟已获用户授权并启动：父Flat1.5_020m/iter22856/a5102af6…，新增中级正反阶梯及完整计划难度范围；Rough低速起步课程，平地组原技能继续；−1.5e²/fullDR/PPO/2.5ms/TGS32/4/2mm保留，每5min完整PT。训练和真实失败计数见[本轮记录](../sources/local/MOD4V3_ROUGH_R1_20261111/README.md)。未自动R2。


2026-11-11偏速处理切段：用户要求加强速度平方惩罚。010m完整检查点iter22925/SHA959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022已核验保存，旧训练SIGINT退出，无FINAL/SAFE_CLOSED，不能写成正常40分钟完成。原段总消耗756.803s（010m后未保存更新也计入），接续−2.0e²用1643s，仍为同一轮40min；新目录MOD4V3_ROUGH_R1_SQUARE2_20261111。保存R1等级、地形分组、偏移和累计计数，重新物理episode。
[接续配方](../sources/local/MOD4V3_ROUGH_R1_SQUARE2_20261111/PLAN.json)


2026-11-11用户进一步要求下一检查点试三次项：平方2.0段在015m/iter23027/SHA22513a6e…完整保存后结束。实际903.074s，无FINAL/SAFE_CLOSED；原R1段756.803s＋本段903.074s已计入同一40min。新接续MOD4V3_ROUGH_R1_ABSCUBIC_20261111，余740s，奖励−2e²(1+|e|/1m/s)，二次基础保留、加绝对三次项，超/欠速对称；其余配方保留。直接有符号e³会奖励一侧，纯|e|³在误差小于1m/s时同系数更轻，不如此改。


2026-11-11 R1本轮最终记录：当前R1首轮已结束：三段PPO合计2400.031s，三组同批评测完成；三次项改善名义PhysX跟踪但fullDR偏速未解决。Flat1.5_020m保留回退，R1_010m实验候选、三次005m名义备用；[最终结果与选择](../sources/local/MOD4V3_ROUGH_R1_ABSCUBIC_20261111/DECISION.md)。总26阶段/118份完整PT实体；不自动R2或追加训练。


## 2026-11-11：华南虎固定权重比较与速度误差口径

已完成5份固定权重、R1 level0/3、nominal/fullDR配对回放；未追加训练。实际速度、pitch、首次episode掩码、原始参考PT与失败均保留于[诊断档案](../sources/local/MOD4V3_SCUT_ROUGH_SPEED_DIAGNOSTIC_20261111/README.md)，数值见[报告](../sources/local/MOD4V3_SCUT_ROUGH_SPEED_DIAGNOSTIC_20261111/REPORT.md)。原华南虎权重直接转到MOD4的结果仅是迁移表现，不能代表原机器人性能。

用户指出起步、爬阶与越障后重新加速需要时间。现有0.5–3s统计混合这些过程；进度标记不代表整段障碍出口。因此这些窗口误差不足以认定R1退化或OOD，不能据此继续加大惩罚或更换父权重。原先“fullDR偏速未解决”的阶段解释需结合[本次修正](../sources/local/MOD4V3_SCUT_ROUGH_SPEED_DIAGNOSTIC_20261111/TRANSIENT_INTERPRETATION.md)理解；原测量与历史结论保留，不改写成通过。后续评判先区分完成进度、正常瞬态和有充分恢复机会后的持续偏差，不新增毕业门槛。


## 2026-11-11：R1坡面起步/轮胎摩擦原因归档与原奖励接续建议

两组固定权重配对回放已完成，每组2880环境×5s，numerical均0。原0.5–3s窗口含坡面零速起步/爬阶/重新加速，不能直接当稳态退化。相同R1 level3中级正阶、+1m/s、10初态下，仅恢复轮胎静/动摩擦到0.9，Flat1.5_020m均速−0.2055→+0.4627m/s，R1三次005m−0.0609→+0.7426m/s；其它初始DR输入和未目标材质通道差均0。仅去轮胎恢复系数没有同量级改善。这是在该条件下定位的主要影响因素，不是全部地形的唯一根因，也未证明DR实现错误或低摩擦不可学习。

完整报告、原始NPZ、失败、输入数组、执行源码和MuJoCo名义回放记录见[原因归档](../sources/local/MOD4V3_ROUGH_START_DIAG_20261111/README.md)。后续建议恢复R1原−1.5e²、指数速度奖励权重1.2，从R1_010m/iter22925/SHA959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022接着推进R1，完整DR、20%名义/20%平地保留；Flat1.5_020m继续作对照。精确建议见[下一轮配方](../sources/local/MOD4V3_ROUGH_START_DIAG_20261111/NEXT_ROUND_RECOMMENDATION.json)，40分钟/每5分钟完整保存和检查；当前状态为建议未启动。按越障进度、通过耗时、重置与有实际恢复机会的跟踪段评判，不增加新毕业门槛，不依据这一窗口继续加罚。


## 2026-11-11：R1第二轮已授权并启动

用户授权新40分钟，从R1_010m（iter22925，SHA959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022）接续。启动收据确认原速度项−1.5e²、指数1.2、4096env/LR3e-5 fixed/clip0.1/epochs3，完整PPO与R1课程levels/types/offsets/累计计数恢复；新物理episode。完整DR、20%名义/20%平地、MOD4接口/时序/solver/2mm单env重置保持，每5min完整PT和检查。原因诊断中的recommendation_not_launched是历史当时状态，本轮已获新授权。详见[本轮README](../sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/README.md)与PLAN。仍推进R1，R2腾空落地待本轮判断。


## 2026-11-11：R0能力、父权重与地形混合口径

R1首轮父为Flat1.5_020m，当前第二轮父为R1_010m；未直接选择R0检查点不代表没有R0浅地形能力。Flat1.5_020m在当时R0浅地形原首次穿越判据已120/120，R1再混合训练这些类型并增加中级正反阶梯。类型在各自level0–3升降级，随机起伏不会变成坡面。

4096环境实际地形分配：R0已有六类型2230（54.4%）、R1新增中级正反阶1047（25.6%）、平地819（20.0%）；只看3277个Rough环境，约68.05%旧类型/31.95%新中阶。两轮R1相同，不是30%旧R0。20%名义/80%完整DR是独立的参数分配，与地形比例交叉。

[全部地形截图与分类型/等级大图](../sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/terrain_all/README.md)：每类每级代表块的真实Isaac Lab网格顶点/面，在本地MuJoCo渲染，无高度夸张。R0/R1标签只表示类型引入阶段，不表示已完成该级；平地组固定level0。


## 2026-11-11：R1第二轮训练与同批评测完成

实际2404.901s，8个5分钟保存点、9份不同字节完整PT及final同字节别名保留。较均衡实验候选r1round2_005m/iter22959/SHA0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f；10m是本批L3最高142/160对照，40m非全面最优。原父/5m/10m/40m的L3穿越139/140/142/139，fullDR平地前进MAE0.22453/0.21035/0.27251/0.16980；名义原六项57/60、60/60、57/60、21/60。5m名义及fullDR整段正式任务均有1reset，不能把窗口通过写成全段稳定。旧六类低档首次穿越均120/120，最高档仍有中阶与反坡未完成样本。

[最终结果](../sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/FINAL_REPORT.md)、[选择与边界](../sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/DECISION.md)、[完整PT](../sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/evidence/MODEL_ARCHIVE_INDEX.json)、[全部实际地形图](../sources/local/MOD4V3_ROUGH_R1_ROUND2_20261111/terrain_all/README.md)。主冻结未覆盖；没有继续训练或自动R2。


## 2026-11-11：底盘落地起摆站立专项（只评测）

固定R1第二轮005m/iter22959/SHA0dcc15f5…，同源PhysX测试8种底部支承落地、随机可行腿姿态，每种1份名义+4份完整DR。站起并保持高度/姿态约1秒：名义6/8、完整DR25/32；分别含1份上电前2mm闭链中止，真实未站起/翻倒为名义1份、完整DR6份。原逐帧双轮接触严格成绩另列6/8、19/32，不覆盖。正常站姿持续通电对照5/5。现有权重有部分地面起身能力，尚不能认定任意摆腿上电均可靠起身。底部导向轮是真实支承，未删除或穿地。

[专项报告、视频和原始轨迹](../sources/local/MOD4V3_GROUND_STAND_PROBE_20261111/README.md)。本轮没有训练、没有改奖励/DR/solver/接口，也没有启动R2；地面起摆恢复与腾空落地分别记录。


## 2026-11-12：R2低落高腾空落地首轮已启动

用户授权按本README推进R2。父R1第二轮005m/iter22959/SHA0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f；完整PPO、R1地形levels/types/offsets与累计计数恢复，新物理episode。R2内容对应华南虎Flatv1到Roughv1的腾空落地准备，R2是项目编号，并非华南虎Roughv2。

平地或旧R0类型level0–1的reset有30%替换为正常可行站姿相对局部地面再抬高5–10cm；实际全体比例随地形与reset变化。其余保留normal/ground，R1中阶继续混训。复用保存的SCUT airborne内部奖励逻辑，35D actor末7槽仍固定normal，78D critic/6动作不变；−1.5e²、指数1.2、完整DR、20%名义/20%平地、2.5/10/20ms、TGS32/4和2mm单env闭链重置保留。

固定权重10env探针完成，数值异常0；4096混合探针有1个原normal初态第1步极端事件，既有单env保护已重置。追踪确认新增603次air均真实离地/接触，其中584次已恢复姿态；前一个因“任意一次数值重置就整批拒绝”的探针ERROR原样保留，未改成pass；后续按既有单env保护口径记录。未调solver或DR来掩盖事件。主训练40分钟、每5分钟完整PT和检查，轮末对父/保存点做落地与Flat/R1配对评测。

[本轮README](../sources/local/MOD4V3_ROUGH_R2_20261112/README.md) · [PLAN](../sources/local/MOD4V3_ROUGH_R2_20261112/PLAN.json)。

R2本轮的“腾空”采用air reset，是抬高后的下落和着地恢复；5–10cm为额外落高，不能当成主动起跳高度。当前未测可控主动跳高，不从参考pose z或后续台阶高度推算跳高能力。


## 2026-11-12：R2首轮训练与同批验收完成

实际2406.301s/iter23230，8个5分钟保存点、首次完整更新和final别名，共10个PT/9种不同字节；全部保留实体。正式落地比较分3批960env以避免初始拥挤容量警告，17组初始DR/姿态/指令跨批差异0，所有正式评测无漏接触容量警告。原2880env无效assessment及4096首探针ERROR保留，未改写。

父R1round2_005m与本轮全部检查点，在5/10cm×平地/低栅格×4指令×10初态的名义/完整DR落地姿态均160/160；父完整DR落地后指令159/160，本轮158–160/160。旧R0六类最低档均120/120，R1-L0完整DR156–157/160。父/本轮005m/040m的R1-L3完整DR139/141/142；名义Flat原六项57/50/25，完整DR43/35/33（各60），说明少量R1进度收益伴随平地精度损失。各指标分别是首次落地恢复、任务窗口或首次穿越，不能合称全段无reset。

综合接续继续选R1父模型0dcc15f5…；R2_005m仅实验备选，不晋升40m。当前已完成R2低落高这一档验证，不等于主动起跳或所有参考空中初态通关。下一步先从父模型做额外15cm固定权重探针，按真实薄弱区间确定后续R2训练，停止原样堆当前低难度时间；没有自动下一轮或R3。

[最终报告](../sources/local/MOD4V3_ROUGH_R2_20261112/FINAL_REPORT.md) · [模型选择](../sources/local/MOD4V3_ROUGH_R2_20261112/DECISION.md) · [完整PT](../sources/local/MOD4V3_ROUGH_R2_20261112/evidence/MODEL_ARCHIVE_INDEX.json)。


## 2026-11-12：按用户新指令统一推进 SCUT Rough-v0，2小时

用户明确要求直接训练华南虎Rough-v0科目，不再分R0/R1/R2逐个短轮。本次从综合接续父R1第二轮005m（iter22959，SHA0dcc15f5ecfca08107dba8b1a1d80de57c777218b5f3a928c094be66c73a644f）恢复完整PPO/RNG，统一使用保存rough_rotation_stair的全部9地形族与10级难度，同时训练行进、小陀螺与组合指令。7200秒PPO，每300秒完整PT保存、下载核验和检查；本条是授权与执行计划，尚非训练成绩。

参考的top-level curriculum为空、height-offset curriculum关闭，所有地形行从启动一起采样；不再要求独立15cm落高探针作为此科目前置门槛。当前MOD435/78/6、2.5/10/20ms、TGS32/4、2mm单env保护、完整DR、20%名义/20%平地、−1.5e²和指数1.2保留；沿用2.2m/s上限和机身坐标语义，无云台观测。为4096env分散出生点，参考14列复制为70列，所有地形族仍在同一科目覆盖。

新目录：[统一科目README](../sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/README.md)。原阶段历史、冻结及实车包保留；本轮新检查点未经比较不自动晋升。


## 2026-11-12：统一SCUT Rough-v0两小时已完成

按用户新指令，统一全部9地形族/10难度行和行进/小陀螺/组合指令，一次连续PPO7206.137秒，848更新；每5分钟保存，26份完整训练PT/25种不同字节，8组同批固定权重PhysX对照全部完成。完整DR最高代表档±1m/s穿越：父/100m/120m为134/133/131（各160），±2.2指令为145/148/144；旋转角速MAE为1.7066/1.8705/1.8548rad/s；PhysX名义Flat58/36/30（各60）。综合继续R1第二轮005m/iter22959/0dcc15f5…，本轮100m仅实验候选、120m未晋升。原冻结/实车包未替换，没有自动下一轮，也未重新引入拆分课准入。

[最终报告](../sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/FINAL_REPORT.md) · [配方/全PT入口](../sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/README.md)。本轮当前总索引29阶段、164个完整训练PT记录；短探针原件另保留。


## 2026-11-12：统一华南虎 Rough-v1 两小时正在训练

按用户后续选择，从Rough-v0 100m完整PPO（iter23665/SHA0010283962…）直接接续，保留其粗糙地形成果；R1第二轮005m和原实车调试包保留作基线。本轮11类地形/10难度并行，增加宽阶、较陡坡与落差、内部腾空落地，不再拆分R0/R1/R2短课。4096环境、单7200s、每300s完整PT保存下载检查；完整DR、20%平地与20%名义独立交叉、35/78/6、2.5/10/20ms、TGS32/4、2mm单env保护、−1.5e²及指数1.2、2.2m/s上限保留；主动跳跃关闭。模型未因开训自动晋升。

[配方/实时证据/完整PT入口](../sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112/README.md)。Rough-v0逐地形报告见[完成报告](../sources/local/MOD4V3_SCUT_ROUGH_V0_2H_20261112/COURSE_COMPLETION_REPORT.md)。
