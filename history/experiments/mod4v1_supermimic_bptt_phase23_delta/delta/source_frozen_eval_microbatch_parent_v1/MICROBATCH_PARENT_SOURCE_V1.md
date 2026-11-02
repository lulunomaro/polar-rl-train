# E3 + W35 独立 frozen-eval microbatch（SOURCE V1）

**交付的是可接入的新源码，不是实际评测。** 24/24 stdlib fake/AST 测试通过；本子代理 SDK/Torch/GPU/原 PT/原 raw/C 账户/锁/SSH/Git/训练操作均为 0。第一轮有 1 个新测试空格锚点 `IndexError`，仅修正 fixture；运行件未因此改动，历史单独保留。真实成功 producer/checkpoint、资源准入、冻结评测及 paired reference 仍待父主线提供。

## 1. 精确边界与原机制复用

- 新入口：[subset parent](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_eval_microbatch_parent_v1/single_gpu_e3_w35_a1_frozen_parent_v1.py>)。它只请求 `E3,W35`，并保留原八角色字典；`CURB_INDEPENDENT113,CURB_PROTECTED878,SLOPE135,SLOPE_INDEPENDENT50,E0,E2` 明确 **deferred**，不是失败、成功或零 exposure 的假 producer。
- [microbatch runtime](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_eval_microbatch_parent_v1/frozen_eval_microbatch_runtime_v1.py>) 在 import 时只校验并导入 reviewed 小 Python core：37927B / `7a092364cf63e9621481dc0a5554b56a22e4412cf89870c3db9a124864074b2e`。cache/caller/pose/close/actual-wait semantic 是原对象直接 reexport，没有另写 checkpoint loader、母本参考或优化器。
- 原八项入口、原严格八项 validator 和 [405 封版索引](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/FROZEN_EVAL_SEALED_SOURCE_INDEX_V2.json>) 保持原样。新 validator 仅将原函数的 **一个**八成员检查替换为新 batch schema；其余整个 AST 相同。没有向原 validator 塞假八成员来获得准入。
- [新 formal worker](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_eval_microbatch_parent_v1/worker_formal_a1_microbatch_v1.py>) 仅两条 import 切换到新 schema/barrier，原 accepted/DR/physics/commands/episode-boundary/control 循环全部保留。原 [NINE wait_start](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/parallel_eval_safe.py#L40-L48>) 还含九成员断言，故本 batch 必须使用新二成员 barrier，既不调用旧 8/9 barrier，也不放宽旧 barrier。

原 private GPU EX + global finite EX、canonical **只读** generation/remaining/minimum/active-owner 检查、1800s bounded resource wait、GPU 空卡且 free>=23500MiB/util=0、主机 RAM>96GiB/disk>25GiB、2400s deadline/900s scene-ready、进程实际 wait、仅 own children 的既有 cleanup 与 finally 解锁块均 LF/AST 对照不变。原函数包含其既有 own-eval timeout cleanup，本件没有执行它，更没有对当前训练父子进程采取动作。

## 2. Schema / API

详见 [API 合同](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_frozen_eval_microbatch_parent_v1/API_CONTRACT_MICROBATCH_V1.json>)。

`GROUP_PLAN.json` 必须是 `kind=A1_FROZEN_EVAL_MICROBATCH_GROUP_PLAN_V1`、`batch_purpose=A1_FROZEN_CANDIDATE_ONLY_E3_W35_MICROBATCH_V1`、`requested_roles=[E3,W35]`、原顺序六项 `deferred_roles`、`overall_eight_pass_rate=null`。`roles` 仍是全部八项原字典；只有被请求两项必须带实际成功 `a1_producer`，其字段/API 沿用 [reviewed core](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_a1_frozen_eval_integration_v2/a1_frozen_eval_runtime_v2.py#L121-L225>)。

每项原 controls：E0=1000、E2=1200、E3=160、W35=1600、C878=750、C113=750、S135=750、S50=1000。原 N80 / seed20260928 / 50Hz policy / 100Hz feedback / physics .0025 / decimation8 / TGS32,4 / closure .01 / mimic .01 / 400N,2000N/m,3Ns/m 及原 DR 不缩减。任务科学 cohort 的 `kind/purpose` 仍是原值，额外 mandatory `batch_purpose/requested_roles/deferred_roles/role_catalog` 才是本次独立调度 schema；实际 `eval_members` 是两项，不谎报八项。

- `select_requested_roles(plan)`：验证完整目录、两项成功 producer、原 scope 与候选-only reference-null，再返回两项。
- `make_task(role,plan,deadline,fds)`：原 task maker + 新 subset 字段；资源仍必须由实际父原门准入。
- `validate_group_task(...)`：保留原 fd/GPU/admission/scope/producer/source checks，仅替换成员 schema。
- `wait_start(task,out,group,ready)`：先写 zero-control scene-ready；只有相同 group/GPU/purpose 的两项都 ready 才继续。原环境 reset/observation/sensor/RNG 顺序不变。
- `evaluate_waited_eval_case`：原 reviewed 函数对象，**只在原 `p.wait()` 后**调用；RC、错误、完整 FINAL/checkpoint/cache/source/controls/boundary/env/App close/intent gates 全保留。

不要求训练达到3000；必须是原完整保存/实际 closewait/cost-close 和锁释放后的成功来源。计数不是技能通过率。全根 CPU 缓存、仅 pi 冻结 mean、mother PT0、N1024 replay/DR/history 不 slice/restore、learn0 等原 core 约束保持。

## 3. 新 root 的安装和精确 CLI（本轮未执行）

用最终 `MICROBATCH_STAGE_INDEX_V1.json` 的 pin/mapping，保留原全部静态工厂/asset/config/accepted observers 与其它 `worker_files` 依赖。reviewed 12 mapping 中的 runtime/loader/pose/App/vendor/E1 等十项原样；新 root 的 formal alias 改装本件 **两 import** worker；入口选下面新 parent，而不是旧 eight parent。旧 eight parent 原封件/原目录始终保留，不在其上编辑或启动 subset。

```text
single_gpu_e3_w35_a1_frozen_parent_v1.py -> NEW_GROUP/single_gpu_e3_w35_a1_frozen_parent_v1.py
frozen_eval_microbatch_runtime_v1.py     -> NEW_GROUP/frozen_eval_microbatch_runtime_v1.py
worker_formal_a1_microbatch_v1.py        -> NEW_GROUP/worker_sources/parent/worker_five_original_n80.py
```

父 stager 必须把最终所有依赖（含本件三项）当前 bytes/SHA 写入新 plan 的 `worker_files`，实际父在 SDK 前逐项核对。不能沿用旧 worker pin 冒充新 import copy。

```sh
OWN='/home/lc01/Zonglin Li/zonglin2'
NEW_GROUP="$OWN/tasks/NEW_DISTINCT_E3_W35_FROZEN_EVAL_ROOT"
# 已安装正确 source mappings，且父提供真实 producer FINAL 后：仅元数据校验，无资源准入
"$OWN/run-python.sh" -u -B "$NEW_GROUP/frozen_eval_microbatch_runtime_v1.py" \
  --validate-plan "$NEW_GROUP/GROUP_PLAN.json"
# 仅父按原资源/预算门重新核对后，由父决定启动；本子代理不执行
"$OWN/run-python.sh" -u -B "$NEW_GROUP/single_gpu_e3_w35_a1_frozen_parent_v1.py"
```

## 4. 结果口径

`all_requested_actual_execution_complete` 是两项 **执行**完成，不是技能成功；终端 RC0、actual waited 和原 semantic success 均须成立。E3 按原 recipe0..11 的 first-episode credited / **74** 报绝对 owner-credit 率，normal recipe12 的6项单列，不补入 rescue；credit 后才发生的终止照原 prefix 语义保留。缺 recipe/错 cohort/非整数计数时 rate=null，不猜阈值。

W35 原 FINAL 的合计 natural-complete/true/false/partial 计数照录；由于未含 moving/standing 分组，**moving_rate/standing_rate=null**，不将合计 true/complete 冒作 moving 率。null 不表示失败或成功。其余六项 deferred；`overall_eight_pass_rate/all_eight_actual_execution_complete/subset_pooled_skill_rate/comparison/relative_improvement/UID_alignment/reference_cache_match/reward_effect_identification` 都 null。E0/S50 原 binary 缺口仍 null。母本 reference 只保留相同 planned reset/seed/pose 协议；actual reference 本版未实现，计划字段 `reference_actual_receipt` 必须 null，不以配置相同推出实际配对。

## 附录：W35 下轮只读 split consumer 的精确接入口（本轮未实现）

原 [rm70_intervals227](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py>)：**14185B**，SHA256 `d84182d3675f41d53d35da54c4d80519b9b2280ccb6d3f47f33cfff64029d609`。
原 [positional_rows227](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/positional_rows227.py>)：**6557B**，SHA256 `72627c449b8ce071bcf278027ef1f9fe6a32ab7f2d20910e895fb13bf8f3fd29`。只 hash/read Python source，未读任何 JSONL。

| 原 API / 位置 | 已存在事实、将来可读字段 |
|---|---|
| [emit_columns(self,columns,extra):135–137](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py#L135-L137>) | 原 columns 只转 CPU/list 一次，每行 `self.rows.append(row)` 一次；这里之后的 row 已是 Python native。未来可在 NEW row consumer 接收副本，不加 SDK getter，不再次转 Tensor。 |
| [close(self,ids,reason,natural):138–170](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py#L138-L170>) | record_type=`same_UID_original_RM70_command`；`standing` 为原 Boolean；`natural_complete_nonterminal_interval`、`original_kinematic_bounds_met`、`complete_interval_bounds_fact` 已计算，不要用速度阈值推 standing 或重写成功阈值。complete 且 fact=False 是原条件 false；complete=False 是原 partial 类，不补入条件分母。 |
| [原 row 字段:151–168](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py#L151-L168>) | `env_id,episode_uid,command_uid,source_E1_episode,original_command_counter,same_UID_segment,start_observed,first_control,last_control,controls,seconds,first_physics_tick,last_physics_tick,terminated_before_reset,truncated_before_reset,end_reason,original_terminal_reason_*` 均已存在。axis/command、along/cross/yaw error、tol/closure/mimic 也在同 row。缺 UID/Boolean/type 或源绑定时另记 Unknown，不拼 episode/command，更不声称跨 candidate/reference UID 对齐。 |
| [book.finish(self):184–190](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/rm70_intervals227.py#L184-L190>) | 先 close window-end partial 和 routes，再返回 pooled events/reasons/producer；events 初始化及累计都没有 standing/moving split。route goal 是 observer-only，不能替代 interval skill。 |
| [PositionalRows227.append(row):99–135](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/positional_rows227.py#L99-L135>) / [finish():137–151](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/positional_rows227.py#L137-L151>) | 将来 NEW wrapper 可复制已产生的原 Boolean/UID 做增量计数，但须原 append **exactly once**、原 row 不改、route rows 单列。保留192MiB cap、retained/dropped/attempted 计数与 producer SHA。finish 仅有 schema/bytes/SHA/rows/limit metadata，不含各组成功数；`field_union` 不是分组计数。 |

下轮可在原 writer 已构造的 row 边界做独立 split，并在其原 finish 完成后合并小 metadata；不得额外 reset/obs/RNG/物理步、不得据缺 UID 猜配对、不得优选保留成功行、不得把 retained 与 attempted 暗中互换。本件只提供字段证据和入口，未实现该 consumer 或读取 raw，也没有生成90%主张。
