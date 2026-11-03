# 当前接续：起立首案真实失败已封存；V2零步与隔离目标首次编译并行

本文件为当前最新状态。基础/完整旧路径见[两主交付handoff](<CONTINUATION_STARTUP_DEPLOY_V1.md>)、[当前进度报告](<reports/STARTUP_DEPLOY_PROGRESS_20261103_V1.md>)。不要重答23:27用户“进度如何”：父23:28已明确源工程交付、起立失败/13m前冲与后续方向，并present了新报告；C源码ZIP也已present。

## 约束/goal
cwd F:/RMPOLAR-RL，task ROOT=此目录。原goal goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d最近实际get revision15/roundsStarted8/max12 active/armed，不重建/resume/complete/blocked。用户“这两个事都当个事办”仍是当前两个主优先：真实摊卧启动起立＋真实旧机代码接入；动量/R64未执行旁支暂停。
Python C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe -B/BLAS-OMP-MKL1/最多4PHYCPU，无GPU/SSH/PPO/canonical/专家tree/index/新agent/Mnemon写。当前无parent running PHY。dangerfullaccess/approvaldisabled，不escalate。仅复用C abf2088f-af10-479a-9108-202785031447、model e4e6c8f2-f08d-4df1-9150-945c804e8c2a；忽略Mnemon idlechildren。Office/ACL无robotics匹配，文件/CLI。旧H1/H2/H4/H5/Stage1/全部旧代码/gain/模型/成绩冻结；不重旧physics/QA/大raw只为档案hash。

## 首个实际受控startup
- [V2 runner](<run_startup_stand_case_v2.py>) SHA f774b28a2fa1559ff915f199a06bcf9ed64910d1caaa785394aabc1a5ec0109b，只改未执行V1的4处private支持语义/日志。support=连续末3s每个2k样本两轮>1N、guide/hard<=1N；pose/q/rate仍100Hz，不证between-sample连续。
- [冻结配置/协议](<STARTUP_STAND_V1/front_admission001/PROTOCOL.json>)、20source index、实际[独立review002](<STARTUP_STAND_V1/front_admission001/FINAL_ENTRY_REVIEW_002.json>) SHA7c2ac56f12d3a146388f7de21e94e66321f5a73de95f0512530aae5917d8399b、parentapproval齐备后只执行front065 nominal seed0一案。无背倾/侧卧/DR/teacher/assist，初始q37/v36只设置一次，不用old upright plant.reset。
- job pwsh-1640986e118b404e已collect exit1。原[ERROR](<results/startup_front065_nominal_v1/ERROR.json>)实际601ctrl/12020phys/29.616s wall，trace2741033B SHA2a48ca65a3bf0ca4c7c63ade5547efb8d744ce2d8514402420d603c369711e38，physics68899251B SHAb605956dd21f545ee0e32d983e8238395aadd0c3dc4f866829e4dd169a9285c1，均producer匹配。计划1000/20000不当实际完成。
- OBSERVE31frames→.31SHAPE→2.31VERIFY→6.00INHIBIT `startup timeout6s`，从未BLEND/BALANCE。不是已ready而handoff代码漏了。3/4/5s估计pitch~.672/.698/.674、qerror~.096/.111/.101均超原.15/.04；轮请求两轴正rail，腿请求峰17–19Nm未到40。
- 6.01 POST truepitch.633385852/rootZ.277183204；6.00 PRE x13.195024666，较初始约13.16m前冲。不是站稳或仅轻微误差。请求不是独立驱动反馈/唯一因果证明；100Hz日志不能补2k姿态/接触身份。
- 后处理另错dr.runtime_receipt不存在：真实FullDR在../traditional_control_20261101/dr_components.py343的queue_receipt。保原ERROR/无result，不回填伪result或0/1完整率。已静态生成[report-only新runnerV3](<run_startup_stand_case_v3.py>) SHA740f8d583b3cf5212e25a71fdcf4fbcbe99944fa59d1abb2d8028385cccaefe8，[receipt](<STARTUP_STAND_V1/reporting_fix003/RECEIPT.json>)证明循环AST不变、0replay/QA/PHY。
- [child诊断REPORT](<STARTUP_FRONT_CAUSAL_001/REPORT.md>)24行 SHA29b1e2ef3cf2c59a503896645e766bc7603ba12072b20b79236b29eb4826779c；EVENTS95102B SHAb10c629c026cc029fe090ea1e7a44d056d9ef2bf467ed0b9bc5789acfdccecbb，note7行。child一次601行/physics0；父为即时回复用户额外read第601行1次1行，必须单列，不能说全局只有1open。0raw-open行政KeyError失败版本保留；随后最小数值先落MINIMUM_OBSERVED，无数值丢失。不再读这些raw。

