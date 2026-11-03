# SuperMimic原论文与当前MOD4v1 BPTT适配：逐项核对 V1

审计日期：2026-11-03。结论针对实际qualified A1训练源，不把本地vendor或民间复现称为作者官方代码。本次没有热改训练器、改物理/DR/验收或启动新GPU训练。

## 结论先行

**有需要纠正的实质性问题，但不是“根本没有做BPTT”。** 当前的短时WM→action/state→reward/critic反向传播主链基本成立；真正高优先级问题是我们改造后的模型/观测/上下文闭环与论文定义不一致，尤其是：

1. 将已经带噪声/延迟的raw35和动态队列/事件放进context，一步监督context head，却在actor里连续递推它；这不等价于论文的“确定性模型输出noise-free observation、展开每步显式重新加入传感噪声”。
2. WM state做k8展开时每步使用真实动态xi，actor却用自己的aux预测xi；state、reward、obs、done四条链没有按论文Eq.1共同在k8自回归预测链上对齐。
3. 借用了去平移/yaw的平地特征，而我们的任务包含台阶/坡/波形地形；实际接口没有显式地形几何输入，必须排查状态可识别性，而不是只增加训练量。
4. frozen teacher + `.05 * unbounded residual` 是自定义迁移架构，不是论文原控制器；冻结teacher不约束总policy的漂移。真实保存回放已显示E3有大残差和动作饱和，且独立原技能评测没有收益。

上述1、2是已核对的结构差异，3是有源证据的高优先级风险，4的架构/数值事实已确认。**没有把它们直接升级为“已经证明是全部技能失败的唯一原因”。** 当前继续保留原mother/Registryv12/H1，不为凑更新数继续同一legacy方案。

## 1. 实际查到哪篇，代码来源是什么

