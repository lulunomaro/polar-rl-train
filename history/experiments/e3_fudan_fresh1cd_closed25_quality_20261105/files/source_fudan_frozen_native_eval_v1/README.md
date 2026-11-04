# Frozen FDN sequence mean — original E3 N80 native worker

仅准备新的实际评测源码；不包含 owner/stager，也不选择或打开任何真实模型。
本任务下达时 W2 已 1800 秒 preGO timeout，未创建 worker；它不是成功训练或可用候选。
新低趴 8s 测评不在此实现中。本次固定原 13 recipes、74 个恢复请求与 6 个 normal。

## 文件与静态依赖

本目录的新入口和辅助件：

```text
worker_fudan_original_n80.py   E3-only original worker + frozen policy lifecycle
fudan_frozen_eval_safe.py      new complete-save CPU cache, one-member barrier, close evidence
frozen_sequence_mean.py       定稿适配器的逐字复制；未改接口/源码
n80_gpu_capacity.py           原 N80 allocation-only preset，逐字复制
launch_storage_contract.py    原 Kit storage route，逐字复制
app_close_semantics_v6.py     完整 V6，实际仅用 _pin_original_app_close
resume_runtime_contracts_v3.py 完整 V6 必需的 stdlib import 依赖，逐字复制
README.md
```

完整 runtime 继续使用原 E3 N80 已证明的全部静态树：B/lib、B/runtime、资产、原
original_run_manifest、原 MOD4_RESET_COLLISION_BANK 及全部间接 DR/contact/feedback/
PD/termination/task 依赖。上面的 7 个 Python 文件仅是新入口闭包，不是可剪枝的
完整 SDK runtime。父侧 materializer 不得按这里的直接 import 列表删减原 runtime。
本目录不含 PoseV4、训练 lowrise26 patch、训练 learner 或新的测试夹具。

复制身份（均为源码 FILE SHA，不是模型身份）：

```text
frozen_sequence_mean.py 20812 bytes
882740577d39d13d7c76a6dfb9816300cb0ab15d143fe05507c1d17714eff925
n80_gpu_capacity.py 653 bytes
ab26d1b22557e6a85231795cd41c52aa53b81e69661c8a62f4c72118a62c74cc
launch_storage_contract.py 117 bytes
e40b51db4bca2f322cc2c9b4b0fe011eed292ae605f4f175f268a5bf90326047
app_close_semantics_v6.py 27769 bytes
3d2d75196fb98fdb45c80a79b5b8bb69873e7c0c2c0b0f6f6610eb11a8c63c39
resume_runtime_contracts_v3.py 22337 bytes
dc4bc67193457a4fb72b125d23fa482cd3d686363bd1a93eb07268f4e4e26cb7
```

## 实际 API 和一次读取语义

[缓存/闭环辅助件](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/source_fudan_frozen_native_eval_v1/fudan_frozen_eval_safe.py>)
提供如下 API；worker 接受与原父相同的 CLI 形状：

```python
task, case_root, group_root = task_args()
cache = WholeFDNCheckpointCache(torch, task)
policy = cache.policy(env.device)
policy.initialize(first_actual_obs["policy"])
# 每次控制：
actions = policy.act()                  # [80,6], deterministic mean, clipped6
obs, reward, terminated, truncated, extra = env.step(actions.clamp(-6, 6))
policy.observe(obs["policy"], terminated | truncated)
cache.check_policy(policy)             # 收尾时；不改变源/权重/history
cache.receipt()                        # JSON metadata only
close_original_resources(task, case_root, env, namespace, cache,
                         execution_error, controls_completed=completed)
```

```text
python -u -B worker_fudan_original_n80.py --task CASE/task.json --group-root GROUP_ROOT
```

父绑定的 **新完整保存**只作一次物理 read_bytes、一次文件 SHA、一次 CPU decode。
原始整份 bytes 与整个 N4096 CPU root 全程保留；Mapping/OrderedDict、Tensor 的
对象/版本/shape/stride/storage/content 与 NumPy 内容/元数据作 CPU 不可变核验。
CPU 内容守卫的叶子 digest 不属于 FILE SHA 计数，也不用于冒充文件身份。
只检查保存的两个 Adam 的结构、非空参数状态和 step 标量与新分支计数一致；
不实例化 optimizer、不套旧 RSL17/旧 iter/LR 规则，不恢复任何状态。

