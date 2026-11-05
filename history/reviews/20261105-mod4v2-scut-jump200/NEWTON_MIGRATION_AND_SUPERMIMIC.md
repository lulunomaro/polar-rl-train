# Newton迁移与SuperMimic交叉推进

2026-11-06人类要求实际使用Newton/MuJoCo-Warp，并在正式一小时PPO开始后开发SuperMimic BPTT兼容。当前mod4-10已更新为当前聊天每30分钟ACTIVE。实际mod4-200-rl-bptt已属于其它聊天的ACTIVE任务，不修改它；旧PAUSED描述已过时。

执行顺序：

1. 完成真实Newton后端、完整final620学习状态接续，启动一小时20,000环境PPO，核实际FIRST621/梯度/完整保存。
2. 训练期间推进SuperMimic兼容；正式PPO启动前不提前做BPTT开发。
3. 无训练时优先完整保存、安全退出、独立80、当前模型实际回放，据实证修复并续训。
4. 从地面自主上跳、双轮整轮离地越过单200mm直角台沿、双轮台顶稳定0.5s验收通过后进入Isaac Lab台阶地图。spawn下落反弹、贴轮爬台不能算。
5. SuperMimic需实际梯度、参数更新、完整保存与模型物理/奖励/接口兼容证据，通过后在完整保存边界切换，不能凭import通过切换。

最新原话完整保存在WORK_ORDER.json的supermimic_interleaving.human_quote。用户直接真实空闲GPU/noledger最高指令保持：不因账本或别聊天控制器等待，不覆盖别聊天账本，不终止别聊天。GPU私有锁、硬件资源、累计100h上限、完整保存及所有失败Git记录保持。

旧PhysX+Warp段已关闭，source461→final620共159PPO/76.32M样本，完整小时均24557.616 step/s，约旧完整小时1.515倍，不能称3倍。原owner退出psutil.ZombieProcess竞态导致漏评测，原错误保留；仅补缺失独立80已完成，80/80均无有效地面起跳、越沿或落台。final620学习诊断已完成唯一一次，不重复解模。

Newton当前已实际启动20k一小时PPO，并从full620完成FIRST621、192physics、20Adam、非零actor/critic梯度及完整首存。现使用Newton SolverMuJoCo直接桥接，不能称完整Isaac Lab3管理器迁移。MuJoCo-Warp前向求解不是可直接反传物理，SuperMimic按学习动力学模型/BPTT实现接入。

实际INDEX、once、owner收据、控制进程与工作单最新值优先。所有试错和报告保留，媒体/模型仅真实路径、大小、SHA，不为归档重跑物理或解模。

迁移实际试错：

- `newton_fudan_final620_1h`首次20k尝试在CUDA编译时拒绝过长TMPDIR，0PPO，25.188363s后自身安全退出/释放；原错误完整保留。
- `shorttmp02`使用唯一私有短TMPDIR后，实际恢复final620/17Adam12400/LR0.0005766503906250003/全部7组件RNG队列，第一物理步EPA临时工作区申请7,688,880,000B失败，0新PPO，70.402157s后退出/释放。完整恢复收据与失败均保留。
- 检查发现Newton通用`rigid_gap=.1`在导入省略gap的MJCF几何时生效；初始468个记录全部正间距0.038–0.199m、nefc仅22，属于无力候选接触。新转换显式保留原MuJoCo默认gap0，并从有效reset pose分配；没有关闭自碰撞、改CAD、降低解算器精度或缩减20k环境。小批量真实PPO/24control/192physics/20Adam通过，闭环0.311mm、mimic0.001576rad。
- 为远端CUDA12.2驱动按MuJoCo-Warp实际警告关闭conditional graph nodes；物理步CUDA Graph保留。`authored_gap03`为此具体修复的新尝试，未重放旧once或热改旧包。

- `authored_gap03`在0PPO时遇到真实非有限传感器输入，372.343848s后完整保存中断状态并退出。`episode_reset04`按单环境数值重置语义修复，真实FIRST621通过，但首轮47次单环境数值重置仍需独立80核查，不能称数值无错误。旧失败保留。

当前`episode_reset04`实际GO03:31:23.539602、SAVE04:31:23.539602、NOMINAL04:36:23.539602（2026-11-06北京时间）。原launch41976已退出，sole35288负责原窗完整保存、安全退出后80和正式回传。训练中只查该本地exact进程及回传文件，不起第二SSH或控制器。

SuperMimic已在FIRST621后开始开发。原固定learner通过SHA引用，4环境64controls/512physics/256条真实复旦标签，24WM与24aux更新以及一次H32 BPTT通过。跨时梯度0.0006620657、WM路径梯度0.0003733160、策略参数变化0.002172055，四优化器/replay/RNG/history保存恢复通过。PPO零残差起始动作CPU验证通过。正式有限worker、eval和完整环境流恢复尚待完成，未切换生产BPTT。

2026-11-06速度实证与具体修复：

- Newton首轮控制采样23483.90 step/s，collection20.17294s、learn0.266594s，98.70%用于采样。此前PhysX+Warp完整小时均24557.62 step/s；目前没有Newton生产提速证据。
- 首轮正式返回的WORKER日志10509950字节，包含58229次线搜索到达15次上限警告；47次数值重置按FIRST计数，后续日志覆盖到222ticks，不冒充同一统计窗口。
- 本地128环境/8controls诊断发现每次`scans()`重新读取解析固定训练YAML并创建同一网格，函数CPU总时间1.16947/2.60937秒，约44.8%。8controls还出现39306次kernel launch与4368次stream synchronize；比例为本地诊断，不能套到远端20k。
- 改为constructor一次构建固定扫描网格。三组姿态、每组六个扫描输出逐项零差；本地单次扫描约130.026ms→2.942ms。同128环境8步未profiler总时间2.45458→1.13243秒，约2.17倍，仅本地小批量实值，未宣称20k生产提速。
- 线搜索GPU逐world printf改为原生overflow位累积、每轮汇总world mask；保留15线搜索/32迭代设置与原overflow位。实际4环境24control/192physics/20Adam通过，`1024`线搜索溢出仍出现在报告，未以静默日志冒充收敛。
- 原active冻结代码、当前owner和once均未修改。修复用于下一完整保存边界候选；需要新的真实20k整轮测量。下一热点是尚未在direct Newton桥启用的400Hz融合验收、状态和D4队列。

完整报告在`N/reports/NEWTON_SAMPLING_SPEED_DIAGNOSIS.json`。原始profiler TRACE约92MB各一份，只索引真实路径/字节/SHA；不复制进Git文字对象。
