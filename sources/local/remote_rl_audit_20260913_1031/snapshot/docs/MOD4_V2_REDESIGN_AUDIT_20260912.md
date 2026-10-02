# MOD4 v2 改造：现状审计与落地方案（2026-09-12 23:20）

对照用户 2026-09-12 的 6 项改造清单，逐项审计本仓库现状。**参考实现已 vendored 在本地**
`refs/fudan_src/fudan_rl_wheel_leg-main`（IsaacGym + rsl_rl，226 个 py，含
`actor_critic_sequence.py`、`export_encoder_jit.py`、`utils/terrain.py`、
`mujoco/python_tools/onnx_mj_{chuanlian,binglian}.py`），不需要联网。

> 本轮结论里，"我们这侧"的部分全部有 `文件:行` 证据；参考实现的确切参数由 5 个并行子代理
> 提取完成，已整合进各节（§7 是索引）。

---

## 0. 摘要：30 秒看懂这份文档

**任务**：按用户 6 项清单改造 MOD4 轮腿 RL（观测/编码器、DR、奖励截断、难度课程、sim2sim 门禁、1024 env）。

**产出（全部未落盘到受保护文件，链仍在跑）**

| 类型 | 交付物 | 验证状态 |
|---|---|---|
| 新模块 2 | `mod4_sequence_model.py`（历史编码器）、`mod4_curriculum.py`（难度等级状态机） | 功能单测通过 |
| 新脚本 6 | `sim2sim_mod4/`：门禁（**PASS rc=0**）、无 GPU 导出器、几何探针、映射拟合器；`run_tunnel_course.sh`（狗洞五阶段）；**`start_v2_chain.sh`（一键起 v2 + 19 个旋钮自检）** | 均已运行/自检 |
| 补丁 **13** 个 | 见 §9.1（清单 6 项 + 7 个自研修正，含 **2 处强制顺序**） | `--check` 全过；沙箱**全量叠加 + 幂等 + 编译**通过 |
| 改的资产 | 两个 MJCF `timestep 0.001→0.0005`（带 `.bak`） | 门禁复验通过 |
| 文档 | 本文 **§0–§18**（逐项证据、纠正、陷阱、runbook、19 轮实测与自纠） | — |

**四处"用户清单与事实不符"的纠正**（都有证据）
1. **§3.6/§3.7**：参考的全局 ±2.5 截断会**摧毁** `route_success`（20 → 0.025）与 `termination`（−20 → −2.5，**诱导早死**）⇒ 默认 `safe` 白名单；已做出完整的"谁被截断"表（20 项截断 / 9 项跳过，且被截断项最大 |w|=2.0 < 2.5，**无一饱和**）。
2. **§3.4**：参考的 `sigma 0.25` 是 `exp(-err²/sigma)`，**有效 std = 0.5**。
3. **§4.1**：`terrain.curriculum` 的升级判据是**"走得远 >2 m"**，不是成功率；`0.7` 属于**另一套速度命令课程**；他们**没有** tunnel/hole 几何。
4. **§6.2**：1024 env 单迭代耗时与 512 **基本相同**（9.02 vs 9.00 s）⇒ 加 env 接近免费。

**四科目的病灶（本轮最重要的产出，全部有定量根因）**

| 科目 | 结果 | 根因 | 对策（已验证补丁） |
|---|---|---|---|
| **小陀螺** | ✅ 专项 **0.703** / spin_deg **1973.7°** | — | 已过门 |
| **上台阶** | 0.000 → **0.250** | 在改善 | v2 训练 |
| **飞坡** | 0.000（`peak_rise` 仅 **0.02 m**，从未离地） | **§13**：交付包的 `launched` 判据是"**站上发射台**"（u∈(−0.8,0.10) + 高于 base 0.10 m + 着地 + 对齐），而我们的 `jump_air` 在付"**任何地方离地 4 步**" ⇒ **奖励与判决指标不同源**（奖励 0.84/回合，指标 200 采样仅 2 次非零） | `patch_jump_launch_ready.py` |
| **过洞** | 0.000（6/8 `time_out`，`landed` 8/8） | **§15**：`tunnel_crouch_pose` 只看关节角不看前进，与 `tunnel_stall`(−0.5/步) 相加后**原地不动净 +1.00/步** ⇒ 蹲着不动就是最优解 | `patch_tunnel_crouch_gate.py`（**结构性**让静止净 −0.50，与权重无关） |

**必须知道的几件事**
- **§9.0**：打开编码器会让热启动失效 ⇒ 用 `patch_partial_warmstart.py`（已用真实检查点验证）。
- **§9.5**：rsl-rl 是 **5.0.1**，其 cfg 迁移路径正好吃我们的 `distribution_cfg`（无启动风险）。
- **§9.3 前置**：**本次链自己跳过了 smoke**（`from_phase=tunnel`）⇒ 起 v2 前**先单跑一次 smoke**（约 1 分钟 GPU）再决定是否继续跳过（第 67 轮发现；评测闭环 0.00056–0.00085 m vs 阈值 0.002，跳过依据只是探针的 0.002035 m）。
- **§11.2**：复旦**实机**腿环 kp 是 **6–15**，我们契约 60，训练 **2500（=167×）** ⇒ 强烈支持"2500 是仿真侧产物"。
- **§5.5/§5.9**：sim2sim **产物半边 PASS（rc=0）**；rollout 半边需要"同轴↔分离轴"的 2→2 映射（几何相似度 1.7–4%，**不需要解析 IK**）。
- **§17**：**验证器不能与实现共用同一个提取模式**——我用同一模式测覆盖率，得出错误的"100%"，真实值 **80/112（71%）**，而漏掉的 32 个正是 v2 的旋钮。

**当前链状态（写作时）**：小陀螺已过门；上台阶 0.000→0.250；飞坡与过洞的定量根因已定位且各有已验证补丁；
链正跑最后一个 **jump** 相位，**约 02:09 收尾**；之后按 §9 上补丁（13 个）并起 v2（`start_v2_chain.sh`）。

---

## 1. actor 观测：去 `base_lin_vel` → 5 帧历史 + 小编码器（latent 3）

**现状：非对称结构已经在了，缺的是历史与编码器。**

| 项 | 现状 | 证据 |
|---|---|---|
| actor 无 `base_lin_vel` | ✅ **已满足** | `mod4_task.py:996-1031` `PolicyCfg` 无 `base_lin_vel` |
| critic 保留特权信息 | ✅ **已满足** | `mod4_task.py:1033-1060` `CriticCfg` 有 `base_lin_vel`（另有 `mdp_obs.*` 无损版本） |
| 35 维部署契约 | ✅ 文档化 | `mod4_task.py:993` "The 35-D deployment contract on the policy side, privileged state on the critic" |
| obs 历史 | ❌ **没有** | 全文件 `history_length` 只出现在 `ContactSensorCfg`（L940/950/955），obs 组无历史 |
| 小编码器 (latent 3) | ❌ **没有** | 无 encoder / latent 相关代码 |

### 1.1 参考实现的确切架构（已提取，`refs/fudan_src/fudan_rl_wheel_leg-main/plane/`）

| 项 | 值 | 证据 |
|---|---|---|
| actor 观测 | **25** 维，**无 base_lin_vel**（该行被注释掉） | `envs/base/legged_robot_config.py:37-43`、`legged_robot.py:343-358` |
| critic 观测 | **141** 维（含 `base_lin_vel`） | `legged_robot.py:374-390` |
| 历史长度 | **5 帧**（100 Hz → 50 ms 窗） | `legged_robot_config.py:41` |
| latent | **3**（注释："at least 3 to estimate base linear velocity"） | `legged_robot_config.py:281-285` |
| 编码器 | `Linear(125,128)-ELU-(128,64)-ELU-(64,3)`，无输出激活、无 LayerNorm | `rsl_rl/modules/actor_critic_sequence.py:71-93` |
| actor MLP | `28 → 128 → 64 → 32 → 6`（输入 = 25 当前帧 ⊕ 3 latent） | `:96-116` |
| critic MLP | `144 → 256 → 128 → 64 → 1`（输入 = 141 特权 ⊕ 3 latent） | `:119-137` |
| 控制率 | 200 Hz 物理 / **100 Hz 策略**（decimation 2） | `legged_robot.py:1598`、`legged_robot_config.py:123,249` |

**历史机制（必须逐位复刻）**：环形缓冲只存**那 25 维 actor obs**（不含特权观测），
`obs_history[0:125]` 左移、**最新帧追加在末尾**（index 0 = t−4，index 4 = t）；
reset 时用**当前 obs 重复 5 次**填满（`legged_robot.py:275-277,398-405`）。
**actor 永远拿不到原始历史**——历史只进编码器（`actor_critic_sequence.py:183`）。

**编码器是"单独训练"的，不是和 PPO 联合优化**（这点最容易漏）：
- 主优化器只含 actor/critic/std，**不含 encoder**（`algorithms/ppo.py:47-54`）；
- encoder 有自己的 Adam，`extra_learning_rate = 1e-3`（`ppo.py:56-62`、`legged_robot_config.py:302`）；
- actor 路径上 latent 被 **detach**（`:183`），rollout 在 `inference_mode()` 下；
- encoder 损失是**回归特权观测的第 0:3 维**：
  `latent[:, :3] ≈ critic_obs[:, :3] = base_lin_vel × obs_scales.lin_vel`
  （`ppo.py:257-286`）——也就是 latent 被监督成**缩放后的机身线速度估计**，不是原始 m/s。
  latent_dim == 3 时只有这一项损失，没有 denoise 项。
- **critic 也吃 latent**：critic 输入 = 141 特权 ⊕ 3 latent（`ppo.py:105-108`、`on_policy_runner.py:57-66,160-163`）。

**导出**：ONNX 把 **encoder + actor 融合**成一张图，**两个输入**：
`obs (1,25)` 与 `obs_history (1,125)`（展平），输出 `actions (1,6)` = **动作均值**（无采样、无 tanh），
opset 17、动态 batch（`plane/export_onnx/export_onnx.py:11-16,23-86`）。
⚠️ 同仓库的 `scripts/export_encoder_jit.py:19-40` 是**过期的**（注释写 27/135，与 shipped 配置的 25/125
矛盾），**不要照抄它的头部**。

### 1.2 ⚠️ API 现实：我们的 rsl_rl 是 **4.x 新版**，参考实现那份是旧版——**不能照搬代码**

这是写补丁前必须知道的事，实测（不是推断）：

| 事实 | 证据 |
|---|---|
| 安装的 `rsl_rl` 是**新一代**：`models/{MLPModel,RNNModel,CNNModel}` + `modules/{MLP,RNN,Distribution}` + `resolve_callable` | `.../site-packages/rsl_rl/` 目录树；`runners/on_policy_runner.py:15,39` |
| 策略是 **`Model` 子类**，runner 通过 `alg.get_policy()` 拿，自带 `as_jit()` / **`as_onnx()`** | `on_policy_runner.py:163-183` |
| **`RslRlPpoActorCriticCfg` 已弃用**（我们 `train_mod4_ppo.py:155` 正在用它） | `isaaclab_rl/rsl_rl/rl_cfg.py:356-360`：*"For rsl-rl >= 4.0.0, this configuration is deprecated. Please use `RslRlMLPModelCfg` instead."* |
| 现代替代品 `RslRlMLPModelCfg`：`class_name="MLPModel"` / `hidden_dims` / `activation` / `distribution_cfg`（含 `GaussianDistributionCfg`） | `rl_cfg.py:22-52` |
| 参考仓库的 `ActorCriticSequence` 用的是**旧版 rsl_rl 的模块 API** | `plane/wheel_legged_gym/rsl_rl/modules/actor_critic_sequence.py`（旧签名） |

**⇒ 第 1 项必须在新 API 上重写，不能复制粘贴。**

**好消息：Isaac Lab 的 obs 历史是现成的，而且是组级的。**

| 事实 | 证据 |
|---|---|
| `ObservationGroupCfg.history_length`（默认 `None`）**会覆盖** group 内每个 term 的 history | `manager_term_cfg.py:233-236` |
| 组级 `flatten_history_dim`（默认 `True`）覆盖 term 级设置 | `:241-246` |
| term 级：`history_length=0` 默认；`(N, H, D)` 会被 reshape 成 `(N, H*D)` | `:189-200` |
| 每个 term 有独立 `CircularBuffer`，reset 时一并重置 | `observation_manager.py:308-309,409-423,511` |

**⇒ 在 `PolicyCfg.__post_init__` 里加 `self.history_length = 5`，actor 观测就从 35 变成 175**
（`5 × 35`，已展平），critic 组不动（保持特权、无历史）。**待实测确认**：Isaac Lab 的展平顺序
（最旧在前还是最新在前）——参考实现是"最新在末尾"，若不一致要以 Isaac Lab 为准并在契约里写死。

### 1.3 第 1 项的落地方案（基于上面的事实）

1. `ObservationsCfg.PolicyCfg.__post_init__`：`self.history_length = 5` → actor 输入 175。
2. 新建 `isaac/mod4/mod4_sequence_model.py`：一个 **rsl_rl 4.x `Model` 子类**
   （`class_name` 供 `resolve_callable` 解析）：编码器 `175→128→64→3`，actor MLP
   吃 `[当前帧 35 ⊕ latent 3] = 38`，critic 路径保持特权。
3. `train_mod4_ppo.py`：把弃用的 `RslRlPpoActorCriticCfg` 换成指向我们模型的 cfg，
   并**按参考实现加编码器的独立优化器与独立损失**（`latent ≈ 缩放后的 base_lin_vel`、
   latent 在 actor 路径上 detach、rollout 在 `inference_mode` 下）——这三条是"学出来的线速度估计器"
   能work的关键，漏掉任何一条都会退化。
4. 导出：用 runner 自带的 `export_policy_to_onnx()`；**单输入 175 → 6 维动作**
   （比参考的双输入更简单，因为历史已在 obs 组里）。
5. **部署契约**：ONNX 输入从 35 → **175**；真机必须维护 175 float FIFO
   （初始化 = 当前 obs 重复 5 次；历史存**未 clip** 的 obs，而当前帧用 clip 后的值）。
   不同步契约就不许交付。

**成本提示**：这是"代码类"三项里最重的一项（obs 配置 + 新模型类 + runner 改造 +
导出/契约四处联动），建议紧跟已完成的第 2、3 项之后单独一轮做。

我们的 actor obs 是 **35 维部署契约**，所以：

### 1.4 目标形态对照（旧版 API 下的设计，已被 §1.2/§1.3 取代）

| 项 | 取值 |
|---|---|
| 历史长度 | 5 帧 |
| 编码器输入 | **5 × 35 = 175** |
| 编码器结构 | `Linear(175,128)-ELU-(128,64)-ELU-(64,3)`（照抄） |
| latent | 3，监督目标 = **缩放后的** `base_lin_vel`（用我们 `CriticCfg` 里 `base_lin_vel` 的
同一 `scale=0.5`，否则 latent 语义偏移） |
| actor 输入 | 35 当前帧 ⊕ 3 latent = 38 |
| critic 输入 | 我们 critic 的维数 ⊕ 3 latent |

需要改三处：① `ObservationsCfg` 加历史（Isaac Lab 用 `ObsGroup` 的 `history_length`，让编码器拿到
175 维；actor 只取最后一帧 35 维）；② **自定义 rsl_rl policy**（encoder + actor + critic 三头，
encoder 独立优化器、latent detach、回归损失）；③ 导出脚本融合 encoder+actor、双输入。

**部署影响（必须同步进 `contract_rm2025_later.json`，否则不许交付）**：
- ONNX 从"单输入 35 维"变成"双输入 35 + 175 维"；
- 真机控制器必须维护 **175 float 的 FIFO**，且：
  **初始化用当前 obs 重复 5 次**、**最新帧放末尾**、
  **历史里存未 clip 的 obs，而 `obs` 输入用 clip 后的值**（参考实现刻意如此：
  ring buffer 在 `±clip_observations` 之前填充，`legged_robot.py:119-124` vs `:198,398-405`；
  部署侧 `mujoco/python_tools/onnx_mj_chuanlian.py:596-608,728-737` 同样处理）；
- **不需要**复刻任何归一化器（参考实现只有固定 `obs_scales` + ±100 clip，`EmpiricalNormalization`
  定义了但从未实例化）。

⚠️ **待核实**：Isaac Lab 的 `ObsGroup` 历史展平顺序（最旧在前还是最新在前）**必须与部署 FIFO 一致**；
参考实现是"最新在末尾"，但如果 Isaac Lab 是反的，就以 Isaac Lab 为准并在契约里写明——
这一条要在写补丁时实测确认，不能假设。

**其他可直接借鉴的细节**：观测噪声只加在 actor obs 上（critic 的副本无噪），
而**历史继承的是加噪后的值**（`legged_robot.py:392-405`）；
参考实现**没有观测延迟**（`grep obs_delay` 无结果），我们自己的 `OBS_DELAY_*` 是额外的。

---

## 2. DR 提前并默认开 + 范围对齐

**现状：DR 基础设施齐全，但被 `RM_DR_OFF=1` 整体关掉，且三处范围与要求不符。**

开关：`mod4_task.py:158` `DR_OFF = os.environ.get("RM_DR_OFF","")=="1"`；链在
`start_mod4_stage_fixedplant.sh:56` 与 `final_acceptance_mod4.sh` 里都设 `RM_DR_OFF=1`。

| 项 | 用户要求 | 我们现状 | 证据 | 判定 |
|---|---|---|---|---|
| Kp 随机化 | ±10% | `stiffness_distribution_params=(0.9,1.1)` | `mod4_task.py:1396-1401` | ✅ 一致 |
| Kd 随机化 | ±10% | `damping_distribution_params=(0.8,1.2)` = **±20%** | 同上 | ⚠️ 比要求宽一倍 |
| 力矩 | ±10% | `EFFORT_LEG=(0.75,1.25)` = **±25%**；`EFFORT_WHEEL=(0.90,1.10)` = ±10% | `mod4_task.py:160-161` | ❌ 腿力矩宽 2.5× |
| 动作延迟 | **0–5 ms** | `ACTION_DELAY_MIN/MAX_LAG = 0..2` **控制步** | `mod4_task.py:170-171` | ❌ **量纲不可表达** |

**动作延迟是硬问题，而且参考实现给了确切机制**：`POLICY_HZ=100` → 控制步 **10 ms**
（`mod4_task.py:145-147`，`PHYSICS_DT=0.0005`、`DECIMATION=20`）。现有实现是**整数控制步延迟队列**
（`_DelayMixin`，`mod4_task.py:709-714`），能表达的是 0/10/20 ms，**表达不了 0–5 ms**。

### 2.1 参考实现的延迟机制（可直接照抄结构）

| 事实 | 值 | 证据（参考仓库） |
|---|---|---|
| 配置单位 | **毫秒** | `legged_robot_config.py:180-181` `delay_ms_range = [0, 10]` |
| 实际实现 | **整数 SIM 步 FIFO**，不是策略步、不是一阶滞后 | `legged_robot.py:1146-1160` |
| 采样 | `round(uniform(low/1000/dt, high/1000/dt))`，**只采一次、从不重采** | `legged_robot.py:1247-1256` |
| 推进位置 | **在 decimation 内层循环里**，FIFO 每 **sim 步**移一位 | `legged_robot.py:98-105` |
| 速率 | sim 200 Hz（5 ms）/ policy 100 Hz（10 ms） | `legged_robot_config.py:123,249` |
| 可达值 | `[0,10] ms` → 只有 **{0, 5, 10} ms**（p={0.25,0.5,0.25}） | 500k 次抽样模拟 |

**⇒ 这正是我们要的粒度**：他们的 `sim_dt` 是 5 ms，我们的是 **0.5 ms**（`PHYSICS_DT=0.0005`），
所以 0–5 ms 在我们这里能落成 **0..10 个物理步、分辨率 0.5 ms**，比他们还细 10 倍。
实现方式：把延迟从"控制步队列"改成"物理步子步延迟"——每个策略步把动作压入 FIFO，
但在 `apply_action` 的每个物理子步按 `k`（该 env 的延迟步数）取"旧动作/新动作"。

**⚠️ 必须避开他们踩的坑**：他们的 `action_fifo` 尺寸是 `ceil(10/1000/0.005) = 2`（合法 idx 0..1），
而采样器会产出 idx=2 ⇒ **约 25% 的 env 越界 IndexError**，在他们 **46/47 个开了延迟的训练配置里是活的**
（G3 用 `+ 1` 修了；jump 的 `[0,5]` 变体更糟，若开启是 50% 越界）。
**我们自己的实现经核实没有这个问题**：`mod4_task.py:721` 分配 `max_lag + 1` 槽、`:745` 对 idx 取 `clamp`。
移植时保持 `ceil(max_ms/1000/dt) + 1` 的尺寸约定，并加一条断言。

### 2.2 ⚠️ 参考仓库有**四代** DR 配置——"他们要了什么"必须指明是哪一代

他们的 `task_registry.save_cfgs` 在训练启动时**把源码拷进 run 目录**，所以 `logs/**` 就是"实际跑过的代码"：

| 代 | 文件大小 | run 数 | Kp/Kd/力矩 | 动作延迟 |
|---|---|---|---|---|
| **G1** | 79618 B | 12（**= live source，逐字节相同**） | `[0.95,1.05]` **±5%** | **OFF** |
| **G2** | 82753 B | 10 | `[0.9,1.1]` **±10%** ← 你说的 ±10% | **ON**，`[0,10] ms` |
| **G3** `randization=*` | 85433 B | 7 | ±5%/±15% + **腿轮分离** | 腿 + 独立轮延迟 |
| **G4** | 87012–87784 B | 8 | `[0.9,1.1]` | ON，`[0,10] ms` |

**⇒ 用户记忆里的"±10%"对应 G2/G4（实际训练用的），不是 live source（±5%）。**

另外三条与我们的设计直接相关的差异：
1. **力矩不是改限幅**，而是在**固定 URDF 限幅之前**乘一个逐关节电机强度系数
   （`legged_robot.py:761-763`：`clip(torques * torques_scale, ±torque_limits)`）；
   `torque_limits` 直接读 URDF、从不随机化。我们的 `EFFORT_LEG=(0.75,1.25)` 是同一类做法
   （逐回合重采样），但**范围要收到 ±10%**。
2. **他们的 DR 全部在环境构造时采样一次，从不按回合重采**（除 G4 的事件 id）；
   我们的是 `mode="reset"`（逐回合）——**严格更强**，这点保持我们的。
3. **他们没有 DR 课程/渐进**（`normal/mid/hard` 是三次独立训练，不是同一轮的阶段），
   也没有观测延迟、编码器偏置、重力/armature 随机化。所以"DR 提前并默认开"在我们这里是
   **纯开开关 + 收范围**，没有"渐进调度"要抄。

⚠️ 还有一个正交风险：DR 开起来后 `closure` 解算误差可能进一步变大——terrain 阶段已经在
**2.035 mm**（门禁 2 mm，见续训文档 §4.7）。开 DR 前建议先把闭链误差的来源定下来。

---

## 3. 单项奖励截断 ±2.5 + tracking sigma 统一 0.25

**现状：Isaac Lab 的奖励项根本不支持截断；但 "sigma 0.25" 的语义与我们担心的不是一回事。**

### 3.1 参考实现的截断语义（已提取，**推翻了我先前的担心**）

`refs/fudan_src/fudan_rl_wheel_leg-main/plane/wheel_legged_gym/envs/base/legged_robot.py:322-330`：

```python
rew = self.reward_functions[i]() * self.reward_scales[name]
rew = torch.clip(rew, -self.cfg.rewards.clip_single_reward * self.dt,
                      +self.cfg.rewards.clip_single_reward * self.dt)
```

而 `_prepare_reward_function`（同文件 L1269-1275）在初始化时已经把每个非零 scale **乘过 dt**
（注释原文 `# remove zero scales + multiply non-zero ones by dt`）。所以这两步合起来**精确等价于**：

> 把 **`raw × 配置权重`** 截断到 **±`clip_single_reward`**

也就是说用户说的"±2.5"是**截断后、乘 dt 前**的 `raw×weight` 量。**注意取值有两个变体**：

| 变体 | `clip_single_reward` | 证据 |
|---|---|---|
| plane（主/平地） | **1** | `plane/wheel_legged_gym/envs/base/legged_robot_config.py:207` |
| **jump** | **2.5** | `jump/wheel_legged_gym/envs/base/legged_robot_config.py:213` |

⇒ 用户的 "±2.5" 对应**跳跃变体**。落地时建议做成旋钮 `RM_REWARD_CLIP`（默认 2.5），
并记录用的是哪一档——这条会影响所有惩罚项的饱和度（见 §3.3）。

### 3.2 我们这边的落地配方（Isaac Lab 无 clip 字段）

已核实：`RewardTermCfg` 只有 `func`+`weight`（`manager_term_cfg.py:316-332`），
管理器是 `value = func(env, **params) * weight * dt`（`reward_manager.py:150`）——**没有 clip 入口**。

要在**不改框架**的前提下复刻参考语义（截断 `raw×weight` 到 ±C，再乘 dt），
在 `RewardsCfg.__post_init__` 里把每个 term 的 `func` 包一层即可：

```python
for f in fields(self):
    term = getattr(self, f.name)
    if not isinstance(term, RewTerm) or term.weight == 0.0:
        continue
    W, C = term.weight, REWARD_CLIP          # C = RM_REWARD_CLIP, 默认 2.5
    raw = term.func
    term.func = (lambda raw, W, C: lambda env, **kw:
                 torch.clamp(raw(env, **kw) * W, -C, C) / W)(raw, W, C)
```

因为 Isaac Lab 随后仍会乘 `weight * dt`，所以 `clamp(raw*W,±C)/W * W * dt = clamp(raw*W,±C)*dt`
——与参考实现逐位一致。**必须验证**：① 权重为 0 的项要跳过（Isaac Lab 会直接跳过它）；
② 负权重（惩罚项）公式同样成立；③ 逐步抽查两三个项，确认 `Episode_Reward/*` 的数值与
手算一致。**不要**用 `only_positive_rewards`（参考实现里是 `False`，`legged_robot_config.py:206/212`）。

### 3.3 截断带来的饱和度（对比参考实现可直接推得）

因为界就是 `±C` 作用在 `raw×weight` 上，**任何 |weight| > C 的项都会饱和**。参考实现 plane 档
（C=1）的实测后果：`orientation=-100` 在倾角约 0.1 rad 时即饱和到 −0.01/步；`lin_vel_z=-1` 在
|v_z|≥1 m/s 饱和；`collision=-1` 在 ≥2 个同时接触时饱和。我们的权重表里
`torques/action_rate/...` 量级很小不会截断，但 **`jump_push=10.0`、`jump_climb=8.0`、
`route_success=20.0`、`track_ang_vel=5.0` 都会被截断**——这本身就是用户想要的效果（防止单项爆炸），
但必须知道它同时**削掉了这些高权重项的峰值梯度**。落地前建议先打印一张
"每项 |weight| vs C，谁会被截断"的表。

### 3.4 tracking sigma：**"0.25" 是 `exp(-err²/sigma)` 里的 sigma，有效 std = 0.5**

参考实现（`plane/.../legged_robot.py:1838-1862`，jump 同）：

```python
lin_vel_error = torch.square(self.commands[:, 0] - self.base_lin_vel[:, 0])
return torch.exp(-lin_vel_error / self.cfg.rewards.tracking_sigma)
```

`tracking_sigma = 0.25`（plane `legged_robot_config.py:208`，jump `:214`，注释
`# tracking reward = exp(-error^2/sigma)`；全仓库、含所有 log 快照里**只出现过 0.25**，无运行时改动）。

⇒ **数学上 `exp(-err²/0.25) = exp(-(err/0.5)²)`，有效 std 是 0.5，不是 0.25。**

这**解除了我先前标记的冲突**：我们代码里那条警告说的 `std=0.25` 指的是
`exp(-(err/0.25)²)`（Isaac 默认写法），而用户说的"统一 0.25"照抄参考实现应该落成
**`std = 0.5`**。我们现状 `track_lin_vel std=0.7071`、`track_ang_vel std=1.4142`
（`mod4_task.py:1526-1540`），**改成 0.5 是从一个较宽的核收紧一档，而不是收到危险区**。

但仍有三点必须注意：

1. **参考实现在两个 tracking 项之外并不"统一"**：`*_enhance` 变体的除数是 `sigma/10`（有效
   2.5，返回 `[-1,0]`）；`base_height` 用**硬编码** `0.001`；`nominal_state` 用 `0.1`；
   jump 的飞行项用硬编码 `4.0/6.0`。所以"统一 0.25"应只施加于**两个 tracking 项**。
2. **参考实现里没有小陀螺任务**（`grep -ri spin` 只命中 `play.py` 的 yaw 打印），因此
   "sigma 统一"**不覆盖**我们的 `track_ang_vel_route_scaled`（按路线缩放的自研核）——
   小陀螺那一档要么保留自研核，要么单独给一个 sigma。**这一条需要用户确认**。
3. jump 变体的 `tracking_lin_vel` 返回 `... * 2`（上限 2.0），`tracking_ang_vel` 不乘 2
   （`jump/.../legged_robot.py:1897-1919`）。若照抄跳跃档，权重与上限要一起看。

### 3.5 顺带提取到的 PPO 超参（可用于对齐我们的 runner）

`legged_robot_config.py:288-300`：`clip_param=0.2`、`gamma=0.99`、`lam=0.95`、`desired_kl=0.005`、
`schedule="adaptive"`、`max_grad_norm=1.0`、`use_clipped_value_loss=True`；
**优势归一化存在**（`rsl_rl/storage/rollout_storage.py:178-181`，`(adv-mean)/(std+1e-8)`）；
观测/动作 clip 到 ±100（`legged_robot_config.py:227-228`）。

### 3.6 ⚠️ 致命相互作用：朴素的 ±2.5 截断会**摧毁**我们的一次性成功奖励

这是本轮最重要的发现。我们的 `route_success` 为了对抗"奖励管理器乘 dt"而**故意按 `1/dt` 放缩**：

```python
# skills_isaac.py:893-905
"""... a weight of 20 paid only **0.2** on the success step while simply surviving a 30 s tunnel
episode accumulates ~30.  A finished route was worth 1/150 of standing still ..."""
return d["success"].float() / max(1e-6, float(env.step_dt))
```

于是**成功那一步** `raw ≈ 1/dt = 100`、权重 20 → **`raw×weight ≈ 2000`**。
若按参考语义把 `raw×weight` 截断到 ±2.5：

| | 现在 | 截断后 |
|---|---:|---:|
| 成功那一步的奖励 | **20.0** | **0.025** |

**一次 800 倍的缩水**，而且正好打在这个项目已经修过一次的痛点上（上面那段 docstring 记录的就是
"完成路线只值站着的 1/150，所以每个阶段都选择苟活"）。参考实现里没有这种 `1/dt` 放缩项
（他们的 scale 都是 O(1)），所以这个截断在他们那里安全，**照抄到我们会直接把成功信号删掉**。

**同样会被截断削掉峰值的高权重项**（|weight| > C=2.5 即饱和）：

| 项 | 权重 | raw 上限 | `raw×weight` 上限 | C=2.5 下的后果 |
|---|---:|---:|---:|---|
| `route_success` | 20.0 | ≈100（=1/dt） | ≈2000 | ❌ 几乎全部被削 |
| `jump_push` | 10.0 | 1.0 | 10 | ⚠️ 只有 ≤25% 的量程可用 |
| `jump_climb` | 8.0 | 1.0 | 8 | ⚠️ 只有 ≤31% 可用 |
| `track_ang_vel`（小陀螺档用满核） | 5.0 | 1.0 | 5 | ⚠️ 只有 ≤50% 可用 |
| `track_lin_vel` | 2.0 | 1.0 | 2.0 | ✅ 刚好不截断 |
| `height` / `crouch_pose` / `tunnel_*` | ≤1.5 | ≤1 | ≤1.5 | ✅ |

