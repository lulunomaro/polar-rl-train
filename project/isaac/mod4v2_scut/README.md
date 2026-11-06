# MOD4v2 复旦奖励压腿跳跃

2026-11-06采样优化：对照basic_loco_lib固定commit后，新增`--sampling-optimization`，融合400Hz闭链/验收和50Hz复旦16项，并保留四Adam状态启用fused执行、learned几何TorchScript图执行。真实本地128环境隔离ABBA总训练吞吐1.44394倍、采样1.78536倍；输出/梯度/完整恢复后H32通过。当前冻结小时不热改，2万环境生产收益待保存评测回放后接入实测。见`OFFICIAL_SAMPLING_OPTIMIZATION.md`与工作单sampling_optimization_20261106。

2026-11-06 10:32最高实际：原服务器重启，旧窗无final；已完成幸存fullFIRST1941的独立80/唯一全状态诊断/全部4实际姿态图审阅，0成功。新增每300s原子完整保存已真实测试恢复后H32通过；新段supermimic_first1941_reboot_periodic_1h实际FIRST1942/fullsave和完整恢复有效，sole79388，SAVE11:30:26.533121。先读HOST_REBOOT_FIRST1941_RECOVERY.md及WORK_ORDER.reboot_recovery_and_periodic_continuation，下文网络故障/旧sole均为历史。

2026-11-06 07:44最高实际覆盖：原collector75124于07:24:39因SSH TCP超时退出；缺失回传恢复也超时。到原服务器不可达而普通外网可达，最终保存/退出/80状态Unknown；当前0收集器。先读`POSTROUND_NETWORK_RECOVERY_PENDING.md`，仅有限恢复同一窗结果，禁止重launch/evalonce或把下文历史FIRST/healthy描述当当前状态。

2026-11-06 06:25最高实际：SuperMimic full1940已完整保存/安全退出/独立80/全部实际回放审阅，1908H32更新与四Adam/replay/RNG完整，但80/80在.68–1.04s导轮06接地终止、0真200mm成功。仅残差输出尺度1→.25候选实测平均5.534s、39/80满7.98s、仍0跳上台，完整恢复测试通过；新段从full1940全部学习状态续训，实际FIRST1941+1H32/fullsave通过，sole75124，SAVE07:23:33。物理、复旦奖励、DR不变。详见`FINAL1940_ALL80_AND_RESIDUAL025_CONTINUATION.md`与工作单。下文05时记录为历史。

2026-11-06 05时更新：Newton上一完整小时实际final881/261新PPO，日志均37325.8控制step/s；独立80仍0真实200mm成功，约束异常原报告保留。新段将原10mm闭链/.01rad mimic重置落实到400Hz，异常control不进入SuperMimic标签。首个20k BPTT段因碰撞工作区显存不足而0更新退出；修复后2.26GB完整replay放内存，仅batch送GPU，保留20k/物理/奖励/H32。环形采样逐值比对、真实4环境H32及四优化器/replay完整恢复通过。正式20k新段实际FIRST/H32跨时间和WM路径梯度、参数变化及2.329GB完整首存均通过，原PPO来源保留；仍有数值/约束重置，技能与稳态速度待本轮独立80和完整日志。见`FINAL881_AND_SUPERMIMIC_MEMORY_REPAIR.md`。

2026-11-06最新要求实际使用Newton/MuJoCo-Warp；`newton_model.py`、`newton_env.py`、`newton_checkpoint.py`、`newton_train.py`与`newton_evaluate.py`实现Kit独立的Newton SolverMuJoCo桥接。明确更换物理解算器，保留原模型、6闭环/4mimic、300N60mm气缸、D0–D7组件、35/78观测、复旦16项公式和完整PPO状态。当前不是Isaac Lab3管理器全迁移。正式20k状态与速度以工作单真实FIRST为准，小批量PPO或局部测试不能冒称生产成功。

