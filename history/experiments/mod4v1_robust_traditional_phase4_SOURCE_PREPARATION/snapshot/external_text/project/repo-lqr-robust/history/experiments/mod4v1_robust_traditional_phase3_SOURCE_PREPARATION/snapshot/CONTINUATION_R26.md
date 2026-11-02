# 接续R26 — 接触身份、实体RM派生地形与刹停换向验证

沿用[上段R16完整上下文](<CONTINUATION_R16.md>)。Goal`goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d`revision4 active/armed/max12，最近get仍roundsStarted0。不要新建/提前complete/blocked。主robotSHA`0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324`、.5ms物理/100Hz控制、31体/311geom/279mesh、轮总15.8、严格D0–D7与边界不变；仅独立新代码/scene，不改冻结源或另一RL会话，不用GPU/SSH/PPO/weights。技能仍Office/ACL不匹配本机器人任务。

## 仍有效的独立H1/H2成果（不要重复调参）

LQR P25独立H1 stand60/64、2m/sforward63/64；H2正4π综合56/64，而角速度/姿态连续约9秒64/64、实际约20圈。没有把角速度通过当完整通过；4漂移+4vRMS失败都留。GroundMPC16仅TRAIN，maxsolver5.05ms/169LQR回退，非MCU deadline资格。详见上段的报告与协议链接。

## R17–R20新增接触/跳阶证据

- R17新contactaudit桥准备时猜错空白(needle4spaces但原3)assert，0episode/0Step，原[PREP.log](<batches/r17_contact_identity4/PREP.log>)/生成器保留。新R18修，不重复旧ID。
- 新[contactauditV1](<physics_bridge_contact_audit_v1.py>)只在原每个mj_step之后read contactForce，actuation/DR/IMU原序不变；audit字段不给controller。stageTime=t−.0005，2kHz记录所有mainwheel/guide/hard-other与环境接触。R18四个instrumented诊断新目的，不是归档回放/独立成功率。
- R18证实0/101第一碰台是guide，201/203是mainwheel；nominal有2个physics tick hard-other碰撞，原100Hz只见1个nonwheel采样漏掉。峰接触瞬时可数千至数万N(未做结构/实机承载资格)。全表面真实离地约.3s，不把双主轮off直接叫全机air。新R19训练pushδ.34/.5/.65/.75与push.11/.13/.15，所有失败保留，未改物理/DC/导轮。
- [auditV2](<physics_bridge_contact_audit_v2.py>)增加真实contactpoint/normal、top/riser/edge诊断分类、每physics-stage真实mesh越沿及首触前air越沿；只grade不control。避免把step任意接触误叫top landing。老R13–R16标签不改，旧step-pair force计数没有原surface身份；final footprint稳定门槛仍保留。
- R20δ.65/push.13候选10DR：完整8/10、anymeshclear8/10、首触前干净airmeshclear5/10、结束稳定2s5/10、hardcollision-free5/10。多数firstcontact导轮顶面/立面，206mainwheel顶面但之后2hard ticks；不是clean-jump鲁棒毕业。对照R16δ.34/.11 7/10end2更强，δ.65仅nominal轮先落台改善，不冒全DR改进。
- 已有[汇总JSON](<reports/R18_R22_CONTACT_TERRAIN_FACTS.json>)，只是小result/batch聚合，没为归档重读raw；新raw producer边写SHA。原[静态候选诊断](<DATA_DIAGNOSTIC/JUMP_CONTACT_IDENTITY_V1/RESULT.json>)仍只是candidate不能顶替新runtime接触。

## 首个真正实体RM派生地形（范围清楚，不是假flat或全CAD）

父只读查E1冻结source：`mod4_task.attach_rmuc2026_terrain`依赖incoming/terrain_cfg.py/fullCADarena，workspace F:/RMPOLAR-RL glob未找到terrain_cfg.py/field_dims.json/STP/rmucUSD/ZIP；一次官方IsaacLabrawweb_fetch也只是fetchfailed，无数据。没有到其它个人目录找，没有启动Isaac/PPO，也没有把缺CAD伪装完整arena。

可用精确来源：E1冻结[e1_rough_recipe](<../mod4v1_experts_fulldr_rm70_20261101/E1_actual_qualification_v1/SLOPE135_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4/e1_rough_recipe.py>) + [resolvedrecipe](<../mod4v1_experts_fulldr_rm70_20261101/E1_actual_qualification_v1/SLOPE135_ACTUAL_TYPED_SOURCE_V1/runtime/isaac/mod4/ROUGH_V1_RESOLVED_RECIPE.json>) + pinnedcustomheight_field SHA`5f444236205f6ab4a56e0c76387b388d5d2d5a7a83ab63386f5cf15ae5b68d0e`/commitb8ff79f3df855faf9dc92f4a282bd80c42649466。

