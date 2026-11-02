# E2 / W35 原接受谓词测量实施方案 V1

**状态：SOURCE_ONLY + CPU 纯合成；非真实专家通过，非 frozen 验证结果。**

本目录仅新增测量源、可证伪假说和合成测试。既有 core / bridge / worker / command / physics / reward / accepted 阈值保持原状。未执行远端、模型、SDK、GPU、canonical、锁、GO、Git 或实际 frozen 评测；未读取旧 raw / JSONL / NPZ。父代理独立处理 actual 时序和未来验证准入。本方案不依赖父代理当前训练进度，也不把训练事实转换成接受率。

## 1. 能力选择与交付入口

已检查当前 available skills catalog 和 host 工具描述：Office 系列与 ACL 诊断均不匹配 RL 源码测量；未加载技能、未装新依赖。采用 `read / glob / grep / write / edit` 与 `pwsh`；通过 host `load_workspace_dependencies` 定位已有 Python，执行 `-I -B` 标准库 CPU 测试，未导入既有运行时模块。

- [observer_uid_ledger_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_measurement_review_v1/observer_uid_ledger_v1.py>)：原谓词计算、逐控制捕获审计、显式 UID / attempt ledger、独占新流 writer、声明式 command cohort join。
- [native_validation_observer_entry_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_measurement_review_v1/native_validation_observer_entry_v1.py>)：独立 future native 插桩入口 `NativeValidationObserverEntry.submit(event)`。它只接收已分离的 Python 标量拷贝；无环境、模型、SDK 或 bridge 导入，无自动 hook、热 patch、step/reset/resample/update 调用。
- [test_cpu_synthetic_v1.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_measurement_review_v1/test_cpu_synthetic_v1.py>)：确定性标准库测试；测试数据全为程序内合成。
- [SOURCE_EVIDENCE_AND_GAPS_V1.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_measurement_review_v1/SOURCE_EVIDENCE_AND_GAPS_V1.json>)：逐源定位、假说及所有未补 runtime 证据的 `null`。

## 2. 原数字与分母逐字义保留

