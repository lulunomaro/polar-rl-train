# 华南虎台阶奖励与增强版 MOD4v1 的代码适配

2026-11-05 00:54实际覆盖：人类“允许100小时”已生效，按每小时完整保存/安全退出/独立80/实际回放/定向修复接续，原canonical余额与严格reserve保持，不再逐小时询问。当前接近/上推修复版已在空闲4090 GPU1通过真实FIRST151：480,000样本、20新Adam、非零actor/critic梯度、FULL_V4首存40,717,335B/SHA `eabb072a02761af1e75d1864a3acf236f91ab9a0335feba67162a432685a6c12`，完整首轮日志0实际错误。完整恢复source150/17项Adam/step3000/LR及RNG/队列/计数器，一次fresh物理reset。唯一collector20700/create00:48:15.353768；旧61200/session54368已完成。actualGO00:40:50.069379、SAVE01:40:50.069379、NOMINAL01:45:50.069379，正式回传于SAVE+45后进行；FIRST不等于技能。当前owner保存安全退出后立即独立80并审全部实际图，再按结果修复/接续。下文待批/FIRSTpending均为历史。

2026-11-05 00:32最新：jump200原hour已完整保存/退出/独立80/审完4图，70新PPO、33.6M样本、final150/Adam3000，全日志无实际错误，但0真实起跳/0越沿/0台顶落地。41/80请求、idle每步仍有.0825奖励，实测策略停滞。新候选只修接近阶段五项正tracking奖励按`clamp(vx_body/command_vx,0,1)`门控、push增加原源码takeoff_vel_z（cap3/weight2），保持几何/验收/物理/PPO；12项jump200和8项旧阶梯CPU回归通过。修复尚未原生训练，新hour需独立授权，不能延长已结束原窗口。详见history/reviews/20261103-mod4v1-scut-native-training/JUMP200_FINAL150_AND_APPROACH_REPAIR.md。

2026-11-04 22:32当前：`jump200/attempt02`已通过真实20,000环境FIRST，iteration80→81、480,000样本、20新Adam、非零actor/critic梯度及完整FULL_V4首存，完整首轮日志0实际错误。首次生产在跨任务恢复`_mode_enabled`配置向量时失败，原0PPO/关闭结果保留；修复仅在显式scut_stairs→jump200迁移时保留新constructor的禁specialmode配置，完整actor/critic/STD/Adam/LR/RNG/队列与计数器继续恢复，9项CPU检查和本次原生FIRST均通过。只用原授权窗剩余，SAVE23:11:34.580026/NOMINAL23:16:34.580026不延长。唯一collector61924负责正式回传，最终200mm跳跃技能仍待保存后的独立80与实际回放。

2026-11-04 19时人类纠正：“机器人跳上去200mm的台阶，不是碎台阶”。当前任务已改为独立`jump200`，单个200mm竖直台沿/水平台顶，从低地自主起跳并双轮落台稳定；覆盖下文inverse-mid小阶梯和允许贴轮爬台的选择。固定华南虎源码有200–220mm/1.5m踏面的STAIR_FOR_RM，原本选到25–40mm/0.1m的inverse-mid分支是任务错误。新任务复用原弹道起跳reward types并显式配置，无物理助推；8项起跳/爬台反例检查及完整学习状态跨任务恢复合成检查通过。实际80基线已在空闲4090完成，80起跳请求但0真正起跳越沿/0触台/0成功，证明旧策略没有200mm跳跃技能。原attempt08已完整保存49PPO/23.52M、fullfinalf6b6…并审完全部4图，保留为小阶梯试验。后续按`TODO_JUMP200.md`执行，来源、几何/奖励适配及待训状态见`SCUT_JUMP200_SOURCE_AND_SCOPE.md`与WORK_ORDER。下文均为历史，不能当当前目标或已成功。

