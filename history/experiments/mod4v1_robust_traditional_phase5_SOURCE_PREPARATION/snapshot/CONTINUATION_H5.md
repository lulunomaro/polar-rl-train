# H5独立验证完成 — 40/64，目标继续

本文件是当前主接续；旧模型、约束与R40–47完整背景见[接续R47](<CONTINUATION_R47.md>)，更早证据沿其链接读取。不要把TRAIN4/4或64条complete当鲁棒毕业。

## 目标与执行约束

- 原独立传统LQR/MPC最终保底Goal仍active/armed：goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d，最近revision7、roundsStarted4/max12；未complete/blocked。正确SPR参考、持续4πrad/s、完整D0–D7及DJI C板/达妙板两路径不变。
- cwd F:/RMPOLAR-RL；本任务根是本文件目录。Python C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe，-B，BLAS/OMP/MKL各1，最多4物理CPU进程。无GPU/SSH/PPO/canonical/专家worktree/index写入。
- Office/ACL技能无robotics匹配，使用文件/CLI；先read再edit/glob/grep；危险全访问但审批关闭，不带提权字段。保留失败与prefix，不为补档重跑已消费轨迹或重hash大raw/资产。无需Mnemon写入。
- 只复用两个agent：C/math abf2088f-af10-479a-9108-202785031447；model/archive e4e6c8f2-f08d-4df1-9150-945c804e8c2a。忽略其他闲置Mnemon子任务，不新建agent。

## H5真正结果，冻结未回调

已读[完整报告](<reports/H5_MINIHOP_L20_INDEPENDENT_FACTS.md>)；[JSON](<reports/H5_MINIHOP_L20_INDEPENDENT_FACTS.json>)包含64行及128份producer raw元数据；[完成回执](<MINIHOP_L20_H5_V1/COMPLETION_RECEIPT.json>)SHA e857f60b05bafc34519f269989bfe37629b72535ae082bafa3438dbdd04978c1。

- 新62100..62163，64/64执行且完整结束，0软件错误/0未启动。38400控制采样/768000物理步。父job pwsh-7b1d1da9096548bf已exit0并collect；分析/封存命令也已exit0。没有父running job。不要再次launch此batch。
- 原门槛**40/64=62.5%**，24机器人失败。Wilson两侧95% [0.502503786840045,0.7333401982117536]，仅声明DR分布内描述，不是硬件或95%可靠度证明。
- 所有64达到原>=80mm净空门槛，实际peak两主轮最低mesh相对地面净空.1760827381..2669160844m；不是270mm台阶跨越。64无>1N hard环境接触采样；24有>1N guide采样，其中3同时endstable<2s，另外21仍按guide严格零原门槛判FAIL，未改标签。
- 末段稳定原门槛61/64；3个endstable0种子62137/62141/62149，guide ticks6001/6027/5984。全部失败保留，不补种/不重跑/不在H5上调参。
- D3=0分组23/28通过；10ms分组17/36。只是非配对全DR分组事实，不声称单变量延迟因果证明。D0-only nominal-mixture分支8/64，仍nominal=False且D1–D7开启，不剔除。
- peak pitch全队列最大.8089112904rad，机械正功率442.36..934.65W；机械值不是母线电功率，也没有硬件冲击/电热额定。
- operational air是all-positive环境normal汇总<=1N连续20ms；endstable是100Hz窗口，不是2k连续接触证书。控制仍原100Hz boxcar→D1→D3，未用raw2k增量信息。动作由operator timer，未接可信contact FSM或C闭环跳。

冻结[协议](<MINIHOP_L20_H5_V1/PROTOCOL.json>)SHA b2aac213f21abda333ec98c711bbec4c1db8577d16683639d632c8e2ae0d6d0b，[base](<MINIHOP_L20_H5_V1/FROZEN_BASE_CONFIG.json>)7165258f7dbf9f49e0d895fd9343e17d33628a3fbf3c863d7dc30e30f1dbf368，[41-source index](<MINIHOP_L20_H5_V1/CONTROLLER_SOURCE_INDEX.json>)a184b92a9fe20049a4c0bafb07e5fdf4a83534a837d54cd897f8f23a4bd18a9e均未变；完成后41小文件SHA再次全同。128 raw共3,393,408,311bytes仅producer元数据，本轮汇总/归档未重开重hash；运行时原279资产guard校验仍执行，不与仅归档hash混淆。

## 统计审查修复不是候选调参

[执行前审查](<MINIHOP_L20_H5_V1/PRE_EXEC_REVIEW.json>)PASS，父read后才写[仿真放行记录](<MINIHOP_L20_H5_V1/PARENT_LAUNCH_APPROVAL.json>)并启动。

