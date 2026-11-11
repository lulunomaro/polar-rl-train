# Flat 完整 DR：速度平方项 1.5 实验

2026-11-11 用户授权“调整一下继续试一下flat课程”。从冻结 Flat `square1_030m`（iter22618，SHA `d5e176401c20dd1b88a74003f7d4993aadc9a9cda301f042953de08fb6108851`）恢复完整 PPO，新物理 episode。

唯一奖励变化：`track_lin_vel_xy_square: -1.0 -> -1.5`，sigma=1；实际每策略步 `-1.5 × (command_vx-vx*cos(pitch))² × .02`，超速和欠速对称。保留指数项1.2及其他奖励。

Flat4096env，819名义参数＋3277完整DR；原MOD4、35/78/6、2.5/10/20ms、TGS32/4、2mm单环境重置。LR3e-5固定、clip.1、3epochs、seed66。

40分钟训练，每5分钟保存完整PT并检查；每点MuJoCo名义回放，结束父模型与8点同批PhysX名义/完整DR配对。检查前进2.0/2.2、后退、旋转、高低身及组合任务，2.7仅诊断。完整PT实体入Git，网络7897代理。

状态：已启动，结果待完整同批评测。此次回Flat，不推进R1。

准备记录：初次复制脚本插入首个PPO保存的定位字符串未匹配，准备进程退出；未上传/未启动GPU。随后按实际monitor的PERIODIC读取位置完成适配。

已于 2026-11-11 16:58:13 Asia/Shanghai 启动，PID1199368。实际STARTUP系数−1.5；RESTORE确认actor/critic/STD/Adam/globalRNG恢复，父iter22618。首完整PPO iter22619，SHA`865cd88a45a41c64904e69350f38176bdf3ae5aded1185dac0924b96e3190a58`，11,048,951bytes，已拉回weights/。短奖励探针无optimizer，24步，无重置，闭链峰0.287970mm，公式误差1.49e-8。首PPO有567次闭链单env reset、numerical0；因此不能把短探针健康写成整轮没有物理终止。

准备读取记录：一次本地JSON读取报空内容，随后重新读取原LAUNCH成功；远端训练与保存未受影响。

配置范围核对：support仅scut_flat_forward_square_env.py与上一Flat轮不同，实际训练owner及其他DR/接口/solver源相同。本轮未开同父同seed−1.0控制组，结束同批评测衡量接训效果，不把全部变化单独归因于加权。

10分钟检查完成：MuJoCo名义2.0→2.159249、2.2→2.421463；仍超原±.15。后退/旋转/高低身各10/10，全部回放reset0。首及5m/10m完整PT已本地保存。训练numerical0；训练随机指令与起身瞬态统计不作为固定任务通过。

15分钟名义MuJoCo：2.0→2.132218（10/10），2.2→2.382817（0/10）；后退−1.387781仍10/10，但相比5m精度下降需在最终PhysX中对照。旋转14.110489、高低身各10/10，无reset。未因单引擎指标晋升。

用户于本轮约18min要求下个保存点切Rough。实际Flat020m完整保存1204.923s，iter22856，SHA`a5102af62938f6bf472855edba34c5f10efce061eecaeb3aebee34815fe7cf87`后发SIGINT并确认原进程退出/GPU释放，接续Rough。Flat未执行完整40min，不补造FINAL；此次未观察到SAFE_CLOSED标记，不能宣称正常finally关闭。后续PhysX配对合入接续Rough阶段。020m名义回放2.150582/2.390690，其他四项10/10、reset0。


本段最终结果（同批评测在后续Rough目录）：保留Flat020m，完整DR2.0→1.895267（5/10）、2.2→2.156276（8/10），MAE0.121645；后退−1.456237、旋转13.499511、高低身各10/10，正式44/60、全部正式/诊断reset0。浅地形首次穿越120/120。原父同批MAE0.129366、44/60、1正式reset。未用新系数控制组，不能仅归因奖励。查看`../MOD4V3_ROUGH_R0_SQUARE15_20261111/FINAL_REPORT.md`。