2026-11-04 17:52人类审看MuJoCo指出旧场地实际是坡。原NPZ确认4个tile均9,060斜面/0竖直面，旧53双轮更高支持/2稳定只代表坡上运动，不是台阶或跳跃技能。人类明确“按华南虎方式上真实直角台阶，允许轮子保持接触”，并授权4090再训一小时20,000环境。attempt08已在fresh空闲72 GPU1启动，改用SDK显式MeshInvertedPyramidStairsTerrainCfg水平踏面/竖直阶面，保留25–40mm/0.1m/1m等配置尺寸；这是明确几何适配，原点高度与heightfield量化不同，不称原配方逐字复现。来自ffce完整状态续训，保留Adam/STD/RNG/队列，一次fresh物理reset。actualFIRST/恢复和原save/nominal以WORK_ORDER为准。见history/reviews/20261103-mod4v1-scut-native-training/RIGHT_ANGLE_STAIR_CORRECTION_AND_CONTINUATION.md。以下升阶文字为原始历史，技能解释已由本段纠正。

2026-11-04 17:03最新实际：attempt07已完整保存安全退出并正式传回，31PPO/14.88M样本/620Adam，FULL_V4 final SHAffce8d5ad2662a8981d971906e4b30bba13da38debbf42b6bc68284345f66d8c。完整训练/评测日志actualerrorlines0，原owner与collector均结束。独立80为53bothup/63anyup/2连续稳定指标，78评测cap/2boundarytimeout、0闭链/mimic/数值异常；早晚4图已由当前模型原生审看。对比原来源同为2恢复，没有明确技能提升；左/右hip目标上限命中94.69%/59.47%仍待按曲线定向分析。原授权小时已结束，不自动再开窗。详见history/reviews/20261103-mod4v1-scut-native-training/SCUT_STAIRS_ATTEMPT07_FINAL_REVIEW.md。以下各时间段为历史。

2026-11-04 16:31 attempt07已通过首个真实PPO与完整首存：480,000样本/192physics/20Adam，actorcritic梯度均非零，FULLV4首存SHA3a475d2b0909e6e07decceb77063c0fcff5c4a1008bb69ad9584a5e5bc5acfd0。对完整首轮WORKER.log有限读回确认actualerrorlines0，原patch溢出已消失；这是首轮执行证据，技能仍待最终独立评测。网络读者恢复完成且未重复启动训练，唯一collector59804已绑定；原SAVE17:02:25.845096/NOMINAL17:07:25.845096不延长，原owner保存退出后立即独立80与actualpose审看。

2026-11-04 16:21最新：attempt06已按计划16:02自动启动并完成FIRST，但20k首轮实际触发contact patch buffer overflow，不能算有效训练。已完整保存退出/独立80/审完4图并释放原锁；final49e8仅作失败来源。新attempt07仅扩大实际溢出的`cfg.sim.physics.gpu_max_rigid_patch_count`至524,288，原pair容量与物理/reward/PPO保持，继续有效0fdd来源。16:20:17已实际启动owner1605308，solelocal24732有限FIRST观察；原授权窗SAVE17:02:25.845096/NOMINAL17:07:25.845096不延长，当前修复原生待FIRST完整日志与首存确认。

2026-11-04 15:23人类已批准“允许重新训练一小时”。新attempt06为20,000环境/3600s保存+300s安全退出，继续用原canonical余额；修复版stairs/sdk共两个module，其它源码与0fdd有效来源按SHA引用。15:20实测72 GPU1空闲24,203MiB，但原canonical/authority/finite锁由standingV28 exactowner1600690持有。唯一localtimer24412已绑定，16:02:11后核原peer完整保存评测释放、freshLOCAL与目标GPU容量，再自动启动和绑定postround；当前尚未GO，不再等待人类批准。实际新GO/save/FIRST以WORK_ORDER和原始回执为准。

2026-11-04 12:24最新覆盖：空闲72 GPU0上的20,000环境阶梯训练原窗口已经结束。此前碰撞对容量不足、扩大容量后OOM、140列单mesh烘焙失败均已关闭并保留；attempt05在接触视图构建时因一个通配符匹配10个全局碰撞体失败，0FIRST/0PPO，无final可评。原owner已ownwait/settled/released，当前没有live训练。现改为10个显式单碰撞体filter路径，目标SDK源码确认singleton广播契约，针对原错误的1项CPU检查通过；仍待原生验证。原窗口不延长，已询问人类是否批准同一canonical余额重新开20,000环境一小时窗。当前结果与修复见`history/reviews/20261103-mod4v1-scut-native-training/SCUT_STAIR_NATIVE_AND_IDLE_GPU_LAUNCH.md`和`WORK_ORDER.json`，下文旧GO/FIRSTpending文字仅为历史。

