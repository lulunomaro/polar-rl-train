# R60当前接续：新16TRAIN仅10/16，停止把旧8的7/8当鲁棒证明

## 当前权威状态

原goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d本轮实际get为 **revision9、roundsStarted6/max12、active/armed**。不重建/resume/complete/blocked。cwd F:/RMPOLAR-RL；任务根为本目录。Python314绝对路径C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe、-B，OPENBLAS/OMP/MKL各1，<=4物理CPU worker，无GPU/SSH/RL canonical/专家worktree或index/新agent/Mnemon写入。catalog Office/ACL无robotics，使用文件CLI；read-before-edit/glob/grep；approvaldisabled不要escalation。所有父PHY job现已settled并collect。

完整既有背景见[旧R55](<CONTINUATION_R55.md>)、[R56 preexec历史](<CONTINUATION_R56_PREEXEC.md>)，后者是写作时状态，不应据其“未launch”否定以下实际完成记录。旧H1/H2/H4/H5、Stage1 V1以及所有source seal不回写。

## PH6 Git已经真实完成，勿再record

父本轮read正式receipt，commit4e7a3fb9855657b5b501de08785f875b1e0bedfd（parent0a21cdc...），ownbranch mod4v1-lqr-mpc-robust，annotated tagtrial-20261103-mod4v1-robust-traditional-phase6 objectdb83d307944644ccf46b4b43b79ffc5633d6897b；remote own/tag/peeled一致，PH1–5refs保留。285全A=279SOURCE+5cover+1record，两门blobSHA/exactpaths/noD/foreign全过，helper b2fd15...不改、inmemoryargv+narrowadd、仅OWNrefs atomic nonforce。main并发54667...→b93479...保留，只紧邻push同值，未写main/expert。postreceipt在ownrepo phase7_PENDING，不在PH6tree；不递归trial。

严格PH6截止R53+CB1/九核build、R49/R52诊断；R54及以后、SPIN_STOP、新诊断、当前手动position profile均PH7pending。旧源版本1历史FSM缺口/7rawunknown及重复binary claims保留。无资产/raw归档hash/旧PHY或旧QA重放。

## 手动position候选：R56已真实入场

[controller](<MINIHOP_POSITION_TRIGGER_V1/controller.py>)默认False，继承原V3非AirRetract V4；达到相对估计里程1.18m后锁下一100Hz tick，次tickprepare_estimator先于packet/update；min decision1s/deadline2.6，等待哨兵2.61无timerfallback。真实push仍检查原.15pitch/roll与1.2speed。原relative push.14/air.25/observer.5/landing.2/captureblend.1/gain/DR/driver/gate不变；浮点边界可差1tick，以真实phase为准。手动里程不是独立世界位置/接触/障碍许可，无RAW2K增强。

[1809零步](<MINIHOP_POSITION_TRIGGER_V1/preflight001/RESULT.json>)后，model agent独立[core review](<MINIHOP_POSITION_TRIGGER_V1/preflight001/PRE_EXEC_REVIEW.json>)及[launcher review](<MINIHOP_POSITION_TRIGGER_V1/preflight001/LAUNCHER_PRE_EXEC_REVIEW.json>)PASS/ready true；父read。新[launcher v2](<launch_manual_profile_train_v2.py>)explicit runner/源锁/preparer锁/并发数/flat→matchingRM，不改v1。

R56父job pwsh-6af2aeacd2c349ee 已collect exit0；r56_position_flat/rm各800/16000，总32000步，两场原gate各True，nominal主指标精确重现旧t195结果；这用于新entry准入，不算新的独立鲁棒性样本。RM firstflight rear-cross2.3825、endstable3.67、guide/hard0、peakmesh.182723m。

## 同8种子配对与更高landing profile

[R57报告](<reports/R57_POSITION_PAIRED_TRAIN_FACTS.md>)是4501..4508同TRAIN新variant、旧R55 baseline未重跑。job pwsh-ac0b927b19004003 已collect；8complete、128000步。local6/8→6/8不变，gained4503（guide33→0）、regressed4504（0→4），4505仍3；main-firstflight4→7，联合3→5。8对DR receipts逐值相同。不能称16个独立样本或已整体改善成功率。

[guide名义静态几何](<LANDING_GUIDE_CLEARANCE_PROPOSAL_V1/REPORT.md>)父read并验收：30个指定reference/weight/pitch，1modelboot/30forward/0integrator，全正余量。guide05是chassis下cylinder **r15mm/半长8mm、offset[-.259,.131,-.135]、轴body-Y**，不是r8mm。使用实际两轮mesh支持求根高，不用.0625滚动半径或circumradius。限定roll/yaw0、wheelphase0、理想名义参考跟踪；不是4505真实q/clearance或operatinglimit。在pitch−.2153时nominal/weight.5余量17.753mm、δ0为33.721、δ+.2为50.002。正余量不能撤销真实碰触。

