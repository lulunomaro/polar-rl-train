# MOD4v3 同构型双轮足机器人多技能纯神经网络 RL 后训练总配方（`5/5` 优雅上台阶 + 平机身 COD 前向跳扑/直跳高台）

> **适用对象**：与 `MOD4v3 / HW300N60_R3` 同构型的双足并联四连杆（含气弹簧重力补偿）+ 双差速轮毂电机轮腿机器人。  
> **核心保证**：**100% 纯本体感受神经网络推理（仅输入 `obs 35D + obs_history 420D -> action 6D`，运行期零教师、零状态机、零世界坐标 $x/z$ 或台阶距离特权输入）**，且基础全地形运动专家 `E0`（`c874`）严格保持 **`0.0` 参数与动作误差**。

---

## 一、 最终毕业最优权重与实测指标速览

| 专家模块 / 技能 | 最优权重路径 | SHA256（前 16 位） | 核心实测毕业成绩 |
| :--- | :--- | :--- | :--- |
| **`E0` 常规全地形巡航/斜坡/下阶** | [model_full_ppo.pt](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt) | `c874a1afa9adc33c` | `flat60 = 60/60`、双阶 `5/5`、下阶 `5/5`、急停正常（在全部新模型中误差严格 **`0.0`**） |
| **`E1` 单级 `200 mm` 优雅上台阶 + 台顶零速驻车** | [model_rl_stair_best.pt](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_RL_SINGLE200_FULLDR_5OF5_20261118/weights/model_rl_stair_best.pt) | `a1acd1a809fff689` | 原版 `evaluate_student200.py` 五起点 **`5/5 (100%)` 严格 `<= 0.60 m/s` 满分通过**（峰速 `0.481~0.557 m/s`，稳态驻车 `3.30~4.96 s`，`0/5` 滑落）；26 密点越边 `21/26` 且 `0/26` 滑落；`100% Full-DR` 越边 `17/30` |
| **`E1-2Step` 连续二级台阶 (`20+20=40 cm`) 扩展基线** | [model_step000.pt](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_MOE_ROUTE2_CONTINUOUS_2STEP_ANTICHEAT_20261118/weights/model_step000.pt) | `274a134a4289a829` | 一级越边 **`5/5`**，`1.5 m` 踏面柔顺站高衔接二级 `40 cm` 登顶驻车严格 `<= 0.60 m/s` 通过 `2/5`（另 `-15 mm` `0.504 m/s`），`0/5` 滑落 |
| **`E2` 平机身低俯仰 COD 前向跳扑 + 直跳 `16/20/24 cm` 高台** | [model_rl_forward_leap_best.pt](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_RL_FORWARD_LEAP_STEP_JUMP_20261118/weights/model_rl_forward_leap_best.pt) | `79e27807294a225f` | `0-DR` 9 工况 **`45/45 (100%)` 达标且 `45/45` 全 `0.0 N` 零擦碰**；**腾空最大俯仰角压降至 `8.70°`**（全回合 400Hz 最大俯仰 `<= 10.82°`）；静止起步前扑 `+0.996 m`、移动远扑 `+1.238 m`；直跳 `16/20/24 cm` 高台 **`25/25 (100%)` 登顶且 `25/25` 零掉台**；`100% Full-DR` 存活 `40/45`、零掉台 `22/25` |
| **原本位深蹲高跳 / 跨栏专用模型（可选备选）** | [model_rl_best.pt](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_RL_HIGH_MOVING_JUMP_20261118/weights/model_rl_best.pt) | `9bad1458faafa999` | `0-DR` `30/30` 存活、双轮峰值净空均值 `33.63 cm`（三连跳 `35.08 cm`），`20 cm` 实体栏架 `5/5` 飞越 |
| **三专家统一零干扰部署模型 (`E0 + E1 + E2`)** | [model_unified_3expert_moe.pt](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_POST_TRAINING_RECIPES_20261118/weights/model_unified_3expert_moe.pt) | `bed1da66c033293b` | `E0 / E1_stair / E2_forward_leap` 跨专家最大动作误差严格 **`0.0`**；连续跑酷+登阶驻车实测视频 [UNIFIED_ALL_SKILLS_COURSE_1X.mp4](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_POST_TRAINING_RECIPES_20261118/media/UNIFIED_ALL_SKILLS_COURSE_1X.mp4) |

