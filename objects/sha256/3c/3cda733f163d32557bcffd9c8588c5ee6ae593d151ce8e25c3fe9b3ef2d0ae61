# MOD4 Isaac Lab 训练闭环 — 完整交接文档
生成时间：2026-09-13 21:10 CST（目标机时间）
目标机：edge@10.24.4.210，仓库 `/home/egde/fangzhen_linux`，GPU RTX 4090（24 GB）

---

## 0. 一句话现状

**狗洞"过不去"的三个真因已全部定位并修好两个半**：(1) 8 个导轮被刚性焊死 → 已改成 8 个被动转动关节（新植物）；
(2) 腿位置环刚度不足（`leg_kp=60` 蹲姿垂 0.13 rad，包络 273.7 mm）→ 用 `RM_LEG_KP=2500` 解决；
(3) **策略动作范围够不到蹲姿**（crank 需 −0.596 rad，动作上限 ±0.5）→ 已加 `RM_CRANK_ACTION_SCALE=0.75`。
当前正在用修好的植物+动作范围重训 tunnel 阶段（`tunnel_height` 奖励历史首次非 0），
`tunnel_underpass_rate` 仍为 0，即"会蹲了，还没学会穿过去"。

---

## 1. 目标（GOAL）与逐项状态

**最终目标**：在 `/home/egde/fangzhen_linux` 完成 MOD4 修复版串联腿底盘的 Isaac Lab 训练闭环，
交付一份**同时覆盖 RMUC2026 全部路线、可继续做 sim2real 的统一策略检查点**。

| # | 要求 | 现状 | 证据 |
|---|---|---|---|
| 1 | 冻结版本：训练时记录源码/资产 SHA256，评测校验，不一致拒绝 PASS | ✅ 已实现 | `run_special_phases_v3.sh` 冻结 8 文件；`check_run_version.sh`；每 run 有 `run_manifest.json` + `src_sha256` |
| 2 | 成功奖励单元验证（一次 route success ≈ +20） | ⏳ 未跑（需 GPU 窗口） | `isaac/mod4/probe_success_reward.py` 已就绪 |
| 3 | 64 环境 ≥6000 步 smoke | ✅ 已跑两次 | `stage_mixed_fixedplant_20260912_194609.log`：closure session max 0.4 mm、mimic 1.7 mrad、无 NaN/OOM |
| 4 | 狗洞接触判定（导轮允许/底板惩罚/顶板终止） | ✅ 已实现 | `guide_contact` 正则覆盖 8 个独立刚体；不再做 `chassis−guide` 相减 |
| 5 | 8 个导轮做成可单独识别对象 | ✅ 完成 | `incoming/mod4_rolling_20260913/.../robot.usd`（31 bodies / 30 树关节 / 8 roller joints，sha `7b4d8535…`） |
| 6 | 低姿态验证（包络 223–245 mm，洞口 247.2 mm 留余量） | ✅ 探针级通过 | KP=2500 时包络 **246.0 mm**；`probe_tunnel_cross_pi.py` 0.12/0.18 m/s 穿越、顶板 0 接触、主轮 ~35 N |
| 7 | 距离课程 + 最终评测用完整路线/原始洞口 | ✅ 训练用 2.30 m 交付终点 | 评测脚本 pin `RM_TUNNEL_GOAL_X=0`（`final_acceptance_mod4.sh`） |
| 8 | tunnel gate：complete ≥0.60、underpass ≥0.80、roof_hit≈0 | ❌ **未达标** | 最新 tunnel 阶段 underpass=0.0000 |
| 9 | terrain 五路线各 ≥0.60 | ⏳ 待重训+评测 | 旧植物基线：ramp_down/step_down 1.0、rough 0.75、ramp_up/step_up 0.44–0.50 |
| 10 | `success_rate` 改名 + 记录 `route_complete_rate` | ✅ 已实现 | Tensorbord 有 `Metrics/velocity_tracking_success_rate`、`Metrics/route_complete_rate`、`tunnel_underpass_rate`、`spin_360_rate`、`route_air_launched_rate` |
| 11 | 统一策略（平衡采样 + rehearsal，不许平均合并） | ⏳ v3 链设计如此，待跑完 | 每阶段特殊路线 41%/34%/22% + 其余 rehearsal |
| 12 | spin ≥0.60 且 spin_deg ≥360° | ⏳ 旧检查点已达标 | model_11448：complete 0.953 / spin 395.36°（旧植物，需在新植物复测） |
| 13 | fly / jump 真实离地、腾空、落地、失败原因 | ❌ 未达标 | 旧基线 fly 0.0（progress 21.8）、jump 0.0 |
| 14 | 名义全绿后再开 DR | ⏳ 未开 | DR 启动器已就绪并已对齐新植物 |
| 15 | 1024 环境吞吐/稳定 | ⏳ 未测 | `run_dr_stage_mod4.sh` 内含 |
| 16 | 最终交付：checkpoint 链 + manifest + 名义/多种子 DR JSON + 逐路线指标 + TensorBoard + 结论 | ⏳ 部分 | 打包器 `package_rolling_fix.py`、`package_delivery_mod4.py` 已就绪 |

