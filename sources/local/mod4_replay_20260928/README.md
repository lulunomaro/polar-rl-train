# MOD4 华南虎式回放

安装位置：将 `replay_mod4.py` 放在目标机
`/home/egde/fangzhen_linux/isaac/mod4/`，将 `run_current_replay.sh` 放在
`/home/egde/fangzhen_linux/replay_tools/`。训练脚本、任务源码、USD 和检查点都不修改。

回放读取当前检查点旁边的 `run_manifest.json`，复原训练时的 `RM_*` 参数，并核对
任务源码、USD、导入合同的 SHA256。不一致时拒绝播放，避免把另一套物理效果误认成
当前策略。默认只接受训练高度范围 0.22–0.27 m；测试 0.32 m 必须显式写
`--allow_height_extrapolation`，输出记录也会标注这一点。

训练结束后，在目标机运行：

```bash
cd /home/egde/fangzhen_linux
bash replay_tools/run_current_replay.sh --headless --profile vel --seconds 15
```

训练进行中可以只检查合同与最新检查点，完全不启动 Isaac：

```bash
cd /home/egde/fangzhen_linux
/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python isaac/mod4/replay_mod4.py \
  --checkpoint runs4090/logs/2026-09-28_22-07-51_flat_v7_4090_20k_s16/model_1650.pt \
  --preflight
```

可视化键盘控制（需要桌面窗口）：

```bash
bash replay_tools/run_current_replay.sh --keyboard --seconds 60
```

W/S 前进后退，A/D 左右转，Z/X 调高度，空格令速度归零。窗口需获得键盘焦点。
例如做明确的 0.32 m 外推试验：

```bash
bash replay_tools/run_current_replay.sh --headless --profile hold \
  --vx 0.5 --height_cmd 0.32 --allow_height_extrapolation --seconds 15
```

输出写在 `replays/<run_name>/`：CSV 记录命令/实测速度、目标/实测高度、倾斜、
双轮接地、闭链/耦合残差、六电机力矩、按合同曲线估算的气弹簧力、动作差分和
各项奖励；HTML 每仿真秒更新一次，供曲线浏览；JSON 固定检查点与资产指纹并
汇总单环境结果。气弹簧力是按该 run 合同估算的值，开启 DR 时不等于逐步实测力。

默认在 PPO 运行时拒绝启动回放，避免抢占正在训练的 4090。需要并行时由操作者
显式设置 `REPLAY_ALLOW_CONCURRENT=1`。回放只显示单个或少数环境的行为，不能
替代同种子多环境、15 秒存活率及 300–700 N 气弹簧 DR 验收。
