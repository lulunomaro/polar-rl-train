# MOD4v1 SuperMimic 核心接入接口（SOURCE_ONLY）

## 交付边界

已提供可导入的 PyTorch 核心扩展与 teacher 残差 wrapper；本地只完成 AST/stdlib 验证。没有启动 Isaac、Torch、模型解码、GPU、SSH、原任务或训练。父负责原任务 EnvFactory、物理终态采样、原命令/奖励/DR、bootstrap 与 owner。

- 核心：[ctx_reward_learner.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/ctx_reward_learner.py>)
- 可选策略封装：[teacher_residual.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/teacher_residual.py>)
- 源码验证：[validate_source.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/validate_source.py>)

## 1. 核心入口

```python
class TaskLearner(ContextRewardLearner):
    def _make_policy(self):
        vendor_pi = super()._make_policy()
        return TeacherResidualPolicy(
            vendor_pi, parent_loaded_frozen_teacher,
            obs_ctx_offset=(13 + 2 * self.mdp.num_joints) + 6,
            residual_scale=0.05, zero_residual_output=True)

learner = TaskLearner(
    parent_bridge, cfg, parent_output,
    device=parent_bridge.device, backend='MOD4v1_original_task_reward',
    aux_hidden=(256, 256), aux_batch=cfg.wm_batch,
    policy_dt_s=0.02,
    predict_context_mask=None,  # default: learn every delta-xi; parent should bind groups
    require_exact_env_resume=False)
# cfg.compile=False, horizon>=2, iterations cap > warmup+3000+skips.
# Parent decides original-task reset/fullDR, N=1024/2048, asset and teacher identity.
result = learner.train(target_bptt_steps=3000)
# Owner must save(include_optimizers=True) in its finally/normal terminal lifecycle.
```

这里只展示连接方式，不是已经运行的任务。`parent_loaded_frozen_teacher` 由父的现有单次读取缓存提供，本模块没有加载路径/权重代码。新 opt_pi 是学生 optimizer；原 PPO optimizer 可以作为 bootstrap provenance 保留，但不移植到新学生。

**重要：不要构造后替换 opt_pi。** 扩展在 `_make_policy()` 返回后筛选 `requires_grad` 参数、建立 Adam、安装真实 step-post-hook；替换对象会丢失 hook。teacher 权重冻结但 forward 保留输入梯度。wrapper 不把 raw35 放入 vendor RunningNorm。

## 2. 环境 bridge 协议

```python
bridge.device                 # str or torch.device
bridge.num_envs               # actual fresh constructor N, not a fake 20k restore
bridge.supermimic_mdp          # task-owned MDP below
bridge.state                  # None or object with .info
bridge.init_state()           # object whose .info['supermimic_state'] is state-info
bridge.step(total_raw_action) # object with state-info + transition in .info
bridge.before_action()        # optional owner stop-before-action hook
```

### 当前 state-info

| key | shape/type | 语义 |
|---|---|---|
| `s` | `[N,13+2J]` float32 | origin-relative root xyz, quaternion **wxyz**, world linear/angular velocities, joint q/J and qd/J |
| `xi` | `[N,D]` float32 | 当前原始 actor35 在前35；原命令3、DR、延迟队列、phase/terrain/remaining time 等后续布局由父冻结并记录 |
| `f` | `[N]` long | 50Hz 当前控制时标；imagination 每步 +1，phase/command age 的其它语义在 xi 中显式记录 |
| `a_prev` | `[N,6]` float32 | 原 observation `last_action` 的同一 raw-command 语义 |
| `ep_step` | `[N]` int | 当前 episode 中已完成控制数；新 episode 必须为0 |

### 真实 transition

```python
transition = {
  's': before_s, 's1': actual_physical_before_reset_s1,
  'xi': before_xi, 'xi1': real_nonterminal_next_xi,
  'xi1_valid': ~done,  # or stricter measured availability mask
  'a': final_clipped_raw_command, 'a_prev': before_last_raw_command,
  'r': actual_original_environment_reward, 'f': before_f,
  'ep_step': before_ep_step, 'done': original_term | original_trunc,
  'term': original_term, 'trunc': original_trunc,
  # optional episode metrics ep_len, ep_ret_norm
}
```

