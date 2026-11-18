# 同构型轮腿机器人“平机身摆腿前扑 (`Level-Chassis Hip-Sweep Forward Leap`)”与直接跳上高台标准后训练配方 (`POST_TRAINING_RECIPE_FORWARD_LEAP.md`)

> **适用对象**：与 `MOD4v3 / HW300N60_R3` 同构型的并联四连杆（含气弹簧蓄能）+ 独立前后髋电机 + 双差速轮毂驱动轮腿机器人。  
> **核心目标**：在冻结基础运动专家 `E0`（如 `c874`，参数与动作漂移严格 `0.0`）的前提下，训练出**全程平机身低俯仰（`0-DR` 腾空 `|pitch| <= 8.7°`、全回合 `|pitch| <= 10.8°`）、100% 前向爆发远跃（单跳 `+0.86 ~ +1.24 m`，零倒退回滚）且能直接腾空飞上 `16 / 20 / 24 cm` 实体高台的纯神经网络专家 `E_jump (obs_35 + hist_420 -> act_6)`**。

---

## 一、 为什么轮腿前向跳扑容易出现 `25°~30°` 大俯仰？（三大物理根因与平机身解耦公式）

`MOD4v3` 拥有独立前后髋关节（`front1_joint` 与 `rear1_joint`）：
- **虚拟腿伸长量**：$\delta = q_{\text{front}} - q_{\text{rear}}$（控制机身离地高度与爆发蹬伸冲量）；
- **虚拟腿摆角（髋均值）**：$\bar{q} = \frac{1}{2}(q_{\text{front}} + q_{\text{rear}})$（控制车轮相对水平机身的前后水平落点，`+\bar{q}` 使车轮向机身**后方**摆动，`-\bar{q}` 使车轮向机身**前方**摆动）。

**前向助推与 Raibert 落足必须 100% 由虚拟腿摆角 $\bar{q}$ 承担，车体机身俯仰角 $\theta_{\text{pitch}}$ 全程目标应锁定为 $0^\circ$！**

### 1. 起跳蹬伸期 (`CROUCH -> PUSH`)：消除高姿加速翘头角动量
- **陷阱**：若在 `PUSH` 伸腿至 `0.40 m` 高姿时猛催车轮加速，地面前向切向力 $F_x$ 乘以高质心臂长 $z_{\text{com}}$ 会产生剧烈抬头角动量（$-F_x z_{\text{com}} < 0$）；反之若 `PUSH` 车轮突然减速，则产生低头栽地力矩。
- **平机身标准配方**：
  1. **低姿蓄力期建立水平动量 (`CROUCH`)**：在 `c_s = 0.64 s`（静止起步）或 `0.44 s`（移动助跑）内保持低重心安全蹲姿 `ct = 0.495 ~ 0.515 rad`（延迟 `0.08~0.15 s` 下蹲确保前导轮 `0.0 N` 零擦地），通过车轮平滑加速 $v_{\text{lunge}} = \max(v_{\text{cmd}}, 1.92 - 0.22\min(0.85, v_{\text{cmd}}))$ 与微小髋后掠 $\Delta\bar{q} = +0.020 v_{\text{lunge}}$ 建立 `vx_takeoff = 1.20 ~ 1.43 m/s`，机身俯仰自然保持在 **`|pitch| <= 5°~6°`**。
  2. **等速配平爆发蹬伸 (`PUSH`)**：车轮速度参考设为等速跟随 `0.94 * body_vx`（消除切向加减速力矩），同时施加精确配平的前后髋偏置：
     $$\Delta\bar{q}_{\text{push}} = -0.326 + 0.085\max(0.95, v_{x,\text{push}})$$
     使离地瞬间净俯仰角速度 $|\omega_{y,\text{takeoff}}| \approx 0$，从源头切断腾空翻转！

### 2. 腾空收腿与落足预置期 (`FLIGHT_TUCK -> LANDING_EXTEND`)：零俯仰目标 + 双轮对称反作用控制
- **平机身标准配方**：
  1. **严格锁定 `pitch_ref = 0.0 rad`**：严禁在空中向机身俯仰环注入非零前倾偏置；
  2. **摆腿与俯仰彻底解耦**：`FLIGHT_TUCK` 快速收腿至 `delta = 0.173 rad`（世界轮底高 `30.4 ~ 32.0 cm`），`LANDING_EXTEND` 仅在虚拟腿摆角上叠加前向落足律：
     $$r_{\text{air}} = \text{MEAN\_GRID}(\bar{\delta}) - 0.55\theta_{\text{pitch}} + 0.16 v_x$$
  3. **双轮对称动量轮 + 四连杆同相俯仰阻尼**：
     $$m_t = 0.5(15.5\theta_{\text{pitch}} + 1.40\omega_y), \quad a_{4:6} = \frac{\bar{\dot{q}}_w + m_t / 0.6}{10.0}, \quad \Delta a_{0:4} = 2.0\,\text{clip}(3.5\theta_{\text{pitch}} + 0.28\omega_y, -0.48, 0.48)$$
     注意必须使用左右轮平均角速度 $\bar{\dot{q}}_w = \frac{1}{2}(\dot{q}_{w,L}+\dot{q}_{w,R})$，防止放大腾空双轮微小转速差引起落台航向偏斜。

