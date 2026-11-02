# MOD4v1 源专项：完整 reset-resume、语义终止门与 A0/A1 分支

## 1. 交付状态与证据边界

本目录只新增 source candidate、diff、stdlib 测试及 receipts；未运行 owner/worker、SDK/App、GPU 或 native 训练，未打开实际 teacher/BPTT checkpoint，未操作原账户/C/GO/锁/Git。先前封版源、三个冻结 command candidate 文件和 active/旧 worker 均保持原 bytes。Phase20 point-in-time 之后的本目录新增件供父代理 Phase21 append；此处没有执行归档、提交或推送。

- **推荐未来组装入口：v4 owner + v4 worker + v4 install-hook + v3 contracts + v2 payload-loader core。** v2/v3 文件留作可复核中间版本，v4 只补父代理转来的 agent82 稳定 pre-reset installer API。
- v2 stdlib：50/50 PASS；v3：50 项回归 + 21 项 variant = 71/71 PASS；v4 installer：12/12 PASS。共有 **83 项不同断言测试**（71 中的50与v2重复），不是133项独立测试。
- 新 full-resume 的测试使用假 model/optimizer 和 AST 抽出的真实 loader body；**实际 Torch full-checkpoint restoration 尚待软件验证，native restoration 尚待原窗口验证**。
- 先前 raw35 command candidate 的真实 CPU 核心集成 V3 已由父代理验证通过，但那是另一个 core/合成 sensor oracle 组合；它不替代本目录 A1 legacy core 或 full-resume 的验证。

## 2. 为什么需要新的 owner 成功门

