# A1 raw35 冻结 mean policy：小型接入件 V1

**本件是 source/stdlib 交付，不是实际冻结评测。** 新增 helper，不新增 supervisor、不启动训练或仿真、不改旧封件。能力匹配：session catalog 只有 Office/ACL，不匹配 RL；实际只用 read/glob/grep/PowerShell 与 bundled Python stdlib。本地 Torch/SDK/GPU/原 PT/C/锁/GO/Git 操作均为 0。

## 1. 交付与 API

- [helper](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/frozen_a1_raw35_v1.py>)：导入时仅 stdlib；真正构建 actor 时才懒加载 Torch/RSL/TensorDict/已审 vendor 与 wrapper。
- [stdlib 测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/test_frozen_a1_raw35_stdlib_v1.py>)、[结果](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/CPU_TEST_RESULTS_V1.json>)：26 项，涵盖整根 CPU/单次读取、元数据反例、真实 forward AST 数值参考、history/reset/clip/冻结。
- [可选后续 CPU/Torch 检查](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/remote_cpu_synthetic_check_v1.py>)：**本次未执行**。只生成自己的 synthetic checkpoint；用真实原 wrapper、RSL 和 vendor Policy 作 4 步 mean 参考、混合 reset、RNG/加载后残差/冻结检查。父代理可在已有合适 CPU 环境、新的输出目录执行，不读 mother PT、不建 SDK。
- [机器可读 API](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/API_CONTRACT_SOURCE_V1.json>)。

```python
from frozen_a1_raw35_v1 import FrozenA1CheckpointCache
# source_final 来自实际 producer FINAL；expected_* 来自批准的实际 source entry。
# role_key 显式传入，既不猜等于 role，也不从不可信 checkpoint 自我授权。
cache = FrozenA1CheckpointCache(
    source_final, own_job_root=source_job,
    role=expected_role, role_key=expected_role_key, run_id=expected_run,
    asset_SHA=expected_asset_SHA, contract_SHA=expected_contract_SHA)
mean = cache.build_mean_policy(env.device, num_envs=80)

# 以下插在原已准入 eval loop，不添加 reset / obs.compute / sensor 采样。
first_or_done = torch.ones(80, device=env.device, dtype=torch.bool)
# obs 是原 harness 已经取得的原 noisy/delayed policy35。
action = mean.act(obs['policy'], episode_start=first_or_done)
# 原 begin/command-before/terminal observer 保持原位置。
obs, reward, terminated, truncated, extra = env.step(action)
first_or_done = terminated | truncated  # 传给下一次 act，非 xi1_valid。
```

若现有 vec.step 已返回原 `term|trunc`，直接沿用该 mask；不为取 mask 再采一次 SDK。原 E1 手动命令路径的 get_observations 已执行原 manager compute，保持原调用频次，勿再加一次来“同步”本 helper。第一帧/每个 reset 后的 10 帧全部重复**当前原观测**；普通控制帧仅 shift+append 一次。helper 不接管评测 recipe、episode UID 或成功记账。

## 2. 与实际 A1 保存格式对齐

