# A1 frozen N80 原评测集成：SOURCE-only V2

## 1. 交付状态

本件只交付 **NEW candidate 源码、原源绑定、白名单 diff 和 stdlib fixture**。45/45 测试通过，耗时 0.422 秒；实际 frozen 评测次数为 0，Torch/SDK/GPU/SSH/原模型 PT/原 raw JSONL/NPZ/C/Git 操作为 0。未安装 candidate、未启动资源父进程、未读取或 stat/hash 原模型，V6 与此前封件保持原样。

本地测试是 fake tensor/metadata 与真实小源码 AST/PIN 核验，不是 Torch actor 数值、实际 checkpoint I/O、实际资源准入或技能通过证据。

- [最终测试回执](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/TEST_RESULTS_STDLIB_FINAL_V2.json>)
- [测试源](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/test_frozen_eval_integration_stdlib_v2.py>)

## 2. 真正的前 POSTTRAIN 原件

绑定依据是原 [NINE 实际 GROUP_PLAN](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/reports/NINE_SINGLE_GPU_V8_CLOSED_20261102_101543/GROUP_PLAN.json#L135-L274>) 的 `worker_files`，而非事后派生 PAIR1 或 N20000 训练 owner。

| 原件 | bytes | SHA256 |
|---|---:|---|
| [原 NINE parent](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/single_gpu_group_supervisor.py>) | 9247 | `7c826b983887cb9ec890c92737095c5e7e7d93538fafaa211021fea2e0d9fc27` |
| [原 formal worker](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/worker_five_original_n80.py>) | 14735 | `aff36092bf1502a6bedd5d4b347b6eb1e5675996cd191c58fbcda7b4f9bc5b1c` |
| [原 E1 worker](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_parallel_worker_safe.py>) | 16275 | `f1218603d369f955a855d45ac97441901ee022f45055f45fdb001e8601d8b795` |
| [原 E1 bridge](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_fresh_runtime_bridge.py>) | 6110 | `59ab2e23ab7d28129391c7897f8f9661ca39f94634be414dfacf047a89fc5c30` |

原 NINE 含 H1；新评测只去掉 H1，保留 E0、E2、E3、W35、CURB_PROTECTED878、CURB_INDEPENDENT113、SLOPE135、SLOPE_INDEPENDENT50。

原有限长度依次为 E0=1000、E2=1200、E3=160、W35=1600、C878=C113=S135=750、S50=1000 control。每角色独立 fresh N80，seed=20260928，physics_dt=.0025，8 physics/control，control_dt=.02，100Hz feedback，TGS[32,4]，原 full D0-D7、闭环 .01m、mimic .01rad、gas400N、stiffness2000N/m、damping3Ns/m 均保留。原 geometry/factory、E2/W35 observer、endpoint、forces、reward、termination 与 accepted denominator 不改；E1 整段原控制采样循环 AST 相同。

原 scope 的局限也保留：E0 原二值技能谓词仍有缺口；E2 point/frame/clock 绑定未由本件实际验证；E3 仅原 160-control 首 episode scope；W35 原 gentle/fixed .3 bin 不是新高速度总体；S50 不借用 S135 的 27/27/26 接受规则。无新 aggregate graduation 或 90% 声明。

## 3. NEW candidate 与白名单

- [适配 runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py>)：A1 cache/caller、真实终止边界、配对 pose、严格来源、durable error 和 App/wait metadata 语义。
- [formal candidate](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/worker_formal_a1_frozen_candidate_v2.py>) → `worker_sources/parent/worker_five_original_n80.py`。
- [E1 candidate](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/e1_parallel_worker_a1_frozen_candidate_v2.py>) → `worker_sources/e1/e1_parallel_worker_safe.py`。
- [E1 bridge candidate](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/e1_fresh_bridge_a1_frozen_candidate_v2.py>) → `worker_sources/e1/e1_fresh_runtime_bridge.py`。
- [八角色 parent candidate](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/single_gpu_eight_a1_frozen_parent_candidate_v2.py>) → `single_gpu_group_supervisor.py`。
- [可重放 builder](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/build_frozen_eval_candidates_v2.py>)：测试在 NEW fixture 目录生成四份 candidate，逐字节匹配当前四份文件。

只有 actor/cache/resume-hook、original-reset 前 pose 安装、真实 term/trunc 传递、错误/关闭/父等待语义和相应身份 metadata 白名单。父进程原 admission 与 finally 清理块经 CRLF→LF 后文本和 AST 相同；不称跨换行的 raw bytes 相同。保持 privateEX + slotfiniteEX、单 canonical authority/C 只读检查、VRAM23500/util0/RAM96GiB/disk25GiB、1800s/retry15s、900s barrier、2400s worker deadline、原 own PID creation/root identity cancellation、全部真实 wait 后 unlock 的顺序。无新 C/账本写入或私设资源准入；actual cost-close 仍由原 canonical parent 主线提供。

最终源码/bytes/SHA/12 aliases 与精确 diff 见封版清单。早期构建回执和早期 diff 仅是生成历史；最终清单与 FINAL_WHITELIST diff 才对应当前源码。

## 4. A1 正确输入与一份 own CPU cache

严格委托未改的 [sealed frozen helper](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py>)，PIN `19226 / 1ea4bcfa1081d63d0da2136fedf8c9fafa508d7bb2155095352da496327e4a21`。

Future worker 必须取得本角色 actual successful A1 V3 FINAL（正确 role/key/run、raw35 view/family、nine named counters、完整新 checkpoint receipt），并核对真实 FINAL metadata bytes/SHA。然后只有 helper 对 own `production/checkpoints/*_complete.pt` 做 single bytes read / single SHA / single BytesIO CPU decode；whole root 留在 CPU 并以 identity/version 保持。没有母本 PT 再开、旧 RSL actor-state loader、旧 N1024 replay/history 切片、环境/RNG restore 或 live WM/critic/optimizer restore。

GPU 只构造整份 A1 `pi`：嵌入 teacher + 已训练 residual + frozen norms，wrapper 初始化在 strict pi load 前完成，hist10 / z32 / hidden512,256,128 / residual .05 / offset0 / action clip6 均由原 helper 固定。

actor 只看到原 env 的 noisy+delayed raw35；goal 是同一 raw35 前三维。critic38/privileged DR/UID metadata 不进入 actor。E1 仍每 control 调一次原 observation_manager.compute；formal 保留原 observation 调用数，无新传感器重采样或零噪声替代。

历史 mask 为首 action 全 True，其后精确使用 **上一原 env.step 返回的 true terminated OR true truncated**；不是累计 first-episode-ended、当前端点过滤、timeout 丢弃或任意 UID。reset 当次历史重复当前 raw35，其余 action 仅追加一次。formal 在原 env.step 后立即 observe_transition；E1 vec 独立保留原两个真旗标后再返回旧 combined done 接口。

observer 的 source_path/SHA/bytes 也绑定 admitted own A1 checkpoint，避免 W35 raw 身份仍误标旧母本 SHA；这只是 metadata，未注入 actor。

## 5. Reference 选择与 actual evaluator 绑定分离

父代理 [source selection](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/EVAL_RSL_REFERENCE_SOURCE_SELECTION_V1.json>) 明确为 executing parent-agent 选择，不是新增 human approval，也不是原 native-GPU 已观测同源。

实际 CPU 证据是 [A1 CPU mean 回执](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/reports/A1_FROZEN_MEAN_POLICY_CPU_V1.json#L13-L37>)：own synthetic checkpoint 的真实 Torch，4×N80 controls，对原 wrapper reference maxerror=0.0。实际 class=`rsl_rl.models.mlp_model.MLPModel`，source bytes=10334，SHA256=`6219ebb3ed4df036dae7ff1c30d0fbb169eaaa659e44a659dd757a292124476b`。CPU 报告 8696B / `0329771e37873d17bf3f806b9caa27b0ef669fec3fbf3e334ff28924094925f0`。

NEW task/cache receipt 保留 `approved_reference_provenance`、`approved_RSL_model_source`，以及独立的 `actual_eval_RSL_source_binding`。原 native-GPU source-observed 字段为 null。未来 eval 必须自己从实际 class/source 验证 module、qualname、bytes、SHA；不同则首 action 前结束并走原关闭流程，不做版本/架构猜测或旧 actor fallback。旧 sealed helper 未增加 hardcoded PIN，旧审批事实保持原样。

## 6. Pose 修复与配对 reset 协议

沿用原 [pose V4](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/pose_cache_runtime_adapter_v4.py>) 的 18161B / `7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f`，以原 logical v3 alias 安装。安装时机固定为 env construction 后、原 sole explicit reset 前；E1 factory 的内部 reset 保持原状，hook 位于原 attach_fresh_guard 入口。SDK constructor 内部初始化不被改写为“零次 reset”。

母本与候选 planned protocol 必须完全同 pose PIN/version/timing、N80/seed、原时钟与 noisy-delayed35；历史 bug baseline 标志必须 False。实际新母本 paired protocol/UID/cache 证据仍是缺件。本件交付 A1 candidate，不假称已实现或执行新母本 paired worker。即使 task 声明 reference_actual_receipt，也只记录为 declared metadata；`reference_receipt_verification`、`actual_reference_same_protocol`、UID/cache match、paired/reward improvement 仍为 null。先有实际同协议母本/候选回执，再讨论配对结果；pose/cache correction 与 teacher 合法性也不混成 reward/tracking 增益。

## 7. 错误、App close 与实际 parent wait

错误先 fsync `WORKER_ERROR`；secondary 和 cache-receipt 失败保持首个错误。E1 原 optional partial NPZ 写之前先 durable error。原 env.close / App.close 各一次，绑定仍是未改 [App V6 helper](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_runtime_compat_v6/app_close_semantics_v6.py>) 的 exact published class/MRO/source/PIN；不改 fast_shutdown 或替换 close。

Fast shutdown 可能直接 hard-exit0：NEW 只写属于 eval FINAL bytes/SHA 的 fsynced pre-close intent，随后 original App.close。父原 `p.wait()` 返回后才校验 semantic。RC0/error/缺 FINAL/不完整 controls/不完整边界/错误 source/PIN/hash/cached root/缺 env close 都按原错误处理。SystemExit(0) exception 不冒充 hardexit0。非 fast 模式必须真实 returned close metadata，且同样严格校验原 class/MRO/source；不靠 intent 单独通过。

这不是 training FINAL validator 的复用或伪造。stdlib fixture 的 wait/source metadata 也不冒充 actual resource admission、实际 App hardexit 或 cost-close 证据。

## 8. 最小剩余件与未来新窗口接口

1. 每角色实际完成后的 A1 FINAL / full new checkpoint bytes-SHA / own role-key-run 九计数；由父主线提供，本 agent 不碰真实 PT。
2. NEW 独立 eval root，原已核验静态工厂、config、assets、worker dependencies、四个 E1 wrapper 与原 accepted predicates 全量保留；只按 12-source alias 清单做新 root 的 candidate/source additions，worker_files 重新填当前源码 SHA。不 hotpatch 当前在跑 V6。
3. plan 包含原 eight `roles`、group/GPU/asset/contract identity、每角色 `a1_producer={own_job_root,FINAL_path,FINAL_bytes,FINAL_SHA,FINAL,role_key,run_id}`、严格 paired planned protocol；reference selection 已由父代理明确，可采用本 runtime 的相同默认 selection/provenance，actual evaluator 仍自行验证。
4. 实际 fresh N80 actor 软件/原 SDK 接口、actual resource admission、App source binding、parent wait 与 cost-close 的新窗口证据；本件结果均不代替这些。
5. 如要比较提升，还需新母本同 pose/reset protocol 的 actual paired eval、原 accepted UID/denominator/reference cache/point-frame-clock 对齐。当前全部 explicit null，不推导通过率。

原资源阈值、等待窗口、物理 DR、命令分布和成功阈值均未缩减。父代理决定是否及何时在新窗口启用。

## 9. 通过率优先与短段/小批的自然关闭边界

父代理转达用户 23:39 修正：增加训练量服务于通过率，3000 只是规模计划，不是验收或评测启动门槛。本 runtime 不要求 producer BPTT>=3000；小段真实计数 + actual successful FINAL + 完整 own save 即可作为 candidate 来源，不能补计数或拿 startup 推导成功。

未来 stage executor 的顺序应是：短段/小批训练 → 原完整保存边界 → 原 owner 实际等待、cost-close 并释放 finiteSH/private locks → NEW purpose 的冻结母本/候选同口径复测 → 有效才扩量；退化则保留母本并归因。当前已准入 owner/worker 不热改，不强杀打断结账，不为了评测复用仍 held 的 slot 或私锁。

本件保留的具体 group parent 是严格原八项 coverage/barrier，不是一个已实现的两角色 micro-batch parent。它不等待八项都达到3000，但需要八项各自已有合格完整来源。若未来按单角色/小批先检验，须用 NEW batch-purpose parent/admission schema 复用本 cache/caller/close-semantic 组件，按每角色原 N80/seed/accepted denominator 报告；原八项总体 coverage 和结论在其余项完成前保持 null，不能把被选 subset 的通过率冒作八项总率。本轮冻结源码，不继续扩 batch 调度而拖延效果验证。

## 附录 A：从同一 own A1 cache 构造母本 teacher 参考的验证路线

这是可复核设计路线，不是已实现或已观测的 paired 母本结果。

1. 由本件 single-read full A1 cache 保留 whole root CPU；原 strict pi load 包含完整 `teacher.*` 参数/缓冲。原 [TeacherResidualPolicy](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/native_supermimic_bridge.py#L70-L82>) 的 base 是 `self.teacher(TensorDict(policy=raw35), stochastic_output=False)`，无额外 teacher 历史通道。
2. 在 NEW reference helper 中，从同一个 cache 的 `root['pi']` 选取完整 `teacher.` 前缀并去前缀，只允许构造原 source-selected MLP class/schema后 strict load；或者直接使用已经 strict-loaded 且 frozen guard 覆盖的 `mean.pi.teacher`。不得新开母 PT，不从 N1024 replay/history/privileged context 造 actor 输入。构造临时随机权重不 restore producer RNG，并需避免扰动 paired env 的原采样序列。
3. 除 metadata 的 `teacher_unchanged` 外，还核验 actual producer 对真实 teacher weights+buffers 的冻结断言、teacher checkpoint provenance、嵌入 teacher 全键/shape/value 完整性与 evaluator 实际 class/source PIN；进行独立 CPU deterministic base/reference 等价和冻结负向测试。字段或 source 证据缺失则保留 unknown，不宣称与原母模型独立等价。
4. 母本与 candidate 使用两个独立 fresh N80 env，同 pose/reset/seed/raw noisy-delayed35/accepted UID 协议，history 与 fresh episode mask 各自从本 env 获得。新母本窗口不沿用历史 cache-bug baseline；raw/cache/reference 对齐、原分母、实际关闭与资源回执分别保存。
5. 此路线还需要 NEW reference worker/CPU math/paired-runtime 验证。本轮未实现或运行这些步骤；当前 paired reference、UID/cache match 和 reward effect 仍为 null。共享同一个缓存的来源便利不等于已完成 paired 实测，也不把 teacher 合法性或 pose 修复归作 reward 增益。
