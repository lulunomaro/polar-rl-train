# v2 起链前清单（一页可执行版）

> 详细论证在 `docs/MOD4_V2_REDESIGN_AUDIT_20260912.md`（§0–§23）。本文件只放**要做的事**与**验收证据**。
> 所有补丁/脚本都已写好并验证过，**真文件零改动**——链退出后你才需要动它们。

---

## 0. 链是否已退出（**必须第一步**）

```bash
pgrep -af "[r]un_special_phases_v3.sh" || echo "chain exited ✅"
pgrep -af "[t]rain_mod4_ppo.py"        || echo "no training ✅"
```
两个都有输出才算退出。**链未退出前不要应用任何补丁**（`FROZEN_FILES` 会 `exit 4`）。

---

## 1. 应用 15 个补丁（顺序有依赖，别打乱）

```bash
cd /home/egde/fangzhen_linux
for P in patch_reward_clip_and_sigma patch_dr_defaults patch_action_delay_substep \
         patch_obs_history_encoder patch_partial_warmstart patch_crouch_pose_kernel \
         patch_tunnel_crouch_gate patch_jump_launch_ready patch_route_curriculum \
         patch_onnx_play_contract patch_acceptance_sim2sim_gate patch_acceptance_gain_parity \
         patch_contract_obs_layout patch_manifest_effective_knobs \
         patch_chain_frozen_plant_paths; do
  python3 migration/linux/$P.py || echo "!!! FAILED: $P"
done
```

**两处强制顺序**（顺序错了会**响亮报错** `ANCHOR FAIL` / `rc=3`，不会静默）：
1. `patch_partial_warmstart` 必须在 `patch_obs_history_encoder` **之后**
2. `patch_tunnel_crouch_gate` 必须在 `patch_crouch_pose_kernel` **之后**（两者改同一个 `return` 行）
3. `patch_chain_frozen_plant_paths` 必须**最后**

---

## 2. 五项验收证据（缺一项就不要起链）

```bash
# ① 每个补丁都幂等（必须列出这 15 个：migration/linux 下有 29 个 patch_*.py，
#    直接通配会把无关的旧补丁也跑一遍）
for P in patch_reward_clip_and_sigma patch_dr_defaults patch_action_delay_substep \
         patch_obs_history_encoder patch_partial_warmstart patch_crouch_pose_kernel \
         patch_tunnel_crouch_gate patch_jump_launch_ready patch_route_curriculum \
         patch_onnx_play_contract patch_acceptance_sim2sim_gate patch_acceptance_gain_parity \
         patch_contract_obs_layout patch_manifest_effective_knobs \
         patch_chain_frozen_plant_paths; do
  python3 migration/linux/$P.py    # 全部应输出 "already patched"
done

# ② 奖励截断表：确认 route_success / termination 被【跳过】而不是被压到 2.5
#    静态检查（不需要 Isaac，直接看补丁里 safe 模式的判据）：
grep -n 'abs(_w) > REWARD_CLIP' migration/linux/patch_reward_clip_and_sigma.py
#    运行期证据（起链后在日志里 grep 这两行；格式已与补丁源码逐字核对过）：
#      grep '\[reward-clip\] mode=' <log>   →  [reward-clip] mode=safe clip=2.50 clipped=NN skipped=NN
#      grep 'SKIPPED (|weight|' <log>       →  每个被跳过的项一行，必须包含：
#            SKIPPED (|weight| 20 > 2.5): route_success
#            SKIPPED (|weight| -20 > 2.5): termination
#    若 route_success 出现在 clipped 一侧而非 skipped，说明模式配错：成功奖励被压成 0.025。
#    注意：不要用 `python3 -c "import isaac.mod4.mod4_task"` 去验证——那个导入需要 Isaac/GPU。

# ③ 课程窗口与 env 数配对（§22/§23：两者必须同时满足）
grep -E "^export RM_ROUTE_CURRICULUM|^export RM_CURR|^ENVS=|^export RM_SEQ|^export RM_JUMP" \
  migration/linux/start_v2_chain.sh

# ④ sim2sim 产物门禁（不需 GPU）
third_party/rc_mjlab/.venv/bin/python sim2sim_mod4/check_sim2sim_mod4.py \
  --onnx <导出的.onnx>     # 期望 RESULT: SIM2SIM MOD4 PASS

# ⑤ 启动脚本自检（旋钮名真的被代码读取）
DRY=1 CKPT=<某个.pt> bash migration/linux/start_v2_chain.sh
#    期望: [v2] verified: all 19 knobs are read by isaac/mod4
```