原 [owner:66–68](../source_runtime/supermimic_original_owner.py#L66-L68) 与 shared owner 在实际 `p.wait()` 后仅以 `rc != 0` 设置 original_error。首个已闭合 native window 的 [truth report](../reports/FIRST_NATIVE_WINDOW_CLOSED_TRUTH_V1.json) 显示六个启动失败角色 RC0 但有 WORKER_ERROR、缺成功 FINAL；因此 RC0 不构成完整成功。该事实不证明 App.close 掩盖异常的具体根因。

新 [v3 contracts](resume_runtime_contracts_v3.py) 的 `evaluate_waited_worker(job_root, returncode, entry, run_id)` 在**原 p.wait() 之后**校验：

1. 实际 rc 必须为0；任一主/回退 error sidefile 存在即失败，即使 JSON 已损坏。
2. 成功 FINAL 必须是新 schema、run/role/role_key 对应、passed_execution=True；A0/A1 view/family 与原 entry 匹配。
3. 九个 producer counter 有效，BPTT≤pi optimizer≤attempt；FINAL BPTT 与 checkpoint counter receipt 相等。
4. checkpoint receipt 必须声明完整新模型/critic/aux/四优化器/replay/RNG/history，SHA/bytes 有效，路径在本 job 的新 production/checkpoints 内。
5. 必须存在**所有原 close 返回之后**写出的 lifecycle receipt；缺此标记的硬进程退出不会被当作成功。
6. 有限窗口完整保存且 target_reached=False 可以是执行成功，但不等于达到3000或技能验收通过。

失败只阻断 pending 新启动；既有活跃子进程仍按原有限窗口/保存/close/wait/结算逻辑处理。原 `account/admit/gpu/environment/verify_sources/plan_protocol`、C/UUIDS/RESERVE 全局赋值、锁/收费/资源调用及有限窗口常数保持 AST 相同。

## 3. 完整 checkpoint：只开字节一次，不走 actor-only 迁移

新 [payload-loader core](ctx_reward_full_resume_candidate_v2.py) 基于原 sealed core SHA `2603308f1adfe65f576eaf2aa3e0275d8465f110e6edd6e3db38304bf3e72039`，只拆开 path decode 与既有完整恢复 body：

```python
def load_full_checkpoint(self, payload, *, allow_environment_reset=False,
                         allow_partial_update=False):
    # 原 load() 在 torch.load 之后的 body，AST 保持相同
```

原 path `load()` 仍委托此 API；未来 worker 不调用 path load，而是 `PinnedOwnFullCheckpoint` 一次 byte open → 一次 SHA → 一次 `torch.load(BytesIO, map_location='cpu', weights_only=True)`，保留整份 bytes/payload，再调用 decoded API。旧 frozen teacher 是**另一份独立 PT**，继续原 PinnedTeacher 一次 byte open/SHA/decode；新 BPTT path 与旧 teacher path 必须不同。

恢复校验在 mutation 前检查：原 schema、完整4 models/4 optimizers、角色/资产/协议/teacher path+SHA+bytes、原 context named order/width、num_envs/30 joints/6 actions、同 actor view、obs/norm/optimizer维度、完整 RNG/replay/history/counters 与安全 update boundary。原 loader 再检查所有算法配置（仅原本允许的 iterations/ckpt/log字段例外）与 strict model state。

- 恢复 WM/pi/critic/aux；opt_wm/opt_pi/opt_v/opt_aux；replay、九个真实 counters、iteration、sim_steps、wall_time、collect_fraction、pending_iteration、last_bptt_receipt；global RNG 最后恢复。
- 明确 `allow_environment_reset=True, allow_partial_update=False`。只执行原 ONE fresh reset；保存的旧 history 仍保留在源 payload，但不跨物理 reset 作为 live history，按原 loader seal replay stream boundary、live history 清零、下一次原 fresh-episode padding。
- 原 done/term/timeout 标签不重写；终止行与 timeout/fresh history mask 不变。
- 原 BPTT future→s1→a0 VJP、optimizer hook 的 verified count 逻辑与 policy_update AST 完全保持。
- 原 capture_rng 已将 NumPy values 转 list；没有为了恢复删 RNG。实际 `weights_only=True` 与完整模型/优化器状态仍须父代理 CPU 软件实测。
- 对旧 producer 未嵌入 run_id 的情况，receipt 分别保留 embedded=None 与 descriptor 的 declared source run，未伪造已验证 producer run 绑定。

## 4. A0 与 A1：全量恢复和 fresh actor-view 对照分开

[v3 contracts](resume_runtime_contracts_v3.py) 支持以下显式分支；v4沿用同一分支逻辑：

| variant | actor_view/family | 恢复来源 | 起点 |
|---|---|---|---|
| A0_FULLCTX_RESUME | baseline_fullctx_v1 / a0_fullctx_legacy_v1 | 自己原 baseline full checkpoint | 原 producer 全量 counters |
| A0_FULLCTX_FRESH | 同上 | 无新 BPTT source，只有原 teacher | 九 counter 全0 |
| A1_RAW35_FRESH | raw35_legacy_held_aux_v1 / a1_raw35_legacy_v1 | 无新 BPTT source，只有独立冻结 teacher | 九 counter 全0 |
| A1_RAW35_RESUME | 同 A1 family，保存的 actor_view/family 必须嵌入且匹配 | 自己后续同 variant complete checkpoint | 自己 A1 counters |

A0 全 state actor 含仿真 privileged context，只保留为历史 baseline 连续性，不将其称为部署 actor。A1 不从 A0 切权重/Norm/Adam/replay/history，也不把旧A0 BPTT计数拼到 fresh A1上。

### 已实际读源码核对 A1 接口

原 [core:395–404](ctx_reward_full_resume_candidate_v2.py#L395-L404) 只查 `project_predicted_context`；冻结 [Raw35ActorMDP:183–200](../source_command_review_v1/command_tracking_torch_candidate_v1.py#L183-L200) 用 `__getattr__` delegate 该方法给原 base MDP，real actor obs 是 noisy/delayed raw35 的 identity slice、goal 是当前 command3，`add_noise` identity。

所以 A1 使用 `Raw35ActorMDP(base, transition_projector=None)` 与原 `TeacherResidualPolicy(..., actor_context_offset=0, scale=.05)`：

- 原 legacy core **不会**调用 strict `project_transition_context`，不需要合成 oracle/100Hz未来 receipt。
- WM/critic 保留原全部 model-side context；actor仅35历史 + known command goal。
- real noise/bias/100Hz delay链不变；imagination依旧 held command/aux sensor **近似**，**未修 E2 body/world command 演化，也非 exact sensor projection**。
- `.05*logits` 仍是原无界缩放；没有混入 bound、anchor、reward decomposition 或 uncertainty。B/C/D继续独立消融。
- worker 对冻结 raw35 module 的 SHA、manifest条目和实际 `__file__` 做明确验 pin；原三个冻结 source bytes不改。

## 5. teacher 的实际设备权重与 buffers 保护

[v4 worker:71–73](worker_supermimic_bptt_pre_reset_candidate_v4.py#L71-L73) 在 actor 建立后对 `actor.state_dict()` 每项实际 tensor 做 `detach().clone()`（在 actor 所在 device）。full load 后及 progress/save/final 均逐项 `torch.equal(current[key], snapshot[key])` 并检查所有 parameter `requires_grad=False`，同时保留原 teacher source-cache frozen assert。这样同时覆盖 weights 与 buffers，非仅检查 CPU 源 checkpoint `_version`。任何不符保留原 error，不以“teacher原源没变”掩盖 actor已改变。

## 6. 原 ONE reset / C113 / pose-cache installer 顺序

推荐 [v4 worker:51–70](worker_supermimic_bptt_pre_reset_candidate_v4.py#L51-L70) 顺序：

1. 原 build_env 与原 fresh-DR/config/assert；不新增构造或 reset。
2. 若父 task明确指定 pinned descriptor，调用 agent82 stable API：

```python
from pose_cache_runtime_adapter_v3 import install_pose_cache_runtime_adapter_v3
handle = install_pose_cache_runtime_adapter_v3(
    env.scene['robot'], receipt_callback=callback)
```

3. 原唯一 `env.reset()`，原 guard 检查。
4. 原 [C113 binder](../source_runtime/original_role_command_binding_candidate_v2.py) 在 reset 后、bridge/首 action 前调用一次；非C113 identity。没有额外 obs/RNG/reset/step。
5. 原 NativeTaskBridge、teacher、model构建；需要时完整 decoded load；不再 reset。

新 [v4 install-hook](resume_runtime_install_hook_v4.py) 只是 descriptor/manifest/SHA/bytes/API/import与时序钩子。实际8-buffer timestamp、class/MRO/writer pin 等由 agent82单独源执行；本专项未创造或修改这些修复逻辑，未改 xyzw→wxyz 或 `err<1e-3` guard。callback仅将 adapter提供的 event字典写到新侧文件，不额外查询 gravity/heading/obs/step/reset/RNG。handle保持至原关闭路径。

未指定 descriptor 时完全no-op。指定后任何源/API/manifest不匹配即真实报错，原 error/close门继续生效；不做静默降级。

## 7. 错误与原关闭路径

[v4 worker:100–107](worker_supermimic_bptt_pre_reset_candidate_v4.py#L100-L107) 在 finally 原 close 前，用 exclusive-create + flush/fsync 保存首个 WORKER_ERROR；后续 close error写独立secondary，不覆盖首错。首路径失败则尝试job根回退，再stderr。依次尝试原 bridge.close/env.close/App.close，单项 BaseException 或写sidefile失败仍继续后续原 close；`SystemExit(0)`不是执行成功。原 App硬退出使post-close receipt缺失，新owner阻断pending。没有外部signal、额外自动重试或账户修复。

## 8. 测试与保留的失败历史

- [v2 recheck receipt](TEST_RESULTS_STDLIB_RESUME_RECHECK_V2.json)：50/50，0.160s，stdlib/fake对象，不是Torch/native恢复。
- [v3 receipt](TEST_RESULTS_ACTOR_VARIANTS_STDLIB_V3.json)：71/71（50回归+21variant），0.205s。
- [v4 receipt](TEST_RESULTS_PRE_RESET_INSTALLER_STDLIB_V4.json)：12/12，0.051s；fake installer仅验证API/无额外getter/时序，不是agent82实际adapter验证。
- [首轮v2 receipt](TEST_RESULTS_STDLIB_RESUME_V2.json) 保留50中1个失败：测试selector误选更早的资源 admission UUID loop，报 `AssertionError: 2537 not less than 1089`；只修测试selector从semantic gate之后找pending loop，candidate未为此更改。
- new generated Python仅AST parse/compile；没有执行owner/worker主程序。

先前 [父CPU集成V3 receipt](../reports/COMMAND_CANDIDATE_CORE_INTEGRATION_CPU_V3.json) 单独记录真实Torch2.10 CPU软件、H16/hist10、pi/critic3、WM/aux20、三次future→s1→a0 VJP与paramdelta非零、actor35、teacher frozen、CUDA未初始化/native0。该receipt属于先前strict-projection candidate + synthetic2x100Hz oracle，不拼进本目录native0/A1fresh0，也不解释成技能90%。

## 9. 未来最小组装件与缺件

最小推荐worker sources：v4worker、v4install-hook、v3contracts、v2payload-loader core、原native bridge、原C113 binder、原vendor。A1再加冻结 raw35 module。父选择pose-cache adapter时再加agent82实际模块并把其SHA/bytes写入同一INSTALL_MANIFEST和entry descriptor；该模块的writer/data双pin由agent82给出，本报告不预填。

```json
{
  "algorithm_variant": "A1_RAW35_FRESH",
  "actor_view": "raw35_legacy_held_aux_v1",
  "pose_cache_runtime_adapter": {
    "kind": "POSE_CACHE_RUNTIME_ADAPTER_V3",
    "module": "pose_cache_runtime_adapter_v3",
    "symbol": "install_pose_cache_runtime_adapter_v3",
    "source_relative": "worker_sources/pose_cache_runtime_adapter_v3.py",
    "SHA": "<AGENT82_FROZEN_SHA>",
    "bytes": "<AGENT82_EXACT_BYTES_INTEGER>",
    "install_timing": "after_build_env_before_only_original_reset"
  }
}
```

A0恢复另需 `resume_bptt` descriptor：kind OWN_NEW_BPTT_FULL_CHECKPOINT_V2、自己新BPTT path/SHA/bytes/producer_run_id、actor_view baseline_fullctx_v1、allow_environment_reset=true、allow_partial_update=false。A1后续同variant恢复还需descriptor algorithm_family=a1_raw35_legacy_v1且源checkpoint嵌入匹配actor view/family；A1_FRESH不带resume_bptt。

**剩余最小验证：**

1. 父代理CPU-only用自己新合成完整checkpoint，验证本payload-loader 4models/4opts/replay/RNG/计数恢复及同A1 view完整resume；目前只有stdlib fake控制流。
2. agent82实际冻结installer SHA/bytes与API源核对；再由父决定新窗口是否部署并保留原guard/错误证据。实际backend getter/frame/cache根因与修复效果仍需native证据。
3. 本A1 legacy core可另做最小CPU实际集成确认；先前strictcandidate CPU通过不是该组合的软件receipt。
4. 父最终决定A0连续性还是A1fresh新cohort，严格分开原native4912和新A1零起点；原命令分布/物理DR/成功阈值不缩减，不hotpatch旧窗口。

## 10. 版本与精确溯源

- 原source→v2：[diff](SOURCE_ONLY_RESUME_DIFF_V2.patch) / [build receipt](BUILD_SOURCE_CANDIDATES_RECEIPT_V2.json)。
- v2→v3：[variant diff](ACTOR_VARIANT_DIFF_V3.patch) / [build receipt](BUILD_ACTOR_VARIANTS_RECEIPT_V3.json)。
- v3→v4：[installer diff](PRE_RESET_INSTALLER_DIFF_V4.patch) / [build receipt](BUILD_PRE_RESET_INSTALLER_RECEIPT_V4.json)。
- 最终所有顶层artifact SHA/bytes、read-only sources SHA、AST/compile与冻结源复核见 [provenance](SOURCE_RESUME_PROVENANCE_V4.json) / [SHA inventory](SHA256SUMS_RESUME_V4.txt)；synthetic fixture目录明确从生产artifact inventory排除，保留在磁盘供反例复核。
