# V6 runtime compatibility：源码证据与最小变更计划

## 1. 已关闭的 V5 窗口事实

来源：[CLOSED_RESULT](<../reports/ACTUAL_A1_NATIVE_V5_20261102_215643/CLOSED_RESULT.json>)、[COHORT_FINAL](<../reports/ACTUAL_A1_NATIVE_V5_20261102_215643/COHORT_FINAL.json>)。

- E3、W35 均实际 GO；进程 RC=0，但已有 semantic error gate 正确将其分类为错误，余下六角色未 GO。
- 首要错误均为 `pose_cache_runtime_adapter_v3.PoseCacheAdapterError: NON_NATIVE_FINITE_TIMESTAMP: _root_link_vel_w`，在 installer 的初始 snapshot 中发生。
- 当时 `installed=0`、`write_returned=0`、`install_rejected=1`；唯一显式 `env.reset`、teacher 构造、learner 构造与训练 action 均尚未到达。SDK/env 已构造，不把此状态写成“没有 SDK”。
- producer startup/counts/iteration/FINAL 为 null。新 BPTT=0 仅为失败阶段推断，不伪装成 producer 输出了九个零计数。
- 所有实际子进程 wait、费用结算、lease release 均已记录完成。六个未 GO 角色不是六次训练失败。
- 次要错误 `actual application exact class differs` 属于 App close binding preflight；它与初始缓存 snapshot 的首要错误分开记录。
- 上述证据未验证原 quaternion/gravity 健康门、physics、技能通过性，也未记录历史 raw timestamp 的实际 type/value。

## 2. `-inf` 的来源：不是 Warp 默认值

