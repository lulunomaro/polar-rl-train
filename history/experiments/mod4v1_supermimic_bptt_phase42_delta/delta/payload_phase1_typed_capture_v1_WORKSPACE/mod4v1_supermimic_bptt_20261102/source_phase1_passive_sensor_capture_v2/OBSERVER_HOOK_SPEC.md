# 最小 NEW observer-hook 规范（未 patch 原封件）

## 已有 API 足够的部分

[原 feedback:24–45](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/feedback_delay_runtime.py#L24-L45>) 的 raw 输入已经是 clean pre-scale；[原 sensor.apply:28–38](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/sensor_mild_math.py#L28-L38>) 的 cache 暴露实际 noise；[原 delay.apply:16–30](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/reward_command_audit_v1/E3/runtime/isaac/mod4/feedback_delay_mild.py#L16-L30>) 的 sample_tick/out 暴露 selection。优先用现有被动组件，无需源变体。

本规范只处理原 API 未外露的局部 `due/delayed/prev/initial`、SDK实际 default q/dq、manager 原本已计算的 term return。原 API 缺字段时保持 UNKNOWN，不把 noisy-clean 两字段或延迟公式重放冒充实际 draw/selection。

## NEW 源变体约束

1. 仅新目录衍生新 source SHA、新 manifest、新 class/module identity，保留原封件逐字节；本交付没有生成或安装这种变体。
2. observer 缺省 None；无 observer 时仍按原顺序执行相同 tensor 运算；启用时仅向 observer 借用原局部对象，observer 只做 bounded detached selected-row clone。
3. `emit(kind, fields)` 隔离 observer 异常，记录 capture_error 并使 exact=False；不改变原函数异常或返回 identity，不 retry 原函数、不吞原异常。
4. 不新增 rand/reset/step/observation/SDKgetter，不新增查当前 state 的 getter；不修改 action/queue/RNG/episode、DR或 physics。一个回调不允许写输入对象。
5. 新变体需独立原-vs-变体 bitwise 返回与 RNG/call-count/queue-order 对照后才谈启用；source-only 规范不是证据。

## 规范事件（原局部量，不是计算配方）

### sensor 原函数

在原 `due` 已计算、原 noise draw 已执行、原 `last`/draw_counts 已更新后，原 return expression 只算一次并赋局部 `out`，再 emit，再 `return out`：

```python
# NEW-source specification only, not an installed patch.
# 原来的: return value+noise+(self.bias if key=='leg_pos' else 0.)
out = value + noise + (self.bias if key == 'leg_pos' else 0.)
emit('sensor_original_result', {
    'key': key, 'tick': tick, 'episode': self.episode,
    'due': due, 'clean': value, 'noise_used': noise,
    'leg_bias_used': self.bias if key == 'leg_pos' else None,
    'draw_counts': self.draw_counts, 'original_result': out,
})
return out
```

不能添加一个新 `torch.rand` 来复现 draw，也不能从 `out-value` 声称得到了原 noise（leg bias、浮点舍入、缓存与delay使该说法失真）。profile off 分支没有原 noise draw，明确 `noise_draw_exposed=False`。

### delay 原函数

在原 `due/old/initial/prev/delayed` 已计算、原三次 cache mutation 后 emit 借用这些局部量与原 cache。需要 queue-before 时在 mutation 之前由 observer clone 已有 cache，不重新计算 queue。在同一 key+env+episode+tick 的重复调用中 `due` 可空；原 out 缓存与本次 clean 不自动配对。原 return clone 只做一次，赋 `out_return` 再 emit/return，保留实际返回对象。

字段：`key,tick,episode,due,old,initial,prev,delayed,queue_before,queue_after,cache.sample_tick,cache.ready,original_input,original_return`。原跳钟异常 `Skipped/reversed feedback sample clock` 原样传播，不补 tick、不 catch 后继续运算。

### SDK default joint values

[SDK joint_vel_rel:260–269](<F:/RMPOLAR-RL/mod4v1_supermimic_bptt_20261102/discovery/sdk_reward_command_call_order_v1/envs/mdp/observations.py#L260-L269>) 当前 return expression 各读取一次 joint_vel/default_joint_vel；NEW 源只把原读取结果赋局部，不增加读取次数：

```python
# NEW-source specification only. Preserve original left-to-right getter order.
actual = asset.data.joint_vel.torch[:, asset_cfg.joint_ids]
default_used = asset.data.default_joint_vel.torch[:, asset_cfg.joint_ids]
out = actual - default_used
emit('joint_vel_rel_original_result', {
    'asset_name': asset_cfg.name, 'joint_ids': asset_cfg.joint_ids,
    'actual': actual, 'default_used': default_used, 'original_result': out,
})
return out
```

joint_pos_rel 同理。没有该 hook 的场合，raw q/dq-relative 仍有直接参数证据，live default 数值则 UNKNOWN；源码配置零不是 live tensor receipt。

### 完整 clean35 的硬缺口

mid100Hz 原循环只计算五个 feedback channel 共16维。其余19维未共同求值；observer hook 没有现成对象可借用，**仍为 UNKNOWN**。不得额外调用 manager.compute/compute_group、clean_policy、commands/height/last_action/mode getter 来补齐。若现场另有原有同时间 all-term 计算，可在那个原本会执行的 return 边界借用其结果，但不能事后把不同时间/episode的值拼成一份“真实mid clean35”。

terminal 边界优先用现有 bridge.pre，capture 不额外 pack；postreset observation 不能替代 terminal pre-reset clean/physical证据。