2026-11-04最新实际：原SCUT阶梯有限80对照已在72 GPU0完成并审看4幅实际pose图，79局8秒cap/1接触终止，0closure/mimic/nonfinite，目标/CAD合规；有56局双轮升阶支持、2局达到本项目恢复观测指标，不能冒充原作者毕业标准。回传还暴露部分跑出mesh后继续下坠；已补回保存YAML开启的V14 rough boundary timeout，原globalmesh加border/margin后abs(x)>49.5或abs(y)>67.5，硬重置仍清timeout。20,000环境一小时新训练已在空闲GPU0实际GO，FIRST与最终状态见WORK_ORDER。详见`history/reviews/20261103-mod4v1-scut-native-training/SCUT_STAIR_NATIVE_AND_IDLE_GPU_LAUNCH.md`。

2026-11-04人类更新：“跳台阶不再强求270mm 按照华南虎的来就行”。新`scut_stairs`只选择公开保存YAML的inverse-mid多级台阶分支，复用原SDK生成器与25–40mm配置阶高/100mm踏面、原difficulty和出生origin；不恢复其它rough科目。该分支无单独高度覆盖，按V13回退全局.2–.42m。原reward/PPO/commands与增强MOD4v1物理/DR保持。旧270mm/首次飞行验收只描述历史，不再阻断新上阶任务。当前target-axis窗已完整关闭59PPO/28.32M样本，独立80仍0top，4图已原生审看；新有限同final原生对照已准备并等待资源，CPU通过不能当技能。详见`history/reviews/20261103-mod4v1-scut-native-training/SCUT_STAIR_BRANCH_AND_RL_DIAGNOSIS.md`。

2026-11-04公开trained_stair的20,000环境窗已完成46次PPO/22,080,000样本；final SHA `a8b954f378940421a5e9860faddf80c4575ae98ee062dddd1d60513de5a31aab`，独立80首局仍0触台/0strict。32局已用逐body接触与最后20步计数确认接触终止，48局达到8秒评测cap，非20秒任务timeout；早晚4幅actualpose已原生审看。新追到原SCUT执行路径中的processed leg target clamp在MOD4映射中遗漏，造成hip目标越过实际±.5rad。现补齐四motor contract限位，并保持原CAD差值/PD/DC/D4；FULL_V4显式区分此接口，旧V3仅 `--repair-target-limits` 可迁移。同final有限80对照正在进行，不能把CPU检查或修复源码称为原生成功。详见 `history/reviews/20261103-mod4v1-scut-native-training/PUBLISHED_RECIPE_FINAL_AND_TARGET_LIMITS.md`。

上述限位对照现已完成：实际全部关节目标/CAD差值合规，但仍0top。随后同final显式 `--repair-first-axis` 对照只把饱和left_crank输出行/偏置置0、该轴STD置1，其余权重保持；原生80首局验证第一轴raw全0、目标合规、0数值异常，仍0top/strict；两次各4幅actualpose均已原生审看。新20,000环境一小时候选从该final做weights-only/freshAdam并显式带入单轴修复，保留原SCUT奖励/PPO。不是完整原SCUT复现或已达270mm技能；当前状态见工作单。

2026-11-04原E0同端点原生诊断已完成：80首局0触台/0strict，61个原连续接触/姿态类终止、19timeout。前24步除高度外的35维输入最大差4.77e-7；第一步输入/动作几乎一致，原输入下第一轴仍100%超过执行裁剪范围，因此不能只归因于适配后actor字段错位。结果与有效早晚4图见 `history/reviews/20261103-mod4v1-scut-native-training/E0_SOURCE_INPUT_NATIVE_REVIEW.md`。保存姿态已由DataView转换为wxyz；一次误按原始SDKxyzw换序的中间图已明确作废，原回放顺序有效。