依据 [原接受 contract:157–217、280–347](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json#L157-L347>)。

### E2

- 只选原 profile 8 / 9（原 moving Boolean + signed_yaw 的正负），两符号分别报告；不以速度替代原分类。
- 同 profile、episode UID、command UID、world_direction、signed_yaw **符号**的连续控制；每控制严格 8 × 0.0025 s = 0.02 s。
- 位移沿固定原 world_direction 投影；yaw 每控制 `atan2(sin(heading_after-heading_before), cos(...))` 后累加。
- sampled endpoint 上 `actual_turn * sign >= 2π` 才 complete；无插值，超转不传给下一圈。
- 接受：`seconds>0 && complete && !terminated && !truncated && abs(along-.5)<=.05 && abs(cross)<=.05 && abs((turn-commanded_yaw_integral)/seconds)<=.2`。
- **complete endpoint 同时 terminal/timeout：仍在 complete 分母，结果 false。** 转满前的终止/reset/resample/身份改变/window-end：partial，原 complete 条件分母之外但保留 attempt。
- control `<100` warmup 到 steady 的跨越仅记录，不切圈。

### W35

- axis 固定为 sampled `_command_heading + π if BODYvx<0`；`v=abs(sampled BODYvx)`。随机保留的 `cmd.direction` 无效，作为未使用的诊断量。
- 两个平移误差都用 **`max(.03, .1*abs(BODYvx))`**；yaw error 上限 **`.2 rad/s`**。
- complete：`count>0 && outer_natural_resample(timer_before<=0 && !within_reset) && start_observed && !terminated && !truncated`。
- accepted 为 `complete && 原运动学界限`。terminal / timeout / reset / unknown start / 参数或 source episode 改变 / window-end 留在 partial ledger，不偷偷纳入条件分母，也不删除曝光。
- moving / standing 只按 sample/open 时的原 `is_standing_env` Boolean 分组，零速度不自动归 standing。
- sampled body / axis / standing / counter 在 resample 后保存；first begin 再读取 source `_e1_episode`；每控制 acted command 单独用于参考积分。原 `count>0` 参数改变规则保留。

**不使用 x8 速度修正、BODY tracking proxy、额外 acceleration cap、catalog goal 或未证据的通过门槛。** 90% 外层 all-started / seed / cohort 聚合尚待父代理事先定义；这里没有发明 global fullskill 毕业规则。

## 3. root / COM / actor / heading：源码所知与所缺

### 3.1 root_pos_w 不是已证的 COM getter

本地 [getter 基类:470–540](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1/base_factory_v4/assets/articulation/base_articulation_data.py#L470-L540>) 与 [alias:1148–1194](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1/base_factory_v4/assets/articulation/base_articulation_data.py#L1148-L1194>) 表明：

```python
root_pos_w -> root_link_pos_w                 # actor/root-link position
root_state_w -> root_link_pose_w + root_com_vel_w  # 文档约定；实际后端仍抽象
root_com_pos_w                              # 另一个 COM position 属性
root_quat_w -> root_link_quat_w             # xyzw
root_lin_vel_w -> root_com_lin_vel_w         # COM velocity，与位置语义分开
```

`heading_w` 文档假设 base forward 为 x，但实现抽象。故“root_pos 是 COM、root_state 是 actor，所以根因确定”缺证据。实际 PhysX getter、timestamp/update 实现、本次运行 backend 类型/模块 SHA 在本地源链中未补齐：[factory snapshot:1–23](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/diagnostics/W35_SDK_DATA_GETTER_ORIGIN_SOURCE_V1/actual_module_spec_v2/1/articulation_data.py#L1-L23>) 仅做分派。

### 3.2 原读数链与新 bridge

- [E2 原桥:15–18](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/minimal_e2_cycles_bridge.py#L15-L18>)：begin 与 terminal 都使用 `root_pos_w` / `heading_w`，reference 取 begin heading + 当控制 BODY command 的投影。
- [W35 原间隔:89–126](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py#L89-L126>)：begin 是 `root_pos_w` / `heading_w`；terminal 是 frame `root[:,:2]`，用 **xyzw** quaternion 自算 heading。相同 API 名称或同一终止函数并不证明同点、同缓存相位。
- 本地 [terrain snapshot:89–142](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/diagnostics/W35_MOTION_WIRING_SOURCE_V2/terrain208_v3.py#L89-L142>)：ground refresh 先触 `root_pos_w`，后 original termination，继而 `root_state_w.clone()` 入 `_e1_pre_reset_frame`；frame 自身原来无 tick 字段。terrain query tick 检查不能外推为 robot getter freshness 证明。该 diagnostic snapshot 的本次 runtime 身份仍为 null。
- 已读 [新 native bridge:84–147](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L84-L147>)：`pack()` 把 `root_state_w` 的 world position 减 `env_origins`，xyzw 重排成 wxyz；`_termination_capture` 在 `_oldterm` 后保留 pre-reset `s1`。`step` 的下一 `s` / `xi1` 是 post-reset，done 的 `xi1` 还被置零。现有 `context` 缺 E2 的完整原 flags / world_direction / signed_yaw 和 W35 的 standing / counter / episode ledger；ep_step 不是全局 episode UID。**单凭训练 transition 或 context 重建原接受标签缺字段。**
- 新 bridge 的 quaternion/gravity 检查仅证它检查的旋转约定；不等于点位、getter freshness、frame 身份或 command cohort 全部已证。

## 4. 未来独立 native 验证的精确插桩协议

本节仅为 parent 后续新建独立 frozen validation source 的接线说明；本次没有安装接线。已封版的 core/bridge/worker 不改。事件入口是上面的独立 module，不是自动运行器。

| 原时点 | future owner 显式送入的事件与字段 | 顺序要求 |
|---|---|---|
| 初始化 arm | `initial_packet`，W35 exact original packet 校验结果 | 原 reset packet、tick0、全 env ids、command/timer 与当前相等才能写 true；否则 false。observer arm 的 0 不是自然 sample 证据。 |
| 每次真实 control 前 | `before_control`：当前原 command、profile/flags、world direction / signed yaw 或 sampled W35 packet、source episode/counter；`Capture(stage='before_control')` | 原 body command 与 position / heading 的已有缓存克隆；记录 integrated physics tick、feedback tick、`_sim_step_counter`、getter read order。 |
| original termination 返回后、任何 reset / resample 之前 | `pre_reset_endpoint`：E2 的原 `root_pos_w/heading_w`；W35 的原 frame `root`；actual tm term/trunc 和逐原因 timeout 属性 | `Capture(stage='after_control_pre_reset')`。W35 frame 真正生成瞬间另取 `frame_capture_*` 和 `frame_identity`，原 frame 不带则 null，绝不把 read tick 当 capture tick。 |
| original resampler 之前 | `resample_before`：selected env、tick、**原 timer_before**、reset nesting | 先关闭旧 UID，natural 只取 timer<=0 且非 reset 内部；缺 timer 为 null。 |
| original sampler 返回后 | `resample_after`：新 sampled body、_command_heading、standing、counter、source episode；真实 pair event UID 若有 | 一次真实 sample 只增一次 observer command UID；无额外采样或 RNG。 |
| original reset 之前 | `reset_before` | 先关闭旧 span，再增 episode UID；reset 内部 resample 按真实嵌套顺序递送。 |
| 窗口末尾 | `finish()` | 所有未完成 span、缺 endpoint、缺 resample-after 都显式保留；writer 不丢尾。 |

### 最小被动入口示例

以下只展示新 validation owner 如何送入已经拷贝的事实；没有任何环境调用：

```python
from native_validation_observer_entry_v1 import NativeValidationObserverEntry
from observer_uid_ledger_v1 import Provenance

entry = NativeValidationObserverEntry(
    Provenance(run_uid=NEW_VALIDATION_RUN_UID, task='E2',
               candidate_actor_sha=PARENT_ACTUAL_ACTOR_SHA,
               source_manifest_sha=PARENT_SOURCE_MANIFEST_SHA,
               reference_frame_and_sample_phase_validated=None),
    new_ledger_path=NEW_EXCLUSIVE_LEDGER_PATH,
)
entry.submit({'kind': 'before_control', 'env_id': ENV_ID,
              'command': COPIED_ORIGINAL_COMMAND_FIELDS,
              'capture': COPIED_BEFORE_FIELDS})
# Future native owner advances the ORIGINAL control; observer does not advance it.
entry.submit({'kind': 'pre_reset_endpoint', 'env_id': ENV_ID,
              'capture': COPIED_PRE_RESET_FIELDS,
              'terminated': ORIGINAL_TERM_BOOL, 'truncated': ORIGINAL_TRUNC_BOOL,
              'reason_masks': ORIGINAL_REASON_BOOLS,
              'reason_timeout_flags': ORIGINAL_REASON_TIMEOUT_FLAGS})
# Deliver actual reset/resample events in their real order, then finish at window end.
summary = entry.finish()
```

### 读数与低扰动要求

1. `Capture` 只接收 scalar/tuple/dict 拷贝；不传 live Tensor、ProxyArray 或 env。observer 自身没有 getter 或 physics 调用。
2. 未来 native owner **先保存原读序**：E2 heading、command/direction、root position；W35 begin root_pos/heading，terminal 原 frame quaternion。native `pack()` 的额外 root_state materialization 可能触发 lazy cache；需记录 before/after pack 阶段，别以新读序掩盖旧现象。
3. 位点探针保存同阶段 actor/link、COM position 与 actor quaternion、实际 link-to-COM local transform；用 `p_COM=p_actor+R_actor*r_offset` 验证点差。若实际 transform 缺失，相关结论留 null。速度 getter 的 COM 语义只作诊断，不替代位移接受谓词。
4. cache 探针只写真实 backend buffer 名称、timestamp / sim timestamp / 更新时间和 read order。未知字段为 null。lazy getter 可刷新内部缓存，因此先保留“不增 getter 的原缓冲基线”，再以独立 probe pass 做读序对照；不声称 getter 读取绝对零扰动。
5. `Capture` 中的当前 tick、frame capture tick 与 frame identity 分开；W35 既有 frame 无原生 stamp 的缺口须如实记录。
6. 审计输出精确位置/heading 残差；没有新增 epsilon 验收门槛。数值边界测试用原公式，实际 dtype/rounding 在 future runtime 另留 provenance；CPU float64 不充当 Torch 后端逐 bit 等价证明。
7. 固定 `.02` 一次时间归一化，8 仅用于物理 tick 核对；feedback2 / control 与 physics8 / control 单独记录。已见缺口导致 `original_accepted=null` / integrity gap，而不是偷偷将 proxy 计为通过。

## 5. 可验证假说而非“runtime 已修”

| 假说 | 预测 / 检验 | 分清什么 |
|---|---|---|
| backend cache / update phase 不同 | 同 tick 下 `root_pos_w - root_state[:2]`、heading 差及 cache stamps/read-order 联动；新鲜 backend transform 与 getter 分别比较 | actor/COM 的固定刚体偏置与时间滞后不同；需要实际后端证据。 |
| 真正 actor / COM 点差 | 点差满足实际 `R*offset`，随姿态转动；不能只凭名字判断 | 本地基类名义上 root_pos 与 root_state 的位置都是 actor，所以 COM 根因当前未证。 |
| reference 定义不同 | 同 UID 下原 nominal-world 位移与 `Σ BODYcmd 投影*dt` 分开显示 | W35 fixed axis 下 BODYcmd 参考不一定等于 sampled nominal；E2 cosine command 的理想 `.5` 是整圈平均，并非每控制 `.5`。 |
| clock / pre-reset / quaternion 混用 | 真正8/2 tick、frame 捕获身份、xyzw / packed wxyz、world / origin-local 对照 | 不以 x8 或换参考目标“修复”接受结果。 |
| policy-dependent cohort 不同 | 相同源 sample packet 的声明式 join，列出 only-left / only-right / packet mismatch | 相同 numerator 或 UID 数字不是 matched cohort。 |

[未部署 cosine candidate:1、32–37](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/diagnostics/W35_MOTION_WIRING_SOURCE_V2/retained_flat_command_math.py#L1-L37>) 只支持一个数学假说，不证明 active E2 实际执行该更新。已发布 E2 `0/187 complete`、W35 moving `18/61 → 18/64` / standing `26/26` 均仅来源于 contract 的历史摘要；本次不读旧行补标签，不把历史汇总当新测量证据。

## 6. UID / episode / cohort 与分母 ledger

- UID 归属：`(run_uid, task, env_id, episode_uid, command_uid)`，清楚标记 `explicit_events_zero_at_observer_arm_v1`。source `_e1_episode` 和 `original_command_counter` 单独保存；0 不替代初始 reset / resample 的证据。
- 每个 E2 circle attempt、每个 W35 command segment 有 `attempt_open` / `attempt_close`；记录 first/last control、physics tick、group、reason、complete、conditional denominator、accepted、term/trunc、phase crossing、body reference 积分。
- 原 source W35 count=0 时没有接受行；本 observer 额外保留零控制 attempt 元数据，不改变原 count>0 分母。
- 参数改变但 command UID 未变时，W35 `same_UID_segment++` 且新 segment start unknown；source episode 变化也不拼接。reset 和 sample 必须显式递送，不从 ep_step、done 后的 xi 或速度猜 UID。
- command population join 要求 parent 事先提供 `cohort_namespace + cohort_event_uid`，同时核对 sampled packet 的 SHA。重复 E2 圈只在**同一真实 command 身份且同 packet**下去重为一个 command population member；不把 command population 相等解释为 attempt/outcome 相等。相同事件键复用于不同 UID 会得到 null。
- 两策略各自自然 reset 后可能产生不同 populations。缺 pair key / 重复歧义返回 `matched_UID_cohort=null`，相同计数不转成 true。不同 actor SHA 各自保留，旧 producer b3 label 不代表 actual candidate。
- 原条件分母与所有 started attempts 并排报告；未声明的外层90规则、真实专家pass、multi-seed coverage、frame/cache validated 始终 null。分母和原阈值未被新测量完整性检查重写。

## 7. 新 writer、CPU 测试与封版

`ExclusiveJsonlSink` 只用 `xb` 创建全新 future ledger，逐写计算 SHA；不读取任何旧流，不剪裁、不跳行。达到明确容量时先报 `BufferError`，owner 将该验证 scope 标为 observation-incomplete，而不是无声保留一个“通过”的子集。有 writer 时完整 control audit 直接落新流，内存仅保留轻量边界/attempt 行；无 writer 的合成测试保留全部行供断言。

CPU 测试复跑命令（结果名须全新）：

```powershell
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' -I -B 'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_measurement_review_v1\test_cpu_synthetic_v1.py' --result-json 'F:\RMPOLAR-RL\mod4v1_supermimic_bptt_20261102\source_measurement_review_v1\CPU_SYNTHETIC_TEST_RESULT_V1_NEW_RUN.json'
```

最终执行：**46/46 通过，0 failures、0 errors、0 skipped，0.138 s**。最终证据为 [CPU_SYNTHETIC_TEST_RESULT_V1_FINAL.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_measurement_review_v1/CPU_SYNTHETIC_TEST_RESULT_V1_FINAL.json>)。早先 [CPU_SYNTHETIC_TEST_RESULT_V1.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_measurement_review_v1/CPU_SYNTHETIC_TEST_RESULT_V1.json>) 是扩展 frame stamp / repeated-cohort / incomplete-resample 测试前的 43/43 历史首轮，不作为封版源码的最终测试绑定。

覆盖 E2 两符号 / sampled2pi / terminal complete / partial / phase / no overshoot carry / 原数字；W35 moving-standing / negative vx axis / tol floor / natural timer / reset nesting / source episode / same UID segment / sampled packet保留；以及 mixed getter 和 xyzw-heading差、clock / endpoint缺口、frame capture stamp null、exclusive stream/no-drop、声明式cohort和独立入口。所有测试为 CPU 内存中的合成轨迹，未调用真实环境。

## 8. 封版结论

已补齐 source-level 测量协议和可运行的被动 observer / UID ledger / native event 入口；保留原 E2 `.5 ± .05`、cross `.05`、yaw `.2` 与 W35 `max(.03,.1|vx_BODY|)`、yaw `.2`。**运行时 getter 根因、实际修复、实际专家通过率、frozen result 均未在本次验证，值为 null。** 后续只由父代理以独立 native frozen 验证源与真实证据收敛上述假说；本目录不触发实际评测。
