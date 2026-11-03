# Saved-replay consistency diagnostic v1 — SOURCE ONLY

交付是一份诊断入口、一份最小 synthetic 测试及 manifest/SHA 封件；没有训练器、环境适配框架或新物理探针。

- 入口：[replay_consistency_diagnostic_v1.py](<replay_consistency_diagnostic_v1.py>)。
- 测试：[test_replay_consistency_synthetic_v1.py](<test_replay_consistency_synthetic_v1.py>)。
- 封件：[manifest.json](<manifest.json>)、[SHA256SUMS](<SHA256SUMS>)。

## 解释边界

**POSTHOC_REPLAY_RESUBSTITUTION_CONSISTENCY**。saved replay 可能已参与训练；结果不是 heldout / generalization / 原任务技能通过率 / 因果归因。没有真实未来标签的新 actions 不是验证。

已有真实参考仍是：E3 recovery 教师/候选/bound 都为 0/74；normal6 首物理 term 0/6、6/6、0/6。W35 moving 19/63、10/69、14/60；standing 26/26、16/17、13/22。自然 cohort 不同、single seed，relative/causal 均 null。bound 是零更新部署约束，不是训练收益。此诊断不改变这些结论，也不借 BPTT 历史计数替代技能证据。

## 只读/执行约束

- 本地只运行 stdlib/AST/synthetic 默认分支；未导入 Torch、未读取真实 checkpoint/raw、未 SSH/SDK/GPU/Git，未改原封件或 canonical 预算账本。
- 父在 remote **CPU** 新 purpose 执行。只允许下列 E3/W35 **own complete**，每次调用单 role、一轮物理 bytes 读取 / SHA / `weights_only=True,map_location='cpu'` decode，无 fallback。
- 整 root（包括 critic、4 optimizer state、replay、saved RNG、history、environment）始终 CPU/cache 保留；不恢复 optimizer/RNG/env/history，不实例化 learner/optimizer/env/SDK；不把 N1024 slice 成 N80 训练恢复。
- 活模型只有 WM、aux、pi（pi 内含 embedded teacher）。实际 class/normalization/API 来自 SHA 固定的真实源；`strict=True,assign=False` 加 key/shape/dtype/value 检查。wrapper 构造先 zero residual，随后严格加载完整 pi，避免初始化覆盖 saved residual。
- 不打开 mother。teacher 只来自 `pi.teacher.*`；FINAL/embedded teacher metadata 相互核验。
- 初始化置于 `torch.random.fork_rng(devices=[])`；取样使用私有 `torch.Generator(cpu)`；全局 Torch/Python/NumPy RNG 前后比较。执行 no_grad，所有参数 requires_grad=False/eval，native BPTT/optimizer/norm updates **0**。
- root/live 模型作完整 tensor identity/version/shape/dtype/device guard 与全值摘要前后比较。全值摘要覆盖未使用 optimizer 等，不只是 actor。原 raw 为不可变 Python bytes；原文件只读、前后 stat(device,inode,size,mtime_ns,ctime_ns) 比较；没有第二次磁盘 bytes/hash。报告明确此磁盘证据强度，不伪称第二次磁盘 hash。
- 输出 `open('x')`，要求是 producer 整 root 外的新 JSON 文件；不回写原文件。source SHA 封件后视为冻结，需要修改时另起版本/重封件。

## allowlist / lineage

固定 producer run：

```text
MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000
ROOT=/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000

E3 role_key=supermimic_e3_72
ROOT/roles/E3/production/checkpoints/model_BPTT002182_I002282_S0005_complete.pt
236664417 bytes
a4c56390b4c549ba8bfb808a63206c0816ad50e8c9659dc053f98cc66b3c8127

W35 role_key=supermimic_w35_72
ROOT/roles/W35/production/checkpoints/model_BPTT001973_I002073_S0005_complete.pt
233435425 bytes
b2f2878ff9aa04ddcd283fe71f5b5924b1bff78b3f04118cfa689244b0665cff
```

