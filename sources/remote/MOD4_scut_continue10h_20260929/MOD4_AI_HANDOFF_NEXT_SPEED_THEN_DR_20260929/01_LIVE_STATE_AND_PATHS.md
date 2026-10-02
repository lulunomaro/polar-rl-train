# 实时状态与入口

## 当前运行（快照 2026-09-29T23:22:14+08:00）

- task root：`/home/egde/rl_candidates/MOD4_scut_continue10h_20260929`
- `status.json`：stage、iteration、training_pid、attempt、latest_checkpoint、speed_limit_m_s、evaluation_path、deadline_epoch。
- 监督器：`isaac/mod4/supervise_speed.py`，日志 `supervisor_speed.log`。
- 当前训练：`train_3.log`，PID 169956（仅快照；不可凭旧 PID 发信号）。
- 当前完整权重：`/home/egde/rl_candidates/MOD4_scut_continue10h_20260929/logs/2026-09-29_22-59-51_scut_speed_1.5m/model_5225.pt`。
- 当前日志目录：`/home/egde/rl_candidates/MOD4_scut_continue10h_20260929/logs/2026-09-29_22-59-51_scut_speed_1.5m`。
- Python：`/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python`。
- 已废止的旧监督器 `resume_after_reboot.py` 不可重启；`launch_speed.py` 是已执行的一次性交接工具，不可再跑。
- 当前 UI：`isaac/mod4/tui_rescue.py`，`start_tui.sh` 可打开终端；UI 只读、5 秒刷新，不负责训练。

## 已做完

- 原 model4725 和 model4950 在 64env×1500step、seed20260926 的 0/.3/.6/1m/s 四档窗口回放均 100% 通过。
- model5050 提速预检：+2m/s 从静止突变，8/8 约 0.52 秒终止；±2m/s 缓升/刹停/反向 15 秒全部存活，但接触窗口仍未通过。
- ±1.5m/s 加减速 15 秒以及另外 48env×5 秒突变指令检查安全通过。后者不是 15 秒性能通过。
- 原训练在 model5150 保存后退出；SHA256 `7db69742da42839a1cedf1cd0b9319d6ab7191d303c98514cf1bfee852d44d00`，见 speed_baseline_checkpoint.json。
- 1.5 阶段从 model5150 的 actor/critic/optimizer/std 继续，已核验首轮 PPO 输出与 manifest，只有 `RM_CMD_VX_MIN/MAX` 从 ±1.2 改为 ±1.5。
- 保持 20000env×24、solver16/4、根高度0.25m、DR关闭、10%站立。奖励/物理/闭链复位代码哈希未变。

## 自动处理与尚未处理

监督器至少在5150+100=5250轮后安排首次新评测，然后每小时评测。1.5范围性能/停车通过且2m/s外推安全通过才自动保存并切2m/s。具体看源码，而不是看到文件名就推断已晋级。

本监督器**不会自动开启 DR，不会自动切 Rough**。这两个阶段需要下一 AI 实现和验证。时间不足则如实交付，不能越过截止时间。

主要输出：`reports/speed_1.5m_model*.json`、`reports/speed_2m_model*.json`、`reports/final_speed_nominal.json`。文件缺失但对应评测进程活着表示尚在运行，勿重复启动。
