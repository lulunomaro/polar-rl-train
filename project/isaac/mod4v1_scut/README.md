# 华南虎台阶奖励与增强版 MOD4v1 的代码适配

本目录是独立的 USD 适配实现，原 H1 冻结训练目录继续保留。2026-11-03 已完成软件接口和 CPU 集成验证；尚未在目标定制 Isaac SDK 上启动本适配的原生物理或训练，不能称原生适配验收完成，也没有新策略跳过 270mm 的结果。

**复核结论：这不是整条程序逐字、逐行为完全等价的移植。** 基础奖励函数体来自固定原源码；输入绑定、模型语义、观测、终止和训练接口需单独核对。本次复核发现并修复了扫描定义、状态更新时序、重置缓存和软限位公式等问题，详见 `history/reviews/20261103-mod4v1-scut-adaptation/REAUDIT_FINDINGS.md`。原 14,492 行处理索引保留为历史版本，不能据此声称每行已动态验证。当前实现仅有 USD 路径，未完成独立 MJCF 后端。

原始来源固定为 `scutrobotlab/wheeled-legged_RL@1a26356d6f591734d4f6f666f5cead1a6925da67`。SOURCES.json 保存每个来源的原路径、SHA256、Git blob 和既有归档位置。原始 MIT 版权与许可位于仓库 `history/reviews/20261103-scut-jump-reward-linebyline/LICENSE_SCUT.txt`，原作者为 SCUTRobotLab。数学函数由 upstream.py 从原文件 AST 加载，保留函数体和原行号，不复制整个上游工程。

公开 `rough_rotation_stair/2026-07-23_16-23-21` 保存配置中的状态机关闭；当前 V14 分支包含另一套可选奖励。保存 YAML 与当前源码有同一固定仓库来源，但没有找到七月训练当时的逐文件源码绑定，不能称整个实现是七月训练程序的字节复现。

## 实际适配了什么

| 部分 | 原源码/模型假设 | 本适配的实现 |
|---|---|---|
| 资产与导入 | SCUT 自身轮腿构型 | task 首次导入前绑定最新 MOD4v1 USD/contract；31 bodies、30 articulation DOFs；质量、惯量、COM 基准从新 constructor 取得 |
| 六维动作 | SCUT front1/rear1/wheel | 按名字映射 left_crank、left_hip、right_crank、right_hip、left_wheel_spin、right_wheel_spin；保留原 MOD4 position/velocity target、PD、DC torque-speed envelope 和物理队列 |
| 被动结构 | SCUT 关节索引 | 八个导轮与四个传动 mimic 不加入六动作加速度/功率/扭矩代价；它们的实际碰撞仍纳入非轮接触 |
| 轮与腿几何 | 原 SCUT 半径、固定侧向腿根位置 | 半径 0.0625m、轮宽 0.02m、圆柱局部姿态、左右 hip 锚点取新 contract；不沿用 SCUT 的 0.217m 腿根侧向偏置 |
| 姿态坐标 | SCUT wxyz | 用实际 gravity 与 heading 回读辨认 SDK 的 xyzw/wxyz，统一传入原数学函数；不按版本猜测 |
| 关节软限位 | SCUT rear2/rear1 特定联动 | MOD4 没有同义 rear2，改为四个独立 crank/hip 的真实上下界；基础分支归一化平方、Airborne 分支弧度 L1 分别保留原定义。这是语义替换；两个 CLI profile 均未给这些项非零权重，仅当前 V14 候选分支使用 |
| 基础奖励 | 86 个 rew 项与门控 | 原函数体计算86项；保存配方37个权重键中26项非零，jump270为39键/28项非零。先状态机处理，后乘一次 dt=.02、配置权重、逐环境 sanitize，再求和 |
| 腾空与台阶分支 | Airborne/JumpTakeoff/StepUp/Stair | 原状态函数保留；顺序 Airborne→JumpTakeoff→StepUp→Stair；启用范围由下方 profile 明示；物理助推关闭 |
| 场地与扫描 | 原粗糙地形扫描 | 每环境真实 0.27m 高台，近沿 x=.8、长3m、宽2m；机身扫描恢复保存配置的1cm分辨率/2cm网格/+5m起点。保存配置轮下scanner为空，两轮地面高度同取机身扫描；前扫用真实mesh，漏扫依原函数回退 |
| 接触 | 三帧、5ms 历史窗口 | 奖励继续读 5ms/三帧传感器；独立验收读 400Hz actual manifold 点、法线、力，区分地面与台顶 |
| 观测 | SCUT actor35、critic78 | 保留 MOD4 actor 100Hz noise/bias/delay，35维；critic clean38 重新排序成35字段，再加 base velocity3、高度1、特权39；裁剪后缩放遵循保存 YAML |
| 生命周期 | DirectRLEnv callbacks | 同一 pre-reset 端点先done后reward；Airborne按原height helper更新，StepUp/Stair原command hook在reward尾部及observation各一次。重复读取同一观测不再次推进状态；仅重置环境重新取扫描，清除上一局历史 |
| 终止 | 原SCUT姿态/接触连续门槛 | 保留MOD4姿态.75rad、chassis50N等终止与closure/mimic；这不等于原SCUT40°/base1N/连续20controls。原数值异常阈值已接回，墙事件不可取消closure/mimic/数值异常的强制重置 |
| PPO | 上游普通 RSL PPO | 适配 RSL5 TensorDict 与分离 actor/critic API，保持保存配方的 rollout24→GAE→PPO；不是 H1 residual/WM 算法 |
| 完整保存 | 上游 runner checkpoint | 原子保存 actor、critic、Gaussian STD、Adam、LR、iteration、D0–D7 RNG/组件/队列及奖励窗口；恢复后一次 fresh physical reset，不宣称续接 PhysX 状态 |
| 成功验收 | SCUT 状态机成功事件 | 独立 strict270：首次飞行整轮后缘 footprint 越沿、双轮实际台顶支持、无地面/沿返回，速度≤.03m/s、roll/pitch≤10°、yaw≤.2rad 连续≥.5s；状态机事件不算验收通过 |

