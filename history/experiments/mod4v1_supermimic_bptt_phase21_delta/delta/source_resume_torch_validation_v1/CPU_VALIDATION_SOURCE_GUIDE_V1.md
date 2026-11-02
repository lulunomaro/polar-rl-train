# A0/A1 legacy-core 与完整 reset-resume：新 CPU 软件验证源

## 状态与交付

- 主脚本：[test_resume_legacy_torch_cpu_v1.py](<test_resume_legacy_torch_cpu_v1.py>)；**31393 bytes**，SHA256 `08c89b3603eb7b32b4eb430a9cde112035ca187695272ee992742ceb147079d7`。已交父代理 CPU 执行并冻结；后续实测修正须另新版本，保留本版。
- 本地 [stdlib/AST 测试](<test_source_contracts_stdlib_v1.py>) **22/22 PASS，0.098s**；[本地 receipt](<LOCAL_STDLIB_SOURCE_CHECK_V1.json>) 明确 `Torch_imported=false`、实际 checkpoint 读取/生成均 0。
- **此处尚无实际 Torch 运行 PASS。** 实际 CPU 结果由父代理新输出目录中的 `SYNTHETIC_TORCH_RESUME_RECEIPT_V1.json` 提供。脚本同时在异常路径写独立失败 receipt 并保留 traceback，随后真实非零退出。
- 全部新增内容仅在本目录；旧 v2/v3/v4 源、三个冻结 command candidate、原 owner/worker/core 均保持原字节。Office/ACL 技能不匹配本 RL 源任务；使用 read/glob/CLI/stdlib，未安装依赖。

## 1. 父代理执行 CLI

使用现有 CPU Torch 环境及原 vendor/dependency 副本。所有路径显式给出；输出目录须从未存在。每次尝试使用新输出目录，不覆盖既有失败证据。

```bash
python -B test_resume_legacy_torch_cpu_v1.py \
  --vendor-parent CPU_INPUT_ROOT \
  --dependency-path EXISTING_SM_DEPS \
  --fixture INPUT/synthetic_cpu_contract_check.py \
  --bridge-source INPUT/native_supermimic_bridge.py \
  --payload-core INPUT/ctx_reward_full_resume_candidate_v2.py \
  --resume-contracts INPUT/resume_runtime_contracts_v3.py \
  --raw35-source INPUT/command_tracking_torch_candidate_v1.py \
  --output-dir CPU_INPUT_ROOT/NEW_NEVER_EXISTED_RESULT
```

`--vendor-parent` 下必须有 `supermimic_vendor_v2/learner.py`；`--dependency-path` 可重复，指向已有 rich/tensordict 等依赖所在目录。脚本不安装依赖、不联网、不发现原 PT、不执行 SDK 或 worker。使用新 Python 进程，避免不相关的预载 module。

五个 source 输入强 pin：

| 输入 | SHA256 |
|---|---|
| fixture | `4de256764f7fec0dac6fbb624a7a4189d7a686dc9d28bd5570a9a43f8afce10d` |
| bridge-source | `8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29` |
| payload-core | `8116ea358dfe32e0efd568d00661ab1e13b602d267ea4b580ced04ec39e898ac` |
| resume-contracts | `dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7` |
| raw35-source | `bb7555ff2de598677ea6cfe5dadefe0a9cfe37d37661635d186bcb14c1df2223` |

fixture/bridge 必须是源文件输入。输入 SHA 不符即中断。实际 import 的 core/contracts/raw35 模块均校验 `__file__`；vendor learner 的实际路径与 SHA 写入运行 receipt。

## 2. 真实源码复用，而非重写 loader

- fixture 仅 AST 选 `FakeTeacher`、`Synthetic`；原底部测试/训练语句不执行。
- bridge 仅 AST 选 `BridgeState`、`OriginalTaskMdp`，并单独选取**原 `TeacherResidualPolicy` 类**。不构造/执行 `PinnedTeacher`、`NativeTaskBridge`，不读取原 bootstrap/selected PT。
- 实际 import 冻结 payload-core `8116...`、v3 contracts `dc4b...`、原 vendor、冻结 raw35 wrapper `bb75...`。
- 实际走 `PinnedOwnFullCheckpoint` → `validate_full_resume_payload` → `load_decoded_full_checkpoint_once` → 原 decoded `load_full_checkpoint(payload, allow_environment_reset=True, allow_partial_update=False)`。
- 自定义 task/payload 完整填写真实 validator 所需 role、asset、contract、protocol、teacher path/SHA/bytes、actor view/family、四模型/四 optimizer/replay/RNG/history、environment/context layout 等字段。身份均明确为 **SYNTHETIC**；不是对某个 native worker 运行的冒名证明。

## 3. A0 与 A1：只改 actor view 的 legacy 对照

两条路径各自从九项计数 0、四个空 optimizer state 开始，使用独立 learner/env：

- **A0_FULLCTX**：context40，actor obs `79+40=119`；teacher 仍取其中原 raw35，residual 仍是历史 full-context 视图。这是基线对照，不是可部署 actor 证明。
- **A1_RAW35**：context40 中前35给 actor，额外5个明确 toy model-only 数值不进入 actor/goal。`Raw35ActorMDP(base, transition_projector=None)`，原 teacher wrapper offset0、`.05` 无界 residual。脚本验证 actor 观测/goal 对 state、previous action、frame 与后缀元数据变化保持 raw35 身份切片。

