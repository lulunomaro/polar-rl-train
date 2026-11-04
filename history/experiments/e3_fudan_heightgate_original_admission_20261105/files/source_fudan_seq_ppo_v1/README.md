# E3 Fudan sequence-PPO：独立 Torch core v1

这是 **MOD4/E3 容量与接口适配**，不是“复旦官方起身代码”或原样复现。
方法参考固定提交 [8204e853](https://github.com/yly-true/fudan_rl_wheel_leg/tree/8204e853dfd2ed06d85a322e1a998c3d20a3be2c/jump/wheel_legged_gym/rsl_rl)：历史编码、PPO/encoder分阶段、critic存下的latent、超参及timeout兼容式。仅依赖Python标准库和Torch，无IsaacGym/NumPy/TensorBoard导入。

## 网络与分支语义

- obs35；history175=5×35，顺序旧→新、含当前帧；worker维护同原任务的尺度/噪声/延迟，core不重复归一化或加噪。
- encoder175→128→64→3；显式用物理机体系线速度(m/s)×3监督。
- actor [obs35, stopgrad(z3)]→256→128→64→action_dim；默认action_dim=6，worker须按实际动作数显式确认。
- critic [priv38原序, stored_z3]→256→128→64→1；PPO期间使用**收集时**latent，不经encoder反传。
- log_std为独立可学习参数，初值log(.5)，不是复制旧std；相对上游direct-std属于参数化适配。
- warm_start仅接受两个完整旧MLP state：`mlp.0/2/4/6.{weight,bias}`；完整验证35/38输入及256/128/64隐藏层，再复制全部层。仅第一层扩列，新增z列置零；无tensor别名、不读旧Adam、不继承旧计数，不改变DR。分支标记NEW_BRANCH_WARM_START，所有计数从0开始。
- 本地明确修正：两个optimizer各自clip自身参数（main1，encoder.1），每阶段清除两组残留grad；完整保存两Adam、模型、计数、独立generator状态。不得称上游原样行为。

## 公共接口

```python
from fudan_seq_ppo import PPOConfig, SequencePPO

learner = SequencePPO(PPOConfig(action_dim=6), device="cpu")
receipt = learner.warm_start(actor_state, critic_state)
collected = learner.act(obs, history, privileged_obs, deterministic=False)
# collected: actions[N,A], values[N], log_prob[N], mu/sigma[N,A], latent[N,3]
tail_value = learner.value(tail_privileged_obs, history=tail_history)  # [N]
# Alternatively: value(privileged_obs, stored_latent=z)
prepared = learner.prepare_rollout(rollout, tail_value)  # optional inspection, no mutation
metrics = learner.update(rollout, tail_value)            # pass ORIGINAL rollout, not prepared
checkpoint = learner.state_dict()                       # detached independent copies
learner.load_state_dict(checkpoint)                     # same config; both Adam + RNG + counters
# evaluate(obs, history, priv, stored_latent, actions): gradient-enabled actor/critic path
# encoder_loss(history, body_velocity): encoder-only supervised path
```

## Rollout dict schema

全为Tensor，T/N一致；float字段按float32复制到learner.device，不修改调用者输入；done字段必须bool。

| key | shape | 语义 |
|---|---|---|
| obs | [T,N,35] | act之前当前部署观测 |
| history | [T,N,175] | 与obs同一时刻的5帧，旧→新 |
| privileged_obs | [T,N,38] | 母版critic原输入原顺序；不擅自重排 |
| body_velocity | [T,N,3] | 同时刻真实机体系速度，物理m/s，**尚未×3** |
| latent | [T,N,3] | act返回的收集时z |
| actions | [T,N,A] | 策略实际采样值，须与所存log_prob一致；物理clip由worker原链处理 |
| values, log_prob | [T,N] | act返回的pre-step V_t和采样动作log概率 |
| mu, sigma | [T,N,A] | 收集时高斯均值/正标准差 |
| rewards | [T,N] | 原任务reward，**尚未timeout补偿**；core不另行缩放 |
| dones, time_outs | [T,N] bool | timeout是done的子集；不得把bool语义混成浮点概率 |

`last_values[N]`是T之后的tail V（使用该时刻priv/history）。done环境该尾值会被遮断。T=48由native worker负责；core允许短功能检查，要求T*N能被mini_batches整除，不静默丢样本。

## 更新与终止语义

默认gamma=.99、lambda=.95；5epochs×4minibatches；ratio/value clip=.2、entropy=.01、value coef1；main Adam lr=.001，desiredKL=.005，阈值上/下2倍时lr÷/×1.5，范围[1e-5,.01]；encoder Adam独立固定lr=.001。先全部PPO批，再全部encoder监督批。优势在整个rollout上以sample-std(+1e-8)归一化；每阶段各自的一次随机排列跨epochs复用。

`timeout_bootstrap_rewards(rewards, values, time_outs, gamma)`明确实现上游兼容：`r_t += gamma*V_t*time_out_t`，这里是收集时**pre-step V_t**，不是terminal_obs的值。随后GAE仍由done切断。`prepare_rollout/update`内部补偿一次，worker勿提前重复补偿。`compute_gae`独立helper接受已经补偿的reward，返回未归一化advantages/returns。

计数分别为updates、policy_optimizer_steps（main Adam，含actor/critic/logstd）、encoder_optimizer_steps、transitions_seen。每次真实optimizer.step成功返回即记账，后置finite参数检查失败也保留该step；失败不伪造完整update。返回有限梯度、参数L2变化与独立step数；这些不是native迭代、技能收益或原预算继承。

## 唯一小CPU功能检查

```powershell
& 'C:/Users/lulu/Desktop/claude/mjcf/.venv/Scripts/python.exe' -B 'test_functional_cpu.py'
```

N8/T8、2epochs×4minibatches，使用完整容量但全为合成权重与数据；检查暖启动均值/value等价、z列零、两梯度方向分离、finitegrad/参数变化、timeout/GAE、输入无alias修改及两Adam+RNG恢复后继续一致。仅在内存序列化合成状态，不读写实际PT。输出同目录小JSON；失败保留，不自动重试。一次脚本内包含primary两次update与restored一次等价继续，所有计数仅为CPU功能证据。

结果状态：唯一一次CPU执行PASS（Torch2.14.0+cpu，N8/T8，2×4）。暖启动mean/value最大误差均0；首update main/encoder各8步且参数变化有限非零；两Adam+generator恢复后继续的完整状态逐tensor一致；调用者输入与checkpoint无alias修改。encoder合成MSE .009707→.002964，仅为功能证据。primary两次update共main16/encoder16步，restored从8/8恢复后再各8步；所有实例实际共main24/encoder24步。小JSON已保留，不重跑。

core、测试及README均为新文件，未改旧源、物理、DR、任务奖励或native worker；没有native训练/评测或实际checkpoint读取。
