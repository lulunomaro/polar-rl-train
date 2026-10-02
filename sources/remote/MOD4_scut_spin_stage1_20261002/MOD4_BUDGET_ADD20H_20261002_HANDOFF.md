# 2026-10-02 用户再次追加20小时：唯一已应用交易

用户原话：预算再添加20小时。追加 ID `USER_ADD20H_20261002_1520`，72000秒，已登记到同一个 canonical 账本；原108000秒＋72000秒＝180000秒，即总有效50小时。本文件优先于之前交接中“总30小时/108000秒”的旧值。

账本仍为 `/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json`。不可复制新预算，清零 charged，或把同一次授权重复添加。两条20小时扩展分别是 USER_ADD20H_20261001_2341 和本次 USER_ADD20H_20261002_1520，均有明确独立用户授权。

收据在当前 root `/home/egde/rl_candidates/MOD4_scut_spin_stage1_20261002/reports/USER_ADD20H_20261002_1520_APPLIED.json`，并有 VERIFIED、LEDGER_BEFORE、STATUS_BEFORE。

交易只短暂暂停已核验 supervisor 在 clock_nanosleep 中的记账循环，更新后恢复；PPO trainer1253458未停止，检查点、optimizer、std、physics、奖励、课程未重置。只读的 /proc/syscall 需要 sudo 授权；账本写入仍由 egde 完成，未改成 root 所有者。凭据只经SSH stdin提供，不保存到脚本、文档或包里。

原首档45分钟试训验收截止仍为2026-10-02 15:48:34北京时间；新增20小时用于后续，不延长首验收窗口。当前 supervisor 的本阶段 status 中总预算/deadline可能保留启动时缓存；canonical 为唯一授权来源，Rich界面已经直接读 canonical 总额和剩余。下一次 training() 将动态读180000秒和剩余预算，更新 status 与 trainer截止；无需重启当前PPO或重复一次性handover。

连续计算预计10月3日19:08左右用完，冻结回放暂停时间不计PPO，因此后续实际墙钟截止可能后移。已计时间保持，停机仍不能算训练。首档仍遵循保存→flat与spin评测→安全续训；多种子自转达标后继续用户已授权的定向平移/启停反向/地形课程，不永久叠同一纯自转阶段。

apply_extension.py 已成功应用，本次不要再执行。其重复调用会核对相同ID并拒绝重复加时；已有 receipt 不能当作下一次用户授权。supervise_spin.py 的 main 是一次性接管入口；其最初 verify_sources 的108000断言是历史部署校验，不能用它盲重跑新预算会话。恢复必须先核对实际进程、active_segment、最新完整权重并结算上次真实运行，再使用安全恢复入口和 budget_authority.validate_budget() 校验两条已登记扩展。

自动巡检继续每两小时，健康无实质变化安静。总有效预算用完时完整保存、终验、停止并删除自动化；不得以暂停评测或后续课程为由自动追加。
