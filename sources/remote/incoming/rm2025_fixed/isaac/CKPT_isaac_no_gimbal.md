# Checkpoint 记录 - rm2025 无云台轮腿底盘 / Isaac Lab (PhysX)

| 项 | 值 |
|---|---|
| 模型源 MJCF | `incoming/rm2025_fixed/scene_training.xml`（交付包 rm2025_fixed，闭链、**无云台**） |
| Isaac 用资产 | `incoming/rm2025_fixed/isaac/robot_serial/robot_serial.usda`（PhysX 串联等效，见下） |
| 为什么不是闭链 USD | 交付包自带的 `isaac/smoke_test.py` 在本机跑通后**未通过它自己的验收**：`left_proximal_closure separated by 0.283094 m`（32 次位置迭代 + TGS 仍不闭合）⇒ PhysX 承载不了这 6 条闭环 |
| 关节/动作 | 6 路力矩：left_hip, left_knee, left_wheel_spin, right_hip, right_knee, right_wheel_spin；限幅 ±40/±40/±6 N·m，腿部带 DM8009 转矩-转速包络 |
| 观测 | 39 维（与交付包 `robomaster_env.py` 同布局：线速度3+角速度3+重力投影3+sin/cos(髋,膝)8+6轮速+2膝角+2膝速+2(膝-髋)+1高度+1速度指令+2轮触地+6上一动作） |
| 奖励 | 1.5*速度跟踪 + 1.5* upright + 高度保持 - 0.03*动作² - 0.02*动作变化² - 0.0005*机械功率，×0.01 s |
| 终止 | base z < 0.22 m 或 倾角 up < 0.5（=约 60°）或非有限值；截断 20 s |
| 物理 | dt=0.0005 s，decimation=20 ⇒ 控制 100 Hz；spawn 高度 0.298937 m（交付包实测轮地切点） |
| 训练器 | rsl_rl PPO，actor/critic MLP 512-256-128 elu，init_noise_std=1.0，obs_normalization=True，lr=3e-04，num_steps_per_env=24，save_interval=100 |
| 日志/权重目录 | `D:\claude2\fangzhen\incoming\rm2025_fixed\isaac\runs\rm2025_serial_isaac\map_v5` |
| 权重文件 | `model_<iter>.pt`（每 100 次迭代一个，另含 `model_best.pt`） |

## 续训 / 加载检查点

```
:: 从最新检查点继续（同模型）
.venv-isaaclab\Scripts\python.exe incoming\rm2025_fixed\isaac\train_isaac.py --viz kit ^
    --resume D:\claude2\fangzhen\incoming\rm2025_fixed\isaac\runs\rm2025_serial_isaac\map_v5\model_*.pt
```

## 下一步：加云台（用户要求：从检查点加载后加云台继续训）

1. 交付包明确写着 **云台/弹仓载荷未建模**（HANDOFF 第 8 条），所以当前策略的 6 个动作里不含云台轴。
2. 加云台的做法（保持检查点可用）：
   - 在 MJCF 里给 chassis 加 `yaw_link/pitch_link`（+弹仓），用 `kinematics.py` 保持闭链中立；
   - 重新 `make_serial.py` + `convert_robot.py` 生成带云台的 USD；
   - 新 env 的 **观测前 39 维保持不变**，云台角/角速度追加在后面；**动作前 6 维保持不变**，云台两个轴追加在后面；
   - 用 `--resume` 加载本 md 记录的 `model_*.pt`：rsl_rl 的 `load(path, strict=False)` 允许新增输出列，
     旧权重原样复用，新增动作列的均值初始化设 0（策略一开始不动云台），再微调；
   - 若 strict 加载失败，脚本会退化为"只加载 actor/critic 已有列 + 归一化统计"，同样能热启动。