- Qiayuan Liao, Yiyang Shao, Junfeng Long, Kevin Zakka, Roberto Horowitz, Pieter Abbeel, Koushil Sreenath：**SuperMimic: Scaling Humanoid Whole-Body Control with One Differentiable World Model**，CoRL 2026，arXiv **2610.28480v1**，2026-10-20提交。[原论文页](https://arxiv.org/abs/2610.28480) / [原PDF](https://arxiv.org/pdf/2610.28480v1) / [原TeX源码](https://arxiv.org/src/2610.28480v1)。
- [官方项目页](https://supermimic.github.io/) 与[作者主页](https://qiayuanl.github.io/)相互指向同一论文。作者SuperMimic条目有Webpage/Paper/Video，目前本次检索没有找到作者确认的公开训练代码链接。GitHub中带Reproduced/mjlab/vibed等名字的仓库不能据名称当官方。
- 当前 `supermimic_vendor_v2` 是本地实现来源；本报告以实际源和论文对照，而不是假定该目录名能证明“完整官方复现”。
- 已保存 [PDF原件](<research/supermimic_arxiv_v1_20261103/paper.pdf>) 3,524,904B，SHA `fe213017ab062f4acc3965da89abd3c29969163e144a2628a662b8ce46691009`；arXiv source gzip 2,901,561B，SHA `256a25330dbd7a7f4ebbc56228a57e6f426c9f155f1e7ace81e0a9d78a6292ab`。只作参考数据，未执行任何下载源码。[下载收据](<research/supermimic_arxiv_v1_20261103/PRIMARY_DOWNLOAD_RECEIPT_V1.json>)。

## 2. 论文原方法的关键约束

### 2.1 确定性模型、noise-free观测、外部传感噪声

论文§3.1–3.2明确：

```text
s_hat[t+1] = f(s_hat[t], a[t], xi_episode)
o_bar[t]   = g(s_hat[t], xi_episode)       # noise-free
policy_input[t] = o_bar[t] + eta[t]       # 每个imagined step重新采传感噪声
```

`xi`是episode级物理随机化参数，如摩擦、校准偏差、torso COM；已知随机性不让确定性WM自己去拟合一个随机采样结果。论文并非“没有DR或噪声”，恰恰把它们分解了。其训练噪声表包含joint q±.01rad、qd±.5rad/s、IMUω±.2rad/s、gravity±.05。

### 2.2 k8自回归多头模型拟合

论文§3.2 Eq.1从记录s0出发，沿记录action自回归k=8：

```text
L_WM = sum_j [state_error_j^2 + reward_error_j^2
             + noise_free_obs_error_j^2 + BCE(done_pred_j, done_j)]
```

各head可以是learned，也可以是analytic；analytic head没有该loss。因此**使用learned reward/done本身并不违反论文**，但其训练输入、目标、展开分布要匹配。原文没有公开到底哪些head在最终运行中用analytic/learned的完整实现细节，不能凭推测补齐。

### 2.3 BPTT与critic

论文§3.3 Eq.2：

```text
c[0]=1; c[t+1]=c[t]*(1-d[t+1])
J=sum_{t=0}^{H-1} gamma^t*c[t]*r[t+1]
  + gamma^H*c[H]*V(s[H],g[H],xi)
```

只在actor backward内固定WM参数；不切断state/action输入梯度，WM每个iteration仍会更新。Eq.3的critic target为：

```text
R[H]=V[H]
R[t]=r[t+1]+gamma*(1-d[t+1])*((1-lambda)*V[t+1]+lambda*R[t+1])
```

同一imagined rollout产生target，一次计算后固定拟合critic；**没有EMA target critic**。默认H32，论文§4.3也展示有critic的H16可工作，无critic的H16失败，H128更慢且最终回报更低。因此不能说“H16必错”，也不能把H32/H128当直接修复。

原文证据：[Method](<research/supermimic_arxiv_v1_20261103/text_sources/sections/method.tex#L68-L117>)、[Algorithm/超参](<research/supermimic_arxiv_v1_20261103/text_sources/sections/appendix.tex#L145-L240>)、[H消融](<research/supermimic_arxiv_v1_20261103/text_sources/sections/results.tex#L205-L208>)。

## 3. 当前哪些地方是对齐的

实际A1训练使用worker `7c4298…`、core `260330…`（resume版8116只分拆loader，训练函数同源）、bridge `821196…`、Raw35 wrapper `bb7555…`。不能拿尚未安装native的deepcopy修复20fd版本冒充当时训练源。

|检查|实际代码结论|
|---|---|
|真实sim收集、WM拟合、policy交替更新|有；不是直接微分PhysX，也不是只有WM-only/BC|
|state/action跨时间反传|没有发现整体detach切断主链；实际optimizer step有future→s1→a0有限非零VJP和参数变化|
|actor时固定WM/aux/critic参数，保留input梯度|有；这是正确固定方式，不应改成整个rollout no_grad|
|soft survival + gamma尾部critic bootstrap|有；不是纯16步贪心reward sum|
|imagined λ return与一次固定targets|与Eq.3主式一致，γ=.99/λ=.95|
|actor Adam β(.9,.95)|一致|
|actor global grad norm1，随后value clip.1|一致；不能误报“没梯度裁剪”|
|critic不使用EMA target|与论文一致，不应照民间教程任意补EMA|
|history10 / latent32|主要维数一致；论文latent32的tanh不是给每个action residual加.05硬界|
|实际deployable A1 actor|Raw35ActorMDP覆盖base，obs=xi[:35]，offset0；旧A0 privileged路线另记，不混淆|

源入口：[实际worker](<source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py#L66-L98>)、[core actor/critic](<source_core_review/ctx_reward_learner.py#L376-L491>)、[base bridge与residual](<source_runtime/native_supermimic_bridge.py#L51-L82>)。

## 4. 已确认差异与优先级

### P0-A：动态、含噪、延迟raw35被放入xi，观测闭环与论文不同

实际bridge把**已带100Hz噪声/延迟的原raw35**直接拼入xi；还拼contact history、torque、PD/执行延迟队列和部分phase等。当前Raw35ActorMDP.add_noise是identity，防止真实采样时二次加噪，这点本身正确；问题发生在imagination：head递推这个raw35，而非重建noise-free observation后通过原采样/延迟过程生成新obs。

因此当前不是论文的 `o_bar(s)+eta` 语义。**修复不能只是把identity改成random noise**，否则real采集会二次加噪，且50Hz端点不足以还原两个100Hz反馈采样/lag；需要新的clean-target与动态sensor queue接口，沿原反馈时序，不减弱原DR/noise。

### P0-B：模型拟合与actor展开面对不同的context分布

[继承WM k8](<../supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source/supermimic_vendor_v2/learner.py#L244-L271>)每步喂真实 `contexts[:,j]`；state递推是多步，但xi是teacher-forced。新增[aux训练](<source_core_review/ctx_reward_learner.py#L337-L353>)只在真实s/s1上做一步r/done/context-delta监督；[actor rollout](<source_core_review/ctx_reward_learner.py#L388-L406>)却连续用WM state和aux产生的xi。

这在xi仅episode固定物理参数时不构成差别，但我们的xi含动态传感/队列/phase。由此多出一条没有在同分布k8链上训练的自回归反馈。它是比“再多做多少次actor update”更优先的适配问题。

### P0-C：平地对称特征与地形任务的状态可识别性

本地geometry.invariant_features去掉绝对x/y/yaw，仅保留height、去heading的R、body速度与q/qd。实际E3/W35 context_layout没有显式terrain geometry/tile/heightmap/raycast/scene-id；原论文实验是flat ground，数据过滤还排除需要地形/物体交互的motions。

对台阶/坡/波形地形，同样body状态和action可能因前方/脚下几何不同而有不同下一状态；contact history只提供部分历史。**已确认的是无显式几何接口，不是已证明所有输入无任何代理信息或已经发现同输入异target。** 先查Markov/aliasing，再决定把地形相对信息/已存在时序加入模型，不偷偷改变原机器人观测/物理/任务。

### P0-D：残差架构没有技能保持约束

当前动作是 `clip(teacher+.05*residual_logits,-6,6)`，不是 `teacher+.05*tanh(...)`，更不是“最多偏离teacher .05”。论文原控制器/共享decoder与goal encoder并非我们这条output-residual迁移结构；teacher冻结不等于整体policy冻结或受信赖域限制。

真实记录history上的E3 scaled residual RMS已有6.96和11.49；这是比.05大很多的实际量。此前unbounded候选normal6物理term6/6，而teacher与零更新bound为0/6，提示保持性应优先验证，但不同natural cohort与zero-update probe不能单独证明因果。bound probe本身也未改善原技能，不把“加tanh”宣布为已证修复。

### P0-E：任务指令、phase、timeout的语义

- E2真实 `vx=2V*cos(heading-worlddir), vy=0` 随heading变；imagination保持command_*，没有按预测heading更新同一原任务指令。这是已知语义缺口，不是调学习率能解决。
- W35原BODY命令在自然resample前保持是正常的；其问题是可能跨12–16s resample边界的clock/抽样语义，不得与E2混为一谈。
- 当前done监督合并term|trunc，imagined概率同时影响reward survival和bootstrap。需核对原task timeout是否应切尾；论文没有给出我们Isaac任务的timeout规则，暂列适配待核验，不武断说“论文必须把timeout分开”。
- 恢复frames确实+1，recovery字段也非普遍held；不再使用“所有恢复阶段都冻结”这一错误概括。

## 5. 超参与训练预算：确有缩减，但不是越大越对

依据原论文App.D Table A.5与actual worker：

|项目|论文默认1GPU|当前实际A1|
|---|---:|---:|
|sim env数|4096|1024|
|每env replay steps|1000|128|
|WM window|8|8|
|WM batches×windows|10×2048|4×512|
|actor rollout batch|4096|512|
|H|32|16|
|critic结构|256,128|256,128（结构一致）|
|critic epochs×minibatches|5×4|2×2|
|WM结构|2048×3|512×3|
|学习率|2e-4|1e-4|
|探索action noise std|.1|.08|
|UTD / policy:model ratio|.4 / 1|.4 / 1|
|cosine schedule|250000迭代至.03倍|继承lr_decay_iters=250000；计划iterations=100000不改变该常数|
|两GPU|同模型data-parallel梯度平均|不同专家独立process/不同WM，不是同一个policy两卡同步|

WM窗口/iteration数量当前2048、原文20480，相差10倍；actor imagined steps当前512×16=8192、原文4096×32=131072，相差16倍；replay总容量131072与4096000相差31.25倍。critic每次4次而非20次optimizer step，H16对尾值更依赖，需优先评估critic质量。

这些是预算/架构差异，不足以证明“小就一定失败”。原文用了H100，不应把其3h/9.8h与4090八专家独立任务直接对标；也不应为了论文320000迭代而绕回“只把更新数堆满”。先修闭环，再按显存/预算确定可验证的规模。

## 6. 我们已有的真实诊断支持什么、不支持什么

[实际CPU保存回放诊断](<ACTUAL_REPLAY_CONSISTENCY_FINDINGS_V1.md>)读取两份own complete各一次，模型/aux/pi冻结，whole-root值/版本/RNG不变；原模型未被训练或改写。每角色one-step64、actor64、H16 matched32windows。它是posthoc/resubstitution，不是heldout，不测actor新动作反事实。

|量|E3|W35|
|---|---:|---:|
|一步真s1奖励头MAE|.00615|.00288|
|原reward样本std|.13613|.00970|
|H16 q MAE conditional→FULL，rad|.13455→.16732|.06851→.08390|
|H16 sensor16 MAE conditional→FULL，缩放obs单位|.03259→.06633|.03121→.05611|
|H16累计reward MAE conditional→FULL|.04955→.08071|.03099→.03936|
|done正例|1/64|0/64|

说明闭环context递推会额外累积误差，且原actor有实际漂移；不证明WM Jacobian在真实sim上正确/错误。传感误差含不可约观测噪声，需噪声floor对照，不能拿它直接与物理验收阈值相比较。W35无done正例，低Brier不证明终止识别。论文自己也只保证surrogate的解析梯度，Eq.1并不包含Jacobian matching，因此“VJP非零+一步loss小”不是技能或梯度质量保证。

此前三组合格原技能：E3均0/74；W35moving teacher19/63、unbounded10/69、bound14/60，standing26/26、16/17、13/22。仍保母，不作相对/因果提升，不把postprocessing效果当训练收益。

## 7. 最小修正顺序（目前是方案，不是已修好）

1. **固定基线与方法测试。** 保留现有全部母本/候选/失败。明确新branch类型和source pins，验证Eq.1/2/3、小系统真实梯度/critic targets、clip/clock/terminal规则。既有正确BPTT主链不推倒重来。
2. **先修模型接口与时序。** 把episode静态DR参数、动态delay/feedback队列、任务phase/command clock与noise-free sensor分层；缺的clean100Hz采样只能新增被动source捕获，不从旧noisy raw35伪造，也不额外抽噪声。核对非平地可识别性/E2真实参考系。
3. **对齐多步模型闭环。** state与learned reward/clean-obs/done在同一k8预测链上联合训练或等价分阶段校准，训练时不再把未来真动态xi当actor能得到的输入。终端physical-before-reset和所有invalid/streamcut正确保留。
4. **再做受控策略更新。** critic先完成原任务尾值/timeout与真实数据校准；依据模型误差决定H16/32，不先延长到H32/128。残差/anchor/actor结构是独立因素，不能把加tanh、改reward、换H、提高batch一次混入。若新view/策略重置，计数/Adam与checkpoint lineage如实重建，不拼旧训练量。
5. **原技能独立复测决定继续。** 只选择1–2角色有限段，保存、close/wait/结算释放再测。先确认normal/standing保持，再看恢复/运动/越障原accepted predicate，多seed、完整失败与partial；没有改进就停，不以论文标题、loss或更新数代替质量。

好的C878/S135继续先做独立seed保持评测源码准备，不为计数扰动。E3 signed-upright单因素候选仍enabled=false/κ=null；这次论文核对没有批准它或启动native训练。

## 8. 公开信息未披露，暂不补猜

原文未给出最终训练代码中的完整state分量/维数、哪些head最终analytic/learned、所有归一化规则/物理action clip/squash数值、warmup细节及我们的Isaac timeout对应规则。官方训练仓库本次未找到。不能将民间EMA、某个wrapper或本地vendor默认提升为论文authority。

主来源：[论文v1](https://arxiv.org/abs/2610.28480)、[项目页](https://supermimic.github.io/)、[作者页](https://qiayuanl.github.io/)。章节与具体TeX行、实际实现源行及本次独立审计产物一并保留在当前研究目录。所有方法调整尚待独立新版本实现和原技能证据，没有修改现有physics/DR/接受阈值或声称RM70实场已验证。