actor35 顺序为 command3、height1、angular velocity3、gravity3、leg position4、wheel position占位2、leg velocity4、wheel velocity2、last action6、mode7。critic78 先使用上述 clean35，再加 body velocity3、observed height1；特权39为 stiffness6、damping6、torque6、feedback delay4、action delay2、轮相对速度6、轮接触2、chassis mass ratio1、左右轮材料6。MOD4 feedback 延迟是一个实际 0/10ms 通道配置，按上游四类特权位置表示；两动作队列的延迟仍以原物理 tick 表示，不伪造 SCUT 的时钟。

## 配置选择与训练配方

- `trained_stair`：公开台阶模型保存的全部基础 reward 权重和 helper 参数；状态机/前扫辅助关闭。模型、动作、DR、时钟和场地按 MOD4 替换，所以是该奖励配方的移植，不是原机器人复现。
- `jump270`：在上述权重上开启 Airborne、StepUp、Stair；把原 0.12–0.14m 检测改为 0.25–0.29m，wall 阈值 .30m，前扫 height bias .27m/max .61m；Stair 相对台面身体高度目标 .25–.34m；启用原 Stair 支持的轮底净空与身体高度指数奖励，各权重1、sigma .01。这些是本任务配置选择，未经原生验证的可达性和效果不作结论。
- `current_airborne_config()`：保留当前 V14 落地前轮速、零扭矩、居中、软限位等字典提取路径，仅供核对/CPU 分支测试，目前不是训练 CLI profile；不冒称它随两个 profile 自动启用。

两个 CLI profile 的 JumpTakeoff 均关闭；其完整奖励函数已加载并测试可选分支，但不称生产执行。SCUT 可选外力/速度 assist 关闭。当前任务从地面起步，不搬入 SCUT airborne-reset 或 gimbal 模型。

PPO：actor/critic 各 `[256,128,64]` ELU，Gaussian std 初值1，rollout24、5 epochs、4 minibatches、LR1e-4/adaptive KL .01、gamma .99、lambda .95、clip .2、entropy .005、value coefficient2、gradient norm1、不作 observation normalization。actor35/critic78 与原 H1 actor103/critic106 不兼容；恢复只接受本适配格式，禁止自动扩输入或丢弃 Adam 假装完整续训。首次使用新接口需要新初始化，现有 H1 完整权重保留为其原始来源。

时钟与物理保持 .0025s、TGS32/4、policy50Hz、feedback100Hz，0.01m closure 为单环境重置、mimic .01rad；D0white_v3/D1–D7、工程气弹簧400N/k2000/damping3、原 PD/DC 与队列使用原共享实现。D6 仅 gas damping，不能称覆盖所有关节摩擦。新 USD SHA256 为 `2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3`；contract 为 `bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755`。

