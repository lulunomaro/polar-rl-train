# 同构型双轮足机器人 (`MOD4v3` 系列) 纯神经网络 RL 优雅上台阶与台顶驻车后训练标准配方

- **配方归档目录**：`d:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_RL_SINGLE200_FULLDR_5OF5_20261118`
- **毕业最优权重**：`weights/model_rl_stair_best.pt`（`SHA256 = a1acd1a809fff689bf09ff067ad270a64e56b3e0ea7798d73f337ba9549ced16`，`E0` 对 `c874` 误差严格 `0.0`）
- **连续二级台阶 (`20+20=40 cm`) 扩展基线**：`../MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118/weights/model_step000.pt`（`SHA256 = 274a134a4289a829f45888843ce2deac572687cf9deee0b289453da39b510c25`）

---

## 1. 核心架构设计（零运行期状态机 / 零教师 / 零特权输入）

1. **标准观测与控制契约**：
   - 输入：`obs(35) + obs_history(12 × 35 = 420)`（仅本体 IMU、关节位置/角速度、上一拍动作与模式位 `obs[28:35]`；**严禁输入世界坐标 `x/z`、台阶距离或运行期状态机相位**）。
   - 输出：`action(6) ∈ [-6, 6]`（`400 Hz` 物理、`100 Hz` 腿部 PD、`400 Hz` 轮速度/力矩伺服、`50 Hz` 策略推理）。
2. **解耦无冲突三子头 MoE 攀爬专家 (`StairExpert`, `obs[29] > 0.5` 激活)**：
   - **基座保留 (`E0 = c874`)**：`obs[29] <= 0.5` 时直接输出冻结的 `c874` 平地/斜坡/下阶策略，参数与动作漂移严格为 **`0.0`**。
   - **冻结高姿直走头 (`approach_base`)**：触阶前保持 `0.409 m` 笔直站高巡航，彻底根除单 MLP 同时拟合“平地直走”与“触墙收腿”导致的 `cos = -0.718` 梯度冲突、深蹲擦地与左右抽搐（首秒塌腿率 **`0.00%`**）。
   - **纯历史接触门控 (`gate`)**：仅由 `420D` 历史检测导轮/主轮触阶特征（平地误触发率 `< 0.004`），触阶瞬间平滑切换至可训练攀爬头 `head(35 + 16 -> 6)`。
   - **独立台顶拉进与零速驻车头 (`top_head`)**：双轮登顶切低姿指令（`obs[3] < 1.5`）后路由至 `top_head`，先在 `v_cmd > 0` 下向台内拉进 `20~35 cm` 远离阶沿，再在 `v_cmd = 0` 下执行无倒溜零速驻车（末端速度 `|vx| <= 0.009 m/s`）。

---

## 2. 四阶段标准后训练流水线（迁移至同构型新机器人一步到位）

### Stage 0：五起点干净低速回放采集 (`<= 0.55 m/s`)
- 在目标机器人 MJCF/USD 模型上，采集覆盖不同到阶距离偏置（`-60 / -30 / 0 / +30 / +60 mm`）的一次直上、零反弹、整程峰速 `<= 0.55 m/s` 轨迹作为干净锚定回放池（含 `150` 帧永久锁死高姿静站样本），并在 `env.step` 重置前锁存真实回合峰速（封堵 `autoreset` 清零绕过限速门控漏洞）。

### Stage 1：远端 Isaac Sim 大规模并行反作弊预训 (`prepare_and_launch_single200_ppo.py`)
- `100%` 台阶环境聚焦单级台阶，启用**掉阶即扣 `-25.0` 并当场终止回合**（彻底杜绝蹭阶拿分后滑落作弊）、单轮无前进速度（`vx < 0.05 m/s`）零密集奖励、前 `15` 轮仅训 Critic 独立预热，获取具备 `>= 4s` 台顶稳态驻车能力的检查点（如 `model_025m.pt`）。

### Stage 2：目标物理引擎 (`400 Hz` MuJoCo) 全回合渐进 `0-DR -> Full-DR` 闭环 PPO (`stage2_ppo_fulldr_train.py`)
- 消除 PhysX 三角网格与真实轮-阶接触法向差异，并在**完整 `10.0s`（`500` 步，取消 1 秒提前重置！）**回合上训练，加入反倒溜惩罚 `-10.0 * relu(-vx - 0.01)`；
- 采用 **Active-Mask PPO**（仅在 `gate_prob > 0.04` 或 `obs[3] < 1.5` 激活区间计算策略梯度与 `approx_kl`），前 `6` 轮 Critic 预热后按 `0% -> 25% -> 50% -> 75% -> 100% Full-DR`（质量 `±12%`、质心 `±2cm`、摩擦 `[0.65, 1.25]x`、PD `±12%`、力矩 `±10%`、台阶高度 `±5mm`、`0~20ms` 延迟）逐级强化。

### Stage 3：末层闭环 CEM + 微半径极值精调 (`stage3_es_5of5_fulldr.py` -> `lock_5of5_exact.py`)
- 针对非光滑回合极值约束（`max_t ||v(t)|| <= 0.60 m/s`），围绕 `5/5` 越边盆地对攀爬头末层 `mlp.e1.head.6` 执行闭环无梯度 CEM 与微半径精调，避免 Adam 首步符号跳变破坏已收敛起点，一举锁死 **`5/5` (`100%`) 正式满分通过** 与高 `Full-DR` 越边率。

---

## 3. 标准复现命令

```powershell
$env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"
# 1. 闭环渐进 0-DR -> 100% Full-DR PPO
D:\claude2\fangzhen\.venv\Scripts\python.exe -X utf8 stage2_ppo_fulldr_train.py
# 2. 末层闭环 CEM 与微半径锁 5/5 精调
D:\claude2\fangzhen\.venv\Scripts\python.exe -X utf8 stage3_es_5of5_fulldr.py
D:\claude2\fangzhen\.venv\Scripts\python.exe -X utf8 lock_5of5_exact.py
# 3. 独立全套基准评测（原版 evaluate_student200 + 21 密点 + 100% Full-DR + E0 四项回归 + 1x 视频）
D:\claude2\fangzhen\.venv\Scripts\python.exe -X utf8 evaluate_stair_fulldr.py
```
