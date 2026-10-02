# 保存、切换、故障恢复

当前硬截止epoch：`1790714033.1554604`，对应 `2026-09-30T04:33:53.155460+08:00`。目前没有新的预算。

1. 先确认当前进程cmdline/cwd属于本任务，不凭快照PID发信号；禁止pkill python、killall或停止整个桌面。
2. 健康运行不要手工切换，supervise_speed.py负责阶段晋级。若因实现DR需切换，先把候选代码、测试、显式环境配置和新监督器准备完。
3. 当前训练的rescue_training.py有STOP_AFTER_SAVE机制：只在**当前run日志目录**创建该文件，训练会在下一次原子完整保存时退出（一般每25轮），而不是立刻强杀。不能在旧run目录写错。
4. 同时必须处理旧监督器，避免它把计划停止解释成预算结束并启动final回放。检查源码后只终止本任务旧监督器或增加明确交接模式；不能先杀训练再想怎么恢复。
5. 验证新完整checkpoint：CPU torch.load成功，有actor_state_dict、critic_state_dict、optimizer_state_dict、iter，tensor有限；记录SHA256。 `.partial`不能用。验证旧trainer已退出，才启动新trainer。
6. 新阶段使用唯一run/log名，保留RM_KEEP_STD=1，runner.load恢复actor/critic/optimizer/std；不得使用会重写std的旧默认暖启动方式。
7. 保留同一绝对deadline，在新env与监督器都传递它；记录源checkpoint、代码hash、环境差异、实际物理合同。不能简单再调用一次初始化10小时的脚本。
8. 启动后检查manifest与首轮PPO输出、唯一trainer、NaN/PhysX错误、GPU和最新完整保存；只看到进程PID不算完成。
9. 更新同目录status.json/终端监控/原线程自动化mod4-10的当前阶段说明，避免后台旧指令拉回错误任务。
10. 评测无权延长训练：到点停止训练，允许做必要终验，但不能偷偷继续优化参数。

故障分支：性能波动不重启；程序崩溃/NaN/映射错误先保留现场，隔离修复，原截止前从最后完整权重恢复。若主机再次重启，要重新核算而非自行许诺补足；本交接不授权额外预算。

不要直接重跑 `launch_speed.py`、`resume_after_reboot.py`、旧 `supervise_rescue.py` 的main；它们包含一次性历史假设。
