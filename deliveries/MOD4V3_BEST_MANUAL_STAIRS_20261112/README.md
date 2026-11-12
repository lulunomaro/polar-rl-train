# 2026年11月12日最牛逼的模型

用户选定名称，保存当前手动播放的 **Rough-v1 120分钟完整PPO权重**，iteration **24482**。模型、完整训练配方、实际训练源码、机械资产、手动回放和原始结果一起保存。

**已复现上台阶：** 本机MuJoCo名义条件，机身高度在2秒内从0.28m调至 **0.365m或0.40m**，3秒后给予 **2.2m/s前进指令**，均登上 **连续两级、每级16.5cm** 的宽台阶，进入 **33cm高平台**。踏面配置1.5m，使用本轮导出的低档宽阶 `r00_c00`。这条记录保留了高度和速度条件。

模型SHA256：`7cc1fc6deeee3d3aba8ae8d2da31dce200079fb229a145f1cbb1cd3bfabea103`。

| 需要找什么 | 入口 |
|---|---|
| 当前播放模型本体、完整PPO续训状态 | [model/training_checkpoint.pt](model/training_checkpoint.pt) |
| 模型身份、真实父权重与上阶条件 | [MODEL_IDENTITY.json](MODEL_IDENTITY.json) |
| 全部实际训练参数和DR范围 | [training/EFFECTIVE_RECIPE.json](training/EFFECTIVE_RECIPE.json) |
| 训练方法、启动命令和延迟语义 | [training/TRAINING_RECIPE.md](training/TRAINING_RECIPE.md) |
| 训练源码、地形、奖励与控制实现 | [training/support](training/support) |
| PPO有效参数、启动/恢复/资产原记录 | [training/evidence](training/evidence) |
| 上台阶成功视频与上台后停车轨迹 | [成功视频](media/upstairs_success_16p5cm.mp4) · [独立包回放记录](evidence/PORTABLE_REPLAY_CHECK.json) |
| 成功上阶的逐步轨迹 | [HEIGHT_STAIRS_RUNUP_CHECK.json](evidence/local_playback/HEIGHT_STAIRS_RUNUP_CHECK.json) |
| 手动方向和高度控制检查 | [MANUAL_CONTROL_CHECK.json](evidence/local_playback/MANUAL_CONTROL_CHECK.json) |
| 本机上下阶和完整地图 | [media](media) |
| 原始完整DR逐地形对照 | [training/PAIRED_COMPARISON.md](training/PAIRED_COMPARISON.md) |

## 手动回放

安装 `requirements-replay.txt` 中的依赖后运行：

```sh
python viewer/showcase.py --mode play
python viewer/showcase.py --mode map
```

Windows也可运行 `打开手动回放.ps1`；加 `-Map` 打开全地图，`-Python` 可指定Python路径。

默认暂停。先点击控制窗，P开始/暂停；W/S前后，A/D转向，松键回零；空格停车；R复位并暂停。Q/E降低/升高站立高度，1/2/3切换0.20/0.28/0.40m，滑条范围0.20～0.42m。面板显示高度指令和离地实测。上台阶、下台阶、各类地形起点与0～9档难度可选择。

当前机械MJCF和全部277个网格、runtime/semantics/reset bank及原有控制框架随包保存。750块地形由本轮Isaac Lab配置、seed66在本机重建；原始网格保存在viewer/tiles。MuJoCo名义可视回放使用2.5ms物理、10ms PD、20ms策略，闭链2mm保护。宽台阶碰撞按各级平台建箱体；其他地形碰撞由5cm射线采样高度场建立。runtime/core/template_spec.json只提供原模板的RobotSpec，策略权重始终读取本包的training_checkpoint.pt。

## 训练配方与能力记录

本模型从Rough-v0 100m、iteration23665、SHA `001028396205e7d44d69ac5af36cdbb638cc26b97daeea29439f84952a58f6e9` 接续。完整DR、20%名义与20%平地独立交叉；11族地形/10档，4096环境、seed66、rollout24、固定学习率3e-5、clip0.1、3个学习epoch；原奖励−1.5e²及指数项1.2；前进指令上限2.2m/s。实际训练7206.600秒、817次PPO更新，每5分钟完整保存。全部细节以effective recipe、启动、恢复和训练日志原件为准。

能力逐条件保存：高度0.365/0.40m、2.2m/s助跑条件已上两级16.5cm；高度0.28m、1m/s的旧录制卡在第一级；直接设高到0.40m而不缓慢调高的短测试也有重置。各次成功和失败都保留在evidence/local_playback。已有完整DR PhysX最高档宽阶上行仍是0/10，见原报告；本快照的命名和本机上阶演示不改写这些结果。原Step6/Step7冻结与R1实车调试包保留。

完整训练历史、原始26份完整PT和后续恢复入口，仍见仓库 `sources/local/MOD4V3_SCUT_ROUGH_V1_2H_20261112`。本包保存的是当前播放的120分钟点，未新增训练更新。
