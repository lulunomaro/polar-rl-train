# R56接续：PH6真实Git已完成；手动相对里程触发仅零步准入，尚未PHY

旧全背景和R54/R55真实结果见[主R55接续](<CONTINUATION_R55.md>)；原goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d最近实际get为revision8/r5/max12 active/armed，未重建/完成/blocked。当前没有父PHY job运行。

## PH6正式收尾，不要再次record

父已read源handoff/consistency/qualification、全377行case reconciliation和全862行gaps、ownrepo AGENTS及两Git政策；核7个小meta实际SHA、helper b2fd15...、ownbranch/HEAD/staged status，再写[PH6父review批准](<PH6_ARCHIVE_REVIEW_APPROVAL.json>)，仅授权一次原归档策略。

model agent已真实完成commit **4e7a3fb9855657b5b501de08785f875b1e0bedfd**，parent0a21cdc6445268c05389103afea071836424b470；ownbranch mod4v1-lqr-mpc-robust；annotated tag trial-20261103-mod4v1-robust-traditional-phase6、tagobject **db83d307944644ccf46b4b43b79ffc5633d6897b**。remote ownbranch/tagobject/peeled已逐项匹配，PH1–5 refs不变。285全A=279SOURCE_PREP+5cover+1record，afteradd/precommit两门无D/foreign/全部blobSHA匹配。原helper不改、inmemoryargv+narrowadd/no--push，atomic nonforce仅ownbranch+newtag。

main早probe54667...→pre-record b93479...的并发推进保留，只有紧邻push前后相同，不写main/expert/index/reset/checkout/force。父已read114行正式[PH6 postreceipt](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase7_PENDING/ARCHIVE_PHASE6_RECEIPT.json>)，它是PH7pending、不在PH6tree，勿递归造新trial。

PH6实际13物理result/9102controls/182040步，R48/R49两guard prefix失败保留；原source1842entries=260newtext11,335,062B+1077priorGitrefs+505rawmeta(498producerSHA/7unknown)，1历史FSM报告saved版本缺口及冲突binary claims如实留，未补造。严格截止R53+CB1/九核build+R49/R52诊断；**R54+、genericlauncher、SPIN_STOP、R55、新诊断/R56与本文件均PH7pending**。

## R55两个失败已被有界独立诊断，不是同一事件

父read[52行报告](<R55_GUIDE_FAILURE_CAUSAL_V1/REPORT.md>)与[receipt](<R55_GUIDE_FAILURE_CAUSAL_V1/RECEIPT.json>)。仅4503/4505四raw各1次，总33600行；20小源SHA不变/26producer匹配，0PHY/mesh/旧QA/Git/heldout，大raw未为归档重hash。

- 4503主轮在2.0735撞bar前沿且当时有ground支持；qualified-air起点2.0955/确认2.1155；首次landing2.444是guide04/06→ground、主轮0、PRE pitch+.824rad，峰25254.13N，33ticks/13段。大姿态偏移早于首次guide冲击，不称guide单独造成先前旋转。
- 4505主轮先在2.438落ground；2.4575 guide05碰bar顶，3ticks/1段，峰6764.39N，PRE pitch−.2153。主轮rear曾在2.3675空中越bar后沿不代表guide/全机也清杆。
- 两案实际capture2.35、K/ff/ref首权重>0=2.36、满1=2.55，observer隔离至2.59，guide都在隔离中。2k真实activeq未知，不能用D1/D2 noisyq或dq积分冒充nominal-only验证真值。原R55仍local6/8、firstflight4/8、联合3/8，guide33/3都失败，不改分数。

## 新候选：手动relative odometry锁NEXT tick，不是接触/地形/真位置检测

[新controller](<MINIHOP_POSITION_TRIGGER_V1/controller.py>)明确继承原Landing V3（不含AirRetract V4），position默认False、operator亦默认False。开时第一个validestimate仅设里程origin；relative estimate达到1.18m且decision>=1s，则只锁下个100Hz tick作为trigger，让下tickprepare_estimator先于packet采集/估计读取trigger。等待期trigger哨兵2.61；deadline2.6前未达距离先fault/INHIBIT，不偷偷回退旧1.95或哨兵处起跳。真实push首tick仍检查原pitch/roll .15/speed1.2，时钟/age/finite不放宽。

目标1.18来自nominal TRAIN的sensor distance，非真实root/DR补偿。仅父read了旧1.95时nominal e.distance1.1940、4503 1.2573、4505 1.2154作为固定时间位置不同的观察，不判唯一因果，不用H5。4505可能是不同guide问题，本单因素不预承诺都解决。

