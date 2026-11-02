# R45 Observer Causal v1 — paired TRAIN,0newphysics

**延长wheelKF/groundkinematics禁用窗口从legacy实际2.00延到2.14，没有改变torquephase/gravityschedule；四seed配对combined仍3/4。坏seed4222恢复窗改善且guide减轻，但guide仍发生，原联合gate保持失败。**

## 精确逐gate表（old R44→new R45）

|seed|peak fullair mesh clearance m|guide ticks|hard ticks|endstable s|combined原判定|
|---|---|---:|---:|---|---|
|4221|0.17767350539278032→0.17767350539278032|0→0|0→0|3.6299999999999666→3.649999999999966|True→True|
|4222|0.2574348525761971→0.2574348525761971|4727→31|0→0|0.0→2.149999999999998|False→False|
|4223|0.2509379737816319→0.2509379737816319|0→0|0→0|3.5999999999999672→3.5399999999999685|True→True|
|4224|0.21167165660998832→0.21167165660998832|0→0|0→0|3.799999999999963→3.789999999999963|True→True|

所有case complete600controls/12000physics，flat=True；mesh门槛>=.08、hard=0、guide=0、endstable>=2，保持浮点原值直接判断，不四舍五入成pass。完整每gatebool见[精确gates](<PAIRED_GATES_EXACT.json>)。R45seed4222endstable=2.149999999999998通过恢复2s，但guide31所以仍False；没有将旧R44未达恢复窗的失败改写成成功。

## 隔离intervention之前的严格比较

每seed command_time_s0..1.99共200条控制采样：estimated14/requested_tau6、公开loggedgyro/proper/q/qd/wheelrate、sensor时钟、gradebefore/after及其他共享字段，float经原JSONdecode为binary64后按structbytes比较，离散type/value精确相同；4case全通过，shape一致。新增phase/hop日志语义和wall耗时明确排除。[比较详情](<PRE2_CONTROL_EQUALITY.json>)同时列firstshared差异。**这不是4000个逐物理step的bit对比**，未读取其它seedphysics来冒这个结论。

全600条phase名称/targetq/qd/trigger时间schedule相等；legacyend不是精确1.99而是1.9900000000000002，所以真正变更是14个controlticks2.00..2.13，2.14双方都启用。原preflight001错误oracle及0023221/0由父保存，本分析未重跑。

## 4222实际接触与support

只有旧新4222physics流被本诊断读取，producerSHA原引用，不为归档重hash。首次落地stage均2.0459999999998506，righttire承载total约6878.180943995356N；不是根据target姿态或mainwheeloff推测。

旧guide>1N总4727ticks/2.3635s，新31ticks/0.0155s。first>1N旧2.304999999999937s、新2.3624999999999563s；新实际stagepitch/roll=[21.053244339835327, -0.0494045675829203]deg、rootpre=[-0.2490658130817518, -0.006816402606900144, 0.23379647587986857]m，guide=['guide_wheel_04', 'guide_wheel_06']，guide总5485.103715393405N/main=[0.0, 7.213694908996923]N。都是已保存私有grading，不是在线controlinput。

延后观测确实在此pairedseed减guide、提高末恢复时间，但没消除guide或改变3/4集合。新firstguide在2.14重新启用之后；这只是时序与配对干预证据，不是重新启用本身一定造成guide的反事实证明，也不支持“quarantine=接触判据”。需要父另行主动落地姿态新TRAIN动作来分离mechanism，本任务未实现/拟合。

落地之后worldsupport有间断：旧968个<=1N gaps，最长0.054s；新83个，最长0.024s。新worldsupport最长连续1.1s，bothmain最长0.501s。100Hzendstable gate不是2k逐点连续支撑，单0.5ms gap也不能被平滑抹除；全部runs见[小contactsummary](<BAD_SEED_4222_CONTACT_SUMMARY.json>)及[完整derived结果](<attempts/001/output/RESULT.json>)。

实际2kroot旋转/drive/rootprepost时间由已存stage给出；每腿实际2kq4未保存，明确unknown。附近100Hzencoder/target及symmetrictruth只作为bracket，未冒同时间实测腿姿；没有全mesh重建或虚构新接触/峰值。

## 范围与source

[scope](<SCOPE.md>)、[分析源码](<analyze_pairs.py>)、[执行前源码及保护SHA](<attempts/001/VALIDATION.json>)、[因果边界](<CAUSAL_BOUNDARIES.json>)、[INDEX](<INDEX.json>)。Source/result/config小文件SHA与原trace/physicsproducerSHA都在derivedRESULT；只8controltrace+2badseedphysics，没有其他轨迹/DR参数拟合、模型/旧文件/Git/新physics/agent/真实IO变化。全部PH5pending；整体Goal继续active。
