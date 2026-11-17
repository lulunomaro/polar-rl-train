# MOD4v3 压低姿态蓄力大跳 + 边移动边跳系统报告 (`MOD4V3_HIGH_MOVING_JUMP_20261118`)

## 1. 核心目标与达成概览

在完全隔离的新实验目录 `d:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_HIGH_MOVING_JUMP_20261118` 内，基于当前已采用的综合低俯仰策略 **`c874`**（[model_full_ppo.pt](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/deliveries/MOD4V3_LOW_PITCH_20261116/model_full_ppo.pt)，SHA256 `c874a1afa9adc33c3fa806d098fc135a76d3e9ecdf411d0ca4ab879696b18617`）与原装 **`MOD4v3 / HW300N60_R3`** 物理资产（MJCF SHA256 `77904c001262d53bdb5ec59b270dc24588b7c1aee8c9ba59d8c85074720c8d8f`），设计、优化、量化验证并交付了 **“压低姿态蓄力大跳 + 边移动边连跳”** 四阶段控制系统与 WASD 交互游乐场。

### 相较历史跳跃基线 (`MOD4V3_MOVING_JUMP_AIR_BALANCE_20261114`) 的核心突破
1. **双轮下沿离地净空大幅提升 (`25.87 cm -> 33.23 ~ 34.70 cm` 标准一键大跳，按住 `C` 极限蓄力可达 `35.70 cm`)**：提升幅度达 **`+7.4 ~ +9.8 cm` (`+34%`)**，连续真腾空时间从 `0.33 s` 提升至 **`0.358 ~ 0.388 s`**，COM 跃升幅度达 **`32.32 ~ 34.97 cm`**。
2. **全速域（原地 `0.0`、前进 `0.4 / 0.8 / 1.2 m/s`、倒车 `-0.5 m/s`、以及 `0.8 m/s` 连续三连跳）40/40 空中平衡全通过**：全部 **30 条轨迹 / 40 次腾空** 均满足全腾空区间 `|pitch| <= 10°` 且 `|roll| <= 5°`（最坏俯仰 `9.98°`、`0.8 m/s` 前进大跳仅 `6.18°`、`1.2 m/s` 高速大跳仅 `5.25°`、最坏侧倾仅 `0.93°`）。
3. **落地后 1 秒俯仰回摆大幅削减 + 全程 `0.0 N` 底盘/导轮触地**：通过 **空中世界系 Raibert 落足预置 + 单向天棚阻尼缓冲 (`Unidirectional Skyhook Damper`) + 落地瞬间交还 `c874` 轮腿平衡**，将移动跳跃落地后 1 秒最大俯仰从历史报告的 `29.99°` 降至 **`10.07°` (`1.2 m/s`) / `14.16°` (`0.8 m/s` 三连跳均值) / `16.44°` (`0.8 m/s` 单跳)**，且全部 30 个评测回合导轮接触力峰值 **`0.0 N`**、底盘接触力峰值 **`0.0 N`**、滚动稳定恢复 **`30/30`**。
4. **100% 严守原厂电机/PD/闭链物理合同**：
   - 未修改任何资产、质量、重力、PD 增益或电机包络；所有控制输出均为标准 `[-6.0, 6.0]` 6 维动作，100% 经由原装 `Mod4v3Mujoco._torque`（`dt = 0.0025 s` 400 Hz 物理、`100 Hz` 腿 PD `60/2`、`400 Hz` 轮伺服 `0.6`、`50 Hz` 策略、腿 `40 / 53.333 / 16.755` 与轮 `5.7759 / 28.185 / 55.3557` 直流包络、`2000 N/m` 气弹簧与四连杆闭链）。
   - 四连杆闭链最大误差仅 **`1.9603 mm`**（远低于 `10 mm` 限制，甚至低于严格训练 `2.0 mm` 诊断线）。
   - 新增网络训练预算消耗 **`0 秒`**（`optimizer_updates = 0`），未触碰远端 GPU 或任何既有目录。

---

## 2. 四阶段深蹲大跳 + 移动连跳控制原理 (`high_jump_controller.py`)

源码见 [high_jump_controller.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/high_jump_controller.py)：