接续候选改用既有 `trained_stair`：恢复公开保存基础奖励、关闭额外状态机和两项奖励、恢复原命令/高度/20秒训练episode；首次task导入前constructor环境参数也与profile同步。人类指定固定270mm场地/出生关系、增强资产/原物理与20,000环境一小时保持。该候选已实际launch，完整首个PPO保存与技能结果以当前工作单为准，不能称已学会上台阶。新增pre-reset各reset-body接触力、姿态与命令/高度记录，不修改终止阈值。见 `history/reviews/20261103-mod4v1-scut-native-training/PUBLISHED_RECIPE_RESTORATION.md`。

此前生产 `jump270` **不等同于公开台阶保存配方仅替换机器人**：它开启了原保存配方关闭的状态机，改用固定前进命令、8秒episode和高度目标，并增加两项Stair奖励。逐行追溯记录不能替代这些任务改动的效果验证；具体原值、当前值与失败证据见 `history/reviews/20261103-mod4v1-scut-native-training/SCUT_RECIPE_PARITY_AND_FAILURE_CAUSE.md`。原E0同端点诊断已完成并见上文，0触台的唯一主因尚未隔离。

2026-11-04修复版E0来源20,000环境一小时窗已完整关闭、正式传回并审看早晚4图：60次PPO、28,800,000实际样本、FULL_V3 final SHA `d86732f97d0020c15036281bac2e23d300eb777db6643bb09b8cdc1740a7ae9a`。独立80首局0strict/0wholeclear/0leading/0top；54个原20连续终止、26timeout，平均4.1415s；闭链/mimic/数值和raw异常重置均0。具体证据见 `history/reviews/20261103-mod4v1-scut-native-training/REPAIRED_E0_FINAL_REVIEW.md`。

原E0历史retention已经有第一轴STD23.351587和maxraw140.443，所以此前把相同大输出直接称为SCUT新训练造成的退化，证据不充分，现追加纠正。下一步是显式 `--e0-source-diagnostic`：仅固定SHA的原E0推理，0优化器；在同一实际端点记录原MOD4/适配后观测和各自动作，两者中仅适配后动作进入物理。它仍需原canonical和资源锁释放；不是已执行结果或新一小时训练。普通SCUT检查点检查与生产入口保持显式兼容要求。

本目录是独立的增强 MOD4v1 USD 适配。2026-11-03 的 **20,000环境、一小时**运行已完整保存关闭：46次新PPO更新、22,080,000样本，final为iteration72、SHA `305f5a9e57086fd7e1b75ef3536e7c375081278479a91f33a9bb18c760b4cfcf`。独立80首局0整轮越沿、0触台、0严格成功，10–17controls终止，保存姿态已原生审图。该运行不是live或待评。

随后全面检查修复了动作执行裁剪遗漏、原debug终止时钟推进错误、评测首局接触统计与出生yaw基准，并补齐全局计数器保存恢复和pre-reset诊断。修复后的六组56项CPU检查通过。2026-11-04已在72第二张4090实际完成同final独立80复测：42–399controls、平均182.55，58个原连续终止、22个timeout；raw异常/closure/mimic/数值重置均0，应用动作最大6，但0触台/0strict且第一轴100%裁剪。早/晚4幅实际姿态已原生审看。后续从原成熟增强E0重新开始修复版20000环境一小时窗，实际运行以 `history/reviews/20261103-mod4v1-scut-native-training/WORK_ORDER.json` 为准。历史18,540行索引提供追溯，不是全程序等价保证。

本轮按最终生效的 **V14 → V13 → wheelbipe25_v3** 继承链补齐了逐行适配，修正了 critic 字段顺序、原始终止计数、命令采样与同步、观测时序和导轮接触分组。当前代码的行号、处理理由和检查依据见 `history/reviews/20261103-mod4v1-scut-adaptation/LINE_ADAPTATION.md`、`LINE_ALIGNMENT.jsonl`、`LINE_ALIGNMENT_RULES.json`；每条来源行都有处理记录。原 `LINE_MAP.jsonl` 的14,492行和 `REAUDIT_FINDINGS.md` 保留为历史记录，不能拿旧行号或旧结论描述当前代码。

