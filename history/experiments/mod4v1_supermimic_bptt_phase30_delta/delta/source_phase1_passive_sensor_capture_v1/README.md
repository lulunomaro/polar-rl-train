# Phase1 被动 clean100Hz 源 API 与 bounded capture（SOURCE ONLY）

状态：`native_enabled:false`、`exact:false`。本包交付源绑定检查、可执行被动 tap、stdlib/fake 测试；不等于原资源现场准入或阶段1验收。技能目录仅 Office/ACL，本任务使用 read/glob/grep 和获准 Python314 `-B`；未运行 SDK、GPU、SSH、Native、训练，未读真实 PT/rawJSONL/canonical 账本、未动锁/Git/旧封件。

## 交付入口

- [被动组件](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v1/passive_capture.py>)：`install_passive_capture(env, bridge, feedback_module, role_api, bridge_pin, *, recorder=None, snapshot=stdlib_snapshot)`。
- [绑定与 AST 工具](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v1/source_api.py>)、[八角色 source pins](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v1/SOURCE_API_MANIFEST.json>)：class/module/function/sourceSHA/声明行/代码首行/参数/默认表达式、完整 local MRO、entry、SDK 四个 observation 函数。Windows `source_path` 只作出处；安装只读实际绑定 callable 的 `__code__.co_filename` / module 的 `__file__`，以 SHA 比较部署副本，不要求 F 盘路径存在。
- [stdlib fake](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v1/fake_runtime.py>)、[执行测试](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v1/test_passive_capture.py>)。fake 不是物理模拟、不是原 Torch 数学等价证明。
- [可选父侧真实 CPU 类 fixture](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v1/cpu_reference_tap_fixture.py>)：父显式传入其已审查的 `torch, SensorCorruption, FeedbackDelay`，函数才运行；本子会话没有执行。仍在 fake 环境闭包内，不走 native preflight，不声称 actor35 equality。
- [最小 NEW hook 规范](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v1/OBSERVER_HOOK_SPEC.md>)、[现场待验模板](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v1/NATIVE_BINDING_RECEIPT_TEMPLATE.json>)。模板不充当现场 receipt。

## 实际 source 路径与时序