1. **阶段 1 — 重力同步稳态深蹲蓄力 (`CROUCH`)**：
   - 保持 `c874` 观测中的 `height_cmd` 平滑恒定（消除观测阶跃引起的策略前窜/后仰），以重力受限斜率（`1.80 rad/s`）将双腿差角平滑压缩至 `crouch_delta = 0.21 + 0.03 * |vx| rad`（机身根高度降至 `0.188 ~ 0.194 m`，高于腹部导轮触地线 `0.178 m` 达 `10 ~ 16 mm`）。
   - 将两侧 `2000 N/m` 气弹簧充分压紧至约 `393 N/侧` 储能，同时完全保留 `c874` 的前后摆角均值 `raw_mean` 与轮速伺服，使机器人在深蹲蓄力期间仍能稳健前进、后退、转向（并支持 **按住 `C` 键持续深蹲瞄准、松开 `C` 键瞬间起跳**）。
2. **阶段 2 — 速度补偿全行程爆发蹬伸 (`PUSH`)**：
   - 确认双轮承重接地（`>= 4` 个 `2.5 ms` 子步）后瞬间释放全行程伸展目标 `1.75089 rad`。
   - 引入速度自适应角动量预偏置 `mean = raw_mean - 0.285 + k_spd * push_vx`，赋予起跳瞬间受控的微正俯仰角动量（约 `+5° ~ +7°`），恰好抵消后续空中收腿与落足前摆产生的反向角冲量，使腾空全过程俯仰对称穿过 `0°`。
3. **阶段 3 — 极速收腿提净空 + 轮腿协同空中平衡 + Raibert 落足预置 (`FLIGHT_TUCK` -> `LANDING_EXTEND`)**：
   - 确认离地后以 `25 ms` 极速收腿至下限 `0.173 rad`，在最高点充分拉高双轮净空至 `34.7 cm`。
   - 全腾空启用轮反作用扭矩（`pitch_kp = 10.0, pitch_kd = 1.1`）+ 双腿共同角反馈（`leg_pitch_kp = 2.6, leg_pitch_kd = 0.21`）+ 左右腿差动横滚反馈（`roll_kp = 0.65, roll_kd = 0.08`）。
   - 下落阶段（`vz <= -0.35 m/s`）结合四连杆中性角查表 `neutral_4bar_mean(delta)` 在世界系执行 Raibert 落足点预置，使触地瞬间车轮恰好位于总质心正下方（消除触地翻仰力矩与轮胎擦地甩头）。
4. **阶段 4 — 单向天棚阻尼落地缓冲 + 无缝连跳交接 (`SKYHOOK_ABSORB`)**：
   - 触地首拍立即将前后摆角 `mean` 与双轮控制 100% 交还 `c874`（绝不在轮胎抓地锁死时强推髋关节），仅在腿长 `delta` 上叠加 **单向天棚阻尼** `skyhook_kd * max(0, -vz)`（仅在下砸 `vz < 0` 时耗散冲击动能，`vz >= 0` 时自动归零不产生弹射反弹）与防触底软保护 `z_guard`，支持落地吸收末段直接无缝触发下一跳实现连续移动多连跳。

---

## 3. 30 回合 / 40 跳名义物理量化评测汇总

完整逐回合原始数据见 [BENCHMARK_RESULTS.json](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/BENCHMARK_RESULTS.json)（每组速度各跑 5 个扰动初始位姿种子，`400 Hz` 原始采样统计）：