### 3. 触台缓冲与巡航恢复期 (`SKYHOOK_ABSORB -> CRUISE_HOLD`)：平滑减速度 + 接地反翘头阻尼
- **陷阱**：倒立摆从 `1.2 m/s` 在 `0.4 s` 内急刹至 `0` 物理上必然要求 $\arctan(a_x/g) \approx 17^\circ$ 后仰角！
- **平机身标准配方**：
  1. 将单次跳跃专家激活门控设为 `JUMP_GATE_DURATION_S = 1.90 s`（`95` 拍 `50 Hz`），触地后用 `1.05 s` 平滑缓降至目标 `v_cmd`（减速度 `< 1.1 m/s²`，物理倾角 `< 6.5°`）；
  2. **接地态反翘头髋阻尼**（注意接地态与腾空态符号相反：车轮锚定地面时，`-\bar{q}` 将机头向下拉平！）：
     $$\Delta\bar{q}_{\text{skyhook}} = \left(1 - \frac{t_{\text{absorb}}}{0.30}\right)\left(0.95\min(0, \theta_{\text{pitch}}) + 0.05\min(0, \omega_y)\right)$$
     将 `24 cm` 高台触地瞬态俯仰从 `15.3°` 直接压低至 **`<= 10.8°`**！

---

## 二、 Stage-2 闭环反作弊低俯仰 PPO 标准奖励与超参数

### 1. 全局刚性低俯仰 + 前向越阶反作弊奖励 (`forward_leap_env.py`)
| 奖励 / 惩罚项 | 数学形式 | 工程作用 |
| :--- | :--- | :--- |
| **全局水平机身密集奖励** | $(4.0\,\Delta t)\cdot\left[0.40\exp(-(\theta/0.08)^2) - 0.15|\omega_y|\right]$ | 全程鼓励机身严格贴近 `0°` 水平且抑制俯仰角速度 |
| **超限俯仰分段重罚** | $-(15.0\,\Delta t)\cdot\left[8.0\,\text{relu}(|\theta|-8^\circ) + 25.0\,\text{relu}(|\theta|-12^\circ)\right]$ | 对超过 `8°` / `12°` 的任何瞬态抬头或低头施加强恢复梯度 |
| **平机身门控跃距×净空奖** | $+9.5 \cdot s_{\text{dx}} \cdot s_{\text{clr}} \cdot \text{pitch\_mult}$ | 若窗口最大俯仰超限则折减完成大奖，防止牺牲姿态换跃距 |
| **拒跳 / 原地跳 / 倒退重罚** | 若 `settled_dx < 0.45 m` 或 `min_vx < -0.05 m/s` 或 `rim < 0.20 m` 扣 **`-18.0`** | 彻底杜绝原地小跳与触地回滚 |
| **上台后滑落零容忍终止** | 承诺上台后若轮底跌破 `h_step - 3.5 cm` 或退回 `x_front - 3.0 cm` 扣 **`-25.0`** 并当场终止 | 杜绝蹭阶滑下骗分 |

### 2. CPU 友好的两阶段训练配置 (`<= 5` 并行环境)
- **线程隔离**：强制设置 `OPENBLAS_NUM_THREADS=1`、`OMP_NUM_THREADS=1`、`torch.set_num_threads(2)`，`ParallelLeapVecEnv(num_envs=5)`（`steps_per_iter = 512`，每轮 `2,560` 步，总计 `36` 轮 = `92,160` 闭环步）。
- **Stage 1 (`stage1_forward_leap_dagger.py`)**：Round 0 (`200` 回合 `beta=1.0`) -> Round 1 (`120` 回合 `beta=0.25`) -> Round 2 (`120` 回合 `beta=0.0` 纯学生闭环采样)，仅将 `max_air_pitch <= 10.0°` 且 `max_episode_pitch <= 12.6°` 且零擦碰的 `0-DR` 帧存入 `trajectories/clean_forward_leap_anchor.pt`。
- **Stage 2 (`ppo_forward_leap_train.py`)**：
  - 第 `1 ~ 8` 轮：仅训练非对称特权 Critic (`16D` 物理特权输入)，Actor 零更新消除冷启动冲击；
  - 第 `9 ~ 36` 轮：`0-DR (9..16) -> 50% DR (17..26) -> 100% Full-DR (27..36)`，`actor_lr = 5.0e-6 ~ 6.0e-6` 余弦退火，`target_kl = 0.010`，`0.35 * symmetry_loss` + `0.38 -> 0.28` 干净低俯仰轨迹锚定；
  - **最优权重硬门控**：仅当验证集 `0-DR` 满足 `pass_rate >= 99%` 且 `max_air_pitch_deg <= 9.9°` 且 `max_episode_pitch_deg <= 12.8°` 时才允许更新 `model_rl_forward_leap_best.pt`。

---

## 三、 一键复训与独立验收命令

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'

# 1. Stage 1：平机身摆腿前扑 3 轮闭环 BC + DAgger（约 10 分钟）
D:\claude2\fangzhen\.venv\Scripts\python.exe stage1_forward_leap_dagger.py

# 2. Stage 2：Critic 预热 + 渐进 DR 低俯仰闭环 PPO（<=5 workers，约 5.5 分钟）
D:\claude2\fangzhen\.venv\Scripts\python.exe ppo_forward_leap_train.py

# 3. Stage 3：零教师独立基准评测（45 0-DR + 45 Full-DR）+ 4 支带实时/峰值俯仰 HUD 的 1x 视频渲染
D:\claude2\fangzhen\.venv\Scripts\python.exe evaluate_forward_leap.py

# 4. 交互式游乐场无头冒烟验收（验证 step20 直跳登顶且 air_pitch <= 10°、ep_pitch <= 13°）
D:\claude2\fangzhen\.venv\Scripts\python.exe play_rl_forward_leap_wasd.py --headless --steps 240 --scene step20
```