**结论：第 3 项的截断不能按参考实现原样照搬。** 三个可行方案（需用户选）：
1. **按项白名单**：只对 O(1) 量级的密集项截断，`route_success` 这类一次性项豁免（最小改动、最安全）；
2. **先归一化再截断**：把 `route_success` 的 `1/dt` 去掉、权重提到 2000（但会让 episodic sum 的
   量纲全面变化，且要重算所有 gate 阈值）；
3. **按项可配的 clip**：`RM_REWARD_CLIP` 全局默认 2.5 + 每项 override（例如
   `route_success: 2000`），最灵活但要维护一张表。
**推荐方案 1**，并在应用前打印"每项 `|weight|` vs C，谁被截断"的表作为验收证据。

### 3.7 ✅ 那张表已经做出来了（v2 真实生效集，`safe` + C=2.5）

从补丁后的 `RewardsCfg` 源码静态提取每个 `RewTerm` 的权重，按 **rmuc2026 模式实际注册**的集合分类
（`MAP_MODE != "rmuc2026"` 那个块在 v2 里**不注册**，已剔除 7 项：
`gyro_track_wide / tunnel_crouch / tunnel_approach / tunnel_traversal / flight_progress /
unwanted_airborne / landing_recovery`）：

| 判定 | 项数 | 项（权重） |
|---|---:|---|
| **截断**（`\|w\| ≤ C`） | **20** | `track_lin_vel`(2)、`height`(1)、`alive`(1)、`route_progress`(2)、`tunnel_height`(1.5)、`tunnel_clearance`(1.5)、`jump_air`(1.5)、`wheel_contact`(0.8)、`jump_crouch`(0.8)、`tunnel_stall`(1)、`lin_vel_z`(-0.6)、`flat_orientation`(-1.5)、`action_rate`(-0.1)、`action_l2_leg`(-0.1)、`action_l2_wheel`(-0.02)、`action_acc`(-0.02)、`leg_symmetry`(-0.2)、`ang_vel_xy`(-0.05)、`torques`(-2e-5)、`joint_power`(-2e-4) |
| **跳过**（`\|w\| > C`，会立刻饱和） | **9** | `route_success`(**20**)、`termination`(-20)、`base_contact`(-10)、`jump_push`(10)、`jump_climb`(8)、`track_ang_vel`(5)、`dof_pos_limits`(-5)、`jump_land`(3)、`jump_hard_land`(-3) |

**两条自检（已断言）**：
- **被截断的 20 项里最大 `|weight|` = 2.0 < C = 2.5** ⇒ **没有任何被截断的项会饱和**，
  规则自洽（截断真的只在"防单项爆炸"的意义上起作用）；
- 被跳过的 9 项恰好是**高权重的技能项与惩罚项**（一次性成功奖励、终止/触地/限位惩罚、
  跳跃推蹬/落地、小陀螺角速度核）——这些保住量程正是我们想要的。

⚠️ 这也说明了"照抄参考的全局 ±2.5"会付什么代价：上表 9 项全部会被压到 2.5，
其中 `termination` 的威慑从 −20 降到 −2.5（**诱导早死**）、`route_success` 从 20 降到 0.025（**成功无意义**）。
`safe` 模式正是为这两类项设的豁免。

---

## 4. 15 条路线难度课程 + 成功率 >0.7 自动升级

**现状：只有 2 个课程项（转速窗口、跳高窗口），没有任何路线/地形难度分级；而且难度分级在当前
训练模式下被两件事挡住。**这是六项里**最重**的一项。

已验证的障碍：

1. **场地是一个共享 USD 原型，不是参数化几何。**
   `make_terrain_cfg(num_envs)` 只是把 `maps/arena_{N}.usda` 实例化 N 份，而
   `build_layout()` 只做摆放（`build_layout.py:11-33`：`AddReference('arena.usda')` + 平移 +
   `SetInstanceable(True)`，manifest 里只有 origins/spacing）。**真正的 15 条路线几何在
   `arena.usda` 这一个原型里**，没有任何难度参数。
2. **狗洞几何在我们代码里是 4 个模块级标量常量**，被奖励/终止/状态机直接当标量用：
   `HOLE_FLOOR_Z / HOLE_CEILING_Z / HOLE_ROOF_X / HOLE_LANE_Y`
   （`skills_isaac.py:27-30`），消费者是 `_hole_inside`(L39-49)、`tunnel_clearance_cad`(L52-66)、
   `tunnel_roof_hit_cad`(L69-74)、`update_tunnel_state`(L97-127)。**要按 env 分难度，这些必须变成
   逐 env 张量（或按 level 查表）**，是一次贯穿式重构。
3. **当前训练模式下 `FIELD_INFO` 是空的。**
   `RM_MOD4_MAP=rmuc2026` 时走 `attach_rmuc2026_terrain()`（`mod4_task.py:885-905`）用交付包场地，
   而程序化场地只在 `MAP_MODE != "rmuc2026"` 时才构建（`mod4_task.py:964-974`）；相应地
   `tunnel_approach/traversal/crouch`、`launch/island/undulation` 这些奖励项在 rmuc2026 模式下
   **根本不注册**（L1511、L1615 的 guard）。
4. **好消息：程序化场地天然是参数化的。**
   `isaac/rmuc2026_field.py` 用 `cad/out_map/field_dims.json` 的**实测区间**造 cuboid：
   `slope_deg=[9.4,25.0]`、`step_height_m=[0.02,0.22]`、`obstacle_height_m=[0.074,0.416]`、
   `roughness_m=0.02`，并且 `rmuc2026_field_per_env(cap_h=None, clear_x=1.1)` 已经带参数、
   已经产出 `tunnel_hole_m=(hole_h,hole_w,depth)` 与 `tunnel_entry/exit/spawn/success`
   （`rmuc2026_field.py:19,121-133,192-269`）。
   洞高 350→250 mm、台阶高度、坡角、跳高**正好就是这些区间的插值**。

### 4.1 ⚠️ 参考实现的真实判定（**"成功率 >0.7 自动升级"这条记忆有偏差**）

参考实现的课程是 **stock legged_gym 的 game-inspired curriculum**，判定**不是成功率**：

```python
# plane/wheel_legged_gym/envs/base/legged_robot.py:848-881
distance = torch.norm(self.root_states[env_ids,:2] - self.env_origins[env_ids,:2], dim=1)
move_up   = distance > self.terrain.env_length / 4          # 8.0/4 = 2.0 m
move_down = (self.episode_sums["tracking_lin_vel"][env_ids]/self.max_episode_length_s
             < (self.reward_scales["tracking_lin_vel"]/self.dt) * 0.4) * ~move_up
self.terrain_levels[env_ids] += 1*move_up - 1*move_down
```

| 事实 | 说明 |
|---|---|
| 升级判据 | **走得远**（离本 tile 原点的 XY 位移 > `terrain_length/4` = **2.0 m**），**不是成功率** |
| 平滑/统计 | **没有**：每 env 一个标量、reset 时算一次，无 EMA、无多回合平均 |
| 步长 | 每回合 **±1 级**，没有"保持"分支；下限 0 |
| 降级 | 那条基于奖励的降级判据**数值上是死的**：`episode_sums` 逐项已被截断到 `1*dt=0.01`/步、20 s 上限 20，恒 `< 40` ⇒ **凡是不够 2 m 的都被降级** |
| 难度映射 | **闭式公式**，不是表：`difficulty = i/num_rows`（10 行），`slope=0.5d`、`step_height=0.05+0.18d`、`discrete_h=0.05+0.1d`、`random_h=0.05+0.05d` ⇒ 台阶最高 **0.212 m** |
| **0.7 是什么** | `commands.curriculum_threshold = 0.7`，属于**另一套"速度命令范围"课程**（只对走完顶级 terrain 的 env 放宽 `lin_vel_x`），与地形升级无关，也**不是成功率** |
| `tunnel` / `hole` / 350→250 mm | **全仓库不存在**（大小写不敏感 `grep tunnel\|hole` 无地形相关命中） |
| 生效条件 | `mesh_type="plane"` 时 `_parse_cfg` 会**强制关掉**地形课程（`legged_robot.py:1602-1603`）；shipped 配置正是 plane ⇒ **他们的地形课程默认是关的** |
| 路线混合 | `terrain_proportions` 累积阈值法；shipped 配置下 9 个分支只有前 6 个可达，stepping-stones/gap/pit 是**死代码** |
| 另一个可用项 | **速度命令课程**（`update_command_curriculum`，`legged_robot.py:894-951`）：对达标 env 每次 ±0.05 放宽 `lin_vel_x`，阈值 0.7——**这个才是可以照抄的** |

他们自己的演化史（48 个 run 快照按函数 md5 分组）：升级距离 **4.0 m → 2.0 m**，且 0.7 闸门后来加了
`tracking_ang_vel` 条件。**从未有过基于成功率的地形升级。**

### 4.2 我们的设计方案（结合两者，但成功判据用我们自己的）

用户要的"15 条路线 × 等级 + 成功率 >0.7 升级"实际上是**两个机制的合成**，建议这样落：

1. **路线难度等级（新写，参考只提供模式）**：照抄它的**结构**——逐 env `level` 张量、
   每回合 ±1、升级时把 env 传送到该等级对应的 tile；但**升级判据用我们自己的 `route_success`**
   （我们有明确的每路线成功判据与 `complete_rate`，比"走了 2 m"更贴合 15 条路线的语义）。
   参考的"走得远"判据对我们的坡道/台阶路线**不成立**（走完 ≠ 走远）。
2. **隧道 350→250 mm 的阶梯必须我们自己写**（参考里没有）。参数化基础已经具备：
   `isaac/rmuc2026_field.py` 的 `hole_h`、`field_dims.json` 的
   `step_height_m=[0.02,0.22]`、`slope_deg=[9.4,25.0]`、`obstacle_height_m=[0.074,0.416]`。
3. **速度命令课程可以直接照抄**（阈值 0.7、步长、basic/advanced 上限），它对小陀螺与直线都有用，
   而且我们的 `gyro_window` 已经是同类机制的雏形。
4. **不要照抄的地方**：① 它那条数值上失效的奖励降级判据；② 只走"距离"的单一判据；
   ③ 它的 tile 传送机制（我们的 15 条路线是语义路线，不是可平移的地形瓦片）。

### 4.3 ⚠️ 落地阻塞：**没有 15 条路线的几何生成器**，需要你先选路径

进一步核实（这一步改变了方案可行性）：

| 事实 | 证据 |
|---|---|
| 15 条路线来自**交付包的 `data/routes.json`**（15 条，带 kind + spawn） | `incoming/rmuc2026_field_20260911/rmuc2026_training/data/routes.json` |
| 我们自己的程序化场地是**另一套车道**（barricade / island / launch ramp / gap banks / undulation），**不是**这 15 条路线 | `isaac/rmuc2026_field.py` 的 lane keys |
| 场地几何在 `arena.usda` → 它只是**引用两个 CAD 派生的二进制资产** | `maps/arena.usda`：`references = @../assets/arena_collision.usdc@`（636 KB）、`@../assets/arena_visual.usdc@`（3.0 MB） |
| 包里**没有** `arena_collision.usdc` 的生成器（`build_layout.py` 只做摆放、`build_layout` 的几何说明是 "one shared arena prototype"） | `tools/` 下只有 `build_layout / build_preview / validate_map` |
| **CAD 源不在本地**：`cad/` 只有 `out/`、`out_map/`，`RMUC2026_V2.0.0.stp` **缺失**（只在 `field_dims.json` 里被标注为 source） | `ls cad/` |
| **没有 mesh→USD 的转换工具** | 仓库内无 `usd_from*` / `*cad2*` / `*to_usd*` |
| 可用的实测尺寸（程序化重建的输入） | `cad/out_map/field_dims.json`：`slope_deg=[9.4,25.0]`、`step_height_m=[0.02,0.22]`、`obstacle_height_m=[0.074,0.416]`、`field_size_m=[29.75,16.0]` |

**⇒ "给 15 条路线加等级（洞高 350→250 mm、台阶高度、坡角、跳高）"需要的几何，我们手上没有生成器，
交付的 `arena_collision.usdc` 是二进制且属于交付件（项目规矩是"交付件字节未动"）。**

三条可行路径，成本与代价不同，**需要你选**：

| 路径 | 做法 | 代价 | 代价/风险 |
|---|---|---|---|
| **A. 程序化重建 15 条路线** | 用 `field_dims.json` 的实测区间 + `routes.json` 的 spawn，在 MOD4 侧用 cuboid 重建 15 条路线的参数化版本（照 `rmuc2026_field.py` 的技术），难度即区间插值 | **高**（要重建 15 条路线的关键特征） | 训练几何与交付场地不再是同一份资产，**必须在交付里声明**；换不来 CAD 级保真 |
| **B. 任务级课程（不动几何）** | 保持交付场地，按等级调**任务参数**：`RM_TUNNEL_GOAL_X` / `RM_TUNNEL_LEAD_M` / `RM_ROUGH_SPEED_MAX` / `RM_EPISODE_S` / 路线权重 / 命令速度窗口 | **低**（都用现成旋钮，今天就能做） | **拿不到"洞高 350→250 mm"**，只是任务难度梯度 |
| **C. 等 CAD 源后重生几何** | 拿到 `RMUC2026_V2.0.0.stp` + 一个 mesh→USD 链，按等级生成 `arena_collision_L{k}.usdc` | 中（依赖外部输入） | 需要你提供 STEP 与转换工具；周期不可控 |

**我的建议**：先做 **B**（今天可落地、立刻改善四科目），同时把 **A** 作为独立任务排期；
**C** 只有在你能提供 STEP 源时才考虑。

**另外**：参考实现那套**速度命令课程**（阈值 0.7、步长 0.05、basic/advanced 上限 2.5/1.5）
**与几何无关、可以立刻照抄**，且我们的 `gyro_window` 已是同类机制的雏形——它属于路径 B 的一部分。

---

## 5. sim2sim 进 gate：ONNX → MuJoCo → 通过才允许交付

**现状：我们已经有这套东西，但是为 RM2025 建的；移植即可，不用从零写。**

`sim2sim_later/` 是一个 **CPU-only** 的 MuJoCo 验收包（README 明说"does not import mjlab,
Isaac Lab, Warp, or torch"）：

| 文件 | 作用 |
|---|---|
| `sim2sim_later.py` | 重建植物 + **35 维观测** + 6 维动作 + ONNX 回放 |
| `check_sim2sim_later.py` | **"Physics/contract/motor/ONNX/rollout acceptance gates"** —— 已经是门禁 |
| `run_sim2sim_later.sh` | 先跑 checker 再回放；`SKIP_CHECK=1` 可跳过 |
| `config/rm2025_later.yaml` | 契约值的人类可读副本（JSON 契约才是真源） |

但它绑定的是 `incoming/rm2025_fixed/robot_hifi.xml` + **RM2025 later 契约**，不是 MOD4。
MOD4 侧另有 `sim_mujoco/`（`mjcf/`、`onnx_play.py`、`sim_baseline.py`、
`tunnel_crouch_traction.py`、`linkage_probe.py`、`leg_ik.py`）与 `sim2sim/`、`sim2sim_cc/`，
ONNX 产物已有 `train/deploy/rm2025_later_smoke_{raw,trim}.onnx`、
`third_party/rc_mjlab/model_6800.onnx`，导出/预检脚本有
`migration/linux/run_onnx_smoke.sh`、`sim2real/preflight_deploy.sh`。

### 5.1 参考实现的 sim2sim 真实情况（已提取，**结论反直觉**）

它有 `mujoco/python_tools/onnx_mj_chuanlian.py`（串链，766 行）与 `onnx_mj_binglian.py`（并联，854 行），
ONNX 经**直接解析 protobuf 核验**：输入 `obs[1,25]` + `obs_history[1,125]`、输出 `actions[1,6]`、
opset 17、encoder+actor 已融合、**图是无状态的**（5×25 缓冲由调用方维护）。历史处理与训练一致
（串链用 **未 clip** 的 obs 更新历史、初始化重复 5 次、最新帧在末尾 ✅）。

**但它没有任何门禁机制**：

| 检查项 | 结果 |
|---|---|
| assert / 阈值 / mse / allclose / 保存结果 | **全无**（grep 无命中） |
| 与 IsaacGym 参考轨迹比较 | **不存在** |
| 指标 / JSON 输出 / 退出码 | **不存在**（`main()` 直接 return） |
| headless | **没有**——焊死在 `mujoco.viewer.launch_passive` + `pynput` 键盘监听上 |
| 命令输入 | **只有键盘**，没有脚本化命令序列 |
| 终止/超时/复位 | **没有**（机器人从 0.5 m 直腿掉落，自己爬起来） |
| `.pt` 检查点 | **仓库里一个都没有**（`.gitignore` 排除了 `model_*.pt`） |
| README / requirements | `mujoco/` 下**没有**任何 md/requirements（只有根 README 4 行） |

**它自己未记录的保真度缺陷（从代码推出，最有价值的三条）**：
1. **`sim_dt` 与积分器不一致**：MJCF 的 `<option>` **没有 `timestep`** ⇒ MuJoCo 用默认 **0.002 s**，
   但脚本硬编码/默认 `sim_dt = 0.005`，且从不读 `m.opt.timestep`。于是
   `steps_per_policy = round(0.01/0.005) = 2` 实际是 `2×0.002 = 0.004 s` ⇒ **策略实际以约 250 Hz 被调用，
   而不是训练时的 100 Hz**；命令斜坡的 `eff_policy_dt` 也跟着错。
2. **力矩限幅与训练不符**：训练从 URDF 读（腿 `effort=50`、轮 `effort=5`）。串链把**全部**关节截到 ±30
   （腿比训练紧 1.67×、轮比训练**松** 6×）；并联截 ±30 且轮再截 ±5（与 URDF 一致 ✅）。
3. **高度命令范围错位**：训练 plane 是 `[0.17,0.33]`，而 runner 夹到 `[0.14,0.25]` 且**默认值 0.10
   低于自己的下限** ⇒ plane 策略一上来就在训练分布之外约 0.15 个 obs 单位。
   另有：两个 runner 的历史来源不一致（并联用了 clip 后的 obs，与训练不符）、
   `chuanlian.py:101` 的 jump 轮阻尼 0.5 与其它处的 0.2 矛盾、`binglian.py:806` 用 `time.sleep` 把
   物理循环限流到约 0.2× 实时。

### 5.2 我们的做法（**不要照抄他们的，扩我们的**）

**结论：在"门禁"这条轴上我们比参考实现领先**——`sim2sim_later/check_sim2sim_later.py` 本身就是
"Physics/contract/motor/ONNX/rollout acceptance gates"，有检查、有退出码、CPU-only、可 headless。
所以正确做法是**把 MOD4 灌进我们这套 checker**，而不是移植他们那套只能键盘玩的 demo。

要做的：
1. 用 MOD4 的 MJCF（用户说串/并联都有）+ MOD4 契约起一份 `sim2sim_mod4/`（可从 `sim2sim_later/`
   复制骨架）；观测必须按 **35 维契约**重建，并**预留 175 维历史输入**（配合 §1 的编码器改造）。
2. **把 §5.1 那三条保真度缺陷当反面教材写进检查**：显式校验仿真 `timestep` 与 `policy_dt` 一致、
   力矩限幅与 URDF/契约一致、命令范围在训练分布内。
3. 场景覆盖 4 个科目（洞 / 台阶 / 坡 / 跳）+ 脚本化命令序列 + 终止条件 + 固定时域。
4. **定义 PASS 判据与退出码**（我们已有骨架），然后挂进 `final_acceptance_mod4.sh`：
   **不过就不产出交付包**。

### 5.3 ⚠️ 实测：我们自己的回放器与 MOD4 部署契约**不一致**——先对齐才能当门禁

三块料确实都齐：串/并联 MJCF 都在（`sim2sim/rm_vehicle/mjcf/rm_vehicle.xml` 6.9 KB、
`sim2sim_cc/rm_vehicle_cc/mjcf/rm_vehicle.xml` 21 KB，meshes 分别 10 / 39 个 STL 都在），
`sim_mujoco/onnx_play.py` 已实现 35 维观测映射 + 部署控制律，`check_sim2sim_later.py` 有
`check()` 式门禁骨架（`main()` 返回 0/1 并打印 `RESULT: … PASS/FAIL`）。

**但 `onnx_play.py` 是为另一套契约配置的**：

| 常量 | `onnx_play.py` | MOD4 契约 `contract_rm2025_later.json` | 判定 |
|---|---|---|---|
| **策略率** | **50 Hz（`:245` `DECIM = round(0.02/dt)` 硬编码）** | **`policy_hz = 100`** | ❌ **2×** |
| **物理步长** | `--dt` 默认 **0.001** | `physics_dt = 0.0005` | ❌ **2×** |
| 轮阻尼 | `--wk` 默认 **1.5** | `wheel_kd = 0.6` | ❌ |
| 轮半径 | `--wheel-r` 默认 **0.073** | `wheel_radius = 0.0625` | ❌ |
| 腿 kp / kd | 60 / 2.0 | 60 / 2.0 | ✅ |
| 动作尺度 | 0.5 / 10.0 | 0.5 / 10.0 | ✅ |

（文档字符串里写的"±30 Nm / ±8 Nm"是**过期注释**：实际实现从 MJCF 与 **ONNX 元数据契约**取力矩预算，
`EFFECT_LEG/EFFECT_WHEEL = 50.9/10.0` 只是 legacy fallback——这个设计本身是对的，
正是门禁需要的东西。）

**⇒ 直接把现在的回放器接成门禁，会"认证一台和实车不同的机器人"**（策略被以 50 Hz 调用、
物理步长 2×、轮阻尼 2.5×、轮半径 17% 差）。这与参考实现 sim2sim 的缺陷**是同一类**
（它把全部关节截到 ±30，而 URDF 是腿 50 / 轮 5）。

**另外两个硬前提**：
1. **`onnx` 与 `onnxruntime` 三个环境都没装**（`third_party/rc_mjlab/.venv` 里 `mujoco 3.13.0` 有，
   但 `onnxruntime` 没有）。按 `sim2sim_later/README.md` 的做法，在 rc_mjlab venv 里一次性
   `pip install onnxruntime` 即可（CPU wheel，不碰 CUDA）。
2. **MOD4 还没有自己的 ONNX 导出器**。`migration/linux/run_onnx_smoke.sh:27` 调的是
   `train/export_onnx.py`（V11 老机器），而 ONNX 元数据契约是 `V11_fix_working/train/export_onnx.py:59`
   写的（`metadata_props`）。MOD4 需要等价的一份，且必须把 §1 的**历史输入布局**一起写进元数据，
   否则门禁无法校验部署侧 FIFO 是否正确。

**修正后的第 5 项落地清单**：
1. 先**对齐回放器常量**（50→100 Hz、dt 0.5 ms、wheel_kd 0.6、wheel_r 0.0625），并把契约值作为
   唯一来源（从 `contract_rm2025_later.json` 读，而不是 argparse 默认值写死）。
2. 写 **MOD4 的 ONNX 导出器**：`runner.export_policy_to_onnx()` + 写入契约元数据
   （含 35/175 维输入布局、kp/kd/尺度/力矩/轮径/力矩-转速曲线）。
3. 写 `sim2sim_mod4/check_sim2sim_mod4.py`：沿用 `check()` 骨架 + 脚本化命令序列
   （洞 / 台阶 / 坡 / 跳）+ 终止与固定时域 + **明确阈值与退出码**。
4. 挂进 `final_acceptance_mod4.sh`：**不过就不产出交付包**。

### 5.4 ✅ 已完成第一步：`sim2sim_mod4/check_sim2sim_mod4.py`（可运行）

骨架沿用 `sim2sim_later` 的既有惯例：`check()` 累积失败、末尾 `RESULT: … PASS/FAIL`、
**退出码 0/2/3**（3 = 依赖缺失，**绝不静默跳过**）。

**契约段（`--stage contract`，纯 python，rc=0 通过）** —— 断言控制律必须来自契约而不是
harness 的 argparse 默认值：

```
[ok] policy rate is 100 Hz | physics dt is 0.5 ms | decimation is 20
[ok] onnx_play.py's policy rate default (50) differs from the contract (100 = 100 Hz),
     so the harness MUST read the contract
[ok] onnx_play.py's physics step default (0.001) differs from the contract (0.0005 s)
[ok] wheel_radius is 0.0625 m (got 0.0625; onnx_play.py defaults to 0.073)
[ok] export_action_permutation is [1,0,3,2,4,5]
leg kp/kd 60.0/2.0 | wheel kd 0.6 | scales 0.5/10.0 | efforts 40.0/5.776 Nm
```

**全量段立刻抓到三个真问题（rc=2）**：

| # | 发现 | 含义 |
|---|---|---|
| 1 | **串链 MJCF `timestep = 0.001 s`**，契约是 **0.0005** | **2× 不匹配**，与参考实现 sim2sim 同一类缺陷（后者静默跑在 2.5× 速度上） |
| 2 | `onnxruntime` 未安装 | 门禁**显式 FAIL**（这是设计），装 CPU wheel 即可 |
| 3 | **两个 MJCF 都没有 `<actuator>` 块**（0 个 actuator 标签，`scene.xml` 也只是 `<include>`，所以 `nu = 0`）—— 串链 `nq=15/nv=14`、并联 `nq=25/nv=24` 都能加载 | **硬集成缺口**：`onnx_play.py:178` 的 `AN = {mj_id2name(...mjOBJ_ACTUATOR, i): i}` 从模型自带执行器构建，`nu=0` 时 **`AN` 为空** → 默认的 `--effort-mode ctrl`（`:277` `d.ctrl[AN[cn]]`）会在第一步 `KeyError`。**修法二选一**：① 给 MOD4 MJCF 补 6 个 `<motor>`（更贴近部署的电机模型，推荐）；② 用 harness 已实现的 `--effort-mode qfrc`（`:382` `d.qfrc_applied[va[jn]] = u`，无需 actuator 即可跑，可先用来打通门禁） |

**剩下要做的**：① 把 MJCF 的 timestep 对齐到 0.5 ms（或让 harness 显式按契约驱动、不依赖 MJCF 的
`<option>`）；② 装 `onnxruntime`；③ 补 MOD4 的 ONNX 导出器（含契约元数据）；④ 脚本化四科目场景
+ 阈值；⑤ 挂进 `final_acceptance_mod4.sh`。

### 5.5 ✅✅ 门禁已全绿通过（2026-09-13 00:15，`RESULT: SIM2SIM MOD4 PASS`, rc=0）

上面 ①②③ 已完成，门禁对一条**真实策略**全绿：

**① 修掉 MJCF 的 timestep 陷阱**：两个 MJCF（`sim2sim/rm_vehicle/mjcf/rm_vehicle.xml` 串、
`sim2sim_cc/rm_vehicle_cc/mjcf/rm_vehicle.xml` 并联）的 `<option timestep="0.001">` → **0.0005**，
现在 `decim 20` 恰好是 **100 Hz**（备份 `.bak_pre_timestep`）。
不过根因其实在 harness 侧：两个 harness 都会覆盖 timestep，但 `sim_mujoco/onnx_play.py:127`
用的是**自己的 argparse 默认值 0.001**，而 `_CONTRACT_JSON` 还是 **Windows 路径**
（`D:/claude2/...`）⇒ 在目标机上**契约根本没被读到**，harness 静默降级。
→ 新增 `migration/linux/patch_onnx_play_contract.py`（契约路径改为相对本文件解析 + `--dt`/
`--wheel-r`/DECIM 全部从契约取），实测解析出 `dt=0.0005 / 100 Hz / wheel_r=0.0625 / DECIM=20`。

**② `onnxruntime 1.30.0`** 装进 `third_party/rc_mjlab/.venv`（走代理 `127.0.0.1:7897`）。

**③ 新导出器 `sim2sim_mod4/export_mod4_onnx.py`——完全不需要 GPU**：
直接从 checkpoint 的 `actor_state_dict` 重建模型（维度由权重形状唯一确定）、
`load_state_dict` 前做**白名单校验**（只容忍 `encoder.*`），
用 `model.as_onnx()` 的 dummy 输入跑 `torch.onnx.export`，
并把**契约值写进 ONNX `metadata_props`**。实测导出 fly 相位正在产出的 `model_15500.pt`：

```
input : obs (batch, 35)      output: actions (batch, 6)      opset: 17
metadata: leg_kp 60 | leg_kd 2 | wheel_kd 0.6 | scales 0.5/10.0 | wheel_radius 0.0625
          physics_dt 0.0005 | policy_hz 100 | wheel_no_load 55.36 | perm 1,0,3,2,4,5
          obs_layout single-frame-35 | encoder_history 0
```

**④ 门禁改动（修掉我自己 checker 的一个不一致）**：`--encoder-history` 默认改为 **auto(-1)**，
**读 ONNX 自己声明的 `obs_width`/`encoder_history` 并交叉校验**契约的 `frame_dim`，
而不是用一个写死的默认值（旧版本默认 5，误拒了一条合法的 35 维策略）。
现在 ONNX 必须声明布局、且 8 个契约值必须齐备，否则门禁 FAIL。

**⑤ 仍未做**：脚本化四科目场景 + 行为阈值（当前门禁校验的是**产物与契约**，
还没跑策略 rollout）、挂进 `final_acceptance_mod4.sh`。

### 5.6 ⚠️ rollout 那一半不是"顺手加一节"——需要连杆映射（本轮核实）

想把门禁从"校验产物"推进到"校验行为"（跑策略、判完成率），必须先解决
**策略动作空间 ↔ MuJoCo 模型关节**的对应，而它们**对不上**：

| 模型 | 关节 | 与契约的关系 |
|---|---|---|
| 串链 `sim2sim/rm_vehicle/mjcf/rm_vehicle.xml` | `left_front1_joint` / `left_rear1_joint` / `left_spring2_joint` + 轮（每侧 3 个） | ❌ 名字与结构都不同 |
| 并联 `sim2sim_cc/rm_vehicle_cc/mjcf/rm_vehicle.xml` | **19 个关节**（`left_rear1/2`、`left_spring1/2`、`left_front1..4` + 轮，每侧 8 个） | ❌ |
| 契约/策略 | `left_crank` / `left_hip` / `left_wheel_spin`（6 个执行关节） | —— |

**`grep -rl "left_crank\|left_hip" sim2sim/ sim2sim_cc/ sim_mujoco/` 无任何命中** ——
我们没有任何一个 MuJoCo 资产使用契约的关节名。

参考实现是怎么解决的：`mujoco/python_tools/onnx_mj_binglian.py` 用**连杆逆解 + 雅可比**把策略的
虚拟关节映到真实的五连杆执行器上（`solve_phi3_left/right`、`solve_phi_piandao`、
`DEFAULT_OFFSET=1.6614`、`l1=0.175`、`l2=0.208`，约 500 行）。而它的**串链** runner 没有做这件事
（子代理发现它 1:1 驱动了并不存在的 dof、把二级电机留在 0）——也就是说**连参考实现也只有并联那一半
是物理正确的**。

**⇒ 三条路**：
| 路径 | 做法 | 成本 |
|---|---|---|
| **A. 移植并联的连杆逆解** | 照抄 `solve_phi3_*` + 雅可比 + 关节映射（并联模型物理正确，参考已验证） | 中–高，但**有可对照的实现** |
| **B. 从 `robot.usd` 生成同构 MJCF** | 让 MuJoCo 模型直接带那 6 个执行关节 + 闭链 | 高（要转 USD→MJCF 并保住闭链） |
| **C. 降级为开环门禁** | 不跑策略，用契约 PD 律（`qfrc`）验证植物：重力站稳、受推恢复、不 NaN | 低，能抓植物/契约缺陷，**但不能验证策略** |

**建议 A**（与参考实现对齐、且它已证明可行），C 作为过渡。

### 5.7 ✅ 上一条结论**被本轮证据推翻**：并联 MJCF 就是 6 自由度植物，**不需要 IK**

上一节说"要 ~500 行五连杆逆解"是在**没看关节标记**的情况下下的判断。把两个 MJCF 的运动链完整 dump 出来后：

**并联 `sim2sim_cc/rm_vehicle_cc/mjcf/rm_vehicle.xml`（20 bodies / 19 joints / nq=25）**

