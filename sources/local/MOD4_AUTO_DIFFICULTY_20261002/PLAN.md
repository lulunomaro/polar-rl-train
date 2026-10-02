# 用户授权自主晋级：执行与边界

用户2026-10-02明确授权自己判断后上难度、加DR。不要等待重复确认。唯一有效预算180000秒（50小时），已有两次20小时扩展不可再应用；预算与原检查点目录保留。仍每两小时线程巡检，健康无变化安静。

## 已接入的下一步

review_spin_admission.py是一次性冻结复核监督器，不是训练器，也不是新预算owner。它等待现有PPO自然到保存边界、完整保存并退出、原监督器进入冻结回放后，才暂停该父进程的后续启动权限；让已有回放完成，再用同一完整候选进行两seed（20261002/20261003）各nominal/white_v1的15秒spin和独立flat回归。全部顺序执行，不并跑20k或重复现有探针。冻结过程不计有效PPO预算；结束或故障恢复原监督器，watchdog防止评测器意外退出后父进程一直停住。程序不修改生产物理/奖励/PPO/std，不直接切新课程。

六个原地自转/启停反转分组和独立flat回归作为进入移动试训的准入，同时保留spin_probe原整体失败布尔量以及原端点window统计。不能删除1m/s失败样本、把准入称总体毕业或放宽原滑移阈值。nominal/white同seed完整root/q要精确相同，否则先诊断，不称严格配对。

发现原spin_probe名义评测无条件引用env._mild_dr，该对象只在white_v1创建。修复仅在冻结评测入口：parameter_audit(env)为white保留原完整审计，为nominal读取真实质量/惯量/材料/局部COM/PD/电机输出scale并检查克隆一致性/有限数，不修改参数。原spin_probe和source freeze备份保存；过去报告的hash和失败标志保留。该诊断补丁不改任何技能门槛。

## 后续自主执行顺序

1. 复核通过后，在MOD4_SCUT_SPIN_TRANSLATION_PREPARE_20261002隔离任务完成真实SDK/body命令更新/观察奖励配对、.15m/s短物理与原能力回归、128env两轮PPO和20k全量验收。现有骨架不是已通过实际验收的训练器。以完整检查点和同一账本安全暖启动，预检权重弃用。
2. 移动从平均世界进度.15→.3→.5m/s；保留站跑和原地spin。明确理想.5净进度对应body瞬时峰1m/s，不能把速度模长或机身恒速绕圈当世界定向移动。若要求瞬时也限.5，重算可达进度，不虚报。
3. 新移动和名义回归多seed稳定后，准备并实际读回更宽白名单DR：质量/惯量共因子.90–1.10、主轮摩擦.70–1.00、六电机输出.90–1.10并重新执行原硬件包络，保留约20%名义样本和有限摩擦桶。此档未实现，先参数回读/同权重配对/PPO短验收再开启。一次只提高一个课程档，不同时加速度、地形和DR来混淆故障来源。
4. 按固定SCUT源码适配Rough v1低难度坡/起伏/台阶；必须有真实地面高度、完整闭链复位、scan/airborne和短物理/PPO验收。保留平地及spin回归，不能只翻terrain flag。随后才更高速spin3–4、6–8等逐级验证，实际电机力矩/转速/载荷余量决定能否提高。
5. 实物300–700N氮气弹簧力-行程未标定，当前3500N/m预载模型保持；不要盲改弹簧或声称已经完成该实物DR。云台/MoE是后续事项。

本轮只部署名义评测修复和两seed复核队列，不声称边转边走、更多DR或Rough已开训。复核收据MULTISEED_SPIN_ADMISSION.json到位后，本线程继续实现安全切换，无须用户再批准。旧一次性supervise_spin.py不可盲重跑。故障先看实际进程/active_segment/完整checkpoint，禁止双开、重复记账或从零重训。

## 17:57运行收据

原训练已自然保存model14141并退出，该权重用于本轮全部配对。reviewer PID1478805已进入paired_frozen_review；原supervisor1239785在无trainer、无active_segment时暂时SIGSTOP，仅阻止重复发评测和启动下一段。已等待原block_model14141_flat回放结束，当前独立nominal自转评测PID1480738；上述PID仅供定位，必须核对真实cwd/cmdline/start_ticks。reviewer有独立watchdog，结束或异常会清理自身评测后SIGCONT原父进程，不能把冻结期间父进程T状态误判为训练故障。不得重复运行reviewer或旧一次性supervise_spin.py。

名义入口补丁收据在旧root/reports/nominal_eval_audit_fix_20261002/APPLIED.json，spin_probe SHA9c39a80ace341494bd1c6a87559e5b4635f0b0e1eff60521633f1bef318ca90e，helper SHA0da20a0777fbbf4352252b8dca1bcfd0d17bd0f75ef34c539e8c40b50a320d78。6个CPU审计测试通过；实际Isaac名义运行是否通过仍以新reports为准。source manifest仅更新冻结评测器并补helper，物理/奖励/PPO/技能门槛和当前生产策略未改变。

复核status及报告在本目录，不是原status的自动汇总。最终读取reports/MULTISEED_SPIN_ADMISSION.json和原root/reports/AUTO_DIFFICULTY_MULTISEED_ADMISSION.json，先核实原父已恢复。此worker仅提供晋级证据，不会自动部署移动课程；通过后必须按以上第1项实际完成SDK/物理/PPO和保存边界接管。