## 启动后画面时间线（正常现象，别当成 bug）
| 策略步 | 看到什么 |
|---|---|
| 0 ~ 120（≈前 5 个迭代） | `--hold-iters 120`：每个策略步把中立位形重新写回仿真 ⇒ 1024 台整齐站在各自那块实测地图上（这是摆位展示，不是控制） |
| 120 之后 | 随机策略接管，多数车会在 1~2 s 内摔倒；摔倒即 `terminated`，立刻被 reset 回站立位形重新计时 |
| 几百个迭代后 | `episode_length`、`upright`、`h` 上升 —— 这就是 PPO 学站立的正常曲线；`h 0.002..0.006 / upright 0.00` 是 it=200 时的真实读数，不是坐标错了 |

监控：`tensorboard --logdir incoming\rm2025_fixed\isaac\runs`，看 `Train/mean_episode_length`、`Episode_Reward/*`。


---
# 2026-09-08 14:18 修复记录：有效训练 `map_fixed_v1`

## 现在在跑
```
train_isaac.py --num_envs 1024 --iters 4000 --save_interval 10 --viz kit --hold-iters 120 --field --run map_fixed_v1
```
运行目录：`incoming\rm2025_fixed\isaac\runs\rm2025_serial_isaac\map_fixed_v1`。Isaac Lab 可见窗口已启动；
每 10 次迭代保存一次，正常结束还会保存最终权重，Ctrl+C 会保存 `model_interrupt_<iter>.pt`。

旧 `map_v1`～`map_v5` 全部无效：TensorBoard 的 `Train/mean_episode_length` 固定为 1，策略没有得到可学习的轨迹，
因此没有从这些权重续训。根因和修复如下：

1. **四元数顺序错误**：Isaac Lab 3.0 的运行时根姿态写入使用 `xyzw`，旧脚本按 `wxyz` 写入，
   每次 reset 都等价于把车绕 X 轴翻转 180°。现已统一为 `xyzw`。
2. **地面和高度重复**：机器人 USD 误带 MJCF 地面，场景又创建了一套地面；同时 `InitialStateCfg` 再加一次
   0.2989 m，使初始 root z 变成约 0.598 m。现已在 USD 包装层禁用内嵌地面，场景初始平移归零，
   启动标定为 root z 0.2989、轮心 z 0.0645，并按 USD 实际轮半径 0.0625 m 写入贴地 root z 0.2969。
3. **观测维度不一致**：配置声明 39 维，但左右轮接触被合并成一个值，实际网络只有 38 维。
   现已给左右轮分别启用 PhysX contact report，并取一个 100 Hz 控制周期内的接触力历史，网络输入恢复为 39 维。
4. **接触间隙过大**：机器人和地图曾各使用 20 mm contact offset，导致画面出现明显悬浮。
   现按交付约定统一为 1 mm。
5. **断点与日志**：旧的 partial-load 分支读取了错误的 checkpoint key，实际会加载 0 个张量；现已支持
   actor/critic 精确加载和扩维时的重叠切片加载，并增加高度、直立率、左右轮接触、摔倒率、各奖励项和终止原因日志。

## 实测地图怎么进 1024 并行训练
`isaac/rmuc2026_field.py:rmuc2026_field_per_env()` 给每个 env 一份自己的地图切片，数据来自
`cad/out_map/field_dims.json`：0.20 m 台阶、25° 上坡、12.1° 下坡、0.416 m 障碍墙；单片跨度 4.47 m，
`env_spacing=6.4 m`。

## 启动后画面时间线
| 策略步 | 看到什么 |
|---|---|
| 0～120 | 摆位阶段：1024 台车以正确朝向站在各自地图切片上 |
| 120 之后 | 随机策略开始控制；初期摔倒并 reset 属于正常探索 |
| 后续 | `Train/mean_episode_length`、`Metrics/upright_fraction`、速度跟踪奖励应逐步上升 |

本次 16 环境验收在策略接管后 `mean_episode_length` 为 33～43（旧脚本固定为 1），无 NaN；
1024 环境正式运行已越过第 50 次迭代，约 2500 steps/s；第 48 次迭代平均回合长度约 721、平均奖励约 16.75。

监控：`tensorboard --logdir incoming\rm2025_fixed\isaac\runs`。