只把 actor 8 张量与 encoder 6 张量 clone 到 policy device。定稿 adapter 先构造网络
再 strict-load；缺键/未知键/错误形状立即失败。14 权重 digest 单独标为
selected_pi_weight_digest_NOT_file_SHA。CPU root 的 critic、log_std、Adam、训练
history、DR、queue、episode、RNG 均不切片、不 apply、不恢复到 N80。
绝不重新打开 1cd 母文件：路径和母 SHA 在选中新文件物理读取之前排除，root 内
母 receipt 仅作为已保存的 provenance 元数据核验。torch.load 在唯一 decode 后
被阻断，原 factory 再尝试读取其它 PT 会留下错误并终止本次目的。

原第一份已 noisy raw35 重复五帧；每个 step 返回的同一份 raw35 只 append 一次。
done 行重复自己的这份观测，其余历史独立前移。act 不 append；不加真实 bodyV、
不读取 critic38 作为 actor 输入，不额外调用观测或抽传感噪声。critic38 只延续原
worker 的形状/有限检查与日志。命令误差统计中的真实速度是原日志，不送 policy。

## 父必须绑定的字段：没有新的父进程实现

仍由已有单成员原父持有 private GPU EX + global finite EX、pass_fds、准备 runtime、
发 ready barrier、实际 child.wait 和释放资源；本目录没有 flock/解锁/预算操作。
保留原原生入口、完整 runtime manifest/worker_files 哈希准入、deadline 和私有目录。
父应先从真实新训练 FINAL + 训练 close intent + 原 owner actual wait/无错误中，
资格确定精确完整 save；不能把 dispatch/preGO wait/timeout 当训练完成。

沿用原 task 的物理、准入、group/GPU/source/runtime 字段，并明确以下新字段：

```json
{
  "kind": "E3_FDN_SEQUENCE_FROZEN_ORIGINAL_N80_V1",
  "purpose": "E3_FDN_SEQUENCE_FROZEN_ORIGINAL_N80_V1",
  "role": "E3",
  "num_envs": 80,
  "controls": 160,
  "seed": 20260928,
  "policy_interface": "fudan_sequence_raw35_history5_latent3_clipped_mean_v1",
  "evaluation_scope": "ORIGINAL_E3_74_PLUS_6_NORMAL",
  "owner_parent_pid": "ACTUAL_PARENT_PID_AS_INT",
  "source_path": "EXACT_SELECTED_COMPLETE_FDN_SAVE_PATH",
  "source_bytes": "EXACT_FILE_BYTES_AS_INT",
  "source_SHA": "EXACT_COMPLETE_FILE_SHA256",
  "source_run": "EXACT_SAVED_RESOURCE_BINDING_RUN",
  "source_training_execution_qualified": true,
  "optimizer_updates": 0,
  "fresh_fullDR_cohort": true,
  "state_projection_or_slicing": false,
  "policy_hz": 50,
  "feedback_hz": 100,
  "physics_dt": 0.0025,
  "TGS": [32, 4],
  "closure_m": 0.01,
  "mimic_rad": 0.01
}
```

占位整数必须由父填实际整数。保留原 asset_SHA/contract_SHA、runtime_root、
absolute_worker_deadline_epoch、group_id/GPU_UUID、actual_group_admission 和其两个
实际 inherited_lock_fds。原 make_task 后需设置新的 kind/interface/scope/owner PID
等描述字段；不改变它的锁获取/等待/释放。删掉旧 source_iteration/source_Adam17/
source_LR：它们不是新 FDN root schema。可额外绑定 expected_learner_counters 和
expected_native_counters；前者为四个 learner 计数完整 dict，后者可为 native 计数子集。