用户要求先启动真实一小时PPO，再在训练中开发SuperMimic BPTT兼容。现有mod4-10已改为同聊天每30分钟ACTIVE：训练中做兼容，没训练优先评测/回放/续训；真200mm跳跃达标后换Isaac Lab台阶地图，SuperMimic实际梯度、更新和保存兼容通过后在保存边界切换。执行条件和原话见`NEWTON_MIGRATION_AND_SUPERMIMIC.md`与工作单。实际mod4-200-rl-bptt属于其它聊天的ACTIVE任务，不修改它。

实际Newton FIRST621已通过，20k首轮23483.90控制step/s，采样20.17294s、学习0.266594s。小批量H32 SuperMimic真实梯度/更新及四优化器replay保存恢复已通过，正式worker/eval尚待完成。速度诊断修复了每control重复解析YAML与重建扫描网格，三组姿态输出零差，本地128环境8control总耗时2.45458→1.13243s；这不是20k生产提速结果。线搜索逐world GPU打印改为原native overflow位累积和每轮汇总，4环境实际PPO通过；求解配置保持。当前active冻结包不热改，下一保存边界应用候选并实测。

04:20有限SuperMimic训练与评测入口现已完成：`supermimic_train.py`、`supermimic_evaluate.py`，真实本地随机PPO来源34轮得到2次验证H32更新，完整四优化器/replay/7组件DR与RNG流保存；恢复CLI至35轮得到第3次BPTT。独立80接口、实际保存姿态图原生审阅完成，0跳跃；仅接口测试，不是生产策略成绩。数值异常标签从归一化、WM、aux、想象起点中排除并保留stream cut。新段20k replay容量64、预计2.26GB，正式显存和策略切换需本轮真实final80/回放后确认。有限截止测试在已过截止时间下仍完整保存退出、0新优化器步，不延长原窗。

2026-11-06最新人类要求先用复旦奖励学习压腿跳跃，并明确不再因账本等待，直接训练。当前选择复旦`yly-true/fudan_rl_wheel_leg`固定commit `8204e853dfd2ed06d85a322e1a998c3d20a3be2c` 的jump完整16项奖励及原逐项裁剪。`fudan_source.py`直接抽取18个原方法，`FUDAN_SOURCE.json`记录原字节SHA、行号、权重与来源；没有混入华南虎基础奖励或weight12速度项。MOD4v2实测body-frame hip锚点到轮心的矢状面长度/角度替代参考机器人连杆公式；保留原0.16m空中收腿、0.31m接地正vz伸腿、0.65m腾空高度目标及contact OR滤波。15项CPU检查已通过。

华南虎窗按人类切换要求完整保存至final357（17Adam7140、LR0.0002562890625000001、STD与7组件/RNG/队列/counter8568），独立80与全部实际回放仍0有效起跳上台。新复旦窗从完整final357接续，保留硬件/PD/DR/PPO/35actor78critic。最高指令覆盖旧账本准入，采用真实空闲GPU私有锁与固定3600s保存+300s退出，直接owner不读写canonical。旧账本拒绝、旧等待进程和全部失败保留；其它聊天继续运行。当前FIRST与真实时间边界见工作单。

以下为华南虎阶段历史来源。

人类2026-11-05要求停止旧训练、换MOD4v2并用华南虎奖励重训。运行代码引用原SCUT公式、训练循环、完整保存和独立80评测，仅新增v2资产/目标/复位接入。新actor、critic、STD和Adam从随机初始化开始，旧v1失败策略不载入。

模型来自`F:/RMPOLAR-RL/mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package`：300N全伸展标称力，200mm伸展、140mm压缩、60mm行程；k2000/d3仍为工程近似。主动hip/crank与从动坐标连续，保留真实CAD等效止挡。

实际OmniPhysics110对发布USD的无限角mimic与单侧角界导入失败，首个20k任务在0PPO时安全关闭。独立新任务层把开放角端点编码为±1e20度数值哨兵；真实有限端点、关节类型、mimic、几何、质量、COM和气缸保持。小规模原生检查确认31body/30DOF、全部硬界回读、20物理步mimic最大误差1.65e-5rad且完整日志无引擎错误。被否决D6表达及读者错误都留存。

