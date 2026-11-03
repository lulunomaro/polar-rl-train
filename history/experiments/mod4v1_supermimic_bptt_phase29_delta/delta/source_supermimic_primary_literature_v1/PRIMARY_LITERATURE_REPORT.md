# SuperMimic 一手文献核验与 BPTT 算法证据

核验日期：2026-11-03（Asia/Shanghai）。任务：独立核实原论文与官方来源、形成供父代理对照实际实现的证据表；本报告没有读取或诊断本地训练 actual，也没有推断根因或声称修复。

## 1. 精确论文、版本、作者与代码身份

- **标题**：*SuperMimic: Scaling Humanoid Whole-Body Control with One Differentiable World Model*。
- **作者，按原顺序**：Qiayuan Liao；Yiyang Shao；Junfeng Long；Kevin Zakka；Roberto Horowitz；Pieter Abbeel；Koushil Sreenath。UC Berkeley。Shao/Long 为 equal contribution，Abbeel/Sreenath 为 equal advising。
- **arXiv**：`2610.28480v1`，提交时间 **2026-10-20 16:29:30 UTC**。本次访问的 submission history 只列 v1；官方 API 的 published/updated 也均为该时间。
- **官方摘要与版本页**：[arXiv abs](https://arxiv.org/abs/2610.28480)、[固定 v1](https://arxiv.org/abs/2610.28480v1)。
- **固定 v1 PDF**：[arXiv PDF](https://arxiv.org/pdf/2610.28480v1)。
- **实际用于算法逐行核对的一手源码**：[arXiv v1 TeX source archive](https://arxiv.org/src/2610.28480v1)。本地保留了[原始源包][archive]、[原始 PDF][pdf]和解包后的 TeX；没有执行 TeX 或其中任何代码。
- **项目主页**：[supermimic.github.io](https://supermimic.github.io/)。arXiv comments 与作者本人主页互相指认此页。
- **第一作者主页交叉核对**：[Qiayuan Liao](https://qiayuanl.github.io/)。其 SuperMimic 条目链接 Webpage/Paper/Video，没有 Code 链接；其 BeyondMimic 等其他条目有单独 Code 链接。
- **会议信息**：arXiv comments、项目页、作者主页均写 CoRL 2026 Oral；本报告没有独立取得会议 proceedings 条目。
- **官方训练 GitHub：`unknown / not found in checked primary sources`**。项目主页和论文没有训练仓库链接；作者主页没有 SuperMimic Code 链接；[GitHub public repos API](https://api.github.com/users/supermimic/repos) 本次返回 `[]`。这些证据支持“本次未找到作者公开链接的训练仓库”，不证明全球不存在其他公开/私有仓库。
- **浏览器 demo 不是官方开源训练代码的替代证据**：[官方 demo](https://supermimic.github.io/demo/)、[其官方 license](https://supermimic.github.io/demo/LICENSE.html)。license 将 HTML/JS/WASM、policy/world-model parameters、architecture/configuration 等列为 UC Berkeley proprietary materials。这里只使用其公开页面陈述核对代码发布性质，没有下载模型或逆向 demo。

### 1.1 名称与来源消歧

本次精确名称/title 检索只确证上述 `2610.28480` 这一 SuperMimic 论文身份，没有找到可核实的另一篇同名论文。检索结果中多个仓库是这篇论文的民间复现，而不是另一篇同名论文或官方实现，例如：

- [CuboiLeo/SuperMimic-Reproduced](https://github.com/CuboiLeo/SuperMimic-Reproduced)：搜索结果和其 README 自述 independent/from-scratch reproduction。
- [YHFone/supermimic-mjlab](https://github.com/YHFone/supermimic-mjlab)：自述 reference implementation；没有作者官方链接背书。
- [NPCLEI/mjlab_supermimic](https://github.com/NPCLEI/mjlab_supermimic)：自述 reproduction。
- [miao-org/awesome-supermimic](https://github.com/miao-org/awesome-supermimic)：资源列表，非原论文/官方训练代码。

本报告不以这些仓库、博客或本地 vendor 填补原论文未说明的细节。**SuperTrack、SuperDyno、DeepMimic、BeyondMimic 是相关但不同的方法**；论文 §2 明确列出并区分它们，见[相关工作原文][related]。

## 2. 最重要的原方法结论

1. 原法是 **online collect → fit world model → BPTT improve actor/critic** 的反复联合训练，不是先用别的策略预训练世界模型后长期冻结。每个 iteration 更新模型和策略；模型只在当前 actor backward 内固定。证据：§3.1、§2，以及 Algorithm A.1。[方法][m70]；[相关工作][related55]；[算法][a169]
2. **模型拟合是 `k=8` 的 autoregressive logged-action 窗口**，而 actor imagination 是 **`H=32`**。两种 horizon 和训练数据生成方式不同。证据：§3.2 Eq.(1)、§3.3 Eq.(2)。[WM 拟合][m78]；[actor][m96]
3. **固定模型参数不是 detach 模型输入/输出**。原文明确 BPTT 要保留世界模型对 state/action 的 Jacobians。停止更新 ω 与切断 `s→a→f→s_next` 是不同操作。证据：§3.3、Algorithm A.1。[BPTT 原文][m107]；[算法][a169]
4. 原文的 reward/observation/done head **每个可以 learned 或 analytic**；没有披露该 G1 实例中每一个 head 的具体选型。已知 tracking reward 的公式，不等于已证实训练中 reward head 一定 analytic。证据：§3.2 的 unnumbered head equations 与 Eq.(1)。[原文][m78]
5. 原法用 **soft survival probability**，不是只在 imagined trajectory 上硬 threshold done；critic 用 imagined-only λ-returns，终点 bootstrap，targets 一次计算后固定；没有 EMA target critic。证据：§3.1、§3.3 Eq.(2)/(3)。[生存权重][m72]；[critic][m109]
6. 原法训练本身已有 **物理 DR + noisy partial observations**。其 deterministic world model 以已知 episode context ξ 为条件、预测 clean observation，再在 actor 输入重加 sensor noise。benchmark 的 no-DR/no-noise 是评测条件，不是训练条件。证据：§3.1–3.3、Appendix A/F。[方法][m72]；[DR][a44]；[benchmark][a343]
7. 原论文承认其 analytic policy gradient 是 **simulator expected return 的 surrogate gradient**，不是“真实 simulator 梯度无偏”的保证。预测 MSE 小也不是 Jacobian 准确性的独立证据。证据：§3.2 原句与 Eq.(1)、Figure 2 caption。[surrogate][m78]；[误差指标][r81]

## 3. World model：state、observation、context、latent

### 3.1 可直接确定的数学对象

论文 §3.1 使用 goal-conditioned POMDP：

- `s_t`：simulator state；可导出 proprioceptive observation `o_t` 与 termination `d_t`。
- `g_t`：goal；默认是 reference motion，其他 interface 可以是 velocity command。
- `a_t = π_θ(o_t, g_t)`：deterministic policy，输出 normalized joint-setpoint 参数。
- `o_t = ō_t + η_t`，其中 `η_t ~ ρ_η` 为已知 observation noise，在 world model 外采样。
- episode context `ξ`：friction、joint calibration offset、torso COM offset。

§3.2 给出的模型为：

```text
ŝ_(t+1) = f_ω(ŝ_t, a_t, ξ)
r̂_(t+1) = r_ω(ŝ_t, a_t, g_t)
ō̂_t     = g_ω(ŝ_t, ξ)
d̂_t      = d_ω(ŝ_t, g_t)
```

世界模型是 **deterministic conditional surrogate**：模型通过条件化 ξ 处理已知 simulator randomness，并拟合 noise-free observation。以上 head equation 是 §3.2 的未编号公式，不宜把它误标为 Eq.(1)。证据：[§3.1–3.2 原文][m72]。[arXiv 固定版本](https://arxiv.org/pdf/2610.28480v1)

### 3.2 State 表示与 latent 的证据边界

- Table A.4 仅确定 dynamics 为输入 `(ŝ_t, a_t, ξ)`、输出 `ŝ_(t+1)` 的 MLP `(2048,2048,2048)`。
- **精确 state 向量分量/维数、是否使用 delta-state、rotation representation、FK/kinematic integration 方式：unknown。** §3.1/3.2 与 Appendix A/C 没有给出足以唯一重建它们的定义。
- 论文没有给出 Dreamer/RSSM 式 stochastic latent dynamics、posterior/prior、KL 或 observation reconstruction encoder。相关工作 §2 反而把 Dreamer 的 latent dynamics 作为不同线路介绍。
- **`z ∈ R^32`、tanh bounded 是 policy goal encoder 的 motor latent，不是 WM latent**。Table A.4 规定 motion encoder 和 velocity encoder 输出 z，shared decoder 接收 z+observation history。[网络结构][a139]
- actor 公式不直接输入 ξ；critic 输入 `(ŝ_t,g_t,ξ)`，是 privileged/context-conditioned critic；WM 也直接输入 ξ。证据：§3.1、§3.3、Table A.4。[方法][m72]；[critic][m109]；[网络][a139]

### 3.3 Observation 与 goal

Appendix A/Table A.1：

| Observation term | 维数 | 每维 sensor noise |
|---|---:|---|
| `q − q0` | 29 | Uniform `[-0.01,0.01]` rad |
| joint velocity | 29 | Uniform `[-0.5,0.5]` rad/s |
| base angular velocity / IMU | 3 | Uniform `[-0.2,0.2]` rad/s |
| projected gravity | 3 | Uniform `[-0.05,0.05]` |
| previous action | 29 | 表中没有添加噪声 |

actor 接收最近 **10 frames** 的这些 observations。单帧 **93 维**是表中 `29+29+3+3+29` 的算术和，不是论文额外声明的 WM state 维数。motion encoder 接收 **`K=10` future reference frames**。Evidence：Appendix A 与 Table A.4。[observation/goal][a7]；[网络][a139]

## 4. World-model fitting：监督 targets 与 horizon

### 4.1 数据来源和 action 对齐

§3.1：simulator 在采样数据时执行 `a_t + ε_t`，replay buffer 保存 **实际执行的 noisy action**，不是只保存无噪声的 actor 输出。`ε_t ~ N(0,0.1²)` 每个 action dimension。action noise 是为了拓宽模型拟合的动作覆盖；原文明确其只服务于 model fit，且 optional。actor imagination 的策略映射仍是 deterministic（其输入可以含 sensor noise）。证据：[§3.1][m72]；[Table A.5][a203]

### 4.2 Eq.(1)

从 replay buffer 采样 `k=8` 连续窗口，只有初始预测 state 取 logged state `ŝ_0=s_0`；后续 **autoregressively** 用模型自己的预测 state 和 logged actions 推进，监督每一步 j=1…k：

```text
L_WM(ω) = E_B Σ_(j=1)^k [
  ||ŝ_j − s_j||²
  + (r̂_j − r_j)²
  + ||ō̂_j − ō_j||²
  + BCE(d̂_j,d_j)
]
```

- `r_j` 来自 simulator reward；`d_j∈{0,1}` 来自 simulator hard termination label。
- analytic head **没有其对应的 loss term**。
- 不是仅一阶 next-state prediction，也不是中间每步都用真 state teacher forcing 的描述。
- Eq.(1) 不包含 Jacobian-matching、uncertainty ensemble、latent KL、conservative model penalty 或 actor imitation loss。
- **未说明**：各物理分量的缩放/nominal-error weights、额外 feature weights、是否跨 reset 采窗口、terminal 后 mask、time-limit/truncation 与 true done 的区别、buffer warmup。

证据：§3.2 Eq.(1)，[原文 78–92][m78]；[Algorithm A.1][a169]。[在线原始源包](https://arxiv.org/src/2610.28480v1)

## 5. Actor BPTT：objective、展开、stop-gradient

### 5.1 rollout 机制

§3.3：从 replay-buffer state 和其 recorded ξ 初始化；每步：

```text
o_t = ō̂_t + η_t,          η_t ~ ρ_η
a_t = π_θ(o_t, g_t)
ŝ_(t+1) = f_ω(ŝ_t,a_t,ξ)
```

模型拟合用 logged actions，actor rollout 是 **当前 policy on-policy imagination**；二者不要混同。`H=32` 大于 `k=8`。world-model weights 在当前 actor update 固定，在下一轮 model phase 继续更新。证据：[§3.3][m96]；[Algorithm A.1][a169]

### 5.2 soft done / continuation 与 Eq.(2)

§3.1 定义：

```text
c_0 = 1
c_(t+1) = c_t (1 − d_(t+1))
```

simulator 记录 hard done；model 提供 `[0,1]` 的 predicted termination probability，使 imagined `ĉ_t` 保持可微。actor 最大化：

```text
Ĵ(θ) = E [ Σ_(t=0)^(H−1) γ^t ĉ_t r̂_(t+1)
            + γ^H ĉ_H V_ψ(ŝ_H,g_H,ξ) ]
```

这是 §3.3 **Eq.(2)**。重要时间索引：即时 `r_(t+1)` 乘的是 `c_t`，terminal 后的 continuation 才乘 `(1−d_(t+1))`；不应无意改成即时 reward 也乘 `c_(t+1)`。[§3.1][m72]；[Eq.(2)][m96]

### 5.3 梯度到底穿过哪里

原句：“BPTT computes a first-order gradient … through the H imagined steps via the world model's Jacobians with respect to ŝ_t and a_t.”

据此可直接核验的数学条件：

- 保留 `∂f_ω/∂s`、`∂f_ω/∂a`，以及返回 `ō̂` 到 actor 输入、reward、soft continuation 到 objective 的依赖路径。
- `ω` 不因 actor objective 更新；这不是将 `f_ω(...)` 包成整个 `no_grad`，也不是把 `ŝ_(t+1)` 每步 detach。
- 对 `∇_θ Ĵ`，ψ 是独立的 critic 参数；Eq.(2) 中 terminal value 对 `ŝ_H` 的路径仍属于 θ 梯度。若把整项 `V(ŝ_H)` 的输出 detach，则删去了 Eq.(2) 所表达的 terminal-state value gradient；具体框架 flag 写法原文未披露。
- reward 和 done 若用 learned head，同样应在 actor objective 中提供状态/动作相关梯度；但原文没有给出每一个 head 的具体实现。
- **critic λ-return 是 critic fitting target，不是原文 actor objective 的替代品**。actor objective 是 Eq.(2) 的 H-step discounted return+terminal bootstrap；不是 PPO likelihood-ratio 或 advantage-weighted log-prob。

证据：§3.3 Eq.(2)、BPTT 段落、Algorithm A.1。[Eq.(2)/BPTT][m96]；[算法][a169]

### 5.4 scope 与模型偏差

§3.2 原文直接称其为：“the gradient of a surrogate for the expected return in simulation”。因此“analytic”只说明对 learned surrogate 可做解析反传，不是对真实 simulator 梯度/真实策略改善的理论保证。Eq.(1) 的值误差监督没有显式保证 Jacobian 精度；本论文没有提供针对任意 task/长 horizon/隐藏随机因素的统一 guarantee。[原文][m78]

## 6. Critic：λ、bootstrap、done、固定 targets

§3.3 **Eq.(3)**：

```text
V_t = V_ψ(ŝ_t,g_t,ξ)
R̂_H = V_H
R̂_t = r̂_(t+1) + γ(1−d̂_(t+1)) [ (1−λ)V_(t+1) + λR̂_(t+1) ]
L_V(ψ) = E Σ_(t=0)^(H−1) (V_t − R̂_t)²
```

- `γ=0.99`，`λ=0.95`。
- returns **只从 imagined transitions** 向后计算。
- `R̂_H = V_H`：horizon truncation bootstrap；termination gate 放在 future return 上。
- targets **每个 rollout 计算一次，在 ψ fitting 时固定**。
- 原文明确 **no EMA target critic network**。
- critic 每 update **5 epochs**，每 epoch **4 shuffled minibatches**。
- exact target-detach API、是否 detach rollout features、time-limit 单独 bootstrap mask：unknown；不要将未披露细节当作者实现事实。

证据：[§3.3 Eq.(3) 与后文][m109]；[Table A.5][a203]。[论文](https://arxiv.org/pdf/2610.28480v1)

## 7. Reward：定义可核实，head 选型仍 unknown

Appendix A/Table A.2 给出 BeyondMimic tracking reward 的修改版：

| Term | 公式摘要 | weight |
|---|---|---:|
| body position | exp(−mean tracked-body squared position error / 0.3²) | 1.0 |
| body orientation | exp(−mean `||log(R_des R^T)||²` / 0.4²) | 1.0 |
| body linear velocity | exp(−mean squared error / 1.0²) | 1.0 |
| body angular velocity | exp(−mean squared error / 3.14²) | 1.0 |
| root position | exp(−squared error / 0.3²) | 0.5 |
| root orientation | exp(−`||log(R_des R^T)||²` / 0.4²) | 0.5 |
| action smoothness | `||a_t − a_(t−1)||²` | −0.1 |
| joint limit | sum of upper/lower limit excess | −2 |

- 去掉 BeyondMimic self-collision penalty。
- joint-limit weight 从 −10 降至 −2。
- Table A.6 caption 明确 **Table A.2 与 A.6 的每个 term 都乘 control period `Δt=0.02 s`**。
- self-collision term 删除的原文理由：stochastic action noise 会出现 contact 压住动作噪声以提高 velocity reward 的利用方式；imagined policy deterministic，作者认为此项没有收益。
- **原文没有把“reward 公式可写出”与“实际 G1 r_ω head 是 analytic”画等号**。方法明确允许 learned 或 analytic；这里保留实现 unknown。

证据：§3.3、Appendix A/Table A.2、Table A.6 caption。[reward][a38]；[Δt][a275]。

## 8. Networks、action bounds、normalization

### 8.1 Table A.4

| Network | Inputs → output | hidden widths |
|---|---|---|
| dynamics | `ŝ_t,a_t,ξ → ŝ_(t+1)` | 2048,2048,2048 |
| motion encoder | 10 future reference frames → z | 2048,1024,512,256 |
| velocity encoder | normalized velocity command + observation-history feature → z | 256,256 |
| shared decoder | z + last 10 observation frames → a | 2048,1024,512,256 |
| critic | `ŝ_t,g_t,ξ → scalar`，每 interface 一个 | 256,128 |

z 为 **32-dimensional，tanh bounded**。非 latent 层的激活函数、初始化、normalization layers 没有在此表列出。证据：[Appendix C/Table A.4][a139]

### 8.2 Actions

Appendix A：`q_sp = α a_t + q0`。低 PD gains 使 setpoint 更像 joint torque proxy，而非 desired position。§3.1 称 a 是 normalized joint setpoint。

**unknown**：每关节 α 数值、PD gains 数值、a 的硬 bounds、decoder 末层是否 tanh、是否 clip noisy executed action、是否另作 action normalization。**唯一明示 tanh 的是 z**；不能由 z 的 tanh 推导 action 被限制在 `[-1,1]`。证据：[action][a35]；[latent][a139]

### 8.3 Normalization：已披露与未披露

已披露：

- a 是 normalized setpoint 参数，但具体 α unknown。
- velocity encoder 接 normalized command，但除命令范围外未给归一化算式。
- evaluation normalized return 是 episode undiscounted reward sum 除以其最大可能值，不是训练 reward normalization 说明。
- Figure 2(c) 的 state prediction error 除以 predefined nominal error；该 nominal error 的数值/逐分量构成 unknown。

未披露：WM state/target loss scaling、actor input running mean/std、critic return/value normalization、reward standardization/clipping、PopArt、normalizer frozen/update cadence。不能从“normalized return”图推断这些训练规则。证据：[§4 首段][r3]；[Figure 2 caption][r81]；[Table A.4][a139]

## 9. Training schedule、ratio、clip 与稳定策略

Appendix D/Table A.5 的原值：

| Group | Hyperparameter | Value |
|---|---|---|
| WM | fitting horizon | k=8 |
| WM | optimizer | Adam |
| WM | LR | 1 GPU: 2e−4；2 GPU: sqrt(2)×2e−4 |
| WM | batches per update | 10 batches × 2048 windows |
| WM | gradient clip | global norm 1.0 |
| actor | imagination H | 32 |
| actor | optimizer | Adam, β=(0.9,0.95) |
| actor | LR | same as WM |
| actor | batch | 4096 imagined rollouts/update |
| actor | gradient clip | **global norm 1.0，then element-wise 0.1** |
| actor | γ | 0.99 |
| critic | λ | 0.95 |
| critic | optimizer/LR | Adam；same LR as WM |
| critic | gradient clip | global norm 1.0 |
| critic | fit | 5 epochs/update，each 4 shuffled minibatches |
| collection | envs/GPU | 4096 |
| collection | action noise | N(0,0.1²) 每维 |
| replay | capacity | 1000 steps/environment，new replaces oldest |
| schedule | update-to-data ratio | 0.4 |
| schedule | policy updates / world-model update | 1 |
| schedule | LR schedule | cosine 至 0.03×，250000 iterations，然后 constant |
| schedule | length | 320000 iterations |
| multi-GPU | sync | data parallel，gradients averaged |

“10 model batches/update”和“1 policy update/world-model update”同时存在；不要把后者误解成每 1 个 WM optimizer minibatch 配 1 个 actor update。**UTD 的精确计数分母、每 outer iteration simulator 步数未进一步展开，不能仅由 0.4 唯一还原调度实现。** 证据：[Appendix D/Table A.5][a203]

### 9.1 Pretrain / warmup

- §2 明确 RWM/RWM-U 从其他 policy trajectories 预训练；SuperMimic 反之，在自己的 policy 所采数据上边训练边 fit WM。
- §3.1 与 Algorithm A.1 确定联合交替循环，而不是 paper 主方法要求的独立预训练阶段。
- **初始 replay 填充、warmup iterations、先收多少 transitions、初始 controller、是否特殊初始化：unknown。** 不要把“没有分阶段 pretraining”扩写成“第一个随机 minibatch 就立刻 BPTT 且无 warmup”。

证据：[§2][related55]；[§3.1][m70]；[Algorithm A.1][a169]

### 9.2 reset curriculum

Appendix D：motion timeline 分为 **1-second bins**，每 bin 记录从该点出发的 policy discounted return running estimate `G_b`。

- 50% uniform over bins；
- 40% `softmax_b(−25 G_b/G_max)`；
- 10% 按该 bin 历史 softmax weight 成比例采样，以保留已学过难动作的练习。

该机制训练的是 **simulator episode reset points**，不是已证实的 WM replay-window prioritized sampling。其 running-estimate 平滑系数/历史权重更新公式未披露。证据：[Appendix D.1][a188]

## 10. DR、noise、termination 与任务适配前提

### 10.1 原法训练是 noisy POMDP，但 stochasticity 被分离/条件化

- episode context：friction Uniform `[0.3,1.2]`；joint calibration offsets Uniform `[-0.01,0.01]` rad；torso COM offsets x±0.025m、y/z±0.05m。
- actor 只用 noisy proprioception+goal，带 10-frame history；world model 和 critic 可使用 logged ξ。
- 每步 clean predicted observation 外加已知 sensor noise。
- **不加入 BeyondMimic root-velocity pushes**：Appendix A 原文说其注入 state discontinuities，deterministic model 捕获不了；作者报告 physical-parameter DR 足以 sim-to-real。
- 外生事件/隐藏扰动/没有写入 ξ 的随机动态，和只加 observation noise 不是同一种建模问题。

证据：§3.2、Appendix A/Table A.1/A.3。[context/DR][a44]；[noise][a7]；[model][m78]

### 10.2 Motion tracking termination

Appendix A：root reference height deviation `|e_p,z| > 0.25 m` **或** tilt error `e_tilt > 0.8`。tilt error 是 reference/robot pelvis frame 中 gravity z-components 的绝对差；upright reference 时约 78°。不同于 BeyondMimic，**不因 end-effector deviation terminate**。证据：[Appendix A][a41]

### 10.3 Sim/task/data 前提

- MuJoCo Warp；50Hz control，4×5ms simulator substeps/control；WM 在训练用 TF32。证据：§4、Figure 4 caption。[results][r3]；[rollout benchmark][r197]
- 同一个 G1 body 的共享物理，所以大 motion library 不要求每个动作单独 dynamics model。
- dense motion-tracking reward 每步提供学习信号。§4 首段将稳定性归于这一点；“several seeds stable”是作者文字报告，图没有 seed variation。
- only flat ground；没有 terrain/object interaction。data filter 去掉楼梯、椅子、箱子等不可用交互与 retargeting infeasibility。
- BONES-SEED raw 142220 clips → name filter 129667 → feasibility 129514，约 264.56h；controlled LAFAN1 40 clips/2.45h。

证据：[§4][r3]；[Appendix E][a279]；[§6 limitations][limitations]。

### 10.4 评测边界，尤其避免混淆训练条件

Appendix F：129514 个 **training-set benchmark** motions，每个从 first frame 跑一次；friction=1.0、no DR、no observation noise、deterministic physics；各 policy 保留其各自 actuator gains/action scale/observation construction；失败使用 SuperMimic training termination。

所以失败数衡量 **training coverage，而非 unseen-motion generalization**；也不是 full-DR/noisy evaluation 成功率。这条不抹掉原法训练已有 DR/noise 的事实。证据：[Appendix F][a343]；[官网 benchmark footnote](https://supermimic.github.io/)。

## 11. 关键 counterevidence / 原论文的证据边界

### 11.1 “加长 BPTT 一定更接近论文或更稳定”不成立

§4.3 / Figure 3：

| H | final training return, no critic | with critic | 到 return .82 的小时数, no critic / critic |
|---:|---:|---:|---|
| 8 | .087 | .392 | 两者未达 |
| 16 | .250 | .843 | 未达 / 1.19 |
| 32 | .840 | .866 | 1.37 / .88 |
| 64 | .862 | .863 | 1.34 / 1.70 |
| 128 | .835 | .823 | 3.80 / 4.62 |

这些是原图 TeX 的确切 source coordinates，不是跨 seeds 的统计估计；training-episode return 的 initial-state 分布随 return-based reset sampling 变化，和固定 40 clips 的 checkpoint score 不同。H128 最长可放进 H100，但较慢且末值更低；default H32 最快。critic-free H32 可达相似 nominal return，却在 0.5–4m/s pushes 下持续 stumbling/4m/s fall；critic policy .5–2.4s settle。证据：[Figure 3 / §4.3][r115]、[原文描述][r208]。

### 11.2 “原法 world model error 小，故 actor gradient 正确”证据不足

Figure 2(c) 0.007–0.011 是 **8-step、state-only、按 predefined nominal error 归一化、online policy rollouts 测量**。它不是 reward/done head accuracy、Jacobian validation、32-step actor-horizon error bound 或 independent held-out generalization bound。原文 §3.3 对 indefinitely long stable rollouts 是经验陈述，并没有给同样长 horizon 的 gradient accuracy bound。证据：[Figure 2 caption][r81]、[§3.3][m96]。

### 11.3 “有 noise/DR 就偏离 SuperMimic”不成立

training physical DR 和 sensor noise 正是原方法内容；真正要比的是：stochasticity 是否被 logged ξ 条件化，noise 是否 clean/observation-external 分离，隐藏动态和 jump events 是否超出原假设。benchmark 的 no-noise/no-DR 不等于 training 无 noise/DR。证据：[§3][m72]、[Appendix A][a44]、[Appendix F][a343]。

### 11.4 “known reward 是必要条件”或“learned reward 必然偏离”均未被原文确立

论文 §3.2 明确允许 reward/observation/termination head learned 或 analytic。可以核实 simulator reward 的具体公式；G1 instance 的 actual head selection 仍 unknown。因此 learned reward 可构成模型梯度误差来源的待测假设，但不是仅凭名称即可下的论文一致性结论。证据：[§3.2][m78]。

### 11.5 “官方实现已验证民间技巧”没有来源链

未找到作者链接的训练 repo。民间实现里的 normalization、action clamp、state dimension、analytic FK、warmup、target nets、rollout masking 都只代表该实现，除非另有原文/作者一手证据。官方 demo 的发布形式不填补这一缺口。[项目主页](https://supermimic.github.io/)；[作者主页](https://qiayuanl.github.io/)；[demo license](https://supermimic.github.io/demo/LICENSE.html)。

## 12. 可供父代理使用的对照清单（不是实际代码结论）

| 若 actual 检查得到该现象 | 原论文证据关系 | 证据 |
|---|---|---|
| actor backward 时每步 detach state，或整段 WM no_grad | 与 full H-step state/action Jacobian BPTT 不同 | §3.3 / Eq.(2) |
| 只拟合 1-step / 中间 teacher forcing | 与 k8 autoregressive fitting 不同 | §3.2 / Eq.(1) |
| WM 无 recorded physical context，而 rollout 隐含随机物理 | 与 context-conditioned deterministic surrogate 前提不同 | §3.2 / App A |
| replay 保存 raw action，但 simulator 执行 noisy/clipped 的另一 action | 与存 executed noisy action 的记录对齐不同 | §3.1 |
| actor 有 sampled action noise / score-function PPO | 不同于 paper deterministic BPTT update | §3.1/3.3 |
| actor 只优化 λ-return/advantage log-prob，而非 reward+terminal value | actor/critic objectives 已替换 | Eq.(2)/(3) |
| done hard threshold 或 c 权重时间索引不同 | soft survival objective 已变 | §3.1 / Eq.(2) |
| critic target 每 minibatch重算，或没有 horizon bootstrap | 与 fixed rollout targets/R_H=V_H 不同 | Eq.(3) |
| critic EMA target net | 与原文 no EMA 不同；可能是适配选择，不自动证明错误 | §3.3 |
| no critic / very short H | 原论文已有失败/短视 counterevidence | §4.3 |
| learned reward head | 原方法允许；仅这一点不构成已证实偏离 | §3.2 |
| normalizer/action bounds/warmup 与民间 repo 不同 | 这些细节原论文未披露，暂时 unknown | App A/C/D |
| hidden stochastic events、稀疏奖励、terrain/object dynamics | 原论文成功条件未覆盖，需要单独证据 | §4 / App A / §6 |

### 12.1 多 interface / downstream adaptation 的额外 stop-gradient 边界

Appendix B、Algorithm A.1 与 Appendix G：

- 每个 interface 有自己的 encoder、reward、termination 和 critic，但共享 **同一个 WM 与同一个 action decoder**。
- motion-tracking objective 更新 motion encoder **与 shared decoder**。
- downstream objective 只更新该 interface encoder，**冻结 decoder weights，但保留 decoder 对 latent input 的 Jacobian**。这与 actor 更新时冻结 ω 却保留 WM state/action Jacobians 是两个不同的 stop-gradient 边界；不要误套为 motion decoder 总是冻结。
- 实验中 velocity encoder 与 motion policy **jointly from scratch** 训练 100000 iterations；4096 simulator env 与 imagined batch 各半分给两个 interface。Algorithm A.1 为清晰写 sample-one-interface，实际 joint experiment 用 mixed batch，脚注对此有说明。
- velocity command 50% 来自 reference，另 50% uniform `v_x∈[-1.5,2.0]m/s`、`v_y∈[-1.32,1.32]m/s`、`ω_z∈[-3.35,3.35]rad/s`；uniform-command 分支有 10% 概率 zeroed standing；reset 或 250 control steps（5s）重采样。
- reference command 用 centered 25-frame averaging；latent alignment MSE 权重 0.1，motion-latent target stop-gradient。distillation 比较使用 motion reward/done，而 velocity reward 条件仅 fall termination。每个 interface 从它自己 logged rollout states 起 imagined rollout。
- 作者说明 downstream encoder 因 decoder weights 不接收其梯度，concurrent training 与 main policy 后再 train encoder 在该意义上等价；但论文没有全面研究大量 interfaces 的共同训练。
- 每个 velocity variant 仅 one seed，作者称其 preliminary；这些结果不是任意 downstream sparse-reward task 的普遍稳定性证据。

证据：[Appendix B][a129]、[Algorithm A.1][a169]、[Appendix G][a432]、[§6 limitations][limitations]。

## 13. Unknown 清单

`official_training_repository`；确切 WM physical-state layout/dimension；delta-state 与 rotation/FK representation；G1 的具体 learned/analytic head 组合；state/input/reward/value normalizer；nominal-error 数值；per-joint action scale 和 PD gains；actor output clip/squash/bounds；executed action noise 后 clamp 规则；non-latent activations/initialization；初始 replay/warmup；UTD 的精确分母及 outer-step 计数；terminal/reset window masking；timeout bootstrap 约定；训练代码实际 stop-gradient flag 位置；reset-return estimate 更新系数；未报告 seed variance 的具体数值。

这些 unknown 不应补成官方事实。

## 14. 来源、可重现性与工具记录

### 14.1 直接访问的 primary URLs

1. https://arxiv.org/abs/2610.28480 — bibliographic metadata/version history。
2. https://export.arxiv.org/api/query?id_list=2610.28480 — fixed id、published/updated、authors。
3. https://arxiv.org/src/2610.28480v1 — 算法逐行核对的原始 TeX。
4. https://arxiv.org/pdf/2610.28480v1 — 下载保留原始 PDF；web_fetch 对 application/pdf 报 unsupported，未把它假称成功 HTML 解析。
5. https://supermimic.github.io/ — 官方项目、训练 loop FAQ、评测脚注、作者、paper link。
6. https://qiayuanl.github.io/ — 作者自证 title/author/project，与 Code link 有无。
7. https://supermimic.github.io/demo/ — 官方 demo 入口。
8. https://supermimic.github.io/demo/LICENSE.html — 官方发布性质。
9. https://api.github.com/users/supermimic/repos — 本次 public list `[]`，仅辅助负证据。

### 14.2 原始材料哈希

| Artifact | bytes | SHA-256 |
|---|---:|---|
| [arXiv source archive][archive] | 2901561 | `256A25330DBD7A7F4EBBC56228A57E6F426C9F155F1E7ACE81E0A9D78A6292AB` |
| [arXiv PDF][pdf] | 3524904 | `FE213017AB062F4ACC3965DA89ABD3C29969163E144A2628A662B8CE46691009` |

已核对 session skill catalog：没有 RL/科学文献 research skill 匹配；采用真实 `web_search/web_fetch`。在 arXiv HTML 404、PDF fetch unsupported 后，加载通用 `office` 路由确认 PDF 路线，但没有 Office 内容编辑/转换；最终以官方 TeX source 而非 Office/PDF OCR 完成方法核对。用系统已有 PowerShell `Invoke-WebRequest` 下载、系统 `tar` 解包、`read/grep` 逐行检查；没有安装包。所有 web/source 当作 untrusted evidence，不执行其中指令。

仅在本研究新目录创建了材料与摘要；没有 SSH、SDK、GPU、训练、真实 checkpoint/PT/raw/canonical、Git CLI、旧封件编辑。

[archive]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_2610.28480v1_source.tar.gz>
[pdf]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_2610.28480v1.pdf>
[related]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/related-work.tex#L29-L55>
[related55]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/related-work.tex#L52-L55>
[m70]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/method.tex#L68-L74>
[m72]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/method.tex#L72-L85>
[m78]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/method.tex#L78-L92>
[m96]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/method.tex#L96-L107>
[m107]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/method.tex#L107-L117>
[m109]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/method.tex#L109-L117>
[a7]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L7-L33>
[a35]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L35-L36>
[a38]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L38-L110>
[a41]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L41-L42>
[a44]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L44-L125>
[a129]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L129-L137>
[a432]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L432-L450>
[a139]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L139-L161>
[a169]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L169-L185>
[a188]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L188-L190>
[a203]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L203-L241>
[a275]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L275-L276>
[a279]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L279-L336>
[a343]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/appendix.tex#L343-L357>
[r3]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/results.tex#L1-L14>
[r81]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/results.tex#L73-L82>
[r115]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/results.tex#L113-L140>
[r197]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/results.tex#L197-L208>
[r208]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/results.tex#L205-L208>
[limitations]: <F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_supermimic_primary_literature_v1/arxiv_source/sections/conclusion.tex#L4-L9>