- 新[rm_grid_terrain_v1](<rm_grid_terrain_v1.py>)从hashchecked源AST只取8个purefunction(不SDK/import/decorator)，把trimesh.creation.box的size/translation记录成相同MuJoCo solidboxes。是上游11families中的`tiny_step`一个，不是整个CADarena/全11family，不声称PhysX runtime等价。
- 保留原9×9m、groundbox厚.05、bar_length_ratio.95、独立random count2..4且forceeven、width.05.. .2、完整height.02–.06(未用gentle1–2cm)。y只平移−4.5m；没有额外无限Plane填底。新模型桥原robotgeoms保持，只换worldterrain；轮D0friction priority/完整DR原样。9组0step几何QA：[GEOMETRY_QA](<RM_GRID_SCUT_V1/GEOMETRY_QA.json>)。
- [R21实际11轨](<batches/r21_rm_grid_train11/BATCH_RESULT.json>)：nominal2cm真实通行7.34785m、0nonwheel/过原screen+progress；4cm6.293m/8nonwheel未过；6cmnominal+8DR全部未过，卡第一/第二bar，进.89–2.64m，数千nonwheel ticks。所有complete≠路段通过；尾速很小是卡住/停止，不能叫跟踪好。
- [R22](<batches/r22_height_rough9/BATCH_RESULT.json>)用新nominalδ0/.2/.4更高腿姿+重新DARE bank，只reset一次后全靠电机，没有rootZassist；每姿态都2cm nominal过，4/6cm全未过，有health fall。说明仅抬腿高度/固定legPID不够，不再盲加。新[bank](<TALL_ROUGH_BANK_V1/INDEX.json>)0physicsSteps/新源，不改旧gain。
- 新几何源虽真实碰撞，不冒"真实RM全图已过"。下一需要namedcontact定位housing/guide/body blocker、sensor-only障碍处理/腿姿/可观测性。原scalarWheelKF共滑不独立可观，所以卡住时两轮一致也可报告假行进，必须如实处理、不可用worldposition反馈补。

## R23/R24/R25软件失败与R26当前运行

为覆盖用户刹停/换向，冻结P25/冻结H2只新增command schedule、无midrunreset/调参。目标：normal正/反2m/s持续后刹停；spin +4π9s→停3s→−4π9s→停4s，总26s；每个spin段连续yaw/pose≥5s、稳态mean±5%与vRMS.15，stop|v|<.15/|w|<.3维持.5s、3s内完成、spinendpointxy<.3；均proposed engineering非用户ratified/新TRAIN，不重新解释H1/H2。

- R23 prep猜4space的tau行而原3assert，0Step；R24修tau但多行metric注入indent错误，0Step。原两个PREP.log/源码都留。避免再猜，R25改[独立transitiongrader](<transition_grader_v1.py>)，2条synthetic正/反例过，schedule注入自动发现实际indent，AST后才跑。
- R25前4个forward0/201/202/203完整12s/24000steps各已消费，但postprocessing沿旧spin-only结果字段读取normalcontroller.center_log AttributeError，未输出result，旧handler也没保存rows。不能把它们叫机器人失败或补造分数，也不为补档重跑。原ERROR/counts/source/日志留在results对应r25目录和[SOFTWARE_ABORT](<batches/r25_transitions27/SOFTWARE_ABORT.json>)；其余23未启动。
- 新R26修getattr(center_log,{})并在静态API检查normal/spin剩余属性，futureERROR写partialtrace；不重复已消费forward0/201..203，forward改204..211八DR，reverse/spin仍未消费0/201..208各9，共26。源[run_transition_case_v3](<run_transition_case_v3.py>) / [launcher](<launch_r26_transitions_train.py>)。
- **当前父后台job `pwsh-66c19964e8dd45f5`仍需collect**，应先读结果，不另启动同批。上一jobR25`pwsh-3e0c14042fd54a90`/R24`pwsh-2af0dddf90cd401d`/R23`pwsh-0dc54e0ab7334fcf`已collected；R18/R19/R20/R21/R22也全部finished/collected。无其它相关父job未处理。

## 两个复用child当前状态

### abf2088f-af10-479a-9108-202785031447