- `s1` 必须为原 physical step 后、自动 reset 前状态。post-reset `s` 仅作为下一条 transition 的起点。
- 若 SDK 的原 obs35 只在 reset 后可用：非 done 的 `xi1` 用原 step 返回的真实 obs/context；done 的 `xi1=0, xi1_valid=False`。不额外调用 observation compute、制造噪声或读历史。
- context loss **和 context RunningNorm 更新**都严格用 `(~done & xi1_valid)`。终止 transition 的 state/reward/done 监督仍保留；不把 reset 后 obs 或 terminal 置零 context 当成目标。
- done 用于 reset-continuation 概率监督，明确包含 timeout；如提供 term/trunc，扩展校验 `done == term|trunc` 并分别保存。没有 split 时只保存 unknown 标记，不宣称推断了 physical termination。
- `a` 是进入原 action pipeline 的 total raw command，与 imagined action 的范围/次序一致。PD torque、已乘 joint target scale 的值、或延迟队列输出与即时 raw command 不可混用。原队列/延迟效应由 context/WM 解释。
- 最终 raw action clip 为 `[-6,6]`；原腿位置/轮速度 scale 及执行延迟留在原环境。vendor collection 噪声后先作 `[-20,20]` 限幅，bridge 必须执行最终6幅裁剪并将该实际 command 入 replay。
- 所有采样 Tensor clone/detach 后入库；不要用 `torch.inference_mode()` 创建直接参与 autograd 的常量（普通 `torch.no_grad()` 更合适），避免 inference tensor 保存反向图报错。

## 3. task-owned MDP

```python
num_joints: int
context_dim: int
obs_dim: int
action_dim = 6
goal_frame_dim: int
max_step_reward: float  # positive reporting scale; not a new task reward

def normalize_context(xi): ...
def add_noise(obs): ...  # identity when xi[:35] already holds original noisy obs

def obs(state6, previous_action, xi, frames): ...
# state6=(position, rotation_matrix, world_lin_vel, world_ang_vel, joint_q, joint_qd)
# supports both [B,...] and [B,hist,...]. Suggested composition:
# cat(invariant_features(state6), previous_action, xi), raw teacher35 begins at S+6.

def goal_with_context(frames, num_frames, xi): ...
# [..., goal_frame_dim*num_frames], task/command-conditioning features.
# No H1/LQR trajectory/reference is inherited. Do not claim repeated current
# command is an observed future command; respect resample/phase validity.

def valid_imagination_start_with_context(frames, horizon, xi): ...
# bool [...]; restrict known remaining-time/command-phase/model-supported range.

def critic_features(state6, frames, normalized_context): ...
def to(device): ...
```

额外接口是 `goal_with_context` 与 `valid_imagination_start_with_context`；替代原 vendor 无 context 的接口。扩展不调用旧 `MDP.reward`/旧 `soft_termination`，奖励来自真实 r 的可微监督 head。父若保留原协议方法，可显式标记旧方法在此分支不用，不要悄悄使用 LQR/H1 analytic 目标。

可选但推荐：

```python
def project_predicted_context(next_xi, next_state, action, next_frames): ...
# Differentiable constraints/known queue shift; hold episode-constant DR;
# enforce last-action slots consistently; no .detach/no_grad across actor35.

def imagination_timeout(next_frames, next_xi): ...
# bool or probability in [0,1]; exact known episode/time/phase cap.
```

`predict_context_mask` 是 D 维0/1列表；0维保留当前值，1维用学习到的 delta。mask/投影和 context 布局必须纳入父的任务 fingerprint。默认全1不是“精确队列模型”证明：随机命令切换、感测噪声、contact history 的均值预测会有误差，应通过 valid-start、有限 imagination 范围、task-specific projection、holdout 一步/多步误差监测约束。

## 4. 原 task reward 的接入与梯度