**这是一份逐行追溯的模型适配，不是整条程序逐字等价或所有行已原生执行的证明。** 原奖励函数体保持固定来源；MOD4几何、PD、随机化、场地与缺失机构均有明确替换。修复版已完成有限原生评测，270mm技能尚未通过。

原始来源固定为 `scutrobotlab/wheeled-legged_RL@1a26356d6f591734d4f6f666f5cead1a6925da67`。SOURCES.json 保存每个来源的原路径、SHA256、Git blob 和既有归档位置。原始 MIT 版权与许可位于仓库 `history/reviews/20261103-scut-jump-reward-linebyline/LICENSE_SCUT.txt`，原作者为 SCUTRobotLab。数学函数由 upstream.py 从原文件 AST 加载，保留函数体和原行号，不复制整个上游工程。

公开 `rough_rotation_stair/2026-07-23_16-23-21` 保存配置中的状态机关闭；当前 V14 分支包含另一套可选奖励。保存 YAML 与当前源码有同一固定仓库来源，但没有找到七月训练当时的逐文件源码绑定，不能称整个实现是七月训练程序的字节复现。

## 实际适配了什么

| 部分 | 原源码/模型假设 | 本适配的实现 |
|---|---|---|
| 资产与导入 | SCUT 自身轮腿构型 | task 首次导入前绑定最新 MOD4v1 USD/contract；31 bodies、30 articulation DOFs；质量、惯量、COM 基准从新 constructor 取得 |
| 六维动作 | SCUT front1/rear1/wheel | 按名字映射 left_crank、left_hip、right_crank、right_hip、left_wheel_spin、right_wheel_spin；恢复MOD4 E0原wrapper的±6执行裁剪，裁剪结果进入PD/奖励/history，RSL保存的Gaussian原采样/logprob不修改。SCUT保存YAML的clip_actions为null，±6是明确的MOD4执行映射 |
| 被动结构 | SCUT 关节索引 | 八个导轮与四个传动 mimic 不加入六动作加速度/功率/扭矩代价；它们的实际碰撞仍纳入非轮接触 |
| 轮与腿几何 | 原 SCUT 半径、固定侧向腿根位置 | 半径 0.0625m、轮宽 0.02m、圆柱局部姿态、左右 hip 锚点取新 contract；不沿用 SCUT 的 0.217m 腿根侧向偏置 |
| 姿态坐标 | SCUT wxyz | 用实际 gravity 与 heading 回读辨认 SDK 的 xyzw/wxyz，统一传入原数学函数；不按版本猜测 |
| 关节软限位 | SCUT rear2/rear1 特定联动 | MOD4 没有同义 rear2，改为四个独立 crank/hip 的真实上下界；基础分支归一化平方、Airborne 分支弧度 L1 分别保留原定义。这是语义替换；两个 CLI profile 均未给这些项非零权重，仅当前 V14 候选分支使用 |
| 基础奖励 | 86 个 rew 项与门控 | 原函数体计算86项；保存配方37个权重键中26项非零，jump270为39键/28项非零。先状态机处理，后乘一次 dt=.02、配置权重、逐环境 sanitize，再求和 |
| 腾空与台阶分支 | Airborne/JumpTakeoff/StepUp/Stair | 原状态函数保留；顺序 Airborne→JumpTakeoff→StepUp→Stair；启用范围由下方 profile 明示；物理助推关闭 |
| 场地与扫描 | 原粗糙地形扫描 | 人类仅要求出生/相对台沿对齐：选原反向阶梯1m中央平台分支，中央低地1m见方、四边距中心.5m、外侧台高.27m；根位置(0,0,.38)、roll/pitch±.15/yaw±3.14，无xy偏移和初速。保留MOD4约束一致关节姿态。扫描保持原分辨率/网格/+5m起点，前扫读实际mesh。原单沿.8m为旧CPU阶段配置 |
| 接触 | 三帧、5ms 历史窗口；V14覆盖基础接触列表 | 奖励读5ms/三帧传感器，按名字重排到31body次序；29个非主轮body含8导轮用于有害接触。无云台分支的终止集合为chassis+8导轮；strict270另读400Hz实际manifold |
| 观测 | SCUT actor35、critic78 | actor为基础28+mode7；critic为clean基础28+body velocity3+observed height1+mode7+特权39，顺序与原代码一致；MOD4 100Hz noise/bias/delay及clip→scale保留 |
| 生命周期 | DirectRLEnv callbacks | 同一 pre-reset 端点先done后reward；Airborne按原height helper更新，StepUp/Stair原command hook在reward尾部及observation各一次。重复读取同一观测不再次推进状态；仅重置环境重新取扫描，清除上一局历史 |
| 终止 | 原SCUT姿态/接触连续门槛 | 直接载入原_get_dones及duration函数：接触>1N、roll/pitch>40°、连续20controls、timeout=max_episode_length−1；debug时钟只在开启debug_value_diagnosis时于reward尾部推进，保存配方为false，不因读取观测启用raw异常门。MOD4 .01m closure/.01rad mimic和非有限仍立即单环境重置 |
| 命令 | SpecialModeUniformVelocityCommand及V13同步 | 原完整命令模块按SHA引用，奖励先使用旧命令，再在reward尾部推进一次采样、height和state hooks；V13把覆盖后的命令写回generator。Manager后续compute被抑制，避免重复时钟 |
| PPO | 上游普通 RSL PPO | 适配 RSL5 TensorDict 与分离 actor/critic API，保持保存配方的 rollout24→GAE→PPO；不是 H1 residual/WM 算法 |
| 完整保存 | 上游 runner checkpoint | 使用FULL_V3及显式动作/观测语义，原子落盘并fsync；保存actor、critic、Gaussian STD、Adam、LR、iteration、D0–D7 RNG/组件/队列、奖励状态及全局计数器。完整恢复后一次fresh physical reset，旧接触窗口不装入新场景。旧V2须显式repair，V1/H1拒绝 |
| 成功验收 | SCUT 状态机成功事件 | 独立 strict270：首次飞行整轮后缘 footprint 越沿、双轮实际台顶支持、无地面/沿返回，速度≤.03m/s、roll/pitch≤10°、yaw≤.2rad 连续≥.5s；状态机事件不算验收通过 |