- **恰好 6 个关节带 `class="motor"`** —— 正是策略的 6 个自由度：
  `left_rear1_joint`、`left_front1_joint`、`left_wheel_joint`（右侧同）×2
  （`class="motor"` 的定义：`damping=0 frictionloss=1.5 armature=0.0158`）
- **`neq = 6`**：六条 `<connect>` equality 约束把五连杆闭环起来
  （`front3↔rear1`、`front4↔rear2`、`spring2↔rear2`，左右各三）
- 每侧其余关节都是**被动**且带限位：`rear2 [-0.84,1.48]`、`spring1 [-0.18,0.32]`、
  `spring2` slide（`stiffness=6000 damping=150`，即气弹簧）、`front2..4 [-1.48,0.84] 等`

**⇒ 结构与训练植物同构**（6 个执行关节 + 闭链），因此：
1. **动力学**：给这 6 个关节施加契约控制律的力矩（`nu=0`，走 `qfrc_applied`），
   **闭环由 MuJoCo 求解器处理**（`neq=6`）——与训练时 PhysX 用兼容 mimic 约束闭合闭链等价；
   **不需要解析 IK、不需要雅可比力矩映射**。
2. **观测**：直接读这 6 个 `motor` 关节角 + floating base，按契约的 `LEG_ORDER`/`WHEEL_ORDER` 排好即可。

**⇒ rollout 的真实剩余工作缩小为**：① 确定 `left_crank`/`left_hip` ↔ `left_rear1_joint`/`left_front1_joint`
的**对应关系与符号/零点**；② 按契约 PD 律施加力矩 + 组装 35 维观测；③ 脚本化四科目 + 阈值。
**没有 500 行 IK**。

### 5.8 ⚠️ 映射仍未确定（探针写了，但方法不对；不要引用它的"结果"）

我写了 `sim2sim_mod4/calibrate_joint_map.py`（扫两个 motor 关节、量基座-轮距、按方向判对应），
过程中修掉自己两个 bug：**取两轮的 `min` 导致曲面恒定**（左腿动时右轮不动）、
以及**用宽域平均梯度**（强非线性映射会互相抵消）。但**它仍然没有把映射定下来**，原因有两个：

1. **`qpos0` 是运动学奇异点**：全关节为 0 时腿接近伸直，局部雅可比 ≈ 0
   （有限差分梯度 −0.0008，实测；参考实现里那些"奇异雅可比"守卫正对应这一点）。
2. **闭链映射强非线性**：曲面量程 0.136 m，但**四角值几乎相同**
   （(−1.2,−1.2)=−0.1345、(1.2,−1.2)=−0.1360、(∓1.2,±1.2) 同值）⇒
   大变化发生在网格内部，全域相关系数因此都 ≈0（`rear1` −0.011、`front1` +0.000）。

**所以探针输出的那个 `score 2/2` 是数值零的符号巧合，不是结论——本文件不采纳它。**

**正确的下一步是几何对应，而不是行为统计**：dump 每个 motor 关节在基座系下的**锚点位置与连杆长度**，
与训练植物（USD/CAD）里 `left_crank` / `left_hip` 的轴向位置逐一比对，按几何定名。
`sim2sim_mod4/calibrate_joint_map.py` 保留作为**几何比对的数据源**（它已经能打印 6 个 motor 关节名、
`neq=6` 的闭环、以及契约的 `mechanical_stop`：`hip=0.4503`、`crank=−0.6360`、
`input_difference_min_rad=−1.0843`）。

### 5.9 ✅ 几何比对做完了——**两个模型是同一拓扑、不同参数化的五连杆**（第三次也是最终的范围修正）

用几何（基座系锚点）而不是行为统计来定名，结果很干净：

| | 训练植物（rolling USD，`import_contract.json`） | 并联 MJCF（`sim2sim_cc`） |
|---|---|---|
| 两个电机关节 | `left_hip`（锚点 y=**0.18130**）、`left_crank`（y=**0.19877**） | `left_rear1_joint`、`left_front1_joint` |
| 锚点（基座系） | 两个**分离**的轴，间距 **0.01747 m** | 两个锚点**完全相同** `[0, −0.22385, 0.2121]`，间距 **0.00000 m** ⇒ **同轴** |
| 轴向 | 均为车体 Y | 均为 `[0,1,0]` ✅ |

**⇒ 它们是同一拓扑（6 电机 + 闭链）但参数化不同的五连杆**：
训练植物是**输入轴分离**（hip / crank 分置两轴，间距 17.5 mm）的构型；
并联 MJCF 是**两输入同轴**的构型（经典 5-bar，正是参考实现 `DEFAULT_OFFSET` 那种结构）。

**所以对应关系不是"改个名"**，也**不是**"500 行通用 IK"——而是**两个 5-bar 参数化之间的
关节空间映射（2→2）**：给定植物的 (hip, crank) 求 MJCF 的 (rear1, front1) 及其雅可比
（力矩按雅可比转置映射回去）。参考实现的 `solve_phi3_left/right` + `solve_phi_piandao`
正是这个模板，而**我们这次有了精确的几何输入**：契约里的关节锚点（上表）+ `bodies` 的连杆长度，
所以映射可以**从几何推导而不是照抄别人模型的常数**。

**范围修正三次的记录（留档，避免再走弯路）**：
1. 初判"需 ~500 行 IK"（未看关节标记）→ 过悲观；
2. 看到 6 个 `class="motor"` + `neq=6` 后判"不需要 IK，只需改名"→ **过乐观**（几何比对证明两者轴系不同）；
3. **最终**：需要**同轴↔分离轴 的 2→2 关节映射 + 雅可比**，几何参数可从契约直接推导。

### 5.10 ✅ 连杆长度比对：确实是**同一连杆的重新参数化**，映射是"常数角偏置"形式

把植物的腿链从契约的 `joints`（parent/child + `local_pos0`）重建出来，与并联 MJCF 的 body 偏移逐一对比：

| 环节 | 植物（rolling USD） | 并联 MJCF | 差异 |
|---|---|---|---|
| 输入轴到基座原点 | `left_hip` **0.1813** ／ `left_crank` **0.1988**（分离，差 0.0175） | `left_rear1`/`left_front1` 同为 **0.3084**（**同轴**） | 轴系不同 |
| 大腿段 | `left_thigh → left_knee` **0.2157** | `left_rear1 → left_rear2` **0.2100** | **2.6%** |
| 小腿段 | `left_shin → left_wheel_spin` **0.2588** | `left_rear2 → left_wheel` **0.2543** | **1.7%** |
| 四连杆从动侧 | `thigh→rocker` 0.1189、`rocker→distal` 0.0643 | `front1→front2` 0.1151、`front2→front3` 0.1370、`front3→front4` 0.2024 | 同量级 |
| 气弹簧 | `gas_inner → gas_barrel` **0.1794** | `spring1 → spring2` **0.1722** | **4.0%** |

**⇒ 连杆长度在 1.7–4% 内吻合**（差异来自不同 CAD 版本的取整/网格化），
所以并联 MJCF **不是另一台机器人，而是同一条腿的另一种参数化**：
植物把两个输入**分置两轴**（相距 17.5 mm），MJCF 把两个输入**同轴**安装。

**⇒ 映射的形式因此确定**：每个输入 = 对应 MJCF 关节 + **一个常数角偏置**（吸收轴分离与装配相位），
正是参考实现 `DEFAULT_OFFSET = 1.6614` 那类常数。剩下的是**数值拟合**（不是推导新公式）：
用植物的 FK（可用 `migration/linux/check_usd_closure_consistency.py` 那套 pxr 前向运动学，
它已经能按关节向量解闭链）与 MJCF 的 FK，对少数几个姿态求 `(rear1, front1) = f(hip, crank)`
的常数偏置与符号，再取数值雅可比做力矩映射。

### 5.11 ✅ 拟合已做：**基座系偏移 + 一个轴确定了，另一个轴被证明"从轮心位置不可辨识"**

新增 `sim2sim_mod4/fit_joint_map.py`（在 **isaaclab env** 里跑，那里同时有 `pxr` 与 `mujoco`）：
对植物的 USD 做前向运动学得到 `left_wheel` 在 chassis 系的位置，对 MJCF 做同样的，
再按曲面对齐 + 最近邻匹配 + 线性拟合。三轮迭代修掉两个方法问题：

1. **参考系不同**：植物 wheel z = −0.273..−0.240，MJCF 是 0.000..0.026 ⇒ 直接匹配是"拿苹果比橘子"。
   先按质心对齐求出**基座系偏移**：
   **Δ = (+0.0008, **−0.2706**) m**（植物 chassis 原点在 MJCF `base_link` 原点上方 **27.06 cm**）。
   对齐后匹配残差从 0.268 m 降到 **mean 9.2 mm / median 6.4 mm**，**81% 的样本 < 1 cm**。
2. **边界假象**：`front1` 的拟合值恒为 −0.5000（扫描区下界）、rmse 恰好 0.00000 —— 那不是拟合，
   是"最佳匹配永远落在网格边缘"。加了**边界钉住比例**诊断后判定为**不可辨识**。

**当前结论（诚实版）**：

| 项 | 结果 | 判据 |
|---|---|---|
| 基座系偏移 | **Δz = −0.2706 m** | 质心对齐，匹配残差降至 9.2 mm |
| `hip ↔ rear1` | **rear1 ≈ 1.169 · hip**（rmse 0.038 rad） | 边界钉住率 14%（<20% 可接受） |
| `crank ↔ front1` | **从轮心位置不可辨识** | 边界钉住率 **100%** |

**为什么第二个轴不可辨识**：轮心位置对 `front1` 几乎不敏感（§5.8 的相关系数也是 +0.000），
在 `qpos0` 附近该链接近死点。

**能定它的可观测量（下一步）**：改用**被动关节角**做匹配（MJCF 的 `rear2`/`front2..4` ↔ 植物的
`rocker`/`distal`/`knee`），或直接施加植物自己的**输入差约束**
（契约 `training_window.input_difference_min_rad = −1.0843`，它把 crank 与 hip 绑在一起）——
即用运动学关系而不是轮心位置来定第二轴。

**结论**：`sim2sim_mod4/fit_joint_map.py` 已经是可复用的拟合工具（含参考系对齐与可辨识性诊断）；
rollout 还差"第二轴的可观测量"这一步，**不需要解析 IK**（与 §5.10 的连杆长度证据一致）。

### 5.12 ⚠️ 上面那条"不可辨识"是**我的采样方法错了**——`mj_forward` 不求解 equality 约束

这是本轮最重要的自我纠正。**`mj_forward` 只做运动学，不求解 `<connect>` equality 约束**，
所以前端那条链在采样时是**悬空**的，轮心位置自然不随 `front1` 变。实测对照：

| `(rear1, front1)` | `mj_forward`（仅运动学） | `mj_step`（约束被求解） |
|---|---|---|
| (0.0, 0.0) | [−0.0008, +0.0001] | [−0.0469, +0.0266] |
| (0.3, 0.0) | [−0.0634, +0.0098] | [−0.0404, +0.0820] |
| (0.3, **0.6**) | [−0.0634, +0.0098] ← **与 front=0 逐位相同** | [−0.1549, +0.0630] |
| (0.0, **0.6**) | [−0.0008, +0.0001] ← **与 front=0 逐位相同** | [−0.2264, −0.0318] |

⇒ **§5.8 的"front1 相关系数 +0.000"与 §5.11 的"边界钉住 100% / 不可辨识"都是这个假象**，
不是连杆的性质。约束由**求解器**执行，所以采样必须让机构在 `mj_step` 下收敛
（本次用 400 步、关闭重力以隔离运动学；收敛后约束残差 max 1.0e-3）。

**修正采样后重跑拟合**：

| 量 | 修正前（假象） | 修正后（约束已求解） |
|---|---|---|
| MJCF 轮心范围 | x −0.198..0.197、z 0.000..0.136 | x **−0.239..0.140**、z **−0.284..0.120**（真正 2-D 运动） |
| `front1` 边界钉住率 | **100%**（不可辨识） | **12%**（可辨识）✅ |
| 匹配残差 | 29.7 mm | **mean 10.2 mm / median 8.3 mm**，65% 样本 < 1 cm |
| 线性拟合 | — | `rear1=0.059·hip−0.097`(rmse **0.32**)、`front1=−0.031`(rmse **0.39**) ❌ |

**最终结论（第四次也是收敛的版本）**：
- 两个机构**运动学相似**（65% 的采样对在 1 cm 内对齐，与 §5.10 的 1.7–4% 连杆长度一致）；
- 但映射**不是"常数偏置"形式**（线性拟合 rmse 0.32/0.39 rad，不成立）⇒ 是**非线性重参数化**；
- 所以正确做法是**用匹配表 + 数值雅可比**，而不是找一个解析常数：
  `fit_joint_map.py` 已经输出 `(hip, crank) → (rear1, front1)` 的匹配对，
  对其做局部有限差分即得雅可比，可直接驱动 rollout 的力矩映射。**仍不需要解析 IK。**
- ⚠️ 1 cm 量级的表面对齐残差意味着 sim2sim rollout **不可能逐位一致**（两个不同仿真器的固有差异），
  门禁的阈值必须按这个量级设定，不能要求与 Isaac 完全吻合。

**对照：串链 MJCF 是简化模型**（`neq=0`、每侧 `front1` 铰链 + `rear1` 铰链 ±2.2 + `spring2` ±1 mm 滑移），
两条腿是**串行树**而非闭链 ⇒ 它**不适合**作为 MOD4 的 rollout 植物；并联那份才是。

**这也是参考实现踩过的坑**：它的**串链** runner（`onnx_mj_chuanlian.py`）1:1 驱动了模型里并不存在的
dof、把二级电机留在 0，只有**并联** runner（`onnx_mj_binglian.py`）是物理正确的。

**本轮已完成且可复现的部分**：
```
RESULT: SIM2SIM MOD4 PASS   (rc=0)
[1] 契约 100 Hz / 0.5 ms / decim 20 / wheel_radius 0.0625 / 动作置换 全绿
[2] ONNX 布局由元数据自声明并与契约交叉校验
[3] 串/并联 MJCF 均加载，且按 0.0005 s 积分 = decim 20 时的 100 Hz
[4] ONNX: 1 输入 (batch,35) / 1 输出 (batch,6) / 8 个契约值齐备
```

---

## 6. 混合阶段 env 提到 ≥1024

**结论：这条不需要写代码——1024 的通路本来就完整，而且实测显示它几乎不花额外时间。**

### 6.1 通路现状（全部核实）

| 项 | 状态 | 证据 |
|---|---|---|
| 起链参数 | ✅ 现成 | `run_special_phases_v3.sh:37` `ENVS=${ENVS:-512}`，`ENVS=1024 bash …` 直接生效 |
| 场地文件 | ✅ 已有 | `maps/arena_1024.usda` + `.json` |
| 场地间距 | ✅ 已配 | `mod4_task.py:894` `cfg.scene.env_spacing = 34.0`（rmuc2026 模式） |
| **上限** | ⚠️ **1024 是硬上限** | `build_layout.py:12`：`if not 1<=num_envs<=1024: raise ValueError('Supported packaged layout range: 1..1024')` ⇒ "≥1024" 实际只能是 1024，除非另生成场地 |
| 显存 | ✅ 充裕 | 512 env 用 4606 MiB / 24564 MiB ⇒ 1024 约 9 GB |

### 6.2 ⚠️ 实测：1024 env 的单迭代耗时**与 512 env 基本相同**（清单里"大约翻倍"偏悲观）

从现有日志按 `num_envs` 分组统计 `Iteration time` 中位数：

| env | run 数 | 单迭代耗时中位数 |
|---:|---:|---:|
| 64 | 4 | **7.50 s** |
| 512 | 18 | **9.00 s** |
| **1024** | **1（`stage_run.log`，2026-09-11 21:45，306 迭代）** | **9.02 s** |

关键证据：`stage_run.log` 是**真实的 1024 env run**（`"num_envs": 1024`），首/末迭代 9.03 / 8.53 s，
306 迭代共 54:53。而 512 env 的 18 个 run 中位数也是 9.00 s。

**⇒ 单迭代耗时由"固定的物理步数"主导，不由 env 数主导。** 把 env 提到 1024
**几乎不增加墙钟时间，却让每迭代样本数翻倍**——是接近免费的 2× 数据吞吐，
而不是"时间翻倍换样本翻倍"的等价交换。

⚠️ 限定：那条 1024 记录是 **2026-09-11 的旧代码 + `stage_run` 相位**，属**指示性对比、非受控 A/B**。

### 6.3 建议

1. v2 的统一/混合阶段直接用 `ENVS=1024`（`--num_envs 1024` 由链自动带上）。
2. 链退出后做一次**受控 A/B**：同一相位、同一 iters，分别 `ENVS=512` 与 `ENVS=1024` 各跑 ~20 迭代，
   记录 `Iteration time` 与显存，把上条指示性结论变成受控数据（几分钟即可）。
3. 若要 >1024，必须先扩展 `build_layout` 的场地生成（硬上限 1024），并重新评估
   34 m 间距下 2048 env 的网格尺寸（1024 → 32×32 网格 ≈ 1088×640 m）。

---

## 7. 参考实现细节提取状态

| 主题 | 状态 | 落到本文哪一节 |
|---|---|---|
| obs 历史 + 编码器 + 导出 | ✅ 已提取并整合 | §1.1 / §1.2 |
| 奖励截断 + tracking sigma | ✅ 已提取并整合 | §3.1–§3.5、§3.6（陷阱） |
| DR 范围（含动作延迟量纲） | ✅ 已提取（三套配置 + 延迟量化机制 + 他们的 off-by-one） | §2 |
| terrain.curriculum 判定 | ✅ 已提取并整合（**纠正了"成功率 >0.7"的记忆偏差**） | §4.1 / §4.2 |
| ONNX→MuJoCo sim2sim 流程 | ⏳ 子代理 43920284 运行中 | 待补 §5.1 |

**参考仓库的两个"代码陷阱"（勿照抄）**：
1. `scripts/export_encoder_jit.py` 头部注释写 `27×5=135`，与 shipped 配置（`25×5=125`）矛盾——
   以 `export_onnx/export_onnx.py` 的常量为准。
2. `rsl_rl/storage/rollout_storage.py:251` 在 else 分支引用了未定义的 `observations`（会 NameError，
   只是当前分支未命中）。
3. DR 侧：`legged_robot.py:1146-1160` 的 `action_fifo` 尺寸 `ceil(10ms/0.005)=2`（合法 idx 0..1）
   但采样器可产出 idx=2 ⇒ 25% 的 env 越界；live source 因延迟开关关闭而休眠，但**在他们 47 个
   开了延迟的训练快照里是活的**（evolved 版本用 `+1` 修了）。**我们自己的实现经核实没有这个问题**
   （`mod4_task.py:721` 分配 `max_lag+1` 槽、`:745` 对 idx 取 `clamp`）。

---

## 8. 实测：spin 阶段走完完整门禁（2026-09-13 00:09，新植物第一个）

评测管线三个缺陷修好后，spin 是**四科目里第一个真正走完**「版本门禁 → 全路线评测 → 专项评测」
的相位。检查点 `logs/isaac_mod4/2026-09-12_23-00-03_mod4_fixed_mixed/model_15497.pt`。

**✅ 专项评测（`slope_spin`，64 env × 2200 步）—— 过门**

| 指标 | 值 | 门槛 | 判定 |
|---|---:|---:|---|
| complete_rate | **0.703** | 0.60 | **PASS** |
| spin_deg | **1973.7°** | 360° | **远超** |
| progress_sum | 268.7 | — | — |
| closure / mimic | 0.38 mm / 1.7 mrad | <2 mm / <0.01 | ✅ |

**全路线评测（64 env × 2200 步，仅 4–9 env/路线，统计偏弱）**

| 路线 | complete | 备注 |
|---|---:|---|
| ramp_down / step_down / run | **1.000** | ✅ |
| slope_spin | 0.500 | 混合采样下 |
| ramp_up | 0.222 | |
| rough_cross / **step_up** / **tunnel_cross** / **fly_jump** / jump_in_place | **0.000** | tunnel 的 `underpass=0`、`roof_hit=0` |

**同时验证了两个修复真的生效**：
- `VERSION_CHECK=PASS` 且**评测没有被跳过**（修复前 tunnel/terrain 都在门禁处 return）✅
- `min_clearance_m = None`（不是 **999.0**）——从未进洞的路线现在报 null，而不是看起来像全图最宽裕的穿越 ✅
- closure 0.38–0.85 mm、mimic 1.7–1.8 mrad ✅

**与旧植物基线对比**：旧 `docs/terrain_spin_model_11448.json` 是 0.95（64 env）。
新植物 **complete 0.703 但 spin_deg 1973.7°**（交接文档记的旧基线是 395.4°）——
完成率低、单回合转得多，两者不是同一配置，**不可直接判优劣**，但小陀螺的能力显然在新植物上保住了。

**小结（四科目）**：小陀螺 ✅ 过门；上台阶 0.000、过洞 0.000（underpass 0）、飞坡 0.000 —— 后三者
正是 v2 那套改造（编码器、DR、奖励截断、课程）要解决的问题。链随后进入 **fly 相位**
（PID 874860，00:09:30 起，fly_jump 采样提到 34.3%），再跑 jump，预计 **01:50 前后**收尾。

**顺带**：`onnxruntime 1.30.0` 已装进 `third_party/rc_mjlab/.venv`（代理 `127.0.0.1:7897`，
直连会 read timeout）。sim2sim 门禁因此只剩两个已知阻塞：**串链 MJCF timestep 0.001 vs 契约 0.0005**、
**还没有 MOD4 的 ONNX 可检**。

## 9. v2 落地 runbook（链退出后照着做）

**前提**：链已退出（`pgrep -af "[t]rain_mod4_ppo"` 为空），GPU 空闲，且**已提交/备份当前状态**。
所有补丁都会自己写 `.bak_pre_*`，回滚 = 把 `.bak` 覆盖回去。

### 9.0 ⚠️ 先读这条：**打开编码器会让热启动失效**（用真实检查点验证过）

用 `logs/isaac_mod4/2026-09-12_23-00-03_mod4_fixed_mixed/model_15400.pt` 的
`actor_state_dict` 与新建的 `LatentEncoderModel` 逐键比对：

| 配置 | 结果 |
|---|---|
| `RM_SEQ_ENCODER=0`（obs 35，**补丁默认**） | `strict=True` **OK**（键与形状完全一致） |
| `RM_SEQ_ENCODER=1`（obs 175） | `strict=True` **FAILS**：`mlp.0.weight` **(256,35) → (256,38)** 形状不符，另多出 6 个 `encoder.*` 键 |

原因：rsl_rl 的 `OnPolicyRunner.load(..., strict=True)` → `PPO.load` →
`actor.load_state_dict(..., strict=True)`（`rsl_rl/algorithms/ppo.py:444-459`），而我们的
`train_mod4_ppo.py:235` 调 `runner.load(warm)` 用的是默认 `strict=True`、且默认 `load_cfg`
**包含 `optimizer: True`**（该 checkpoint 的优化器是 1 个 param_group / 17 个参数，加编码器后数量也变）。

**⇒ 结论与对策**：
- **应用 `patch_obs_history_encoder` 本身是安全的**（补丁默认 `RM_SEQ_ENCODER=0`）。
- **但一旦把 `RM_SEQ_ENCODER=1` 打开，就不能再从任何现有检查点热启动**——这与目标里
  "在现有检查点上继续"对第 1 项是冲突的。三条路选一：
  - **A. 从零训** actor/critic（编码器必须从零；actor 首层输入维度变了也必须重训）。成本最高。
  - **B.（已实现，推荐）部分热启动**：`migration/linux/patch_partial_warmstart.py`
    —— 把 checkpoint 的 `mlp.0.weight` **前 35 列原样拷入**新模型、新增 3 列**置零**
    （所以新维度在第 0 步贡献恰好为零，actor 真的从旧策略继续），丢掉不再匹配的优化器状态，
    并用 `strict=False` + **白名单校验**（只容忍 `encoder.*`，其他意外的键一律拒绝）。
    **用真实检查点验证过**：填充后 `mlp.0.weight` 35→38、前 35 列逐位相同、新 3 列全 0；
    `load_state_dict(strict=False)` 的 missing 恰好是 6 个 `encoder.*`、unexpected 为 0。
    该补丁**必须先跑 `patch_obs_history_encoder.py`**（前置检查会返回 rc=3 并在提示里说明）。
  - **C. 先不开编码器**：先落第 2/3 项（DR + 奖励截断，**不改变网络形状、可正常热启动**）跑一轮，
    编码器留到下一轮再做。
- 无论选哪条，`critic` 不受影响（它的观测集没变，仍是同形状的普通 `MLPModel`）。

### 9.1 应用补丁（顺序有依赖，别打乱）

```bash
cd /home/egde/fangzhen_linux
# ORDER MATTERS in two places (both verified by the sandbox composition test):
#  * patch_partial_warmstart needs patch_obs_history_encoder first (its precondition guard
#    returns rc=3 otherwise);
#  * patch_tunnel_crouch_gate needs patch_crouch_pose_kernel first.  Both rewrite the SAME
#    `return` line of tunnel_crouch_pose; the gate patch handles the post-kernel and the legacy
#    shapes, but the kernel patch only recognises the legacy block, so kernel MUST come first.
#    A wrong order fails loudly ("ANCHOR FAIL body: 0 matches", rc=2) -- it cannot pass silently.
#  * patch_chain_frozen_plant_paths must be LAST (bash reads a running script incrementally).
for P in patch_reward_clip_and_sigma patch_dr_defaults patch_action_delay_substep \
         patch_obs_history_encoder patch_partial_warmstart patch_crouch_pose_kernel \
         patch_tunnel_crouch_gate patch_jump_launch_ready patch_route_curriculum \
         patch_onnx_play_contract patch_acceptance_sim2sim_gate \
         patch_acceptance_gain_parity \
         patch_manifest_effective_knobs patch_chain_frozen_plant_paths; do
  echo "=== $P"; python3 migration/linux/$P.py --check && python3 migration/linux/$P.py
done
```

| 顺序 | 补丁 | 为什么这个位置 |
|---|---|---|
| 1 | `patch_reward_clip_and_sigma` | 奖励形状影响一切；默认 `safe` 模式保护 `route_success` |
| 2 | `patch_dr_defaults` | DR 默认开 + 范围对齐；必须与 1 同时生效才是同一实验 |
| 3 | `patch_action_delay_substep` | 延迟粒度；与 2 同属 DR，一起验证 |
| 4 | `patch_obs_history_encoder` | 改观测维度 → **会改变策略输入形状**，必须在起链前 |
| 5 | `patch_crouch_pose_kernel` | 过洞奖励核；独立于上面 |
| 6 | `patch_chain_frozen_plant_paths` | 改的是链脚本本身（被 bash 增量读取），**只能最后做** |

### 9.2 逐项验证（每步都要有证据，不要只看 `--check`）

```bash
# 1) 语法 + 冻结哈希（应显示 changed: 0 之后才有意义——这些文件现在不再是冻结集）
bash -n migration/linux/*.sh
python3 -m py_compile isaac/mod4/*.py migration/linux/*.py
# 2) 奖励截断：起一个短 run，看 stderr 里的
#    [reward-clip] mode=safe clip=2.50 clipped=N skipped=M
#    [reward-clip]   SKIPPED (|weight| 20 > 2.5): route_success      <-- 必须出现
# 3) 编码器：起链日志里应出现
#    Actor Model: LatentEncoderModel(...)   /   Critic Model: MLPModel(...)
#    manifest 的 policy_obs_dim 应变成 175（原来 35）
# 4) 延迟：manifest 里 action_delay_substeps=(10, 5.0)（0.5 ms × 10 = 5 ms）
# 5) DR：manifest 的 env 里 RM_DR_OFF=0，effort_scale legs=(0.9,1.1)
```

**smoke 门禁**：v2 第一次起链**必须**含 `smoke` 相位（它不占多少时间），因为改了观测维度、
奖励截断与 DR 三项。注意 terrain 阶段的闭链 session max 已到 **2.035 mm**（门禁 2 mm），
smoke 可能因此 FAIL —— 若 FAIL 先看是闭链还是 NaN/OOM，别直接放过（见 §4.7）。

### 9.3 起 v2 链（1024 env，见 §6）

> **先做这一步（约 1 分钟 GPU）**：`SMOKE=1 PHASES="smoke" bash migration/linux/run_special_phases_v3.sh <ckpt> smoke 1`
> —— **本次链是带 `from_phase=tunnel` 启动的，smoke 从未跑过**（日志：`[v3] skip phase smoke`）。
> 跳过它的理由是**探针**测到的 0.002035 m（超过严格的 <0.002 门禁），而**评测**实测闭环只有
> 0.00056–0.00085 m，终止阈值是 0.002（`mod4_task.py:1655`）。**这个跳过是从上一轮继承的假设，
> 没有被重新验证过**；先实测一次，过了就把 `FROM` 设成 `smoke`（多一层体检），没过再继续跳过。


```bash
CKPT=logs/isaac_mod4/<链尾 run>/model_<N>.pt      # 用 8.1 之前那条链的最终 checkpoint
setsid nohup env ENVS=1024 bash migration/linux/run_special_phases_v3.sh \
  "$CKPT" tunnel 1000 > logs/isaac_mod4/chain_v2a_run.log 2>&1 < /dev/null &
tail -f logs/isaac_mod4/chain_v2a_run.log
```

- `from_phase=tunnel` 会自动跳过 smoke（`phase_index tunnel` = 1）；**要跑 smoke 就从 smoke 起**
- 1024 env 的期望单迭代耗时 ≈ **9 s**（§6.2 实测），1000 迭代 ≈ **2.5 h/相位**，
  五相位 ≈ **12 卡时 ≈ ¥25**

### 9.4 起链后 30 分钟内该看的四个数

| 指标 | 期望（与 512 env 的 400 迭代基线对比） |
|---|---|
| `Episode_Reward/crouch_pose` | 从**恒 0** 变成非 0（高斯核生效的标志） |
| `Episode_Reward/jump_push` | safe 模式跳过截断，量程不再被压到 25% |
| `Metrics/plant/closure_err_session_max_m` | 应 < 2 mm；若 ≥2 mm 记录是哪条路线 |
| `Metrics/spin_360_rate` / `route_complete_rate` | 与 0.03 / 0.19 的 512 env 基线对比（注意 1024 下统计口径变了） |

### 9.5 起链前静态预检（已完成，两处风险均排除）

**风险 1：有没有代码硬编码 35 维、在编码器打开后静默出错？** —— 没有。

| 位置 | 结论 |
|---|---|
| `train_mod4_ppo.py:170` `info["policy_obs_dim"]` | **从 env 现算**（`group_obs_dim["policy"]`）⇒ 打开编码器后自动变 175 ✅ |
| `sim2sim_mod4/check_sim2sim_mod4.py` / `export_mod4_onnx.py` | 同时支持 35 与 175，且门禁**读 ONNX 自声明布局** ✅ |
| 其余出现 "35" 的地方 | 全是注释/docstring，或**另一台老机器的** `sim2real/dump_obs_real.py` / `patch_jump_channel.py`（真机部署侧，属于 §1.3 已登记的"必须同步契约"项） |

**风险 2：`handle_deprecated_rsl_rl_cfg` 会不会因为我把 `policy=` 换成 `actor=`/`critic=` 而报错？**
—— 不会，而且路径正好。**实测安装版本是 `rsl-rl-lib 5.0.1`**（不是 4.x）：

- 该函数在 **`rsl-rl >= 4.0.0`** 分支里，只有 `policy` **存在**时才用旧 cfg 反推 `actor`/`critic`
  （`utils.py:73-120`）⇒ 我不设 `policy`，这段逻辑直接跳过 ✅
- **`>= 5.0.0`** 分支调用 `_update_distribution_cfg`，而它的第一步就是
  `if model_cfg.distribution_cfg is not None: pass`（`utils.py:243-244`）
  ⇒ 我显式给的 `GaussianDistributionCfg(init_std=RM_INIT_STD, std_type="scalar")` **被原样采纳**，
  随后那些 deprecated 字段（`stochastic`/`init_noise_std`/…）被 `del` 掉 ✅
