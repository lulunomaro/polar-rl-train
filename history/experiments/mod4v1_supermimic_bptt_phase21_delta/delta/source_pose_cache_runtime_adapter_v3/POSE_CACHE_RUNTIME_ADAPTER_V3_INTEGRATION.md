# Pose cache runtime adapter v3 — 可合并 SOURCE，尚未 native 安装

## 1. 交付状态

这是新的 instance-only 实现，不是 sealed v2 的 bool-gated 原型。仅写本新目录；旧 bridge、worker、SDK、v1/v2 封版件、旧 instance、旧结算均未修改。本轮 stdlib CPU **54/54 PASS**，0 SDK/torch import，0 GPU/物理 step，0 native 安装。实际新 instance 的 binding、cache 误差和任务通过性仍为 **null**，留给父代理的新 native 构造验证。

- 主模块：[pose_cache_runtime_adapter_v3.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_pose_cache_runtime_adapter_v3/pose_cache_runtime_adapter_v3.py>)。
- 测试：[test_pose_cache_runtime_adapter_v3.py](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_pose_cache_runtime_adapter_v3/test_pose_cache_runtime_adapter_v3.py>)；[CPU 结果](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_pose_cache_runtime_adapter_v3/CPU_TEST_RESULTS_V3.json>)；[透明执行历史](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_pose_cache_runtime_adapter_v3/CPU_TEST_EXECUTION_HISTORY_V3.json>)。
- 机器接入契约：[RUNTIME_ADAPTER_CONTRACT_V3.json](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_pose_cache_runtime_adapter_v3/RUNTIME_ADAPTER_CONTRACT_V3.json>)。

## 2. 稳定 API 与唯一安装位置

调用者先让封存的本模块在**新 job 的自有源码路径**中可导入。导入本模块不会安装 hook，不导入 SDK。

```python
from pose_cache_runtime_adapter_v3 import install_pose_cache_runtime_adapter_v3

# 原 build_env() 构造新 instance 之后，原 ONE explicit reset 之前：
pose_cache_adapter = install_pose_cache_runtime_adapter_v3(
    env.scene['robot'], receipt_callback=pose_cache_receipt_callback,
)
obs, info = env.reset()  # 这是原有的那一次 reset，不是追加一次
# 之后沿用原校验、teacher/actor/bridge 顺序。
```