| 评测工况 | 存活 / 稳定恢复 | 最低深蹲根高 `z_min` (m) | COM 跃升 `dz` (cm) | **双轮下沿峰值净空 (cm)** | 连续真腾空 (s) | 空中最大 `|pitch|` / `|roll|` (°) | `10°/5°` 达标 | 落地后 1s 最大 `|pitch|` (°) | 导轮 / 底盘接触峰值 (N) | 最大闭链误差 (mm) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **原地大跳 (`0.0 m/s`)** | `5/5` / `5/5` | `0.1880` | `33.02` | **`34.28`** | `0.3725` | `8.52` / `0.64` | `5/5` | `24.34` | `0.0` / `0.0` | `1.381` |
| **低速移动大跳 (`+0.4 m/s`)** | `5/5` / `5/5` | `0.1887` | `33.23` | **`34.57`** | `0.3725` | `7.12` / `0.39` | `5/5` | `21.71` | `0.0` / `0.0` | `1.347` |
| **中速移动大跳 (`+0.8 m/s`)** | `5/5` / `5/5` | `0.1897` | `33.39` | **`34.70`** | `0.3725` | `6.18` / `0.49` | `5/5` | **`16.44`** | `0.0` / `0.0` | `1.440` |
| **高速移动大跳 (`+1.2 m/s`)** | `5/5` / `5/5` | `0.1904` | `33.46` | **`34.39`** | `0.3675` | `5.25` / `0.87` | `5/5` | **`10.07`** | `0.0` / `0.0` | `1.484` |
| **倒车移动大跳 (`-0.5 m/s`)** | `5/5` / `5/5` | `0.1880` | `32.72` | **`33.23`** | `0.3575` | `9.98` / `0.93` | `5/5` | `19.72` | `0.0` / `0.0` | `1.285` |
| **移动连续三连跳 (`3x @ +0.8 m/s`)** | `5/5` / `5/5` | `0.1946` | `32.32` (max `32.96`) | **`33.72`** (`33.25–34.26`) | `0.3633` | `6.36` / `0.49` | **`15/15`** | **`14.16`** | `0.0` / `0.0` | `1.960` |
| **总计 / 全局极值** | **`30/30` / `30/30`** | `0.1880` | `33.46` (按住C达 `34.97`) | **`33.23 – 34.70`** (按住C达 **`35.70`**) | `0.3725` | **`9.98` / `0.93`** | **`40/40`** | `10.07 – 24.34` | **`0.0` / `0.0`** | **`1.960`** |

---

## 4. 交付文件清单与使用方式

全部文件均严格位于 `d:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_HIGH_MOVING_JUMP_20261118`：

- **核心控制器与物理封装**：[high_jump_controller.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/high_jump_controller.py)
- **交互式 WASD + 蓄力大跳游乐场**：[play_high_jump_wasd.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/play_high_jump_wasd.py) 与一键启动脚本 [Run_MOD4v3_High_Jump.bat](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/Run_MOD4v3_High_Jump.bat)
  - 双击 `Run_MOD4v3_High_Jump.bat` 即可打开控制面板 + MuJoCo 3D 追踪视窗：
  - `W/S` 前进后退、`A/D` 转向、`Q/E` 升降站高、`Space` 或 `J` 一键深蹲蓄力大跳（支持原地、高速移动及连续连跳）、**按住 `C` 压低姿态持续蓄力瞄准 + 松开 `C` 爆发大跳**、`1/2/3` 实时切换（平地标尺场 / `14·20·25 cm` 连续跨栏场 / `18·34 cm` 高台地形场）、`R` 复位、`P` 暂停。
  - 无头冒烟验证证据：[headless_player_smoke.json](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/evidence/headless_player_smoke.json)、[headless_hurdles_smoke.json](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/evidence/headless_hurdles_smoke.json)。
- **量化评测与视频渲染器**：[benchmark_and_render.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/benchmark_and_render.py) 及 [BENCHMARK_RESULTS.json](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/BENCHMARK_RESULTS.json)
- **`1.0x` 实时侧向追踪 MP4 视频（`1280x720 @ 50fps`）**：
  - 原地深蹲蓄力大跳（峰值净空 `34.3 cm`）：[STANDING_HIGH_JUMP_1X.mp4](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/media/STANDING_HIGH_JUMP_1X.mp4)
  - `0.80 m/s` 边移动边蓄力大跳（峰值净空 `34.6 cm`）：[MOVING_HIGH_JUMP_08MPS_1X.mp4](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/media/MOVING_HIGH_JUMP_08MPS_1X.mp4)
  - `0.80 m/s` 边移动边连续三连跳（峰值净空 `34.3 cm`）：[MOVING_MULTI_JUMP_1X.mp4](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/media/MOVING_MULTI_JUMP_1X.mp4)
- **端到端 RL 专家蒸馏方案与轨迹数据包**：[RL_DISTILLATION_PLAN.md](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/RL_DISTILLATION_PLAN.md) 与 `9300` 帧 `50 Hz` 示教轨迹库 [high_jump_demos_c874.npz](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/trajectories/high_jump_demos_c874.npz)（SHA256 `512da92a3dcd...`）。