## 逐行核对与验证

仓库 `history/reviews/20261103-mod4v1-scut-adaptation/LINE_MAP.jsonl` 按原文件每个非空非注释行列出原行号、代码、函数、处理方式、目标文件与行号。`REWARD_TERMS.json` 另列每个基础项的原始表达式、行号与保存权重。被排除的 debug/视觉/gimbal/其它算法也列出原因。机械覆盖索引不等于每行都在原生运行中执行过。

`CPU_VALIDATION_ATTEMPT5.json`：12项通过，含86基础项、45类可选奖励、打乱 runtime 名称映射、四元数双约定、dt一次、终态/重置顺序、观测与接触清理、有限圆柱 footprint/首次飞行反例，以及真实 RSL5 的24步 rollout、独立重算GAE、PPO update、完整存取与命令计时张量恢复。使用合成张量，0生产PT读取、0新 physics、0新GPU训练。早期 fixture 错误和轮圆柱近轴 float32 消减误差保留在 Attempt1/3，修复未覆盖失败报告。

2026-11-03 再复核：`REAUDIT_NUMPY_ORACLE_ATTEMPT2.json` 的14项通过，包含用独立 NumPy 方程核算全部26个非零基础奖励及其加权总和（9种合成姿态/速度/动作/接触/终止输入）；`CPU_REAUDIT_INTEGRATION_ATTEMPT1.json` 的原12项集成检查通过。合计26项检查，不代表26个原生episode或所有条件组合。首轮复核5失败/3缺API错误、独立方程首轮float64/float32死区边界差异均保留；后者是测试输入精度问题，修复测试未改生产奖励。最新目标位置与源SHA见 `REAUDIT_LINE_MAP_DELTA.json` 和 `REAUDIT_SOURCE_INDEX.json`。

任务层面仍有两点需要实际训练验证：恒定前进命令0.6m/s没有台顶停稳阶段，不能等同于验收要求的速度≤0.03m/s；近沿机身仍在低地时，基础高度项相对机身下地面，而新增Stair项相对目标台面，两项可能暂时拉向不同高度。本次保留这些显式任务配置，未把奖励重设计混称为一比一修复。原生SDK、完整D0–D7读回、扫描和400Hz接触仍待验证。

阶段提交后的普通补充修复：原 manager 的 `_reset_idx` 会重新创建 `extras['log']`，现在先保存终态奖励/状态日志，原 reset 完成后再合并，避免分项曲线丢失。`CPU_RESET_LOG_SUPPLEMENT.json` 单项检查通过，已有12项结果保留，未重跑 physics/PPO。

本机 stock IsaacLab 与目标运行时不同：本地没有原任务要求的 `isaaclab_physx.physics.PhysxCfg` 定制后端；不能改用其它 SDK 字段/solver 冒充验证。目标原生检查必须使用 `DEPENDENCIES.json` 中的实际共享 runtime，并由原 canonical owner 供应资源锁和绝对 save deadline；train.py 自身不申请/复制预算，不改变旧 once，不启动定时器。`--help` 可在无 physics 条件下查看参数；`--support` 仅引用已有共享模块目录。原生 startup/fullDR/400Hz 接触、独立技能评测与真实回放完成之前，本适配状态为 `CPU_VERIFIED_NATIVE_PENDING`。

2026-11-03 17:15 +08 的一次有限只读检查读到远端 RSL5.0.1、IsaacLab6.1.14；原 canonical 正被 owner1535837 占用。`find_spec(isaaclab_physx)=false` 仅表示应用启动前默认路径不可见，历史原生任务会在 app 启动后启用扩展，不能据此断言远端扩展缺失。检查未导入 SDK、未扫描 GPU、未启动 worker、未读取 PT、未写 canonical；SSH 最终关闭并恢复 FREE。本机的依赖差异与远端当前资源占用分别记录。

原生运行须给出 `--assets --runtime --runtime-manifest --guard --job-root --iterations --save-deadline`；`--profile jump270 --num-envs 80` 对应本任务，原保存边界前停止启动新 rollout 并完成原子 full save。异常路径仍尝试完整保存，然后关闭 logger/env/app。resume 还原的是学习与随机流，fresh reset 后 episode/接触窗口清空；不是旧物理场景续态。
