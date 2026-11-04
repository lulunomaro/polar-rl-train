# 当前九专家一次大评测：完成交接

本轮人类任务为只做一次各自原科目的冻结评测，不继续SuperMimic重构、训练或子代理工作。1亿token是上限而非消费目标。旧持续Goal已暂停；当前一次评测在直接人类请求下执行，未重新启动旧训练。

## 实际完成

- 新独立批次：`MOD4V1_CURRENT_NINE_FROZEN_ASSESSMENT_20261104_090739_1793754459497533800`。
- 一张4090，九模型各80环境。2026-11-04 09:13:31至09:29:10（UTC+8），共同真实控制窗口137.31秒。
- 九路完整原控制数全部完成；全部子进程RC0且实际wait，原父进程RC0且独立外层实际wait；私卡EX与finiteEX均已释放。未做第二次物理回放。
- 当前保留最佳模型：E0/C878/C113/S135为已选20-PPO后训练候选；E2/E3/W35/S50保留母本；H1原冻结版。模型、Registry与预算均未修改，新增训练更新0。
- 完整闭合日志没有发现所扫描的PhysX/CUDA/接触容量错误；W35本批543行及schema一次功能读取、哈希、解码，未截断或丢行。

## 结果入口

- [逐科目结果表](<F:/RMPOLAR-RL/mod4v1_current_nine_assessment_20261104/CURRENT_NINE_SUBJECT_COMPLETION_RESULTS.md>)
- [机器汇总](<F:/RMPOLAR-RL/mod4v1_current_nine_assessment_20261104/CURRENT_NINE_SUBJECT_COMPLETION_RESULTS.json>)
- [原终末和关闭等待汇总](<F:/RMPOLAR-RL/mod4v1_current_nine_assessment_20261104/reports/QUALIFIED_CLOSED_RESULT.json>)
- [W35原分组与日志检查](<F:/RMPOLAR-RL/mod4v1_current_nine_assessment_20261104/reports/W35_ORIGINAL_SPLIT_RESULT.json>)

S135上/下/站立27/27、27/27、26/26；C878为26/27、27/27、26/26；C113为22/27、27/27、26/26。E3恢复0/74，正常6不并入分母。H1准备64、起跳42、落台0、成功0，原窗口20s。E2原世界系整圈联合达界0/187，43个未完整周期另列。W35运动18/61、站立26/26，partial183/45另列。E0只报连续误差及0/80物理终止，S50只报原回放/终止事实：两者原完整二元规则仍缺失，不伪造通过率。单seed有限窗口的结果不等于完整专家毕业或RM70实场验证。

## 收集器订正，不涉及物理重跑

初版本地收集器错误地对四个E1 worker强制要求`WORKER_EVAL_STARTED`文件；原E1 worker本来不发布该文件。原父进程自己已经认定九路执行完成。初版false报告保留，未改写原生产者或伪造marker。

[订正记录](<F:/RMPOLAR-RL/mod4v1_current_nine_assessment_20261104/reports/COLLECTOR_START_MARKER_ERRATUM.json>)以同一缓存中的原group_barrier、完整actor/physics/feedback计数、实际控制时间、env/PRE_CLOSE、原父子wait及释放证据恢复四路正确执行状态；源模型、轨迹和原始终末均未重新读取来重评物理表现。

## 结束边界

一次大评测已完成。只合并归档本批结果、收集器订正和上一阶段之后新增的已有文字报告；不补训练、不重放旧once、不再开启Source审计分支。旧SuperMimic分支保持暂停，H1和所有母本保留。