---

## 二、 硬件控制契约与 `35D + 420D -> 6D` 标准接口

后训练同构型机器人时，必须先对齐以下底层控制频率与观测约定（可用 [adapt_new_wheel_leg_robot.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_POST_TRAINING_RECIPES_20261118/scripts/adapt_new_wheel_leg_robot.py) 自动换算新机型的派生阈值）：

- **物理与执行器频率**：`dt = 0.0025 s`（`400 Hz` 物理），腿部关节 PD `100 Hz`（4 分频），轮毂伺服 `400 Hz`，策略推理 `50 Hz`（`0.02 s`），并联四连杆气弹簧 `K_gas = 2000 N/m`（按整机质量比线性缩放）。
- **`35D` 本体观测定义**：
  - `obs[0:3]`：`[v_x_cmd, v_y_cmd, w_z_cmd]`
  - `obs[3]`：`h_cmd * 5.0`（上阶高姿助跑 `0.4091m -> 2.0455`，跳扑基准 `0.28m -> 1.40`，台顶驻车低姿 `0.20m -> 1.00`）
  - `obs[4:7]`：机体系角速度 $\boldsymbol{\omega}_b \times 0.5$
  - `obs[7:10]`：机体系重力投影 $\mathbf{g}_b = \mathbf{R}^\top [0, 0, -1]^\top$
  - `obs[10:16]`：关节角偏差 `[L_front, L_rear, R_front, R_rear, 0, 0]`
  - `obs[16:22]`：关节角速度 $\dot{\mathbf{q}} \times 0.1$
  - `obs[22:28]`：上一控制拍裁剪后实际执行的 `6D` 动作 $\mathbf{a}_{t-1} \in [-6, 6]^6$
  - `obs[28:35]`：专家路由位（常规 `[1,0,0,0,0,0,0]` -> `E0`；轮腿上台阶 `obs[29]=1` -> `E1`；前向跳扑/直跳高台 `obs[30]=1` 持续 `1.90 s` -> `E2`）

---

## 三、 配方 A：轮腿优雅上台阶与台顶零速驻车（[POST_TRAINING_RECIPE_RL_STAIR.md](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_RL_SINGLE200_FULLDR_5OF5_20261118/POST_TRAINING_RECIPE_RL_STAIR.md)）

1. **三子头无梯度冲突结构**：`approach_base`（冻结高姿笔直行走，彻底消除 `cos = -0.718` 平地深蹲抽搐）+ `gate`（纯 `420D` 历史触阶门控）+ `head`（可训练缩腿攀爬头）+ `top_head`（双轮越边切 `obs[3] < 1.5` 后先拉进台面 `20~35 cm` 再执行无倒溜零速驻车）。
2. **反作弊与回放限速铁律**：
   - 上阶后滑落/退回立即扣 **`-25.0`** 并当场终止回合；单轮触顶且 `vx < 0.05 m/s` 零密集奖励；
   - 在 `_reset_idx` 前锁存真实回合峰速，严守 `<= 0.60 m/s` 方可进入在线回放池；
   - 必须在**完整 `10.0s`（`500` 步，无 1 秒提前重置）**回合上对 `vx < -0.01 m/s` 施加反倒溜惩罚，防止慢速后溜掉阶。