---

## 2. 当前正在运行的东西（接手须知）

| 项 | 值 |
|---|---|
| 链路脚本 | `migration/linux/run_special_phases_v3.sh`（PID 844927，启动于 20:30，`tunnel` 起始阶段，400 迭代/阶段） |
| 训练进程 | `train_mod4_ppo.py --num_envs 512 --additional_iterations 400`（PID 845008） |
| 训练日志 | `logs/isaac_mod4/stage_mixed_fixedplant_20260912_203028.log` |
| 链路日志 | `logs/isaac_mod4/chain_v3d_run.log` + `logs/isaac_mod4/special_phases_v3_*.log` |
| 起点检查点 | `logs/isaac_mod4/2026-09-12_20-15-25_mod4_fixed_mixed/model_14300.pt` |
| 最新检查点 | `logs/isaac_mod4/2026-09-12_20-30-35_mod4_fixed_mixed/model_14550.pt`（每 50 迭代一个） |
| 阶段顺序 | `tunnel → terrain → spin → fly → jump`（smoke 已完成，跳过） |
| 每阶段后 | 版本门禁 `check_run_version.sh` + 平衡评测 64 env×2200 步 + 专项单路线评测 64 env |

**接手方式**：
```bash
tail -f /home/egde/fangzhen_linux/logs/isaac_mod4/chain_v3d_run.log          # 链路
tail -f /home/egde/fangzhen_linux/logs/isaac_mod4/stage_mixed_fixedplant_20260912_203028.log
pgrep -af "train_mod4_ppo"                                                   # 单任务检查
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
```
**要停链**：`kill 844927 845008`（先链脚本后训练）。**不要**在训练运行时改任何 `.py/.usd/.json`——
v3 链每阶段结束都会 `sha256` 复核冻结文件，不一致直接 `exit 4`（这是 GOAL 的硬要求）。

---

## 3. 三个真因与修复（这是本次交接最重要的部分）

### 3.1 导轮被焊死（已修）
交付 USD 把 8 个导轮做在**一个刚体** `/Robot/links/guide_rollers` 上（`/Robot/joints/chassis_guide_rollers_fixed`）。
PhysX 里等价 8 个滑块：低姿态下主轮离地 ~1.8 mm、全部载荷压在滑块上 → 被接触阻力刹停。

修复：`incoming/mod4_rolling_20260913/`（新版本目录，交付件字节未动）
- `chassis_mod4/isaac/robot.usd`：8 个独立刚体 + 8 个被动转动关节（轴=车体 Y，沿用交付 `localRot0/1=(0.5,0.5,0.5,0.5)` 约定），
  导轮质量 0.0025 kg（= 交付 0.02÷8，**派生值非实测**）、实心圆柱惯量、轴承阻尼 `1e-4 N·m·s/rad`（**TO BE CALIBRATED**）
- `chassis_mod4/isaac/import_contract.json`：从新 USD 重算（31 bodies / 30 树关节 / 6 closures / 0 fixed / 34 碰撞体 / 277 视觉 / 6 执行关节）
- 导轮碰撞摩擦 0.9（滚动来自关节，不靠把摩擦改 0）；不做 `chassis_force − guide_force`
- 生成器：`tools/build_rolling_rollers_usd.py`、`tools/make_rolling_contract.py`

### 3.2 腿位置环刚度不足（已修）
交付 PD `leg_kp=60` 在蹲姿重力矩下垂 0.13 rad：

| 指令 hip | 实现 hip | root | CAD 包络 |
|---:|---:|---:|---:|
| +0.4702 (KP=60) | +0.3221 | 0.2067 m | 273.7 mm（比洞口高 26 mm）|
| +0.4702 (KP=1500) | +0.4666 | 0.1796 m | 246.5 mm |
| +0.4702 (KP=2500) | +0.4671 | 0.1791 m | **246.0 mm** |

