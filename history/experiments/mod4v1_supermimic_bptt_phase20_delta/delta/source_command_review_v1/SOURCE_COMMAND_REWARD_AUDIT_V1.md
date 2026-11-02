# MOD4v1 command / observation / reward 源码审计 V1

## 结论与证据等级

- 当前源码存在足以优先检查的 **command tracking / actor deployment contract / imagined observation** 问题；奖励公式与监督结构可作为后续独立消融。此结论来自源码和解析反例，**不是 native 改善、恢复、通过率或 getter live 错误的实验证明**。
- 本专项只在新目录写候选、公式测试、差异和文档；原 runtime、旧封版 core、在跑 E0/E2 全部保持原样。没有 SSH、SDK/App、GPU、选中 PT、旧 rawJSONL、C/GO/锁、Git 或实际训练操作。
- 本地 stdlib：**37/37 PASS**；Torch 本地不存在，未安装、未导入。相邻 CPU Torch 脚本的 22 个软件/autograd 测试交父代理在全新 CPU 用途 root 执行。父代理的结果另为 receipt，本文不预填通过。
- 现有 measurement review 明示 runtime UNKNOWN；本审计继续保留 backend 类/方法与 SHA、getter timestamp/freshness、actor/COM 点及 frame、运行中 command binding、native pass 全为未知。历史 manifest、版本字符串和源文件标题均不覆盖这一限制。
- 候选是 **source-only / not train-ready**：strict 默认在缺少真实 command/sensor 时钟 receipt 时抛 `UnknownCommandEvolution`。合成 oracle 只证明机制，身份仍是 SYNTHETIC。

## 1. P0：原 residual 使用仿真特权数据，不等于可部署 raw35 策略

当前桥的 `obs = invariant_features(state) + previous_action + ALL context`，actor raw35 teacher slice 起点为 79，完整 observation 为 `79 + context_dim`。虽然 teacher 只读 raw35 且冻结，residual 仍读真实状态、完整 context 中的 mass/gain/COM/PD/gas/spring、队列、接触等字段；真实噪声/时延并未约束这一绕路。