## model当前新委托：Startup V2（尚无新物理）
[父锁METHOD](<STARTUP_STAND_V2/METHOD.md>)已写并发给原model child，重新catalog-first。独立subclass/默认featureFalse精确delegate。
仅SHAPE/VERIFY：已有ctrl.K的腿行反馈，局部copied error清distance/yaw/vx/yawrate(0,1,7,8)，pitch/rate乘原quintic scale；scale*ff-Kleg@err＋原roll20/2±8，不能并联额外60/3/120/4 PD。轮用同packet encoder -0.30*wheel_vel2、±2Nm阻尼；旧phase/observer/qref/ready/timeouts/全轴限幅不变。实发log/last_tau更新，原BLEND捕获此last_tau，不在BLEND/BALANCE覆盖。无teacher/contactpermission/速度硬界证明，线性模型域外只是新假说。
先<=420enabled100Hz synthetic/<=40disabled/<=12typed新零步、0模型/FK/旧499/PHY/Git/agent；从report-fixedV3派生新entry，core/receipt给父后等新物理审批。此时未收到实现/单元结果，禁止自动跑case或重旧ID。

## 真实旧机代码接入：第一交付已封存/present
- [stage1ZIP](<MOD4_DEPLOYMENT_PORT_V1/mod4_deployment_port_stage1.zip>)5900131B/456entry，SHA58ad988be5dcb53d0079d20bd6bff4852f079629a37fcfe9d33724631320fb8b。427derived=423继承中2窄patch＋4新文件，其余421原bytes；原165+新4=169成员齐。40host/0，非fulltarget/CAN/刷写。父已readREADME/VALIDATION/RECEIPT/NEXT_PLAN/headers+完整patch178行。默认unbound无provider/arm，typed motor-qref、enable-only/ACK/RUN/STOP/DISABLE，旧轮不是MOD4DM。
- [V2静态准备REPORT](<MOD4_DEPLOYMENT_BUILD_PREP_V2/REPORT.md>)59行6812B SHA2d52f00b1a0f0f188c2461a6bfbdc516c2fe4432fa3e0522af80664d9fce9bba；RECEIPT b3ab2cc6...。14工具命令0，ARMCC路径实际5.06u6.750而非声明u4.422；DFP2.17.1存在，CMSIS5.8默认已知路径未见，project本地CMSIS宏5.1/RTE CORE5.5声明。34include33目录存在，protocol缺目录active需求未知。AHRS1对象/DSP272中2代表静态VFP/wchar/enum线索，不叫全库ABI相容；denormal语义差别/FPSCR未知。

## C当前新委托：V3隔离compile-only（未收到实际编译结果）
已明确写并发[PARENT_COMPILE_SCOPE](<MOD4_DEPLOYMENT_TARGET_COMPILE_V3/PARENT_COMPILE_SCOPE.json>)。parent已read59行V2；显式选现有u6.750新variant，不改封存pCCUsed，不假称u4精确复现。不安装/生成RTE/造stub，只用真实existing include；必需输入或group/file继承解释不明确则0compile停报。
C23:45回小plan：解析169members/每TU有效flags/字面argv先冻结，已知armasm同bin一次vsn；再至多162C+1ASM每TU仅首次编译一次、首实际error即止、保存成功prefix/failed/unstarted；直用受信工具不UV/hook/bat/flash，freshV3objects/log/deps。0link；全部compile过后仍须另审ABI/符号再批准link。不得降diag/删music/换库以拼成功，不重40/423源hash/旧QA/PHY/Git/新agent。stage1/V2只读。

新两条工作与报告均PH10pending；PH9已真实7b7d2633.../tagphase9，不重复record/push。等两个child新结果，不查旧失败/raw或恢复被暂停R64。整体Goalactive，尚无真实起立或已刷MOD4固件资格。