- 原 vendor WM 仍按真实状态 transition 做多步监督。
- 新 auxiliary features 为 `(inv(s), inv(s1), a, a_prev, normalized xi, f*0.02)`。
- 新模型监督：原 r 的归一化 MSE、原 done 的自然 BCE、有效非 terminal delta-xi 的 MSE；reward/context 的 RunningNorm 分离，terminal 假context不污染统计。
- 每次 `wm_update()` 后单独 `opt_aux.step()`；这些步骤不计 BPTT。
- imagination 每步 `pi -> WM state1 -> r_hat/done_hat/delta_xi -> next obs/history/goal`，没有跨步 detach。WM/aux/critic 权重在 policy 阶段冻结，但输入梯度保留。
- survival 为 `cumprod(1-done_hat)`；当前 terminal transition 的 reward 权重是进入该步前的 survival，终止后不跨 reset。若有确切 timeout，叠加成 reset probability=1。
- reward head 是原 reward 的**学习近似**，不是严格原 reward 可微实现；必须看 holdout reward/terminal/context/state 误差，防止 policy 利用 WM/head 外推。原 skill>=80/90%的验收必须在真实原 task、原 predicate 下另测。

## 5. 真实 >=3000 计数

目标字段：`learner.counts.pi_bptt_optimizer_steps`，每个专家单独累计，checkpoint 是持久真值。

仅当 opt_pi 实际 post-hook 执行，且同时满足：

1. `horizon>=2`；本次是 policy_update 的 BPTT 域；
2. loss、policy 参数梯度有限且非零，lr>0；
3. future reward/bootstrap 对第0 action 梯度有限非零；
4. future objective -> 第1 imagined physical state -> 第0 action 的 **WM VJP** 有限非零（排除只有 a_prev/action-rate 的捷径）；
5. 一组具有非零梯度的 student 参数在 optimizer step 后 L2 变化非零。

`pi_optimizer_steps` 另记所有真实 pi.step；`policy_attempts`、WM/aux/critic、BC、teacher推理、环境transition、imagination H 个子步均不计为目标步骤。若某次成功pi.step缺跨时证据，归 `pi_unverified_steps`，不用于3000目标。

## 6. 完整保存与可持续恢复

`save(include_optimizers=True)` 仍用原 vendor 的 tmp+replace 原子发布，增加：aux权重/两个normalizer/opt_aux、replay数据与ptr/size、obs_hist、Python/NumPy/Torch CPU/CUDA RNG、真实计数/receipt、context mask、collect fractional accumulator、pending iteration采样/WM余量及父环境payload。

桥可实现：

```python
def export_supermimic_resume():
    return {'exact': True, 'payload': parent_fullstate, 'receipt': parent_provenance}

def import_supermimic_resume(value):
    # restore physical pose/vel, ORIGINAL command/private RNG, DR nominals/scales,
    # action+feedback queues/timers, phase/contact history, cached state/obs,
    # episode counters and bridge last_action without an extra reset/RNG sample.
    ...
```

payload 必须是 `torch.load(weights_only=True)` 支持的 tensors/primitive/list/tuple/dict，别塞自定义类/NumPy ndarray。`exact=True` 是父实际实现的声明，本核心没有验证其物理充分性。

- 有 exact bridge：`learner.load(own_full_checkpoint)`，全局 RNG 最后恢复。
- 只有 learned components 可恢复：父先 fresh constructor+原 task reset，再 `load(..., allow_environment_reset=True)`。这明示是 reset-resume，不是精确原 rollout；replay 最后一行增加 `stream_cut`，下一段 WM window 不跨 discontinuity，原 done label不篡改。
- stop-before-action 或完整迭代边界保存为 safe boundary；中途 optimizer 事务异常标记 `update_boundary_safe=False`，load 需明确 `allow_partial_update=True`，可能重试局部更新，别称逐位完全重放。
- `_checkpoint(include_optimizers=False)` 是 inference 快照，不含完整恢复状态；load 会挡住把它当 resume 的用法。
- 父还应绑定 expert checkpoint hash、new MOD4v1 asset/contract hash、task/reward/context source hashes；本扩展的结构合同只检查形状/50Hz/aux架构/mask，不代替完整物理身份凭据。