3. **四步训练法**：五起点干净低速回放采集 -> 前 `15` 轮 Critic-Only 独立预热 -> **Active-Mask 渐进 `0% -> 25% -> 50% -> 75% -> 100% Full-DR` 闭环 PPO** -> 末层闭环 CEM + 微半径极值精调锁死 `5/5` 满分。

---

## 四、 配方 B：平机身低俯仰 COD 前向跳扑与直跳高台（[POST_TRAINING_RECIPE_FORWARD_LEAP.md](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_RL_FORWARD_LEAP_STEP_JUMP_20261118/POST_TRAINING_RECIPE_FORWARD_LEAP.md)）

1. **彻底解耦“虚拟腿摆角 $\bar{q}$”与“机身俯仰角 $\theta_{\text{pitch}}$”（核心突破）**：
   - **严禁靠压低车头俯仰（`20°~30°`）产生前跳或顺轮落足**！
   - **低重心平姿前冲蓄力（`CROUCH`）**：机身保持 `|pitch| <= 5°` 水平，先在低重心下加速建立 `vx_takeoff = 1.20 ~ 1.43 m/s` 前向动量；
   - **零净俯仰冲量蹬伸（`PUSH`）**：蹬伸瞬间车轮切换为等速跟随（`0.94 * vx`）并配平前后髋偏置，使离地角速度 $|w_y| \approx 0$；
   - **腾空双轮角动量锁平与摆腿落足（`FLIGHT`）**：腾空目标机身俯仰严格锁定 `pitch_ref = 0.0 rad`（利用双轮反作用力矩动量轮阻尼压制空中俯仰 `<= 8.70°`），Raibert 前伸落足完全由虚拟腿髋摆角承担；
   - **平滑缓降与高台自适应吸能（`ABSORB`）**：`1.90s` 门控窗口内纯靠本体 `dq / gyro` 历史自动适应提前 `16 / 20 / 24 cm` 触台吸能并稳停/续行。
2. **两阶段训练法**：
   - **Stage 1（闭环 DAgger 热启动）**：覆盖静止前扑、移动远扑、连续二连扑与 `16/20/24 cm` 三维实体高台（`<body mocap="true">` 确保碰撞精确）采集 `~39,000` 帧干净轨迹训练 `TemporalHistoryEncoder (Conv1d+MLP) + delta_head`。
   - **Stage 2（反作弊 + 刚性低俯仰渐进 DR 闭环 PPO）**：前 `8` 轮 Critic 预热 -> `0% -> 50% -> 100% Full-DR`；全程施加水平机身奖励 `+0.40 * exp(-(pitch/0.08)^2)` 与超限重罚 `-8 * relu(|pitch|-8°) - 25 * relu(|pitch|-12°)`，叠加原地跳/回滚 `-18.0` 重罚与高台滑落 `-25.0` 即刻终止。

---

## 五、 同构型新机器人一键迁移与统一模型合成命令

```powershell
$env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"

# 1. 根据新机器人质量、轮径、腿长自动换算全套控制与反作弊阈值
D:\claude2\fangzhen\.venv\Scripts\python.exe sources\local\MOD4V3_POST_TRAINING_RECIPES_20261118\scripts\adapt_new_wheel_leg_robot.py --spec-json your_robot_spec.json --out adapted_thresholds.json

# 2. 将最优 E0 (常规) + E1 (上台阶) + E2 (平机身前向跳扑/直跳高台) 合成为单文件零干扰 MoE 并渲染全技能连贯跑酷+登阶视频
D:\claude2\fangzhen\.venv\Scripts\python.exe sources\local\MOD4V3_POST_TRAINING_RECIPES_20261118\scripts\unified_all_skills_moe.py

# 3. 启动三专家统一交互式游乐场（WASD 巡航 / SPACE 平机身跳扑与跳上高台 / E 轮腿优雅上台阶 / P 台顶零速驻车）
sources\local\MOD4V3_POST_TRAINING_RECIPES_20261118\Run_MOD4v3_Unified_All_Skills.bat
```