- critic 侧我不给 `distribution_cfg`（`None`）⇒ `stochastic` 保持 MISSING、不进 `elif` ⇒ 确定性 critic ✅
- **注意**：`4.0.0 <= 版本 < 5.0.0` 会走 `_validate_old_stochastic_cfg`（**校验**而非迁移），
  那是唯一可能因缺字段报错的分支——我们是 5.0.1，不在其中 ✅

**结论**：runbook §9.1 的 10 个补丁 + §8.3 的起链命令，**在 rsl-rl 5.0.1 上不存在已知的启动期风险**；
`RM_SEQ_ENCODER=0`（默认）时行为与今天一致，可逐项开开关。

### 9.6 尚未定的事（需要你拍板）

1. **第 4 项课程走哪条路径**（§4.3 的 A/B/C）——建议先 B。
2. **奖励截断口径**：默认 `safe`（保护 `route_success`）；要完全照抄参考就用
   `RM_REWARD_CLIP_MODE=all`，但**先读 §3.6**。
3. **小陀螺 sigma**：默认已统一到 `RM_TRACK_SIGMA=0.5`，需要保留自研核就显式给别的值。
4. **腿环刚度**：继续用 `RM_LEG_KP=2500`（与部署契约的 60 差 41.7×，§4.6）还是改回 60 重训。

---

## 11. 复旦**部署**仓库分析（`XYEGA_RM2026_WheelLeg_Infatry_RLdeploy`）

来源：`github.com/chushanxiaodaoshi/XYEGA_RM2026_WheelLeg_Infatry_RLdeploy`（经代理 socks5h 拉取，
1.5 MB / 40 条目）。它自述与 `yly-true/fudan_rl_wheel_leg`（训练/sim2sim 仓库）是同一战队的两半：
*"运动学解算的相关内容其实就是杨佬在 sim2sim 里面验证通过后迁移下来的"*。

### 11.1 ✅ 它就是训练仓库缺的那份"部署契约"——而且**含解析五连杆解**

`pseudocode/math_core.cpp`（358 行）给出了完整可用的解析解，正是我们 §5.9–5.12 一直在拟合的东西：

```
solveLegGeometry(phi1, phi4):        // 两个真实电机角 → 虚拟腿状态
    x_b = l1·cos(phi1), y_b = l1·sin(phi1)
    x_d = l1·cos(phi4), y_d = l1·sin(phi4)
    圆-圆求交 →  phi2 = 2·atan2(b0 + √disc, a0 + c0)
    phi3 = atan2(y_c − y_d, x_c − x_d)
    l0   = √(x_c² + y_c²)          // 虚拟腿长
    phi0 = atan2(y_c, x_c)         // 虚拟腿摆角
solveJaccobian(phi1,phi4,g):  dphi3/dphi1, dphi3/dphi4
buildForceTorqueMap(...):     完整 2×2 雅可比 j11..j22 + det + 有效位，
                              奇异守卫 kMinSin=1e-4 / kMinDet=1e-6
```

**输入映射（左右不对称！）**：
```
左: phi1 = ls_angle(小腿)   phi4 = lt_angle(大腿)     relative_phi3 =  phi3 − phi4 − π/2
右: phi1 = −rs_angle        phi4 = −rt_angle          relative_phi3 = −phi3 + phi4 + π/2
```

**⇒ 这解释了我在 §5.8/5.11 为什么用"轮心位置"匹配会含糊**：策略的四个腿自由度是
**(大腿, 虚拟小腿)**，而"虚拟小腿"是由 `solveLegGeometry` 从两个真实电机角**算出来的**——
所以正确的对应应该在 **(l0, phi0) 虚拟腿状态**上做，而轮心位置本身是 l0/phi0 的极坐标表达，
两者等价，但对 `(phi1, phi4)` 的雅可比在默认姿态附近可能退化。**有了这段解析解，就不必再数值拟合**：
直接用我们自己的 l1/l2 + 偏置，令我们植物的 (l0, phi0) 与 MJCF 的一致，即可解出偏置与符号。

**部署流水线（readme 原文）**：传感器 → 电机零点转换（实机→策略） → 虚拟腿运动学（五连杆→phi3/l0/雅可比）
→ 构建 25 维观测 → **125 维历史（5×25，循环左移 [t−4…t]）** → CubeAI 双输入推理 → **PD + 雅可比映射**
（虚拟力矩→实际关节力矩 + 气弹簧补偿） → 物理电机索引映射（推理索引→CAN 通道）。

**部署契约常数（`math_core.hpp`）**：

| 项 | 值 | 我们契约 |
|---|---|---|
| `kPosActionScale` / `kVelActionScale` | **0.5 / 10.0** | **0.5 / 10.0** ✅ 一致 |
| `kRealTorqueLimit` / `kClipActions` | 100.0 / 100.0 | — |
| `kParallelTorqueLimit` / `kWheelTorqueLimit` / `kJumpWheelTorqueLimit` | 35.0 / **5.0** / 4.0 | `leg_effort` 40 / `wheel_effort` **5.78** |
| 气弹簧补偿 | 370.1（spin 270.1/300.1） | `gas_springs`（我们做 DR，不显式补偿） |
| `kThighOffset` / `kShankOffset` | **0.2569 / 0.767** | ❓ 我们列为**待标定的硬件项**（§9.6） |
| `obs_dof_pos`（4 维） | `[-0.23, -0.65, 0.23, 0.65]` | — |
| `cmd_scale` | `[3.0, 0.25, 5.0]` | ✅ 与我们的命令缩放同量级 |
| 硬件 | 4× **8009P** 髋 + 2× **3508** 轮 + **16.33** 减速箱 | DM-J8009-2EC（内部 9.0）+ DM3519+15.8 |
| 跳跃阶段常数 | `noScale 0.1 / putScale 0.4 / FTPScale 1.0` | — |

### 11.2 ⚠️ 对我们的一个硬提醒：**腿环增益差 166×**

| | leg kp | leg kd | wheel kd |
|---|---|---|---|
| 复旦**实机部署**（stable / spin / jump） | **15 / 10 / 6** | 1.0 / 1.0 / 0.5 | **0.1** |
| 我们部署契约 | **60** | 2.0 | 0.6 |
| 我们训练实际 | **2500** | 10 | — |

- 训练/契约 = **41.7×**（§4.6 已记）
- 契约/复旦实机 = **4.0×**
- **训练/复旦实机 = 166.7×**

⇒ 一支同样打 RM 的战队，**实机上跑的是 kp 6–15**。我们契约的 60 已经比他们高 4 倍，
而**训练用的 2500 是他们的 167 倍**。这强烈支持"`RM_LEG_KP=2500` 是仿真侧的产物、不是可部署配置"
这一判断（§9.6 ② 那个待你拍板的问题），也说明**per-skill 增益**（他们 stable/spin/jump 用不同 kp）
是值得考虑的部署形态。

### 11.3 ⚠️ 但他们的**产物不自描述**（这一环我们反而领先）

4 个实际部署的 ONNX（`stable/spin/upstairs/jump`）我都解析过：

```
inputs = obs[1,25] + obs_history[1,125]     outputs = actions[1,6]     opset 17
metadata_props: **NONE**（全部四个都没有）
```

**契约只活在文件名里**：`stable_pos0.23_0.65_p15.0_d1.0_0.1.onnx`（pos 目标、p、d…）。
⇒ 改名即丢契约、无法机器校验。**我们的导出器把契约写进 `metadata_props` 且门禁强校验，这一点严格更优**
（§5.5）。他们的文件名约定可作为"最低限度做法"参考，也是反例。

### 11.4 其他值得记的部署实践

- **per-skill 策略切换**（`ChassisPolicy::{Stable,Spin,Jump,Upstairs,Stop,...}` + 翻倒自救策略），
  **不是**单一统一策略 —— 与用户"统一策略"的目标方向相反，但说明工程上分科目是可行的过渡形态。
- **电机零点与索引映射**：`kThighOffset/kShankOffset` + `LEFT_THIGH=0, RIGHT_THIGH=1,
  RIGHT_SHANK=2, LEFT_SHANK=3, RIGHT_WHEEL=4, LEFT_WHEEL=5`（**左右小腿在 CAN 侧是反的**）。
  这正是我们 §9.6 里"编码器零位/电机台架"那项的答案形态。
- **硬件保护**：髋关节接固态继电器 + 超电 + 大容值电解电容，防剧烈运动时髋电机进欠压保护；
  他们明说"翻倒自救、功率控制与部署相关性弱，只给思路"。
- **仿真里做、实机上用**的经验：`phi3` 是**虚拟**量、`relative_phi3` 还带 `−π/2` 与左右镜像 ——
  这类符号约定如果搞错，仿真与实机就会差一个镜像，而**不会报任何错**。

### 11.5 与训练仓库合起来看

两半放在一起才完整：训练仓库给了**奖励/DR/课程**，部署仓库给了**契约/运动学/推理/保护**。
但**两边都没有自动化验证**——训练侧 sim2sim 无门禁（§5.1），部署侧产物无元数据（§11.3）。
⇒ 我先前那句"跑通过、但没被验证过"对**两半都成立**；我们这两天的版本门禁/冻结哈希/ONNX 契约元数据/
sim2sim 门禁，正是补这一环。

---

## 12. 我们自己也有同一类可复现性缺口（被复旦的失效模式照出来的）

对照复旦"13/47 个 run 静默用 140 维 critic"那件事，我回头查了**我们自己的 manifest**：

```python
# train_mod4_ppo.py:283（现状）
"env": {k: os.environ[k] for k in sorted(os.environ) if k.startswith("RM_")},
```

这是**进程环境变量的快照**，不是**代码实际解析出的配置**。实测 50 个 MOD4 run 的该字典大小：

| `RM_*` 键数 | run 数 |
|---|---:|
| **0** | **7** |
| 4 | 14 |
| 5 | 9 |
| 6 | 7 |
| 7 | 6 |
| 8 / 9 | 1 / 2 |
| 12 | 4 |

**⇒ 37/50 个 run 无法事后判断自己的执行器增益、DR 状态、动作延迟、奖励截断或课程窗口**——
而这些量**全部**是 `os.environ.get(..., default)` 读的，所以"manifest 里没有"**不等于**"用的是默认值"。

**已经做对的部分**（这也是版本门禁能工作的原因）：`code_sha256_12`、`src_sha256`、
`robot_usd_sha256`、`import_contract_sha256`、`versions`、`init_checkpoint_sha256` 都记了 ✅。
**缺的只是运行时旋钮。**

**修法**：新增 `migration/linux/patch_manifest_effective_knobs.py`（未应用，已验证）——
在 manifest 里加一个 `effective` 块，**读模块级常量**而不是环境变量
（`mod4_task.LEG_KP/LEG_KD/REWARD_CLIP/TRACK_SIGMA/_ACTION_DELAY_SUBSTEPS/…`、
`skills_isaac.TUNNEL_PRECROUCH_LEAD_M/…`），全部用 `getattr(..., None)` 包裹，
**补丁前后都能跑、缺名字也绝不影响训练**。验证：`--check` 两锚点唯一 → 沙箱副本 `py_compile` 通过 →
真文件未动（`5489e8f3ef5f`）。

**顺带确认了一个高价值事实**：当前 fly run 的 manifest **确实记了** `RM_LEG_KP=2500`、
`RM_LEG_KD=10` —— 即**训练真的跑在 2500/10，而交付契约是 60/2.0（§11.2）**。

---

## 13. 飞坡为什么学不会：**判决指标要的是"先爬上发射台"，而我们的奖励在付"轮子离地"**

飞坡相位（400 迭代、`fly_jump` 采样权重 34.3%）结束后：专项评测 64 env
**complete 0.000**、`peak_rise 0.02 m`、`air_after 0.00`；训练里
`Metrics/route_air_launched_rate` **200 个采样只有 2 个非零（最大 0.0020）**，
而 `Episode_Reward/jump_air` 一直在付（末值 **0.8414**/回合）、`jump_push` 0.0037、`jump_climb` 0.0000。

### 13.1 判决指标的真实判据（交付包 `route_commands.py:78`）

`rc.launched` 来自**交付包**的 `RouteCommands`（`incoming/rmuc2026_field_20260911/rmuc2026_training/isaac/route_commands.py`），
不在我们仓库里 —— 这就是**奖励与指标能长期不一致而不报错**的原因：

```python
# line 78  —— launched 需要同时满足五项
self.launched |= fly & (u > -.8) & (u < .10) \
               & ((p[:,2] - self.base_height) > .10) \
               & wheel_grounded & (|p[:,1] - self.goals[ids,1]| < .40)
# line 79
self.air_after_launch |= fly & self.launched & ~wheel_grounded & (self.air_time > .04)
# line 87 —— fly 路线的"完成"必须先 launched
reached = torch.where(fly, reached & self.air_after_launch & wheel_grounded, reached)
```

**⇒ `launched` 是一个"站上发射台"的锁存量**，要求：
① 在 `u ∈ (−0.8, 0.10)` 这条**狭窄的 X 窗口**内；② 根部高度 **> base+0.10 m**（即**在坡上**，不能在低处沟底）；
③ **轮子着地**（这是发射**前**的条件）；④ 横向对齐 <0.40 m。

**⇒ 所以 `launched = 0` 的真正含义不是"没离地"，而是"从未到达发射区"。**
这与实测吻合：`fly_jump` progress 仅 3.9（专项 60.4），`peak_rise` 只有 **0.02 m** —— 根部**从没高出 base 10 cm**。

### 13.2 病因：奖励指向了错误的行为

| | 我们的奖励 | 交付指标 |
|---|---|---|
| 判据 | `st["air"] = air * frac`，`air = 连续 4 步无轮接触` | `launched` = **位置窗口 + 高度 + 着地 + 对齐** |
| 结果 | 0.84/回合（一直在付） | 2/200 采样非零（≈0） |

策略学会的是**在平坦地面卸载轮子**去收 `jump_air`（权重 1.5），
而不是**先爬上发射台**。奖励里**没有任何一项奖励"到达发射区"**——`jump_crouch/push/climb/air/land`
全都是**起跳之后**的项，起跳**之前**的接近段只有通用的 `route_progress`。
（代码里已有两次同类教训：`skills_isaac.py:1071` 记着 `frac = risen/target` 曾被刷；
`route_isaac.py` 的 `jump_in_place` 高度命令从 0.24 改回 0.34，因为"crouch 成了奖励最优"。）

### 13.3 可执行的修法（比"再训 400 迭代"便宜得多）

把交付包的 `launched` 条件**镜像成一个奖励项**（例如 `jump_launch_ready`）：
在 `u ∈ (−0.8, 0.10)`、`z > base+0.10`、`grounded`、横向对齐时付分，
并对 `st["air"]` 加上"必须先 `launch_ready`"的门控，与指标同源。

这样梯度就指向**真正的前置条件（爬上发射台）**，而策略在平地上刷 `jump_air` 的路径被切断。
**这不需要更多算力，只需要让奖励与判决指标对齐。**

**同时建议**：`Metrics/route_air_launched_rate` 与 `Episode_Reward/jump_air` 应当在
同一张图上对照监控——它们分属两个子系统（交付包的 `RouteCommands` vs 我们的 jump 状态机），
**不一致不会报错，只会让训练白跑**。

---

## 14. 过洞为什么 0.000：**判据可达，但机器人只走了 0.38 m 就没到洞口**

用和 §13 相同的方法查交付包的过洞判据（`route_commands.py:84`）：

```python
self.underpass_visited |= tunnel & (u > .78) & (u < 1.07) & (p[:,2] < .080) & (|dy| < .35)
```

其中 `p = root_pos_w - self.origins`（`:60`），所以 `p[:,2]` 是**根部相对场地原点的高度**。

### 14.1 判据是可达的（数值核算）

| 量 | 值 | 是否满足 `p[:,2] < 0.080` |
|---|---:|---|
| 沟底相对原点（`route spawn_ground_m[2]`） | −0.1558 m | — |
| **站立**时 `p[:,2]` = `base_height + trench_z` | **+0.1819** | ❌ 不满足 |
| **蹲姿**根部高度（实测 `probe_crouch_kp3`: `root_h=0.1799`） | 0.1799 m | — |
| **蹲姿**时 `p[:,2]` = `0.1799 − 0.1558` | **+0.0241** | ✅ **满足** |

⇒ **我们的蹲姿本身就满足判据**（`+0.0241 < 0.080`）。所以过洞**不是姿态不可达**。

### 14.2 真正的瓶颈：蹲姿前进距离

- u 窗口 `(0.78, 1.07)`；洞口 CAD 跨 `x = 0.751..1.101`；路线 `x: 0.3 → 2.3`
- ⇒ 从出生态到窗口起点需前进 **0.48 m**，窗口本身宽 0.29 m
- 实测蹲姿行进速度 **0.05–0.09 m/s** ⇒ 0.48 m 约需 **8 s**（episode 20 s，**够**）

而评测实测（fly 相位，8 env）：

```
underpass_seen = 0.0     roof_entries = 0     min_clearance_m = None
fail/tunnel_roof_hit = 0     progress_sum = 3.01（≈0.38 m/env）
```

⇒ **机器人只前进了约 0.38 m，没到 0.48 m 的洞口**；`roof_hit = 0` 也说明它**根本没碰到洞顶**，
即从未接近洞口。**病根是"蹲姿下无法持续前进"，不是蹲不下去。**

### 14.3 与已有证据一致，且 v2 的三项改动正好对症

- 代码注释（`skills_isaac.py` 与 `route_isaac.py`）已记录：蹲姿是一个**协调动作模式**，
  `sigma=0.28` 的关节噪声**几乎采样不到**；且蹲姿下只有 0.05–0.09 m/s。
- 交付路线 2 m 对 20 s episode 本就偏长（这正是 `RM_TUNNEL_GOAL_X` 与距离课程存在的原因）。
- **v2 对症的三项**：① `patch_crouch_pose_kernel.py`（高斯核，直接给"经过验证的蹲姿"付分）；
  ② `RM_CRANK_ACTION_SCALE=0.75`（让 crank 能到达蹲姿几何）；③ `run_tunnel_course.sh`
  的五阶段课程（`hold` 先稳蹲 → `crawl` 要求**净前进 0.08 m** → `approach` → `cross`）。

### 14.4 链结束后的决定性探针

`isaac/mod4/probe_tunnel_cross.py`（以及 `probe_tunnel_cross_pi.py`）就是为这一诊断写的——
应在链退出后跑一次，看那 0.48 m 是在哪一步停滞的（是速度上不去、还是被 `tunnel_stall` 或别的东西打断）。
**在拿到探针输出前，不应再假设过洞需要改几何。**

---

## 15. 过洞的定量根因：**"蹲着不动"是净正收益**（并修正 §4/§14 的一处我自己的建议）

### 15.1 失败形态（fly 相位 8 env 的完整字段）

```
fail/time_out = 6 / 8      fail/base_contact = 3 / 8      landed_rate = 1.0
underpass_seen = 0         entered = 0                    min_clearance_m = None
progress_sum = 3.01 (≈0.38 m/env)     roof_entries = 0     roof_hit_terminations = 0
```

⇒ **不是摔倒，是"稳稳蹲着直到超时"**（6/8 time_out，8/8 保持轮子着地，从没接近洞顶）。

### 15.2 为什么这是最优解：两步的收益算术

```python
# skills_isaac.py:818  tunnel_stall
return -0.5 * zone * (1 - clamp(|vx|/0.08, 0, 1))     # vx=0 → −0.5/步（weight 1.0）
# skills_isaac.py:150  tunnel_crouch_pose —— 只看关节角，完全不看是否前进
zone = ((st == 1) | (st == 2)).float()
return zone * (1 - (err/band).clamp(max=1.0))         # 蹲对姿势 → +1.0/步（weight 1.5）
```

| 场景 | crouch_pose | stall | **净** | 结论 |
|---|---:|---:|---:|---|
| **现状**（rmuc2026 块，weight 1.5） | +1.50 | −0.50 | **+1.00/步** | ❌ 原地不动**仍然赚钱** |
| 我的 `hold` 阶段（weight 2.0，**我自己的脚本**） | +2.00 | −0.50 | **+1.50/步** | ❌ **我把它变得更赚了** |
| 我的 `crawl` 阶段（weight 1.5，**我自己的脚本**） | +1.50 | −0.50 | **+1.00/步** | ❌ 同上 |

**代码注释自己就记着这个意图**（`:818`）：*"without this term 'hold the crouch and time out'
is a stable optimum"* —— 他们加了惩罚项，**但幅度不足以把符号翻过来**。

**⇒ 这就是过洞 0.000 的定量根因**，而且**复旦包的 `tunnel_crawl` 阶段警告的正是这件事**：
*"保持低姿态并净前进至少 0.08 m，**不能原地刷 crouch 奖励**"*。

### 15.3 ⚠️ 对我自己建议的修正（重要）

我在 §4.2/§9.1 推荐了 `patch_crouch_pose_kernel.py`（把 crouch 奖励换成高斯核，"更平滑、处处非零"）。
**如果不同时解决上面这个符号问题，那个补丁会让过洞更糟**——一个更宽更高斯的核只会让"原地蹲着"
更赚钱。**必须先让 `crouch_pose_w < stall 惩罚`（gain=0.5 时即 < 0.5），或者提高 stall 的 gain/weight**，
平滑核才有意义。这条已写进 §9.1 的应用顺序注意事项。

### 15.4 已做的修正：`run_tunnel_course.sh`

`crawl` 及之后的阶段把 `RM_CROUCH_POSE_W` 全部压到 **0.5 以下**，使"原地不动"净负：

| 阶段 | crouch_pose_w | vx=0 时的净收益 |
|---|---:|---:|
| `hold`（**故意**保留 +1.00，只用于发现蹲姿，12 s 短 episode） | 1.5 | +1.00 |
| `crawl` | **0.30** | **−0.20** ✅ |
| `approach` | **0.20** | **−0.30** ✅ |
| `cross` | **0.15** | **−0.35** ✅ |
| `recover` | **0.10** | **−0.40** ✅ |

⚠️ **`hold` 是刻意的例外**（那一步就是要"学会蹲住"），所以它**必须短**、而且**不能作为常驻训练配置**——
否则它教的就是我们正在修的坏习惯。

### 15.5 待办（链结束后）

1. 加一个 `RM_TUNNEL_STALL_GAIN` 旋钮（现在 `gain=0.5` 是函数默认参数，**无法从环境变量调**），
   这样"让原地不动净负"就不必靠压低 crouch 权重来实现；
2. 在 `crawl` 及之后把 crouch_pose 改成一**次性**奖励（姿势保持 ≥1 s 才付一次），
   从根上消除 dense farming；
3. 跑 `probe_tunnel_cross.py` 验证：修正权重后，0.38 m → 能否突破 0.48 m。

---

## 16. 奖励路径的交互验证（第 64 轮，两处确认无遗漏）

补丁越堆越多，必须确认它们**互不遗漏**。这一轮查了两处：

**① `patch_reward_clip_and_sigma` 会漏掉后加的奖励项吗？不会。**
它的 `__post_init__` 用 `for _name in sorted(vars(self))` 遍历**运行时实例属性**，
而不是硬编码字段清单 ⇒ 由 `patch_jump_launch_ready` 后加的 `jump_launch_ready` 字段
**自动被纳入**（权重 2.0 ≤ C=2.5，且原值 ≤1 ⇒ `raw*weight ≤ 2.0 < 2.5` ⇒ **永不饱和**）。
`tunnel_crouch_pose`（权重默认 1.0）同理。

**② 自己修复的覆盖率也必须量化——第 63 轮的教训。**
`patch_manifest_effective_knobs` 第一版用手工常量清单，实测只覆盖
**14 / 80** 个 `RM_*` 旋钮（**17.5%**）。这与复旦"13/47 个 run 静默用 140 维 critic"是同一类病：
**手工维护的清单必然漂移**。四轮迭代后（手工清单 → 正则 → 限定 4 文件扫描 → **纯字符串 + 扫全目录**）
达到 **80/80 = 100%**。

**⇒ 可复用的检查方法**：每当新增一个"记录/校验"类补丁，都要**量化它的覆盖率**
（这里就是"代码读了 N 个旋钮，你记了几个"），否则它会给人虚假的安全感——
比没有它更糟。

---

## 17. ⚠️ 方法论：**用和实现相同的方法去验证实现，只能证明自洽，永远无法证明正确**

第 64 轮我宣称 `patch_manifest_effective_knobs` 覆盖率 **100%（80/80）**。**那句话是错的**，
而错的原因比结果本身更重要：

我用 `os.environ.get("RM_...` 这个模式去**枚举**"代码读了哪些旋钮"，
又用**同一个模式**去写**记录器**。两者当然一致——**它们同盲**。

换成**独立的方法**（枚举代码里所有带引号的 `RM_*` 字面量）后：

| | 数量 |
|---|---:|
| 代码中以字面量出现的 `RM_*` 旋钮 | **112** |
| 经 `os.environ.get(` 直接读取 | 80 |
| **经助手函数读取**（`_f("RM_X", d)` 之类） | **32** |
| 我的记录器实际覆盖 | 80 → **71%**（不是 100%） |

而那 32 个**恰好是 v2 补丁引入的旋钮**：
`RM_ACTION_DELAY_MS_MIN/MAX`（item 2 的动作延迟）、`RM_CURR_*`（9 个，item 4 的课程阈值）、
`RM_EFFORT_*`（6 个，DR 的力矩范围，`RM_EFFORT_LEG_MIN=0.90` 正是 `patch_dr_defaults` 改的那个）、
`RM_OBS_DELAY_*`、`RM_CMD_*`、`RM_HEIGHT_*`。

**⇒ 最需要被记录的旋钮，恰是记录器看不见的那些。**

**修法**：记录器改为匹配行内**任意带引号的 `RM_` 字面量**（不再假设读取方式），
`start_v2_chain.sh` 的自检同理（它原来也会把 `RM_ACTION_DELAY_MS_*` 误判为"拼写错误"）。
修好后：记录 **117 / 字面量 113 ⇒ 100%**，且
`RM_ACTION_DELAY_MS_MIN→0.0`、`RM_CURR_PROMOTE→0.7`、`RM_EFFORT_LEG_MIN→0.90`、`RM_OBS_DELAY_MAX_LAG→2`
全部进来了。

**可复用的规则**：
> **验证器与实现不能共用同一个提取模式。** 如果两者用同一个假设去"看待"代码，
> 那个假设错了，验证器只会**确认它是对的**。
> 本会话里同一类问题已出现多次（版本门禁硬编码资产路径、`RATE_KEYS` 未定义、`rm_forward` 不闭合约束、
> `RM_TUNNEL_LEAD_M` 双重语义）——**共同点都是"检查器和被检查者共享了同一个错误假设"**。

---

## 18. 把 §17 的"独立方法"原则用于我自己的验证（两处独立核查）

### 18.1 组合测试的文件覆盖（独立提取，不靠测试自身）

用脚本从 13 个补丁里**独立提取**它们引用的路径，再与我的组合测试沙箱比对：

```
13 个补丁共引用 9 个不同路径 → 沙箱缺失 0 个
实际被改动: mod4_task / route_isaac / skills_isaac / train_mod4_ppo /
            final_acceptance_mod4.sh / run_special_phases_v3.sh /
            start_mod4_stage_fixedplant.sh / onnx_play.py （8 个）
未改动: mod4_curriculum.py（patch_route_curriculum 只把它作为前置条件检查，不修改 ✅）
```

⇒ **组合测试确实覆盖了补丁会碰的每一个文件**（若漏一个，测试会静默地没测到它）。

### 18.2 链的判决函数读的字段名是否真实存在（独立比对 JSON 键集）

判决逻辑用的是**计数**字段再除以 envs，而不是 `*_rate`：

```python
rate(b, "underpass_seen")       # JSON 有（计数）✅
rate(b, "air_after_launch")     # JSON 有（计数）✅ —— 注意不是 `air_after`
b["complete_rate"]              # 直接索引：缺了会 KeyError，不会静默 ✅
```

与 `eval.json` 的真实键集逐项比对：**全部有效，无静默 0** ✅。
（若是 `b.get("air_after", 0.0)` 就会永远是 0——这正是 §17 要防的那类错。）

**唯一瑕疵（仅日志可读性）**：判决日志打印 `air_after=%.2f`，但实际读的是 `air_after_launch`。
**命名不一致容易误导后来人**，建议日志标签与字段名统一（一行改动，未动）。

**⇒ 第 66 轮结论**：这两处都是**干净的确认**，没有发现新缺陷。
但方法本身值得保留：**每当我用某个工具验证某样东西，就问一次"这个工具的提取方式，
和被验证对象的实现方式，是不是同一个假设？"**

---

## 19. ⚠️ 过洞的**第二个**缺陷：交付路线在 episode 预算内跑不完（与策略无关）

第 72 轮核查时发现，而且它把 §14/§15 的结论**精确化**了：

```
交付的过洞路线长度        : 2.00 m（waypoints (0.3,-5.95,-0.16) → (2.3,-5.95,-0.16)）
实测蹲姿行进速度          : 0.05-0.09 m/s（docs/probe_crouch_drive.py）
⇒ 跑完需要                : 22.2 - 40.0 s
链实际用的 episode        : **20.0 s**（RM_EPISODE_S 默认值，从未被设置过）
评测实际用的 rollout      : **22 s**（--steps 2200 @100 Hz）
```

**证据（`RM_EPISODE_S` 从未设置）**：
- `migration/linux/tunnel_tuning.env` 与所有 `migration/linux/*.sh` 都**不含** `RM_EPISODE_S`
- fly run 的 `run_manifest.env` 12 个键里**没有** `RM_EPISODE_S` ⇒ 用的是默认 `20.0`
- 代码注释（`mod4_task.py:1710`）**自己就指出**"蹲姿机器人很慢（~0.06 m/s）"，并把它做成可配——
  **但没人配**

**必须精确区分两件事**（这是本节最重要的部分）：

| 现象 | 需要走多远 | 可用时间 | 结论 |
|---|---:|---:|---|
| **`underpass_seen = 0`**（判据是 u>0.78，即从 0.30 起 **0.48 m**） | 0.48 m | 5–10 s（20 s 内**够**） | ❌ **不是**预算问题 ⇒ 仍是 §14/§15 的**蹲姿行进**问题 |
| **`complete_rate = 0`**（要跑完 2.00 m） | 2.00 m | 需 22–40 s，只有 20 s | ✅ **构造上不可能** ⇒ 与策略无关的**独立缺陷** |

⇒ 所以过洞有**两个**独立缺陷，修一个不够：**① 蹲着不动是净正收益（§15）② 完整路线跑不完（本节）**。

**已做的修正**：`run_tunnel_course.sh` 的评测步数从固定 `2200` 改为 `$((EPS * 100))`——
**用该阶段自己的 episode 长度评分**（原来用 22 s 的 rollout 去评一个 50 s 的阶段，是另一种"让门禁不可能通过"）。

### 19.1 推广到全部路线：谁还有"构造上跑不完"的风险

把全部 10 种路线的长度除以 20 s 训练预算（评测是 22 s），得到"需要的平均速度"：

| 路线 | 长度 | 20 s 内跑完需 ≥ | 实测能力 | 判定 |
|---|---:|---:|---|---|
| **fly_jump** | **5.80 m** | **0.29 m/s** | 平地上可达，但要**带着爬坡** | 最苛刻但不是不可能 |
| run | 3.50 m | 0.17 m/s | ✅ 已在过门（1.000/0.600） | 可达 |
| rough_cross | 3.30 m | 0.17 m/s | ❌ 0.000 | 需探针确认（搓板路） |
| ramp_up / ramp_down | 2.11 m | 0.11 m/s | ✅ 0.556 / 1.000 | 可达 |
| **tunnel_cross** | **2.00 m** | **0.10 m/s** | **蹲姿 0.05–0.09** | **❌ 构造上不可能** |
| step_up / step_down | 1.30 m | 0.07 m/s | ✅ 0.250 / 1.000 | 可达 |
| jump_in_place / slope_spin | 0（原地） | — | ✅ spin 0.703 | 判据是转角，与距离无关 |

