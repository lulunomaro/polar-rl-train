# 当前接续：两条主交付——摊卧启动起立＋实际老机工程接入

## 用户新优先项与目标

用户21:22要求“机器人在地上摊着，启动后能站立起来，这个也需要调”；21:25提供实际上过旧轮腿的不成熟工程，21:27明确“这两个事都当个事办”。父已实际edit原Goal，id `goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d` **revision15/roundsStarted8/max12 active/armed**，保留全部原LQR/MPC/fullDR/270/实机与Git目标，同时优先这两个交付。不要重建goal、用直立reset冒起立或提前complete/blocked。

cwd F:/RMPOLAR-RL；Python C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe -B/BLAS-OMP-MKL1/最多4物理CPU，无GPU/SSH/PPO/canonical/专家tree/index/新agent/Mnemon写。dangerfullaccess/approvaldisabled，不escalate。只复用C abf2088f-af10-479a-9108-202785031447与model e4e6c8f2-f08d-4df1-9150-945c804e8c2a。Office/ACL不匹配本轮控制/源码任务，文件与CLI。用户问实机代码已明确回答：有可移植C9核心/host与M4M7 partial，不是已刷可用整机固件；当时present了已有source bundle；新提供真实工程后不是从零缺BSP，而是复用并适配。

## 真实旧部署包的已读与提取

用户明确路径 C:/Users/lulu/Documents/xwechat_files/wxid_yut919v6wi5a22_9afc/msg/file/2026-08/StandardRobotpp-balance1(3).zip，76,134,913B、1184entries。[中央目录](<DEPLOYED_BASELINE_AUDIT_V1/CENTRAL_DIRECTORY.json>)与[受限提取script](<DEPLOYED_BASELINE_AUDIT_V1/extract_selected_sources.py>)已完成一次：391text/7,724,844 original bytes，单file1MiB/total16MiB上限，逐member CRC/rawSHA/编码/UTF8SHA记录于[manifest](<DEPLOYED_BASELINE_AUDIT_V1/SELECTED_SOURCE_MANIFEST.json>) SHA33a79a69e5ebd1be437b05c75de378359d969f63d0761aa9303e79ce2a47a98d。source_original保存原bytes，source保存可读UTF8/原换行；没有wholeZIPhash/执行ZIP程序/脚本/build/flash；不读.git/config/hooks/objects，不扫微信其他目录。music/build/bin等跳过，不等完整build闭包。

源码根 DEPLOYED_BASELINE_AUDIT_V1/source/StandardRobotpp-balance1/。父已实际read README135行/robot_param89行/部分extras.c：真实选balanced_infantry，而非凭函数名猜。

### C板级审计已封存，父read55行REPORT

[REPORT](<OLD_DEPLOYED_BOARD_AUDIT_V1/REPORT.md>) SHA916cc700499fb2a40f4f9fcbbc3138e8fa59c9fcd8a28887f6301ef8ed329ef4，[12项绑定表](<OLD_DEPLOYED_BOARD_AUDIT_V1/CANDIDATE_BINDINGS.json>) SHA174bfc53b9691ab413b80dceecbf161850025dcf17a4f0f3d8575b22489cf342；42重点文件匹配manifest，0构建/硬件IO/模型/PHY。实际STM32F407IGHx/M4，HAL HSE12MHz→168MHz，Keil CLOCK25MHz字段不当实测；FreeRTOS1kHz tick，chassis执行后delay2tick非严格2ms。

四DM8009关节CAN1 PD0/PD1/1Mbps、命令ID1..4→FB0x51..54、MIT；轮实际MF9025/LK CAN2 PB5/PB6/1Mbps、TX0x280、FB0x141/142，**不是MOD4 DM3519**。通用DM实际量化P±12.5rad/V±30rad/s/T±10Nm/Kp0..500/Kd0..5，normal joint限7Nm，不能把这个旧值当MOD4输出40Nm绑定。BMI088 gyro1k/accel800混合epoch、SPI-DMA-RTOS-AHRS，非仿真2k同窗包；epoch/seq/age/overrun缺。

