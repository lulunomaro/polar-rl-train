# 用户明确追加20小时：使用同一账本，总有效预算30小时

用户在当前线程明确说“预算再增加20小时”。新增授权72000秒，原授权36000秒，
合计108000秒有效PPO进程时间。已计时间保留，停机和无训练的独立冻结评测不计。
这不是从现在重新开始30小时，也不是另外复制一份20小时账本。

唯一canonical账本路径继续使用原文件名：
`/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json`。
文件名历史含10H，实际读取authorized_training_seconds和budget_extensions。
本次唯一扩展ID：`USER_ADD20H_20261001_2341`，不得重复应用同一扩展。

生产目录不变：`/home/egde/rl_candidates/MOD4_mild_dr_trial_20261001`。
扩展请求先登记在reports/USER_ADD20H_20261001_2341_REQUEST.json。
实际提交、完整保存检查点、已计时间和原PID证据在同目录的_APPLIED.json。
另有BUDGET_BEFORE_ADD20H/STATUS_BEFORE_ADD20H/PROCESSES_BEFORE_ADD20H备份。

原监督器内存把36000写死，原训练进程环境也固定了旧deadline，因此必须在
完整保存边界接管一次；仅改JSON会让旧监督器校验报错或在旧时限退出。
apply_budget_extension20h.py只暂停已核实的旧监督器，原trainer继续到保存边界，
保存actor/critic/optimizer/std/iter后正常退出。核对latest_complete和退出日志，
结清同一active_segment，关闭旧父进程的启动/记账权限，再一次性提交108000秒。
已完成注册不等于已应用，要读_APPLIED和实际进程；交易进度在
reports/BUDGET_EXTENSION20H_PROGRESS.json，交易日志apply_budget_extension20h_20261001.log。

新监督器入口：`isaac/mod4/supervise_budget30h.py`，日志
`supervisor_budget30h_20261001.log`。动态记账通过budget_authority.py核对原授权加
明确的扩展历史，重复ID/未登记总额/待处理扩展/负已计时间测试均拒绝。
prepare_budget_runtime.py只更新监督记账，不改变训练物理、奖励、电机、弹簧或PPO。
源差异在reports/BUDGET_RUNTIME_PREPARED_20261001.json，旧监督源码备份保留。

新训练仍20k×24、solver16/4、原生Plane、MOD4详细USD、root目标.25m、
速度±1.5m/s、10%站立、yaw0、white_v1轻DR、KEEP_STD1、接触积分和5ms采样。
从交接处最新完整检查点继续，不从零、不重置std，不重复旧初始预检。
新status.budget_seconds=108000供已经打开的Rich终端实时读取，无需新开重复窗口。

每半小时首次、之后每小时已有80env×15秒确定性回放；每小时线程巡检仍保留。
接下来自主完成Rough v1的真实地面/完整闭链复位/状态机/指令/观察映射和隔离验收，
通过再保存切换；参考MOD4_AUTO_PROGRESS_NEXT_AI_20261001/ROUGH_NEXT_TASKS_20261001.md。
20小时追加不是立即打开未经验证地形或300–700N弹簧DR的理由。
旧窗口和积分统计、真实卸载/间隙/滑移/正确力矩诊断继续并列。

突然重启先确认实际进程已退出，对canonical.active_segment按最后健康/日志/
完整保存/shutdown上界记账，保留charged及扩展记录；不能重复应用20小时交易。
新的supervise_budget30h.py可在账本已对清、无trainer且当前owner仍为本root时恢复。
其他科目接管后owner_root改变，就使用新科目的监督器，不能盲启动旧flat任务。
预算耗尽后完整保存、名义/轻DR终验、更新终端、如实报告并停用自动化。
