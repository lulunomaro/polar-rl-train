# SuperMimic 原论文—本地 vendor—实际 A1：独立 source-only 审计 V1

## 0. 结论先行

**实际 A1 具有真实的多步可微 actor–world-model BPTT 主链；主链的 survival、bootstrap、critic λ-return、梯度裁剪和 Adam β 并未发现所述公式级错位。但是，这不足以判定 surrogate 梯度适合原物理任务。最应优先核查的是：新增 learned heads 只做真实状态对的一步监督，却在 H16 中与动态/含噪 context 联合递推；`.05` residual 并非幅度上限；以及 terrain/command/termination 的任务闭环语义。**

已证实的是源码机制与差异，尚未证实的是哪一项导致真实失败。本文没有重新打开 PT/raw、没有执行 audited 模块、没有运行模型、训练或物理环境。所有新产物仅在当前新审计目录。

三层来源严格分开：

1. **原论文 primary**：[arXiv:2610.28480v1](https://arxiv.org/abs/2610.28480v1) / [项目页](https://supermimic.github.io/)；本地原始 TeX 的 [method][PM]、[appendix][PA]、[results][PR] 由父会话下载解包，本审计直接读取对照。
2. **本地 vendor**：[learner][VL]、[networks][VN]、[replay][VR]、[geometry][VG]、[contract][VC]、[包说明][VI]。本地未找到 README/来源元数据，也没有已证的官方仓库链接。该目录只能称本地 vendor，不能提升为官方实现。
3. **实际 A1 路径**：[qualified worker][W] → [resume core][RC] / [训练 core][C] + [native bridge][B] + [Raw35 wrapper][A]。已有 CPU posthoc 的 deep-copy loader 不是当前 native 已安装版本。

## 1. 固定范围、哈希与版本一致性

- 技能 catalog 只有 Office/PDF/ACL；本任务是纯源码/TeX/JSON/MD 审计，不匹配这些技能。采用 read/glob/grep + 本机标准库 AST/哈希，不安装依赖。
- 工作区 `F:/RMPOLAR-RL`；只新建本报告、结构化 JSON 与 [AST 证据][AST]。没有 SSH、SDK/GPU 查询、PT/raw 读取、训练、Git、锁、预算 canonical 或旧封件修改。所有模型、母本/H1、原物理 DR、原接受条件保持原状。
- [qualified worker][W] SHA256 `7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7`。
- [训练 core][C] SHA256 `2603308f1adfe65f576eaf2aa3e0275d8465f110e6edd6e3db38304bf3e72039`。
- [resume core][RC] SHA256 `8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac`。
- [native bridge][B] SHA256 `8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29`。
- [Raw35 wrapper][A] SHA256 `bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223`。
- 标准库 AST 对比结果：上述两份 core 的所有共有函数除 `ContextRewardLearner.load` 外 AST 相同；resume 仅增加 `ContextRewardLearner.load_full_checkpoint`；其 body 等于旧 `load` 去掉 payload 读取首语句后的 body。训练、loss、rollout、norm、optimizer、replay 方法没有 AST 差异。该结论可将原 core 行证据用于实际 resume 训练机制，但不是运行时导入/安装的再次证明。11 个 Python 源均 AST parse 成功，详见 [AST 证据][AST]。

## 2. 原论文明确支持什么：先纠正容易混淆的判断

- [method:78–92][PM78] 明确：WM 的 reward、observation、termination head **可 learned，也可 analytic**；learned heads 的 loss 出现在 k=8 autoregressive windows 中；analytic head 没有对应 loss。因此“采用 learned reward/done”本身不是偏离原论文。本地 vendor 选择 analytic reward/soft termination 只是其自身实现选择。
- [method:72、78、98–99][PM72] 将观测分成 noise-free observation 与模型外采样的已知 sensor noise；模型条件为每 episode DR context。训练本身有 POMDP/DR/观测噪声。[appendix:18–22、119–125][PA18] 给出噪声及摩擦/校准/COM 随机化。
- [appendix:343–357][PA343] 的 friction=1、无 DR、无 obs noise、deterministic physics 只用于 benchmark；不是原训练的限制。129514 条为 training-motion coverage，不是 heldout 泛化证明。
- [method:96–117][PM96]：默认 H32；冻结 WM 权重只在 actor backward 内，仍对输入求导；critic imagined-only λ-return、固定一次目标、无 EMA target critic。[appendix:172–183][PA172] 明确 WM 和 policy 每轮更新。
- [results:208][PR208] 的 ablation 支持带 critic 的 H16，不支持把“我们的 H16”直接判成 bug；原任务中无 critic 的 H≤16 失败，也不是本任务的自动因果解释。

## 3. 高优先级问题清单（事实强度与因果强度分开）

|ID|问题|已观察证据|判断与置信度|
|---|---|---|---|
|F01|新增 reward/done/context heads 只有真实状态对的一步监督|[core:337–359][C337] 每次 state WM update 后另做 `sample_transitions`；aux 用真实 `s,s1`，未经过 k8 predicted-state/context rollout|**确定差异，高置信**。paper 的 learned heads 应在 autoregressive windows 上拟合；这使 actor 使用的 closed-loop head 输入/Jacobian 缺直接多步监督。尚无失败因果证明。|
|F02|noise-free observation + fresh noise 的分解被 noisy/delayed raw35 的确定性 delta 预测替代|[bridge:98–130][B98] 存实际 noisy/delayed raw35；[Raw35:190–200][A190] identity slice/noise；[core:395–407][C395] 递推 raw context|**确定机制，高置信**。不是单纯“少加噪声”：动态随机观测进入 ξ 并自回归预测。具体噪声条件分布、100Hz clock 与 delay queue 可观测性仍待证。|
|F03|`.05` teacher residual 没有输出幅度约束/anchor|[bridge:70–82][B70] `teacher + .05*delta`，只有总动作 clip6；[发布 CPU 结果:33–34][D33] E3 第二/三分量 scaled residual RMS 6.96/11.49|**确定机制+已发布实测，高置信**。零初始化仅保证起点；不能把 scale 当 ±.05。clamp 饱和与越出 teacher 分布是强排查方向，不是物理失败的充分解释。|
|F04|将 dynamic ξ 当静态部分 held，并有角色相关 reference/command 语义缺口|[worker:73–76、94][W73] held raw command/height/modes/command_*；[core:395–407][C395] 不更新 held 字段|**确定机制，高置信；影响角色条件化**。E2 body/world command 随 heading 的 evolution 不等价于 held；W35 BODY vx 通常可 held，不能混用 E2 指控。边界/重采样覆盖待证。|
|F05|terrain/scene 的 Markov/alias 风险|[实际 E3 layout:910–1003][DE910]、[W35 layout:910–991][DW910] 无显式 terrain geometry/heightmap/tile；[geometry:169–183][VG169] 去掉 x/y/yaw|**明确接口事实，高置信；Markov 不足为风险而非已证漏项**。contact18/torque/raw35 可能携带代理信息，但不能自动等于前方 Curb/Slope 几何。未构造同输入异后继的冲突对。|
|F06|reset probability 的 label 合并 physical term 与 timeout trunc|[bridge:142–144][B142] `done=term|trunc`；[core:163–175、265][C163] BCE 用 done；实际 MDP 没有 `imagination_timeout`|**确定代码，高置信；任务错误判定中等/未知**。若 trunc 是外部 time limit，合并会提前消掉 bootstrap；若本来就是任务结束则可合理。需按原 timeout 语义区分；paper 未给可直接照搬的 timeout 处理细节。|
|F07|资源/统计配置显著缩小，同时仍依赖 critic 和复杂上下文|[worker:84][W84] vs [paper Table A5][PA203]：WM windows/update 为 2048 vs 20480，actor transitions/update 为8192 vs131072；critic4次 vs20次 optimizer minibatches|**确定参数差异，高置信；效果因果未知**。这不是“只把原方法挪个任务”，但也不是缩小即必错。未做受控容量/数据/critic 对照。|

### 3.1 F01/F02 的具体闭环为什么比“梯度非零”更重要

本地 state WM 的 [k8 rollout][VL244] 每步使用日志 `contexts[:, index]`，并只对 predicted physical state 计算 loss。原来 ξ 若是每 episode 常量，这样做与固定 ξ 一致；现在 ξ 还含 raw35、torque、queue、phase 等动态量，它成为实际 teacher forcing。

新增 aux 的 [features/loss][C135] 是 `inv(s), inv(s1), a, a_prev, normalized_xi, seconds` → reward、delta-context、done-logit：reward/context 做 z-MSE，done 做自然无权 BCE；context loss 仅用非 done 且 xi1_valid 的样本。它的训练输入是**真实状态对**，而 actor 中的 [aux 输入][C390] 是 `s_hat, WM(s_hat,a,xi_hat), a, ..., xi_hat`。aux 没有多步闭环校正训练，也没有用 WM-predicted s1 直接拟合这些头。

于是 actor 的 H16 使用了一个训练中未联合展开过的 `state_hat ↔ noisy-context_hat ↔ policy` 闭环。未来 reward 对 first action、甚至经过 state-transition 的 VJP 非零，只验证路径存在；不能验证状态/观测/reward/done 的 Jacobian 与真实任务一致。低 one-step value MSE 也不约束 off-support action Jacobian。该表述既不把 learned heads 判错，也不把梯度回执当性能证明。

### 3.2 F04：reference/command 的已知事实与边界

原 motion-tracking 论文使用未来 K10 reference frames；velocity interface 可用 command3，并非每个任务都必须 K10。[appendix:30–33、131–137、435–444][PA30] 说明接口和共享 decoder 训练方式。我们实际 goal 是 `xi[:3]`、goal_frames1、history10，是独立 teacher+residual task adaptation，而不是论文 joint motion/velocity encoder 的逐项复现。

实际 worker 把 raw35[:4]、14:16、22:35 及静态 DR/`command_*` 清零预测 mask；legacy projector 只覆盖 14:16=0、22:28=current action。[Raw35:202–239][A202] 虽定义较新 transition/reward projection 方法，**当前 core 未调用这些方法**；`transition_projector=None` 也没有让旧 core 抛错，因为旧 core 查询的是代理到 base 的 `project_predicted_context`。文件里“存在新语义”不等于实际 A1 已使用。

E2 的 `vx=2V*cos(heading-world_direction)` 随 predicted heading 演化，held 当前 body command 是已知近似，不是修复；本审计读取的候选 [e2_command:57–74][A57] 给出该区分，但未执行/安装。W35 BODY vx 在通常持有窗口中可以是常量；父会话指出其 12–16s resample 边界须单独覆盖。当前 A1 `valid_imagination_start_with_context` 全 True，未按这些边界筛选或精确推进，源码不足以证明所有 H16 起点均无边界。

### 3.3 F05：terrain 与状态不变性

原 [flat-ground 数据过滤][PA282] 去掉 stairs/boxes/ladders/chairs 等 terrain/object 依赖动作。该前提下移除绝对平面位置/yaw 有合理对称性。我们 bridge [pack][B89] 虽存物理 root position/rotation，但 WM、aux、critic 都通过 `invariant_features` 输入：只保留 height、去 yaw 的 orientation6、body v/ω、q/qd。**“状态包里有 x/y”不等于网络真的接收 x/y。**

已发布 E3/W35 layout 实际有 contact_history18、torque30、DR、action-delay pending/applied、feedback delay、PD 等；E3 有 time_left 与 recovery5，W35 有 command direction/heading/time_left。没有命名的 terrain mesh/tile/heightmap/scan/scene conditioning。原观测 mode 或接触也许能间接提示地形；因此这里只确认接口缺少显式几何，不把“Curb/Slope 一定发生了同输入异目标 alias”写成事实。地形对物理动力学/未来接触与 yaw/position 的依赖，需要保持 actor raw35 不变、仅从 WM state/context 足够性角度继续核实。

## 4. World model：target、loss、normalization 逐项

|项|本地 vendor 与实际 A1|与论文的关系/结论|
|---|---|---|
|预测对象|[networks:116–163][VN116] 为 local one-control-step increment：heading-frame Δp、body SO(3) log、body Δv/Δω、Δq/Δqdot，再 denormalize 与 integrate|实际继承该 state model；没有查到把 derivative 当 increment 或漏乘 dt 的证据。target 本来就是一帧差，而非每秒导数。论文未公开这些局部 target/坐标的完整实现细节。|
|state target 帧与集成|Δp 用当前 yaw frame；ΔR=`log(R_t^T R_next)`；Δv/Δω 用当前 full body frame；回写用相同当前 frame|[state_error:165–191][VN165] 用真值帧衡量 integrated state 的误差，未发现前后帧对不上。不能把 reward tracking frame 的问题混到此处。|
|输入/输出 norm|[RunningNorm:34–70][VN34] running mean/var，max_count=2e8，输入 eps=.01，输出 eps=1e-4；collect 在真实 executed-action transitions 更新|identity `normalize_context` 之后仍有整体 WM `in_norm`，不是完全未归一化；aux 又有自己的 `in_norm`。paper 未给足数据来认证这些 eps/max_count 为官方默认。|
|k8 state loss|[learner:244–271][VL244] autoregressive predicted state，logged actions + true per-step xi；error/std 平方后 mean feature、sum valid time / batch|std=max(out_norm.std,err_floor)。floors依次为pos .003、rot .005、v .02、ω .05、q .003、qd .05。loss 未按有效步数再平均；这是 vendor 原生机制，不是新增 aux bug。|
|损失尺度|[learner:355–365][VL355] 返回 loss/k；logged metric 与训练 target norm 含其具体实现|paper 的公开公式是 sum state/reward/clean-observation/BCE；[results:81][PR81] 说 plotted state prediction error 用 predefined nominal error。没有官方代码/完整 normalization recipe，不能把论文的 0.007–0.011 与本报告 posthoc rad/m 单位 MAE 直接对比。|
|新增 heads|[core:135–175、337–359][C135] one-step real pairs；独立 aux Adam，每 state WM update 后一次|learned heads 是 paper 允许项，但该一步/多步训练域差异是 F01。reward 已保留原 environment r，包括原 cost；这里没有另造论文 motion reward、BC/KL/anchor reward。|

## 5. Actor BPTT 与 critic：保留的正确机制、待证内容

### Actor

实际 [worker:66–69][W66] 安装 `Raw35ActorMDP(..., transition_projector=None)`，因此 actor 每帧只取 `xi[:35]`、goal只取已知 command3、history10、offset0；privileged WM/critic context suffix 不进入 actor。不能用 base `OriginalTaskMdp.obs` 的全状态拼接指控实际 A1 actor 泄漏。MDP 的物理 joints30/action6 由显式 action_dim 分开，网络并非错误地要求30个控制输出。

[core:376–440][C376] 每一步重新计算 action → WM.step → aux → next_context → next_obs/history → next goal。states、contexts、actions 没有逐步 detach；仅 replay 初始 history no_grad 合理。`frozen_parameters` [178–189][C178] 临时冻结 WM/critic/aux 参数并恢复原 requires_grad，**没有 no_grad 截断输入梯度**。norm 在 actor rollout 内不 update。teacher wrapper eval/frozen 且其调用外无 no_grad；所依赖 rsl_rl MLPModel 内部 forward 本审计未读，不能超出 wrapper 保证其全部 input-autograd 语义。

`alive=cumprod(1-dones)`，当前奖励权重为 `[1,alive[:-1]]`，终点 bootstrap 为 `γ^H*alive[-1]*V_H`，对照 [method Eq2][PM100] 无 off-by-one。current terminal transition reward 被计入，后续生存与 bootstrap 被抑制。

actor trainable 参数用 Adam β(.9,.95)，[core:439–440][C439] 先 global norm1，再 elementwise .1，与 [paper Table A5][PA210] 相同。教师参数不进新 trainable optimizer。已有回执额外测 delayed reward/bootstrap→a0 和 state-transition VJP，是图连通性审计，不是梯度可信度或任务学会的凭证。

### Critic

[core:459–489][C459] 只用 imagined transitions，递推 `R_t=r_(t+1)+γ(1-d_(t+1))*((1-λ)V_(t+1)+λR_(t+1))`，seed `R_H=V_H`；targets 在 no_grad 中只算一次并固定，shuffle 后拟合。γ=.99、λ=.95、critic global clip1、无 EMA target，与 [method:109–117][PM109] 一致。当前 epochs2×minibatches2 小于 paper5×4 是配置差异，不是缺失 critic。

critic 的输入有 invariant physical features + 全 context + episode frame/1000 + goal，属于 privileged critic；这与**actor 没有 privileged leakage**并不冲突。critic 与 aux 的 train support、calibration、gradient 质量仍未由源码或少量 replay 测试认证。

### Action clipping 与 teacher

- [bridge:70–82][B70] 零初始化 residual 输出层；latent 有 tanh，[vendor Policy:218–222][VN218] 的 action decoder 没 tanh；`.05` 不是 residual cap。总 action clip[-6,6] 在 wrapper 与 imagined step 都出现。
- [collect:318–327][C318] action+Gaussian(.08) 先外 clip20，再由 [bridge.step][B142] clip6；replay 与 norm 使用 bridge 记录的 clip6 raw manager command，不是探索前动作、不是延迟后的 torque。动作噪声在 clip 边缘被截断，这是已知分布改变，不是“数据没记 executed action”的错误。
- clipping 之外是否有 native action-manager 中的进一步变换，需原任务语义证据；本审计没有把 manager command 与最终物理 torque 混为一谈。

## 6. Termination、cut、timeout 与 replay

- [bridge:93–95、142–144][B93] 在原 termination compute 后、reset 前抓 physical s1；terminal transition 的 r/done/state target 保留，xi1 用 mask 排除 reset 后 context。新 state 接 reset state、previous_action归零。没有发现将 reset state 当 terminal s1 的源码证据。
- [core:74–114][C74] `done=term|trunc` 做一致性检查；k8 mask 包含 terminal/cut 当前 transition，只排除其后的 reset/断流行；resume stream_cut 不伪装为真实 done。`sample_starts` [vendor replay:79–102][VR79] 以真实 ep_step/可见 age 左侧重复补齐，既不是强制零 history，也没有通过省略 valid terminal 来回避失败。
- 实际 base MDP 对 imagination start 全返回 True，没实现 `imagination_timeout`；core 虽有 hook，并未因此自动获得真实 timeout。done head 拟合的是 reset 概率含 trunc，不一定等于 physical failure 概率。若外部 timeout 仍该 bootstrap，要保留与物理 term 分支；若 timeout 是目标结束则另论。论文未详述此具体桥接，F06 不能凭通用 RL 习惯直接定罪。

## 7. 完整主要配置对照

|项目|论文 primary / 本地 vendor|实际 qualified worker|解释|
|---|---|---|---|
|WM hidden|2048,2048,2048|512,512,512|缩小容量；非默认复现|
|actor encoder/decoder|2048,1024,512,256|512,256,128 residual + frozen teacher256,128,64|自定义 teacher-residual adaptation|
|critic hidden|256,128|256,128|一致|
|history / latent|10 /32(tanh)|10 /32(tanh)|一致|
|goal|motion K10；velocity cmd3+history encoder|cmd3，goal_frames1|任务接口变化，不应强制套motion K10|
|k / H|8 /32|8 /16|H16+critic 有论文 ablation 支持，仍需本任务证据|
|WM sampling|10×2048 windows|4×512 windows|每 iteration windows 为1/10|
|actor sampling|4096×32|512×16|每 iteration imagined transitions 为1/16；批数不是独立模型样本保证|
|critic epochs×minibatches|5×4|2×2|optimizer mini-steps 为1/5；当前 batch 总暴露也更小|
|replay per env|1000|128|较短历史覆盖；是否不足待证|
|LR单GPU|2e-4|1e-4|全部 optimizer 使用同一当前 LR|
|LR schedule|cosine to .03 over250000 thenconstant|继承同函数，按真实 iteration 而非BPTT计数|匹配形式；计划100000轮并不等于250000轮衰减完毕|
|UTD / policy:WM outer updates|.4 /1|.4 /1|collect accumulator 平均2.5控制步/轮；4个WM minibatches+4个aux，再1个actor|
|γ / λ|.99 /.95|.99 /.95|一致|
|action noise|Gaussian .1|Gaussian .08 后clip6|探索配置变化；paper说明探索可选|
|global gradient clip|WM1，actor1再.1，critic1|相同；aux额外1|不是缺少clip|
|WM-only warmup|paper未详列；vendor500|100|仅能确认vendor差异，不编官方warmup默认|
|training length|paper320000|cfg100000，另由目标BPTT步数/stop条件停止|不是本审计执行计划|
|EMA target critic|明确无|无|正确；不混淆网络weight averaging|

配置来源：[paper Table A5][PA203]、[vendor defaults][VL34]、[worker:84][W84]、[core train loop:571–594][C571]、[cosine:530–535][VL530]。若同样按较早 iteration 停止，cosine 仍接近初始 LR；这与 residual 越界可并存，但不存在“查看 schedule 就已证明优化不稳定”的推论。

## 8. 已发布真实结果如何约束解释

只引用 [CPU posthoc报告][D]，没有重开模型/replay。其 resubstitution 不是 heldout、不是 actor 新动作反事实；完整 H16 选择无 done/cut/invalid survivor 窗口，因此还没检验失败边缘/跨边界 rollout。

- E3 FULL H16：q MAE **.167317 rad**、rotation **.0262374 rad**；raw sensor16 MAE **.066328**，conditional为 **.0325883**。
- W35 FULL H16：q MAE **.0838976 rad**、rotation **.0238579 rad**；raw sensor16 MAE **.0561137**，conditional为 **.0312125**。
- E3 scaled residual RMS 第二/三项 **6.9595 /11.4883**；总动作 saturation第二/三项 **.5625 /.984375**。W35 residual更小，但这不是跨任务可比的因果对照。
- reward one-step MAE：E3真s1 .0061548、WM-s1串联 .00546448；W35 .0028826/.00320529。E3样本reward std .136134，W35 .00969654。误差均值小不等于 action/state Jacobian 对，更不等于 actor out-of-support 可信。
- done正例 E3 **1/64**、W35 **0/64**；低Brier/ECE不能代表失败正类识别/终止梯度校准。
- 用户/父会话提供的原世界质量：E3 teacher/candidate/bound 均 **0/74**，normal6 physical term分别 **0/6、6/6、0/6**；W35 moving **19/63、10/69、14/60**，standing **26/26、16/17、13/22**。single seed、独立自然cohort；不推相对提升或因果。原接受标准继续保留。

这些结果支持“优先核对完整 state+context 闭环与 residual support”，不支持把它们改写成已经定位根因、模型从未学到动力学、critic无效，或小步 loss 很好所以训练正确。

## 9. 后续核查优先级（仅提出；未实施）

1. **先固定闭环语义**：区分物理 static DR、可推演动态 state/context、随机 sensor/feedback queue 与 exogenous command；核对 clean target + fresh-noise/100Hz delayed-sample 构造。实际 actor 仍保持原 raw35，不向 actor 注入 WM/terrain truth。
2. **验证 surrogate 而非只读梯度范数**：在独立冻结评测设计中对 heldout one-step、full H16、failure-edge、command边界分开测 state/observation/reward/done；再测小动作扰动的 value/directional derivative 一致性。现有 source-only审计并未执行这些测试。
3. **并列核对 residual/support 与 head训练域**：记录 deterministic residual/output saturation、原cost分量；比较同起点/同目标的冻结诊断，再决定是否需要受控新候选。当前 bound 文件/新 projection 定义不能当作实际已生效。
4. **核对 terrain Markov 条件与 timeout 语义**，在现有任务/DR/acceptance不变的前提下先证明是否存在模型输入混叠；不要凭flat-ground论文结果删地形、降DR、改终止、改母本。
5. 之后才有依据进行容量/critic fitting/sample exposure 的单因素复测。单独续跑更多 BPTT updates 不是本报告给出的结论。

### 明确未知

官方源仓库链接与原 normalization/target 实现细节；本地 vendor 的来源；rsl_rl teacher内部forward input-grad；实际 raw35 sensor噪声/100Hz feedback queue 完整时序的可推演性；terrain alias 是否真实发生；每个 trunc 项的任务语义；head/critic/action Jacobian 的真实一致性；多 seed 和 heldout 原技能通过率。它们均不由本审计偷偷补成假定值。

[PM]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/method.tex>
[PA]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/appendix.tex>
[PR]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/results.tex>
[PM72]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/method.tex#L72-L99>
[PM78]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/method.tex#L78-L92>
[PM96]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/method.tex#L96-L117>
[PM100]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/method.tex#L100-L115>
[PM109]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/method.tex#L109-L117>
[PA18]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/appendix.tex#L18-L125>
[PA30]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/appendix.tex#L30-L137>
[PA172]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/appendix.tex#L172-L183>
[PA203]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/appendix.tex#L203-L236>
[PA210]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/appendix.tex#L210-L224>
[PA282]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/appendix.tex#L282-L321>
[PA343]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/appendix.tex#L343-L357>
[PR81]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/results.tex#L81>
[PR208]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/research/supermimic_arxiv_v1_20261103/text_sources/sections/results.tex#L208>
[W]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py>
[W66]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py#L66-L69>
[W73]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py#L73-L94>
[W84]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py#L84>
[C]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py>
[RC]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/ctx_reward_full_resume_candidate_v2.py>
[C74]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L74-L114>
[C135]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L135-L175>
[C163]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L163-L175>
[C178]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L178-L189>
[C318]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L318-L327>
[C337]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L337-L359>
[C376]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L376-L440>
[C390]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L390-L398>
[C395]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L395-L407>
[C439]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L439-L440>
[C459]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L459-L489>
[C571]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py#L571-L594>
[B]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py>
[B70]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L70-L82>
[B89]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L89-L95>
[B93]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L93-L95>
[B98]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L98-L130>
[B142]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L142-L144>
[A]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_command_review_v1/command_tracking_torch_candidate_v1.py>
[A57]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_command_review_v1/command_tracking_torch_candidate_v1.py#L57-L74>
[A190]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_command_review_v1/command_tracking_torch_candidate_v1.py#L190-L200>
[A202]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_command_review_v1/command_tracking_torch_candidate_v1.py#L202-L239>
[VL]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/learner.py>
[VL34]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/learner.py#L34-L62>
[VL244]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/learner.py#L244-L271>
[VL355]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/learner.py#L355-L365>
[VL530]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/learner.py#L530-L535>
[VN]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/networks.py>
[VN34]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/networks.py#L34-L70>
[VN116]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/networks.py#L116-L163>
[VN165]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/networks.py#L165-L191>
[VN218]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/networks.py#L218-L222>
[VR]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/replay.py>
[VR79]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/replay.py#L79-L102>
[VG]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/geometry.py>
[VG169]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/geometry.py#L169-L183>
[VC]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/contract.py>
[VI]: <F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/__init__.py>
[D]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/ACTUAL_REPLAY_CONSISTENCY_FINDINGS_V1.md>
[D33]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/ACTUAL_REPLAY_CONSISTENCY_FINDINGS_V1.md#L33-L34>
[DE910]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/ACTUAL_SAVED_REPLAY_CONSISTENCY_E3_V1.json#L910-L1003>
[DW910]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/ACTUAL_SAVED_REPLAY_CONSISTENCY_W35_V1.json#L910-L991>
[AST]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_paper_code_audit_v1/SOURCE_AST_EVIDENCE_V1.json>