**⇒ 两条路线需要单独审视**：
- **`tunnel_cross`**：需要的 0.10 m/s **高于**实测蹲姿上限 0.09 m/s ⇒ 2.00 m 在 20 s 内**永远跑不完**（§19）。
- **`fly_jump`**：5.80 m / 0.29 m/s 是全部路线里最苛刻的，**它同时还要爬坡到发射台**（§13）。
  这解释了为什么飞坡"连发射台都上不去"——**先要满足一个 5.80 m 的位移预算**。

**这张表也说明**：`slope_spin` 之所以是小陀螺里唯一过门的，部分原因是**它的判据是转角而不是位移**——
对轮腿来说，"原地转 2π"比"按平均速度跑完 N 米"宽松得多。**判据形式本身会决定科目难度**，
这一点在后续设计任何新科目时都值得先算一遍。

**起 v2 前要决定**：混合相位的 `RM_EPISODE_S` 是否从 20 提到 ≥45（代价：所有科目的 episode 预算都变长，
会改变 jump/ramp 等科目的训练动力学），还是**只把过洞交给五阶段课程**（每个阶段自带合适的 episode）。
**建议后者**——课程脚本已经为每阶段配好 12/20/30/50/50 s，且五阶段的目标按实测速度都可达。

---

## 20. 失败科目的完整定性（第 74 轮收口）

§19.1 里唯一"需探针确认"的 `rough_cross`，答案来自本次链**唯一救回的那份专项评测**
（`docs/acceptance_phase_v3_terrain/eval_focus_rough_cross.json`，64 env × 2200 步）：

```
attempted_rate = 1.0            64/64 都在尝试前进
每 env 平均推进 3.81 m          而路线只有 3.30 m
complete_rate = 0.000
fail/base_contact = 385         ⇒ 每 env 摔 6.02 次
fail/time_out = 9
```

⇒ **`rough_cross` 不是距离预算问题**（走的总距离超过路线长度），
而是**稳定性问题**：能穿过搓板路，但**一路撞底**（`base_contact` 终止）——所以**一次干净通过都没有**。
（这份报告同时保留了**修复前的哨兵值** `min_clearance_m = 999.0`，
正是我后来修掉的那个 bug 的现场 ✅。）

### 20.1 五个失败科目的最终定性表

| 科目 | 实测 | 病灶（定量） | 类别 |
|---|---|---|---|
| **slope_spin** | ✅ **0.703 / 1973.7°** | 判据是**转角**不是位移 | 已过门 |
| **step_up** | 0.250（在升） | 探索难度 | 训练 |
| **fly_jump** | 0.000，`peak_rise` 0.02 m | ① 奖励与判决指标**不同源**（§13）② **5.80 m** 位移预算（§19.1） | **奖励设计** + 预算 |
| **tunnel_cross** | 0.000，6/8 `time_out` | ① 蹲着不动**净 +1.00/步**（§15）② **2.00 m** 在 20 s 内超出蹲姿速度（§19） | **奖励设计** + 预算 |
| **rough_cross** | 0.000 | **稳定性**：每 env 摔 6.02 次 `base_contact`（**与预算无关**） | **控制/速度上限** |

**⇒ 三个失败科目分属三类不同的病**，这就是为什么"再多训一会儿"对它们都不管用：
- 两个是**奖励指向了错误的行为**（可改奖励，不需要更多算力）
- 一个是**预算/阈值设定本身不可达**（要改 episode 或判据）
- 一个是**稳定性**（要降速或改姿态）

**方法论**：任何一个科目拿到 0.000，先按这三类各查一遍——
**① 奖励与判决指标是否同源？② 判据在时间/距离上是否可达？③ 是摔了还是没动？**
三个问题分别对应 `jump_air vs launched`、`2.00 m / 20 s`、`fail/base_contact` 这三处证据。

---

## 21. `rough_cross` 的具体成因：一个"设计性捆绑错误"，而第 4 项的课程正好是解药

### 21.1 证据

```python
# route_isaac.py:83 —— 旋钮自己的注释就写着它是"命令范围课程"
rough_cap = float(os.environ.get("RM_ROUGH_SPEED_MAX", "0") or 0.0)
if rough_cap > 0.0:
    for i, route in enumerate(rc.routes):
        if route["kind"] == "rough_cross":
            rc.speeds[i, 1] = min(float(rc.speeds[i, 1]), rough_cap)
```

- `rough_cross` 的 `speed_range_m_s = **[0.3, 2.0]**` —— 在 **±35 mm、最大约 10° 的搓板路**上
- `RM_ROUGH_SPEED_MAX` 默认 **0 ⇒ 不限速**
- **51 个 run 的 manifest 里只有 1 个记录了它** ⇒ 50/51 都是不限速训练的
- 链脚本甚至**显式 unset** 它（`:295`）

### 21.2 为什么这是设计错误：限速被和"路线长度"捆在了一起

链脚本的注释原文：

> *"Delivered route lengths in training as well: no shortened goal, no extra spawn lead.
> `RM_TUNNEL_GOAL_X` / `RM_TUNNEL_SPAWN_DIST` / `RM_ROUGH_SPEED_MAX` stay unset:
> the goal distance and the spawn must stay the delivered ones (goal 2 forbids a shortened course
> as 'proof')."*

这条论证对**路线长度**成立（不能用缩短的路线冒充通过），但**对命令范围不成立**：
限速**不缩短路线**——机器人仍要跑完 3.30 m，只是被要求**先把可生存的速度学好**。
而且这个旋钮的源码注释（`route_isaac.py:81-82`）明确写着它的用途是
*"caps that route's sampled speed so the traversing skill can be learned before speed"*。

**⇒ 把课程旋钮和完整性旋钮一起 unset，是这次失败的直接原因。**

### 21.3 解药就是我们为清单第 4 项做的课程（免费）

`isaac/mod4/mod4_curriculum.py`（第 4 项，路径 B）发布的 `_mod4_route_speed_scale` 表
**已经按路线把命令速度乘一个等级比例**，等级 0 的 `speed_scale = 0.60`：

```
rough_cross 等级 0 生效速度上限 = 0.60 × 2.0 = 1.20 m/s（比不限速的 2.0 低 40%）
```

而 `patch_route_curriculum.py` 的消费端正是
`cmd = cmd * torch.tensor(_tbl)[_ids]`（`route_isaac.py`）——**与 `RM_ROUGH_SPEED_MAX` 想做的是同一件事**，
但它是**近似自动的**（成功率窗口驱动的等级状态机），而且**不碰任何路线长度**。

**⇒ 启用 `RM_ROUTE_CURRICULUM=1`（`start_v2_chain.sh` 已默认开启）同时解决了两件事**：
清单第 4 项的难度课程，**以及** `rough_cross` 的速度课程。
这是本次会话里少见的"一个改动同时结清两个问题"。

### 21.4 三个失败科目 → 三类病的最终对照

| 科目 | 类别 | v2 是否已覆盖 |
|---|---|---|
| `fly_jump` | 奖励与判决指标不同源 | ✅ `patch_jump_launch_ready` |
| `tunnel_cross` | 蹲着不动净正收益（+ 预算） | ✅ `patch_tunnel_crouch_gate`（+ 课程脚本自带 episode） |
| `rough_cross` | 命令范围过宽 ⇒ 稳定性 | ✅ **`RM_ROUTE_CURRICULUM=1`**（等级 0 即 0.60× ） |

---

## 22. 课程的窗口尺寸与相位长度不匹配（会让 v2 的课程"几乎不生效"）

第 77 轮核算：

```
--steps_per_env 默认 = 24        ⇒ 1 迭代 = 24 控制步
1 个相位 = 400 迭代              = 9,600 控制步
RM_CURR_WINDOW_STEPS 默认 = 4000 ⇒ 每相位只关 2.4 个窗口
```

而等级从 4 降到 0（`speed_scale` 1.00 → 0.60）需要 **4 次降级**，
⇒ **默认窗口下一个相位最多移动 2 级**，`rough_cross` 永远到不了 0.60×
（要 4 次降级 = 1600 迭代 = **4 个相位**）。

**⇒ 修正**：`start_v2_chain.sh` 显式设 `RM_CURR_WINDOW_STEPS=1000`
（≈42 迭代/窗口 ⇒ 每相位 ~9 个窗口 ⇒ 缓和可在**同一相位内**完成）。

| 窗口 | 每相位窗口数 | 最多移动级数 | 判定 |
|---:|---:|---:|---|
| 4000（默认） | 2.4 | 2 | ❌ 到不了 0.60× |
| **1000（v2）** | **9.6** | **9** | ✅ 足够 |
| 600 | 16 | 16 | ✅ 更快但样本更少（`MIN_ATTEMPTS=40` 仍满足） |

**这类"参数与预算不匹配"的问题在本次会话里出现了三次**（§19 episode 预算、§19.1 路线长度、
本节课程窗口）——**共同点：默认值当初是按某个语境选的，换到新语境就静默失效**。
**检查方法**：把默认值换算成"在一次相位/一集里会发生几次"，再问"够不够触发它的机制"。

---

## 23. 第 4 项与第 6 项的**耦合**：课程要生效必须同时满足两个条件

§22 把窗口从 4000 调到 1000 后，出现第二个约束：窗口越短，**每窗口的样本越少**，
而 `RM_CURR_MIN_ATTEMPTS = 40` 会拒绝决策。核算（按链的实际采样配比 + `RM_EPISODE_S=20`）：

| envs | 窗口 | 低配额科目（rough/step/tunnel）每窗口 attempts | 每相位窗口数 | 判定 |
|---:|---:|---:|---:|---|
| 512 | 4000 | ~98 ✅ | **2.4** | ❌ 等级最多移动 2 级 |
| 512 | **1000** | **~24 ❌**（<40） | 9.6 | ❌ **样本门槛卡死** |
| **1024** | **1000** | **~49 ✅** | **9.6** | ✅ **两个条件同时满足** |
| 1024 | 4000 | ~195 ✅ | 2.4 | ❌ 等级移动不够 |

**⇒ 清单第 4 项（课程）依赖第 6 项（1024 env）**：两者单独任一个都会让课程**静默不生效**。
`start_v2_chain.sh` 已把 `ENVS=1024` 与 `RM_CURR_WINDOW_STEPS=1000` 配成一对并注明理由。

**诊断量（已存在，无需改代码）**：课程每窗口发布
`Curriculum/route_curriculum/attempts_<kind>` 与 `level_<kind>`。
**若 `attempts_<kind>` 长期 < 40 而 `level_<kind>` 不变，就是被样本门槛卡住了**——
此时应当**降低 `RM_CURR_MIN_ATTEMPTS`**，而不是"再多等等"。

⚠️ 注意：`attempts_*` 只在 `att > 0` 时发布，所以"键缺失"意味着该窗口该类**零尝试**
（比样本不足更严重，通常说明该类没被采样到）。

---

## 24. rollout 工装的实测状态（第 87–88 轮）：跑通了，但**还不能判定**

新增 `sim2sim_mod4/rollout_mod4.py`：加载 MJCF、**按契约的 `obs_layout` 组装 35 维观测**、
100 Hz 跑 ONNX、用契约 PD 律（kp/kd/scale/effort 钳位）经 `qfrc_applied` 驱动 6 个电机
（MJCF `nu=0`，闭环由 `neq=6` 的 `<connect>` 约束完成），输出物理量。

### 24.1 对照实验逼出了**两个我自己的 bug**（这是本轮最有价值的部分）

用**零动作策略**（纯 PD 保持默认姿态）作对照——**一个已知答案的输入**：

| 版本 | 结果 | 诊断 |
|---|---|---|
| 加载 `rm_vehicle.xml`（只有机器人） | `tilt=0.6°`、`vx=0.000`、`h: 0.2986 → −10.73` | **竖直自由落体** ⇒ 该文件**没有地面**（地面在 `scene.xml` 里，它 `<include>` 机器人）⇒ 已修 |
| 基座放在契约的 `root_height=0.2989` | tilt 107° | **参考系错**：§5.11 实测 MJCF 的 `base_link` 在**轮轴高度**，与车体原点差 **Δz = −0.2706 m** ⇒ 已加 `--base-z-offset`（默认 −0.2706） |
| 修正后仍 tilt 152° | 倒下 | **`qpos0` 是折叠姿态**：§5.8 实测全零时**轮心与基座同高**（0.0751 vs 0.0750），保持它不等于"站住" |

**若我只跑真实策略看到 `DIVERGED`，我会误判为"策略不能迁移"——而实际是我的工装有两处错。**
这就是"跑一个已知答案的对照"的价值。

### 24.2 剩余阻塞：**MJCF 的站立姿态**（唯一未解的一项）

`qpos0` 是折叠的；而 `mj_step`（约束已求解）采样显示**存在大幅伸展的构型**
（如 `(rear1, front1) = (0.0, 0.6)` → 轮心到 `[−0.2264, −0.0318]`，即向前下方伸出 22.6 cm）✅
⇒ 站立姿态**存在**，只是需要**解**出来：找 `(rear1, front1)` 使轮心位于基座正下方约 0.27 m。

**工具已经具备**：`sim2sim_mod4/fit_joint_map.py` 里的 **`mj_step` 采样**（含约束求解）
就是为此写的（§5.12 修掉了 `mj_forward` 不闭合约束的假象）。
**下一步**：用它做一次二维求解（目标 = 轮心相对基座的 `(x≈0, z≈−0.27)`），
得到站立姿态后再用零动作对照验证"能站住"——**那时 rollout 的判决才有意义**。

### 24.3 诚实的状态声明

`rollout_mod4.py` **端到端可运行**，但**尚未产生有意义的判决**。
**不要把它当作"sim2sim rollout 门禁已通过"。** 目前它验证的是：
契约布局可驱动观测组装 ✅、ONNX 可在 MuJoCo 侧调用 ✅、控制律与 `qfrc` 路径可用 ✅、
以及**对照实验能定位工装自身的错误** ✅。

⚠️ 另注：`--mapping {front1_is_hip,rear1_is_hip}` 两种假设**都发散且结果相近**
⇒ **mapping 不是当前发散的原因**，不要靠试 mapping 来"修"它。

---

## 25. rollout 工装：三次对照实验 → **三个不成立的假设**（收敛结论）

§24 记录了前两个。本轮补上第三个，并给出**收敛的判断**。

| # | 我的假设 | 对照实验结果 | 修正 |
|---|---|---|---|
| 1 | 加载 `rm_vehicle.xml` 即含有地面 | 零动作下 `tilt=0.6°`、`vx=0.000` 却 `h→−10.7` ⇒ **竖直自由落体** | 改加载 `scene.xml`（`<include>` 机器人 + 地面）✅ |
| 2 | 基座可放在契约的 `root_height=0.2989` | tilt 107° | 加 `--base-z-offset`（MJCF 的 `base_link` 在**轮轴高度**，Δz=−0.2706，§5.11） |
| 3 | 左右腿可用**同一组**关节值（或取负镜像） | 同值：左轮 z=0.1095 / 右轮 z=0.0855（**差 2.4 cm**）；取负值：完全不对称 | ❌ **两腿需独立姿态**，简单镜像不成立 |

**并且已排除的两个嫌疑**（都做过实验）：
- **增益缺口**（§11.2）：扫 `kp = 60 / 200 / 600 / 2500`，**全部倒下**（tilt 91–178°）⇒ 不是增益问题
- **mapping 选择**：`front1_is_hip` 与 `rear1_is_hip` 结果相近且都倒 ⇒ 不是 mapping 选择问题

**站立姿态本身是解出来的、不是猜的**：用 `mj_step` 采样（约束已求解）求解，
`(rear1, front1) = (0.20, 1.00)` 使轮心落在基座正下方 **0.2696 m**，残差 **0.0004 m**，
且次优解差 0.065 m（**明确分离**，非退化拟合）。

### 25.1 收敛的结论

三次对照实验，**三次都是我的工装假设不成立**——这个比例本身就是结论：

> **我们现有的两个 MJCF 不是这条策略的即插即用植物。**
> §5.9/5.10 已经证明它们是**同拓扑、不同参数化**的五连杆（连杆长度吻合 1.7–4%）；
> 现在进一步表明：连**左右腿的对称性约定**都和策略侧不同。

⇒ item 5 的 rollout 半边**必须**先完成那个映射（2→2 关节映射 + 雅可比），
`rollout_mod4.py` 是**应用该映射的正确位置**（它已经跑通了契约布局→观测→ONNX→PD→`qfrc`→物理这条链路）。
**在此之前不要期待 rollout 给出 PASS。**

**下一步的具体形状**（已具备全部输入）：
1. 用 `scene.xml` + `mj_step` 采样，把**左腿和右腿分别**解出站立姿态（不再假设镜像）；
2. 用复旦部署仓库的 `solveLegGeometry(phi1, phi4)`（§11.1 的解析解）+ §5.11 的 Δz，
   建立"策略关节 ↔ MJCF 关节"的 2→2 映射；
3. 回到 `rollout_mod4.py` 做零动作对照 —— **能站住之后，真实策略的判决才有意义**。

---

## 26. 对 §25 的修正：我那套"无重力运动学求解"**本身不可靠**

按 §25 的步骤 ① 分别解左右腿时暴露：

```
保持左腿 (0.20, 1.00)，扫右腿：
  最优 (rear1=0.30, front1=1.05) → 右轮 (x=+0.0149, z=-0.2388)  误差 0.0342 m
  ⚠️ 并伴随数值不稳定: "Nan, Inf or huge value in QACC at DOF 23"
```

而左腿同样的解法残差只有 **0.0004 m**。**右腿差了 85 倍，且求解本身不稳定。**

**根因**：我的 `settle()` 是「**重力关掉 + 只按住 2 个主动关节**」。
在这种设置下**被动关节没有回复力**，其最终值只取决于初始状态与数值漂移。
⇒ §25 里"同值 z 差 2.4 cm / 取负值更差"的**不对称结论很可能是这个方法造成的假象**，
**不能据此断言"MJCF 的左右腿参数化不同"**。这条修正必须显式记下（否则后人会照着一个假结论去做）。

**正确做法**（下一步应采用的）：**开着重力、在 PD 律下让物理自己收敛**——
即 `rollout_mod4.py` 已经在做的事，只是它需要一个**足够好的初值**才不会一开始就倒。
换句话说：**这个问题不该用"运动学求解"绕过，而应当用"物理收敛"验证**；
运动学求解只适合给出**初值候选**，且必须**左右腿同时解、并检查被动关节是否收敛**
（例如比较两次不同初值的解是否一致——不一致就说明未收敛）。

**第 90 轮的净结论**：§25 的"两腿参数化不同"**降级为未证实的怀疑**；
真正确定的是——**运动学求解方法本身需要先修正**，而在此之前
`rollout_mod4.py` 的 `DIVERGED` **既不能归因于策略、也不能归因于 MJCF 的对称性**。

---

## 27. ⚠️ 重要自我纠正：§24 报的"站立姿态残差 0.4 mm"是**无效的**（方法不收敛）

第 91 轮做了 §26 要求的**收敛性检验**——同一组主动关节值、**三组差异极大的被动关节初值**：

```
A) 被动初值 = qpos0        左轮 [ 0.1092, -0.2661,  0.1688]
B) 被动初值 = 随机 ±1.0 rad 左轮 [ 0.0043, -0.1992,  0.5309]   ← 天差地别
C) 被动初值 = 全部 +0.8 rad 左轮 [ 0.1148, -0.2662,  0.1649]

左轮在不同初值下的最大差异 = 0.3828 m   ⇒ ❌ **未收敛**
（另有数值不稳定警告：QACC at DOF 2）
```

**⇒ 结论：`重力关 + 只按住 2 个主动关节 + mj_step` 这套求解不收敛，结果取决于初值。**

**因此必须显式作废以下数字**（它们只是"以 `qpos0` 为被动初值"的产物）：

| 作废项 | 原报数字 | 状态 |
|---|---|---|
| §24 的站立姿态 `(rear1, front1) = (0.20, 1.00)` | 残差 0.0004 m、"次优解差 0.065 m" | ❌ **无效** |
| §25 的"左右腿不对称（z 差 2.4 cm）" | — | ❌ **无效**（同源方法） |
| §25 的"右腿最优 3.4 cm" | — | ❌ **无效** |
| §5.8 / §5.11 里用同样方法得到的"相关系数 +0.000 / 边界钉住 100%" | — | ⚠️ **已在 §5.12 由 mj_step 修正过一次，但当时没做收敛性检验** ⇒ 其可信度同样**未经证明** |

### 27.1 正确的方法（本节的可复用结论）

**判断一个数值解能不能用，先做收敛性检验**：换一组**差异很大**的初值再解一次，
结果不一致就说明**方法本身无效**，后面所有数字都不必谈。

而这条正好是本会话反复出现的同一主题的**最纯粹形态**：
- §17：验证器与实现共用同一个提取模式 ⇒ 只能自证
- §26/§27：求解器没有收敛性检验 ⇒ **输出看起来精确（0.4 mm！）却毫无意义**

> **"残差很小"不等于"解是对的"**——残差小只说明它满足了我写的那个目标函数，
> 而目标函数是基于**未收敛的中间量**算出来的。

**正确做法**：运动学求解要么用**解析解**（复旦部署仓库的 `solveLegGeometry`，§11.1 已提取，
它不依赖初值 ✅），要么用**物理收敛**（开重力 + PD + 接触，即 rollout 已在做的），
并且**每次都要做收敛性/一致性检验**。

---

## 28. item 5 rollout 半边的**最终状态**：缺失映射已被三重证据确认

第 92 轮按 §27 的建议改用**物理收敛搜索**（开重力 + PD + 接触，不依赖任何运动学求解）：

```
16 组候选姿态 × 2 个基座高度，零动作（纯 PD 保持该姿态）：
  最好的也只是 tilt≈20-22° 的缓慢倾倒，其余 37-180°
  ⇒ 全部 DIVERGED，无一站住
```

结合此前的排除实验：

| 实验 | 变量 | 结果 |
|---|---|---|
| 增益扫描 | `kp = 60 / 200 / 600 / 2500` | 全部倒 ⇒ **不是增益** |
| mapping 选择 | `front1_is_hip` / `rear1_is_hip` | 都倒且相近 ⇒ **不是这个二选一** |
| 姿态搜索 | 16 组 `(rear1, front1)` | 全部倒 ⇒ **不是初始姿态没选好** |
| 基座高度 | 0.30 / 0.3321 | 都倒 ⇒ **不是高度** |
| 加载文件 | robot vs scene | 这个是**真 bug**（无地面 ⇒ 自由落体）✅ 已修 |

### 28.1 一致的唯一解释

**用策略的动作语义去驱动 MJCF 的关节，本身就是错的。**
策略在 Isaac 里学的是**植物**的动作语义（`left_crank` / `left_hip`，两轴相距 17.5 mm），
而 MJCF 的两个驱动关节是**同轴**的（§5.9–5.10 实测：锚点完全相同、间距 0.00000 m；
连杆长度吻合 1.7–4%）。两者是**同拓扑、不同参数化**的五连杆。

⇒ **无论怎么调姿态/增益/高度，都不可能"站住"**，因为送进去的动作含义就是错的。
这与 §5.9/5.10/5.12 的预测完全一致，**现在由 16 组物理实验独立确认**。

### 28.2 本轮真正留下来的东西（可复用）

1. **`rollout_mod4.py`**：端到端可运行的 rollout 工装（契约布局 → 35 维观测 → ONNX → 契约 PD 律
   → `qfrc_applied`（`nu=0`）→ 物理），带 `--mapping / --stand-pose / --base-z / --leg-kp / --contract / --mjcf` 开关。
   **它是应用映射的正确位置**——映射一旦定下来，这里立刻能出判决。
2. **一套"对照实验"的方法**：用**已知答案的输入**（零动作）去检验工装。
   本轮靠它逼出了**加载错文件**这个真 bug，也靠它排除了增益/姿态/高度/mapping 四个嫌疑。
3. **一条作废清单**（§27）：把基于不收敛方法得到的数字逐项标记为无效，避免后人继承。

### 28.3 明确的状态声明（供验收使用）

> **item 5 的"产物半边"= PASS（`check_sim2sim_mod4.py` rc=0）。**
> **item 5 的"行为半边"= 未完成**，且**其完成的前提是 2→2 关节映射**（§5.9/5.10/5.12/28 一致）。
> `rollout_mod4.py` 现在**不能**作为交付门禁——它会把"映射缺失"表现为 `DIVERGED`。

---

## 29. 🚨 第一份 DR-on 数据：**两个已过门科目在 DR 下都掉到 bar 以下**

> **背景**：至今**所有**训练与评测的 DR 都是关的（`RM_DR_OFF=1`，51 个 run 的 manifest 一致如此）。
> 也就是说 **"DR 打开后会怎样"这个问题从未被测量过**。清单第 2 项恰恰要求"DR 提前并默认开"。

正式验收 `baseline_16295`（checkpoint `model_16295.pt`）的 **nominal（DR OFF）** 与 **首个 DR 种子**：

| 路线 | DR OFF | DR ON (seed 0) | Δ | bar |
|---|---:|---:|---:|---:|
| **step_up** | 0.750 | **0.000** | **−0.750** | 0.60 ⇒ **崩塌** |
| **slope_spin** | 0.750 | **0.500** | −0.250 | 0.60 ⇒ **掉出** |
| ramp_down | 1.000 | 1.000 | 0.000 | 0.60 ✅ 守住 |
| step_down | 1.000 | 1.000 | 0.000 | 0.60 ✅ 守住 |
| ramp_up | 0.333 | 0.222 | −0.111 | 0.60 |
| run | 0.600 | 1.000 | +0.400 | — |
| jump_in_place | 0.000 | 0.400 | +0.400 | — |
| rough_cross / tunnel_cross / fly_jump | 0.000 | 0.000 | 0.000 | — |

### 29.0 第二个种子到达后：结论**加强**（2/5 种子）

| seed | slope_spin | step_up | ramp_up | run |
|---|---:|---:|---:|---:|
| **DR OFF**（nominal） | 0.750 | 0.750 | 0.333 | 0.600 |
| DR ON seed 0 | 0.500 | **0.000** | 0.222 | 1.000 |
| DR ON seed 1 | **0.000** | **0.120** | 0.333 | 1.000 |
| **DR ON 均值（2 种子）** | **0.250** | **0.060** | 0.278 | 1.000 |
| bar | 0.600 | 0.600 | 0.600 | — |

⇒ **两个当前过门的科目，在 DR 下都远低于各自 bar**（小陀螺 0.250 vs 0.600；上台阶 0.060 vs 0.600）。
`run` 反而 0.600→1.000（无 bar，且更可能是小样本噪声）。

**§29.2 的建议因此从"选项"升级为"必做"**：v2 **不能**原样打开 DR，
否则会用刚拿到的两个过门科目去换一个鲁棒性指标。

### 29.0b 三个种子后：结论**稳定**，且呈现清晰的"科目相关性"

| seed | slope_spin | step_up | ramp_up | ramp_down | rough_cross | run |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 0.50 | 0.00 | 0.22 | 1.00 | 0.00 | 1.00 |
| 1 | 0.00 | 0.12 | 0.33 | 1.00 | 0.00 | 1.00 |
| 2 | 0.25 | 0.12 | 0.22 | 1.00 | 0.00 | 1.00 |
| **DR ON 均值** | **0.250** | **0.083** | 0.259 | **1.000** | 0.000 | 1.000 |
| *DR OFF*(nominal) | *0.750* | *0.750* | *0.333* | *1.000* | *0.000* | *0.600* |
| bar | 0.600 | 0.600 | 0.600 | 0.600 | 0.600 | — |

**三点观察（3/3 种子一致）**：

1. **小陀螺**（0.750 → 0.25，三个种子 0.50/0.00/0.25）**全部低于 bar**
2. **上台阶**（0.750 → 0.083，三个种子 0.00/0.12/0.12）**全部远低于 bar**
3. **而 `ramp_down` 与 `run` 完全不受影响**（1.000 / 0.600→1.000）

⇒ **DR 鲁棒性是"科目相关"的，不是全局退化**：
**先学会的、样本充分的驾驶类技能扛得住**；**后期才学会、样本很少的特殊技能（小陀螺、上台阶）扛不住**。
这在机理上说得通——特殊技能是"刚学会"的，处于能力边缘，扰动一来就掉出去。

**⇒ 对 v2 的直接含义**：DR 打开后，**特殊技能需要更多训练样本或更温和的扰动**，
而驾驶类技能不必额外保护。这也让 §30.3 的"第 1 项与第 2 项必须一起上"更有分量：
历史编码器正是让"边缘技能"在观测延迟下仍能维持的那一环。

### 29.1 初步结论与其**样本量限制**（两者必须一起说）

**结论**：当前 checkpoint **对"DR 默认打开"不鲁棒**——DR 关时两个过门的科目，
**DR 一开就都掉到各自 bar 以下**。

**限制（不可忽略）**：
- 这是 **5 个种子中的第 1 个**；其余 4 个仍在跑，**min/mean/`all_seeds_ge_0.6` 才是结论**。
- 混合评测里**每个科目只有 8 个 env** ⇒ `complete_rate` 的分辨率是 **1/8 = 0.125**，
  0.750 = 6/8、0.000 = 0/8。
- 因此 `jump_in_place 0.000→0.400`、`run 0.600→1.000` 这类"提升"**更像噪声**，
  不能解释为"DR 有正则化收益"。
- 但 `step_up` 从 **6/8 掉到 0/8** 的幅度，超出了"噪声"能轻松解释的范围，
  **应当按真信号对待**。

### 29.2 对 v2 计划的直接影响

若 v2 照清单把 DR 打开，**必须先回答**：
1. 5 个种子的 min/mean 是否真的把 `step_up`/`slope_spin` 打到 0.60 以下？
2. 若是 ⇒ v2 需要**同时**做一件事，否则会把刚拿到的两个过门科目赔回去：
   - 选项 A：**降低 DR 强度**（`RM_EFFORT_*` 收窄、延迟上限降低），先保住进度；
   - 选项 B：**加长训练**（DR 需要更多样本才能收敛，400 迭代可能不够）；
   - 选项 C：**先只对失败科目开 DR**（本仓库没有这种粒度，需新增）。

⚠️ 这也解释了为什么"DR 提前并默认开"这条**在本次验收之前无法评估**——
**没有任何 DR-on 的参照系**。`baseline_16295` 的 5 个种子将补上这个参照系。

---

## 30. ⚠️ 对 §29 的关键修正：DR 崩塌**不等于**"v2 不该开 DR"——它是"当前 checkpoint 没练过 DR"

### 30.1 DR 打开时实际生效的是**七类**扰动，不是清单里的三类

`RM_DR_OFF=0` 时的全部扰动（`mod4_task.py:158-172`，实测默认值）：

| 项 | 范围 | 清单第 2 项是否提到 |
|---|---|---|
| `EFFORT_LEG` / `EFFORT_WHEEL` | ×0.75–1.25 / ×0.90–1.10 | ✅ 提到（力矩 ±10~25%） |
| `EFFORT_NOISE` / `_WHEEL` | ±3% / ±2% | ✅ 提到 |
| `ACTION_DELAY` | **0–2 控制步 = 0–20 ms** | ⚠️ 提到 0–5 ms（**实际默认是 0–20 ms**） |
| **`OBS_DELAY`** | **1–2 控制步 = 10–20 ms**（`HOLD_PROB` 0.75） | ❌ **没提** |
| **`ARMATURE_SCALE`** | **×0.7–1.6** | ❌ 没提 |
| `LEG/WHEEL_FRICTION_MAX` | 0.10 / 0.02 | ❌ 没提 |
| **`ENCODER_BIAS`** | 0.015 rad（关节零位偏置） | ❌ 没提 |

### 30.2 因此 §29 的 DR 种子测的是**什么**

那些种子评的是一个：

> **DR 关训练出来、且观测是单帧（无历史编码器）**的 checkpoint，
> 放到一套它**从未见过**的扰动下——其中包括 **10–20 ms 的观测延迟** 与 **0.7–1.6× 的转子惯量随机化**。

（已核实：该 run 的 manifest `env` 快照里**没有** `RM_SEQ_ENCODER`，策略就是 35 维单帧 ✅）

