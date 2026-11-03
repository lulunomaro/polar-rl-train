# R55当前接续：名义首次飞越6cm首bar；新全DR TRAIN局部6/8，双条件3/8

## 目标与环境

原goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d继续active/armed；最近实际get为revision8/round5/max12，未完成/blocked/重建。完整旧范围见[H5/此前接续](<CONTINUATION_R51.md>)、[R50接续](<CONTINUATION_R50.md>)及更早R34/R38。任务是独立传统LQR/MPC最终保底，不碰另一RL专家会话。SPR正确引用是Balanced-infantry (1).zip；自转是持续4πrad/s。

cwd F:/RMPOLAR-RL；Python314绝对路径为C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe，-B、OPENBLAS/OMP/MKL各1，最多4物理CPU worker，无GPU/SSH/PPO/canonical/专家worktree或index写入。catalog只有Office/ACL无robotics，当前文件/CLI执行。danger-full-access/approvaldisabled，不加escalation flags。read-before-edit/glob/grep；不为补档重跑已消耗物理/旧QA或大raw资产hash；不写Mnemon，不开新agent。

原模型MJCF SHA0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324；.5ms implicitfast物理/100Hz控制、全原几何/接触/闭链/原D0–D7与inversePD→D4 target→randomPD/gain→signedDC保持。当前hop仍Python V3，非C跳跃/可信自动接触FSM。原100Hz均值→D1→D3，没有RAW2K增强输入。只初始化root，无中途assist/reset。Guide/hard>1N物理采样严格0的gate不放宽。

## R51–R53已收齐的负结果（保留）

- [R51事实](<reports/R51_BAR_CAPTURE_FACTS.json>)：提前capture .18/.25在旧approach/t2.1下各完整16000步，原局部0/2，guide7/11且nextbar包络失败。两案firstflight cross null。父job pwsh-9cfb919a91754be2已collect。
- [R52计划](<MANUAL_FIRST_BAR_V1/early_takeoff003/PROTOCOL.json>)改forward .9/startx.2/trigger2.0/stop2.5，复用原V3与guard。独立[review](<MANUAL_FIRST_BAR_V1/early_takeoff003/PRE_EXEC_REVIEW.json>)ready true/15个small源SHA，零步803。真实flat800controls/16000steps完整但guide7，故[RM未准入](<MANUAL_FIRST_BAR_V1/early_takeoff003/RM_ADMISSION_DECISION.json>)，不是RM失败；case r52_early_rm未消耗。父job pwsh-d98f294c509f4abb已collect。
- [R52接触诊断](<R52_FLAT_CONTACT_CAUSAL_V1/REPORT.md>)：firstlanding2.464左轮ground6869.99N/pitch−3.38°；capture2.49，K/ref首非零2.50，而stop命令也在2.50（confound）。guide06 ground2.537..2.540共7ticks，rootPREz.213526/pitch14.667°、主轮力0；wheel/ground实际恢复2.64在guide之后，非初guide前因。不把legacy target_q4当capture实际参考，要看landing_position_ref4。
- [R53计划](<MANUAL_FIRST_BAR_V1/early_landing004/PROTOCOL.json>)仅在R52上把predAir .35改.18/.25，零步2066、实际capture tick2.33/2.39。flat2/2 gate通过后才匹配RM；4case均800/16000，总64000新步，RM0/2，guide9/8，nextbar包络均True，firstflight cross仍null。父job pwsh-ac45ab83bdd34424已collect。
- [R53直接接触证据](<reports/R53_PREAIR_BAR_CONTACT.json>)用可复用[有界分析器](<inspect_first_bar_contact_v1.py>)只读到4272physics rows：首bar前上棱接触2.1355，仍timed_push且早于first **qualified20ms** air2.1395；法向x≈−.9777/z≈.2101，合Fn5908.855N。该样本所有正力来自bar，**不据此声称仍有ground支持或此前从未短暂离地**；qualified-air与真实瞬时takeoff不同。

## R54真正新增的名义结果

[协议](<MANUAL_FIRST_BAR_V1/takeoff_window005/PROTOCOL.json>)预列t1.90/t1.95，其他均R53 air250同参数：predAir.25/obs.5/forward.9/start.2/stop2.5、原pitch-roll .15和speed1.2guard。air250选择在R53 TRAIN后，非R53前预注册；依据同样flat pass/RM fail中较小峰pitch，已诚实记录。不是H5调参。