[Warp TimestampedBuffer 构造:34–35](<../discovery/sdk_warp_timestamp_actual_v4/timestamped_buffer_warp.py#L34-L35>) 默认 `self.timestamp = -1.0`。该源 SHA256 为 `ed1832b6cebf3388caba447caf4ef8256f4c154c2c400ca9e5ef258818a74db7`。Torch 对应源也默认 `-1.0`，SHA256 为 `1020269322e63b6383c9782f8cf369cbe8b55f52e081bccd79d03ae52712bd59`。

实际角色源码另有原生 stale 写入链：

1. [E3 build_env:134–153](<../discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/train_mod4v1_e3.py#L134-L153>) 构造原角色环境。
2. [RecoveryEnv:4、27](<../discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/e3_recovery_runtime_v1.py#L4-L27>) 继承原 ChassisPD 环境。
3. [ChassisPD:8–14](<../discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/chassis_pd_training_env.py#L8-L14>) 在构造中建立 `ChassisCOMSDK`。
4. [ChassisCOMSDK:28–89](<../discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/chassis_com_pose_roundtrip_sdk_adapter.py#L28-L89>) 的 `__init__ → reset → apply → invalidate_COM_dependent_cache`，在 46–52 行将包括 `_root_link_vel_w` 的缓存 timestamp 设为 `-float('inf')`。W35 同名原角色源也包含这一赋值。
5. [SDK root_link_vel getter:632–654](<../discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py#L632-L654>) 以 `timestamp < _sim_timestamp` 判断 stale，随后重算并 stamp 当前时钟；因此原生 `-inf` 具有明确 stale 语义。
6. [封版 worker:52–65](<../source_app_close_semantics_v5/worker_supermimic_bptt_app_close_candidate_v5.py#L52-L65>) 在 installer 前已检查 `_chassis_com.component.enabled`；本次错误到达 installer，说明该检查已经通过。

这条源码链解释了“原角色环境可能合法保留 native float `-inf`”。它不是历史 timestamp 实测；V5 的原值/type 未被序列化，继续保留 UNKNOWN。旧错误也可能由未知 type 导致，未据此追认实际值。

## 3. 最小 V4 pose adapter

新源：[pose_cache_runtime_adapter_v4.py](<pose_cache_runtime_adapter_v4.py>)，18161 bytes，SHA256 `7357827a72a03f6300ce3f7c6da3ad2a05a551480a1aad04a91dbaac4a497e2f`。

唯一数值接受扩展：

```python
if clock is not None and type(value) is float and value == -math.inf:
    return value
```

- 仅 BUFFER timestamp 接受确切 `builtins.float` 的负无穷。clock 仍必须是原生有限非负数。
- NaN、正无穷、bool、未知 scalar/wrapper、float subclass、未来 timestamp、非哨兵负数仍报错；不做类型强转。
- 安装 snapshot 对实际读到的负无穷输出有限 JSON tag：`STALE_SENTINEL / NEGATIVE_INFINITY / builtins.float / actual_native_value_read=True`。同时记录 clock 与各 timestamp 的 Python type；不在安装阶段写 SDK timestamp，也不将 clock 变为元数据值。
- writer/data `__self__`、`__func__`、MRO、定义源双 SHA、方法 code/line、backend、array/buffer 身份检查原样保留。
- 仅在原 full-state writer 成功返回之后，将同八个派生缓存 timestamp 置为 `-1.0`。原 writer 调用数、返回对象、异常、仿真时钟、getter、step/reset/RNG 均不增加、不改写。
- 新 event kind 为 `PINNED_INSTANCE_POSE_CACHE_ADAPTER_V4`，source code version 为 `POSE_CACHE_RUNTIME_ADAPTER_V4_NATIVE_NEGATIVE_INFINITY_STALE_V1`。
- `install_pose_cache_runtime_adapter_v3` 是新 `install_pose_cache_runtime_adapter_v4` 的同一函数 alias，供已封 worker 的逻辑 ABI 使用。未来 source index 显式安装新 SHA 到逻辑旧文件名；不将新 bytes 称为旧 V3 原源。

[最小差异](<POSE_CACHE_SENTINEL_DIFF_V4.patch>)、[构建及 AST 保护收据](<BUILD_POSE_CACHE_ADAPTER_V4.json>)。

## 4. App 合法 module alias 与仍待补的 native 证据

[实际 AppLauncher:27–29](<../discovery/sdk_app_launcher_actual_v6/app_launcher.py#L27-L29>) 从 `isaacsim` 引入 `SimulationApp`；[实际构造:1208](<../discovery/sdk_app_launcher_actual_v6/app_launcher.py#L1208>) 使用该类。

[isaacsim expose_api:167–199](<../discovery/sdk_reset_cache_backend_v2/isaacsim/package_init.py#L167-L199>) 在标准 import 失败时走 `from simulation_app import AppFramework, SimulationApp`，再注册 aliases。这为下列两个 exact module 身份提供源码依据：

- `isaacsim.simulation_app.simulation_app`
- `simulation_app.simulation_app`

V6 App helper 由父代理/82 独立封版，只扩展这两个已来源支持的 module alias，保留同一完整 48933-byte SDK 源、`SimulationApp` exact MRO、close 定义及 first line pin；不是接受任意 subclass。历史实际 module 仍未记录；后续新 native receipt 才能证明实际选择了哪个身份。

## 5. V6 新窗口组装边界

只在新的 source directory 中构建两份 V6 CLI。继续使用已封 V5 worker、shared owner、shim 的原 bytes；source index 仅替换两个源码来源：V4 pose adapter、V6 App alias helper。原 authority/common/GPU helper、原 bridge、payload core、V3 contracts、V4 installer、raw35 view、C113 command binder 等其余十二项保持 SHA 不变。

- 新 run/root 前缀 `MOD4V1_A1_RAW35_V6_`；新 source-index kind、stage-complete、root-manifest、parent-dispatch-purpose 均使用 V6 独立名字。
- `stage` 默认只读；显式 `--stage` 仅写全新 root，不启动 owner。`dispatch` 是分开的 CLI，默认只读，显式 `--dispatch` 要求父 marker 绑定新 root/run/stage SHA，且目的未消耗、没有旧 GO/TASK/production。
- 角色顺序仍是 E3、W35、CURB_INDEPENDENT113、CURB_PROTECTED878、SLOPE135、SLOPE_INDEPENDENT50、E0、E2；H1 排除。
- A1_RAW35_FRESH；九个新计数从零开始，旧 A0=4912 不作为 offset。N=1024、H16/history10、目标至少 3000 原样；seed、teacher 元数据、base_root、原 native plant constructor family 保持不变。
- 不增加 E2 command 修复、精确 100Hz sensor projection、bound/anchor/reward 改动，不缩 command 分布、物理 DR 或原验收阈值。
- 原 C/account/lock/resource admission、3900/3600/300/1800 时限、reserve、gravity `1e-3`、物理/frame/quaternion 逻辑全部不变；不增加额外健康 gate。
- 本代理只产出源码、stdlib shadow/fake/AST 测试与 SHA。实际 stage/dispatch/retry、SDK/GPU、原模型 PT、C/锁/Git 操作均为零。

## 6. 已执行的软件验证与后续最小缺件

[66 项测试收据](<CPU_TEST_RESULTS_V4.json>)：66/66 PASS，0 failure、0 error，约 1.250 秒。54 项旧 V3 shadow/实际源 AST 回归保留，另加 12 项 stale/JSON/type 反例。实际旧 `BoundedPoseCacheEventsV5` 的 `allow_nan=False` recorder 类能接受新 tag；未执行 SDK/真实 adapter 安装。

仍待独立完成：父/82 的 V6 App helper 精确路径、bytes/SHA/ABI 收据；将其封入新的 14 项 V6 source index，运行 V6 fake-stage/mock-Popen 与实际小源 SHA 回归。之后是否在新窗口启用由父代理决定。即使软件测试全部通过，仍不等同于新 native type/value receipt、BPTT 累计、real full-resume 或原技能通过率。
