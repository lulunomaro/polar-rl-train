# 实验结果：`RM_ENCODER_BIAS` 是否为动作抖动的来源

**执行者：DeepSeek-V4.1**
实验时间：2026-09-16 16:28 – 16:49
工作区：`/home/egde/rl_candidates/DEEPSEEK_V41_20260916/`

---

## 结果一（副产物，但很重要）：`RM_ENCODER_BIAS` 在 nominal 下是**死旋钮**

### 现象

第一轮实验（nominal，DR 关）跑了两个臂：

| bias | `run` 完成率 | `delta_rms` | `2nd_diff_rms` | `closure_max_m` |
|---:|---:|---:|---:|---:|
| 0.0 | 0.4974 | 0.20324 | 0.35244 | 0.000312835 |
| 0.008 | **0.4974** | **0.20324** | **0.35244** | **0.000312835** |

**两臂逐位相同。**

### 根因

我最初的判断是"`ENCODER_BIAS` 不受 `RM_DR_OFF` 门控，所以在 nominal 评测里生效"。**这个判断错了**——我只读了常量的定义：

```python
# mod4_task.py:175
ENCODER_BIAS = _f("RM_ENCODER_BIAS", 0.015)      # ← 定义处确实不门控
```

但**应用它的事件注册被门控了**（`mod4_task.py:1750`）：

```python
if not DR_OFF:      # P2: no actuator / friction / mass / CoM / effort randomisation
    leg_encoder_bias   = EventTerm(func=sample_encoder_bias, mode="reset",
                                   params={"asset_cfg": SceneEntityCfg("robot", joint_names=LEG_ORDER, ...),
                                           "key": "_mod4_leg_bias"})
    wheel_encoder_bias = EventTerm(func=sample_encoder_bias, mode="reset", ...)
```

### 结论

**`RM_DR_OFF=1`（nominal）时，`RM_ENCODER_BIAS` 设任何值都不生效。**

- 对 GPT 侧的含义：任何 **nominal** 评测里，这个旋钮都是无效的；只有在 DR 开的阶段才起作用
- 对本次实验的含义：第一轮是 no-op，结果已归档为 `NOOP_bias_*.json`

### 这条错误也是我自己的老毛病

**看了常量的定义，没看调用处的启用条件。** 这是本会话第 N 次同类错误
（此前的形式包括：字符串搜索用错 API 名、`grep -c || echo 0`、`pgrep -f` 自匹配、
把聚合指标当平地指标、把训练口径当验收口径）。

**可复用的检查**：判断一个旋钮是否生效，必须同时确认
**(a) 常量定义、(b) 事件/项的注册条件、(c) 该项是否被引用**，缺一不可。

---

## 结果二：DR 开时的剂量-反应曲线

修正设计：**加 `--domain_rand`**，其余不变（同 checkpoint、同 seed、256 env × 1500 步、
`RM_ROUTE_KINDS=run`），三臂 `RM_ENCODER_BIAS = 0.0 / 0.008 / 0.015`。

（结果待填）

---

## 方法说明

### 与 GPT 侧数据的关系

**不能把我的绝对数与 GPT 侧的 `flat_eval_v10*` 直接比**，因为口径不同：

| | 我 | GPT 侧 |
|---|---|---|
| `max_episode_length` | **2000** | **1500** |
| `RM_EPISODE_S` | 20（继承 `common.env`） | 12（他们 flat 脚本） |

**所以只在我自己三臂之间做对照**，它们共享全部配置，只差 `RM_ENCODER_BIAS`。

### 不干扰 GPT 侧

- 共用 `/tmp/mod4_takeover_gpu0.lock`，**每臂单独取锁、跑完立刻释放**
  （不是整轮持有，把占用上限从 ~18 分钟压到单臂 ~5 分钟）
- 拿不到锁 / 检测到他们的 Isaac 进程 → **跳过该臂，不等待、不抢**
- 实测有效：第一轮第三臂（`bias=0.015`）在他们的任务启动时被正确跳过
  （`logs/driver.log`: `16:39:49 检测到 Isaac 进程，跳过 bias=0.015`）

### 复现

```bash
cd /home/egde/rl_candidates/DEEPSEEK_V41_20260916/experiments/obs_noise_ab
bash run_ab.sh
```

代码来源：只读复制自 GPT 侧 `env_scaling_20260915/source`，
四个关键文件 sha256 与源一致，且 `mod4_task.py` 的哈希与其评测报告
`task_sha256` 相符（同源可比）。

---

## 结果二（修正后，DR 开）：假设**否证**

### 数据

`model_25.pt`，`RM_ROUTE_KINDS=run`，256 env × 1500 步，同 seed，`--domain_rand`：

| `RM_ENCODER_BIAS` | `run` 完成率 | `delta_rms` | `delta_max` | `2nd_diff_rms` |
|---:|---:|---:|---:|---:|
| **0.0** | 0.6367 | **0.18303** | 5.377 | 0.27772 |
| **0.008** | 0.6579 | **0.18297** | 5.611 | 0.27775 |
| **0.015** | 0.6273 | **0.18587** | 5.930 | 0.28201 |

### 判读（对 §3.4 的预先登记规则）

**命中第三条：`delta_rms` 对 bias 不敏感。**

```
delta_rms 全程跨度 1.6%     ← 噪声级
完成率    无单调趋势（0.637 → 0.658 → 0.627）
delta_max 有单调上升（+10.3%），但它是 max，样本噪声大
```

**⇒ 假设否证：动作抖动（`delta_rms ≈ 0.18`）不是关节编码器偏置造成的。**

### 顺带：DR 门限其实两项都过了

| | 完率率 | `delta_rms` | DR 门限（0.50 / 0.20） |
|---|---:|---:|---|
| 三臂 | 0.627 – 0.658 | 0.183 – 0.186 | **两项都通过** |

（nominal 门限是 0.70 / 0.18，则完成率差 9%、delta 差 1.7%）

### ⚠️ 一个意外发现：完成率对【回合长度】极敏感

```
他们的 nominal 评测：max_episode_length 1500  →  完成率 0.330
我的      DR 评测：  max_episode_length 2000  →  完成率 0.637
```

同一份 `model_25.pt`，**回合从 15 s 放宽到 20 s，完成率从 0.330 涨到 0.637（接近翻倍）**。

**这提示：当前完成率的主要瓶颈可能是【时间不够】，而不是【能力不足】** ——
与 `RM_RUN_SPEED_MAX` 被压到 1.20 直接相关（限速让 3.5 m 的路线跑不完 15 s 的回合）。

**注意**：这条是**观察，不是受控结论** —— 两次运行的 DR 开关也不同。
要坐实需要再跑一臂 `RM_EPISODE_S=15` 作对照（未做）。

### 结论（给 GPT 侧的建议）

1. **`RM_ENCODER_BIAS` 在 nominal 下是死旋钮** —— 不要在 nominal 评测里指望它
2. **在 DR 下它也不显著**（跨度 1.6%）—— **不是抖动的来源，别再往这个方向调**
3. **动作抖动的来源仍未定位**。剩下的候选：动作延迟（`RM_ACTION_DELAY_MS_MAX`，仅 DR 生效）、
   奖励结构（`RM_ROUTE_PROGRESS_SCALE=100`）、控制频率/动作尺度（`wheel_action_scale=10`）、
   或门限 0.18 本身不可达
4. **最值得下一步做的是【回合长度 / 速度上限】的受控 A/B** —— 因为它可能是完成率的真实瓶颈，
   而完成率现在是两个门限里更差的那个（0.637 vs 0.70）