实际缺陷：所有非OFF（含SAFE）state0会发FC；SAFE为零速阻尼+wheel stopPID，不是FD。offline10ms标志/DM fault nibble/IMU age未完整接停机；ScanOffline无selected caller。CAN发送poll20次后无条件AddTx，不查返回/ACK/TTL；SendJoint局部cnt未初始化。Error_Handler空/未证watchdog。只是source缺陷与候选配置，不宣称已观测实机故障或当前刷入image。

### model启动行为审计已封存，父read42行REPORT

[REPORT](<OLD_DEPLOYED_STARTUP_AUDIT_V1/REPORT.md>) SHAd92d0e67769276378219e18c7482f843c38d6a28f926ddc1e2b2e226341b69ed，[receipt](<OLD_DEPLOYED_STARTUP_AUDIT_V1/RECEIPT.json>) cf4ba48af4aaa71241b4e7ad6bafc3cf63905396f93beeb9088b31b8c60ea27f。真Keil/main→RTOS→chassis_task链已闭合；357tick启动delay、Observer/Exception/SetMode/Reference/Console/Send循环真实可达。STAND_UP枚举/target .18m/pi2有意图，但无正常mode setter/完成守卫；ConsoleStandUp local qref未初始化，产生它们的LegController调用已注释却仍读；wheel −220是Iq API值非Nm。CmdCali直接true/SetCali空，碰止点校准入口未闭合且速度比较非abs。不能搬旧参数/符号/6state K当新MOD4 state14。当前FSM_DETECTOR原recovery默认disabled/contextunbound，只产ref无地面执行器，不是开启flag就能起立。

## 父已执行的初态几何与自然落稳（不是受控起立）

[geometry001](<STARTUP_STAND_V1/geometry001/RESULT.json>)1model/2forward/0step：合法旧crouch仍双轮最低，不是躺姿；更深delta−.8/−1在旧operating envelope被挡，原错误完整保存，不松限/不重跑。[geometry002](<STARTUP_STAND_V1/geometry002/RESULT.json>)另1model/6forward/0step：保持合法crouch所有关节，初始wholebody pitch+.65/−.65/+1.25，用原全collision exact support一次放置至minZ=.001m，lowest为guide而非upright轮支撑。闭链约7e−13只是静态几何，不等自然落稳。

[passive settle](<STARTUP_STAND_V1/passive_settle001/BATCH_RESULT.json>)job pwsh-fa3e3d7882804c3c已collected exit0；1model compile、3data独立case、每案2s/4000step，总**12000新physical steps**；0controller/estimator/动力driver，ctrl精确0、气弹簧/重力/全部碰撞/闭链保留，初始后无qpos覆写/辅助。direct zero torque是模型禁能近似，不是已验证真实poweroff电路。三案complete，closure/mimic约1e−4以下、stationary tail≥.5s，均仍LYING_SETTLED_CANDIDATE，绝非站起成功。每2k raw producer SHA一次写入，不为归档重hash。

实际smallBATCH父已结构读：
- front_rest_065：pitch+.3836868287rad，root [.0317309,-.0000186,.2371387041]；qabs4=[.40797836065,.90000028595,.40798298142,.90000031384]；双轮+guide04/06支撑，静止tail.8525s。
- back_rest_065：pitch−.6510662677rad，root [−.1413946,.0001515,.2793471050]；qabs4=[−.50000016229,−.00799805807,−.50000011090,−.00794762327]；双轮+guide05/07支撑，静止tail.5315s。
- front_rest_125最终趋同front，pitch+.3836895012、rootZ.2371392，tail.5945；不冒三个独立姿态族。

气弹簧把delta自然伸到约+.492，初态**不是**原深蹲。软限位超出命令界约3e−7rad，测量不能偷偷改；新reference可按实际界投影并记差，不将合法自然软限位一律误判。后续controlled新trial可只在初始化使用这些保存final qpos/qvel；之后禁止扶正/抬root。最终成功需guide/底盘退出支撑、双轮承重并持续站稳，不能只看姿态或运行结束。

## 当前两原agent已转实际实现，待收产物

