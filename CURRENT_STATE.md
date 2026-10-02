# 2026-10-03 归档时状态

正式训练仍在 MOD4_scut_spin_rate_20261002：20k env×24、solver16/4、原生平地、实际 root 0.25m、white_v1、完整 actor/critic/optimizer/std 暖启动。成熟 4rad/s model15583 有两 seed nominal/white 的 15s 回归证据，6rad/s 为当前学习档。归档时文件/status 只作快照，实时情况需读实际进程和唯一账本，不能把这里当实时监控。

目标原地 2转/秒=4π rad/s=120rpm，尚未达到。自转世界定向净进度 0.5m/s、普通组合转弯、Rough、云台负载和 MoE 不宣称已完成。普通转弯有独立冻结候选和短基线，未启动新转弯 PPO；传感器 full/delay 候选出现异常而拒绝，noise-only 初证据尚未正式部署。

唯一账本位于 MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json，总180000秒（50小时），36000+两条已应用72000扩展；归档不追加/复制/重置预算。两小时线程巡检授权继续，现有训练和其它 AI 任务未被本次收集打断。

旧窗口、eager5ms、积分均力及真实卸载/间隙/滑移保留。低力不是腾空，积分100%不是连续承重；实物弹簧力—行程未校准，仿真通过不是实车认证。