精确签名 `install_pose_cache_runtime_adapter_v3(robot, *, receipt_callback: Callable[[dict], None]) -> PoseCacheAdapterHandle`，见[入口:312](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_pose_cache_runtime_adapter_v3/pose_cache_runtime_adapter_v3.py#L312-L343>)。无 `live_binding_verified=True`、skip、pin override 参数。父代理/集成同伴负责未来 worker 的实际合并；本轮未合并或启动。

callback 只接收 Python JSON 元数据，写到**新 job 自有目录**；不要读 SDK、额外采 gravity/heading、调用 observation、推进 history/RNG，也不要创建 JSONL。建议 `installed` 单独保留一次 binding JSON，其他事件覆盖一个 latest JSON，而不是累计大日志：

```python
# 以下为接入片段，不在本轮执行。
def pose_cache_receipt_callback(event):
    name = ('POSE_CACHE_BINDING_INSTALLED_V3.json'
            if event['event'] == 'installed' else 'POSE_CACHE_LATEST_EVENT_V3.json')
    (new_job_dir / name).write_text(
        json.dumps(event, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
```

最终工作回执可用 `pose_cache_adapter.receipt()`，它只复制已持有元数据，不触发 SDK getter。`handle.uninstall()` 仅恢复之前的 instance method binding，不改类/SDK/源文件，不恢复陈旧 timestamp。清理异常不得覆盖原任务异常；任何安装/调用/回执失败均沿未来 worker 的 error/非零退出/owner fail-closed 链停止，不继续训练。

## 3. 新 native 构造时的真双 pin

固定 source bytes：

| 对象 | bytes | SHA256 |
|---|---:|---|
| `isaaclab_physx.assets.articulation.articulation.Articulation` defining owner | 220628 | `47d96553282b389493e69f691b8dcbfeb98997a5a80b88c2571c60ba8b58cb6d` |
| exact `isaaclab_physx.assets.articulation.articulation_data.ArticulationData` | 91275 | `43a31992353ad3a500024d0ec908d5b253ada7a0aac9a1cd2261466e10bda4ff` |

新模块的[pin:50–59](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_pose_cache_runtime_adapter_v3/pose_cache_runtime_adapter_v3.py#L50-L59>)和[binding 校验:95–171](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_pose_cache_runtime_adapter_v3/pose_cache_runtime_adapter_v3.py#L95-L171>)实际检查：

1. bound fullstate writer 是 `MethodType`，`__self__ is robot`，`__func__` 是实际 MRO class dict 定义；记录 actual type/MRO，不凭 import 名称推断。
2. defining owner 的 module/qualname/source file 与 module `__file__` 一致，实际文件 bytes/SHA 符合 pin；function `co_filename`、qualname、AST declaration 行一致。
3. 原 fullstate writer 动态调用 pose/COM-velocity 两个 delegate，所以也验证它们仍由同一已 pin owner 定义；仅验证，不额外调用、也不 wrap 这两个 API。
4. 读取原 `robot._data` plain field，避免额外访问 `robot.data` property。实际 data **exact type**、MRO、module/source bytes/SHA 和 `__backend_name__ == 'physx'` 均检查；未知 data subclass 不放行。
5. 所有八个 buffer/其 data 字段、timestamp、clock 先校验。只允许 plain Python field 或 native member slot，拒绝会执行 getter 的 descriptor；clock/stamps 必须是原生有限 `int/float`（不接受 bool/tensor/隐式 `.item()`），clock≥0，stamp 为 -1 或 [0,clock]。每次调用复核 data/buffer/array identity。

文件 pin 是当次 source/binding 的约束，不是对任意被篡改 Python 进程的密码学执行证明；没有 SDK native 正例，旧 worker actual backend/MRO unknown 仍保留。测试正例只在测试作用域把私有 pin patch 到**自有 fake test 源**，不冒充真实 SDK 绑定。未 patch 的 production 默认确实对 fake fail-closed。

## 4. 原 writer 返回后仅八个 timestamp

[调用核心:247–291](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_pose_cache_runtime_adapter_v3/pose_cache_runtime_adapter_v3.py#L247-L291>)：原 bound writer 原参数调用一次；原异常对象保持；成功返回后再复核 metadata/identity 与 clock 不变，之后唯一 SDK data mutation 是 `object.__setattr__(buf, 'timestamp', -1.0)`。八个字段为：

```text
_projected_gravity_b, _heading_w, _root_link_vel_w, _root_com_pose_w,
_root_link_lin_vel_b, _root_link_ang_vel_b, _root_com_lin_vel_b, _root_com_ang_vel_b
```

不写 root pose/velocity/joints/arrays/Proxy，不伪回 clock，不额外调用 getter/update/forward/step/reset/obs/RNG。不是重算 cache，而是使下一次**原有** getter 正常按 `timestamp < _sim_timestamp` 重算。返回原 writer 的同一个 return object。

- 原 writer 抛错：没有 stamp 清洗；callback 报错也不遮蔽原异常。
- 原 writer 返回后 clock 改变、field/identity 改变或失配：报错，保留真实 clock/物理写入，不伪造回滚；后续调用 sticky fail-closed。
- callback 在成功路径失败：也报错并锁住该 handle 的进一步写入。安装 callback 失败会恢复之前 instance binding。
- 八次 plain stamp 赋值不是跨字段原子事务。若意外赋值失败，可能已经写入一部分 stamp；停止并保留失败证据，不回滚真实物理状态、不重试。
- 所有 callback 事件都是少量 metadata：`installed`、`write_returned_and_invalidated`、`original_writer_raised`、`adapter_rejected_before_write`、`adapter_rejected_after_write`、`install_rejected`、`uninstalled`。成功调用含 before/after clock、八 stamp、write/return/invalidation 计数；install 含实际 source/MRO 双 pin。每次一条小回执，非轨迹日志。

## 5. Source 依据与边界

- 被 pin 的[fullstate writer:4799–4815](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation.py#L4799-L4815>)依次调用 pose/COM velocity setter。
- [pose setter:445–503](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation.py#L445-L503>)写 actor pose 并 invalidate 若干 root/body 项，但遗漏本八 derived timestamps；[COM velocity setter:704–733](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation.py#L704-L733>)也没有补齐八项。
- [gravity:995–1006 / heading:1012–1027](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py#L995-L1027>)只在 stamp 严格小于 clock 时重算；[update:121–131](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py#L121-L131>)的 `+= dt` 表明 `update(0)` 不是普遍补救。
- 原 SDK [reset:423–437](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/base/manager_based_env.py#L423-L437>)最后才计算原有 observation；安装提前到原 reset 前，避免仅到 bridge guard 才处理、让 obs 已基于陈旧 getter 生成。
- 原 [bridge:90](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L90>) `xyzw→wxyz`、[gravity guard:133–136](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L133-L136>) 的负 last ROW 和 `1e-3` 均保留。
- 原 actor gravity 的 [delay/history:520–544](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/mod4_task.py#L520-L544>)与 [noise/slot:1211–1217](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E0/runtime/isaac/mod4/mod4_task.py#L1211-L1217>)不改。不把 actor noisy/delayed gravity overwrite 成 truth，也不要求 actor gravity 等于即时 SDK truth。

**仅 wrap `write_root_state_to_sim`。** Direct pose/link/COM write API 不自动扩大覆盖。未来需要查看原 reset 调用链/实际 callback 计数；`installed` 但 0 次 fullstate return 不等于已验证 cache 刷新。也没有覆盖任意 setter、所有 world-frame/sensor/cache 或 kernel/stream 实现。实际 Warp buffer class 的 native layout、实际 world gravity/stream/cache tick/物理同刻误差仍待未来 binding/preflight；若 layout 不符合本检查会停止，而不是临时改 pin 或调用额外 getter填字段。

C113 的 after-reset command binding 是独立接点，由父代理/接入同伴处理；本模块不改命令、不加 reset/obs/RNG。E0/S50 原 binary acceptance 缺口继续为 null，不加 proxy。旧已 CLOSED run 的结算、count/null、成功率都不被本 v3 重写。

## 6. CPU 证据与复现

```powershell
& 'C:\Users\lulu\.dsh\dsh-runtimes\dsh-primary-runtime\dependencies\python\python.exe' -S -B '.\test_pose_cache_runtime_adapter_v3.py'
```

工作目录是本新目录。54 测试覆盖真实 fetched bytes/AST、未 patch 默认拒 fake、双 pin/owner/delegate/数据类/路径/代码行失配、八字段缺失、descriptor 不执行、finite/native clock、未来 stamp、wrong self、duplicate/reentrant、identity/clock 变化、exact-once/return identity、其他 API/类/另一 instance 不变、callback/原异常优先、sticky failure、uninstall 及旧 bridge 不变。

首轮 50 测试为 0 fail/1 error：缺少 `__file__` 已停止，但 `inspect.getsourcefile` 抛 `OSError: source code not available`，早于新模块归一化为 `PoseCacheAdapterError`。只修新模块，透明保留该 run；随后 53 PASS，再加入 sticky-failure 测试及 latch，最终 54 PASS。结果不等于已 native 安装、物理根因证实或任务提升。

父代理负责后续 native 真 binding/同刻 guard/preflight 与实际训练/Git。当前交付到 source-only 为止。