实际 payload-core 只调用原 `project_predicted_context`，raw35 wrapper 通过 `__getattr__` 委托 base；不调用新的 strict command/sampled-sensor hooks。A1 的 `last_projection_status` 必须始终 `not_used`，无 oracle、无新采样回执。故命令仍 legacy held、sensor context 仍 aux 近似，**不称 tracking fixed 或 sensor exact**。无 bound/anchor/reward decomposition/uncertainty 修改。

## 4. 每条真实 CPU 测试计划

使用 `horizon=16`、`hist=10`、CPU、1线程、tiny hidden16：

1. 原合成 fixture collect8（8 env，真实 `sim_steps=64`）。
2. 实际 WM/aux optimizer 各20次。
3. 实际 policy/critic 各3次；九项计数必须严格等于：attempt3、pi3、verified BPTT3、unverified0、skipped nonfinite0、skipped zero0、WM20、aux20、critic3。每次均要求 future→s1→a0 的 cross-time 与 WM-path VJP 为正且有限、参数梯度与实际参数差值为正。
4. `_checkpoint(True)` 生成**自己的新 synthetic full PT**，并写入新结果目录。teacher identity 仅由新 fake teacher 的 BytesIO 计算，无 teacher 文件读取。实际 teacher state 额外注册一个 toy buffer，便于测试 buffer 检查。
5. 独立 fresh learner/env 仍九计数0、模型/optimizer 尚未恢复；每个新 checkpoint 恰好一次真实 byte read、一次 SHA 验证、一次 BytesIO `torch.load(weights_only=True,map_location='cpu')`、一次 decoded loader 调用。
6. 逐项比较四模型全部参数/normalizer buffer、四 optimizer tensor/参数组、replay 所有字段、九 counters、iteration/sim/wall、collect_fraction、pending phase/remaining、last gradient receipt、context mask。source history 在完整包保留，但 live history 按 reset-resume 清0；仅 replay 最后行 `stream_cut=True`，`done/term/trunc/xi1_valid` 原位不变。
7. 在任何 RNG probe draw 前，实际 `core.capture_rng()` 必须与 saved Python/CPU Torch/CUDA-empty（若有则含 NumPy）完全相同；再与独立 RNG object 生成的下一批数逐项对比。测试脚本不手动调用 global `restore_rng`，防止掩盖 loader 缺陷。NumPy 仅在现有环境可导入时验证；receipt 中 RNG sequence 布尔按此条件理解。
8. 从 restored3 累计继续：新 env 首次原 `init_state` 后 collect1，真实 WM/aux各1、policy/critic各1，得到 pi/BPTT4、WM/aux21、critic4、iteration4、sim72。不是把 fresh计数加旧 offset。验证 fresh episode 历史填充及 sample-window stream-cut mask。

合成 collect_fraction `.375` 与 collect-phase pending 是专门测试恢复字段的 sentinel，不是 native 运行日志。合成环境的唯一 fresh `init_state` 不冒充 SDK `env.reset` 的调用证明。

## 5. 负例与 teacher 保护

- A0→A1、A1→A0：真实 `validate_worker_variant` 阻断跨 view descriptor；即使改 descriptor view，真实 `validate_full_resume_payload` 仍在模型 mutation 前因 contract/dimension 不符阻断。
- 另做**独立的** `pi.load_state_dict(strict=True)` shape 负例，验证底层 Torch shape guard。它不是绕过 metadata gate 的 admitted resume；目标对象随后丢弃、不继续训练。
- A0 新 bad full PT 仅改 `teacher.net.weight`；A1 新 bad full PT 仅改 `teacher.synthetic_frozen_buffer`。其余 teacher source identity metadata 不变，因此实际 full loader 可完成；随后对 actor 的真实 `state_dict`、frozen parameter/grad、eval mode 的检查必须抓到差异。
- 独立 source-root 的值和 `_version` 此时仍未变化，说明 source-cache 身份/版本保护不等于实际 actor weights/buffers 保持。正常 restore/continue 路径则要求实际 teacher 每项完全相等。

每条路径只生成一个正常 synthetic full PT 与一个 bad-teacher synthetic PT；合计4个新 synthetic PT。每个恰好一次 byte read/decode。它们严格位于新输出目录；原模型 PT 读取计数保持0。

## 6. 软件验证边界

本脚本只检验实际 Torch 软件层的模型/optimizer/normalizer/replay/RNG/full-loader/梯度与 actor-view 组合；本地此时只有22项 AST/stdlib 检查通过。

以下仍不由本测试证明：native owner admission/原计账锁；真实 bootstrap PT byte cache；真实 E0/E2 checkpoint 恢复；physics/DR/noisy feedback/100Hz sample clock；live backend/getter/quaternion/cache绑定；App.close fast-nonreturn语义；姿态 adapter；原任务鲁棒性或成功率。父另 v5 close/adapter 分支与本脚本独立；旧封件不变，native计数仍0。
