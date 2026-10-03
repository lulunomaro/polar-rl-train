用户2026-10-03明确要求“预算再加20小时”。在原唯一canonical账本一次性追加72000秒，唯一扩展ID USER_ADD20H_20261003_3RD。原36000秒加三次已登记72000秒，总252000秒（70小时）；不建立第二份预算，不重置已用时间，不重复旧扩展。

问题：原在线supervise_autonomy.py有180000秒固定校验及固定status标签，直接扩展账本会使后续验收失败。修复仅涉及status/verify/training的预算读取及运行版本标识：用既有budget_authority校验登记授权，动态显示总额。其他函数AST、物理/奖励/PPO/DR策略保持；历史handover预算证据不改写。新控制器SHA 8fbc1bd395d677096d02866dd5ee7224a95cbadf2e34962c1bb5a5182212eb9c。

在核实实际PID/cwd/cmdline/start_ticks后，关闭旧父后续启动权限，按真实trainer对应run目录STOP_AFTER_SAVE完整保存model15875并正常退出。源SHA f1619a7571c8edfceeb5d4be9f4511ac014d027e8e558206c197046ecd7c194a，CPU actor/critic/optimizer/std/iter共68浮点张量有限。权重、优化器、std、iteration保留；保存退出尾段仅结算一次154.972393秒，退出检测至多0.25秒不确定性明示。结算后charged=155401.960700秒、剩余=96598.039300秒（约26小时50分），排错/迁移停机不计PPO。

旧监督器和guardian已经退役。新监督器2490960/start_ticks17250655、guardian2490993/start_ticks17250722独立会话运行，--resume从完整15875进入既有冻结站跑/自转验收；此验证时没有PPO trainer且active_segment为空是计划内评测。status实际budget_seconds和authorized_training_seconds均252000，autonomy_version=sleep_v3_budget_dynamic。三项扩展各仅一条，103源哈希全部匹配，近期活动日志未见所查运行错误。原Rich1551130按canonical读取新预算，未另开窗口。

当前4rad/s、white_v2不变；6rad/s此前连续三失败的rate_rejected=[6.0]保留，不借预算扩展重试失败档、放宽门槛或增加硬件上限。本记录只证明预算扩展与监督器兼容交接，不证明120rpm、世界0.5m/s自转净进度、Rough、云台或实车认证完成。每两小时巡检和健康无实质变化安静保持，到总有效预算耗尽完整保存/终验/停止，禁止自动追加。

验证：动态授权接受登记70小时，拒绝重复扩展/未登记总額/负charged；函数AST差异仅预算三处；实际CPU完整保存、正常退出证据、唯一账本三扩展、源指纹、单一新监督器及实际252000状态回读。原报告与被拒绝权重全部保留；权重只索引不上传Git。