每 role 必须是原 `production/FINAL.json` 与原 `TASK.json`，且父预先提供各自 exact bytes/SHA；路径按固定 root 派生，resolved path 相等才读。不是从早期失败 V4 FINAL 取值。FINAL kind/role/role_key/run/成功执行/raw35 family/variant、checkpoint 完整性/bytesSHA/path/iteration/teacher 逐项核对；payload 同 FINAL/TASK original protocol、asset/contract、counts 严格对应。完整 config key/value/type 与真实 worker+vendor 默认一致，seed 绑定原 TASK。任何 mismatch 直接报错，无放宽或替代 checkpoint。

## 计算内容及样本边界

### 一阶 H1

默认随机取 **64** 个真实 transition（上限64，不分层重加权）。terminal 的 `s1` 是 bridge 在 reset 前 capture 的真实物理状态，r/done 为有效标签，所以保留到 physical/reward/done 面板。context/raw35 target 只用 `~done & ~stream_cut & xi1_valid`，永不把 terminal zero-xi1 或 post-reset observation 当 target。

- vendor `WorldModel.step(State,a,normalize_context(xi))`；normalize_context 是源中的 identity。
- 状态误差使用真实 `WorldModel.state_error`，而非对 quaternion 分量作 RMSE：heading-local position3、so3-log rotation3、target-body linear/angular velocity 各3、joint q/dq 各30；另报 body projected gravity3。
- 输出各组 MAE/RMSE/max/per-component、saved WM output std 标准化混合单位误差。
- aux 分 **true s + true s1**（头拟合一致性）与 **true s + WM s1**（一阶串联）两档。
- 原 reward MAE、真实 reward mean/std/mean_abs、saved reward_norm.std、两种尺度比；done=term OR trunc 的自然分布 Brier/BCE/ECE10/bin count/置信概率。若64样本没有正例，明确 positive_labels=0，绝不当“已验证物理终止识别”。
- 原 aux 未 mask delta 对比 `recorded xi1 - recorded xi`；effective saved-mask+legacy-projector xi1 与全 xi/raw35/sensor16 误差。sensor16 是 `4:14` 与 `16:22`（0.5*omega3、gravity3、legpos4、0.1*legvel4、0.1*wheelvel2），保留原 noisy/delayed 单位，不从 clean physical state 反造 sensor。

### Actor drift

单独无放回最多64个合法 history 窗口。只用原 `xi[:35]` 的 history10，以及最新原 cmd[:3]。teacher 是 embedded deterministic mean。报告六分量 scaled residual(.05)、actor-minus-clipped-teacher、teacher 原值，以及 actor/teacher clip saturation 和 preclip outside 比例。不是新 actions 的未来 rollout 验证。

原 ring chronology 按 `(ptr-size+age)%T`，不按物理行顺序。history 每条 edge 验证 no done/streamcut、xi1_valid、f/ep_step +1，并验证 selected s1->s、xi1->xi、a->a_prev 实际数组相等。history 首段未知时跳过；只有真实可见 `ep_step=0` 才按原 repeat-current padding 重复该已知 observation，绝不填零或把 ring oldest 冒充 reset。

### H16 两档、matched windows

默认最多 **32** 个完整 H16 窗口。每个窗口16步全部 no done / no streamcut / xi1_valid，chronology 与真实数组 adjacency 都检查。不会越 ring 末端索引 fake obs。该 survivor-window selection 有覆盖偏差；H16 done 面板不是全分布校准。

1. **CONDITIONAL_STATE_OPENLOOP**：state 只从首真 state 开始，之后 WM state 连续开环；每步用 recorded applied action 与 **真实 xi、a_prev、f**。这是条件 state 预测一致性，有 oracle context，**不是实际 policy-imagination 全链误差**。
2. 可选 `--full-context-openloop`：**FULL_STATE_AND_CONTEXT_OPENLOOP_ALONG_RECORDED_ACTIONS**。初始真实 s0/xi0/a_prev0/f0 后，只有 action 仍取 recorded；随后按真实 core 的 `WM.step -> aux.features -> delta xi * savedmask -> OriginalTaskMdp.project_predicted_context` 更新，a_prev=recorded a，frames+=1。state/context 不重锚，不偷用真实未来 xi 作为输入。真实 s1/xi1/r/done 只作标签。不是 actor-generated rollout，也不使用 learned done gating 改变匹配窗口。