用户 MuJoCo 验证用的是**带积分**的位置环（KP=320/KD=10/**KI=90**）；纯比例等效需要更高刚度。
旋钮：`RM_LEG_KP / RM_LEG_KD / RM_LEG_KI`（`migration/linux/patch_leg_pi.py`，积分通路已接好、当前 KI=0）。

**旁证**：交付 USD 的闭链几何与 CAD 完全一致——CAD 硬限位关节解下 6/6 spherical closure 残差
`0.00000 m`（`migration/linux/check_usd_closure_consistency.py`）。所以"Isaac 蹲不到 0.178 m"不是模型错。

### 3.3 策略动作范围够不到蹲姿（刚修，最关键）
腿动作 = tanh × `leg_action_scale(0.5 rad)` → crank 通道上限 **−0.5 rad**；而蹲姿需要 **−0.595844 rad**
（验证姿态）/−0.636（机械限位）。后果：**所有训练里 `Episode_Reward/tunnel_height` 精确等于 0.0000**，
策略从未进入蹲姿带——与奖励、迭代数、植物无关。

修复：`migration/linux/patch_leg_action_range.py`
- 新增 `RM_LEG_ACTION_SCALE`（hip，默认 0.5）、`RM_CRANK_ACTION_SCALE`（crank，tunnel 用 **0.75**）
- 新增验证姿态奖励 `tunnel_crouch_pose`（`migration/linux/patch_tunnel_crouch_pose.py`，权重 `RM_CROUCH_POSE_W`）
- **部署影响**：导出的 ONNX 继承该尺度，`train/deploy/contract_rm2025_later.json` 的
  `leg_action_scale/新增 crank_action_scale` 必须同步改成同值，否则真机动作尺度不一致

**效果**：新 tunnel 阶段 `Episode_Reward/tunnel_height` 首次非 0（0.04–0.09 波动），说明策略开始蹲了。

---

## 4. 已测得的科目成绩

**旧植物基线（独立评测，作为下限参考）**

| 科目 | 检查点 | 完成率 | 关键量 |
|---|---|---|---|
| 小陀螺 | model_11448 | **0.953** | spin **395.36°** |
| 下坡 / 下台阶 | model_11897 | 1.00 / 1.00 | — |
| 起伏路 | model_13649 | 0.75 | — |
| 上坡 / 上台阶 | model_11897 / 13649 | 0.44–0.50 | — |
| 狗洞 | model_11149/13649 | **0.00** | 物理不可能（已修） |
| 飞坡 / 原地跳 | model_13649 | 0.00 | fly progress 21.8 |

**新植物探针（真实 PhysX，`RM_LEG_KP=2500`）**

| 项目 | 结果 |
|---|---|
| 低姿态包络 | 246.0 mm（洞口 247.2 mm，静态余量 1.2 mm；用户 MuJoCo 245.634 mm/1.57 mm）|
| 穿越 0.12 m/s | x_max 1.354、顶板接触 0 步、主轮平均 35.5 N、承载时间比 55% |
| 穿越 0.18 m/s | x_max 1.522、顶板 0 接触、主轮 34.7 N、承载 61% |
| 洞内最小净空 | −0.6 ~ −1.0 mm（CAD 皮肤 vs 顶板，训练终止阈值是 −2 mm）|
| 闭链 session max | 0.4 mm（门禁 <2 mm）|
| mimic session max | 1.7 mrad（门禁 <0.01 rad）|

---

## 5. 工具与文件清单

**新版本植物包**：`incoming/mod4_rolling_20260913/`
- `README.md`、`TASK_LIST.md`、`MANIFEST.sha256`、`validation/static_report.json`
- `chassis_mod4/isaac/{robot.usd, import_contract.json, meshes.usdc, robot_cfg.py, scene.usda}`
- `tools/{build_rolling_rollers_usd.py, make_rolling_contract.py, package_rolling_fix.py}`
- ZIP：`/home/egde/MOD4_rolling_idlers_20260913.zip`
  sha256 `56f65c3f84295974982030e11549a523ef153bf8987b0ad273ac933f279f6fd4`

**补丁脚本**（`migration/linux/`，全部 `--check` 可干跑、幂等、自动 `.bak_*` 备份）
- `patch_guide_sensor_regex.py` — `guide_contact` 覆盖 8 个刚体
- `patch_leg_pi.py` — 腿位置环积分 + `RM_LEG_KP/KD/KI`
- `patch_leg_action_range.py` — `RM_LEG_ACTION_SCALE/RM_CRANK_ACTION_SCALE`
- `patch_tunnel_crouch_pose.py` — 验证姿态奖励项
- `patch_usd_override.py` — `RM_MOD4_USD` 支持**文件路径**（旧代码只取目录 + 硬编码 robot.usd）
- `patch_scripts_use_rolling_plant.py` — DR 启动器/最终验收对齐新植物
- `patch_guide_roller_friction.py`、`patch_tunnel_lead_knob.py`、`patch_dr_battery_terrain.py`、`patch_eval_clearance.py`、`patch_stage_gate.py`

**探针**（`isaac/mod4/`）
- `probe_tunnel_cross_pi.py` — 新植物穿越试验（速度、净空、顶板、主轮载荷）
- `probe_crouch_kp.py` — 低姿态刚度扫描（包络 vs KP）
- `probe_crouch_geometry.py` — 蹲姿实现角度 + 最低点 + 接触力分解
- `probe_rolling_plant.py`、`probe_material_check.py`、`probe_tunnel_geometry*.py`、`probe_success_reward.py`

**链路/评测/打包**
- `run_special_phases_v3.sh`（阶段序列器，含冻结哈希、版本门禁、逐路线评测）
- `check_run_version.sh`、`read_phase_eval.py`、`eval_terrain_mod4.py`、`stage_gate.py`
- `final_acceptance_mod4.sh`（名义 + 5 个 DR 种子 + roof 检查 + 版本门禁）
- `run_dr_stage_mod4.sh`、`start_mod4_dr_fixedplant.sh`（1024 环境吞吐 → DR 训练 → 验收）
- `package_rolling_fix.py`、`package_delivery_mod4.py`、`checkpoint_chain.py`

**调参文件**：`migration/linux/tunnel_tuning.env`（v3 链唯一旋钮来源，内容见 §6）

**证据日志**：`docs/probe_crouch_kp*.log`、`docs/probe_crouch_pi.log`、`docs/probe_tunnel_cross_pi.log`、
`docs/probe_crouch_sweep.log`、`docs/tunnel_probe_20260912_181236.txt`（**已作废，方法学错误**）、
`docs/TUNNEL_IDLER_FRICTION_FINDING_20260912.md`、`docs/MOD4_ROLLING_STATUS_20260913.md`

---

## 6. 标准操作流程

### 6.1 当前旋钮（`migration/linux/tunnel_tuning.env`）
```
RM_MOD4_USD=/home/egde/fangzhen_linux/incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot.usd
RM_LEG_KP=2500
RM_LEG_KD=10
RM_LEG_KI=0
RM_LEG_ACTION_SCALE=0.5
RM_CRANK_ACTION_SCALE=0.75
RM_CROUCH_POSE_W=1.0
```
> `run_special_phases_v3.sh` 与 `start_mod4_dr_fixedplant.sh`、`final_acceptance_mod4.sh` 都会 source 这个文件，
> 保证"训练/DR/验收"跑在同一台机器上。

### 6.2 继续训练（从任意阶段）
```bash
cd /home/egde/fangzhen_linux
# 从头： smoke → tunnel → terrain → spin → fly → jump
CKPT=logs/isaac_mod4/<run>/model_<N>.pt
setsid nohup bash migration/linux/run_special_phases_v3.sh $CKPT smoke 400 \
  > logs/isaac_mod4/chain_v3e_run.log 2>&1 < /dev/null &
# 从中间（例：terrain）
setsid nohup bash migration/linux/run_special_phases_v3.sh $CKPT terrain 400 ...
DRY_RUN=1 ...   # 只打印计划与权重分配，不占 GPU
```

### 6.3 单独确认狗洞物理（~6 分钟，占 GPU）
```bash
OMNI_KIT_ACCEPT_EULA=YES RM_MOD4_MAP=rmuc2026 RM_MOD4_TERRAIN=field RM_DR_OFF=1 \
RM_ROUTE_KINDS=tunnel_cross RM_MOD4_USD=$PWD/incoming/mod4_rolling_20260913/chassis_mod4/isaac/robot.usd \
RM_LEG_KP=2500 RM_LEG_KD=10 \
/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python isaac/mod4/probe_tunnel_cross_pi.py \
  --num_envs 4 --speeds 0.12,0.18,0.25
```

### 6.4 验收
```bash
bash migration/linux/final_acceptance_mod4.sh <checkpoint> <tag>    # 名义 + DR 种子 + roof 检查
python3 migration/linux/read_phase_eval.py docs/acceptance_phase_v3_<label>/eval.json
```

### 6.5 打包
```bash
python3 incoming/mod4_rolling_20260913/tools/package_rolling_fix.py     # 植物修复包 + MANIFEST + ZIP
python3 migration/linux/package_delivery_mod4.py <checkpoint> <tag>     # 策略交付包
```

---

## 7. 未完成事项（按优先级）

1. **狗洞穿洞**：会蹲了但 `tunnel_underpass_rate` 仍 0。下一步（已备好工具）：
   - 先看当前 tunnel 阶段结束后的逐路线评测（`docs/acceptance_phase_v3_tunnel/eval.json`）
   - 若仍 0：按用户建议的**五阶段课程**（`tunnel_hold` 稳蹲 → `tunnel_roll` 低速滑行 → `tunnel_approach` 洞前加速 → `tunnel_cross` 完整穿越 → `tunnel_recover` 出洞恢复），
     用 `RM_CROUCH_POSE_W` 提高姿态跟踪权重、把 `RM_TUNNEL_LEAD_M`（现 0.40）调小让蹲姿更晚
   - 若穿过但净空不足：调 `RM_LEG_KP`（2500→3500/4000）或把 `RM_CRANK_ACTION_SCALE` 再放宽
2. **上坡/上台阶**（旧基线 0.44–0.50）：terrain 阶段已把三者采样各提到 20.5%，等新植物结果
3. **飞坡 / 原地跳**（旧基线 0）：需要真实离地/腾空/落地统计；注意 `RM_JUMP_SCRIPT_PROB` 必须为 0（禁止脚本覆盖 PPO 动作）
4. **成功奖励单元验证**：`probe_success_reward.py`（要求实际增量 ≈ +20，而不是 +0.2）
5. **DR 阶段**：名义全绿后 `run_dr_stage_mod4.sh`（1024 环境吞吐 → DR 训练 → 多种子验收），必须报最差样本净空
6. **统一策略**：最后用平衡采样 + rehearsal 跑一轮，产出统一检查点与父链（`checkpoint_chain.py`）
7. **交付**：ONNX 导出 + `sim2real/preflight_deploy.sh` + 逐 episode 评测 JSON + TensorBoard + 结论

---

## 8. 需要用户/硬件决策的项（不解决不得宣称"可实车"）

1. **洞口净高 vs 包络**：真机实测洞口 250 mm（交付地图 247.2 mm），而 CAD 视觉包络最低蹲姿
   245.6 mm（本包姿态）→ 静态余量仅 1.5 mm 量级。需要：顶面降矮 ≥5–10 mm，或复测洞口净高。
2. **轮胎压缩量**：本包用"小幅展开姿态"绕开，但真机低姿态牵引/导轮滚阻/轮胎压缩量仍未实测。
3. **导轮轴承阻尼**：仿真用 1e-4 N·m·s/rad，**无台架数据**，需实测（滑行试验即可）。
4. **动作尺度**：`RM_CRANK_ACTION_SCALE=0.75` 必须同步到部署契约与真机控制器（否则动作幅值不一致）。
5. **电机台架曲线 / 编码器零位**：`leg_motor`/`wheel_motor` 包络与零点校准仍需实测数据。

---

## 9. 成本账（用户关心的卡时）

训练日志 `Time elapsed` 求和：**28.4 卡时**（截至 2026-09-12 20:10），加探针/评测 ~3.5 卡时 ≈ **32 卡时 ≈ ¥64（¥2/h）**。
其中 ~9.6 卡时明确白烧在"旧植物上训狗洞"（那时物理上不可能）。
当前链每阶段 **400 迭代**（原 700），整链预计 ~6 卡时 ≈ ¥12。

---

## 10. 禁忌与已踩过的坑（不要重复）

1. **一次只跑一个训练**；不要在训练运行时改 `.py/.usd/.json`（v3 链会 `exit 4`）。
2. 旧检查点（model_11149/11897/11448 等）与新植物**不同版本**，只能作为 `CROSS_VERSION_BASELINE_ONLY` 迁移基线，
   不得当作新版本通过（`check_run_version.sh` 会拦）。
3. `chassis_force − guide_force` 相减做法**错误**：导轮与底盘已是两个独立刚体，允许同时接触。
4. 不要用"把导轮摩擦改成 0"来替代被动关节；滚动必须来自关节转动。
5. `RM_MOD4_USD` 必须给**文件路径**（patch 之前只取目录且硬编码 `robot.usd`，导致多次 A/B 静默无效）。
6. `probe_tunnel_inertia.py`（旧惯性探针）**方法学错误**（只传送 root、不写腿关节、速度未真正注入），
   其"0.15/0.25 m/s 只滑 9 mm"的结论不得再引用；正确的穿越证据是 `probe_tunnel_cross_pi.py`。
7. `run_special_phases_v3.sh` 的 smoke 判定曾误读启动日志导致误判 FAIL（已修：改为读 `[launch] log=` 指向的 stage 日志）。