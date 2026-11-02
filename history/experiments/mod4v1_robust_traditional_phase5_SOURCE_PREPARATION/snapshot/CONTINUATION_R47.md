# 接续 R47 — H5执行中时的阶段快照

> **后续H5已完成：40/64通过，64/64完整结束，768000物理步。当前主接续是[CONTINUATION_H5](<CONTINUATION_H5.md>)。下文“当前/运行中”均指本快照写作时，不代表H5仍在运行；不要重启同一batch。**

本文件更新至R47及H5执行前冻结。旧完整背景见[阶段包接续](<CONTINUATION_STAGE1_DELIVERY.md>)、[R38接续](<CONTINUATION_R38.md>)、[R34接续](<CONTINUATION_R34.md>)。旧文件是当时状态，后续进度以本文件为准。

## 目标/环境/约束

- 目标仍是独立传统LQR/MPC最终保底；SPR Balanced-infantry (1).zip为正确参考，4πrad/s为持续绕自身轴自转；独立于另一会话RL。
- 最近get：goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d，revision7，roundsStarted4/max12，active/armed；未更改complete/blocked/resume。
- cwd F:/RMPOLAR-RL，任务根为本文件目录；Python C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe，-B，BLAS/OMP/MKL各1，≤4物理CPU workers；不动GPU/SSH/PPO/canonical/专家工作树与index。
- Office/ACL技能无机器人任务匹配，使用文件/CLI。danger-full-access，审批关闭，不设置提权字段。先read再edit，发现用glob/grep；保留失败源码/日志/前缀，新case新ID；不为补档重跑已消费轨迹，不为归档重hash巨raw/资产。Mnemon无需写入。
- 只复用两个agent：C/math abf2088f-af10-479a-9108-202785031447；model/archive e4e6c8f2-f08d-4df1-9150-945c804e8c2a。不要新建agent，忽略闲置Mnemon子任务。

## 旧冻结证据与已交付包

H4实际C闭环驻车60/64、2m/s原速度姿态门槛64/64，但52/64横向峰值>.3m，不是直线精度资格。H2稳定角速/姿态64/64、综合56/64；停启换向未毕业。270mm、6cm粗糙路、完整硬件链仍未毕业。禁止在这些holdout上调参。

用户两次询问进度已回复，并已present[阶段包V1](<DELIVERY_STAGE1_20261102_V1/MOD4v1_Traditional_Stage1_20261102_V1.zip>)及[阶段报告V1](<reports/STAGE1_DELIVERY_PROGRESS_20261102.md>)。ZIP 10,725,489bytes/851payload/34有因省略，SHA8b5bd15b3c26db510ee353b233597332b5899e81e5cec4ef723d265dabe01288；7稳定C模块+验证/构建材料，不含大模型/raw/EXE/DLL/BIN，不是完整独立物理环境或已绑BSP。V1报告/ZIP保持不可变，新成果另开V2。

## PH4真正归档完成

正式[postcommit回执](<../repo-lqr-robust/history/experiments/mod4v1_robust_traditional_phase5_PENDING/ARCHIVE_PHASE4_RECEIPT.json>)已父逐行read：commit db8fd0606e00a450504853181a6b4cdf66869d68，parent fa6838807f4d69d2b8ac52300d74ad40f365d2ed；ownbranch mod4v1-lqr-mpc-robust；annotated tag trial-20261102-mod4v1-robust-traditional-phase4，object5aadabd68a83f1e4ef93dd2b18518128c46f87a9。remote ownbranch/tag/peeled一致，PH1/2/3未变，2932全A/无D/foreign/各blobSHA核对。原helper SHA b2fd15dee16735721e18ed88b55e9e3159344f1d6f8095217f2db84852c2cd3e未变（实际helper名record_experiment.py，以核对SHA为准）。main只声明紧邻操作窗口f30410178844fbd6d122922f218831b1ac095821同值，不宣称无其他会话并行推进。

