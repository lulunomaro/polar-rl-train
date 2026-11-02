# R51当前主接续 — 两项capture时序试验已完成，原gate 0/2

完整背景/环境/PH5真实Git/CB1封存/旧R48–49证据见[主R50接续](<CONTINUATION_R50.md>)，旧H5仍40/64冻结。[当前Goal]为原goal-4d4bef80-e614-432d-a8cd-8f385ef2dd7d，最近revision8/r5/max12 active/armed，未complete/blocked。

## R50最新结果，已collect

父job pwsh-00131f9a7af442c8已exit0并job_output收完；[flat batch](<batches/r50a_smooth_air_flat1/BATCH_RESULT.json>)及[RM batch](<batches/r50b_smooth_air_first_bar1/BATCH_RESULT.json>)两个新名义case都800controls/16000steps，总32000新物理步。

- smooth .16s quintic飞行腿参考+brake2.7的flat移动gate通过：peakair.1671462m/endstable3.43/guide-hard0。
- 同策略RM6cm局部gate仍失败：guide13/hard0、pitchpeak.6109783、endstable3.51、progress2.72654/y.11918；整个collision包络过首bar且没到下一bar两项都真。any-air rear-cross2.616是后续air，**first-flight-only rear-cross为null**。
- [R50事实](<reports/R50_SMOOTH_AIR_FACTS.json>)：旧R49对新R50在新air-ref生效2.24之前224controls/4480steps的23744共享leaf（state/packet/tau/grade等）0bit/离散差；不是全部physics逐bit证明。guide7→13、pitch .5949→.611，故smooth策略没有治guideground，旧失败保留，不宣称更鲁棒。guide时间2.5115..2.527，早于stop变化2.7；不能归因后续brake。

## R51预先限定的两项TRAIN，已收齐

[R51协议](<MANUAL_BAR_CAPTURE_TIMING_V1/PROTOCOL.json>)是**bar-specific operator-timed landing-preparation**，复用原V3（不是V4 smooth）与同旧guard/K/ff；已在R49 TRAIN观察bar-top landing2.4955后guideground2.507，而原planned capture2.59附近才开始。只将predicted_air_after_push从.35改为.18/.25，用定时提前准备腿姿，brake2.7用于局部停车；observer quarantine仍.5（名义边界2.74），不是接触检测，不用H5。

新[runner capture-v3](<run_manual_capture_v3.py>)保留v2 private first-flight-vs-rebound标签、原driver。两case只RM名义，早capture参数是已知support-height-specific profile；不以同参数flat gate作为预选门槛，协议在物理前明确此scope（无实机）。没有降低任何局部成功gate：guide/hard严格0、mesh>=.08/endstable>=2/y<=.3/progress>=.5/整个包络过首bar且全程未到下bar。

[零步预检](<MANUAL_BAR_CAPTURE_TIMING_V1/RESULT.json>)1666/0、0integrator/1600固定合成command。浮点边界实际capture tick .18案**2.43**（数学边界2.42），.25案2.49；不能把名义边界当真实100Hz执行tick。observer实际启用tick也以运行记录为准，不硬补2.74。

父后台job **pwsh-9cfb919a91754be2**已exit0、job_output已collect，**不要重复launch**。case r51_bar_air180/r51_bar_air250各800controls/16000physics，总32000新物理步，两个均complete但原局部gate **0/2**：guide分别7/11ticks且nextbar保守包络失败；endstable3.43/3.51、pitchpeak.595195/.593985。两案first-flight-only rear-cross均null（诊断，不是新增成功门槛）。[小结果汇总](<reports/R51_BAR_CAPTURE_FACTS.json>)没有读raw证明nextbar真实力身份。提前capture没有消除原guide，旧失败保留。所有新源码/物理均PH6pending，旧H5/PH5 seal不动。

## 两个原agent当前工作

- C abf2088f-af10-479a-9108-202785031447的CB1已seal并父read，后新接CONTROL_CORES_LINK_V1：实际BOM9唯一runtime TU+13头/inc=22，预算预声明，host每源一次对象复用C/CPP default smoke≤64assert/语言；M4/M7各9新对象+layout probe各一次armlink--partial。只是构建/符号/默认unbound组合，无真发送/完整事务/物理/旧QA，尚未完成；PH6pending。
- model e4e6c8f2-f08d-4df1-9150-945c804e8c2a在R49_MOVING_CONTACT_CAUSAL_V1做0physics小审查。已报告right tire对rm_bar_011的firstlanding点z.059876/法向[0,0,1]为top不是riser；guide6 ground2.507..2.510早于capture/gravity与wheelKF恢复，因此本案不归因上述重新启用。2.6045为后续rebound。可选dq→q条件重建须全800同epoch100Hz anchor<=1e−9rad，未通过则unknown；无改旧R45unknown、无改控制或H5。

## 长期约束

当前cwd F:/RMPOLAR-RL，Python314 -B，BLAS/OMP/MKL各1，≤4物理CPU，只有上述两agent，无GPU/SSH/RL canonical/专家index/新agent/Mnemon写入。catalog仅Office/ACL无robotics，文件CLI/read-before-edit/glob/grep；不为补档重跑轨迹/旧QA或大raw资产hash。当前仅父R51 job仍相关待collect，其他父job全settled。

PH5已经remote commit0a21cdc6445268c05389103afea071836424b470 / tagtrial-20261103-mod4v1-robust-traditional-phase5（object0701622bb247649b33f78fa4627bfa3f7a1cbd9c），只ownrefs，严格截止H5+Power+seam，不再record。CB1/R48以后及本文件均PH6pending。原1历史错误报告版本SHA缺口/unknown raw继续披露。总体6cm全段/270mm/自转停启换向/可信接触FSM/真实driver-rate功率及唯一发送/双板BSP/HIL/WCET仍未毕业。
