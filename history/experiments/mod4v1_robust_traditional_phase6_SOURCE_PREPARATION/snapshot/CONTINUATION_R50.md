# R50接续 — 移动小跳/首坎原型执行中，PH5已真归档

主背景沿[H5接续](<CONTINUATION_H5.md>)及[旧R47](<CONTINUATION_R47.md>)。H5仍独立冻结40/64，不用其失败调参。当前Goal最近get revision8/round5/12 active/armed，id goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d；任务整体未完成。

## 环境与资源

cwd F:/RMPOLAR-RL，任务根是本文件目录；Python C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe，-B/BLAS-OMP-MKL各1，最多4物理CPU。新试验用1–2workers，无GPU/SSH/PPO/canonical/expert index/实机。技能Office/ACL无robotics匹配，文件/CLI，read-before-edit/glob/grep；不补跑已消费轨迹，不为归档重hash大raw/资产。无需Mnemon写入。只复用C abf2088f-af10-479a-9108-202785031447、model e4e6c8f2-f08d-4df1-9150-945c804e8c2a，不新agent。

## PH5真实完成，父已read正式回执

[PH5 postcommit receipt](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase6_PENDING/ARCHIVE_PHASE5_RECEIPT.json>)110行父已read。commit0a21cdc6445268c05389103afea071836424b470，parentdb8fd0606e00a450504853181a6b4cdf66869d68；ownbranch mod4v1-lqr-mpc-robust；annotated tag trial-20261103-mod4v1-robust-traditional-phase5，tagobject0701622bb247649b33f78fa4627bfa3f7a1cbd9c/peeled同commit，remote逐项验证。原helper SHA b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e不变，单次helper/narrow-add，811全A无D/foreign/blobsSHA全验；只ownbranch+新tag atomic，PH1–4不变。main仅紧邻窗口70cf50fd3c2fbb0a19b62e1e672372bdd6c29327同，不宣称整个period无并发。

PH5截止H5+Power+seam，2416源条目=792新text14,527,569B+984旧Gitrefs+640rawmeta（638known/2currentunknown与旧15unknown重叠），1776textpairs全核；100case=99physicalresult+1R46zero-step ERROR。1历史FSM ERROR_REPORT保存SHA版本缺口保留。SOURCE_PREPARATION/cover/唯一record已入Git，旧phase5_PENDING未stage/未删（同bytes在snapshot），新postreceipt PH6pending；不能称whole worktree clean，也不要重record/push/tag。新CB1/所有R48+物理和脚本排除，均PH6pending。

## CB1候选数学服务已seal并父read

[README](<SPR_AUDIT/PC3_CANDIDATE_BUNDLE_V1/README.md>)47行、[VALIDATION](<SPR_AUDIT/PC3_CANDIDATE_BUNDLE_V1/VALIDATION.json>)和[RECEIPT](<SPR_AUDIT/PC3_CANDIDATE_BUNDLE_V1/RECEIPT.json>)已读。

- 新3200固定fixture组合268829检查0/逐bit0；238行internal/effective shaper不同已正确区分；newnative1583/0、CPP真externC PASS、25clock/age/expiry插点、M4/M7首次2objects7868/7320B compile-only。
- 首native1583/1为测试把age0 view与raw signedzero直接位等误断，旧失败/source/bin/CSV保留；仅新oracle保存raw再比held-view，core未改、3200不重跑。
- INDEX112文件，SHA d1f069e115761a34e605fd622ffa21952b3559f97e7f36ed8984010e7a9096af；RECEIPT95d1a858c1c252e7a04e22f284f891842bbd1f74c9e574cae745906f3ff2d91b；[source ZIP](<SPR_AUDIT/PC3_CANDIDATE_BUNDLE_V1/cb1_source_bundle.zip>)23934B/9entries SHA6cd5f2613c7649f550ca674545a17f77e761ec7cd1417f0a753687112ed36fcf；core42c03540ab13b7dc8cd99ae7abc966f63f7843127d13818b812156a146adf3d0。元数据GBK读UTF8首seal错误保留，UTF8修复复用ZIP，无重测/编译。
- 只是estimator/P25/DC纯API的no-send候选bundle。candidate_math_valid不是send_permission，可用输出send恒0；默认unbound/disabled显式init/arm，command.enable0不伪装1。mean gyro/source/arrival/aged前7维/held roll及internal/effective shaper各自标记；无dispatch/enqueue/FSM/MPC/Power/driver总链/板/WCET资格。17真实引用末SHA全同，旧core只读。

C agent现已复用做CONTROL_CORES_LINK_V1：仅选一次每个runtime源做CB1+C3数学/C2+FSM+nativeMPC/ASQP+Power组合host C/C++真实链接、极少默认unbound typed smoke、新M4/M7 relocatable或compile-only符号检查。排除dispatch/SDK/parser/worker/send，不伪造contact许可、不实现事务/driver，不重跑旧3200/219等，尚未完成；全部PH6pending。

## R48–R49新TRAIN（不改H5）

