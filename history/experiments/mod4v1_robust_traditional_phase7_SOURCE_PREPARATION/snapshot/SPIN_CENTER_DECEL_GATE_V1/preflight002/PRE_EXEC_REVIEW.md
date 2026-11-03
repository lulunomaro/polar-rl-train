# R61独立静态pre-exec review

PASS / ready_for_physics=true；issues=[]。

- defaultFalse exactdelegate到旧Legacy。enabled只将active predicate拆为原请求active或alreadyactive+operatorYaw==0+低forward+previous shaper finite nonzero；不传fake yaw、不自动开启从未active的centering。
- previous shaper到0才释放，可晚于current shaper一tick，不是measured spin/contact。kt20/cap1.8/lead/半径/K/gyroobservergain0/无capture切换不改；no-side-slip/odom误差仍原假设。
- 实际run_spin_decel_gate入口锁spin+sensors；packet→estimate→command之后才privategrade；原apply_torque_request AST同。StreamedRows先strictserialize/写/hash再memory；异常只原traceback+已写prefix/hash/controls/physicalcallbacks，不再serialize坏row。result gates和transition return显式bool，原门槛保留。
- launcher读取旧R26三个TRAIN配置，只case_id+centerflag；nominal=True/seed0、DR201/202、26s、obsaccel0、正反4pi/stop时段未改。首PHY前FROZEN_PLAN锁3configs/所有source/templates/review/launcherSHA；新输出专名，软件失败raise不继续。nominal完成且无health/software才准入两fixedpairedTRAIN，composite即便失败仍记失败、不是准入前提。
- 原preflight00224657/0，disabled2600完整math/state位等价、enabled首1000、shaper2600相同；420retainedtick为synthetic10..12.09/22..24.09。review未运行这些unit/boot/model；actualclock边界及gate以运行flags日志为准，不新增integerphase修复或额外数值门槛。
- firstprepare001生成缩进错误/0step原证据保留，retry02 AST导出成功不改控制law。无H2holdout/H5/asset/raw读取、无PHY/compile/Git/newagent；源/冻结RESULT未改。仅新TRAIN执行入口审查，不预测改善/技能通过或board/WCET。