actor35 顺序为 command3、height1、angular velocity3、gravity3、leg position4、wheel position占位2、leg velocity4、wheel velocity2、last action6、mode7。critic78 在前28个clean字段后接 body velocity3、observed height1、mode7、特权39；不能把mode放到velocity前面。特权39为 stiffness6、damping6、torque6、feedback delay4、action delay2、轮相对速度6、轮接触2、chassis mass ratio1、左右轮材料6。MOD4 feedback延迟是一个实际0/10ms通道配置，按上游四类特权位置表示；两动作队列的延迟仍以原物理tick表示。

## 配置选择与训练配方

- `trained_stair`：公开台阶模型保存的基础reward权重、helper、PPO和基础命令配方；状态机/前扫辅助关闭。恢复原速度范围、heading、special modes、10% standing、5–15s重采样、height .2–.42m、20s episode及训练起始随机episode时钟。原rough地形生成器的按地形命令/高度覆盖、边界重置与云台分支未在当前固定270mm场地启用，所以不是完整rough训练复现。
- `jump270`：在上述权重上开启 Airborne、StepUp、Stair；把原 0.12–0.14m 检测改为 0.25–0.29m，wall 阈值 .30m，前扫 height bias .27m/max .61m；Stair 相对台面身体高度目标 .25–.34m；启用原 Stair 支持的轮底净空与身体高度指数奖励，各权重1、sigma .01。这些是本任务配置选择，未经原生验证的可达性和效果不作结论。
- `current_airborne_config()`：保留当前 V14 落地前轮速、零扭矩、居中、软限位等字典提取路径，仅供核对/CPU 分支测试，目前不是训练 CLI profile；不冒称它随两个 profile 自动启用。