证据：[原桥](../source_runtime/native_supermimic_bridge.py#L28-L81)、[原 worker](../source_runtime/worker_supermimic_bptt.py#L43-L66)。

新 [Raw35ActorMDP](command_tracking_torch_candidate_v1.py#L164-L239) 的 real observation 是 `context[..., :35]` 的 identity slice，goal 仅该前缀的 3 个 command 值，history 仍为原长度。teacher/residual 都只接触 raw35 history/current command。不向 actor 加验收 UID、terrain 标签、真实 DR 参数或 WM 隐状态。WM、aux、critic 可保持原有 privileged supervision；它们和 actor 输入边界独立。

### 强制 migration 条件

- 旧 `79+C` residual/normalizer/optimizer 与新 35-D actor 输入 shape 不兼容；不切旧权重、切 Adam 动量或拼旧缓冲来冒充完整 resume。
- 该候选的 extension schema 改为 `mod4v1.ctx_task_reward.command_candidate.v1`；原 load contract 的相等检查保持原样，旧 fullcheck 不应穿过。
- 若父代理选 fresh 冻结 teacher + fresh raw35 residual/normalizer/optimizer：新 candidate native BPTT 计数从 **0** 开始；旧 baseline 的历史计数另存、不相加。这里没有打开或迁移任何 teacher PT。
- 新窗口还需独立记录 teacher artifact identity、source/config SHA、fresh/reset-resume 语义与各计数，不能把 SYNTHETIC 步算作 native 训练。

## 2. E2 命令不是一般 Vcos / Vsin 投影

实际 source 的 moving reference 为：

```text
vx_body = clamp(2 * V * cos(heading - fixed_world_direction), -body_limit, body_limit)
vy_body = 0
wz_body = signed_yaw
```

证据：[E2 dynamic write](../discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/e2_directional_spin_runtime_v1.py#L89-L104)、[实际数学函数](../discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/spin_translation_math.py#L12-L23)。保留原 2V 系数和 vy=0；完整理想转一圈时才有平均 along-world progress V，绝非每个时刻的固定二维世界速度。

原 [worker mask](../source_runtime/worker_supermimic_bptt.py#L57-L60) 把 raw `[:4]` 及 command metadata delta mask 为 0；原 [projection](../source_runtime/native_supermimic_bridge.py#L64-L66) 只更新 wheel-position zero / last_action。故 H16 中 command held，不随 imagined yaw 改变。源码自己也承认这是外生命令近似。

### 定量反例（纯解析）

H=16，dt=.02，yaw=4 rad/s：总 yaw 1.28 rad = 73.3385977767°。V=.5 时 BODY vx 振幅 1 m/s。

- 任意初始相位最大 held-error：`4V*sin(1.28/2) = 1.1943908827247842 m/s`。
- heading0=axis=0：初值 vx=1，末值 vx=.2867152096319555，误差 .7132847903680445。

[stdlib receipt](TEST_RESULTS_STDLIB_V1.json) 中反例已测试。它说明 held 近似不必然很小，不说明实际控制器已出现该轨迹或已改善。

### transition / resample 时钟

`_update_command()` 先写 dynamic，再 `phase_elapsed += .02`。因此最终观测时记录的 phase_elapsed 是 **下一次 write 的相位**；第一次 imagined next write 应使用该值，不再先加一步。源 profile 是 0→ramp→hold→brake→stop→reverse→hold→brake→stop 的原 12 秒 piecewise，不缩任何段。

SDK command term 先 `time_left -= dt`，`<=0` 自然重采样，再 `_update_command()`。当前桥把 time_left 编码成原秒值的 `.01`，判断 H16 边界前须反解。跨 resample/reset/manual command mutation 的未来若缺原 RNG/state 或明确 tape，标记 unknown；不丢掉这些窗口伪造覆盖率、不缩原命令域。

[SourceCommandSnapshot / FrozenSourceCommandProjection](command_tracking_torch_candidate_v1.py#L95-L161) 已实现这套 conditional 短 H 演化接口。snapshot/model-side metadata 不进入 actor；heading frame 的实际绑定由未来 receipt 确认。

## 3. W35：实际 all-rough BODY command held，验收方向另捕获 sampled heading

[W35 actual eligibility](../discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/command208_v3.py#L16-L20) 返回全 false；[RoughStraightCommand](../discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/terrain208_v3.py#L19-L30) 的普通非站立 command 为 `vx=.6u-.3, vy=0, wz=0`。因此该实际 config 下，未重采样/reset 的短 H BODY command held 是可用规则，**不应套用 E2 或 legacy flat moving projection**。

[W35 config](../discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/config_mod4v1_w35.py#L14-L48) 保留 20% standing、原 [-.3,.3] BODYvx、12..16s。`_command_heading` 在 [每次动态 write](../discovery/reward_command_audit_v1/W35/runtime/isaac/mod4/command208_v3.py#L51-L61) 被当前 heading 覆盖，不是不可变的 sampled axis。

验收必须保留：普通自然 resample 的瞬间捕获 sampled heading；sampled BODYvx<0 时轴加 pi；standing 用真实 sampled Boolean，不靠小速度阈值猜。该 sampled axis 属于 observer/评价分段，不作为 actor feature 或 reward 伪标签。

## 4. raw35 与 state：应共享 SAMPLE-time 观测装配，不能替换为干净 current-state

[原 policy observation contract](../discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/mod4_task.py#L1206-L1245)：

| raw35 索引 | 来源 / 原尺度 |
|---|---|
| 0:3 | 当前 BODY command |
| 3 | height command ×5 |
| 4:7 | sampled/noisy/delayed BODY omega ×.5 |
| 7:10 | sampled/noisy/delayed projected gravity |
| 10:14 | selected leg q-default q + 原 bias/noise/delay |
| 14:16 | zero wheel position slots |
| 16:20 | selected leg qd-default qd + 原 noise/delay，×.1 |
| 20:22 | selected wheel qd-default qd + 原 noise/delay，×.1 |
| 22:28 | 最后输入 env 的 6-D action，不偷换成 PD/物理 applied queue |
| 28:35 | 原 mode block |

LEG_ORDER=`left_crank,left_hip,right_crank,right_hip`；wheel=`left_wheel_spin,right_wheel_spin`。总关节 30，不等于这六个通道恰好是前六列。候选要求实际 resolved indices 与 actual default q/qd，不硬编码前六。

原 [feedback runtime](../discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/feedback_delay_runtime.py#L24-L27) 是 `SensorCorruption → FeedbackDelay → observation scale`，每 4 个 .0025s physics tick 采样，即 100Hz；每个 .02s control 内有两个采样。BODY 值保留 **sample frame**，不在 apply frame 重旋转。原噪声、episode leg bias、0/10ms per-episode lag、warmup 与 same-tick cache 语义都保留。

当前桥只有 delay 配置而没有所有 `cur/out/sample_tick` 和控制内两个 sample states。故仅有 50Hz state1 的 WM 没有证据能完整重建上述延迟值。`raw35[4:22] == clean(state1)` 在真实 delayed/noisy 情形下本来不成立；这一点不应被误报为 getter live 错误。

[共享 compose_raw35](command_tracking_torch_candidate_v1.py#L20-L54) 接受 **noise+delay 后的 sample-time 值**，只做原尺度/slots 装配；real obs 保留 identity。strict 默认要求 sensor/sample clock receipt；显式诊断模式才允许 `command_exact_sensor_aux_approximation`，该标签不是 exact sensor reconstruction。

## 5. reward、φ/WM、critic 看的是哪个时钟与 frame

参考 SDK [step order](../discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py#L192-L270) 是：

```text
process a_t → 8 physics steps → episode counter++
→ termination at physical s1_t → original reward(s1_t, OLD cmd_t)*dt
→ reset done rows → command compute/resample/write cmd_t+1
→ final noisy/delayed obs xi_t+1
```

这是 referenced source 的精确调用顺序，运行中 method binding 仍待 receipt。

| 链 | 状态/command / clock |
|---|---|
| real replay label | physical pre-reset s1；native r/done；xi_t 是旧 command；done xi1=0、xi1_valid=false |
| φ 若指 WM 状态转移 | `wm.step(s_t,a_t,normalize(xi_t))`；输入 invariant(s_t) 去世界 xy/yaw，仍保留 root z、旋转衍生量、BODY v/omega、q/qd；没有独立 frame 参数 |
| auxiliary reward / done / delta | invariant(s_t), invariant(s1), a_t, a_prev, xi_t, `f_t*.02`；原生训练标签用旧 command 对应转移 |
| next actor / goal | projected/predicted xi_t+1、state1、action_t、f_t+1；goal 来自新 raw command |
| critic / bootstrap | imagined s_H，xi_H，goal_H，f_H；MDP feature 的 `f/1000` 是另一缩放，不应误叫物理秒；两者索引链相同但尺度不同 |

原 bridge flatten 的位置/速度 getter 引用已记录在 measurement review：actor pose 与 COM velocity 文档不能替代实际点/frame receipt。当前源没有单独的 potential/φ reward 对象；不要凭符号构造新潜势奖励或声称已发现 getter 的确定故障。

## 6. reward 侧的可证范围与利用风险

原 [SCUT tracking funcs](../discovery/reward_command_audit_v1/E2/runtime/isaac/mod4/scut_flat_rescue.py#L13-L41) 是：

```text
forward_err = cmd_t.vx - v_body_x(s1)*sqrt(clamp(1 - gravity_body_x(s1)^2, 0))
lin_exp = exp(-forward_err^2 / sigma)      # sigma NOT squared
lin_square = (.25*forward_err)^2
lin_huge_gap = (forward_err^2 > .5)
yaw_err = cmd_t.wz - omega_body_z(s1)
yaw_exp = exp(-yaw_err^2 / .25)
yaw_square = (.25*yaw_err)^2 * actual_height_gate
```

不把这些无权重分量冒充完整 native reward。原 reward 还有 height/local terrain、contact、action/acceleration/torque/power、rolling 与相应课程项，依赖实际 source/config/weight/gate/clock。候选 [original_tracking_terms](command_tracking_torch_candidate_v1.py#L313-L325) 只给源公式分量。

**C 候选**：确认实际 term list、weights、dt、height gate、body getter point/frame 后，构造 weighted original tracking component `r_exact`；aux target 改为 `native_r - r_exact`，imagination 返回 `r_exact + learned_residual`。原 native 标签/成功阈值不改；父代理未提供该 exact callback 时默认行为仍是原 scalar head。

原 aux 的 reward 头是无界线性输出，done 是 state/action 条件 sigmoid；critic 又以 imagined reward/done 的 lambda target 学习。冻结这些权重只阻止它们被 actor optimizer 改动，不阻止 actor 顺其输入 Jacobian 寻找高 reward / 低 done 的模型盲点。这是结构性风险，**不是当前已有 reward hacking 的 runtime 诊断**。

建议独立记录 held-out native reward/term residual、Jacobian 与 actor 搜索后误差、done Brier/ECE/尾部漏报、WM rollout support、bootstrap value 偏差；按 role/真实 motion mode 分层，但分层标签不进入 actor。

D-uncertainty 辅助函数实现 `mean(ensemble_reward)-beta*population_std`；当前不包含已训练/已校准 ensemble，不接成默认 native reward。对模型偏差、ensemble 相关性及 hard failure 稀有样本仍需单独评估。

## 7. residual / anchor / 信赖域

原 action 是 `clamp(teacher + .05 * unbounded_logits, -6, 6)`；`.05` 是比例，不是 residual 上界，logit=1000 时输出可达 6。teacher 冻结和零输出初始化只保证起点，并不保证后续技能保留。

新 `BoundedTeacherResidualPolicy` 用 `clamp(clamp(teacher,-6,6)+radius*tanh(logits),-6,6)`；radius=.05 是候选 action-unit 预算，不是实物稳定性证明。teacher weights 冻结，teacher forward 不放进 no_grad，保留 input derivative。可选 anchor 用 `(action-clipped_teacher)^2/radius^2`；teacher/reference 输入图不 detach，避免把 state 梯度偷切。anchor 默认 0。

`ScaledTeacherResidualPolicy35` 专为 A1/B/C 对照，继续使用原 `.05*logits`；bounded / anchor / uncertainty 都各自单列消融，不混在“只修 tracking”中。

## 8. s1→a0、终止、timeout、fresh episode 保持

[原 core](../source_core_review/ctx_reward_learner.py#L376-L491) 的 imagined state/action/context 没有 detach；WM/critic/aux 的 parameter freeze 不切 input grad。候选 core 只插入纯 differentiable hooks：

- 独立 transition projection hook；旧 projection 作为未启用 hook 时的兼容路径。
- 可选 reward decomposition target / imaginary reconstruct hook。
- 可选 actor anchor penalty，只加 actor loss，不改 critic reward target。

[unified diff](SOURCE_TO_CANDIDATE_DIFF_V1.patch) 与 [build receipt](BUILD_CANDIDATE_RECEIPT_V1.json) 证明：`ContextReplayBuffer`、`TaskAuxiliaryModel` 整类 AST-identical；`collect`、`load`、history/resume/receipt 等方法 AST-identical。s1→a0 的 VJP 原逻辑保留逐字：future reward/bootstrap → first action，并再测 future→s1→a0 排除 a_prev-only 捷径。

原 term/timeout labels 不改；done 行的 next context target 仍无效；终止所在 transition reward 保留，后续 replay window cutoff 不变；fresh ep_step=0 仍用当前 obs 填历史；reset-resume 仍 stream boundary seal + history zero。奖励/anchor 没有切掉整条 imagined graph。

## 9. 消融：区分真实 baseline、actor contract 修复、tracking、reward、regularizer

| 组 | 唯一变化与比较方式 |
|---|---|
| A0 current native baseline | 保留原 source/teacher/fullstate residual/held mask，只作为历史基线和源诊断，不宣称 deployable |
| A1 deploy-view control | fresh raw35-only residual；同 teacher/历史/预算/原 `.05*logits`、held command/原 reward head；显式记录 actor-view+fresh-start 的必要差异 |
| B tracking only | 相对 A1，仅修有源依据的 E2/W35 command/共享 sampled observation projection；残差尺度、原 reward head 不改 |
| C reward decomposition | 相对 B，仅加已核验原 tracking component + fitted residual head；native label、阈值不改 |
| D-bound | 相对 C，仅 bounded residual，anchor=0、无 uncertainty |
| D-anchor | 独立相对 C 或预登记 D-bound 参照，仅打开 anchor；列清 parent group |
| D-uncertainty | 独立相对 C，仅启用已校准 ensemble LCB/support budget，不顺手加 anchor/bound |

A0→B 直接变化含 actor contract/fresh start，不能归因“tracking only”；A1 是必要匹配控制。全组保持原 command distribution、物理 DR/扰动、episode limits、验收 endpoint 与原 success thresholds；报告自然 resample/reset unknown coverage，不筛 easy windows。

## 10. 最小缺件（新窗口启用之前）

1. **live binding / point / clock receipt**：actual env/backend class/module/method SHA，关键 getters 的 sample/apply 时间及 actor/COM 点/frame；原 measurement observer 被动方案继续使用，未知项不填猜测。
2. **model-side command snapshot**：E2 的真实 mode Booleans、standing、fixed world_direction、signed_yaw、post-write phase counter、decoded time_left、manual mode、active command config/projection source；W35 sampled heading/Boolean/vx 在原自然 resample 边缘记录。不要借验收 UID 充当 actor feature。
3. **100Hz sensor queue/tape**：resolved joint IDs/default q/qd、原 channel cache 与两个 sample/control 的 noisy values/stamps、lag/warmup/reset 状态；需要 WM 内 100Hz sample-state prediction 或有根据的 sensor latent model。只有 50Hz endpoint 仍是缺件。
4. **reward/source calibration**：active term weights/dt/gate、body getter 点/frame与 clock 对齐，held-out native target 残差/support、done calibration。C/D 任一项都不自动“提高通过性”。
5. **fresh migration / 软件与原条件验收**：父代理完成 CPU Torch 与新 core 集成测试；决定新窗口的 actor35 migration、teacher identity、独立计数，然后才考虑 native 等条件比较。现有 E0/E2 不 hotpatch。

## 附：精确路径、SHA、测试与差异

所有 source/candidate SHA 见 [provenance](SOURCE_PROVENANCE_V1.json)；新文件清单见 [SHA256SUMS](SHA256SUMS_V1.txt)。核心固定值：

- 原 core SHA256 `2603308f1adfe65f576eaf2aa3e0275d8465f110e6edd6e3db38304bf3e72039`；候选 SHA256 `c0cc5d201e98598d32f62572a61be633cb7d8bcdf53e5f33883792df12539454`。
- [Torch candidate](command_tracking_torch_candidate_v1.py) SHA256 `bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223`。
- [self-contained CPU Torch tests](test_command_tracking_torch_cpu_v1.py) SHA256 `3ac2d347ba10333cc3e10870ac94225c04963570c8d5e6c9263cefadf0595703`；最小依赖为该脚本+相邻 Torch candidate+父环境已有 Torch。22 个测试仅合成软件/梯度，optimizer/native expert BPTT 均 0。
- [stdlib test script](test_command_tracking_stdlib_v1.py)：37/37 PASS，含解析 H16 held 反例、原尺度/slots、two100Hz/one50Hz 区别、cache/warmup/reset、原 sigma 公式、actor privacy、终止 window 与 protected AST/VJP 检查；测试收据 [TEST_RESULTS_STDLIB_V1.json](TEST_RESULTS_STDLIB_V1.json)。

父代理 remote CPU 测试命令（新 CPU root 中复制两个冻结文件）：

```text
python -B test_command_tracking_torch_cpu_v1.py --output NEW_CPU_ROOT/TORCH_SOFTWARE_RECEIPT_V1.json
```

额外新写 [core integration CPU source](F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_command_review_v1/test_command_tracking_core_integration_cpu_v1.py)，SHA256 `348c1494133292fb3905c5e33f5b55c1dc8a0cca10fcfbc5ba48ace7283f45f4`。本地仅 stdlib AST/compile PASS，未执行 Torch。它只 AST 提取旧 tiny fixture 的 FakeTeacher/Synthetic 和桥的 BridgeState/OriginalTaskMdp（不执行旧 fixture bottom、不加载 PT），真正 import 两份冻结 candidate 与父代理已有 vendor。H16、hist10、collect8、WM/aux20、actual policy/critic3；断言三步均 verified BPTT、future→s1→a0 VJP/参数增量非零、teacher 冻结、actor35、CUDA 未初始化、native0。传感 substep 是声明的 SYNTHETIC 几何中点/end+外生 noise/bias/lag oracle，**不填补实际100Hz缺件**。bound/anchor/decomposition/uncertainty 均关闭。父代理需在独立 CPU 用途目录实测；三份冻结源码和既有 build/test receipt 均未为此修改。

```text
python -B test_command_tracking_core_integration_cpu_v1.py --vendor-parent CPU_INPUT_ROOT --fixture INPUT/synthetic_cpu_contract_check.py --bridge-source INPUT/native_supermimic_bridge.py --candidate-dir INPUT/FROZEN_CANDIDATE_DIR --output-dir CPU_INPUT_ROOT/NEW_RESULT_DIR
```

vendor-parent 直接包含 supermimic_vendor_v2；output-dir 必须为全新目录。结果写其下 CORE_INTEGRATION_RECEIPT_V1.json 与 SYNTHETIC_LOGS，不保存 checkpoint。本专项不把这类软件步作为 native training 或 90% 通过证明。
