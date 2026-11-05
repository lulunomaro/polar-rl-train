# Newton迁移与SuperMimic交叉推进

2026-11-06人类要求实际使用Newton/MuJoCo-Warp，并在正式一小时PPO开始后开发SuperMimic BPTT兼容。当前mod4-10已更新为当前聊天每30分钟ACTIVE，旧mod4-200-rl-bptt继续PAUSED。

执行顺序：

1. 完成真实Newton后端、完整final620学习状态接续，启动一小时20,000环境PPO，核实际FIRST621/梯度/完整保存。
2. 训练期间推进SuperMimic兼容；正式PPO启动前不提前做BPTT开发。
3. 无训练时优先完整保存、安全退出、独立80、当前模型实际回放，据实证修复并续训。
4. 从地面自主上跳、双轮整轮离地越过单200mm直角台沿、双轮台顶稳定0.5s验收通过后进入Isaac Lab台阶地图。spawn下落反弹、贴轮爬台不能算。
5. SuperMimic需实际梯度、参数更新、完整保存与模型物理/奖励/接口兼容证据，通过后在完整保存边界切换，不能凭import通过切换。

最新原话完整保存在WORK_ORDER.json的supermimic_interleaving.human_quote。用户直接真实空闲GPU/noledger最高指令保持：不因账本或别聊天控制器等待，不覆盖别聊天账本，不终止别聊天。GPU私有锁、硬件资源、累计100h上限、完整保存及所有失败Git记录保持。

旧PhysX+Warp段已关闭，source461→final620共159PPO/76.32M样本，完整小时均24557.616 step/s，约旧完整小时1.515倍，不能称3倍。原owner退出psutil.ZombieProcess竞态导致漏评测，原错误保留；仅补缺失独立80已完成，80/80均无有效地面起跳、越沿或落台。final620学习诊断已完成唯一一次，不重复解模。

Newton当前已通过CPU/GPU20physics、完整35actor/78critic/192physics及4环境一次真实PPO迁移测试。正式20k生产尚未启动；现使用Newton SolverMuJoCo直接桥接，不能称完整Isaac Lab3管理器迁移。MuJoCo-Warp前向求解不是可直接反传物理，SuperMimic按实际动力学模型/BPTT实现接入。

实际INDEX、once、owner收据、控制进程与工作单最新值优先。所有试错和报告保留，媒体/模型仅真实路径、大小、SHA，不为归档重跑物理或解模。

迁移实际试错：

- `newton_fudan_final620_1h`首次20k尝试在CUDA编译时拒绝过长TMPDIR，0PPO，25.188363s后自身安全退出/释放；原错误完整保留。
- `shorttmp02`使用唯一私有短TMPDIR后，实际恢复final620/17Adam12400/LR0.0005766503906250003/全部7组件RNG队列，第一物理步EPA临时工作区申请7,688,880,000B失败，0新PPO，70.402157s后退出/释放。完整恢复收据与失败均保留。
- 检查发现Newton通用`rigid_gap=.1`在导入省略gap的MJCF几何时生效；初始468个记录全部正间距0.038–0.199m、nefc仅22，属于无力候选接触。新转换显式保留原MuJoCo默认gap0，并从有效reset pose分配；没有关闭自碰撞、改CAD、降低解算器精度或缩减20k环境。小批量真实PPO/24control/192physics/20Adam通过，闭环0.311mm、mimic0.001576rad。
- 为远端CUDA12.2驱动按MuJoCo-Warp实际警告关闭conditional graph nodes；物理步CUDA Graph保留。`authored_gap03`为此具体修复的新尝试，未重放旧once或热改旧包。