1. **model：STARTUP_STAND_V1/controller.py**，sensor-only(e14/IMU/enc/command)，不读truth/DR/model。公开Tall0 gain、默认off。OBSERVE有效静态proper .25s→锁实测q起点→quintic2s SHAPE_TO_STAND(PD60/3+warmFF、wheel仅旧GroundController两行、不叠legLQR)→VERIFY(.5s tilt<.15,qerr≤.04,qd≤.20,gyro≤.5)→BLEND .5s→BALANCE；6s timeout/坏包INHIBIT，实际接管再restore wheel/groundconstraint flags。先不支持侧卧/倒扣或|pitch|>1rad/roll>.25，单独报告包络。upright_prior=False仅有效静态proper初始化；首次badnorm fallback0不能假装姿态已正确。预锁≤500 synthetic command frames/≤20typed、0新模型/FK/PHY/旧QA后交父，禁止自动物理。父已补真实front/back限位姿态给unit，不能只测舒适crouch。**已收到新controller合成PASS但尚无受控起立成绩**：[controller](<STARTUP_STAND_V1/controller.py>) SHAe0f8105b32f69738b681a0d442da07e07021b22cbae7f1f993d33e1643aa7c52，499command/20typed、497frame-check/0，0geometry/model/FK/PHY/旧QA。front完整链是人为解析tracking，back27帧只锁点，均非物理成功。父已实际read全308行相关代码。[新runner](<run_startup_stand_case_v1.py>)已写但未执行，独立delta审查已发model；计划只front065 newnominal10s1000ctrl20000step，初始一次加载已落稳qpos/qvel，est.upright_priorFalse，原sensor/driver20步不改；private成功要BALANCE后末3s实际双轮承重/guide+hard退出/tilt<.10/低速/腿收敛/rootZ>=.30/高度增加>=.05/xy<=.5。不把elapsed/源码编译当站起。先freeze+review+approval，不自动跑DR或其他姿态。
2. **C：MOD4_DEPLOYMENT_PORT_V1**，真实派生工程实施，原selected/ZIP/oldcore不改。先parse Keil165members/库/include/startup/build闭包，缺选exact成员让父补(尤其AHRS/CMSIS lib/music)，不执行旧build/bat/postbuild/flash。可从source_original复制新project，保存before/hash/patch；修cnt未初始化、STAND_UP未初始化ref、显式arm/feedback/fault/stop绑定与默认不自动FC；STOP/DISABLE分开，旧MF轮不是DM后端。最小C99 adapter+hostsynthetic≤40check可做，无真实CAN/完整targetbuild/刷写/PHY/新gain，完整build待父审依赖另批。**现已实际收到并审读封存派生工程**：父read README32/VALIDATION34/RECEIPT78/NEXT_PLAN10、两header80与完整patch178行。实体[源码ZIP](<MOD4_DEPLOYMENT_PORT_V1/mod4_deployment_port_stage1.zip>) 5,900,131B/456entry、SHA58ad988be5dcb53d0079d20bd6bff4852f079629a37fcfe9d33724631320fb8b；[最终闭包](<MOD4_DEPLOYMENT_PORT_V1/BUILD_CLOSURE_FINAL.json>) SHA7a2d081ad9754791b6912b10d0f1949a64a3d76aebda13feb62a1934099570ca。423继承payload核不改、derived427files(仅2继承窄patch+4newC/h)，原165+新4=169齐、421其余原bytes一致，可逆patch；6Windows alias/368lexical节点不是实际条件预处理。cnt/static初始化、STAND_UP明确raw-motor qref、Console与emit门、默认unbound/不自动FC、STOP/DISABLE独立、target/output改名与autoFlash关闭已落文件。完整target编译/link/ARM/CPP/库ABI/真实CAN-SPI/刷写仍0，不宣称可上车。C stage1只读，父已另委托MOD4_DEPLOYMENT_BUILD_PREP_V2仅窄工具version/Pack与opaque库静态ABI计划，不批targetbuild，不重跑40/旧QA。 新code/mod4_port_gate/bridge默认unbound、manualarm、6轴fresh/enabled ACK才RUN，ENABLE_ONLY/STOP/DISABLE独立，非CAN硬件执行。C已原bytes复制391到新派生树、Keil165中17active未选依赖已精确请求；父已一次补选32files(17+必要music.h)/13,506,260B用于真实build闭包：[manifest](<DEPLOYED_BASELINE_AUDIT_V1/build_supplement001/MANIFEST.json>) SHA524b8dd11524fece9ac7faf5f9bd842e4d06e9f020d76f64ea47378e26bdcc7c。含AHRS.lib34756B与DSP13,294,064B，opaque未执行，CRC/rawSHA实际生成，非wholeZIPhash。cmsis_os.c是cp1252导致首次未选；原bytes和可读转码均保。已允许C仅补入独立派生工程以闭合165target，不批完整targetbuild/flash。