默认强制 require_native_updates=True，并绑定 source_run；要求完成的 T48/N4096
新分支 updates>0、main/encoder 两个 Adam 的 5×4 步数>0，native/physics/feedback
计数一致，拒收 error-path 保存。母 receipt、fullstate 结构按新训练 V2 root 校验。
source_training_execution_qualified 只是父的描述，不是 child 对训练 owner wait 的
独立证据；缓存对此始终输出 external_training_FINAL_actual_wait_verified_by_worker=False。
父原有证据负责这部分。新 worker 只自行证明选中文件的 bytes/SHA/run 与解码内容。

## 真实 FINAL、fsynced intent 与外层 wait

保留原 case 名称和原日志：

```text
FRESH80_FULLDR_BEFORE_CONTROL.json
WORKER_SCENE_READY.json
WORKER_EVAL_STARTED.json
FINAL.json
PRE_CLOSE.json
SDK_FULL_STDOUT_STDERR.log  (仍由父捕获)
```

新增 FDN_N80_APP_CLOSE_INTENT.json。所有 worker 输出
采用 exclusive partial + flush/fsync + 原子发布 + directory fsync，保留失败，不重试目的。

```text
FDN_N80_APP_CLOSE_INTENT.json
WORKER_ERROR.json
ENV_CLOSE_ERROR.json
APP_CLOSE_BINDING_ERROR.json
CLOSE_EVIDENCE_ERROR.json
APP_CLOSE_ERROR.json
```

顺序：控制收尾/不可变检查 → 真实 FINAL → 原 env.close → V6 Python/source 绑定 →
CPU 源 root 再核验 → fsynced intent → **立即原 app.close() 零参**。不改 fast_shutdown
或 App 配置；不安装 PoseV4、close monkeypatch、额外 sim.stop 或替代 lifecycle。
只复用 V6 的 _pin_original_app_close，不调用它的 SM-only FINAL/close/wait 判据；
完整 V6+V3 依赖已随源码交付。异常包括 SystemExit 都形成 error，不把 RC0 视为替代。
证据失败仍尝试原关门，但不生成合格 intent。

父最小资格变化：原 single_gpu_group_supervisor 第 59 行的
RC0 + FINAL.passed_execution + PRE_CLOSE 不再足够。原 actual child.wait() 和锁保持
逻辑不变，增加以下 conjunction（这是接入要求，不是这里新启动的父逻辑）：

1. 实际 wait 的 PID 等于自己启动的 worker；实际返回码 0，非 poll/意图推定。
2. 读取真实 FINAL，kind/group/GPU/role/PID/parent/task SHA 与本次 task/child 一致；
   num_envs=80、controls=160、seed=20260928、physics=1280、feedback=320、delay 两路各1280。
3. 读取真实 intent，其 final_path 指向本 case FINAL，final_sha256 等于 FINAL 实际字节；
   group/GPU/role/PID/parent/task SHA 与 FINAL/本次 task 一致。
4. intent.env_close_returned=True、error_before_close=False、close_errors=[]；V6 原 App
   binding 的 exact_class/method/source pin 与本次已绑定 helper 一致。原 App source pin：
   48933 bytes / SHA6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903，
   close 定义行848，合法模块名为 isaacsim.simulation_app.simulation_app 或
   simulation_app.simulation_app。fast_shutdown 是原实际 bool，不能为通过而改配置。
5. FINAL 与 intent 的 source_binding 都等于父选择的 path/bytes/FILE-SHA/run；缓存
   三个一次计数均为1、whole CPU guard 通过、原生+双 Adam provenance 正、policy
   actions/observe 都为160且不 pending、权重前后不变。14 权重 digest 不是 FILE-SHA。
6. 上列全部 error sidefiles 不存在，父自身无错误/超时/终止；ready/start/PRE_CLOSE
   仍须齐全。intent 或 APP.close 的正常返回本身不代表父 wait 已完成。

父应在原 terminal row/已有结果中记录此资格，保留失败记录；不建新的审计/封装流程。
worker 的 passed_execution 只指本次控制过程；最终资格由父上述实际闭环决定。
技能毕业字段仍为 false；按原 first-episode recipe rows 读恢复事实，不增加新合格率。

## 对原 worker 的精确差异