**⇒ 所以 0.75 → 0.25/0.06 的崩塌，正确的含义是：**
1. **当前 checkpoint 不鲁棒**（完全在预期内——它**从没在 DR 下训练过**）；
2. 它**量化了 v2 的 DR 训练必须买到多少**：从 **0.06 / 0.25** 提到 **≥0.60**；
3. **它不能推出"v2 不要开 DR"**——恰恰相反，它说明**必须在训练时就开**（这正是清单第 2 项的要求）。

### 30.3 一个新发现的**跨项耦合**：第 1 项是第 2 项的前提

**观测延迟 10–20 ms 对"单帧观测"的策略是硬伤**：它看到的永远是过期的状态。
而 **5 帧历史 + 编码器（清单第 1 项）恰恰是应对观测延迟的机制**——
历史让策略能从"过期的若干帧"里推断当前状态。

> ⇒ **第 1 项（历史编码器）与第 2 项（DR 默认开）是耦合的**，
> 和 §23 发现的"第 4 项依赖第 6 项（1024 env）"是同一类。
> **v2 应当两项一起上**：只开 DR 而无历史，等于让单帧策略硬扛 20 ms 延迟；
> 只加历史而不训练 DR，则延迟鲁棒性学不到。

**⚠️ 另注**：清单第 2 项写的"动作延迟 0–5 ms"，而当前 DR 默认是 **0–20 ms**。
v2 要在两者间做选择——**若按清单收窄到 0–5 ms，DR 的强度会显著低于本次测量**，
崩塌的幅度也应随之减小。

---

## 31. ✅ 正式验收基线完成（`docs/acceptance_baseline_16295/`）——DR 定论

`final_acceptance_mod4.sh model_16295.pt baseline_16295` 已跑完（exit 0，02:30 → 03:25）。
产出：`nominal.json` + `nominal_gate.txt` + `roof_check.txt` + `dr_seed_0..4.json` +
`dr_summary.json` + `FROZEN_VERSION.txt`（记录 checkpoint `d15aa478…`、`mod4_task 022b5d5c`、
`robot.usd 7b4d8535`、`import_contract cbcdacdf`）。

### 31.1 nominal（DR OFF，seed 20260912，64 env × 2200 步）

| 路线 | complete | 门禁 |
|---|---:|---|
| **slope_spin** | **0.750**（spin_deg **367.5°**） | ✅ **PASS → promote** |
| **step_up** | **0.750** | ✅ OK |
| ramp_down / step_down | **1.000** | ✅ OK |
| run | 0.600 | — |
| ramp_up | 0.333 | ❌ FAIL |
| rough_cross / tunnel_cross / fly_jump / jump_in_place | 0.000 | ❌ FAIL |

`closure 0.607 mm` ✅、`mimic 1.83 mrad` ✅、**`ROOF_CHECK=PASS`** ✅。

### 31.2 ★ DR 定论（5 个种子，`dr_summary.json`）

| 路线 | min | mean | `all_seeds_ge_0.6` | DR OFF 对照 |
|---|---:|---:|---|---:|
| ramp_down | **1.000** | **1.000** | ✅ **True** | 1.000 |
| step_down | **1.000** | **1.000** | ✅ **True** | 1.000 |
| **run** | **0.800** | **0.960** | ✅ **True** | 0.600 |
| ramp_up | 0.222 | 0.311 | ❌ False | 0.333 |
| jump_in_place | 0.000 | **0.320** | ❌ False | 0.000 |
| **slope_spin** | **0.000** | **0.250** | ❌ **False** | **0.750** |
| **step_up** | **0.000** | **0.150** | ❌ **False** | **0.750** |
| rough_cross / tunnel_cross / fly_jump | 0.000 | 0.000 | ❌ False | 0.000 |

**三条结论（5 种子一致）**：

1. **`ramp_down` / `step_down` / `run` 完全 DR 鲁棒**（`all_seeds_ge_0.6 = True`）；
   `run` 甚至从 0.600 **升到** min 0.800 / mean 0.960。
2. **两个在 DR 关时过门的科目，在 DR 下全部失守**：小陀螺 mean 0.250、上台阶 mean 0.150，
   **且 5 个种子的 min 都是 0.000**。
3. **所以"DR 提前并默认开"这一条，不能原样照做**：它对驾驶类技能无害甚至有益，
   但对**刚学会的特殊技能**（小陀螺/上台阶）是破坏性的。
   → v2 需要 **`V2_MILD_DR=1` 起步**，或给特殊技能更多训练样本（§29.2/§30）。

**⚠️ 再次强调（避免误读）**：这测的是"**DR 关训练出来的** checkpoint 在 DR 下的表现"。
它**不**证明"开了 DR 训练会变差"——恰恰相反，它量化了 **v2 的 DR 训练必须买到多少**：
把 0.000/0.250/0.150 提到 ≥0.60。

---

## 32. ⚠️ v2 实测状态（第 109 轮）：**smoke 拦住了 4 个真 bug，第 5 个（CUDA 级）尚未解决**

按你的选择，验收基线跑完后进入 v2：**17 个补丁已应用到真仓库**（17/17 成功），
五项验收证据全过，然后按清单第 3 步**先跑 smoke** —— **smoke 连续拦住了 4 个启动期 bug**：

| # | 报错 | 根因 | 状态 |
|---|---|---|---|
| 1 | `EULA ... EOF when reading a line` | `start_mod4_stage_fixedplant.sh` 的 `OMNI_KIT_ACCEPT_EULA=YES \` 后**插了一行注释**，续行被截断 ⇒ 赋值丢失（此前一直靠父进程兜底） | ✅ 已修（`patch_eula_continuation.py` + 启动脚本自身导出） |
| 2 | `NameError: name 'SEQ_HISTORY' is not defined` | `patch_obs_history_encoder` 在 `mod4_task.py` 用 `SEQ_HISTORY`，却**只在 `train_mod4_ppo.py` 定义** | ✅ 已修（`patch_obs_history_encoder_fix.py`） |
| 3 | `ValueError: The term 'track_lin_vel' expects ... ['kwargs']` | `patch_reward_clip_and_sigma` 的包装闭包 `def _wrapped(env, **kwargs)` 被 Isaac Lab 的 `inspect.signature` 解读为**必填参数 kwargs** ⇒ 所有带 params 的奖励项都无法加载 | ✅ 已修（`@functools.wraps(fn)`；已用最小复现单测证实内省从 `['env','kwargs']` 变为 `['env','command_name','std']`） |
| 4 | `TypeError: accumulate_route_stats() takes 1 positional argument but 2 were given` | 我写的 step EventTerm 函数签名是 `(env)`，而 Isaac Lab **必须以 `(env, env_ids)` 调用**（`skills_isaac.py` 已写明此约定） | ✅ 已修（签名改为 `(env, env_ids=None)`） |
| 5 | **`CUDA error: device-side assert` → `Exception: Failed to get net contact forces from backend`** | 发生在**第一个 `update_jump_state`** 读 `wheel_contact` 时（`skills_isaac.py:1072`） | ❌ **未解决** |

### 32.1 第 5 个问题的已知信息（供后续接手）

```
train_mod4_ppo.py:466 main → on_policy_runner.learn:87 → vecenv_wrapper.step:185
  → mod4_env.py:81 step → event_manager.apply:289 → skills_isaac.py:1072 update_jump_state
  → contact_sensor.data → _update_buffers_impl → get_net_contact_forces
      Exception: Failed to get net contact forces from backend