[零步预检](<MANUAL_FIRST_BAR_V1/takeoff_window005/RESULT.json>)982/0、600新profile合成command，未跑物理；实际capture tick t190=2.29/t195=2.35。新[通用名义TRAIN launcher](<launch_manual_profile_train_v1.py>)仅parent-admitted TRAIN，按去scene/terrain/ID后的完整control profile严格flat→RM匹配；软件错停余波、失败不改标；不是独立HOLDOUT launcher。

[名义结果](<reports/R54_FIRST_FLIGHT_6CM_FACTS.json>)及[简报](<reports/R54_FIRST_FLIGHT_6CM_FACTS.md>)：4/4完整、3200controls/64000physics，flat2/2，RM1/2。

| RM方案 | guide/hard ticks | 首次qualified-air中main-rear cross | endstable | 原局部gate |
|---|---:|---:|---:|---|
| t1.90 | 0/0 | null | 3.58s | False，仅nextbar保守包络失败；未仅据此补造真实nextbar力接触 |
| t1.95 | 0/0 | 2.3825s | 3.67s | True |

T195首次取得**主轮mesh后沿在原operational-air中且firstlanding前越过首bar后沿**；最终全collision保守包络在bar后且没有到下bar包络。peak mesh .182723m、maxY .004134m、pitchpeak.257927rad。这里不是整机瞬间AABB全腾空跨过，不是真实零力证明；air阈值为Σ全部正world法向≤1N持续20ms。不是270mm、全9m格栅/全部11地形、全DR可靠性或硬件资格。父job pwsh-3a8e2935dc704665已collect。

## R55新全DR TRAIN，已收齐（不要重复launch）

[launcher](<launch_r55_first_bar_DR8_v1.py>)在R54后选择唯一名义原局部gate通过的t195，之后冻结[新TRAIN协议](<MANUAL_FIRST_BAR_V1/t195_DR_train006/PROTOCOL.json>)与[source前索引](<MANUAL_FIRST_BAR_V1/t195_DR_train006/SOURCE_PREEXEC.json>)，未用种子4501..4508、nominalFalse、FullD0–D7、8s/100Hz/2k，max4。父grep在写计划前确认batches JSON无这些seed；新ID不重复。它不是独立holdout。

父job **pwsh-0fbde356c5a54f0d**已exit0/job_output collect，8/8 complete、6400controls/128000真实步；源/原gate不变。全部hard0、endstable>=2、Y<=.3、最终behindbar/nevernextbar两项True。统计见[结构化事实](<reports/R55_FULLDR_FIRST_BAR_TRAIN_FACTS.json>)及[简报](<reports/R55_FULLDR_FIRST_BAR_TRAIN_FACTS.md>)。

- 原局部gate **6/8**，失败4503 guide33ticks、4505 guide3ticks；3ticks仍严格失败，不舍入或看尾部稳定改分。
- 首次qualified-air中main-rear cross **4/8**：4501/4505/4507/4508。
- **同时原gate通过且firstflight cross仅3/8**：4501/4507/4508。不能把6/8写成6/8 clean首次飞越。4502/4504/4506可满足原局部gate而没firstflight cross，landing或rebound语义另列。
- peakmesh范围.191558..246364m，依旧非270mm。4503 pitchpeak.813554但完整恢复，guide仍失败；勿未读raw就断言4503唯一撞棱机理。4505 firstflight已有cross但有后续guide，可能是不同问题，尚需有界TRAIN诊断。
- 接近指令.9m/s、手动定时单bar后停车，不是2m/s越障或自动感知控制。100Hz endstable不是每个2k采样连续双主轮支撑。C jump/Power未接进此次physics。

## 新C九核组合交付已父read验收（仅构建资格）

[README](<SPR_AUDIT/CONTROL_CORES_LINK_V1/README.md>)、[VALIDATION](<SPR_AUDIT/CONTROL_CORES_LINK_V1/VALIDATION.json>)、[RECEIPT](<SPR_AUDIT/CONTROL_CORES_LINK_V1/RECEIPT.json>)已读。9唯一runtime C TU+13header/inc=22原源均未变；host同9对象完整C与extern-C CPP各37/0新default smoke、29layout字段一致、45强定义无重复。全部默认invalid/send0或FSM inhibit，**不是有效控制/发送事务**。

M4/M7各9runtime+1constprobe，一次真实armlink --partial --no_remove --no_scanlib，133360/131156B，ELF ET_REL非固件；内部peer闭合，各36系统libm/RT/内存未定义项保留。未ARM执行/RT库+BSP链接/WCET/量化/driver-preview/actual-held/final enqueue。