独立[统计脚本审查](<MINIHOP_L20_H5_V1/STATISTICS_PRE_REVIEW.md>)发现2个软件中断分支表述缺口：无条件x/64、耗量漏软件prefix。执行统计之前父修正，仅完整队列用64分母；valid-result耗量与软件prefix known/unknown分列，不补配置步数。[原脚本副本](<MINIHOP_L20_H5_V1/statistics_corrections001/analyzer_before_review_fix.py>)和[修正回执](<MINIHOP_L20_H5_V1/statistics_corrections001/CORRECTION_RECEIPT.json>)保留。原gate/checks、passed/accepted/full及Wilson函数AST全同，H5未停止/重启。

当前[分析脚本](<analyze_h5_minihop_l20_v1.py>)SHA9d9a96afa7f3e7829e7f3495c9ab1758f94943ec55a1e291c34c58d325a32fc9，已运行一次成功产生报告。旧runner kind字符串含TRAIN是历史泛用标签，统计核对冻结cohort与精确base，不依据该字符串选样或选参。

## C模块进度和真实集成缺口

[Power C源码包](<SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_source_bundle.zip>)11,076bytes，SHA5b36782d316e616eb74a673ee5141078e22ed79f2393f1a98e27b29a96176002，CRC已核对，5个成员：C/H、BUILD、MODEL_CONTRACT、NUMERICAL_BUDGET。它是独立新数学模块，不在阶段V1 ZIP里。219固定数值例、38508检查0fail、native2290/0及C++pass；M4/M7对象编译非运行。cal/thermal/electrical/driver-rate域默认UNBOUND→invalid，未接任何H5/机器人功率链，不能据此宣称电功率受限或目标板通过。详细[模块说明](<SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/README.md>)。

[有界接口报告](<CONTROL_CHAIN_SEAM_AUDIT_V1/REPORT.md>)84行、7实际源文件、53源码行链接；源报告SHA663d4997492cff2b1c31449e495be7a7399ba5f62990097dc56c23b83e412b4f。明确断点：C3 cycle内部enqueue且缺完整候选bundle；FSM输出不是自动发送许可；NM valid数学fallback可与clock fault/deadline并存；driver preview状态隔离、Power后F32/CAN/tracking enclosure再认证、warm/last_u实际held事务及唯一最终sender均尚缺。

C agent现实施**PC3_CANDIDATE_BUNDLE_V1最小非驱动候选服务**（新目录、未seal，暂不入包/本次archive cutoff）：只公开estimator/P25/DC数学API，不调用cycle/enqueue、send_permission恒false，不接FSM/MPC/Power、不伪造operator enable。保留source/arrival/estimate/drive/mean aperture/seq及internal/effective shaper独立标签；available ns/checked us桥及freshness/clock/alias/fault保护；gyro为有aperture的mean，不冒充瞬时endpoint。计划新组件用旧3200固定fixture逐bit QA和有界故障测试，不重跑旧物理/SDK/blockedIO；新M4/M7仅对象。预算已先声明0bit差。不要把旧审查closing通知当新实现完成。

model agent执行前及统计短审查完成，无新physics；接下来可做PH5源码快照准备，但先看父书面cutoff，不自行扩到active candidate/未来物理或直接commit。

## 交付/Git/下一关

[阶段V1](<DELIVERY_STAGE1_20261102_V1/MOD4v1_Traditional_Stage1_20261102_V1.zip>)仍10,725,489bytes/SHA8b5bd15b3c26db510ee353b233597332b5899e81e5cec4ef723d265dabe01288，不改旧包。其7C核心/旧H4/H2等证据仍成立，H4前进64/64不等于直线资格，H2正向持转不等于停启换向。R42名义4cm通过、R43 DR1/8及6cm失败仍保持。

PH4已真实commit db8fd0606e00a450504853181a6b4cdf66869d68，tag trial-20261102-mod4v1-robust-traditional-phase4，object5aadabd68a83f1e4ef93dd2b18518128c46f87a9；只own branch/tag atomic，旧helper/PH1–3/专家index未改。[PH4 postcommit回执](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase5_PENDING/ARCHIVE_PHASE4_RECEIPT.json>)保留。PH4 cutoff<=R39，不含R40以后/Power/H5。本轮全PH5pending，不能重record PH4。历史1个FSM ERROR_REPORT版本缺口/15 raw未知不伪造、不为补档重hash。

后续重点仍为实际无真值估计/接触/FSM闭环、全caller与唯一发送/driver-rate功率合成、6cm/270mm/移动越障、spin stop/reverse与双板绑定/HIL/WCET。新控制策略只能在新TRAIN上开发，H5冻结结果保持独立，不拿24失败种子反复优化冒独立验证。目标尚未完成，勿标blocked（仍有实质软件/仿真工作）。
