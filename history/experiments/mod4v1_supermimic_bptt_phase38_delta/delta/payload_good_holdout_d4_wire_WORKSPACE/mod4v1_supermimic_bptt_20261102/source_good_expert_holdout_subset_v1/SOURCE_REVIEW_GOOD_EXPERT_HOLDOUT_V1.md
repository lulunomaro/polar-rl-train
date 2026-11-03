# C878 / S135：质量保持独立 seed 评测的最小 SOURCE 包

## 1. 交付状态与目标

- 本包仅准备下一次独立 seed 的原技能保持证据；没有训练或新原技能实测。`enabled=false / staged=false / dispatched=false`。
- 唯一请求角色：`CURB_PROTECTED878`、`SLOPE135`。完整八角色字典保留，另外六角色 deferred；`H1` 不属于字典、无 factory 调用、无实例构造。
- 原 N80、每角色 750 control、50 Hz policy / 100 Hz feedback / 0.0025 s physics、6000 physics / 1500 feedback、ascending 27 / descending 27 / standing 26、原接受条件及 D0–D7 均保留。没有新 E0 / S50 predicate。
- 技能 catalog 已核对：现有 Office / Windows ACL 技能与 RL SOURCE 分析不匹配；使用 FS read / glob / grep，之后只运行本地 stdlib / fake / AST 测试。
- 没有 SSH、SDK/Torch/native import、GPU 查询、真实 PT/raw 读取、canonical 预算账本或锁操作、Git 操作；原 16 / 14 / 完整八 scope 封件无编辑。临时测试布局与 JSON 都位于本 NEW 目录，仅含源码和 synthetic metadata，退出即清理。

## 2. 历史证据与 actor 身份