首审计遗漏__hardfp__fabsf，原failed脚本/log保留。安装math.h证实alias后只修精确分类器重读saved对象，未重编/link/smoke/旧QA。封存INDEX 8adb9c3d33c671a72a730fe66f5f9352ada1649af67357040a7f7c30b07ce0a8。36entry[source/build ZIP](<SPR_AUDIT/CONTROL_CORES_LINK_V1/control_cores_source_bundle.zip>)77951B，SHA28ce215c2c4cd79367346abe780ab23f93cb76d14899780feb1d415706128c5c。CB1本身纯candidate，不等于发送许可。

## 两个旧agent当前工作，勿开新agent

1. C abf2088f-af10-479a-9108-202785031447在SPIN_STOP_CAUSAL_V1分析**仅R26/R27both TRAIN201/202四trace**，无heldout。方法/32小输入先锁、46源SHA核对，DRV配对相同，4×2600行。首提取因111180B超98304B输出预算，未写WINDOWS；保留失败后只以全局列schema无损去重、重读四trace收尾；现WINDOWS92991B，未改窗口/阈值/数据。现已封存且父read[58行报告](<SPIN_STOP_CAUSAL_V1/REPORT.md>)与[RECEIPT](<SPIN_STOP_CAUSAL_V1/RECEIPT.json>)；报告SHA866f8b80d74d00ef27bbdfb27253842c105a07642203d9a453b064737a7a23d7、receipt8c65e44afd5aac94e9ff9686519406f874e396175e9e6645112c0abdf785372e。agent当前已inactive，无运行job；只提出下一TRAIN假说，未实施新spin控制。
   - 中间事实：正stop命令10s、负stop22.01（floatgrid），shaped w要stop+2.09s才0，但common-centering校正在operator stop立即关。
   - R27both从startup也介入，非单因素stop干预。negative-stop seed202 baseline/both位移1.1861/.5892m，最后1s truevx.5467/.0701；source-aligned vx偏差−.1037/−.0879、age-view pitch误差−.0841/−.0695rad。因此有真实漂移亦有观测误差，不把残差全归时戳。
   - 没有yawI/抗饱和标量或2k raw target/clip mask。末子步ctrl不是独立电机力矩/电功率；requested/ctrl都没碰绝对峰不证明没signedDC饱和。旧R26 0/8与R27both2/8不改。
2. model e4e6c8f2-f08d-4df1-9150-945c804e8c2a：R49/R52诊断与R52review已完成/父read；现按[PH6正式cutoff](<PH6_ARCHIVE_CUTOFF_R53.json>)做SOURCE_PREPARATION ONLY，等待REVIEW_HANDOFF/INDEX/manifest/consistency/gaps。**未授权stage/record/commit/tag/push**。目标ownrepo下phase6_SOURCE_PREPARATION，不能碰expert/main/index。0physics/大rawhash/旧QA/新agent。

## Git与档案边界

PH5已真实remote commit0a21cdc6445268c05389103afea071836424b470，annotated trial-20261103-mod4v1-robust-traditional-phase5 object0701622bb247649b33f78fa4627bfa3f7a1cbd9c，811allA/无D/foreign、只ownbranch+newtag。正式postreceipt在ownrepo phase6_PENDING，父旧轮已read；不重复record。

PH6 SOURCE截止**R53闭合结果+CB1/九核build+R49/R52诊断+PH5receipt**，预计13物理result/182040步仅独立对账期待，以真实receipt为准；deferred RM不是失败。只明确allowlist/import-producer闭合，脚本routing hint不当存在证明。旧PH1–5同byte优先Gitref，raw/279资产producer metadata、unknown保持unknown，单历史FSM错误报告SHA版本缺口继续披露。

**R54/takeoff_window005、通用launcher、SPIN_STOP、R55及本接续/后续报告都排除PH6，归PH7pending。** R54源/结果中旧provisional PH6_pending布尔不回写篡改，实际成员由后来的明确cutoff决定。Stage1 V1 ZIP及已交付报告保持原样。

## 下一实质动作

先收并read两个agent结果，所有父job当前已settled/collect。下一PHY未启动，不预称R56存在。可仅在新TRAIN上有界诊断4503与4505的firstbar/landing/guide时序，再决定新的manual位置触发或leg-only预落地调度；**不要凭猜测断言原因或用H5失败raw调参**。若实现新variant需default disabled、preserve旧source、零步entry验证、明确新TRAIN/冻结/再新holdout。不能把这次6/8当全9m或clean firstflight通过率。

强鲁棒整目标仍有6cm全程/其他地形、270mm跳落、spin停启换向、可信接触FSM/功率实际driver域、唯一发送和board BSP/HIL/WCET缺口；保留goal active。H4 stand60/64/fwd64/64但lane未过；H2 angular64/64而composite56/64；H5仍40/64，均冻结，不靠名义或host断言补成整体验收。
