# MOD4v2 复旦奖励压腿跳跃

2026-11-06最新要求实际使用Newton/MuJoCo-Warp；`newton_model.py`、`newton_env.py`、`newton_checkpoint.py`、`newton_train.py`与`newton_evaluate.py`实现Kit独立的Newton SolverMuJoCo桥接。明确更换物理解算器，保留原模型、6闭环/4mimic、300N60mm气缸、D0–D7组件、35/78观测、复旦16项公式和完整PPO状态。当前不是Isaac Lab3管理器全迁移。正式20k状态与速度以工作单真实FIRST为准，小批量PPO或局部测试不能冒称生产成功。

用户要求先启动真实一小时PPO，再在训练中开发SuperMimic BPTT兼容。现有mod4-10已改为同聊天每30分钟ACTIVE：训练中做兼容，没训练优先评测/回放/续训；真200mm跳跃达标后换Isaac Lab台阶地图，SuperMimic实际梯度、更新和保存兼容通过后在保存边界切换。执行条件和原话见`NEWTON_MIGRATION_AND_SUPERMIMIC.md`与工作单。实际mod4-200-rl-bptt属于其它聊天的ACTIVE任务，不修改它。

实际Newton FIRST621已通过，20k首轮23483.90控制step/s，采样20.17294s、学习0.266594s。小批量H32 SuperMimic真实梯度/更新及四优化器replay保存恢复已通过，正式worker/eval尚待完成。速度诊断修复了每control重复解析YAML与重建扫描网格，三组姿态输出零差，本地128环境8control总耗时2.45458→1.13243s；这不是20k生产提速结果。线搜索逐world GPU打印改为原native overflow位累积和每轮汇总，4环境实际PPO通过；求解配置保持。当前active冻结包不热改，下一保存边界应用候选并实测。

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