[A1 worker:65–99](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_app_close_semantics_v5/worker_supermimic_bptt_app_close_candidate_v5.py#L65-L99>)保存完整 `pi`，含 `teacher.*`、`residual.*` 和 norm buffers，并把 role/run/role_key/view/family/variant/asset/contract 写进根；[full-resume save:493–511](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py#L493-L511>)另含 auxiliary、replay、RNG、history 和环境快照。这里读实际 FINAL 指定、在 own job 内的完整 checkpoint：一次 whole bytes、一次 SHA、一次 `torch.load(BytesIO, map_location='cpu', weights_only=True)`。核对 producer path/bytes/SHA、九项真实计数、iteration、teacher frozen receipts 和元数据；原 mother PT 不重开。

整个根与原 bytes 留 CPU，用递归 identity/version/schema 检查保持不变。仅严格拷贝 `pi` 的参数与 buffers 到独立 actor；**无 learner、optimizer、WM、critic、aux、replay 上 actor 设备，无 load/resume/RNG restore**。来源 N1024/T128/保存的 1024×10×35 history 保留原样；N80 只建立新的 inference history，既不切片来源 replay，也不把 N1024 物理/DR 快照应用到 N80。

[原 wrapper:70–82](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L70-L82>)的构造函数会把 residual 最后一层清零。因此顺序是**原 wrapper 构造 → 整个 pi strict load → eval/freeze**；加载后不再清零。不能换成另一个同名 residual wrapper。teacher 架构沿[原 constructor:43–48](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L43-L48>)：RSL MLPModel35→6、256/128/64、ELU、原 GaussianDistribution scalar-std 配置。均值调用 `stochastic_output=False`；STD 状态也严格加载但不采样。

Residual 用[原 Policy:194–222](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/networks.py#L194-L222>)：hist10、z32、goal3、hidden512/256/128，原 goal encoder 和 decoder；offset0、scale0.05、**base+delta 后总 clip[-6,6]**。核对 state keys、shape、dtype、数值有限及 norm var/count 非负；strict load 后逐 tensor 相等，不靠静默 dtype 转换。原 [RunningNorm:34–70](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_core_review/evidence/networks.py#L34-L70>)mean/var/count 严格加载、eval/nograd，无 update；buffer 版本和 eps/max_count、wrapper offset/scale/hist 持续冻结。构造 CPU 随机初始化用 fork_rng 还原全局 CPU RNG，mean 不加训练 action noise。

原[实际 collect:305–320](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_resume_runtime_v2/ctx_reward_full_resume_candidate_v2.py#L305-L320>)是 `ep_step==0` repeat-current padding，不是 zero padding。[Raw35ActorMDP:164–200](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_command_review_v1/command_tracking_torch_candidate_v1.py#L164-L200>)只用原 context 前35维与同一前3维命令；本件不引入 DR/clean sensor、UID 或新角度解算，也不修复原 held context/E2 reference 语义。

## 3. 沿原冻结评测接入，不用旧 PPO 入口冒充 A1

[旧 generic metadata](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_eval_generic_pair_v1/generic_eval_metadata.py>)和[旧 WholeCheckpointFreshCache:12–39](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/PAIR1_RETENTION_EVAL_SOURCE_V3/parallel_eval_safe.py#L12-L39>)期待 PPO actor/17-Adam/iter 等 A0 schema；只替换 PT 路径并不兼容 A1。保留原 scope/admission/group barrier/wait/物理评测 loop，显式新增 A1 checkpoint-provenance 与 actor 适配层。旧 actor/STD/optimizer probe 若依赖 `actor_state_dict` 或顶层 distribution，须按 A1 `mean.pi.teacher` 与完整 pi receipt 审查，勿静默跳过 gate。

[原 N80 接口说明](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/POSTTRAIN_EIGHT_EXCLUDING_H1_20261102/source_eval_generic_pair_v1/MINIMAL_SOURCE_FILE_MAP_AND_INTERFACES_V1.json>)保持：seed20260928；原 asset/physics/DR；0.0025s×8=0.02s，反馈100Hz；原 finite EX/private GPU EX/canonical read-only、组内同步与实际 children wait。E0/E2/E3/W35/C878/C113/S135/S50 原控制上限分别1000/1200/160/1600/750/750/750/1000。每角色/组完整原分母，stand 与 moving 不拼接，不改 speed/阈值/recipe/physics/DR。helper 的 source-pass 不是任何资源准入或 producer waited proof。

- E2：沿[原 terminal observer/loop:69–115](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/worker_five_original_n80.py#L69-L115>)及原 cycle 接口保留 episode/world UID、命令/profile/sign、实测 yaw 与世界坐标参考、自然完整周期/terminal 分母；不拿 history-reset 或训练 xi flag 代替。
- W35：沿[原 reset/interval hook:47–63](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/worker_five_original_n80.py#L47-L63>)的 natural interval 与 BODY 正/负轴；moving/standing 分开，partial/reset/timeout/window-close 保留原 ledger。
- E3：沿同一原 worker 的 first-episode/recipe/credited/实际 term-trunc callback；credited 不等于单步 delta，不把 helper reset mask 当恢复事件。
- E1：沿[原 endpoint loop:51–106](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_parallel_worker_safe.py#L51-L106>)的几何/Fz/顺序/首失败接口；[原 E1 vec:43–65](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/E1_N80_FRESH_FULLDR_PARALLEL_SKILL_SCREEN_SOURCE_V5_FEEDBACK_DESCRIPTOR/e1_fresh_runtime_bridge.py#L43-L65>)已取观测并返回原 done。
- [原接受契约](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_acceptance_review/EXPERT_90_PERCENT_ACCEPTANCE_CONTRACT_SOURCE_V1.json>)的 E0/S50 binary predicate 继续 null，不造 no-fall/边界/奖励 proxy。

## 4. 已知边界与下一步

本地仅 stdlib：缓存测试替换**私有 decoder**读取自己标明 JSON-not-Torch 的小型 synthetic 文件；数值测试只提取原 RunningNorm/Policy/wrapper 的纯 forward AST，以 fake arrays 和固定尺寸稀疏 MLP 作 reference。未运行真实 Torch decode/build、RSL 实际绑定、GPU/SDK、真实 A1 checkpoint 或 N80评测。[后续 CPU 脚本](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_eval_a1_raw35_v1/remote_cpu_synthetic_check_v1.py>)运行前由父代理安排环境与批准源；其结果也只证明 own synthetic CPU 条件。

vendor networks 与 native wrapper 的源码 bytes/SHA 固定；RSL 实际 class/module/file/SHA 会在后续 mean receipt 记录，但本次未取得其独立硬编码 source pin，需与原 frozen-eval 批准包核对。TensorDict/Torch 版本也由实际环境核实。`weights_only=True` 如遇未审的自定义全局/叶类型就停止，不自动换 unsafe decoder；形状/dtype/角色/变体不匹配同样停止，无母模型重开或 A0/B fallback。实际 A1 producer路径/bytes/SHA、remote CPU结果、resource admission/wait、实际通过率目前全部 unknown/null。
