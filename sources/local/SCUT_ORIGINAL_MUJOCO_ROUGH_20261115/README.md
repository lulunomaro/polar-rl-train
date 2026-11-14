# 华南虎原模型：复用 WASD MuJoCo 播放器

2026-11-15，按用户澄清使用**之前的 WASD MuJoCo 窗口**。本次是推理与可操控回放，没有启动训练。

实际权重：SCUT `rough_rotation_stair/2026-07-23_16-23-21/model_1000.pt`，iteration 1000，SHA256 `d19492be858ffd431a67e5aa40afb4a4c51dc9a1c914c5c92022ed46d5868db7`。原参考说明把这一训练标为上台阶较好的模型。本目录 `weights/` 保存完整 PT 正文。

运行：在本目录执行 `D:\claude2\fangzhen\.venv\Scripts\python.exe -X utf8 -B -u scut_player.py`，或者双击 `启动华南虎MuJoCo.cmd`。窗口初始暂停，点击控制面板后按 P 开始。

| 操作 | 控制 |
|---|---|
| 前进、后退、转向 | 按住 W/S/A/D，松开停车 |
| 调整高度 | Q/E；1/2/3 高度预设；高度滑块 0.20–0.42 m |
| 调整行驶/转向速度 | 控制面板滑块 |
| 跑动中发送跳跃指令 | 空格，或者“空格 起跳指令”按钮，保留当前运动键 |
| 开始/暂停 | P |
| 清零运动键 | K |
| 回到当前地图起点 | R，复位后暂停 |
| 切换地形 | 选择地形和难度 0–9，点击上台阶/下台阶/跑图起点 |
| 全地图 | “打开完整地形地图”按钮 |

复用的播放器：`deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112/viewer/manual_control.py`、`runtime/core/play_ppo_flatv1_control.py` 的控制窗口、键盘队列、暂停/高度控制和场景选择；`showcase.py` 的已有地形与全地图。新文件只提供原版 SCUT 的推理和机器人后端及必要的按键接线。

地图来自既有 Rough-v1 保存生成器的 MuJoCo 重建，11 类、10 难度、原地图 75 列；宽台阶沿用 box 碰撞，其余沿用采样 heightfield 碰撞。此处是 MuJoCo 回放，不是原生 Isaac/PhysX 的实测结果。

机器人使用作者 ROS2 sim2sim 包中的 `wheelbipeV14_2.xml` 及配套 STL，18 个单自由度关节、浮动底盘、6 个闭链连接；该 MuJoCo 参考有固定云台，未包含 Isaac USD 的导轮拓扑。保留这一差异，不能把回放视为原生 USD 的动力学等价验收。生产 MOD4 资产、权重、训练源码没有改动。

接口：35 维观测、6 维动作；顺序为作者 ROS2 normal-policy 合同 `[left_front1,left_rear1,right_front1,right_rear1,left_wheel,right_wheel]`。尺度按原保存配置：高度 ×5，机体角速度 ×0.5，关节速度 ×0.1，动作历史保留策略动作。四腿 PD 60/2、力矩限幅 40；轮速目标 ×10、Kd 0.2、力矩限幅 5。弹簧复用原保存配置线性关系 `400 + (600−400)/0.07 × max(0.06076−q,0)`，名义随机偏置 0，执行器阻尼 50。物理 1 ms、策略 20 ms。这里是名义参数回放，不是 full-DR 重新评测。

空格发出 25 个策略步的 jump onehot、目标 0.70 m、时间槽，沿用官方旧播放器的手动窗口接口含义；不改策略动作、不施加机身冲量或瞬移。公开权重的保存配置 `jump_takeoff_state_machine_cfg.enabled=false`，因此按钮接通不能证明模型具备主动跳跃能力。本次在平地以约 1.23 m/s 跑动时触发，窗口内机身最高上升约 7.09 cm，**没有观察到双轮同时脱离接触**，尚不能报告真正起跳成功。

验证证据：`evidence/HEADLESS_PROBE.json`。每类 8 s，平地/随机起伏/低速宽台阶三段均无重置，最大闭链误差约 0.44 mm。台阶段只证明回放可运行，不能称连续台阶通关。保留原 2 mm 单环境闭链保护。控制窗口中实按空格已看到跳跃请求并保留运行速度的提示；已修复新后端地形处于默认隐藏显示组的问题，重新打开后实际看到机器人和台阶。

排查历史完整保留：最初错误弹簧公式的短探针保存为 `HEADLESS_PROBE_initial_spring_mismatch.json`；按原源码公式修正后独立重测。用户澄清前的一次原生 Isaac 播放尝试因本机 RSL-RL 5.x 缺失旧接口失败，保存为 `superseded_native_isaac_attempt.*.log`；该方向已结束，没有修改本机安装。

当前另一个对话的两小时 MOD4 训练保持运行。本任务不晋升、不覆盖其父权重。

## 同屏对比我们的冻结综合最优

用户随后要求保留华南虎窗口，另开我们的最优模型。`open_best_mod4.py` 已使用原播放器和该综合父模型已有的训练对应接触/姿态保护打开第二套窗口。实际权重为 `deliveries/MOD4V3_BEST_COMPREHENSIVE_20261113/model_full_ppo.pt`，SHA256 `db6e9ccf5c6d4d05a68633fd82861d903c4c52fcc1a6dd89132e55e2a4bf1283`，iteration 25331；登记表中仍是冻结的综合默认模型。新窗口与华南虎各自独立，未结束或重启已打开的华南虎。

运行第二个窗口：`D:\claude2\fangzhen\.venv\Scripts\python.exe -X utf8 -B -u open_best_mod4.py`。注意键位沿用：我们的旧控制窗里空格停车；SCUT 专用测试控制窗里空格发送跳跃指令。两边均按 P 开始，WASD 驾驶，Q/E 调高度。我们的运行状态保存在 `runtime_mod4/`，SCUT 保存在 `runtime/`，不互相覆盖。