原参考：
[worker_five_original_n80.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/worker_five_original_n80.py>)；
[parallel_eval_safe.py](<F:/RMPOLAR-RL/mod4v1_experts_fulldr_rm70_20261101/NINE_N80_PARALLEL_SOURCE_V8/parallel_eval_safe.py>)；
[原单成员 stage 参考](<F:/RMPOLAR-RL/mod4v1_e3_continue_v2_20261104/stage_e3_frozen_after_close_v2_once.py>)。
没有执行或修改这些文件。

| 原位置 | 新入口的精确变化/不变项 |
|---|---|
| worker:4、31；safe:12–39 | WholeCheckpointFreshCache/RSL actor 改为 WholeFDNCheckpointCache/FrozenSequenceMean。新 root schema，不检查旧 iter/17Adam/LR/STD，不建 rsl MLPModel/critic/Adam。 |
| worker:9、17–28、47–51、69–71、76–77、87–95、113–115 | 固定 E3，删除其它角色的不可达分支；完整 E3 runtime 静态依赖仍全部保留。 |
| worker:14–16、22–23、29、34、43、50–53、60–63 | 原 factory、CLI N80/seed、capacity、显式 fresh reset、13 fall bank、fullDR/物理/反馈/DR getter 与首份 observation compute 顺序保留；新增原 phase 模块/recipe=arange80%13 身份检查，未改 task。 |
| worker:63–65 | 去 TensorDict/actor_obs；首份已有 noisy raw35 进入 initialize。接口显式 raw35×5→latent3→actor38→6；critic38仅日志。 |
| worker:72–86、96、108–112 | 原 termination compute 包装、pre-reset first_episode_live/credit/term 和13行 recipe 事实保留；显式请求分母74、normal6排除，不拼接 reset。 |
| worker:97；safe:40–48 | 原 empty_cache/零控 ready/barrier 顺序保留；仅一个 E3 member，ready900s/父原deadline不变。 |
| worker:98–107 | 160次循环、命令快照、clip6、env.step、有限检查、物理8×/反馈2×/delay8×保持；唯一策略生命周期变化为 act 后用本次返回 obs/done observe 一次。 |
| worker:116 | 大部分 case/termination/reward/skill 字段保留。新增新分支/provenance/PID/task/history接口；不伪造 actor_STD/RSL_clip/旧20k源字段。max_raw_action_abs=null：adapter已clip，另记 max_policy_return_action_abs 和原 max_applied_action_abs，未观察 preclip linear max。 |
| worker:119–122 | 原 env.close→app.close 顺序及零参保持，增加真实 FINAL 对应 durable intent/错误保留/V6源绑定；outer actual wait 才可资格。没有 PoseV4。 |

原 10mm closure 与 .01rad mimic 保持；.002m 仅保留原诊断 prefix-hit 日志，不作新停训线。
原 gravity/speed/omega/0.5s stable 与 3s 请求不变；160 controls=3.2s。
低趴新初态/8s、整腿后收目标与独立 31 体 MuJoCo 验收均另行进行，本 worker 不声称覆盖。

## 本轮验证边界

实际唯一一次 AST_AND_COMPILE_ONLY 检查 PASS：7 个 Python 文件均完成 AST parse +
compile(code object only)。sources_imported=False、Torch_imported=False、SDK_imported=False、
native_worker_executed=False、real_checkpoint_bytes_read=False、CPU_fixture_executed=False、
existing_tests_rerun=False。没有执行 worker、构造环境/learner、读取真实 PT/原始轨迹、
SSH/GPU/Git/预算修改，也没有执行任何 CPU fixture 或旧测试。

```text
worker_fudan_original_n80.py 16092 bytes / 261 lines
SHA256 c85f13ee760092d916b3aee993c3f06f957f96fe1f170d67f950ac7ab86e65dd
fudan_frozen_eval_safe.py 20917 bytes / 387 lines
SHA256 b42feb400aacb53e8c75c16973f6bae580cfbc1c4eb83d3a8eca847add4c0694
```

这些是源码身份及语法检查结果，不是缓存/原生执行/技能通过证据。Python 源码在该
AST 检查后未再变更；随后仅把这份说明补入 README。