各档报 h=1..16 的物理/重力/速度/关节、reward/done/xi/raw35 sensor 误差与16步累计原 reward 误差。没有合法 H16/actor history 时输出明确 MISSING/NO_LEGAL 状态及样本数，不伪造 PASS。FULL 的命令/部分 metadata 在 legacy 源中确实 held；报告该近似，不换成其它 command 演进接口。

### 原 mode / clock / recovery 证据

只依据 xi 实际 layout 中的 scalar command_mode/key/recovery_recipe/request、或 raw35[28:35] exact vector 做 observed groups（最多8个 unique value）。不赋予“standing/moving/recovery phase”臆测标签，不制造 xi 中没有的 UID/phase。报告 actual sampled f/ep_step、存在的 recovery 字段 offset/width/mask/value。

以下源码提供精确证明；source SHA 见 manifest：

```text
source_runtime/native_supermimic_bridge.py:98-130
  xi prefix=('actor35_original',35); context_layout 仅记录真正采样到的字段。
  command_time_left/age * .01；recovery_age/stable * .01；recipe/request/credited 原尺度。
source_runtime/native_supermimic_bridge.py:142-144
  f/ep_step 是 transition 前控制钟；done 的 xi1 清零并 xi1_valid=False；physical s1 reset前capture。
source_runtime/native_supermimic_bridge.py:64-66
  out=context.clone();out[...,14:16]=0.;out[...,22:28]=action;return out
source_command_review_v1/command_tracking_torch_candidate_v1.py:183-200
  Raw35ActorMDP.__getattr__ 委托 base；obs=context[:35]，goal=context[:3]，add_noise identity。
source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py:66-84
  mask[:4]=0;mask[14:16]=0;mask[22:35]=0
  额外 held iff name.startswith(('mild_','PD_')) or name.endswith(('factor','delta_m','lag_steps'))
                  or name.startswith(('feedback_delay','command_'))
  recovery_* 没有被此条件普遍 held；需按实际 layout 与 saved mask 看每维。
source_quality_microtrain_resume_alias_v2/ctx_reward_full_resume_candidate_v3.py:393-408
  next_frames=frames+1
  aux.features(state,state1,action,previous_action,normalized,frames)
  next_context=context+context_predict_mask*delta_context
  next_context=project(next_context,state1,action,next_frames)
  state,context,frames,previous_action=state1,next_context,next_frames,action
source_quality_microtrain_resume_alias_v2/ctx_reward_full_resume_candidate_v3.py:153-162
  aux seconds=frames.float().unsqueeze(-1)*policy_dt_s(.02)；不是 held frames。
```

诊断只抽取 AST 中真实 OriginalTaskMdp/TeacherResidualPolicy/TaskAuxiliaryModel/Raw35ActorMDP class，注入已读实际 namespace；不执行 PinnedTeacher、NativeTaskBridge、learner 构造或旧测试 fixture bottom。core v3 的 whole deepcopy 只是训练恢复 ingress 改动；诊断未走该 load_full_checkpoint。

## 父执行前所需封件（仅源码搬运，原件保持不动）

本 bundle 的三项内容文件 SHA 见 manifest；manifest 本身另由 SHA256SUMS 绑定（共四项）。额外依赖只读源如下，父可以复制到 `$INPUTS` 后按 basename 指定；脚本校验 bytes-content SHA，不依赖本机 F 盘位置：