---

## 3. 先单跑一次 smoke（**§19 的教训**）

本次链是带 `from_phase=tunnel` 启动的，**smoke 从未跑过**；跳过它的依据只是一个探针的
0.002035 m，而**评测实测闭环只有 0.00056–0.00085 m**（阈值 0.002）。

```bash
CKPT=<checkpoint> SMOKE=1 PHASES="smoke" bash migration/linux/run_special_phases_v3.sh "$CKPT" smoke 1
```
- **过了** ⇒ `start_v2_chain.sh` 用 `FROM=smoke`（多一层体检）
- **没过** ⇒ 保持 `FROM=tunnel`，并把失败值记进报告

---

## 4. 起 v2

```bash
CKPT=<最新checkpoint> bash migration/linux/start_v2_chain.sh      # ENVS=1024, FROM=tunnel, ITERS=400
```
脚本会：校验 19 个旋钮名 → 检查无并发训练 → 打印配置 → 调链。
`RM_SEQ_ENCODER=1`（编码器）**会让严格热启动失效**，脚本已同时打开 `RM_PARTIAL_WARMSTART=1`（§9.0）。

---

## 5. 起链后 30 分钟要看的四个数

| 看什么 | 期望 | 不对时的含义 |
|---|---|---|
| `[reward-clip] … clipped=NN skipped=NN` | skipped ≈ 9（高权重技能项） | 若 `route_success` 在 clipped 里 ⇒ 模式配错，成功奖励被压成 0.025 |
| `Curriculum/route_curriculum/attempts_<kind>` | ≥ 40（低配额科目 ≈49） | **长期 < 40 ⇒ 被样本门槛卡死**，降低 `RM_CURR_MIN_ATTEMPTS`，别干等（§23） |
| `Curriculum/route_curriculum/level_rough_cross` | 应在几十个迭代内从 4 下降 | 不动 ⇒ 看上一行；下降 ⇒ §21 的限速课程生效 |
| `Metrics/route_air_launched_rate` | 有非零才算飞坡在学 | 若仍恒 0 而 `jump_air` 在付 ⇒ `jump_launch_ready` 没进奖励表（§13） |

---

## 5.5 ⚠️ "打开 DR"在代码里**实际意味着什么**（与清单写的不同）

你清单第 2 项写的是"Kp/Kd ±10%、力矩 ±10%、动作延迟 0–5 ms"。而 `RM_DR_OFF=0` 时
`mod4_task.py:158-172` 实际同时打开了**七类**扰动：

| 项 | 实际默认 | 清单是否提到 |
|---|---|---|
| `EFFORT_LEG` / `EFFORT_WHEEL`（力矩上限缩放） | ×0.75–1.25 / ×0.90–1.10 | ✅ |
| `EFFORT_NOISE` / `_WHEEL`（力矩噪声） | ±3% / ±2% | ✅ |
| `ACTION_DELAY` | 控制步 0–2（**0–20 ms**）；**打上 `patch_action_delay_substep` 后由 ms 模式取代 → 0–5 ms** | ⚠️ 清单写 0–5 ms |
| **`OBS_DELAY`**（观测延迟） | **1–2 控制步 = 10–20 ms**，`HOLD_PROB` 0.75 | ❌ **没提** |
| **`ARMATURE_SCALE`**（转子惯量） | **×0.7–1.6** | ❌ 没提 |
| `LEG_FRICTION_MAX` / `WHEEL_FRICTION_MAX` | 0.10 / 0.02 | ❌ 没提 |
| **`ENCODER_BIAS`**（关节零位偏置） | 0.015 rad | ❌ 没提 |

**两点直接影响你的决策：**

