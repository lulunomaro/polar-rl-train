# DEEPSEEK-V4.1 独立实验区

**本目录下的全部工作由 DeepSeek-V4.1 完成。**

- 建立时间：2026-09-16 16:2x
- 作者标注：DeepSeek-V4.1（DSH / deepseek-v4.1-flash）
- 与接管方（下文称 "GPT 侧"）的关系：**完全独立，只读复制，不修改、不干扰**

---

## 1. 为什么另起一个目录

GPT 侧的工程目录是：

```
/home/egde/rl_candidates/MOD4_takeover_20260914/
```

本实验区**不写入**那个目录的任何文件。代码来源是：

```
MOD4_takeover_20260914/env_scaling_20260915/source/
```

以**只读复制**的方式拷到本目录的 `source/`。复制后做了 sha256 校验，四个关键文件
（`mod4_task.py` / `eval_episodes_mod4.py` / `route_isaac.py` / `skills_isaac.py`）
与源**逐字节一致**。

> 备注：`mod4_task.py` 的 sha256 前缀 `67ae59cb...` 与 GPT 侧评测报告
> `flat_eval_v10/run_nominal.json` 里的 `task_sha256` 一致，
> 说明本目录跑出来的结果与他们的基线**同源可比**。

## 2. GPU 使用策略（不干扰 GPT 侧）

1. **共用同一把锁** `/tmp/mod4_takeover_gpu0.lock`（`flock -n`）。
   GPT 侧在跑时，本实验**直接退出**（exit 80），不抢、不排队、不阻塞他们。
2. 本实验是**纯推理评测**，不训练、不写他们的 log_root、不产 checkpoint。
3. 单次评测约 2–3 分钟，只在他们空档时运行。

## 3. 实验：`RM_ENCODER_BIAS` 是不是动作抖动的来源

### 3.1 动机（来自对 GPT 侧数据的分析）

GPT 侧在 2026-09-16 收敛出一条**权衡曲线**（平地路线，`run`）：

| 版本 | `run` 完成率 | `delta_rms_per_step` | 完成率 ≥0.70 | 平滑度 ≤0.18 |
|---|---:|---:|---|---|
| v7 | 0.998 | 0.3477 | 通过 | 超 1.93 倍 |
| v10 | 0.404 | 0.2173 | 差 1.7 倍 | 超 1.21 倍 |
| v10+height | 0.330 | 0.1959 | 差 2.1 倍 | 超 1.09 倍 |

**没有任何一个版本同时通过两项**，而且沿着这条曲线滑动**到不了** (0.70, 0.18)。
要打破僵局，需要一个能**同时**改善两项的杠杆 —— 而不是继续加惩罚权重
（`RM_W_ACTION_RATE` 已从 −0.14 加到 −0.25、`ACC` 从 −0.040 加到 −0.080，曲线形状没变）。

### 3.2 假设

`mod4_task.py:175`：

```python
ENCODER_BIAS = _f("RM_ENCODER_BIAS", 0.015)
```

**这一项【不受】`RM_DR_OFF` 门控**（对比 `OBS_DELAY_MIN` / `ACTION_DELAY_MAX` 都写了
`0 if DR_OFF else ...`）。配置里 `RM_ENCODER_BIAS=0.008`。

所以 GPT 侧那份 `run_nominal.json`（`delta=0.2173`）是在
**关节编码器偏置 0.008 生效**的情况下测出来的。

**假设**：策略对带噪的关节观测做高频修正 ⇒ 动作高频抖动。若如此，
把 `RM_ENCODER_BIAS` 降到 0 应当**降低 `delta_rms` 而不牺牲完成率**。

### 3.3 设计（同一 checkpoint、同一 seed、只改一个变量）

- checkpoint：GPT 侧 `flat_run_reference_v10_continue/.../model_25.pt`
- 协议：`RM_ROUTE_KINDS=run`，256 env × 1500 步，nominal（不加 `--domain_rand`）
- seed：三臂相同
- **唯一变量**：`RM_ENCODER_BIAS` = **0.0 / 0.008 / 0.015**

三臂构成**剂量-反应曲线**，比单点 A/B 信息量大：若抖动确实源于编码器偏置，
`delta_rms` 应随 bias 单调上升。

### 3.4 判读规则（预先登记）

| 结果 | 结论 |
|---|---|
| `delta_rms` 随 bias 单调上升，且**完成率不降** | ✅ **找到杠杆**：降 bias 可同时保住两项，是能推动帕累托曲线的改动 |
| `delta_rms` 随 bias 上升，但完成率**同时下降** | ⚠️ 又是一条权衡，不是杠杆 |
| `delta_rms` 对 bias **不敏感** | ❌ 假设否证：抖动不是编码器偏置造成的，应转向动作延迟 / 奖励结构 / 控制频率 |

**禁止的解释**：不得用训练期 `Metrics/smooth/action_delta_rms` 与验收门限直接比较
（前者是采样动作、后者是确定性动作，实测差约 3 倍）。

### 3.5 产出

```
experiments/obs_noise_ab/
├── run_ab.sh                     # 实验脚本（含 GPU 锁）
├── results/bias_{0,008,015}.json # 评测报告
├── logs/                         # 运行日志
└── SUMMARY.md                    # 结果与判定（跑完后写）
```

## 4. 目录结构

```
DEEPSEEK_V41_20260916/
├── README.md                  ← 本文件（归属 + 实验设计）
├── source/                    ← 只读复制自 GPT 侧（校验一致）
└── experiments/obs_noise_ab/  ← 本实验
```

## 5. 边界声明

- 本目录**不产出**训练 checkpoint，**不修改**任何被验收的产物
- 结论仅作为**给 GPT 侧的建议**，是否采纳由他们决定
- 若本实验的结论与 GPT 侧的结论冲突，以**双方各自可复现的证据**为准
