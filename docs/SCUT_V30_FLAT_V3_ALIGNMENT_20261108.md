# MOD4v3 对齐华南虎 V30 Flat（2026-11-08）

## 目标

把 MOD4v3 的平地训练对齐华南虎 `MOD4_STANDING200_SCUT_RECIPE_V30_FLAT`
（只读参考），而不是继续沿用 standing 或 BC 热启动。目标是先完成
平地速度、转向、站立/高度与动作平稳性的联合训练；不把本文件当成
200 mm 台阶或实车验收结论。

## 参考任务

86 只读参考目录：

```text
/home/robemo/mod4v3_native_scut_20261106_1793976241913700500/
migrated_host72_20261107_1794039340895209800/data/tasks/
MOD4_STANDING200_SCUT_RECIPE_V30_FLAT_1793786097220799900
```

参考配置/结果：

- `train_seconds=3600`
- `target_iterations=6528`
- 实际完成 `iteration=1709`
- `PPO_updates=237`
- `episodes_completed=23343`
- `passed_execution=true`
- 独立 200 mm skill acceptance 是单独的评测，不属于本 flat run

## 本次实现

正式 run 使用：

- 210/4090 主机：`egde@10.24.5.27:4090`
- 4096 并行环境，seed 66
- episode 20 s，policy 50 Hz
- physics dt 0.0025 s，decimation 8
- PhysX TGS 32/4
- 35D actor / 78D critic / 6D action
- SCUT 动作顺序：
  `left_front1, left_rear1, right_front1, right_rear1,
  left_wheel, right_wheel`
- 速度指令 `vx=-2.7..2.7 m/s`
- yaw 指令 `±2π rad/s`
- heading 50%，standing 10%，指令重采样 5–15 s
- 高度指令 0.20–0.42 m
- 高度语义：`root_z - ground_z`
- `use_absolute_height=false`
- `use_leg_length_as_height=false`
- PPO actor/critic MLP `256/128/64`
- `value_loss_coef=4.0`
- mild DR：`white_v3`
  - mass/inertia 0.9–1.1
  - leg gain 0.9–1.1
  - wheel gain 0.9–1.1
  - wheel friction 0.7–1.0
  - 20% nominal
  - spring/PD/COM/armature/joint-friction/push/noise/delay 保持关闭

奖励权重以 `evidence/2H_STARTUP.json` 中的 `reward_weights` 为准；代码和
实际运行回执共同保存，不在报告里另造一套权重。

## 热启动选择

使用 V28 flat 检查点转换为 SCUT 动作顺序后热启动：

```text
checkpoints/mod4v3_v28_flat_scut_order.pt
```

没有使用：

- standing 热启动：在 ±2.7 m/s / ±2π rad/s / heading 指令下速度会塌到接近 0
- BC student：训练 MSE 约 0.00454 / val MSE 约 0.00932，但 16 环境确定性
  回放 `final_stable_count=0`、平均 `vx≈0.0099 m/s`，不可作为正式热启动

## 当前训练状态（只读快照）

### 第一小时

路径：

```text
.../scut_flat_v30_v28warm_1h_20261108_r1
```

完成 `iteration=2554`，`elapsed=3602.34 s`，最终奖励
`+0.076826`，timeout `102363/103235`（约 99.1%），closure
`211/103235`（约 0.20%），最大 closure `2.1024 mm`，mimic/numerical
均为 0。最终 checkpoint SHA-256：

```text
bcef5b8964ffb8cca5dcb4f07adcaa92e6775c36268dec12443da06919991421
```

### 第二小时（写入本报告时仍在运行）

路径：

```text
.../scut_flat_v30_v28warm_2h_20261108_r1
```

快照 `iteration=4260`，约 `3.0 万 env-step/s`，`mean_reward=+0.08525`，
timeout `163786/164510`（约 99.56%），closure `165/164510`（约 0.10%），
最大 closure `0.8583 mm`，mimic/numerical 均为 0。该快照不是最终结果，
训练仍在自然运行。

最近一次周期 checkpoint：

```text
iteration=4229
SHA-256=1e7a0285dfe30ee2f1fee3d1059cdf607dce5683af24e4bdf3eb5568a8a79ce0
```

## 判读

当前奖励从第一小时末的约 `0.0768` 上升到第二小时的约 `0.0853`，
之后进入平台；timeout 比例高、closure 低、mimic/numerical 为 0，
说明当前不是 NaN/数值崩溃。奖励平台不等于独立能力毕业，仍需分速度、
分高度、yaw/heading、200 mm 支撑/台阶、MuJoCo 回放和接触连续性评测。

## 已知差异

- 工作区规则要求闭链单环境重置门限 2 mm；华南虎 V30 元数据使用 10 mm。
  本次没有提高门限，也没有改写历史记录；最大 closure 仍低于 2 mm。
- 本次是 MOD4v3 USD，不是华南虎原始 MOD4v1 USD；不能直接把本 flat run
  宣称为华南虎完整科目毕业。
- `skill_acceptance` 是独立 200 mm 测试，不是 flat 训练奖励的一部分。

## Git 记录范围

本目录保存实际训练源码快照和只读回执。没有提交检查点、日志、USD、
rollout、tar 包或凭据。若后续生成第二小时 `FINAL.json`，应另立试验记录
或追加证据，不覆盖本快照。

## 第二小时最终回执（已正常结束）

第二小时窗口于 `elapsed_seconds=7200.82` 正常结束，进程退出后写入
`FINAL.json` 与 `SAFE_CLOSED.json`。最终 `iteration=4772`，平均奖励
`+0.085682`，timeout `216436/217254`（约 99.62%），closure
`184/217254`（约 0.0847%），最大 closure `0.6105 mm`，mimic/numerical
均为 0，`L0_mean=0.25271 m`，`theta_abs_mean=0.14956`，`vx_mean=0.08964`。

最终 checkpoint：

```text
model_final.pt
iteration=4772
SHA-256=ea9bb5517ef173fca19f0657bfef788eb007b8066ac3a7c7e305b4e9ae5b2b1d
```

最后周期 checkpoint：

```text
model_periodic.pt
iteration=4689
SHA-256=d820724822bd453b02966d44312c8d9749369bc1ab08bc487aeb781d87b6d8af
```

`SAFE_CLOSED.json` 为 `scene_closed=true`。这次是自然跑完 2 小时窗口，
不是人工停训；奖励已在约 `0.085–0.086` 平台，不能把“跑完”直接等同于
独立能力毕业。
