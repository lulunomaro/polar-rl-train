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
| 物理 | dt=0.0005 s，decimation=20 ⇒ 控制 100 Hz；轮半径 0.0625 m，root-link 由轮心实测偏移自动贴地 |
| 训练器 | rsl_rl PPO，actor/critic MLP 512-256-128 elu，init_noise_std=1.0，obs_normalization=True，lr=7e-05，num_steps_per_env=24，save_interval=10 |
| 日志/权重目录 | `/home/egde/fangzhen_linux/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac/spin_pure_v2` |
| 权重文件 | `model_<iter>.pt`（每 10 次迭代及正常结束各保存一次；Ctrl+C 时保存 `model_interrupt_<iter>.pt`） |

## 续训 / 加载检查点

```
:: 从最新检查点继续（同模型）
.venv-isaaclab\Scripts\python.exe incoming\rm2025_fixed\isaac\train_isaac.py --viz kit ^
    --resume /home/egde/fangzhen_linux/incoming/rm2025_fixed/isaac/runs/rm2025_serial_isaac/spin_pure_v2\model_*.pt
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

