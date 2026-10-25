# T2-z 对 MOD4 后续训练的可行性研究（实际只读研究）

研究 ID：MOD4_T2Z_FUTURE_TRAINING_FEASIBILITY_20261025。研究日：2026-10-25（Asia/Shanghai）。上游固定版本：`c72f051f5cffcb1f372a32bc488df273556d39b9`，提交时间 `2026-10-16T02:12:17Z`，提交说明 Link published arXiv paper；论文 `arXiv:2610.22364v1`，2026-10-15。[上游提交](https://github.com/T2-z-latent-optimization/T2-z/commit/c72f051f5cffcb1f372a32bc488df273556d39b9)、[原论文](https://arxiv.org/html/2610.22364v1)。JSON 同目录提供全部实际引用、源码链接、内容 SHA256、检索错误和兼容性分类。

**结论：思想有研究价值；原 T2-z 当前不值得接入 H1 主 PPO。** 它可作为未来对摩擦、质量、接触条件等隐变量进行离线辨识或慢速候选策略比较的研究方向；不能当成已验证的 PPO 样本加速、神经推理加速或 PhysX 替代器。近期应继续解决当前跳跃与距缘位置的时序问题。本文没有产生训练、模型下载、新 actor 输入、world model、GPU rollout 或预算授权。

## 官方方法究竟做什么

上游为动作条件视频预测器增加每个环境共享的 32 维 latent。训练交替更新世界模型和环境 latent；测试冻结共享模型，通过已观察的交互轨迹预测误差反向更新 latent，再预测同环境不同动作的未来视频。原方法不要求给出摩擦、质量等数值真值，也没有独立的 observation-to-environment-latent encoder；但必须知道哪些轨迹来自同一个物理环境。环境改变/重置后不能随意沿用旧 latent。[README](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/README.md)、[环境分组](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/t2z/metadata.py#L9)、[latent 更新代码](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/t2z/inference/ours.py#L505)。

它仍依赖预训练知识：官方安装要求 **Wan2.2-TI2V-5B 基础文件和 BWM 初始化 checkpoint 两者齐备**，然后使用本任务 RGB 视频与动作轨迹微调。BWM 是初始化来源，不是在线 teacher；Wan VAE 是视频编解码器，不是环境历史 encoder。代码中名为 physical_context_encoder 的模块包含 latent 的投影/条件化，不应因此误称为从状态历史直接推断环境的网络。DINO 历史 encoder 是对照方法，不是 Ours 的必要模块。无需专家“成功示范”标签并不等于无需交互数据；预测训练需要动作及真实后续帧。[模型布局](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/configs/model/wan2_2_ti2v_5b.yaml)、[数据读取](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/t2z/data.py#L18)、[physical context 模块](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/wan_video_action/models/physical_context.py)。

训练目标为 flow-matching 的视频 latent MSE，排除已观测前缀；训练模块为 DiT、action_encoder、physical_context_encoder，优化器 AdamW；没有与当前 RSL PPO 的 actor/critic、优势估计、策略概率比或当前 17 tensors/17 Adam 状态连续性兼容的现成接口。接入 PPO、做 teacher/student 蒸馏或给 actor 增加 z 都属于另行设计的新方法。[损失](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/t2z/training/losses.py#L5)、[优化器](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/t2z/training/ours.py#L618)、[训练配置](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/configs/ours/sim_pushbox_friction.yaml#L72)。

## 与当前 H1/E3 的兼容性

| 项目 | 上游实际接口/证据 | 对本项目的判断（本研究推断） |
|---|---|---|
| 输入数据 | RGB video + 同步动作，Friction 为 224×224、41 帧、1 帧历史；真实 Ball 为 320×160、61 帧 | 当前状态 raw 不能直接喂入视频 VAE。48 帧可视回放也不自动构成跨环境、同步、可训练的 RGB 数据集；不能把稀疏回放当全部训练视觉数据。 |
| 动作 | 官方配置 14 维，模拟 eef_delta，真实任务 joint_target；action stats 归一化；编码器把四动作对应一组视频 latent | 轮腿的关节/轮速/PD processed targets 语义和时钟均不同，补零到14维不能继承操纵动作语义。需要新动作路径及任务微调，无法直接用当前 PPO checkpoint 替换。 |
| 环境分组 | 同物理环境内多动作轨迹共享 latent；metadata 显式 environment_index/physical_environment_index | 不能只把20k个并行 env_id永久当环境参数 ID。每次随机化/重置要追踪实际配置；要跨 episode、物理配置划分防泄漏。 |
| 时序 | 论文为 Franka/LIBERO 动作与20fps RGB；代码四动作分组 | H1 100Hz/2.5ms×4；E3 50Hz/2.5ms×8。20fps每帧跨20个物理步，H1跨5控制步，E3为2.5步；需真实时间戳/动作区间聚合，不能简单丢帧或复制动作。快速闭链接触、起跳、着陆有严重域差。 |
| 技能范围 | 官方模拟为推块、抛物、碰撞、开灯、配重等；真实任务为球/门/杆/软管操纵 | 检阅的官方任务与论文没有轮腿自平衡、双轮跳台阶、270mm顶面接触稳定的验证。预测画面好不能证明真实接触正确。 |
| 成功标准 | 候选动作视频评分后在真实/模拟环境执行，按任务结局计成功 | 本项目仍须双轮真实跳上270mm并顶面真实contact稳定0.5s；峰高、视频相似度、生成画面或模型自报success均不能替代。 |
| 控制与吞吐 | 40 latent梯度步 + 每查询25去噪步；没有20k×100Hz控制接口 | 只能考虑低频/离线辨识或高层候选排序，不能插入当前每10ms的H1控制环。跨任务/硬件没有实测速度外推依据。 |

代码依据：[Friction 配置](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/configs/ours/sim_pushbox_friction.yaml)、[真实 Ball 配置](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/configs/ours/real_ball.yaml)、[动作读取/适配](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/wan_video_action/data/operators.py#L418)、[动作时序编码](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/wan_video_action/models/wan_video_action_encoder.py#L47)、[推理配置](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/configs/inference/sim_pushbox_friction.yaml)。当前状态 raw、正式检查点与目标来自本研究接收的项目上下文；本研究没有读取/执行模型权重或重新跑 raw。

## 资源与加速判断

**官方实测/预算：** 论文附录B常见任务为每方法 `2×H200×24小时`；Mass×Friction为`4×H200×48小时`；多背景为`4×H200×24小时`。附录E.4在单H200上报告一次 latent 适配加5个query视频总18.09秒，排除模型载入、样本读取、MP4写出；这不是每控制步或每候选的延迟，也不是4090数据。论文实验使用Franka操纵、20fps、14通道动作，未提供轮腿动态接触的验证。[论文附录B、E.4](https://arxiv.org/html/2610.22364v1)。

**代码默认值：** Friction/真实Ball等 launcher 为2进程，Mass×Friction/多背景为4；允许环境变量覆盖进程数。训练为bf16，gradient checkpointing开启，offload/fp8默认关闭，batch_size=1但每次更新还包括多组/多microbatch。上游使用 Accelerator.prepare 与 DDP kwargs；随仓库 launcher 未声明模型/优化器分片方案。增加DDP进程不等于把两张24GB合成一张48GB。[2进程launcher](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/launch/train_ours_sim_pushbox_friction.sh)、[4进程launcher](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/launch/train_ours_sim_mass_friction.sh)、[训练分发](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/t2z/training/ours.py#L1383)、[bf16模型构造](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/scripts/train.py#L108)。

**未知且不伪造：** 本研究未取得可核对的4090峰值显存/小时数/全量磁盘占用，也未视觉读取论文资源图上的具体内存柱数值。5B级核心参数仅按2bytes/param就约10GB十进制，还不含VAE、梯度、优化器、激活、暂存和分发开销；这只是量级下限，不是fit证明。不能把普通Wan视频推理的24GB宣称移用于T2-z全模型微调/反向latent适配。24GB 4090是否能以某种offload/分片方式运行，须单独预审及新授权实测。

**本地瓶颈证据：** 已有M3 FP32六完整更新，H1 collection中trace压缩35.935%、reset31.299%、physics26.412%、NN inference0.0581%；E3 reset70.106%、physics21.192%。T2-z不处理这些主耗时，本研究没有新的加速结果。半精度仍无有效增益结果；上游bf16不为当前PhysX/state半精度背书。依据现有 `reports/NEXT_ACTUAL_POST67_M3_FP32_PROFILE_CLOSED_V9_HALF_SCOPE_REPLAY67_WORK_ORDER.json`，JSON索引含实际文件SHA。

## 建议的未来最小实验：两条路线严格分开

### A. 优先方案：借鉴latent思想的轻量状态动力学，非原T2-z复现

只在另获离线建模授权后开展。先CPU检查现存冻结raw的时间戳、实际动作/processed target、状态和contact字段、环境配置/episode标识及覆盖范围；若缺稳定物理分组、多轨迹或独立测试配置，标数据不足，不追加新rollout。固定正式source67及其SHA，以既存数据索引取样，不复制大raw，不改actor/critic、PD、commands、2.5ms物理、成功门槛、预算或canonical。

对照必须包括：(1) pooled小型状态动力学；(2)同规模网络+32维latent，交替拟合；(3)同预算历史encoder；若已有数值参数标签，可另列只用于离线比较的oracle条件上界。三者同数据/优化预算/3 seeds，按物理配置和episode隔离训练/测试；测试同环境用K=1/2 support，query完全隔离，禁止用query未来或成功标签更新latent。比较S=0/5/10/40适配步，不能只报告support拟合误差。

评估query的1步、100ms、500ms状态误差，接触开始/脱离时刻误差，双轮真实顶面contact事件的漏报/误报、着陆高度和距缘联合误差、非有限率、p50/p95适配时间及峰值显存；按环境配对报告置信区间。离线误差改善只证明预测作用，不称技能毕业或PPO样本效率改善。预先建议进入下一阶段的研究标准：关键query预测误差相对pooled降低≥10%、接触误报不恶化，并在3seed方向一致；这些是新研究对照决策标准，绝非追加当前生产训练门槛。

**计划成本估计，未运行：** 初始10万到100万已存transitions、≤100万参数，CPU数据审查；若获授权使用一张已实际释放的4090，整个比较上限2 GPU小时，数据/派生索引与小模型上限1GB，不追逐完整训练收敛。算例：100万×64个float32字段约256MB（仅数组），真实字段/压缩/I/O另算。若上限内不收敛或数据不足，如实no-go/unknown；不借第三卡unknownpeer，不影响当前专家。CPU可行性与耗时、真实raw字段和独立物理配置数量均待数据审查，不能当已完成。

只有离线结果支持时，才另行申请小规模冻结策略环境验证；那一步需要单独明确rollout预算、环境数、候选安全边界及真实contact验收。本次没有运行它。

### B. 原T2-z视觉复现：后续独立高成本方向

需要另批两份预训练资源下载、磁盘容量/许可证检查、同步RGB与H1实际动作数据采集和适配器、task-conditioned world-model训练及硬件试载。先做单任务小样本的显存/40步latent适配/5query测量，与Standard视觉world-model同数据同预算比较；再决定是否值得完整训练。原文2×H200×24h是参考预算，不是本项目可承诺的4090小时数。没有H1训练数据和任务微调时，仅对BWM优化新z不应视作获得H1动力学。

未来较合适的阶段是：H1已经能按真实接触标准稳定完成台阶技能，之后面对跨地面摩擦/负载/接触环境变化且能取得交互证据时，做慢速环境辨识、离线候选策略筛选；如果最终要高频部署，再另立小模型蒸馏/状态适配研究，并重新验证控制接口。当前“起跳高度时机与前移距缘未对齐、crank常clip”的已知问题，没有证据由未知环境因素主导；引入5B视频模型会增加新的数据、域差和资源问题。

## 实际执行与记录边界

本阶段只读取本地规则/已有报告及官方GitHub API、固定commit源码、arXiv HTML；未clone、pip、下载模型/数据、执行上游代码、GPU/PhysX/SSH、外部通信或修改生产。源码HTTP只在内存读取，文件SHA随引用索引保存。Git由父任务统一唯一annotated trial归档并核验远端；此报告落盘时状态为 **LOCAL_REPORTS_PENDING_ROOT_GIT_ARCHIVE**，不能称已经入Git。

本次读取错误保留：Python管道调用exit1且无输出（改用PowerShell官方HTTP）；项目站点web不可访问（改用同作者官方代码和论文）；PowerShell临时变量误用自动$Matches导致Hashtable追加错误（改名重读）；M3槽键初查e3为空，实际键为recovery并已更正读取。它们不是训练失败，也没有制造新的训练trial结果。具体记录在JSON，原失败不改写为pass。
补充读取错误（原文不覆盖）：在整理引用哈希时，GitHub tree API返回HTTP403 `rate limit exceeded`（工具chunk 5c4dfb），该次JSON生成在写出前失败，未产生残缺JSON。停止API重试，改为固定commit raw内容直接计算SHA256及git blob SHA1；raw200已确认（chunk 80ec76）。不继续请求API、不下载仓库或模型。最终引用索引不声称完整下载/逐行审阅整个仓库；目录清单曾用于定位，关键文件与关键段单独定向读取，个别广范围输出曾被工具截断。
明确答复24小时：这是用任务交互数据离线训练动作条件世界模型和环境latent，使模型后来能适应新环境；不是训练机械臂策略/PPO，也不是每个新环境均耗24小时。新环境冻结世界模型，仅优化32维z40步。18.09秒包括适配与5个query视频生成，不是适配单项。

引用索引补充更正：第二次生成在local路径数组包装处失败（chunk8f29dc），内存源码SHA256未落盘；随后一次超长Windows命令在创建进程前被拒（os206），未执行或写出。最终索引保留固定commit、全文raw链接及已取得git blob SHA1；源码SHA256未知即unknown，不再扩张请求。本地文件与最终Markdown实际计算SHA256。前文所说源码SHA256随索引保存是原计划，此处明确其未最终保留的实际状态。