（其前有 PhysX 的 CUDA device-side assert：CudaKernels.cu:1571 / GpuRigidContactView / GpuRigidBodyView）
```

**未验证的怀疑（按可能性）**：
1. **`ENVS=1024` 与接触传感器视图的交互**：`build_layout` 上限是 1024，而 smoke 相位用 64。
   失败发生在 **tunnel 相位（1024 env）**；smoke 相位本身**也 0 迭代**，但它的报错未被单独确认。
   **建议第一步**：把 `ENVS` 降到 512、只跑 smoke，看是否仍触发 —— 这能立刻区分"1024 特有"还是"普遍"。
2. **GPU 状态**：本次连续启动了 6 次 Isaac（每次 30–60 s 启动），日志里多次出现
   `failed to fork the child process ... Resource temporarily unavailable`。
   **建议**：`nvidia-smi` 确认无残留占用，必要时重试一次干净运行。
3. **我的补丁在 1024 env 下的副作用**（观测历史 175 维 × 1024 env 的显存/形状）。

### 32.2 ⚠️ 当前仓库状态（重要）

- **17 个补丁 + 4 处修复已应用到真仓库**（`isaac/mod4/*.py`、`sim_mujoco/onnx_play.py`、
  `train/deploy/contract_rm2025_later.json`、3 个 `migration/linux/*.sh`）。
- 全部文件 `py_compile` / `bash -n` 通过 ✅；**但 v2 跑不起来**（第 5 个问题）。
- **每一步都可回退**：每个补丁都留了 `*.bak_pre_*`（连同本次修复的
  `*.bak_pre_seqfix` / `*.bak_pre_clipsig` / `*.bak_pre_seqenv` / `*.bak_pre_eula`）。
- **基线不受影响**：`docs/acceptance_baseline_16295/` 是补丁前产出的，与当前代码状态无关 ✅。

### 32.3 本轮的净价值

> **smoke 这一步本身值 4 个真 bug。** 这 4 个如果没有 smoke，都会在 v2 正式训练时炸掉——
> 而且第 3 个（奖励管理器无法构建）会**让所有相位都起不来**，第 1 个（EULA）会**让任何新调用方都起不来**。

这也再次印证本会话的核心教训：**`py_compile` + 锚点检查不足以验证补丁**——
4 个 bug 里只有第 4 个是"签名/语法"类，其余三个（续行截断、跨模块名字、内省签名）
**都只有在真正运行时才暴露**。

---

## 33. v2 启动失败的收窄结论（第 110 轮）+ 一个测试陷阱

### 33.1 已排除与已确认

| 事实 | 证据 |
|---|---|
| **与 env 数无关** | 64 env 的 smoke 相位**同样** 0 迭代 + 47 个 `device-side assert` ⇒ **不是 1024 特有** |
| 失败点固定 | traceback 每次都到 `skills_isaac.py:1072`（`update_jump_state` 读 `wheel_contact`）⇒ 其**前**是 PhysX 的 `CudaKernels.cu:1571` / `GpuRigidContactView.cpp:202` |
| 植物是对的 | 那些失败的 smoke 日志里 `plant=…/mod4_rolling_20260913/…`（`7b4d85356355`）✅ 不是植物错配 |

### 33.2 ⚠️ 本轮我自己的实验陷阱（值得记下）

为做单变量实验，我**直接调用** `start_mod4_stage_fixedplant.sh` 而没有先 `source tunnel_tuning.env`，
结果它用了**默认植物**：

```
[launch] plant=incoming/mod4_fixed_20260912/.../robot.usd   ← 交付版（导轮焊死）
RuntimeError: Sensor at path '.../guide_roller_[0-9]+' could not find any bodies with contact
             reporter API.
```

⇒ **不 source 调参文件就直调 stage launcher，会静默换成交付版植物**，而交付版**没有独立的
`guide_roller` 刚体**，接触传感器根本建不起来。**这次失败是我的测试设置错误，不是代码问题**——
但它本身是一个值得记的陷阱（与本会话反复出现的"静默配置错配"同一类）。

**正确做法**：直调时必须显式带上 `RM_MOD4_USD=…/mod4_rolling_20260913/chassis_mod4/isaac/robot.usd`。

### 33.3 下一步的单变量实验（每次约 5 分钟）

按可能性排序，**一次只改一个变量**、用 64 env / 30 迭代：

1. **`RM_ROUTE_CURRICULUM=0`** —— 同时关掉我新增的 step 事件与 CurrTerm。
   这是唯一**新增了 step 事件**的补丁（`EventTerm(func=route_curr.accumulate_route_stats, mode="step")`），
   而失败恰好发生在一个 step 事件里 ⇒ **首选嫌疑**。
   ⚠️ 必须显式带 `RM_MOD4_USD`（见 §33.2）。
2. **`RM_SEQ_ENCODER=0`** —— 关掉 5 帧历史（观测管理器的缓冲）。
3. **`RM_ACTION_DELAY_MS_MAX=0`** —— 关掉子步延迟（唯一改 `ActionTerm` 的补丁）。
4. 若以上都通不过 ⇒ **逐补丁回退**（每个补丁都有 `*.bak_pre_*`）。

### 33.4 当前状态的诚实总结

- ✅ **基线完好**：`docs/acceptance_baseline_16295/`（补丁前产出，与当前代码无关）
- ✅ **13 项交付物齐备**：17 补丁 + 2 模块 + 7 脚本 + 文档 §0–§33 + 起链清单
- ✅ **smoke 拦下 4 个真 bug 并已修**（§32）
- ❌ **v2 仍起不来**：第 5 个（CUDA 级）未解决，已收窄到"某个 step 事件路径"，
  首选嫌疑是**我新增的课程 step 事件**
- ⚠️ **真仓库处于已打补丁状态**，每个改动都有 `.bak` 可回退

---

## 34. ✅ 元凶已隔离：**课程接线**（其余 v2 配置全部可用）

第 111 轮做了 §33.3 的第 1 项单变量实验，结果**决定性**：

| 实验 | 配置 | 结果 |
|---|---|---|
| **A** | v2 全开，**`RM_ROUTE_CURRICULUM=0`** | ✅ **30/30 迭代完成，零错误** |
| **B** | v2 全开，`RM_ROUTE_CURRICULUM=1` | ❌ 0 迭代，**47 × `device-side assert`** |

两次都**显式带上了正确的 `RM_MOD4_USD`**（rolling / `7b4d85356355`，日志已核对 ✅），
所以植物错配被排除。

### 34.1 一个必要的修复（但不充分）

`accumulate_route_stats` 开课时**每个控制步做 GPU→CPU 同步**（`ids.detach().to("cpu").tolist()`），
而项目自己在 `mode_onehot` 的注释里就记着这条教训：
*"the earlier list comprehension walked 1024 route ids per control step (a GPU->CPU sync plus 1024
Python int() calls at 50 Hz) and the audit asked for a vectorised implementation"*。

**已改为向量化**（`torch.bincount`，每步零同步；窗口关闭时一次性同步），并有单测 ✅ ——
**但实验 B 仍然失败** ⇒ **同步不是（唯一）原因**，病因在课程接线的其他地方
（`route_difficulty_schedule` 这个 **CurrTerm**，或 `route_isaac.py` 的**消费端**）。

### 34.2 ⇒ v2 现在可以跑（少一项）

**`RM_ROUTE_CURRICULUM=0` 时，v2 的其余五项全部可用**：
① 5 帧历史 + 编码器 ✅ ② DR 默认开 ✅ ③ 奖励截断 + sigma ✅
⑤ sim2sim 产物门禁 ✅ ⑥ 1024 env ✅ —— **只有第 ④ 项（路线难度课程）需要单独调试**。

`start_v2_chain.sh` 已把课程**默认改为关闭**，并在注释里写明隔离证据与"其余五项可用"。

### 34.3 下一步（交给后续轮次）

在 v2 能跑起来的前提下，**用二分法定位课程接线的具体故障点**（每次约 5 分钟）：
1. 只保留**消费端**（`route_isaac.py` 的 `cmd` 缩放），去掉 step 事件与 CurrTerm；
2. 只保留 **CurrTerm**，去掉消费端与 step 事件；
3. 只保留 **step 事件**。

三项逐一验证即可定位到具体补丁，而且**不必再阻塞 v2 的整体推进**。

---

## 35. 二分结果（第 112 轮）：**step 事件已排除**，剩两个嫌疑

| 实验 | step 事件 | CurrTerm | 消费端 | 结果 |
|---|:---:|:---:|:---:|---|
| A（§34） | — | — | — | ✅ 30/30 迭代（`RM_ROUTE_CURRICULUM=0` ⇒ 三者全关） |
| B（§34） | ✔ | ✔ | ✔ | ❌ 47 asserts |
| **C（本轮）** | **✗ 注释掉** | ✔ | ✔ | ❌ **仍 47 asserts** |

⇒ **新增的 step 事件不是原因** ✅（已排除；其注册也已恢复，`py_compile` 通过）。

**剩余两个嫌疑**（各对应一次约 5 分钟的实验）：

| # | 实验 | 做法 |
|---|---|---|
| **D** | 只关**消费端** | 把 `route_isaac.py` 里 `route_commands` 末尾的 `cmd` 缩放两行注释掉，保持 `RM_ROUTE_CURRICULUM=1` |
| **E** | 只关**CurrTerm** | 把 `mod4_task.py` 里 `route_difficulty = CurrTerm(...)` 注释掉，保持 `RM_ROUTE_CURRICULUM=1` |

**D 优先**：消费端**每控制步**执行（`torch.tensor(_tbl)[_ids]` + `torch.cat`），
而 CurrTerm 只在 **reset** 时执行。**每步路径**更可能触发接触视图的断言。

**⚠️ 注意**：做 D/E 时务必**显式带 `RM_MOD4_USD`**（§33.2 的陷阱：不 source 调参文件就直调会静默换成交付版植物）。

### 35.1 当前可用状态（不变）

**`RM_ROUTE_CURRICULUM=0`（启动脚本的默认）⇒ v2 正常训练** ✅ —— 五项清单项可用，仅第 ④ 项待定位。

---

## 36. ✅ 二分完成：故障点 = **课程在事件里做 CUDA 工作**，且时间点精确吻合

### 36.1 决定性证据：失败发生在**第一个课程窗口关闭的瞬间**

最后一轮实验（消费端已改为零分配）仍然失败，**但迭代数从 0 变成了 12** —— 这个数字就是答案：

```
RM_CURR_WINDOW_STEPS = 300 控制步
1 迭代 = 24 控制步（--steps_per_env 默认）
300 / 24 = 12.5  ⇒  第 12 个迭代结束时关闭第一个窗口
实测：训练到 12 个迭代后出现 49 个 device-side assert
```

⇒ **故障发生在窗口关闭的那一刻**，而不是启动时、也不是每步。窗口关闭时课程做了两件 CUDA 工作：

```python
# (1) route_difficulty_schedule —— 把所有计数器同步回 CPU
att_list = st["attempts"].detach().to("cpu").tolist()     # GPU->CPU 同步
# (2) _publish —— 分配一个新的 CUDA 张量
env._mod4_route_speed_scale_t = torch.tensor(..., device=env.device)
```

两者都在 **CurrTerm/EventTerm 的调用栈内**、即 **PhysX 管线中间**执行 ⇒ 接触视图内核断言 ✅。

### 36.2 正确的修法（已识别，尚未实施）

**把速度缩放搬到 host 侧、只做一次**——**照 `RM_ROUGH_SPEED_MAX` 的既有做法**：

```python
# route_isaac.py 里已有的、被证明可靠的模式（一次性、host 侧）
rough_cap = float(os.environ.get("RM_ROUGH_SPEED_MAX", "0") or 0.0)
if rough_cap > 0.0:
    for i, route in enumerate(rc.routes):
        if route["kind"] == "rough_cross":
            rc.speeds[i, 1] = min(float(rc.speeds[i, 1]), rough_cap)
```

⇒ 课程等级变化时（每窗口一次）**直接改 `rc.speeds`**，而**不要在每步缩放 `cmd`、也不要在事件里建张量**。
`rc.speeds` 是控制器构造期使用的采样范围，改它**发生在 host 侧且不在物理管线内** ✅。

**这一步应当在下一轮做**，并把 §34 里"默认关"改回"默认开"。

### 36.3 本轮的净结果

| 项 | 结论 |
|---|---|
| step 事件 | ❌ 已排除（实验 C） |
| CurrTerm 本身 | ✔ 参与（窗口关闭时触发） |
| 消费端 per-step 分配 | ✔ 参与（改为零分配后迭代数 0→12，证明它是一部分原因） |
| **根因** | **课程在事件/CurrTerm 内做 CUDA 分配与同步**（与 PhysX 管线冲突） |
| **修法** | **host 侧改 `rc.speeds`（照 `RM_ROUGH_SPEED_MAX`），事件内零 CUDA 操作** |

**`RM_ROUTE_CURRICULUM=0` 仍是 v2 的可用默认**（其余五项全通），本轮**不改变这一点**；
但 §36.2 给出了一条**明确的、有先例的**修复路径。

---

## 37. ✅✅ v2 确认可用（第 114 轮）：45 迭代零错误，且截断报告与设计预测吻合

用**真实 smoke 规格**（64 env、60 迭代）跑了完整 v2 配置（仅课程关闭）：

```
植物           : 7b4d85356355（rolling ✅ 正确）
迭代           : 45 / 60（280 秒窗口内跑完的）
错误           : （无）✅
[reward-clip]  : mode=safe clip=2.50 clipped=22 skipped=9      ← 见下
部分热启动     : partial ✅（走了 patch_partial_warmstart 的零填充路径）
Iteration time : 6.09 s
```

### 37.1 `skipped=9` **精确命中 §3.7 的预测**

§3.7 从源码静态提取出"v2 生效集里 `|weight| > 2.5` 的项共 9 个"：

```
route_success(20) termination(-20) base_contact(-10) jump_push(10) jump_climb(8)
track_ang_vel(5) dof_pos_limits(-5) jump_land(3) jump_hard_land(-3)
```

**运行期报告 `skipped=9` ✅ 完全一致** ⇒ 截断白名单的实际行为与静态分析一致
（`clipped=22`，静态预测 20；差 2 项，属预期内的边界差——静态提取按源码块归类，
运行期按实例字段遍历，`jump_launch_ready` 等新增项也计入）。

### 37.2 v2 的最终可用配置

| 清单项 | 状态 |
|---|---|
| ① actor 5 帧历史 + 编码器（latent 3）+ 部分热启动 | ✅ **运行验证通过** |
| ② DR 默认开（含 0–5 ms 动作延迟，ms 模式取代控制步队列） | ✅ 运行验证通过 |
| ③ 奖励截断 ±2.5（`safe`）+ tracking sigma 0.5 | ✅ **`clipped=22 skipped=9`，与预测一致** |
| ④ 路线难度课程 | ⚠️ **暂停**（`RM_ROUTE_CURRICULUM=0`），修法见 §36.2 |
| ⑤ sim2sim 产物门禁 | ✅ 独立运行 `RESULT: SIM2SIM MOD4 PASS` |
| ⑥ 1024 env | ✅ 已配置（本次用 64 做快速验证） |

⇒ **六项里五项已运行验证，第四项有明确的修复路径且不阻塞其余五项。**

### 37.3 起 v2 的确切命令

```bash
# 先跑一次完整 smoke（本次已验证可过）
CKPT=logs/isaac_mod4/2026-09-13_01-17-30_mod4_fixed_mixed/model_16295.pt \
  FROM=smoke bash migration/linux/start_v2_chain.sh
# 再起正式 v2 链（ENVS=1024）
CKPT=<最终 checkpoint> bash migration/linux/start_v2_chain.sh
```
（`start_v2_chain.sh` 已默认 `RM_ROUTE_CURRICULUM=0`，并在注释里写明隔离证据；
若课程修好，设 `RM_ROUTE_CURRICULUM=1` 即可。）

---

## 38. ✅✅✅ 课程修好：host 侧缩放，六项清单全部可用

按 §36.2 的修法实施后，**决定性验证通过**：

```
RM_ROUTE_CURRICULUM=1（host 侧缩放）
迭代 : 40 / 60（280 秒窗口内）      错误 : （无）✅
课程 : 10 条 Curriculum/route_curriculum/level_* 指标全部发布 ✅
```

### 38.1 修法的最终形态（三处改动）

| 改动 | 内容 |
|---|---|
| **移除** `route_isaac.py` 的每步缩放 | 恢复为原始的 `term.command[:, 0] = cmd[:, 0]` 三行；**step 事件内零 CUDA 工作** |
| **新增** `mod4_curriculum._apply_speeds_to_routes(env)` | 在**窗口关闭**时，按等级把 `rc.speeds[i, 1]` 缩放到 `base[i] * scale[k]` —— 与 `RM_ROUGH_SPEED_MAX` **同一机制、同一成本级**（host 侧、原地、无分配、每窗口一次） |
| **不发布** CUDA 张量 | `_mod4_route_speed_scale_t = None`；只保留 python 列表供诊断 |

**幂等性**：`base` 在第一次调用时记下交付上限（`_mod4_route_speed_base`），
所以等级反复变化**不会累乘** ✅。

### 38.2 六项清单的最终状态（全部可用）

| 项 | 状态 | 证据 |
|---|---|---|
| ① 5 帧历史 + 编码器（latent 3）+ 部分热启动 | ✅ | 运行验证（`partial` 路径） |
| ② DR 默认开（0–5 ms 延迟） | ✅ | 运行验证 |
| ③ 奖励截断 `safe` + sigma 0.5 | ✅ | **`clipped=22 skipped=9`**，与 §3.7 预测一致 |
| ④ **路线难度课程** | ✅ **已修** | **40/60 迭代零错误 + 10 条等级指标** |
| ⑤ sim2sim 产物门禁 | ✅ | `RESULT: SIM2SIM MOD4 PASS` |
| ⑥ 1024 env | ✅ | 已配置 |

### 38.3 起 v2 的最终命令

```bash
CKPT=logs/isaac_mod4/2026-09-13_01-17-30_mod4_fixed_mixed/model_16295.pt \
  FROM=smoke bash migration/linux/start_v2_chain.sh     # 先 smoke（已验证可过，且六项全开）
CKPT=<最终 checkpoint> bash migration/linux/start_v2_chain.sh    # 正式链（ENVS=1024）
```
`RM_ROUTE_CURRICULUM` 已默认 **1**；`V2_MILD_DR=1` 可选（§30 的 DR 崩塌证据）。

---

## 39. ⚠️ 实时发现：smoke 的闭环门禁**与 DR 不兼容**（且这解释了旧链为何跳过 smoke）

### 39.1 实测

v2 链（`RM_DR_OFF=0`，六项全开）smoke 相位运行中，`closure_err_session_max_m` 的轨迹：

```
迭代 1..25 : 0.000600 m   （稳定）
迭代 33    : 0.001200 m   （一次新的最差值）
smoke 门禁 : < 0.002 m    ⇒ 当前已用掉 60%
```

对照基线（DR **关**）：

| 运行 | closure session max |
|---|---|
| `acceptance_baseline_16295`（DR OFF） | **0.000607 m** |
| v2 smoke（DR ON） | **0.0012 m 且仍在爬** |
| **smoke 门禁** | **< 0.002 m** |

**机理**：DR 把 `ARMATURE_SCALE` 随机化到 **×0.7–1.6**、力矩噪声 ±3%、摩擦与编码器偏置也在变
⇒ 约束力变大 ⇒ 闭环残差上升。**DR 大约把它翻倍**。

⚠️ **方法学说明**：不要把 `session_max` 当线性斜坡外推——它是**单调阶跃函数**
（只在出现新的最差值时跳一次）。所以"按斜率外推到 12.6 mm"是**错的模型**；
正确说法是"**一次新的最差事件把它推到 1.2 mm，它可能再跳，也可能就此停住**"。

### 39.2 这解释了悬案（§19 / 第 67 轮）

本轮之前我记录过："**本次链是带 `from_phase=tunnel` 启动的，smoke 从未跑过**，
跳过它的依据只是一个探针的 0.002035 m，而评测实测只有 0.0006 m"，并建议"先跑一次 smoke"。

**现在这次实测给了答案**：那个探针值（2.035 mm）**不是噪声**——
**DR 打开后闭环确实会升到门禁附近**，所以旧链跳过 smoke 的决定**很可能是对的**，
而原因不是"探针错"，而是：

> **`< 2 mm` 这条 smoke 阈值是在 DR 关闭下标定的；v2 把 DR 默认打开后，它不再适用。**

### 39.3 正确的修法（待办）

**让门禁 DR-aware**，而不是继续靠"跳过 smoke"绕过：

```bash
# 概念上：
if [ "${RM_DR_OFF:-1}" = "1" ]; then LIM=0.002; else LIM=0.004; fi   # DR 打开时放宽
```

否则**每一条打开 DR 的链都会在第一道门被卡死**（这正是 v2 现在面对的情况）。
**在链运行期间不修改该脚本**（bash 增量读取运行中的脚本，见 §121 的约束）；
若 smoke 真的 FAIL，立即可用 `FROM=tunnel` 继续推进，门禁修正随后做。

---

## 40. ✅ v2 的运行期自描述被验证（第 129 轮）：manifest 37 键 ⇒ 评测能重建编码器配置

### 40.1 查的是一个会让所有 v2 评测失真的风险

v2 的策略是 **175 维输入**（5 帧历史 × 35）。如果评测脚本**不从 run manifest 回放
`RM_SEQ_ENCODER`**，它会以 **35 维**建环境 ⇒ 策略**加载不上或静默错配** ✗。

**实测：风险不存在** ✅

```python
# eval_terrain_mod4.py:59-63
MANIFEST, MANIFEST_PATH = _find_manifest(args.manifest, args.checkpoint)
    os.environ[_key] = str(_val)          # 回放 manifest 的 RM_*（CLI 优先）
```

v2 run 的 manifest（`logs/isaac_mod4/2026-09-13_04-47-00_mod4_fixed_mixed/run_manifest.json`）：

| 键 | 值 |
|---|---|
| `RM_SEQ_ENCODER` | **1** ✅ |
| `RM_SEQ_HISTORY` | **5** ✅ |
| `RM_DR_OFF` | **0** ✅ |
| `RM_ROUTE_CURRICULUM` | **1** ✅ |
| `RM_CURR_WINDOW_STEPS` | **1000** ✅ |
| `RM_LEG_KP` | 2500 |

⇒ **评测会用 5 帧历史重建环境**，175 维策略正确加载。

### 40.2 顺带验证了 §12 的可复现性修复

| run | manifest 的 `RM_*` 键数 |
|---|---|
| 基线（补丁前，如 `2026-09-13_00-09-37`） | **12** |
| **v2 run** | **37** ✅ |

§12 修的是"`env` 只是**进程环境快照**，50 个 run 里 37 个记不到自己的配置"。

**⇒ 这两个修复是互相依存的**：
**没有 §12 的 manifest 完整性，§1 的编码器就会在评测时静默退回 35 维** ✗
——即"改了观测却没记录观测配置"，而这种错误**在训练日志里完全看不出来**。

---

## 41. v2 配置的"消费者"逐个排查（§138–§141）：**三处坏了、一处对的**

v2 的配置真源是 **run manifest 的 `effective` 块**（§40：123 个键）。但每个消费者是否都从那里读？
逐个查了四处，结果是 **3 处坏了**：

| # | 消费者 | 它当时从哪读 | 后果 | 状态 |
|---|---|---|---|---|
| §138 | 增益一致性检查 | manifest 的**裸常量名**（`LEG_KP`） | 键不存在 ⇒ **静默什么都不检查**（exit 0） | ✅ `patch_gain_parity_keys_fix.py` |
| §140 | 验收的 sim2sim **ONNX 导出** | **环境变量** `RM_SEQ_ENCODER`（而它只 source 了不含该变量的 `tunnel_tuning.env`） | 从 175 维 ckpt 导出 35 维 ⇒ 导出器拒绝 ⇒ **跑完 1 小时后 `exit 6`** | ✅ `patch_acceptance_encoder_from_manifest.py` |
| §121/122 | **链的冻结清单** | 硬编码的文件列表 | 新模块与**整个场地侧**（含定义验收判据的 `route_commands.py`）未被证明未变 | ✅ `patch_frozen_files_modules.py` |
| **§141** | **相位评测**（`eval_terrain_mod4.py`） | **manifest 的 `env` 块** ✅ | — | ✅ **本来就是对的** |

### 41.1 为什么评测那一处是对的

```python
# eval_terrain_mod4.py
57: # The task switches have to be in os.environ BEFORE mod4_task is imported below: MAP_MODE, ...
59: MANIFEST, MANIFEST_PATH = _find_manifest(args.manifest, args.checkpoint)
61: for _key, _val in (MANIFEST.get("env") or {}).items():
63:     os.environ[_key] = str(_val)
66: launcher = AppLauncher(args)
74: import mod4_task          # ← 在环境变量设置【之后】
```

**关键点**：`RM_SEQ_ENCODER` 是**import 时读取**的（`mod4_sequence_model.py` / `mod4_task.py` 的模块级常量），
所以"先设环境变量、后 import"是**硬性顺序要求**。这段代码**自己写了注释说明这一点** ✅
——**项目自己记录过的约束救了这一处**。

### 41.2 三类消费者的共同教训

> **配置的真源是 manifest，但消费者各自按环境变量写。**
> "环境里恰好有"在开发时成立（因为跑链的 shell 里设了），一旦换调用路径（验收脚本、
> 单跑评测、直调 stage launcher）就失效——而**失效方式各不相同**：静默跳过、最后一步中止、
> 或者悄悄用默认值。

**可复用的检查**：对每一个"消费 v2 配置"的地方，问一句
**"它是从 manifest 读的，还是从环境读的？"** —— 四查三坏。

---

## 42. ✅✅ v2 smoke 通过（第 146 轮），链已进入 tunnel 相位

```
[v3] smoke done -> logs/isaac_mod4/2026-09-13_04-47-00_mod4_fixed_mixed/model_249.pt
[v3] === phase tunnel envs=1024 iters=400
```

| 指标 | 实测 | 门禁 | 判定 |
|---|---|---|---|
| 迭代 | **250 / 250** | 完成 | ✅ |
| `closure_err_session_max_m` | **0.0013** | < 0.002 | ✅ **余量 35%** |
| `mimic_err_session_max_rad` | **0.0018** | < 0.01 | ✅ 余量 82% |
| 错误 | **0** | — | ✅ |
| `[reward-clip]` | `clipped=22 skipped=9` | 与 §3.7 预测一致 | ✅ |
| 课程指标 | 10 条 `level_*` 全 = 4 | 起始最高（§76） | ✅ |

产出的 v2 起点 checkpoint：`2026-09-13_04-47-00_mod4_fixed_mixed/model_249.pt`

### 42.1 对 §39 的回顾（我当时的告警没有变成事故，但仍值得记）

我先前担心"**DR 下的闭环会撞上按 DR-off 标定的 2 mm 门禁**"。实测：closure 在 0.6 → 1.2 → **1.3 mm**
处结束，**通过了但用掉了 65% 的门禁余量** ✗→✅。

**⇒ 结论**：§39 的告警**方向正确、后果未发生**；`patch_smoke_gate_dr_aware.py` 仍然值得应用——
它把那 65% 的余量**显式化**，避免下一次在别的植物/配置上被动撞线。
**并且我先前那个"按斜率外推到 12.6 mm"的错误模型也被彻底证伪**（真实终值 1.3 mm）。

### 42.2 接下来

```
tunnel(1024 env × 400 迭代) → terrain → spin → fly → jump
```

**tunnel 是第一道"科目门禁"**：`tunnel_cross/complete_rate ≥ 0.60` 且
`underpass_seen_rate ≥ 0.80` —— 这正是检验 §15 `tunnel_crouch_gate` 的时刻
（基线里 `underpass_seen = 0`，因为原版 `tunnel_crouch_pose` 让"蹲着不动"净赚 +1.00/步）。

---

## 43. 🔴 **最重要的发现**：链的相位/smoke 门禁**一直是失效的**

### 43.1 证据

v2 smoke 的判决行（读它自己的输出）：

```
[v3] smoke: stage_log=logs/isaac_mod4/phasev3_smoke_044655.log nan/oom hits=0 \
             closure_session_max=none mimic_session_max=none
[v3] smoke: WARNING metrics not found in logs/isaac_mod4/phasev3_smoke_044655.log \
             - not failing on that alone
```

**`closure_session_max=none`** —— 它**没读到闭环值**，而真实值（我现在手工读）是 **0.0013** ✅，
就在 `stage_mixed_fixedplant_20260913_044655.log` 里。

### 43.2 根因：一行 grep 的模式错了

```bash
# smoke_verdict() 里
stage=$(grep -h "^\[launch\] log=" "$launcher" | tail -1 | sed 's/.*log=//')
[ -n "$stage" ] && [ -f "$stage" ] || stage="$launcher"
```

但 launcher 实际打印的是：

```
[launch] pid=900797 log=logs/isaac_mod4/stage_mixed_fixedplant_20260913_044655.log
         ^^^^^^^^ "pid=" 在 "log=" 前面
```

**实测**：旧模式匹配 **0** 次；改成 `^\[launch\] .*log=` 匹配 **1** 次 ✅；修正后能读出
`closure 0.0013 / mimic 0.0018` ✅。

⇒ `stage` **永远回退到 launcher 日志** ⇒ 永远找不到指标 ⇒ 走
"**metrics not found → WARNING, not failing on that alone**" 分支 ⇒ **门禁从不判定** ✗✗

### 43.3 代码注释恰好记录了这个退化过程

```
# NOTE (2026-09-13): $1 is the LAUNCHER log ... The first version grepped the launcher log,
# found no metrics, and declared a spurious FAIL that stopped the chain after the smoke.
# Now: ... a missing metric is a WARNING, not a failure
```

⇒ **为了消除一次误报，把检查降级成了警告** —— 而由于模式本身永远匹配不到，
**这个警告变成了常态**，门禁实际上被关掉了 ✗。
这正是 §39 记录的退化链：**门禁误报 → 被放宽 → 静默失效**。

### 43.4 影响范围（重要，需分清）

| 对象 | 是否受影响 |
|---|---|
| **链的相位门禁**（训练中途的 PASS/FAIL） | ❌ **全部失效** —— 每个相位的判决都不可信 |
| **正式验收**（`final_acceptance_mod4.sh`） | ✅ **不受影响** —— 它直接从 `eval.json` 算门禁 |
| **基线数据**（`docs/acceptance_baseline_16295/`） | ✅ **有效** —— 它来自验收而非链门禁 |
| 本次 v2 链的推进 | ✅ **反而有利**：门禁不拦，Phase 会全部跑完并产出 eval，而**我自己每轮在读指标** |
| §39 的 DR-aware 阈值补丁 | ⚠️ **仍然有用但不够** —— 它调的阈值，门禁根本读不到输入 |

### 43.5 修法

`patch_smoke_verdict_logpath.py`（已写、`--check` 通过、**链运行中不应用**）：

```bash
stage=$(grep -h "^\[launch\] .*log=" "$launcher" 2>/dev/null | tail -1 | sed 's/.*log=//')
```

**并建议同时把"指标缺失"从 WARNING 改回失败**（§43.3 的教训：不能用"降级为警告"来消除误报，
那等于关掉检查）——但这一条要等放开门禁后观察一轮再定，避免再次误伤。

### 43.6 教训

> **一个"找不到输入就警告"的门禁，和没有门禁是无法区分的。**
> 本会话在 §17/§63/§121/§122/§138/§140 反复遇到同一个模式，**这一处是最严重的**：
> 前面几处让"某个检查"失效，这一处让**整条链的全部相位检查**失效。

---

## 43.7 ⚠️ **对 §43 的范畴修正**（我上一轮的论断过宽）

§43 我写了"**整条链的全部相位检查失效**"。逐处查完之后，**这是不准确的**。精确的范畴是：

| 门禁 | 输入来源 | 用日志路径？ | 受影响？ |
|---|---|---|---|
| **`smoke_verdict()`**（链的 smoke 门禁） | **stage 日志的指标** | ❌ **模式错**（`^\[launch\] log=` 永不匹配） | 🔴 **是 —— 实际失效**（v2 的实测输出已证：`closure_session_max=none` → WARNING → 通过） |
| 链的 **per-phase verdict**（`run_special_phases_v3.sh:205-232` 的内联 python） | **eval JSON** ✅ | ✅ 不读日志 | ✅ **正常**（有正确的 bar 表）——**但它只 print，从不 exit** ⇒ **不阻断链** |
| **正式验收的门禁**（`final_acceptance_mod4.sh:64`） | `stage_gate.py --eval nominal.json` | ✅ **故意传 stub**（`docs/_gate_stub.log`） | ✅ **正常** ⇒ **基线数据有效** |
| `eval_and_gate_mod4.sh:114` | `stage_gate.py --log "$LOG"` | 取决于 `$LOG` | ⚠️ 待查（本次链不走这条路径） |

### ⇒ 正确的结论

1. **失效的是 `smoke_verdict`**（唯一用 stage 日志指标的门禁）——**不是"全部相位检查"** ✗
2. 链的 per-phase verdict **算得对**，但**只打印不阻断** ⇒ 链在 fly/tunnel 全 FAIL 的情况下仍会跑完全部相位
   （这解释了链 1 为何一路跑到 jump ✅）
3. **正式验收的门禁是好的**，所以 `docs/acceptance_baseline_16295/` 的结论与 §42 的 smoke 通过
   （closure 0.0013，**我手工核过**）**都成立** ✅

### 43.8 补偿控制（现在的做法）

既然 `smoke_verdict` 不可信，就用**与验收同一权威路径**手工复核每个相位：

```bash
python3 isaac/mod4/stage_gate.py --stage <terrain|spin|tunnel|fly|jump> \
    --log docs/_gate_stub.log --eval docs/acceptance_phase_v3_<tag>_<phase>/eval_focus_<kind>.json
```

**已用归档的链 1 报告验证过这套调用** ✅：
- spin（focus）：`complete 0.703 OK`、`spin_deg 1973.7 OK` ⇒ **`PASS -- promote`** ✅
- fly（focus）：`0.0000 FAIL`、`air 0.0000 FAIL` ✅（与记录一致）
- 且它**逐字复现**了链 1 当年的 `[gate] PASS -- promote` 输出 ✅

### 43.9 附带发现：混合 eval 与聚焦 eval 的分辨率差异（会误导人）

同一个 checkpoint 的两次评测：

| 文件 | slope_spin 的 envs | complete | spin_deg |
|---|---|---|---|
| `eval.json`（混合 10 种路线） | **4** | 0.500 ✗ | 250.5° |
| `eval_focus_slope_spin.json`（全 64 env） | **64** | **0.703** ✅ | **1973.7°** |

⇒ **混合 eval 对单一科目只有 ~4 个环境（分辨率 1/4）**，会让及格科目看起来不及格 ✗。
**判断单科目必须用 focus 报告**；链的门禁用的正是 focus ✅（这也是它当年能晋级的原因）。

---

## 44. 补偿控制脚本 + jump 相位的一个可预见风险（第 149 轮）

### 44.1 `migration/linux/my_phase_gate.sh`：手工复核每个相位

因为 §43 的 `smoke_verdict` 不可信，复核改用**与正式验收同一条权威路径**
（`stage_gate.py` + **focus 报告**，log 传 stub）：

```bash
TAG=v2 bash migration/linux/my_phase_gate.sh                 # 全部相位
DIR=docs/acceptance_phase_v3_spin bash migration/linux/my_phase_gate.sh    # 单个
```

**已用归档的链 1 报告逐字验证** ✅：

| 相位 | 输出 | 与记录 |
|---|---|---|
| spin | `0.7030 OK` / `1973.7020 OK` ⇒ **`PASS -- promote`** | 一致 ✅ |
| fly | `0.0000 FAIL` / `0.0000 FAIL` | 一致 ✅ |
| jump | `peak_rise_m 0.0200 FAIL`（bar 0.04） | 一致 ✅ |

**它自己也有一个不足，已修**：`stage_gate.STAGES` 里 `terrain/spin/tunnel/fly` 的 log 要求是空的
（所以 stub 够用），但 **`jump`（和 `run`）需要真实日志里的 `Curriculum/jump_target/...`** ✗。
脚本现在**从链日志解析"相位 → 真实 stage 日志"** —— 用的正是
`[launch] pid=<n> log=<path>` 这一行，**也就是链自己那个坏 grep 没能提取出来的同一行** ✅。
（对当前 v2 链验证：`tunnel → stage_mixed_fixedplant_20260913_051316.log` ✅）

### 44.2 jump 相位的可预见风险：`window_done` 可能需要很久才能达到 1.0

`stage_gate.py` 对 `jump` 的 log 判据是：

```
Curriculum/jump_target/jump/reach_ratio  >= 0.5
Curriculum/jump_target/jump/window_done  >= 1.0      <-- 至少完成【一个完整窗口】
```

**当前实测（tunnel 相位中，jump_in_place 只占 2.6% 槽位）**：

```
reach_ratio: 0.3541   （bar 0.5）
window_done: 0.0000   （bar 1.0）   <-- 一个窗口都没完成
window_steps: 420.5
```

**⇒ 风险**：若 jump 相位（400 迭代）里 jump 的样本仍不足以让窗口走完一轮，
`window_done` 会停在 0 ⇒ **该相位按 log 判据永远过不了** ✗。
（`air_frac 0.0748` 也说明这个阶段的跳跃样本还很稀疏。）

**⇒ 但不会阻断链**：§43.7 已确认链的 per-phase verdict **只 print 不 exit** ✅。
所以 jump 相位的**决定性数字仍然是 focus eval 的 `peak_rise_m ≥ 0.04`** ✅ ——
`window_done` 只影响 `stage_gate.py` 的 log 那一半。

**⇒ 建议下一轮在该相位结束后**用 `my_phase_gate.sh` **分别看** log 判据与 eval 判据，
不要因为 log 判据 MISSING/FAIL 就判定该科目失败 ✅。

---

## 45. ✅ 课程在同一条链里**真的在降级**（第 151 轮，tunnel 相位 76/400）

### 45.1 实测

```
Curriculum/route_curriculum/level_tunnel_cross: 4.0000  →  3.0000
```

等级 4（scale 1.00）降到 3（scale 更低）——这意味着**第一个窗口已关闭、成功率低于降级阈值、
等级被下调、并且缩放被应用到 route 控制器** ✅

**⇒ 这是 §38 那个 host 侧修复的端到端证据**：
- 若没有 §38 的修复，这一步会在窗口关闭时抛 CUDA assert（§36 的 12 迭代 = 288 步 ≈ 300 的吻合）
- 现在它**正常完成了窗口结算并改了等级** ✅
- 而且这正是课程**该做的事**：对失败科目**缓和难度**，而不是让它一直失败 ✅

### 45.2 同相位的其它正向信号

| 指标 | 迭代 20 | 迭代 76 | 判读 |
|---|---|---|---|
| `tunnel_height` | 0.0050 | **0.0214–0.0302** | **↑6×**：策略正在学会下蹲 ✅ |
| `tunnel_clearance` | 0.0000 | −0.0003 … −0.0007 | 开始进入洞区（惩罚项活跃） |
| `tunnel_stall` | −0.0001 | −0.0002 … −0.0008 | **防蹲门禁活跃** ✅（§15） |
| `route_progress` | 0.055 | 0.079 … 0.086 | 缓慢上升 |
| `route_success` | 0.0000 | 0.0000 | 尚未完成（预期） |

**历史对照**：链自己的调参注释记录过
*"the crouch needs crank −0.595844 rad, which a 0.5 rad/unit action CANNOT reach (tanh ≤ 1)
— that is why `Episode_Reward/tunnel_height` stayed **exactly 0 in every run**"*。
现在它是 **0.005 → 0.03** ⇒ **曲柄动作范围（`RM_CRANK_ACTION_SCALE=0.75`）修复生效** ✅

### 45.3 ⚠️ 一个需要记录的数据点：闭环在缓慢逼近那条门禁

```
closure_err_session_max_m: 0.0013（smoke 结束）→ 0.0014 → 0.0018
smoke 门禁 0.002  ⇒  已用 90 %
```

**不影响推进**（smoke 已通过；且 §43.7 确认链的相位 verdict **不读闭环**），
但它**在真实数据上印证了 §39 的判断**：DR 打开后闭环会持续逼近按 DR-off 标定的阈值 ✅
—— `patch_smoke_gate_dr_aware.py` 因此仍然值得应用。

---

## 46. 🔴 过洞路线**在结构上不可能完成** —— 且课程的"降速=变简单"假设在此**恰好相反**

### 46.1 数字（v2 run 的真实配置）

从 v2 run 的 manifest 实测：

| 参数 | 值 |
|---|---|
| `RM_EPISODE_S` | **20.0**（**已验证被显式写入 manifest** ⇒ 不是"没设"） |
| 评测步数（链的 `eval_phase`） | **`--steps 2200`** = **22 s** @100 Hz |
| `tunnel_cross` 路线长度（§19.1） | **2.00 m** |
| 下蹲时的可行速度 | **0.05–0.09 m/s** |

**核算**：

```
走完 2.00 m 需要      22.2 – 40.0 s
episode 内最多走      0.09 × 20 = 1.80 m
                      1.80 m  <  2.00 m        ← 即使全程按下蹲速度上限
```

**⇒ `tunnel_cross/complete_rate` 在结构上不可能变成非零** ✗，与训练多少迭代无关。

### 46.2 代码自己知道这件事——但默认值从未被改

```python
# mod4_task.py:1856-1858
# RM_EPISODE_S: the dog-hole route is short but the crouched robot is slow (~0.06 m/s ...
self.episode_length_s = float(os.environ.get("RM_EPISODE_S", 20.0))
```

注释**写着下蹲只有 ~0.06 m/s**（⇒ 2.0 m 需要 33 s）✅，而默认 **20 s** 一直没动 ✗。
（§19.1 早就记过"`RM_EPISODE_S` 默认 20，**从未被设置**"。）

### 46.3 ⚠️ 两处必须【同时】改，只改一处无效

| 处 | 现值 | 需要 |
|---|---|---|
| `RM_EPISODE_S`（训练时的 episode 长度） | 20 s | **≥ 40 s** |
| 链评测的 `--steps`（评测截断） | **2200**（22 s） | **≥ 4000**（40 s） |

**⇒ 只改 `RM_EPISODE_S` 而评测仍是 2200 步，评测会在 22 s 处截断，照样判不及格** ✗。

### 46.4 🔴 课程在此处是**反作用**的（我 §4 设计的一个缺陷）

我的路线难度课程把等级映射成**速度缩放**（等级越低 ⇒ 速度上限越低 ⇒ "越简单"）。
**对以"距离/时间"为判据的路线，降速恰好让它【更】不可能走完** ✗✗：

```
等级 4（scale 1.00）: 2.0 m @ 0.09 m/s = 22.2 s   ← 已超 20 s
等级 2（scale 更低）: 速度更慢 ⇒ 需要更久 ⇒ 更不可能
```

**实测印证**：tunnel 相位里课程**连续降级 4→3→2**，而 `route_success` **始终为 0** ✗
—— 课程"努力帮忙"却把问题推得更远。

**⇒ 修法（两条都该做）**：
1. **提高 episode 上限**（§46.3 的两处同时）——这是**根因**；
2. **让课程的降速不作用于"长度受限"的路线**：`tunnel_cross` 这种以"到达终点"为判据且
   时间受限的路线，等级应当**只降其他维度**（如洞高/对准要求），**不降速度**；
   或者对这类路线把速度缩放限制在 `≥1.0`（即不降速）。

### 46.5 对本轮 v2 的预期

**tunnel 相位的门禁（`complete_rate ≥ 0.60`）在本次 v2 里不可能通过** ✗ ——
这不是训练不足，而是**两个配置量的乘积不足**。因此：
- 我不应把该相位的 FAIL 解读为"§15 的防蹲门禁无效" ✅（`tunnel_stall < 0` 与 `tunnel_height > 0` 都已实测生效）
- 下一轮 v2（或本链之后）应当**先做 §46.3 的两处修改**，再谈过洞科目

---

## 47. 过洞窗口补丁（§46 的修法）+ 一条关于**验证强度**的教训

### 47.1 `patch_tunnel_episode_and_eval.py`（已写、已验证、**未应用**）

三处协同改动（**只改一处无效**，见 §46.3）：

| 处 | 改动 | 为什么 |
|---|---|---|
| `run_special_phases_v3.sh`（普通 + focus 两处） | `--steps 2200` → `--steps ${RM_EVAL_STEPS:-2200}` | 评测的截断窗口否则会把更长的 episode 切掉 |
| `start_v2_chain.sh` | `RM_EPISODE_S=45`、`RM_EVAL_STEPS=4500` | 2.0 m @ 0.05 m/s = 40 s，留出余量 |
| `mod4_curriculum.py` | **长度受限路线不降速**（`tunnel_cross` 的 speed scale 夹在 ≥1.0） | 课程对"距离/时间受限"路线降速是**反作用**（§46.4） |

**沙箱验证**：`self-check OK: … imports and defines LENGTH_LIMITED_KINDS=('tunnel_cross',)` ✅
`bash -n` 两个 shell ✅ ｜ `import` 成功 ✅ ｜ 夹取代码已在 `_apply_speeds_to_routes` 里 ✅

### 47.2 ⚠️ 教训：这一个补丁的验证强度被迫**连升四级**，每级都抓到上级看不到的问题

| 强度 | 检查 | 结果 |
|---|---|---|
| ① | `--check`（锚点唯一） | **通过** —— 但产物是坏的：常量插在 `from __future__` **之前** ⇒ SyntaxError ✗ |
| ② | `ast.parse`（能解析） | **通过** —— 但常量落在 **docstring 内部**：它只是文本，**从未被定义** ✗ |
| ③ | AST **顶层赋值**检查 | ✅ 抓到了 docstring 那一次 |
| ④ | **真正 import 一次** | ✅ 抓到了 `__future__` 那一次 |

**⇒ 结论（本会话反复出现、这次最尖锐）**：

> **"这个文件能被解析"不等于"这个改动生效了"。**
> ②之所以通过，是因为把一行赋值放进文档字符串里**语法完全合法** ✗；
> ④之所以必要，是因为常量插在 `from __future__` 之前**只有 import 才会报错** ✗。

**⇒ 补丁现在带第 ④ 级自检**（子进程 import + 读取常量），**失败自动回滚备份** ✅。
**这两次失败都不是靠"更仔细地看"发现的，而是靠把检查换成更强的一种** ✅。

---

## 48. ⚠️⚠️ **对 §46 的修正**：过洞**不是结构上不可能** —— 我的推算过于悲观

### 48.1 实测把它推翻了

§46 我断言"`tunnel_cross/complete_rate` **在结构上不可能变成非零**"。tunnel 相位跑到 196/400 时：

```
Episode_Reward/route_success:   0.0000 → 0.0417 → 0.0208 → 0.0174     ← 非零！
Episode_Reward/tunnel_clearance: -0.0001 → +0.0001 → +0.0005          ← 转正，进洞了
Episode_Reward/tunnel_height:    0.0510 → 0.0563 → 0.0580             ← 起点的 12 倍
level_tunnel_cross:              4 → 3 → 2 → 1 → 0                     ← 降到最低
```

**⇒ `route_success` 变成非零了** —— 我的"不可能"是错的 ✗。

### 48.2 我错在哪里

我用的是 **路线自己的下蹲速度区间（0.05–0.09 m/s）** 去算"2.00 m 需要 22–40 s > 20 s episode" ✗。

**但实际策略并不是全程下蹲**：`tunnel_clearance` 只在洞内为负/接近 0，
其余路段机器人可以**全速前进** ⇒ **实际通过时间远短于我算的 22–40 s** ✗。

**⇒ 正确做法**：应当**从实测的通过时间/进度推算**，而不是拿"下蹲速度"当全程速度 ✗。
（`route_progress` 在 196 迭代时已到 0.10 左右，说明单位时间推进量比我估的高。）

### 48.3 修正后的正确结论

| 说法 | 状态 |
|---|---|
| ~~"过洞在结构上不可能完成"~~ | ❌ **错误，已推翻** |
| **"过洞很紧，且当前成功率远低于 0.60 的门禁"** | ✅ **正确**（实测 0.017–0.042） |
| **"课程对长度受限路线降速是反作用的"** | ⚠️ **弱化**：降级期间成功率确实从 0 升到了 0.04，**无法证明降速有害** |
| "episode 20 s 偏紧、评测 2200 步是硬截断" | ✅ **仍成立**（这是可测的配置量，不是推算） |

**⇒ `patch_tunnel_episode_and_eval.py` 仍然值得应用**（把 episode 与评测窗口同时放宽是**纯粹的正向**——
它不会让任何已能完成的路线变差），但它的理由要从
"否则不可能完成"改成"**给紧的路线更多余量**" ✅。

### 48.4 我在这份文档里已经犯了两次"过强结论"，都已在原地修正

| # | 我的过强结论 | 被什么推翻 | 修正处 |
|---|---|---|---|
| 1 | "整条链的全部相位检查失效" | 逐处排查后发现只有 `smoke_verdict` 失效 | §43.7 |
| 2 | "过洞在结构上不可能完成" | 实测 `route_success` 非零 | **§48（此处）** |

**共同点**：两次都是**从一个正确的局部观察，跨到了不该跨的普遍结论** ✗
（第一次从"smoke 门禁失效"跨到"全部门禁失效"；第二次从"按下蹲速度算不完"跨到"不可能完成"）。

**⇒ 可复用的规矩**：**推算只能用来提出假设，结论必须来自实测。**

---

## 49. 🔴🔴 本次 v2 最严重的功能缺陷：**评测用错了策略类 ⇒ 每个相位的评测都失败、报告全部缺失**

### 49.1 症状

tunnel 相位训练正常结束（`model_399.pt`），但报告目录里**只有 `version_check.txt`** ✗，
链的判决随后死于：

```
FileNotFoundError: docs/acceptance_phase_v3_tunnel/eval.json
FileNotFoundError: docs/acceptance_phase_v3_tunnel/eval_focus_tunnel_cross.json
```

而评测**确实跑了**（日志有 "focused single-kind eval (tunnel_cross, 64 env, 2200 steps)"）✗ ——
**失败被 `>>"$LOG" 2>&1 || true` 吞掉了** ✗（与文档早先记录的 `RATE_KEYS` 事故同一种隐藏方式）。

### 49.2 根因（就在日志里）

```
RuntimeError: Error(s) in loading state_dict for MLPModel:
  Unexpected key(s) in state_dict: "encoder.0.weight", ..., "encoder.4.bias"
  size mismatch for mlp.0.weight: copying a param with shape torch.Size([256, 38])
                                  from checkpoint, the shape in current model is torch.Size([256, 175])
```

```python
# eval_terrain_mod4.py:100 —— 用【已弃用】的旧 API，没有 class_name
policy=RslRlPpoActorCriticCfg(init_noise_std=0.3, actor_hidden_dims=[256,128,64], ...)
# ⇒ handle_deprecated_rsl_rl_cfg 把它变成【普通 MLPModel】✗

# train_mod4_ppo.py:209 —— 训练侧用我的编码器类
SEQ_ACTOR_CLASS = ("mod4_sequence_model:LatentEncoderModel" if SEQ_ENCODER else "MLPModel")
```

### 49.3 ✅ 重要的澄清：**训练侧是对的，坏的只是评测侧**

直接读两个 checkpoint 的 state_dict：

| run | `mlp.0.weight` | `encoder.*` 键 |
|---|---|---|
| smoke `2026-09-13_04-47-00` | **(256, 38)** | **6** ✅ |
| tunnel `2026-09-13_05-13-28` | **(256, 38)** | **6** ✅ |

**38 = 35（当前帧）+ 3（latent）** —— **正是设计意图** ✅：
编码器吃 175 维历史 → 3 维 latent，与当前帧拼接 ⇒ MLP 输入 38 ✅

**⇒ 训练完全按预期工作；评测建了 175 维的普通 MLP 去加载它** ✗

### 49.4 这是 §41 那个模式的**第三次**实例，而且代价最大

| # | 消费者 | 它从哪里取配置 | 后果 |
|---|---|---|---|
| §138 | 增益检查 | manifest 的**裸常量名** | 静默什么都不检查 |
| §140 | 验收的 ONNX 导出 | **环境变量** | 跑完 1 小时后 exit 6 |
| **§49** | **评测的策略类** | **写死的旧 API** | **每个相位的报告全部缺失** ✗✗ |

**⇒ 共同规矩（第三次强调）**：
**每一个消费 v2 配置的地方，都必须从 run manifest 取；写死或读环境都会在换调用路径时失效。**

### 49.5 修法

`patch_eval_actor_class.py`（已写、`--check` rc=0、沙箱 `py_compile` 通过、**未应用**）：

```python
_ACTOR_CLASS = "mod4_sequence_model:LatentEncoderModel" if RM_SEQ_ENCODER=="1" else "MLPModel"
actor=RslRlMLPModelCfg(class_name=_ACTOR_CLASS, hidden_dims=[256,128,64], ...,
                       distribution_cfg=...GaussianDistributionCfg(init_std=0.3, std_type="scalar")),
critic=RslRlMLPModelCfg(class_name="MLPModel", hidden_dims=[256,128,64], ...),
```

（编码器自身的维度由 `RM_SEQ_*` 提供，而它们**已经**被 manifest 回放设置 ✅ —— §40）

### 49.6 ✅ 可挽救性：训练没有白费

**不必中断链** ✅：

| 资产 | 状态 |
|---|---|
| 每个相位的 checkpoint | ✅ **都在磁盘上**（`model_249.pt`、`model_399.pt`、…） |
| 训练日志的完整指标 | ✅ 在（`Episode_Reward/*`、`Curriculum/*`，我一直在读） |
| **相位评测报告** | ❌ 缺失，但**可重建** ✅ —— 应用 §49.5 后对每个 checkpoint 重跑评测即可 |

**⇒ 链结束后**：应用 §49.5 → 对每个相位 checkpoint 重跑 `eval_terrain_mod4.py`（普通 + focus）
→ 用 `my_phase_gate.sh` 判定 ⇒ **全部相位结论都能补回来** ✅

---

## 50. ✅ 链运行中**安全地**改了一个文件（本会话首次），并救回 4 个相位的评测

### 50.1 动机

§49 的缺陷让 **每个相位的评测都失败** ✗。但 `eval_terrain_mod4.py` 与
`run_special_phases_v3.sh` 的性质**不同**，这给了一个挽回的机会：

| 判据 | `eval_terrain_mod4.py` | `run_special_phases_v3.sh` |
|---|---|---|
| 在链的 `FROZEN_FILES` 里？ | **不在** ✅ | 在 ✅ |
| 被运行中的 bash 增量读取？ | **不被**（是独立 python 子进程）✅ | **被** ✗ 绝不能改 |
| 每次评测是否重新加载？ | **是**（每个相位一个新进程）✅ | 是，但正在执行的那个不会 |

**⇒ 三条同时成立 ⇒ 安全** ✅

### 50.2 应用与核对（实测）

```
① eval_terrain_mod4.py 在冻结清单里: 0        ✅
② 补丁只改这一个文件:                 是        ✅
③ 应用后 py_compile:                  OK        ✅
④ 冻结文件核对:                       8 一致 / 0 不一致  ⇒ 链不会发现改动 ✅
```

改动（`_ACTOR_CLASS` 从 manifest 选类，见 §49.5）：

```
110: _ACTOR_CLASS = _actor_class_from_manifest()
123:     class_name=_ACTOR_CLASS,
128:     class_name="MLPModel",
```

### 50.3 ⚠️ 并核对了**求值顺序**（§141 同类陷阱）

```
59:  MANIFEST, MANIFEST_PATH = _find_manifest(args.manifest, args.checkpoint)
110: _ACTOR_CLASS = _actor_class_from_manifest()      ← 在 manifest 解析之后 ✅
```

**⇒ 顺序正确** ✅（否则会用错误的类）。用两个真实 v2 manifest 实测：两者都选出
`mod4_sequence_model:LatentEncoderModel` ✅，与训练一致 ✅。

### 50.4 效果

| 相位 | 报告 |
|---|---|
| **tunnel** | ❌ 评测已失败 ⇒ **事后用 `salvage_phase_evals.sh` 补跑** ✅ |
| **terrain / spin / fly / jump** | ✅ **将自动产出**（terrain 的评测约 1 小时后执行，那是修复的第一次真实验证） |

**⇒ 从"5 个相位报告全丢"变成"只剩 1 个要补跑"** ✅

### 50.5 可复用的判据（"能不能在链运行中改这个文件"）

> **① 它不在冻结清单里？ ② 它不是正在被执行的脚本？ ③ 它由独立子进程每次重新加载？**
> **三条同时成立才可改。** 反例：`run_special_phases_v3.sh` 第 ② 条不成立 ⇒ 绝不能改（§121）。

---

## 51. ✅ §49 修复验证成功 + 🔴 v2 的第一份相位数据证实了 DR 的破坏

### 51.1 §49 的修复在真实链里生效

```
docs/acceptance_phase_v3_terrain/eval.json      Sep 13 07:44  ← 新产出 ✅
state_dict 错误总数：2                          ← 与修复前【相同】（都是 tunnel 那两次）⇒ 无新增 ✅
```

**⇒ 剩余相位（spin/fly/jump）将自动产出报告** ✅（tunnel 仍需 `salvage_phase_evals.sh` 补跑）

### 51.2 terrain 相位实测（`model_399.pt`，64 env × 2200 步，DR OFF 评测）

| route | **基线** | **v2（terrain 相位）** | 变化 |
|---|---:|---:|---:|
| **step_up** | **0.750** ✅ | **0.000** | **−0.750** 🔴 |
| **slope_spin** | **0.750**（`spin_deg 367.5°`） | **0.000**（`spin_deg 123.6°`） | **−0.750** 🔴 |
| ramp_up | 0.333 | **0.000** | −0.333 🔴 |
| ramp_down | 1.000 | **1.000** | ±0.000 ✅ |
| step_down | 1.000 | **1.000** | ±0.000 ✅ |
| rough_cross | 0.000 | 0.000 | ±0.000 |
| fly_jump（progress） | 9.85 | **30.73** | **+20.9** ⬆（待 fly 相位检验） |

门禁：**FAIL**（`ramp_up`/`step_up`/`rough_cross` 全 0，bar 0.60）
闭环仍健康：`closure_max 0.00071`、`mimic 0.00169` ✅

### 51.3 🔴 DR 的破坏被第四次、也是最直接地证实

| # | 证据 | 结论 |
|---|---|---|
| 1 | §29/§30：DR 5 种子下 `slope_spin` 0.750→0.25、`step_up` 0.750→0.06 | 预测：DR 打掉两个过门科目 |
| 2 | §162：terrain 课程把 `step_up` 从 4 降到 3 | 独立印证（课程自己发现了） |
| 3 | §163：全部 terrain 科目降到最低 1，成功率仍 ~0 | 加难度也没用 |
| 4 | **§51 本轮实测**：`step_up` **0.750→0.000**、`slope_spin` **0.750→0.000** | **确凿** 🔴 |

**⇒ 且科目相关性再次成立**（§29.0b）：`ramp_down`/`step_down`（简单驾驶类）**完好 1.000** ✅，
只有**后期习得的特殊技能**被完全打掉 ✗。

### 51.4 结论与下一轮的硬性建议

**本次 v2 的配置（完整 DR + 400 迭代 × 1024 env）不足以维持基线能力** ✗。
`step_up` 与 `slope_spin` 从过门直接归零，**这不是训练波动，而是四重一致的证据**。

**下一轮必须二选一（或并用）**：
1. **`V2_MILD_DR=1`**（armature 0.85–1.25、观测延迟 ≤1 步）—— 杠杆**已经做好并验证** ✅
2. **大幅加长训练**（400 迭代不够 —— DR 需要更多样本才能学到鲁棒策略）

**并且 §30.3 的耦合判断被证实**：**第 1 项（5 帧历史 + 编码器）必须与第 2 项（DR）配合** ——
编码器正是让"边缘技能"在观测延迟/扰动下存活的那一环 ✅

---

## 52. ⚠️⚠️ **对 §51 的修正（第三次自我纠正）**：那个对照**不是同口径**

### 52.1 问题

§51 我写"v2 实测 `step_up` 0.750→0.000、`slope_spin` 0.750→0.000 ⇒ **DR 破坏了策略**" ✗。
**但两个数来自不同的训练阶段**：

| | checkpoint | 训练进度 |
|---|---|---|
| 基线（`docs/acceptance_baseline_16295/`） | `2026-09-13_01-17-30_…/model_16295.pt` | **链 1 的最终**（跑完全部 5 个相位）✅ |
| v2（`docs/acceptance_phase_v3_terrain/`） | `2026-09-13_06-22-02_…/model_399.pt` | **v2 的第 2 个相位**（只跑了 smoke + tunnel + terrain）✗ |

**⇒ v2 少跑了 2 个相位，分数更低是【预期】的** ✗ —— 这**不能**证明 DR 破坏了能力 ✗✗

### 52.2 三类证据要分开看（只有第 1 类是同口径的）

| # | 证据 | 是否同口径 | 能证明什么 |
|---|---|---|---|
| **1** | **§29/§30：同一个基线 checkpoint，DR-off vs DR-on 评测** | ✅ **是**（同 ckpt、同评测） | **基线策略不 DR 鲁棒**（`step_up` 0.750→0.06…）✅ |
| 2 | §162/§163：课程把 terrain 科目降级 | ⚠️ 间接 | DR 下训练**进展不顺** ✅，但不等于"能力被破坏" |
| 3 | **§51：v2 第2相位 vs 基线最终** | ❌ **否** | **什么都证明不了** ✗ |

### 52.3 而且"在 DR 下训练会破坏能力"**尚未被任何数据证明**

即使第 1 类证据，测的也是"**DR 关训练出来的**策略**在** DR 评测下" ⇒ 那是**鲁棒性**，不是"DR 训练有害" ✗。
**我必须把这条也撤回** ✗。

### 52.4 修正后的正确表述

| 命题 | 状态 |
|---|---|
| 基线 checkpoint 不 DR 鲁棒 | ✅ **已证实**（§29/§30，同口径） |
| DR 下训练进展不顺（课程反复降级） | ✅ 已观察（§162/§163） |
| ~~v2 的 `step_up`/`slope_spin` 被 DR 打掉~~ | ❌ **撤回**（对照不同口径） |
| ~~在 DR 下训练会破坏已学能力~~ | ❌ **撤回**（无数据支持） |
| **DR 强度是否是瓶颈** | ⏳ **待同口径检验** |

### 52.5 正确的检验方式（只需等链跑完）

**唯一公平的对照**：**v2 的最终 checkpoint** vs **基线的最终 checkpoint**（都是"跑完 5 个相位"）✅。
链结束后用一条命令即可：

```bash
python3 migration/linux/compare_v2_vs_baseline.py --v2 docs/acceptance_v2
```

在那之前**任何"v2 比基线差"的说法都不成立** ✗。（届时 `V2_MILD_DR` 是否值得用，也应由那个对照决定 ✅。）

### 52.6 三次自我纠正的共同教训

| # | 过强结论 | 被什么推翻 |
|---|---|---|
| 1 | §43 "整条链的全部相位检查失效" | 逐处排查：只有 `smoke_verdict` 失效 |
| 2 | §48 "过洞结构上不可能完成" | 实测 `route_success` 非零 |
| 3 | **§51/52 "DR 破坏了策略"** | **对照的两个 checkpoint 训练进度不同** ✗ |

**⇒ 规矩（第三次强调，这次更具体）**：
**在比较两个数字之前，先确认它们是同口径的。**
前两次是"从局部跨到普遍"，这一次是"**用不可比的量做比较**" ✗——
而它之所以看不出来，是因为**两个数字都叫 `step_up complete_rate`** ✗。

---

## 53. ⚠️ 差点骗过我的陷阱：**比较文件时必须核对 provenance，不能只看路径**

### 53.1 现场

§169 我建立"同口径相位对照"后，立刻去读两侧的 `eval_focus_rough_cross.json`：

```python
("chain1 (DR off)", '.../archive_.../acceptance_phase_v3_terrain/eval_focus_rough_cross.json')
("v2     (DR on) ", 'docs/acceptance_phase_v3_terrain/eval_focus_rough_cross.json')
```

输出：

```
chain1 (DR off)  rough_cross  complete=0.000 progress=  244.05  (2026-09-12_21-21-27_mod4_fixed_mixed)
v2     (DR on)   rough_cross  complete=0.000 progress=  244.05  (2026-09-12_21-21-27_mod4_fixed_mixed)
                                            ^^^^ 一模一样          ^^^^ 同一个 checkpoint！
```

**两个"不同路径"下其实是同一个文件** ✗：v2 的 focus 评测**还没跑到** `rough_cross`
（terrain 有 5 个科目，逐个跑，当时在第 1 个 `ramp_up`），所以那个路径上**还是链 1 的旧文件** ✗。

### 53.2 如果没有这两道防线，我会得出完全错误的结论

| 防线 | 作用 |
|---|---|
| **归档**（§131） | 链 1 的原件已在 `docs/archive_.../`，没被 v2 覆盖掉 ✅ |
| **核对 `checkpoint` 字段** | 一眼看出两次读的是同一个 checkpoint（`2026-09-12_21-21-27`）✅ |

**⇒ 缺任一防线，我都会写下"DR 没有影响（244.05 = 244.05）"** ✗ —— 而它是**同一个文件读了两遍** ✗✗

### 53.3 规矩

> **在比较两个数据文件之前，先核对它们的 provenance 字段（这里是 `checkpoint`）。**
> **路径不同不代表来源不同** —— 输出目录复用（§131）会让"新路径"上躺着"旧文件" ✗。
> 这与 §52 的教训是同一条：**§52 是"训练进度不同"，§53 是"文件来源相同"** ——
> 两者都会让比较失效，而**两者的数字看起来都完全正常** ✗。

### 53.4 操作化

`my_phase_gate.sh` / `compare_v2_vs_baseline.py` 都应当（且已经）**打印 checkpoint 路径** ✅；
人的一侧则必须**读那一行**，而不是只看数字 ✗。

---

## 54. 🎯 第一次**同口径**对照（terrain 相位，provenance 已验证）

### 54.1 数据

两侧都是**跑了 3 个相位后的 terrain checkpoint**，同一评测、同一种子：

| | checkpoint | `rough_cross complete` | `rough_cross progress` |
|---|---|---:|---:|
| **链 1（DR 关）** | `2026-09-12_21-21-27`（model_15098） | 0.000 | **244.05** |
| **v2（DR 开）** | `2026-09-13_06-22-02`（model_399） | 0.000 | **48.13** |

（两侧 `checkpoint` 字段均已核对 ✅ —— §53 的陷阱不会重演）

### 54.2 能说什么、不能说什么（严格区分）

| 命题 | 状态 |
|---|---|
| 同一相位下，**v2 的 `rough_cross` progress 只有链 1 的 1/5** | ✅ **已证实**（48.13 vs 244.05） |
| 该科目两侧都**未完成**（complete 0.000） | ✅ 已证实 ⇒ **不存在"退化"** ✗ |
| 这就是 **DR 造成**的 | ❌ **不能断言** —— v2 = DR **+ 编码器 + 奖励截断 + 课程**，四者同时变了 ✗ |
| n=1 科目、1 相位 | ⚠️ 样本极小，不能外推 ✗ |

**⇒ 严格表述**：
> **"v2 的配置在 terrain 相位下，`rough_cross` 的推进量只有链 1 的约 1/5。"** ✅
> 归因到 DR 需要**受控实验**（只改 DR 一项）✗。

### 54.3 接下来会更丰富的同口径对照

链 1 的归档里，**spin / fly / jump 三个相位同时有 `eval.json`（混合）与 focus** ✅
（terrain 只有 focus ✗、tunnel 什么都没有 ✗）⇒ 那三个相位能给出**每个科目**的同口径对照，
包括 **`step_up`、`slope_spin`**（§51 里我错误比较过的那两个 ✅）。

**⇒ 到那时才能对"DR 强度是否是瓶颈"下结论** ✅，也才能决定 `V2_MILD_DR` 是否必要 ✅。

### 54.4 当前 v2 的自主数据（无匹配基准，仅供记录）

| 科目 | v2 complete | v2 progress |
|---|---:|---:|
| `ramp_up`（focus） | 0.031 | 46.78 |
| `step_up`（focus） | 0.000 | 66.34 |

链 1 **没有**这两个科目的 focus ✗ ⇒ **无同口径参照**，不作解读 ✗（§52/§53 的教训）。

---

## 55. 🔴🔴 **第一次有效的同口径对照：spin 相位出现重大退化**（provenance 已验证）

### 55.1 数据（两侧都是**跑完 4 个相位**的 checkpoint；同评测、同种子）

| 科目 | **链 1（DR 关）** | **v2（DR 开）** | delta | 门禁 |
|---|---:|---:|---:|---|
| **slope_spin（focus）** | **0.703** | **0.000** | **−0.703** | 🔴 **REGRESSED below bar** |
| slope_spin（混合） | 0.500 | 0.000 | −0.500 | 🔴 FAIL |
| **run** | **1.000** | **0.400** | **−0.600** | （run 无 bar） |
| ramp_up | 0.222 | 0.000 | −0.222 | FAIL |
| ramp_down | 1.000 | **1.000** | ±0 | ✅ PASS |
| step_down | 1.000 | **1.000** | ±0 | ✅ PASS |
| rough_cross / fly_jump / jump_in_place | 0.000 | 0.000 | ±0 | FAIL |

```
chain1 ckpt=2026-09-12_23-00-03_mod4_fixed_mixed
chain2 ckpt=2026-09-13_08-15-40_mod4_fixed_mixed        ← 不同 ⇒ 对照有效 ✅
```

**陀螺角度**：`spin_deg` **1973.70° → 201.43°**（约 1/10）🔴

### 55.2 这次和 §51 的区别（为什么这次可信）

| | §51（已撤回） | **§55（本次）** |
|---|---|---|
| 对照基础 | v2 第 2 相位 vs 基线**最终** ✗ | **同为第 4 相位** ✅ |
| provenance | 未核对 | **两侧 checkpoint 已核对** ✅ |
| 工具 | 手工读文件 | `compare_phase_matched.py`（**来源相同即拒绝**）✅ |

**⇒ 这次是有效的** ✅ —— 退化是真实的，不是口径问题 ✗。

### 55.3 但仍要注意归因（同一纪律）

v2 = **DR + 编码器 + 奖励截断 + 课程**，四者同时变了 ✗ ⇒
**"这是 DR 造成的"仍然不能断言** ✗，只能说：

> **"v2 的这组配置在同一相位下，把 `slope_spin` 从 0.703 打到 0.000、把 `run` 从 1.000 打到 0.400。"** ✅

### 55.4 这改变了建议

| 原建议 | 新建议 |
|---|---|
| "用 `V2_MILD_DR=1` 或加长训练" | **仍然成立，且更紧迫** ✅：完整 DR 下 4 个相位后，**基线过门的小陀螺归零、`run` 大幅退化** ✗ |
| — | **并且要做受控实验**：只改 DR 一项（其余保持 v2），才能把原因钉死 ✅ |

### 55.5 接下来

**fly 与 jump 相位**会给出更多同口径对照（链 1 的归档里两者都有 `eval.json` + focus ✅），
其中包含 **`step_up`**（§51 里我错误比较过的那个）✅ —— 到那时退化面会完整 ✅。

---

## 56. 受控实验协议（§55 的退化需要归因，这是可执行的方案）

### 56.1 已知与未知

| | |
|---|---|
| **已知**（§55，同口径） | v2 的配置在 spin 相位把 `slope_spin` 0.703→**0.000**、`run` 1.000→**0.400** 🔴 |
| **未知** | 是 **DR**、**编码器**、**奖励截断**、还是**课程**造成的（四者同时变了 ✗） |

### 56.2 最小可信的下一步（一次运行，约 10 小时）

**只改 DR 强度**（其余三项保持 v2 原样）：

```bash
CKPT=logs/isaac_mod4/2026-09-13_01-17-30_mod4_fixed_mixed/model_16295.pt \
V2_MILD_DR=1 RM_ACCEPT_TAG=milddr bash migration/linux/start_v2_chain.sh
```

`V2_MILD_DR=1` 只改**两个 DR 分量**（§167 实测）：
`RM_ARMATURE_MIN/MAX 0.7/1.6 → 0.85/1.25`、`RM_OBS_DELAY_MAX_LAG 2 → 1` ✅
（编码器、奖励截断、课程**全部不动** ✅）

### 56.3 判定规则（在每个相位结束时用同口径对照）

```bash
python3 migration/linux/compare_phase_matched.py \
  --chain1 docs/archive_acceptance_phase_v3_chain1_20260912/acceptance_phase_v3_ \
  --chain2 docs/acceptance_phase_v3_milddr_ \
  --phase <terrain|spin|fly|jump>
```

| 结果 | 结论 |
|---|---|
| mild-DR **仍退化** ⇒ 主因**不是** DR，而是编码器/截断/课程之一 | 下一轮改为**逐项回退**（先关课程、再关截断） |
| mild-DR **基本恢复** ⇒ **DR 强度是主因** ✅ | 把 `V2_MILD_DR` 的默认值写进启动脚本，并作为 v2 的正式配置 |
| mild-DR **部分恢复** | 记下恢复比例，作为 DR 强度的标定依据 |

**⚠️ 必须用 `--phase` 做同相位对照** ✗ —— 与最终 checkpoint 比较是无效的（§52）✗，
且必须让工具核对 `checkpoint`（来源相同即拒绝，§53）✅。

### 56.4 为什么这个协议是充分的

- v2 的配置里**只有四项**变了（DR / 编码器 / 截断 / 课程）✅ ⇒ **最多 2–3 次运行**就能定位 ✅
- 每次运行都能**逐相位**给出同口径对照（工具已就绪 ✅）
- 而且**不需要跑完全部 5 个相位**：**spin 相位（第 4 个）已足以判定** ✅
  （§55 的退化在 spin 相位已完全显现 ✅）⇒ 实际上每次运行**约 6 小时**即可判定 ✅

### 56.5 在此之前不应做的事

| ✗ 不要 | 为什么 |
|---|---|
| 把 v2 的结果当作"DR 有害"的证据 | 四项同时变了，无法归因（§55.3） |
| 用最终 checkpoint 对比中途相位 | 口径不同（§52） |
| 只凭路径读报告 | 可能读到上一条链的旧文件（§53） |

---

## 57. ⚠️ 负面结果：飞坡的 `jump_launch_ready` 奖励**恰好支付 0**（§13 的修复未生效）

### 57.1 实测（fly 相位 76/400）

```
Episode_Reward/jump_launch_ready : 0.0000     ← 我新增的奖励项，一分未付 ✗
Episode_Reward/jump_air          : 0.0000     ← 从未离地
Episode_Reward/jump_land         : 0.0002
Episode_Reward/jump_hard_land    : -0.0013
Curriculum/route_curriculum/level_fly_jump     : 3.0000   （从 4 降级）
Curriculum/route_curriculum/level_jump_in_place: 3.0000
```

### 57.2 这意味着什么

`patch_jump_launch_ready`（§13）的设计是：让奖励**先支付"站上发射台并锁定"**
（`u∈(−0.8, 0.10)`、`z>base+0.10`、接地、对准），从而把"先爬上平台"这一环变成可学的 ✗。

**支付 0.0000 ⇒ 那个条件从未被满足** ✗ ⇒ **该修复在本次运行里没有起作用** ✗。

同时 `jump_air = 0.0000` ⇒ **机器人从未离地** ✅ 与之一致：**没上平台 ⇒ 没起跳 ⇒ 没腾空** ✗。

### 57.3 与基线对照（同科目）

| | 基线（链 1） | v2 |
|---|---|---|
| `fly_jump complete` | 0.000 | 待评测 |
| `fly_jump progress` | 9.85 | **30.73**（terrain 相位时）⬆ |

**⇒ 有迹象表明机器人"更接近"平台**（progress 上升 ✅），**但仍未进入发射状态** ✗。

### 57.4 可能的环节（下一步诊断方向，不在此断言）

1. **条件本身太严**：`u∈(−0.8, 0.10)`、`z>base+0.10`、对准 —— 任一不满足即为 0 ✗
2. **`launched` latch 依赖 `route_commands` 的路径**：机器人在**到达平台之前**就超时/换路线 ✗
3. **课程把 `fly_jump` 降级**（4→3）⇒ 难度更低但**发射条件与难度无关** ✗ ⇒ 降级帮不上 ✗

**⇒ 判定方式（无需新数据）**：等 fly 相位的 focus 评测给出 `air_after_launch_rate` 与
`peak_rise_m` ✅ —— 若两者仍为 0，则**该科目的修复必须重做** ✗（而不是继续调参 ✅）。

---

## 58. ✅ 飞坡修复为何不生效：**它其实是一个"伪装成密集奖励的稀疏奖励"**

### 58.1 交付包的 `launched` 条件（`route_commands.py:78`）

```python
self.launched |= fly & (u > -.8) & (u < .10) & ((p[:,2] - self.base_height) > .10) \
                 & wheel_grounded & (torch.abs(p[:,1] - self.goals[ids,1]) < .40)
```

即**五个条件同时成立**：

| # | 条件 | 含义 |
|---|---|---|
| 1 | `fly` | 该 env 是 fly_jump 路线 |
| 2 | `u ∈ (−0.8, 0.10)` | 处于路线**末段**（发射区） |
| 3 | `p_z − base_height > 0.10` | **底盘比基准高 0.10 m** ⇒ **站在抬高的发射台上** |
| 4 | `wheel_grounded` | 轮子着地 |
| 5 | `|p_y − goal_y| < 0.40` | 横向对准 |

### 58.2 我的 `jump_launch_ready` 在做什么

**它镜像了同一条件**（§13 的设计）✅ —— 也就是说：

> **奖励只在"机器人已经站在发射台上"时支付** ✗

**⇒ 但机器人现在连发射台都到不了** ✗（`jump_launch_ready = 0.0000`、`jump_air = 0.0000`、
`route_success ≈ 0`）⇒ **该奖励对"如何到达平台"这个缺失环节不提供任何梯度** ✗✗

### 58.3 这是一个**伪装成密集奖励的稀疏奖励**

| | |
|---|---|
| 设计意图 | "把先爬上平台这一环变成可学的" ✅ |
| 实际效果 | **只有当那一环已经学会时才支付** ✗ —— 因果倒置 ✗ |
| 与 `jump_air` 的区别 | `jump_air` 支付"离地"✗（同样需要先到平台）；两者**都卡在同一个前置条件上** ✗ |

**⇒ 这解释了为什么 `progress` 上升（route_progress 奖励有效 ✅）而 `launched` 从不触发** ✗。

### 58.4 ⇒ 正确的修法（下一轮，不是调参）

**必须提供【通往平台】的密集梯度**，即把奖励从"在平台上"改成"**在逼近平台**"：

1. **按路线坐标 `u` 支付接近奖励**（越接近发射区 `u→0`，支付越高）✅ —— 这是现成的、可微的、密集的信号 ✅
2. 保留现有条件作为**到达后的加成**（不是唯一来源）✅
3. 并且**不要用 `launched` 去门控 `jump_air`** ✗ —— 那会让两个奖励同时依赖同一个未达成的前置 ✅
   （§13 的 gate 设计在这里是**反效果**的 ✗）

**⇒ 判据**：改完后再看 `jump_launch_ready`/`jump_air` —— 若仍为 0，说明连"接近平台"都没发生，
那问题在**路线可达性**（参照 §46 的窗口/长度核算 ✅）而非奖励形状 ✗。

---

## 59. ⚠️ **对 §58 的限定**：`route_progress` **已经**奖励接近 ⇒ 更可能的瓶颈是**episode 窗口**（§47 的补丁同时修 4 个科目）

### 59.1 §58 说得过头了

§58 我断言"`jump_launch_ready` 是伪装成密集奖励的稀疏奖励，**缺少通往平台的梯度**" ✗。
**但 `route_progress` 奖励本来就在支付"沿路线前进"** ✅ —— 所以**梯度并不缺失** ✗。
（基线把 `fly_jump` 的 progress 从 9.85 提到 v2 的 **30.73** ✅，正是它在起作用 ✅。）

### 59.2 更可能的瓶颈：**20 秒的 episode 装不下 5.80 m 的路线**

| route | 长度 | **20 s 需要** | **45 s 需要** |
|---|---:|---:|---:|
| **fly_jump** | **5.80 m** | **0.290 m/s** | 0.129 m/s |
| run | 3.50 m | 0.175 m/s | 0.078 m/s |
| rough_cross | 3.30 m | 0.165 m/s | 0.073 m/s |
| tunnel_cross | 2.00 m | 0.100 m/s | 0.044 m/s |
| ramp_up / ramp_down | 2.11 m | 0.105 m/s | 0.047 m/s |
| step_up / step_down | 1.30 m | 0.065 m/s | 0.029 m/s |

**⇒ `fly_jump` 在 20 s 内需要【持续 0.290 m/s】** ✗ —— 而它还要**减速、对准、爬上平台、起跳** ✗
⇒ **到达发射台本身就吃掉了全部预算** ✗，这解释了 `jump_launch_ready = 0.0000` ✅

### 59.3 ⇒ 结论：**§47 的补丁（episode 45 s）同时修 4 个科目**

`patch_tunnel_episode_and_eval.py` 的 `RM_EPISODE_S=45` 与 `RM_EVAL_STEPS=4500` 是**全局**的 ✅
（只有"长度受限路线不降速"那一处是按科目夹取的 ✅）⇒ 它把上表第二列换成第三列 ✅：

| 受益科目 | 20 s 需要 | 45 s 需要 | 余量改善 |
|---|---:|---:|---|
| **fly_jump** | 0.290 | 0.129 | **2.2×** ✅ |
| run | 0.175 | 0.078 | 2.2× ✅ |
| rough_cross | 0.165 | 0.073 | 2.3× ✅ |
| tunnel_cross | 0.100 | 0.044 | 2.3× ✅ |

**⇒ 这一个补丁是"性价比最高的修复"** ✅ —— 它同时缓解**四个科目**的紧约束 ✅

### 59.4 修正后的优先级（下一轮）

| 优先级 | 措施 | 理由 |
|---|---|---|
| **1** | **应用 `patch_tunnel_episode_and_eval.py`**（episode 45 s + 评测 4500 步） | 同时放松 4 个科目的长度约束 ✅（§59.2） |
| 2 | `V2_MILD_DR=1`（§56 的受控实验） | 归因 DR（§55 的退化解不了长度问题 ✗） |
| 3 | §58 的"接近奖励" | **降为可选** ⚠️：梯度已存在（`route_progress`）✗ |

### 59.5 这是本会话第四次修正自己的结论

| # | 过强/不准确的结论 | 修正 |
|---|---|---|
| 1 | §43 "全部相位检查失效" | §43.7 只有 `smoke_verdict` |
| 2 | §48 "过洞结构上不可能" | §48 实测成功率非零 |
| 3 | §51 "DR 破坏了策略" | §52 对照不同口径 |
| 4 | **§58 "缺少接近梯度"** | **§59 梯度已由 `route_progress` 提供；瓶颈是 episode 窗口** |

**⇒ 规矩（第四次）**：**在下结论前，先问"这个功能是否已经有别的机制在提供？"** ✗
—— §58 的错误正是**没有先检查已有的奖励项** ✅。

---

## 60. 阶段验收汇报（2026-09-13 10:02，链运行 5h15m）—— 四科目进度

### 60.1 链进度

```
smoke ✅ → tunnel ✅ → terrain ✅ → spin ✅ → fly（进行中 160/400）→ jump（未开始）
错误：0（全程）        还剩约 4 小时
```

### 60.2 四科目实测（全部经 provenance 核对、同相位对照）

| 科目 | 基线（链1，同相位） | **v2** | 判定 |
|---|---:|---:|---|
| **小陀螺** `slope_spin` | **0.703** ✅ | **0.000** | 🔴 **退化 −0.703** |
| **上台阶** `step_up` | 0.000（spin 相位） | **0.500** | ✅ **提升 +0.500**（仍低于 0.60 ✗） |
| **过洞** `tunnel_cross` | 0.000 | 训练中 `route_success` 0→**4%**、`tunnel_height` 0→**0.03** | ⚠️ 有进展但远不够；**评测报告缺失**（§49） |
| **飞坡** `fly_jump` | 0.000 | 相位进行中；`jump_launch_ready` **全程 0** ✗ | ⚠️ 修复未生效（§59 已定位为 episode 窗口） |

其它：`ramp_down`/`step_down` **1.000 保持** ✅ ｜ `run` **1.000→0.400** 🔴 ｜ `rough_cross` 0/0

### 60.3 数据可信性的三点保障（本会话新增）

1. **同相位对照**（不是中途 vs 最终 ✗）——§52
2. **provenance 核对**（两侧 `checkpoint` 不同才比较 ✅）——§53，工具已自动拒绝 2 个无效对照 ✅
3. **门禁独立判定**（链的门禁失效 ⇒ 用 `stage_gate.py` + focus 报告 ✅）——§43

### 60.4 需要用户决策的四件事

| # | 决策 | 建议 |
|---|---|---|
| 1 | 等链跑完（~4h）看 fly/jump，还是现在就起温和 DR 对照 | **建议等** —— jump 相位的 `step_up` 最有信息量 |
| 2 | 温和 DR 对照（`V2_MILD_DR=1`，约 6h） | 与 #1 互斥（单任务）✗ |
| 3 | 应用 **7 份待应用补丁** | 链结束后 `post_v2_chain.sh` 一次执行 ✅ |
| 4 | **增益 2500 vs 契约 60** | 验收会 `exit 8`；需决定改契约值或 `RM_GAIN_PARITY_MAX=0` |

### 60.5 尚不能断言的事（纪律）

| 说法 | 状态 |
|---|---|
| "DR 是退化的原因" | ❌ **不能断言**（v2 同时改了四项）⇒ 需 §56 的受控实验 |
| "tunnel 科目失败" | ❌ 报告缺失，**不能用缺失当失败** ⇒ 需 §49 salvage 补跑 |
| "fly 修复无效" | ✅ 可断言"`jump_launch_ready` 支付为 0"，但**原因**已定位为 episode 窗口（§59）而非奖励形状 |

---

## 61. 🛑 v2 链被**人工终止**（第 182 轮）—— 用户的判断是对的

### 61.1 终止原因（用户决定）

同相位对照（provenance 已核对）显示：

| | complete | spin_deg |
|---|---:|---:|
| **链 1（旧，`model_16295.pt`）** | **0.703** ✅ | **1973.7°** |
| **v2（新）** | **0.000** ✗ | **201.4°** |

**⇒ 新策略在小陀螺上确实归零** ✗ ⇒ 用户决定**立即停链并回退** ✅
终止点：**fly 相位 184/400**（跳过了 fly 剩余 + 整个 jump 相位，约省 4 小时）。

### 61.2 昨天的策略**完好无损**

```
logs/isaac_mod4/2026-09-13_01-17-30_mod4_fixed_mixed/model_16295.pt
sha256 d15aa478778b2985c434106b...   写于 02:07   未被触碰 ✅
成绩：小陀螺 0.750 / 367.5° ✅  上台阶 0.750 ✅  ramp_down/step_down 1.000 ✅
```

### 61.3 🔴 我的三处失误（必须写下来）

| # | 失误 | 应当怎么做 |
|---|---|---|
| **1** | **07:44 就拿到 terrain 相位评测（`slope_spin = 0.000`），却没有停链** ✗ | **立刻停** —— 那时只跑了 3 小时，能省下后面 6 小时 ✗ |
| **2** | 起链前选择**完整 DR**，依据是**推测**（"在 DR 下训练就会学会鲁棒"）✗ | 先用 `V2_MILD_DR=1` 起步，或先用受控实验验证 ✗ |
| **3** | **没有任何"技能保持"检查** —— smoke 只查闭环/mimic ✗ | 每个相位后检查四科目，**退化即停** ✗ |

**⇒ 失误 3 是根因**：我把"能跑起来（smoke 通过 ✅）"当成了"方向正确" ✗，
**而"能跑"与"没退化"是两件不同的事** ✗。

### 61.4 用户的选择（本轮的决策）

| 决策 | 选择 |
|---|---|
| 链 | **立刻停，回退用 `model_16295.pt`** ✅ |
| 下一步方向 | **温和 DR 起步（`V2_MILD_DR=1`）** ✅ |

**⇒ 并且必须补上失误 3 所缺的那一环**：**每相位技能保持门禁**（见 §62）✗→✅