唯一历史通过率来源为[已发布八专家报告](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/MOD4V1_EIGHT_EXPERTS_POSTTRAIN_FINAL_V1.md#L45-L59>)，均为 seed `20260928`、N80、原 750 control 条件：

| 原专家 | ascending | descending | standing |
|---|---:|---:|---:|
| CURB_PROTECTED878 | 26/27 | 27/27 | 26/26 |
| SLOPE135 | 27/27 | 27/27 | 26/26 |

[已发布 A1 quality-boundary metadata](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/A1_ADMISSION2_QUALITY_BOUNDARY_CLOSED_TRUTH_V1.json>)明确两角色为 actual0-update fullfreshcapture，9 类计数全 0、iteration 0；fresh WM / optimizer0 不作为训练。E3 / W35 新 teacher / unbound / bound 未获改进证据，仍 deferred，未改变保母决定。

本包选择 actual0 own A1 fullcapture 内的 **embedded 原 teacher deterministic mean** 作为保持 baseline；不是 fresh residual，也不是对母 PT 的第二次读取。所有完整远端 identity 字符串固定在[协议组件](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/holdout_protocol_components_v1.py#L9-L24>)并由真实已发布 metadata 交叉测试。

| 角色 | own A1 container bytes / SHA256 | 原 motherteacher bytes / SHA256 |
|---|---|---|
| C878 | 220144758 / `ae4ac8d31b82c9b7488e7e40419bf2d590be6566822b78a7604e49f848e6bcfe` | 17621306 / `db3d5a6a2a81fb71f6f4e3ca0ee18c09785ddff80b990787960ffc3d8d376d68` |
| S135 | 220144758 / `22d7ea42c208256cc5c89980472f72df71d8f279a9bc98f09c1eaa8426f2abe1` | 17620922 / `ec5b495691e10bf4ef6587e7fad99df02a18ff48e44f6b70d5170aaa7b641b05` |

容器身份 `OWN_A1_FULL_CHECKPOINT_CONTAINER_NOT_MOTHER_FILE` 与 `original_bootstrap_teacher` 分开。原 whole-pi / Norm / STD / all-state freeze、N1024 CPU root / history / replay 不切片、physical N80 包含性、一次 own bytes/hash/decode、mother opens 0 均沿原 helper。producer evidence 仍由实际 TASK / INSTALL_MANIFEST / FINAL 和完整 pinned producer worker / bridge 的 allstate snapshot + `torch.equal` 保存前、FINAL 前 AST 重导；published report 或 caller boolean 单独不替代这些原证据。

## 3. 真实 E1 entry → factory → one-reset → done 接口

经真实 import 路径确认，而非按目录存在时间挑链：

1. 原[CURB wrapper](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/worker_curb878_n80.py>)及[SLOPE wrapper](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/worker_slope135_n80.py>)调用原 alias `e1_parallel_worker_safe.main_role(exact_role)`；NEW manifest 只将该 alias 绑定到[NEW E1 worker](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_worker_v1.py#L92-L135>)。
2. worker 从 **task.runtime_root** 读取 `E1_CANONICAL_SOURCE_METADATA.json`、断言 canonical==role，加入其 `runtime/isaac/mod4` 与 `runtime`，原 launcher / mod4_task / fresh guard 仍由此链导入；新旧本地目录的存在不证明 active。
3. factory 精确接口：`build_original_route80(role, descriptor, case, identity, torch, np, wp, tensor) -> original_bundle`。NEW[factory](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_factories_v1.py>)的请求入口只接纳两角色。两个实际 factory 仅将 args.seed 和对应 assertion 路由至 `current_seed()`；其他 cfg / 物理 / terrain / command / geometry / reset 完整函数 AST 与原相等。
4. `attach_fresh_guard(env, identity, torch_module, tensor)`先调用本包 seed-bound pose installer，再包原 reset；factory 在其后作唯一一次 explicit `env.reset()`。NEW[bridge](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_bridge_v1.py>)的该完整函数 AST 未变；pose adapter 自身不消费 seed/RNG。
5. 沿原 canonical 的 `OriginalA1NoResetDecisionVec(env, cache, torch_module, TensorDict, tensor)`：无第二次 reset；`get_observations()`原 observation_manager 每 control 一次，policy `(80,35)`、critic `(80,38)`仅验证布局；actor 仅收原 noisy/delayed policy35，command prefix≤1e-6。
6. `step(action)`原 `env.step(clamp(action,-6,6))`返回 separate `terminated, truncated`，先传 `caller.observe_transition(terminated,truncated)`，再向 E1 loop 暴露合并 done。`OriginalEpisodeBoundary`首 action 的 start 全 True，后续是 **真正的 terminated | truncated**；无 zero-mask、无自制 done、无跨 episode predicate 拼接。fake 测试分别覆盖 term / trunc / pending-step 顺序。
7. 原 E1 `_run_loop(...)`完整函数 AST 保留：manual groups、50/100 Hz、physical callbacks、contact / force、ordinary / integrity / unknown / trunc reason 暴露、原 `_e1_pre_reset_frame` 与 EndpointPredicate 均未替换。该 loop 的 dormant S50 描述分支仍保留原 AST，但请求路由不构造 S50。

原 formal embedded worker 仅接纳 E0 / E2 / E3 / W35，直接替换请求列表会触发其角色硬 pin；本包明确用上述真实 E1 route。

## 4. 必需的 NEW 小变更与接口

| NEW 部件 | 必需变化 | 原逻辑保持 |
|---|---|---|
| [runtime / schema / barrier](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/good_expert_holdout_runtime_v1.py>) | own seed/context/protocol、两成员路由、full8 catalog、actual0 identity、原 E1 metrics semantic、独立 seed summary | 原 producer/source guard、cache、close / error AST、原 task 资源描述符 / N80 / 物理检查 |
| [NEW parent](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/single_gpu_good_expert_holdout_parent_v1.py>) | 新用途标签；semantic row 加 seed / holdout；SOURCE entry 要求未来显式 reviewed enabled/staged | 原 main 整体 AST（仅上述元数据差异），privateEX + finiteEX / Creadonly / wait / p.wait / finally |
| [NEW E1 worker](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_worker_v1.py>) | 请求两角色、手动 RNG seed 取 current_seed、使用 own runtime / barrier；FINAL 加 explicit purpose | 原 plant loop、ready 前 0step / 0actor、原环境/App close |
| [NEW bridge](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_bridge_v1.py>) | fresh audit 显式 seed/purpose，断言 cfg.seed | attach guard / reset 位置及 D0–D7 原审计 |
| [NEW factories](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/e1_good_expert_holdout_factories_v1.py>) | 两个 seed expression + 两个对应 assertion、two-role dispatch | 两角色原完整 factory AST 归一后相等；没有新物理/阈值/acceptance |

`select_requested_roles(plan)` → `[C878_row,S135_row]`；`make_task(role,plan,deadline,fds)` → own seed-bound task；`wait_group_start(task,group,maximum_seconds=900)` → exact-two, same-seed barrier。task/plan/pose/start/FINAL 的 seed 与 purpose 逐层绑定；canonical 模块 globals 不变，其旧 seed-pinned `make_task` 不被调用。

精确 plan/task kind、required fields、证据字段与函数签名见[接口契约](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/API_CONTRACT_GOOD_EXPERT_HOLDOUT_V1.json>)；这些是 SOURCE 协议，不是已 materialized 的 GROUP_PLAN。

## 5. 两个独立 holdout 协议

| seed | 独立 purpose | 执行单位 |
|---:|---|---|
| 20260929 | `GOOD_EXPERT_HOLDOUT_C878_S135_SEED20260929_V1` | 自己的 group_id，恰好两角色，各 N80 / 750 control |
| 20260930 | `GOOD_EXPERT_HOLDOUT_C878_S135_SEED20260930_V1` | 另一个 group_id，恰好两角色，各 N80 / 750 control |

- 原 `20260928` 仅作 published baseline provenance；其重评不计作新独立证据。不同 seed 的实际 UID/pose 独立性不是单靠相同 planned 配置即可证明；`paired_effect_claim=false`，`reference_actual_receipt=null`。
- 两 seed 保持同一固定 original-teacher actor，不做训练、threshold 调整或 role 混合。统计只在每角色、每方向 / standing 条件内：每 seed 27 / 27 / 26；两 seed 汇总分母 54 / 54 / 52。
- 方向分别保留 original complete、contact_confirmed；standing 使用既有 assessor 的 `group=='stand' and first_ordinary_failure_control is None`，并非 crossing。原 EndpointPredicate 的 stand complete/contact 为 0 是预期语义。
- summary 只消费两个独立 group、exact-two waited semantic rows 和一致的原 metrics；给出描述性 Wilson95，并明确非 IID/cluster-adjusted 或非劣性证明。没有整个技能 90%、pooled whole-skill rate、improvement、新测质量或八技能毕业率。

## 6. 完整依赖闭包与当前待补

[小 manifest](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/GOOD_EXPERT_HOLDOUT_SOURCE_INDEX_V1.json>)列出 20 个 overlay、原 V8 全 worker dependency pins、真实历史原 runtime rows / asset metadata 及 materialization requirements；没有大 stager/executor。

- `a1_frozen_eval_runtime_v2.py` **保持 canonical 37927 bytes / `7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e`**。NEW runtime 用不同 alias，避免递归/循环导入；完整模块 import 测试已跑。
- `app_close_semantics_v5.py` alias 仍绑定完整 AppV6（27769 / `3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39`），其 `resume_runtime_contracts_v3.py` 是完整 dc4base（22337 / `dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7`）；测试确认 `_base` 为真正导入的该模块，不作 AST 切片。
- 继承真实原[GROUP_PLAN](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json>)对应的原 runtime_origin / runtime_root；其历史 teacher 字段仅是 provenance，不覆盖本包固定 posttrain motherteacher identity。
- 原资源主干：private GPU EX + global finite EX，canonical generation/minimum/active-owner 只读；空卡≥23500 MiB、util=0、RAM>96 GiB、disk>25 GiB；1800 s bounded resource wait、900 s ready barrier、2400 s deadline；实际 `p.wait()`之后作 semantic；finally 等完全部 own child 后解锁。完整 AST 测试通过，没有用新 executor 替代。
- **仍需未来父代理 materialize/验证**：selected task.runtime_root 的完整原 role tree、完整 static banks / assets / deps，而非只 import slice；完整七文件 vendor tree `ddf9d6e1744c050fd5298805d125a611673ff22ade52c5177fb02c488ff8f0c0`；原 ownjob producer TASK / INSTALL_MANIFEST / FINAL 及源文件的实际绑定。此 SOURCE 包未读取/复制原 raw/static bank bytes。
- 旧 E3/W35 stage hardpin 角色/seed/kind；它不直接标记本 NEW source 为 staged。未来 stage binding 需独立 reviewed 新 kind，保留完整原 deps，再走父代理 review → CPU → preflight → stage → dispatch。当前 `ready_for_native_dispatch=false`、`original_runtime_tree_materialized_here=false`、`overlay_alone_is_complete_native_runtime=false`。

## 7. 本地验证与封件

本地[stdlib/fake/AST 测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/test_good_expert_holdout_stdlib_v1.py>)21/21 通过；结果见[测试报告](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/TEST_REPORT_GOOD_EXPERT_HOLDOUT_V1.json>)。覆盖 exact2/full8/deferred/H1、两个 purpose 与跨 seed 负例、原 term/trunc 边界、guard→one reset、parent wait/finally 与 E1 全 loop AST、factory 仅 seed 差异、canonical/AppV6/Base import、producer 全源码 guard、close semantic 正负例、conditional summary、真实 published actual0 identity。

40 项 inherited/indexed 原 source 路径继续 byte-exact；另逐一核对 old embedded16 / micro14 / integration **完整八 scope 的 12 个映射** 全部 SHA 一致（“8”是 scope，不是该 index 的映射数量）。audit：model/raw/budget opens=0，forbidden native imports=0，process/network/lock operations=0。所有 positive close / wait / barrier / summary fixture 明示 `SYNTHETIC_METADATA_NOT_NATIVE_OR_WAIT_PROOF`，不升级为真实运行证明。

可重复的 SOURCE-only 命令（仅派生 equality-check、metadata equality-check、stdlib 测试；不执行 parent）：

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B 'mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/derive_holdout_sources_v1.py'
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B 'mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/build_source_manifest_v1.py'
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B 'mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/test_good_expert_holdout_stdlib_v1.py'
```

[source seal 工具](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/seal_good_expert_source_v1.py>)仅对 14 个明确 NEW 文件与全部 indexed text dependencies 哈希；已有 seal 时只验证、不替换。重复检查命令：

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B 'mod4v1_supermimic_bptt_20261102/source_good_expert_holdout_subset_v1/seal_good_expert_source_v1.py' --verify
```

最终 source seal 写入后保持稳定；后续需求应新版本派生，不编辑本 seal 覆盖的内容。此文档所述结果仅为 SOURCE 交付与 fake/AST 验证，新质量仍未测。