```text
F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py
F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_quality_microtrain_resume_alias_v2/ctx_reward_full_resume_candidate_v3.py
F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_command_review_v1/command_tracking_torch_candidate_v1.py
F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py

VENDOR_PARENT=F:/RMPOLAR-RL/supermimic_step270_e0_20261101/discovery/tasks/H1step270_dual72_fudan_supermimic_E3_2610v85m2/e2/source
VENDOR_PARENT/supermimic_vendor_v2/__init__.py     # docstring-only AST 检查
VENDOR_PARENT/supermimic_vendor_v2/contract.py
VENDOR_PARENT/supermimic_vendor_v2/geometry.py
VENDOR_PARENT/supermimic_vendor_v2/networks.py
```

远端需现有 CPU Torch（支持 `weights_only`、`assign=False`）、tensordict、实际 rsl_rl.models.MLPModel 及依赖；可重复 `--dependency-path` 指向该源码依赖父目录。真实 MLP 源 path/bytes/SHA 被写入报告（该动态依赖没有新增猜测 pin）。不安装 SDK，不调用 GPU，不自动安装包。需要的真实数据文件只有所选 role 的原 FINAL/TASK/上面 allowlisted complete.pt；不需要 mother/raw/其它 checkpoint。

## CLI

### 本地已执行：stdlib / AST / synthetic（不导入 Torch）

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B `
  'F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_replay_consistency_diagnostic_v1/test_replay_consistency_synthetic_v1.py'
```

15 tests PASS，覆盖 wrapped/partial ring、unknown history、true ep0 padding、done/cut/invalid/clock gap、H16 tail、mask/recovery、严格 config/lineage、AST 禁训练调用与全局seed、单次 decode kwargs；这不是 Torch PASS。

### 父 remote CPU：建议先可选真实 Torch API synthetic smoke

```bash
# 所有路径变量由父指定到 SOURCE 封件；此步不读取 PT/FINAL/TASK/raw。
COMMON=(--bridge-source "$INPUTS/native_supermimic_bridge.py"
        --core-source "$INPUTS/ctx_reward_full_resume_candidate_v3.py"
        --raw35-source "$INPUTS/command_tracking_torch_candidate_v1.py"
        --cache-source "$INPUTS/frozen_a1_raw35_v1.py"
        --vendor-parent "$VENDOR_PARENT")
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 "$CPU_PYTHON" -B \
  "$BUNDLE/test_replay_consistency_synthetic_v1.py" --torch-smoke "${COMMON[@]}"
```

这是小 synthetic tensor（B2、H16、小hidden）的实际 vendor/aux/wrapper API 冒烟、冻结/RNG/guard 区分检查，无 optimizer/checkpoint/skill 声明。本地未运行该分支。

### 父 remote CPU：实际 saved-replay 诊断

```bash
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_A1_RAW35_V6_ADMISSION2_20261102_231937_1793632777470828000'
# 父先核实原 JSON，再提供各自 exact pins；不是凭字段重序列化的 SHA。
ROLE=E3
FINAL_BYTES="$E3_FINAL_BYTES"; FINAL_SHA="$E3_FINAL_SHA"
TASK_BYTES="$E3_TASK_BYTES"; TASK_SHA="$E3_TASK_SHA"
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 "$CPU_PYTHON" -B \
  "$BUNDLE/replay_consistency_diagnostic_v1.py" \
  --role "$ROLE" --final "$ROOT/roles/$ROLE/production/FINAL.json" \
  --final-bytes "$FINAL_BYTES" --final-sha "$FINAL_SHA" \
  --task-bytes "$TASK_BYTES" --task-sha "$TASK_SHA" \
  "${COMMON[@]}" --batch 64 --windows 32 --sample-seed 20261103 \
  --cpu-threads 1 --full-context-openloop --output "$NEW_DIAGNOSTIC_DIR/E3_consistency.json"
# W35 另一个新进程：ROLE=W35，用 W35_FINAL/TASK 的 exact pins，输出新 W35_consistency.json。
```

父可在已核实 SOURCE SHA 后运行 `--help` 查看完整参数。实际数据/真实 Torch 执行留给父；本交付只有本地 stdlib 测试证据。运行成功只表示诊断完成，质量结论仍须独立真实任务评价。