奖励采用固定SCUT commit `1a26356d6f591734d4f6f666f5cead1a6925da67` 的保存基础reward字典，启用源码可选的push-height、push-velocity和peak-height公式，权重2/1/2。单200mm场地、实际ray触发、MOD4轮半径及禁物理助推是明确任务适配，不声称公开训练的逐字复现；v1累加projection/bilateral/tuck等奖励修补不带入。

final239之后选择同一固定华南虎源码的`takeoff_vel_z`奖励：仅push阶段计算`clamp(world_vz,0,3)`，原weight4训练至final346，push向上速度均值0.064225→0.223073m/s，最大0.185133→0.421753。独立80仍0有效起跳/越沿/落台，全部push轮底不超过1.312mm。全部实际回放已审阅，据此只将该权重4→12；dt仍在原reward tail乘一次，基础字典与原2/1/2保持，未引入新奖励公式或物理助推。3项源码公式和6项既有v2检查通过；从完整final346/17Adam6920/STD/组件RNG队列计数器接续，原newconstructor nominal保护与一次fresh physical reset保持。首次准入遇原共享账本实际占用而拒绝，原false保留；实际释放后追加admission_resume01并启动，FIRST与窗口边界以实际回传为准。

20,000环境、3600s保存+300s退出、完整actor/critic/STD/Adam/DR/RNG/queue/counter保存、退出后立即独立80/seed9137/400Hz评测保持。旧canonical/reserve准入现由最新直接训练指令覆盖。目标仍为地面主动向上离地、整轮腾空越沿、双轮真实台顶稳定0.5s。

当前真实状态和所有失败见`history/reviews/20261105-mod4v2-scut-jump200/WORK_ORDER.json`与`EVIDENCE_INDEX.json`。原目录及once不清除、不重放。`BINDINGS.json`记录唯一共享依赖；新任务不整树复制旧生产目录。

人类最新要求“不用等控制器释放，账本共用，直接开训别浪费时间”。本地控制器清单现为信息记录，不再因另一聊天的host86收集器而阻断本聊天SSH/取回/启动；原服务器canonical余额、strictreserve、GPU私有锁与实际扣费准入保持。final60→148的闭窗新增88PPO、42.24M样本，完整17Adam2960；独立80全部7.98s但0真实起跳/越沿/落台。全部4张侧/顶回放图和7.98s原mesh视频关键帧已原生审阅。最新明确指令下从完整final148开下一小时，实际FIRST与时间边界只以工作单和原owner回执为准。

第二次0PPO失败来自旧motor_stop_terms对连续关节None端点的假设；新v2奖励适配器明确将4个无独立角界电机的限位辅助代价返回0，不修改SCUT奖励公式和权重。6CPU和3phase真实源reward调用的合成端点均有限；独立rewardapi03已启动，FIRST以实际回传为准。

首轮实际完成60次PPO更新（28.8M样本），final60已完整保存并回传，训练和原owner安全退出。随后的独立80评测在导出场地时访问了旧scut_step270网格，实际场地为scut_jump200，因此RESULT/ALL80未生成，不能称评测通过。v2 configure现同步共享配置选出的MESH，单项CPU验证通过；旧冻结生产包和原始错误保留。补评测仅用同一final60、0优化器操作，在原canonical和锁释放后进行，不重训。
# Warp sampling replacement (2026-11-06)

Human authorized replacing the sampling flow using `basic_loco_lib`.
`warp_train.py` enables GPU kernels and CUDA graphs for400Hz contact reduction
and jump acceptance plus the50Hz16-term Fudan reward. `warp_tests.py` compares
the existing equations and state transitions, including resets. The initial
replacement keeps PhysX TGS32/4; full Newton backend migration is not claimed.
The old active segment is frozen; switch only from its actual complete final
after independent80 and native saved-pose review. Local component benchmarks
are not an end-to-end throughput result. See `WARP_SAMPLING_REPLACEMENT.md` in
the v2 review directory for actual timings, limits and retained failures.