两个CLI profile的JumpTakeoff均关闭；其完整奖励函数已加载并测试可选分支，但不称生产执行。SCUT可选外力/速度assist关闭。当前任务从地面起步，使用MOD4 reset，不搬入SCUT airborne-reset、预定义倒地恢复或gimbal模型。jump270明确使用vx=.6、vy=wz=0、无special/heading/standing、height=.25、8s episode并从零episode时钟开始。

PPO：actor/critic各 `[256,128,64]` ELU，Gaussian std初值1，rollout24、5 epochs、4 minibatches、LR1e-4/adaptive KL .01、gamma .99、lambda .95、clip .2、entropy .005、value coefficient2、gradient norm1、不作observation normalization。source任务失败与timeout同时出现时沿用原wrapper的timeout bootstrap；closure/mimic/数值强制重置清除timeout。actor35/critic78与原H1 actor103/critic106不兼容。默认只恢复 `MOD4V1_SCUT_FULL_V3` 及当前动作/字段语义；旧失败V2必须显式 `--repair-unclipped-v2`，完整学习状态保留，但执行接口已修复。不得自动扩输入、丢弃Adam或把迁移称为相同环境续态。V1即使维度相等也拒绝载入。

时钟与物理保持 .0025s、TGS32/4、policy50Hz、feedback100Hz，0.01m closure 为单环境重置、mimic .01rad；D0white_v3/D1–D7、工程气弹簧400N/k2000/damping3、原 PD/DC 与队列使用原共享实现。D6 仅 gas damping，不能称覆盖所有关节摩擦。新 USD SHA256 为 `2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3`；contract 为 `bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755`。

## 逐行核对与验证

仓库 `history/reviews/20261103-mod4v1-scut-adaptation/LINE_MAP.jsonl` 按原文件每个非空非注释行列出原行号、代码、函数、处理方式、目标文件与行号。`REWARD_TERMS.json` 另列每个基础项的原始表达式、行号与保存权重。被排除的 debug/视觉/gimbal/其它算法也列出原因。机械覆盖索引不等于每行都在原生运行中执行过。

本轮 `LINE_ALIGNMENT.jsonl` 按20个固定来源文件的18,540个物理行补建当前对照，含空行/注释、V14/V13覆盖关系、原AST复用、模型替换、任务覆盖与未启用分支；再应用 `LINE_ALIGNMENT_CORRECTIONS.json` 的35行分类修正。原代码不另复制，行记录引用原SHA/blob和原行文本SHA；`LINE_ALIGNMENT_RULES.json` 给出具体目标文件/行、适配理由与检查函数。一个来源语句可能对应多个目标语句，反之亦然；不靠增加空行伪造一对一行号。

本轮最新三份报告为 `LINE_PARITY_ATTEMPT6.json`（16项）、`LINE_PARITY_REGRESSION_ATTEMPT3.json`（14项）、`LINE_PARITY_RSL_INTEGRATION_ATTEMPT3.json`（12项），合计42项CPU检查通过，包含26个启用基础奖励的独立NumPy核算及真实RSL合成rollout/GAE/update/save/load。0生产PT读取、0原生physics、0GPU训练。Attempt3/4曾错误采用基类的导轮排除，虽fixture通过，人工追到V14后发现最终覆盖不同；已修复并在Attempt5/6验证，前报告完整保留并标明已被后续语义审查替代。

`CPU_VALIDATION_ATTEMPT5.json`：12项通过，含86基础项、45类可选奖励、打乱 runtime 名称映射、四元数双约定、dt一次、终态/重置顺序、观测与接触清理、有限圆柱 footprint/首次飞行反例，以及真实 RSL5 的24步 rollout、独立重算GAE、PPO update、完整存取与命令计时张量恢复。使用合成张量，0生产PT读取、0新 physics、0新GPU训练。早期 fixture 错误和轮圆柱近轴 float32 消减误差保留在 Attempt1/3，修复未覆盖失败报告。