[手动首坎说明](<MANUAL_FIRST_BAR_V1/README.md>)、[runner v1](<run_manual_first_bar_v1.py>)复用原V3 controller，只改operator/forward/stop配置，完整SCUT finite9×9m tiny_step 6cm场景仍含全部条栅/机器人碰撞。只局部首横坎，不冒整段RM或270mm。private [bounds rows](<MANUAL_FIRST_BAR_V1/grade_rows.py>)在force audit后给所有mask/显式pair collision geom的compiled rbound+1e−8球包络及exact tire x，未改物理形状；false包络证明不等于实际触碰，另看真实contact。

R48 [0step admission](<MANUAL_FIRST_BAR_V1/preflight001/RESULT.json>)4840/0，2真实静态modelboot/2400固定合成command，0integrator。新1m/s、x=.8、trigger1s、stop2s：flat实际101controls/2020steps后controller_guard退出，e.pitch.219678>.15，真pitch.226775，v~.747；没有air/guide/hard，两个RM config依入场规则未消费。[R48事实](<reports/R48_MOVING_ADMISSION_FACTS.json>)。没有放宽guard。

R49仅延后operator、延长跑道（x=.1，trigger2/2.1，stop3s），controller/gain/guard不改。[0step002](<MANUAL_FIRST_BAR_V1/long_runway002/RESULT.json>)1605/0，真实初始tire后缘minx.00163762>=0。
- t2.0 flat在201controls/4020steps被v估计1.216265>1.2挡住，pitch约−.0033，没有降门槛或算通过。
- t2.1 flat 800/16000完整/局部flat gate通过：peakair.1803484m/endstable3.20s/guide-hard0，progress3.14925m/y.04045。
- 只将该admitted时间送同t2.1 RM6cm，800/16000完整但局部gate失败：guide7/hard0，endstable4.02s/progress3.02877/y.10665、peakair.1549868；实际nextbar012有>1N contact137ticks，包络maxfront3.79988越3.48893，scope停车也失败。不能宣称整段粗糙路或首坎严格通过。
- [接触事实](<reports/R49_FIRST_BAR_CONTACT_FACTS.json>)父从该单case raw作因果读取（不是为归档hash）：guide6对**ground**2.507..2.510，7个0.5ms样本；firstair2.246，firstlanding2.4955；旧any-air rear-cross2.6045在landing后，是rebound，不能叫clean-first-flight。原分数不改写。

已收完父R48 job pwsh-b889f5af891244e3与R49 pwsh-67e624aa1cc64fe7，均exit0；它们包含guarded robot未过，不是software errors。R49合计36020步，R48另2020。

model agent在R49_MOVING_CONTACT_CAUSAL_V1做上述TRAIN有界归因（0新physics/Git/H5）。可选仅当确认积分器及所有100Hz对齐验证maxerr<=1e−9rad时，从nominal私有dq序列重建hinge q4；属于条件推导，不是原测量，不覆写旧R45unknown；若不满足就reject/unknown。只少数关键窗口/FK，不逐279mesh重建、不选gain。

## R50进行中，不能重复launch

新[air V4 subclass](<MINIHOP_AIR_RETRACT_V4/controller.py>)只在原flight时段把瞬间crouch leg位置ref改为end→crouch的.16s quintic；保留原0速度PD参考、所有guard、push/flight/capture时钟及V3 K/ff，default disabled。新[grade v2](<MANUAL_FIRST_BAR_V1/grade_rows_v2.py>)将first-flight-cross与任意后续air/rebound分开，旧R49结果不重grade。

[预检](<MINIHOP_AIR_RETRACT_V4/preflight001/RESULT.json>)3277/0、0integrator，1600固定输入新旧比较；defaultdisabled与非flight τ逐bit同，17个flight tick有真实目标/τ变化，最大refstep.0523776rad；引用q_start归还，原几何FK有效、firstflight/rebound私有分类fixture验证。不是机器人成功率。

[新runner](<run_manual_air_retract_v2.py>)从v1派生，仅控制器/私有classifier/结果标签换新，实际driver仍原封闭类；新增sourceclosure与controller_equations_unchanged=false明确。旧landing manifest继承changed描述只涵盖capture，scope以新kind/新source/实际V4为准，不伪装仅命令变更。

[协议](<MINIHOP_AIR_RETRACT_V4/PROTOCOL.json>)预先固定x=.1、forward1、trigger2.1，新增smooth.16，brake提前2.7用于首坎局部停车；先新flat入场，再最多1个RM6cm。未读H5做选择。父后台job **pwsh-00131f9a7af442c8**已启动，当前未收最终结果；不可重启。对应[launcher](<launch_r50_smooth_air_v1.py>)、[preparer](<prepare_r50_smooth_air_v1.py>)。预期batch r50a_smooth_air_flat1及若admitted才有r50b_smooth_air_first_bar1；结果待实际collect。

所有新物理/模块/本文件为PH6pending；两板BSP、实际功率链/唯一发送、contact可信度/自主FSM、spin stop-reverse/6cm全段/270mm/HIL/WCET均未毕业。当前父仍有上述R50物理job，最终回复前收取；有用工作很多，不标Goal complete/blocked。