## 暂缓的动量工作、Git和背景

用户新任务前的momentum method/collector只封存零步组件；[方法](<TAKEOFF_MOMENTUM_CAPTURE_METHOD_V1/REPORT.md>)39行、nonconst两H API只用scratch、wholeCOM/worldH/完整contact pure torque与unknown；[collector](<MOMENTUM_PRIVATE_COLLECTOR_V1/REPORT.md>)38行，23interface+25pure/0，1boot/1forward、1scratchkin/comPos/A及2cross、0step/RNE/control。ring/events.py与R64两个draft**未测试/未接episode/未运行**；用户新优先后停止进一步R64。不要消耗原budget或冒新物理证书。

PH9正式已完成，父read[receipt](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase10_PENDING/ARCHIVE_PHASE9_RECEIPT.json>)170行：commit/remotepeel7b7d2633a25dad356809a56ddfa2d546f1cded10，parent662204600bf79ace36815db569a5d02f3b327981，tagtrial-20261103-mod4v1-robust-traditional-phase9/object47e9af16274fbf83ebc662c4134414968c2a6600。306全A=298SOURCE+7cover+1record，rec.main一次、原helperb2fd15...不改，手动atomic非force只ownbranch+新tag，PH1–8不动；main8654c630...仅相邻窗口，非全程无并发。后receipt PH10_PENDING不在PH9tree，旧pending5..9不stage/delete；不得重record/push。新真实部署包审读、startup初始化/新代码等PH10待稳定cutoff。

旧H1/H2/H4/H5/Stage1与R63失败原样。R63nom2/2、所选四TRAIN1/4 vsold2/4，默认off；.2748m单轮mesh峰不是270阶毕业。首个controlled startup已经执行，见[ERROR](<results/startup_front065_nominal_v1/ERROR.json>)与[batch](<batches/startup_front065_nominal1/BATCH_RESULT.json>)：job pwsh-1640986e118b404e已collect exit1；实际601ctrl/12020step，2.74MB control与68.9MBphysics prefix均producerSHA+error_receipt再次一致。控制在6.01s前停止后，父runner末报告错调用不存在dr.runtime_receipt()（真正API在traditional_control_20261101/dr_components.py:343为queue_receipt），因此无result.json，**不冒完整机器人0/1通过率/不重旧case**。原V1未执行，V2强支持语义every20subrows>1N/非轮<=1由review002+独立父approval锁；20source+one front seed0，reviewSHA7c2ac56f...。report-only新[runnerV3](<run_startup_stand_case_v3.py>) SHA740f8d583b3cf5212e25a71fdcf4fbcbe99944fa59d1abb2d8028385cccaefe8与[fix receipt](<STARTUP_STAND_V1/reporting_fix003/RECEIPT.json>)仅改一个方法名，循环AST同、0replay/QA/PHY，不回填伪result。model已新委托STARTUP_FRONT_CAUSAL_001，仅新601-row control一次+small ERROR诊断真实phase/故障，不读68MB物理/旧QA/挑gain；结果待收。C已封存派生工程并新做BUILD_PREP_V2：实际四ARMCC工具版本都是5.06u6 build750，不是project5.06u4 build422，已保存版本argv/日志；仅静态include/Pack/libABI，不编译/link/flash。当前无running PHY，两agent分析中，整体Goal active，尚无已通过受控起立或真实部署资格。