R58只改landing_gain spec为[已存delta0](<TALL_ROUGH_BANK_V1/gain_delta0.json>)，其K/ff/eq/ref由旧V3一起插值，所以不是纯高度单因素。posture选择为较近的更高参考、TRAIN假说，不是静态证书。原position调度/guard/driver/time不改。[零步939/0](<MINIHOP_POSITION_TRIGGER_V1/tall0_profile003/RESULT.json>)、236个capture前合成τbit相同、102referenceFK点，未新线性化或onlineDARE。

R58 job pwsh-29bcd613627b4ce3 已collect；nominalflat/RM各800/16000均通过原gate，RM endstable4.49、peakpitch.29999、guide/hard0、firstflightcross2.3825。R59 job pwsh-6a15c6f1a4444f73 已collect；同8 TRAIN128000步，**local7/8、firstflight7/8、联合6/8**，gained4505、无local regression vsR57，仅4504 guide2仍失败。见[R59事实](<reports/R59_TALL0_PAIRED_TRAIN_FACTS.json>)，由[通用小result汇总](<record_local_bar_train_v1.py>)重算原gate，无大raw读取/重hash。绝不把guide2舍入忽略。

## R60 fresh16是重要负泛化证据

[冻结计划](<MINIHOP_POSITION_TRIGGER_V1/tall0_fresh_train005/PROTOCOL.json>)在旧8上选择δ0后、物理前冻结代码/配置，未用4601..4616（父grep核）；max4、8s、原100Hz传感/2k物理/全D0–D7，机器人失败继续/软件错停波，不替换种子。它是fresh TRAIN，不是独立H6。

父job **pwsh-40a42e43ba144f99**已exit0并在本轮collect：**16/16完整、12800controls/256000真实步，原local仅10/16**。main-firstflight rear-cross16/16，但联合也仅10/16。失败guide seeds4601/4603/4605/4606/4609/4614；4606还hard5。所有原门槛保留，尾部稳定不能盖过碰触。peakmesh约.17957..26130m，仍非270mm。见[R60报告](<reports/R60_TALL0_FRESH16_TRAIN_FACTS.md>)及[结构化结果](<reports/R60_TALL0_FRESH16_TRAIN_FACTS.json>)。

父依据全小result实际汇总确认，不凭截断stdout填数；无需重launch补档。旧8拟合7/8不能代表泛化，暂不再盲目加高姿态或宣称强鲁棒。16个main清杆不等于整机/guide/hard都净跨，这正是此轮定位重点。代码/基准不改H1/H2/H4/H5，无H5 raw调参。

## 当前两个原agent的新任务（无新agent）

- C abf2088f-af10-479a-9108-202785031447：AIR_PITCH_AUTHORITY_V1，尚待结果。仅3existing姿态crouch/pushendδ+.2/landingδ0，rootZ1m/姿态0/qvel0/轮phase0，保留全部geoms/ground/闭链确保ncon0；每pose ctrl0、双hip+1Nm、双crank+1、双wheel common+1，共12 mj_forward，禁止step。先核actuator行序/gear/rootpitch frame，报告相对ctrl0 rootpitch/关节qacc小扰动响应与符号。不是完整D4持续施矩/硬件权限或姿态控制证书，不选gain/不写runtime。正常boot，不另资产hash/读raw。
- model e4e6c8f2-f08d-4df1-9150-945c804e8c2a：R60_FRESH_CONTACT_AUDIT_V1，尚待结果。只freshTRAIN4606 hard+大pitch、4605 guide+低pitch，各trace/physics一次；firstbar/air起点确认/firstlanding/guide/hard首峰末+计数、samePRE rootpitch/forces、真实position decision/push与邻近landingref/weight/observer。不预设唯一原因，不积分D1/D2 q冒真q，不读其他raw/H5/DR样值入控制，<=90行报告+事件JSON，0新PHY/Git/编译/旧QA/新agent/归档rawhash。

## 下一步与完整目标缺口

先读上述两报告再选择新单因素策略，不以静态余量表或unit qacc直接定实际gain；可能需要审查launch/flight/landing力矩与全机清障，而非只修主轮标签。无R61新控制/PHY存在，未发新H6；若后续新variant，先default-off/源前锁/真实entry零步+名义准入，再新TRAIN/正式新holdout。不能把这个局部单bar结果扩成全9m/其余10族/2mps越障/270/自动contact FSM/已接Power或C跳跃。

强目标还缺全程rough、270跳落、自转停启换向、真实driver-rate功率与actual-held/unique-send、双板BSP/HIL/WCET。原H4C stand60/64/forward64/64但lane未过，H2angular64/64但composite56/64、stopreverse旧0/8/R27both2/8；H5仍40/64，全部冻结。保留goal active。下一新报告/代码均PH7pending。