1. **`OBS_DELAY` 10–20 ms 是清单没提、但很可能最伤的一项** —— 对**单帧观测**的策略，
   它等于"永远看过期的状态"。而 **`RM_SEQ_ENCODER=1` 的 5 帧历史正是应对它的机制**，
   所以 **第 1 项与第 2 项要一起上**（详见审计 §30.3）。若只开 DR 不加历史，难度会显著更高。
2. **`ARMATURE_SCALE 0.7–1.6` 幅度很大**（±40%），`EFFORT_LEG 0.75–1.25` 也比"±10%"宽。
   若想先从温和的 DR 起步，这三个旋钮都可调：
   `RM_EFFORT_LEG_MIN/MAX`、`RM_OBS_DELAY_MIN_LAG/MAX_LAG`、`RM_ACTION_DELAY_MS_MIN/MAX`。

**参照数据（本次验收，`docs/acceptance_baseline_16295/`）**：DR 关训练出来的 checkpoint，
在 DR 开时 小陀螺 **0.75 → 0.25**（2 种子均值）、上台阶 **0.75 → 0.06**，都远低于 0.60 的 bar。
⚠️ 这**不代表 v2 不该开 DR**——它测的是"没练过 DR 的旧 checkpoint"；它的作用是**量化 v2 必须改进多少**。

## 6. 待你拍板的四件事（不定也能跑，但会影响结果解释）

1. **第 4 项课程路径**：A 程序化重建 15 条路线 / **B 任务级（已实现）** / C 等 CAD 源
2. **腿环增益**：训练 2500 / 契约 60 / 复旦实机 6–15（§11.2）。
   选契约值时 `patch_acceptance_gain_parity` 会放行；选 2500 时它会在验收时 **exit 8**
   （可用 `RM_GAIN_PARITY_MAX=0` 降级为告警，但**要求把原因写进报告**）。
   它读 `dirname($CKPT)/run_manifest.json` 的 `effective` 块——manifest **与 checkpoint 同目录**，
   且训练刚开始就写好（实测：00:09:38 写 manifest，00:10:02 出第一个 checkpoint）。
   ⚠️ 若指向一个**被复制出来**的 checkpoint（如拷进 `docs/acceptance_*/`），
   它会报 `CANNOT COMPARE`（rc=0，不拦人）——要拿真实判定请指向**原 run 目录**里的 checkpoint。
   ⚠️ 也注意：**补丁之前**产出的 run 没有 `effective` 块（实测本链所有 run 都是），
   所以这条检查只在 v2 起的 run 上才有意义。
3. **奖励截断**：默认 `safe`（保护 `route_success`/`termination`）vs `all`（照抄参考，但会诱导早死）
4. **过洞的 episode**：混合相位是否把 `RM_EPISODE_S` 从 20 提到 ≥45（§19）。
   **建议：不提**，只把过洞交给 `run_tunnel_course.sh`（每阶段自带 12/20/30/50/50 s）

---

## 7. 已知未完成项（不影响起链，但别当成已完成）

- **sim2sim 的 rollout 半边**：产物半边已 PASS（rc=0）；行为半边需要"同轴↔分离轴"的 2→2 关节映射。
  已测定：两机构**连杆长度吻合 1.7–4%**（是重新参数化，不是两台机器人），
  但映射是**非线性的**（线性拟合 rmse 0.32/0.39 rad 不成立）⇒ 用**匹配表 + 数值雅可比**，
  不要指望一个常数偏置。工具：`sim2sim_mod4/fit_joint_map.py`（已含参考系对齐与可辨识性诊断）。
- **本机没有** `MOD4_247p2_tunnel_sim_20260912`（全盘零命中）；`/home/egde/*.zip` 只有
  `MOD4_RL_rewards_20260912.zip` 与 `MOD4_rolling_idlers_20260913.zip`。
- **`MOD4_RL_rewards_20260912` 未被使用**：其代码是同血脉的早期快照（`mod4_task.py` 17:56 vs 线上 20:30），
  自称的 9 项修复线上**全部已有**，且线上多出 `CRANK_ACTION_SCALE`、`RM_LEG_KP`；
  它自带的 USD 是**导轮焊死的交付版**（与线上滚动版冲突）。唯一值得拿的是**五阶段狗洞课程**
  ——已落成 `run_tunnel_course.sh`。