[新runner](<run_manual_position_v4.py>)只换class import及诚实metadata，main物理loop AST原样；sensor→estimate→新command→privategrade/apply，所有geometry/force只grading。原push .14、predAir .25、capture blend .1、landing .2、observer .5、gain/limits/DR和原gate均保留。注意“relative phase unchanged”指配置与公式，实际float/10ms边界仍可能差1tick，以日志为准，不混入integer-phase修复。原push阶段wheel仍可更新、quarantine从postpush开始，没有冒称触发即全隔离。

[准备器](<prepare_r56_position_trigger_v1.py>)已真实执行一次；[1809零步检查](<MINIHOP_POSITION_TRIGGER_V1/preflight001/RESULT.json>)0fail/0integrator。disabled600组τ与旧V3逐bit相同；enabled在同latch合成输入600组也相同，prepared flags一致。1.94当前prepared gain1.5仍approach、只锁1.95；次tick1.95预先gain0再push。名义旧trace**只作调度计算**195行，decision1.94/latch1.95，没有扭矩/四元数/物理重放。新entry真实loader、source SHA与loop AST一起验证。非稳定性/硬件资格。

R56计划case r56_position_flat/rm，仍nominal flat原gate实际通过才匹配RM。**尚未launch，不能填PHY结果。**

## 新launcher与待review

[通用launcher v2](<launch_manual_profile_train_v2.py>)新文件，旧v1不改：explicit --runner且runner必须有源锁；preparer由独立SHA或files同路径SHA锁；尊重protocol max_workers；支持--review并核ready与checked_sources；同control profile去scene/terrain/ID后严格flat→RM。

model agent正在R56独立pre-exec静态review，要求[preflight目录](<MINIHOP_POSITION_TRIGGER_V1/preflight001/>)下PRE_EXEC_REVIEW.json/md，ready_for_physics bool+实际checked_sources。最近中间消息尚无实质问题，正做最后SHA/AST；**等实际ready文件并父read后才启动**。计划命令（未执行）：

```powershell
$env:OPENBLAS_NUM_THREADS='1'; $env:OMP_NUM_THREADS='1'; $env:MKL_NUM_THREADS='1'
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B .\launch_manual_profile_train_v2.py --plan-dir MINIHOP_POSITION_TRIGGER_V1/preflight001 --expected-status PASS_ZERO_STEP_R56_POSITION --preparer prepare_r56_position_trigger_v1.py --runner run_manual_position_v4.py --batch-prefix r56_position_nominal --review MINIHOP_POSITION_TRIGGER_V1/preflight001/PRE_EXEC_REVIEW.json
```

[paired R57 launcher](<launch_r57_position_paired_DR8_v1.py>)仅已写未执行：要求真实r56_position_rm原localgate pass，再对4501..4508同8TRAIN种子新ID跑variant，旧R55结果不重跑。剥除4position keys及ID/cohort后config必须与各旧baseline精确相同。不是16独立样本或新holdout，8全DR、max4、软件错停余波/机器人失败保留。尚未创建paired_train002/PROTOCOL或case目录。

## 两旧agent，禁止新开

- model e4e6c8f2-f08d-4df1-9150-945c804e8c2a：PH6已完成后正在R56小review，不再Git/PHY。
- C abf2088f-af10-479a-9108-202785031447：R55诊断完成后开始LANDING_GUIDE_CLEARANCE_PROPOSAL_V1，只名义几何可行性：原landingδ−.2/已存tallδ0/.2三个候选、参考weight .5/1、pitch五点、roll0共<=30静态pose，用真实mainmesh/primitive支撑确定根高与guide05底面相对6cm余量。必要mj_forward但禁止step；不是4505实际q或动态安全/新operatinglimit，不选gain/不实现控制、不提升confidence，不读raw/H5或重hash279资产。尚待结果，不填表。

cwd仍F:/RMPOLAR-RL，Python314 -B/BLAS1、<=4PHY CPU、无GPU/SSH/专家canonical或worktree/index/新agent/Mnemon操作。Office/ACL catalog无robotics；fs read-before-edit/glob/grep，approvaldisabled不请求escalation。所有父jobs已收齐，无R56/R57 PHY运行。旧H1/H2/H4/H5/Stage1与source seal不改；whole9m/其余地形/270mm/spin停启换向/真实Power与唯一send/BSP/HIL/WCET继续未毕业，goal active。