PH4 cutoff只到R39+已封C/FSM/nativeMPC/COM/阶段V1/旧blockedIO与原型/PH3回执。9262源条目=2903新text68,499,328B+5155旧Git refs+1204rawmeta（1189known/15unknown），1个历史FSM ERROR_REPORT文本SHA版本缺口保留；原53/5/6历史字段不重写。所有WORLD_LEG、R40以后、MINIHOP_AUDIT_V2、observer/landing/power与本文件均PH5pending。不要重recordPH4。agent最后closing failed通知不推翻已落盘已读回执。

## R40–R43世界腿姿态，未放宽原rough gate

真实SCUT/RM tiny_step 9×9m有限地面、完整2–6cm条栅，是11类之一，不是整套RM CAD。原模型/接触/DR/PD/signedDC保持。

- V1 sensor pitch反向共同hip/crank参考，gain.75/cap.30/rate2/hipref±.48，保持delta。R40四名义4/6cm×delta0/.2：0/4，85000物理步；d0h4无非轮/进展7.72m，但停车仍保持腿参考导致末段pitchRMS.3225rad；估计误差RMS.00398rad不是主因。
- V2从启动就按shapedv/.4激活：R41四名义0/4，85000步。末段pitch改善却改变启动路径，d0h4 guide7/y.5607失败。
- [V3控制器](<ROUGH_WORLD_LEG_V3/controller.py>)只在第一次forward→stop后才随速度退world补偿，启动/drive与V1严格相同。R42单名义4cm13s/26000步通过：progress7.083941m/y.259411m/nonwheel0/tailpitchRMS.0258172/vRMSE.0426536/peakpitch.7393rad。851控制采样/17020步以前共享106375leaf比较0差（不是所有物理字段都逐步全量记录）。[R42事实](<reports/R42_NOMINAL4CM_FACTS.json>)。
- R43 V3全DR TRAIN4401..4408共208000步，8/8complete，只有4407 PASS（1/8）；其余非轮/进展/y/两例末段姿态失败。[原batch](<batches/r43_world_DR8/BATCH_RESULT.json>)，旧失败不改写。无heading/roll新消融实现。
- 计数语义注意：[RM buffer源码](<physics_bridge_rm_buffer_v1.py#L26-L33>)的nonwheel_ticks是每0.5ms先hit布尔再加一次，即unique physics ticks；不能把旧R30某些逐contactpoint计数的描述泛化到R22/R40/R43所有字段。

## 严格小跳审计V2与R44–R45

[MINIHOP_AUDIT_V2说明](<MINIHOP_AUDIT_V2/README.md>)封存，INDEX9ee8c0ee1bc02115aa3cb9ba0ae090610b42605007ff67c0c29e7ccb9f3fab80。all-positive环境normal先汇总，total≤1N连续20ms为operational air；main/guide/hard、worldforce signed frame及cache pre-stage与rootpost+.5ms区分。只是private grading，不送控制器；不是硬件air/冲击额定证据。原R39每点>1N再汇总旧分数不重grade。

R44 stationary flat固定pushdelta+.2/push.14/air.35/captureblend.10，DR4221..4224：4complete/48000步，原V2 flat80mm/no-guide-hard/endstable2s门槛3/4；4222guide4727 ticks/endstable0失败。首次落地均mainwheel，瞬时5.7–7.1kN，不是硬件软着陆证明。[R44事实](<reports/R44_MINIHOP_FACTS.json>)。

[R45新observer控制器](<MINIHOP_OBSERVER_V2/controller.py>)仅将wheelKF及groundkinematics禁用延到push后.50s，不改torque phase/重力修正schedule。初unit001在check998误把legacy end当精确1.99；原源码/log保留0physics。实际[边界诊断](<MINIHOP_OBSERVER_V2/BOUNDARY_DIAGNOSTIC.json>)：old1.9900000000000002，真正启用2.00，新2.14，所以只改14ticks2.00..2.13。002只修test oracle，3221/0，固定estimated inputs的600扭矩math bitmatch。

R45四同seed新轨迹4complete/48000步，仍3/4；4222guide4727→31/endstable0→2.149999999999998，但guide非0依旧失败。首次landing仍2.046/righttire6878N；新firstguide2.3625、pitch21.05°、guide04/06合5485N。新support有间断，100Hz endstable不等于2k连续支撑。

父已读[配对因果README](<R45_OBSERVER_CAUSAL_V1/README.md>)，INDEX768859a9f348080bcd9c5032e63d361e8ef9ec5879667a123393ef16a97c814b：4case各200条command0..1.99，800records/92000共享leaf严格binary64bits（含signedzero）/离散相同；除新phase/wall，涵盖估计/请求/公开packet与before-after grade；不是4000逐物理step全量bit比。只读8控制trace+坏seed2physics，无新物理/拟合/大raw重hash。2k每腿q4没存，unknown；不能用100Hz bracket冒同stage腿姿。新guide在重启观测后只说明时序，不证明必然因果。

## R46–R47主动落地：两候选各4/4 TRAIN通过

[新landing控制器](<MINIHOP_LANDING_V3/controller.py>)继承R45。仅timed capture开始后.20s cubic平滑leg位置ref、预计算两名义K与ff；保留同一shaper/yaw状态、原push/flight/capture时钟和.50s观测quarantine。无在线DARE/仿真truth/DR参数；默认landing_transition_enable=false。K凸插值是实验策略，不是稳定性证明。固定腿PD实际用0速度参考，未假称跟踪轨迹导数。[数学预检](<MINIHOP_LANDING_V3/preflight001/RESULT.json>)5414/0/0步，两候选disable600bitmatch、enable前200bitmatch、FK有限及endpoint精确。

R46候选landing delta−.4（旧jump bank）名义600/12000通过。delta−.2（旧nominal gain）原runner把保存的gain wrapper直接arrays，KeyError q，0controls/0step；旧[ERROR](<results/r46_l20_nominal/ERROR.json>)与空前缀保留，不能算robot失败。单测用load_gain而runtime没用，入口覆盖不足。

新[runner v4](<run_minihop_landing_v4.py>)仅修实际loader：bank用arrays，single复用已有load_gain并shape/finite检查，先加载再建plant；control-loop AST相同。[loader入场预检](<MINIHOP_LANDING_V3/loader_preflight004/RESULT.json>)14/0/0步真实导入两个spec与构造。只新R46b补未消费的−.2名义600/12000 PASS，没重跑−.4。

R47使用v4，两候选各同4221..4224，8/8complete/96000步、各4/4通过原V2门槛。**只有4个独立DR种子，不是8个独立样本。** 两候选peak mesh相同.1776735/.2574349/.2509380/.2116717m（apex在调度前）；所有guide/hard0。l40 worstpitch.3203076/minendstable2.63；l20 .2596820/2.87。坏4222分别end2.63/2.87，均无guide。[训练事实与选择](<reports/R47_LANDING_TRAIN_FACTS.json>)记录8条result及producer rawSHA，未再读大raw。

## H5独立验证：已冻结，已于2026-11-03 00:11 +08启动

[冻结协议](<MINIHOP_L20_H5_V1/PROTOCOL.json>)SHA b2aac213f21abda333ec98c711bbec4c1db8577d16683639d632c8e2ae0d6d0b、[base config](<MINIHOP_L20_H5_V1/FROZEN_BASE_CONFIG.json>)、[41文件index](<MINIHOP_L20_H5_V1/CONTROLLER_SOURCE_INDEX.json>)已落盘，不修改。TRAIN后/holdout前依据通过数→较低worstpitch→较长minendstable选择l20（不是预先注册的TRAIN排名规则）。

计划新seeds62100..62163/64，batch配置目录grep无已有seed命中，flat stationary operator-timed6s，600control/12000physics各，总768000步，max4 CPU。原100Hz boxcar→D1→D3信息路径，无raw2k额外信息。保持全部D0–D7真实路径/原grade；robot失败仍跑完整计划并留档；软件错误停止后续waves、保留prefix与unstarted，不能补种替换。64/64 Wilson95下界约.9434不是95%可靠度证明。

[独立审查JSON](<MINIHOP_L20_H5_V1/PRE_EXEC_REVIEW.json>)、[简报](<MINIHOP_L20_H5_V1/PRE_EXEC_REVIEW.md>)、[receipt](<MINIHOP_L20_H5_V1/PRE_EXEC_REVIEW_RECEIPT.json>)父已read，PASS且issues=[]，未消费H5。JSON SHA5f398445c6b7e75bd05a76e8dfa8227714f3be41224f591654346935a1408954。父创建[限定仿真放行记录](<MINIHOP_L20_H5_V1/PARENT_LAUNCH_APPROVAL.json>)后执行[launcher](<launch_h5_minihop_l20_v1.py>)；当前父后台job **pwsh-7b1d1da9096548bf**，运行中，尚未收最终结果。不可再launch同一batch。预计结果在batches/h5_l20_minihop64/BATCH_RESULT.json（待生成，不冒充已存在）。候选41文件和冻结3文件未改。最近R47 pwsh-0501a87db2154e2e、R46b pwsh-c3126daa740c4562已exit0 collect。

[分析脚本](<analyze_h5_minihop_l20_v1.py>)已创建并AST检查通过，尚未运行读取H5结果。仅读小result/protocol核对配置、原门槛、D0–D7/信息路径、实际控制/步数及producer SHA元数据；无raw重hash/新physics/调参。若软件错误或未启动，完整64分母资格与Wilson置null；robot health/grade失败仍保留。model agent现只读该统计脚本作短审查，不读H5未完结果。

## Power sealed，父已read；当前两agent新任务

[Power说明](<SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/README.md>)与[VALIDATION](<SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/VALIDATION.json>)父已核验：INDEX37f85d62a731a9dd3fe17b92c107d26d19dab31eb919adf1115ede56a21830ae，ZIP5b36782d316e616eb74a673ee5141078e22ed79f2393f1a98e27b29a96176002，core613723ccdb1021ec9cf04b4b1260261b73368c6cd6f4ca307eba88b50240c571。219=27named+192random，38508/0，input24309bits全同，209valid/7 reserve-infeasible/3 uncertified原样；native2290/0、CPP实际pass、36逻辑clock全invalid，M4/M7首次2objects23324/23084B只compile。首2290/1及38508中的3个负零endpoint bit失败保留，仅s==1优先级修复，不改fixture/认证/预算。

电模型用BUS-referred Cbus_loss_upper与其他损耗上界，非裸绕组R。Klower需预算电流量上界关系，非裸Kt自动保证总相流。显式reserve不缩减；invalid zero不是必需制动signedbox中的合格fallback。默认实机校准/电热/电池域UNBOUND→invalid。未接任何robot轨迹；ARM软double/helpers/libm、FTZ/区间证书前提、BSP/runtime/ISR/WCET未绑。实际源头文件在模块根pa1_allocator.h，不是猜测include/pa1.h（后者read notfound，不是ACL）。

- [接口seam报告](<CONTROL_CHAIN_SEAM_AUDIT_V1/REPORT.md>)84行及[receipt](<CONTROL_CHAIN_SEAM_AUDIT_V1/RECEIPT.json>)已完成/父read，REPORT SHA663d4997492cff2b1c31449e495be7a7399ba5f62990097dc56c23b83e412b4f。实际C3内部已enqueue且cycle出参无REF/MATH/SHAPER全bundle；FSM是state/advice非反向自动发送许可；NM final clock/deadline故障可同时valid=1给数学fallback，须外查clock_valid/deadline/总callerdeadline；Power后float/CAN/tracking证书与NM warm/last_u实际held一致性未解决。默认unknown/disable与硬件unbound保持。这里只读7文件0实现/编译/physics，不是总链资格。
- C agent已新接PC3_CANDIDATE_BUNDLE_V1最小**非驱动**纯API候选adapter：估计/P25/DC数学独立快照、完整epoch/shaper语义、available ns与checked us/故障/alias保护；不调用cycle/enqueue，不发硬件，不接MPC/Power/FSM，不伪造许可。新组件可用旧3200fixture验证（无新physics），仅host/C++及M4/M7对象编译；尚未完成不入现有包，旧core冻结。避免把旧closing通知当新任务已完成。
- model agent现做H5统计脚本短静态审查；R45包/执行前审查已完成，不因closing failed重跑。只新review文档，不改冻结JSON或读取H5未完结果。

后续尚需实际driver-rate功率链/双板BSP与HIL、移动/自动越障、6cm与270mm、自转停启换向，以及更强独立holdout。不要只因软件模块存在、compile成功、TRAIN4/4或64跑完便完成Goal。