上一轮再复核：`REAUDIT_NUMPY_ORACLE_ATTEMPT2.json` 的14项通过，包含用独立NumPy方程核算全部26个非零基础奖励及其加权总和（9种合成姿态/速度/动作/接触/终止输入）；`CPU_REAUDIT_INTEGRATION_ATTEMPT1.json` 的原12项集成检查通过。旧报告合计26项检查，不代表26个原生episode或所有条件组合。首轮复核5失败/3缺API错误、独立方程首轮float64/float32死区边界差异均保留；后者是测试输入精度问题，修复测试未改生产奖励。`REAUDIT_LINE_MAP_DELTA.json` 和 `REAUDIT_SOURCE_INDEX.json` 是上一轮身份；当前以 `LINE_ALIGNMENT_RULES.json` 和 `LINE_ADAPTATION_SOURCE_INDEX.json` 为准。

任务层面仍有两点需要实际轨迹验证：恒定前进命令0.6m/s没有台顶停稳阶段，不能等同于验收要求的速度≤0.03m/s；近沿机身仍在低地时，基础高度项相对机身下地面，而新增Stair项相对目标台面，两项可能暂时拉向不同高度。本次接口修复保留这些显式任务配置，未把奖励重设计混称为一比一修复。旧原生运行已经执行D0–D7读回、扫描与400Hz接触；修复版须重新做有限实际评测。

阶段提交后的普通补充修复：原 manager 的 `_reset_idx` 会重新创建 `extras['log']`，现在先保存终态奖励/状态日志，原 reset 完成后再合并，避免分项曲线丢失。`CPU_RESET_LOG_SUPPLEMENT.json` 单项检查通过，已有12项结果保留，未重跑 physics/PPO。

本机 stock IsaacLab 与目标运行时不同：本地没有原任务要求的 `isaaclab_physx.physics.PhysxCfg` 定制后端；不能改用其它 SDK 字段/solver 冒充验证。目标原生检查使用 `DEPENDENCIES.json` 中的共享 runtime和原资源锁；train.py 不申请或复制预算。修复源码已完成same-final有限原生复测，旧退化策略不再直接续训；新E0来源训练及其独立验收状态见当前工作单。

2026-11-03 17:15 +08 的一次有限只读检查读到远端 RSL5.0.1、IsaacLab6.1.14；原 canonical 正被 owner1535837 占用。`find_spec(isaaclab_physx)=false` 仅表示应用启动前默认路径不可见，历史原生任务会在 app 启动后启用扩展，不能据此断言远端扩展缺失。检查未导入 SDK、未扫描 GPU、未启动 worker、未读取 PT、未写 canonical；SSH 最终关闭并恢复 FREE。本机的依赖差异与远端当前资源占用分别记录。

原生运行须给出 `--assets --runtime --runtime-manifest --guard --job-root --iterations --save-deadline`。原保存边界前停止启动新rollout并完成原子full save。最新人类配置为jump270/20,000环境/3600s+原300s安全退出。`--resize-resume`按明确字段恢复旧完整actor/critic/STD/Adam/LR/iteration/globalRNG；不同环境数的DR行和队列重新建立，旧完整检查点不改，不能称逐环境随机流或PhysX续态。`--init-checkpoint`是SCUT风格的成熟MOD4 E0权重微调，新的Adam/iteration；critic38按语义映射至78，新增字段系数置零；E0静态mode与SCUT状态aux不同，已明确记录。

目标SDK启动实际修正：USD顶点显式GfVec3f/Vt数组；RayCaster mesh缓存按(path,device)从实例取；原共享E0 asset-diff声明按路径引用；MOD4可行关节库之后恢复指定根出生高度。独立评测整段env/状态生命周期保持inference_mode一致。失败原件/各attempt source SHA均保留。80环境26次更新后的完整模型SHA为d5dddb7a638fbc7de0152f8d383d818f4c5e794ada1829b9bdb89ab429e1a205，独立80首局全于10–22controls终止、0wholeclear/0top/0strict；未把短训或接触当交付。