旧五stageQP1/ODOM/真实H1/QP2fast/ARM_OBJECT_BUILD_V1全sealed，详见上段。当前新`SPR_AUDIT/portable_control_v3_current`：原V4estimator/P25实际K +explicitpacket/timing/dispatch固定C port已编码。纯Python64复放固定TRAIN R04_202/R11_k20_201与旧estimated14逐项差0；3200packet总对照C32对原state14max1.15092e−5、τmax2.00777e−4Nm，独立synthetic等预定budget0超限。扩故障6040assert0fail；原首maybe-uninitialized警告/partialobject/源留，未降warning。新三模块×M4/M7共6/6对象compile-only、C++externCsmoke过；还在最终README/index/221旧hash复核封存，不冒全port完成前实板可用。

明确只1+2估计/P25；H2 commonτ20反馈未移植，只FKvy诊断。100Hz已聚合coherentepoch packet不是通道瞬时同步或真实2kCAN。坏payload重复/过期/alias/mean权重/agefault硬return零valid0，queue invalidate/disable不假硬件已经执行。

封存后已安排新`HOST_CLOSED_LOOP_IO_V1`：长驻本机stdin/stdout typedversion/seq/count协议，Python64 subprocess连接MinGW32exe(不ctypes32DLL)，只P25/初始化一次，返回preDC数学τ与最终DCguardedτ两种明确字段，父新physics用而他不跑physics。无网络/CAN/BSP/硬件deadline。此新stage/postR16都PH3pending，PH2不扩范围。

### e4e6c8f2-f08d-4df1-9150-945c804e8c2a

[CONTACT_PROXY_NOMINAL_V1](<CONTACT_PROXY_NOMINAL_V1/README.md>)已sealed：runtimeSHA9e5316dd0ae8dab2da116b3e72a648b36e2b6b49239cf364da16d7b67ac46da6，constants14c38264...；32/32合成/代数单测、13PUBLICstaticpose+mj_forward、guard0Step，COM/body误差~1.7e−16m、gravityprojection7.62e−11Nm。nomEqFz70.0574/70.1681由motor/Gas/J/MCI解出，不硬塞mg/2、不补静态g。

Input `ContactProxy(Config).step(SensorInput,now)`，绝对q4/qdot/τ4输出侧域、3timestamp/有效/ProperRoot/ωα/σ/置信/标定显式；设计τfixture只sim/synthetic绑定。只nominal public常量、无runtimeDR override/contacts/root truth。动态RNE/wheelspin/patchmoments/guide载荷路径未全观，等效XZ不是身份，双off非全机air。默认confidencecap.55 < FSM默认.8，故不会凭32tests自动升级可靠触地。

当前优先PHASE2Git归档截至R16 +本sealedCONTACT/FSM/ARM/ODOM/QP/H1/H2，排除ACTIVEcurrentC3和R17及后新代码/scene。只ownbranch/tagatomic，不touch原expertindex/main，不重复phase1；rawproducerSHA仅索引；R15软件33与物理分母分开。PH1仍commit93e0814f.../tagtrial-20261102-mod4v1-robust-traditional-phase1，勿重做。

PH2sealed之后已安排新动态COM补偿目录(优先于他再查terrain，因为父已有boxport)：public31bodyFK/MCI rCOM(q)与rDot/rDDot、proper_COM =properOrigin+α×r+ω×(ω×r)+2ω×rDot+rDDot，sensorq/qd/qdd/ωα与uncertainties；wheelCOM偏心若需要wheelangle则显式绑定/未知降conf或worstbound，不假balancedwheel/不自动.8概率。只static/synthetic0Step，父后续用真值grading验证，不反馈给controller。

## 接续顺序

1. collect当前R26job，所有nonzero先查，不再多行注入猜缩进；新的软件error留原并独立分类，别用统计复跑填补遗失rows。
2. 接入sealedproxy/FSM先shadow诊断，defaultconf不足应如实unknown，不放宽阈值就冒可靠触地。考虑mean IMU窗口中心t−.00525与末帧encoder/torque时间偏移，不能同queueepoch就撒谎同步；新C3已写边界。
3. root需要障碍/动态腿控制；先named物理接触找6cm blocker，再传感器可达的检测/hop/高度调度，不删硬碰/导轮，不用gt前方距离。所有新variant TRAIN决定后新独立holdout，H1/H2只读。
4. currentC3/stdioadaptersealed后，父新MuJoCo闭环验证C链，区别preDC与finalτ、原inversePD+限幅的双层语义；ARM只对象不等于ARM runtime。
5. 保持goalactive、最多4物理CPU、无GPU/远程干扰、Phase2截止不追R17后活动文件；这些新进展下一PH3归档。