当前 [worker:26–65](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_native_v6_runtime_compat/_SOURCE_INPUT/sealed_source/worker_supermimic_bptt_app_close_candidate_v5.py#L26-L65>) 的 SHA 为 `7c42986077de62278e33a49f560f22602c9ba4d4e69b058f5f5f8f0893c099c7`；按原 family/role entry 构建，physics `.0025`、control `.02`、decimation `8`。E1 四个变体的 entry 来自其已有 source metadata，未从名称猜测。

以已读 E3 为锚（其余七角色逐文件 SHA/MRO 在 manifest）：

| 原函数/位置 | 直接可观察证据 |
|---|---|
| [feedback(env,key,raw):24–27](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/feedback_delay_runtime.py#L24-L45>) | `raw` 是原 term 已调用 SDK observation 得到的 clean、pre-scale 参数；内部恰好一次原 sensor.apply，再一次原 delay.apply。不是从 noisy/delayed raw35 反推。 |
| [SensorCorruption.apply(self,key,value,tick):28–38](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/sensor_mild_math.py#L28-L38>) | 原 `cache[key]=(last,noise)` 暴露实际 noise（包含同 tick 复用），原 `bias` 暴露 leg bias；tap 克隆这些已有量和原 return，绝不做 noisy-clean 相减。 |
| [FeedbackDelay.apply(self,key,x,tick):16–30](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/feedback_delay_mild.py#L16-L30>) | 原输入 x、cache 前后 `last/cur/out/sample_tick/ready`、delay、episode；`sample_tick/out` 是原真实 selection。局部 `delayed`/`due` 本 API 未外露，留 `UNKNOWN`，不重演队列。 |
| [100Hz scene.update closure:74–86](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/feedback_delay_runtime.py#L74-L86>) | 先 previous(dt)，再 `_sim_step_counter%4==0` 逐五 channel 调原 term。400Hz physics 中每控制第4/8子步，即 mid10ms/end20ms 各一轮，不是每8子步只采一次。 |
| [SDK step:202–273](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reward_command_call_order_v1/envs/manager_based_rl_env.py#L202-L273>) | `_physics_handles_decimation=False` 才有八次 scene.update；若为 True 只有一次，preflight 直接失配。termination → reward → reset → command/interval → observation；end returned obs 可已是 reset 后。 |
| [NativeTaskBridge._termination_capture:84–96](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_runtime/native_supermimic_bridge.py#L84-L96>) | SHA `8211964c2ce3dd78fdb9fee6603ee4a4dcfbca6fa9d7df44f20d3ddb7aaead29`。原 callback 已完成 pack 与 term/trunc，tap 仅复制已有 `bridge.pre`，不多调用 pack/get_term/SDK getter。 |

### same tick 与 episode 边界

`apply` 调用次数 ≠ fresh100Hz sample 数。sensor 同 tick 只缓存 noise，clean 仍由原 term 重新得到；delay 同 tick 直接复用 out。因此一次 manager 重算即使 clean 已变，也可能得到旧 out。capture 的 `clean` 明确指本次原 raw 输入，不擅自把它关联到旧 out。使用前后原 `last`、`draw_counts`、每行 `episode`、`sample_tick` 判读；未保留相应历史时 selected-clean/selected-noise 证据仍 UNKNOWN。

原 reset(ids) 会在同一 physics tick 将 selected rows 的两个 last 置 -1、episode++，产生合法重新 draw/warmup。新 episode 第一次即使请求 lag1，真实 `sample_tick==当前tick`、`ready=False`、age0；不跨 episode 接旧 sample。tap 记录 partial reset 前后与 reset_depth，reset 内部重算不算正常 control mid/end。

## dtype、scale、joint/default 来源

[PolicyCfg:1210–1245](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/mod4_task.py#L1210-L1245>) 的 actor35：commands `[0:3]`，height×5 `[3:4]`，gyro×.5 `[4:7]`，gravity `[7:10]`，leg qrel `[10:14]`，wheel zero slots `[14:16]`，leg dqrel×.1 `[16:20]`，wheel dqrel×.1 `[20:22]`，last_action `[22:28]`，mode7 `[28:35]`。五个100Hz feedback 只覆盖16维。其余19维没有在 mid 原循环共同计算，**完整 clean35 mid/end 保持 UNKNOWN**。旧 raw35 已 noisy/delayed，不能倒造缺失 clean。

- Leg 顺序来自 [LEG_ORDER/WHEEL_ORDER:114–116](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/mod4_task.py#L114-L116>)：left_crank,left_hip,right_crank,right_hip；wheel left_wheel_spin,right_wheel_spin。preflight 验实际 term.params 名称、resolved joint_ids 与 preserve_order=True；gyro/gravity 的可变默认 asset_cfg 和显式 override 都必须是 robot，不能仅靠默认对象 id。
- [SDK joint_vel_rel:260–269](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reward_command_call_order_v1/envs/mdp/observations.py#L260-L269>) 实际减的是 `asset.data.default_joint_vel.torch[:,asset_cfg.joint_ids]`。源码 [init_state:387–389](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/mod4_task.py#L387-L389>) 声明默认 q/dq 为0；这只是配置出处，未替代 live buffer 证据。tap 不额外读取 default SDK getter，现场数值仍 UNKNOWN。
- [backend default buffers:204–239](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reset_cache_backend_v2/backend/articulation_data.py#L204-L239>) 声明 wp.float32 与 init_state 来源；capture 克隆实际 raw/noise/output，不 cast，不把 source dtype 声明冒充现场观测值，`sensor_stage.dtype` 记实际 return dtype。
- actor35 没有 quaternion 字段。bridge 原 pack 才做 xyzw→wxyz；tap 不添加 quaternion getter/变换。

## 安装、bounded 与恢复契约

显式安装前必须已有原 env fresh reset / 原 bridge。检查 actual MRO、sys.modules/module identity、原 helper class binding、active policy term 函数的 `__globals__['feedback']`、scene.update 闭包中的原100Hz函数与 self、实际源 SHA/line/bytecode/signature、原 bridge 类 descriptor。失配在任何 setattr 前抛错，不回退到猜测模块。term.func 本身不包装，默认对象与动作参数不替换。

只改六个可恢复绑定：target sensor.apply、target delay.apply、实际反馈 module.feedback、已有 scene.update、termination.compute、env._reset_idx。共享 module 遇到另一 env 就原样透传；所有原函数恰好一次，返回同一个对象；原异常原对象传播，既有 RNG/queue mutation 不回滚、不重试。snapshot 错误只记 capture_errors/UNKNOWN，原调用继续。关闭恢复安装前 instance dict 的“有属性/无属性”状态；若另一 owner 后装覆盖，报 restore conflict，不覆盖它。

```python
# 仅父侧已准入短窗口的接口示意；本包不会 step/reset/compute 或获取资源。
manifest = json.loads(manifest_path.read_text())
recorder = BoundedRecorder(first=32, last=32, max_events=256)
# witness_ids 是父在窗口前准备的1..8行device long index；无 dtype cast/CPU拷贝。
snapshot = tensor_snapshot_adapter(torch.Tensor, witness_ids, env.num_envs)
tap = install_passive_capture(env, bridge, sys.modules['feedback_delay_runtime'],
    manifest['roles'][role], manifest['bridge'], recorder=recorder, snapshot=snapshot)
try:
    # 父自己的既有 bounded driver；不额外调用 obs/clean_policy/audit/reset/getter。
    pass
finally:
    tap.close()
```

默认 first2/last2 只是调试默认，四个 individual events 不足证明五通道×mid/end。实测显式用32/32，并把 cap 设到涵盖约定短窗口（每正常control至少10 sampling feedback +5 manager feedback+1 boundary，reset可能更多）。first/last 加 count，tick 内无文件 I/O、无 O(n²) 累积重写。`retained_last` 是 **cap 内的最后记录**，不是任意长 run 真结尾；耗尽只停 payload 捕获，原执行继续、计数继续。父另行有界停窗口，不使用真实 PID signals。

## 执行与证据分层

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B 'F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v1/test_passive_capture.py'
```

最终 [stdlib/fake receipt v3](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/source_phase1_passive_sensor_capture_v1/STDLIB_FAKE_TEST_RECEIPT_v3.json>)：21项，含双slot、same-tick changed raw/cachehit、partialreset同tick、warmup、original call/RNG/getter/queue守恒、return identity/default identity、异常对象传播、terminal pre-reset、观察器自身失败隔离、恢复、foreign env透传、10000次bounded cap、source pin/bytecode tamper、迁移路径与可变robot默认检查。旧17/19项 receipts 仅保留历史版本源 SHA，最终封件以 v3 为准。

后续门仍开放：父 review → 真实 Torch CPU 类+tap → 原资源短窗口实际 preflight绑定 → 同原种子/动作/原时序的 bitwise actor35 equality、源 call counts/SDK getter/RNG/queue/reset证据 → 缺口裁定。所有这些不由 fake 或 source pin 自动推出；物理DR/H1/mothers/acceptance保留，不训练、不写 native/stager。
