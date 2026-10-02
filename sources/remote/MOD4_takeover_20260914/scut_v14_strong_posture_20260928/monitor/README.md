# MOD4 实时训练监控

打开 http://10.24.4.210:8765/ ，或双击 Ubuntu 桌面的“MOD4强化学习监控”。页面每10秒读取当前20,000环境任务的 TensorBoard scalar、supervisor 状态与 nvidia-smi。监控是只读进程，不修改 PPO、USD、奖励或检查点；无 GPU 计算。源代码为 monitor/server.py 和 monitor/index.html。

“训练进度与验收达成度”的条形图来自带探索噪声的训练批次，只显示趋势；右侧“确定性验收”读取最近的64环境×15秒无探索动作结果，明确标记旧检查点。旧检查点的结果不能代表当前策略已达标。现场严格门槛：存活≥80%、速度误差≤0.75m/s、倾斜≤8°、双主轮接地≥90%、动作差分/二阶≤0.18/0.25、闭链≤2mm、耦合≤0.01rad。

服务由用户级 systemd 单元 `mod4-monitor.service` 托管，用户 linger 已开启。查看状态：`systemctl --user status mod4-monitor.service`。监控自身日志：`journalctl --user -u mod4-monitor.service -f`。如需重启页面服务：`systemctl --user restart mod4-monitor.service`。服务不控制训练进程。

## Ubuntu 终端界面（默认）

Ubuntu 桌面的“MOD4终端训练监控”快捷方式现在启动原生 curses 终端仪表盘；无需浏览器或 HTML 页面。当前窗口已在 seat0 的 GNOME 桌面打开。按 `q` 关闭窗口，按 `r` 立即刷新；终端和后台每2秒读取；奖励等训练指标约每32秒完成一轮后更新。手动启动：`monitor/open_tui.sh`。TUI 只读本机监控服务的 JSON 指标，不执行任何训练、推理或 GPU 计算。图表中的步速指环境策略步/秒，奖励和动作平滑度来自带探索噪声的训练批次；右侧确定性评测独立显示并标记旧检查点。
