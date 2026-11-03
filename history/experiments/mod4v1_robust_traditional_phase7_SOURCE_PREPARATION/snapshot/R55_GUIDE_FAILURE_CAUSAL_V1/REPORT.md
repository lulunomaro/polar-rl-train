# R55_GUIDE_FAILURE_CAUSAL_V1 — 两条 fullDR TRAIN 的只读事件分析

## 范围与结论
- 仅4503/4505：[方法](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/R55_GUIDE_FAILURE_CAUSAL_V1/METHOD.json>)和[20小输入SHA/两路径锁](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/R55_GUIDE_FAILURE_CAUSAL_V1/SOURCE_LOCK.json>)先锁，四个raw各解析一次，分别800控制行+16000私有物理行；26项必要源码匹配实际producer manifest。无其他TRAIN/heldout/H5、大raw hash或279mesh读取。
- **两例原guide计数严格保留33/3，原first-bar判定均false。4503是先主轮碰杆、后guide落ground；4505是主轮先落ground、后guide碰杆顶，不能合成同一唯一机理。** 不改控制/观测/扰动或原分数。
- [精简事件JSON](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/R55_GUIDE_FAILURE_CAUSAL_V1/SUMMARY.json>) / [有界事件与去重邻近控制证据](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/R55_GUIDE_FAILURE_CAUSAL_V1/EVENTS.json>) / [receipt](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/R55_GUIDE_FAILURE_CAUSAL_V1/RECEIPT.json>)。后续只读这些新保存事件，无重扫或字节上限重试。

## 同stage语义
- [实际runner:52–70](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/run_manual_capture_v3.py#L52-L70>)先在`command_time_s`取packet/估计/算request，再执行20个0.5ms子步；trace的`grade_before`对应控制起点，`grade_after/time_s`对应起点+10ms。
- [hook:43–64/106–134](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/contact_grade_v2.py#L43-L134>)记录PRE root位置、同stage刷新后的rotation/接触/力、同stage bounded ctrl；POST root另列。下面pitch均由**同stage PRE rotation**算，不用POST或最近100Hz姿态冒充。
- [air:122–128](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/contact_grade_v2.py#L122-L128>)为全部环境正法向总力≤1N持续40个0.5ms stage；“air起点”是回标区间起点，“确认POST”晚20ms。guide计数沿[runner:74](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/run_manual_capture_v3.py#L74>)的`guide_normal_N>1`，不是contact点数。
- 首杆是两case相同的rm_bar_011：x=[1.651910,1.837022]m，top z=.06m。“首次杆接触”专指任一单点normal>1N，与全环境air阈值分开。

## 事件顺序（时间s；pitch为rad）
| 事件 | 4503 | 4505 |
|---|---|---|
| 首杆任一点>1N | **2.0735，timed_push**；right_tire→bar前沿/顶，两个点2855.97/700.78N，同时有ground支撑；PRE pitch=-.00534 | **2.4575，timed_capture**；guide05→bar顶6764.39N，同时主轮在ground；PRE pitch=-.21529 |
| 首qualified-air区间起点 / 确认POST | 2.0955 / 2.1155；起点PRE pitch=+.03306 | 2.0770 / 2.0970；起点PRE pitch=-.01117 |
| first landing | **2.4440，guide04/06→ground**，总25254.13N、主轮0；PRE pitch=+.82400 | **2.4380，left_tire→ground**，6966.82N、guide0；PRE pitch=-.23205 |
| guide首 / 峰 / 末 | 2.4440 / 2.4440 / 2.5250；峰25254.13N，表面全ground | 2.4575 / 2.4575 / 2.4585；峰6764.39N，guide05→bar011 |
| guide计数/连续段 | **33 ticks，13段**；首末跨度81ms，不是连续16.5ms | **3 ticks，1段**；3个连续0.5ms stage，计1.5ms |

- 4503确实在air起点前22ms已主轮碰杆；但“更早触发必然解决”仍无因果试验证据，其他fullDR/轨迹也不同。首landing已是guide触ground，而非guide触杆。
- 4503在首landing的PRE root=[2.008683,.011800,.296512]m，root x虽过杆，记录的main rear x=1.743702仍未越back=1.837022；原first-flight main-rear-crossing仍null。不用root点越杆替代全轮/全机清杆。
- 4505原first-flight main-rear crossing=2.3675s；首landing后19.5ms才guide碰杆。其guide点约[1.795093,.115785,.059881]m，仍在杆顶范围，而main rear x=1.947102已过杆后沿。**主轮清杆并不证明guide/全机清杆。**
- 所有正力contact身份/坐标保留在事件证据；未把冲击峰值当准静态支撑能力或电机电功率。

## 实际参考、K/ff权重与observer
- 两例控制日志相同：1.95s进push；**2.09s仍标push**且wheel quarantine已开；2.10s进predicted_flight_retract；**2.35s进timed_capture**；K/ff/eq权重2.36s首次>0、2.55s满1；wheel/ground-kinematic观测隔离至2.59s。使用实际100Hz记录，不把理想2.34s当实际切换时刻。
- [landing schedule:25–47](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_LANDING_V3/controller.py#L25-L47>)同时插值K、tau_eq和eq，再置真实Ground分支ref；是定时实验，不是contact detector或稳定性证明。[observer:14–25](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_OBSERVER_V2/controller.py#L14-L25>)亦明确timer不是contact。
- 两例guide首/峰均发生在wheel observer仍隔离时，4503最后guide亦早于2.59s。因此这些事件不是“恰逢wheel观测重新打开”的证据；也不据此排除此前惯性观测误差。
- **实际capture用`landing_position_ref4`，不是V1残留`target_q4`。** [Ground固定腿:30–31](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/ground_controller_v4.py#L30-L31>)用ref的绝对hip/crank组合；V1的`target_q4`在capture仍为[.454174,-.041510]×2，不代表此时Ground PD目标。

| 时刻及意义 | 实际landing ref4（左右相同，列每侧hip/crank） | K/ff/eq权重 | 邻近100Hz observer/真估姿态 |
|---|---|---:|---|
| 2.43，4505首landing所在控制区间 | [.382420,-.009183]×2 | .35200 | wheel disabled；pitch估-.223660 / before真-.229437 |
| 2.44，4503首landing所在控制区间 | [.367489,-.002456]×2 | .42525 | wheel disabled；pitch估+.795944 / before真+.813554 |
| 2.45，4505 guide所在控制区间 | [.352251,+.004409]×2 | .50000 | wheel disabled；pitch估-.219876 / before真-.226546 |

- 4503在2.43s、首次guide前14ms，真pitch已+.787596，估+.769559。大姿态偏移先于首次guide，guide冲击不是全部先前旋转的原因；2.44s同控制起点估/真误差约-.01761rad，不拿4ms后的PRE pitch=.82400与之直接当同时误差。
- 两例2.43/2.44/2.45时的ref和权重相同，真实姿态/接触不同；“4505由capture单独造成”尚未识别。2k真实active q4未记录，**unknown**；不由dq积分或D1/D2编码器重建冒充校验真值，也不反推出腿实际跟踪误差。
- 本两case D3 receipt为0ms，但D1噪声/D2偏置仍开；4503仅D0层标nominal，其他DR仍存在。D4记录4503腿5ms/轮2.5ms、4505均5ms；这些仅解释数据来源，未送入任何控制或取消扰动。

## 请求与末子步ctrl
- [实际motor链:8–16](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py#L8-L16>)先用观测生成processed target，再D4/当前状态PD/双DC clip/motor gain；bounded ctrl是写`d.ctrl`的模拟控制输入，非独立实测输出扭矩。
- `request`标控制起点，最后子步ctrl在起点+9.5ms；事件ctrl另按事件PRE stage配对。4503首landing ctrl为2.444s，早于该区间末值2.4495s；4505 guide ctrl为2.4575s，早于末值2.4595s。两者既非同request时刻，也非同target队列内容。
- 4503在2.44s请求轮[+5.77591,+5.77591]Nm，first-landing事件ctrl约[+.81279,+.81481]、该区间末值约[+.50445,+.50469]。4505在2.43s请求轮[-5.77591,-5.77591]，2.438s landing事件约[-.80036,-.79894]，2.4395s末值约[-5.77591,-.73754]。同一100Hz请求内ctrl也会变化。
- 缺queued/processed target、preclip raw和clip mask，request-ctrl差不直接识别具体饱和/迟滞的唯一贡献；不读取DR采样值补造这些阶段，也不把编码器/姿态变化全归capture。

## 封存资格
- 原guide33/3与两case false逐项复核；仅提出观测区别，不提出新控制候选、不重评分、不归唯一机理。没有自设输出字节cap/重扫循环；四raw只打开一次，随后仅保存事件分析。
- **本新分析PH7 pending，排除当前PH6 cutoff。** 无model/mesh加载、physics、编译、旧QA、Git、新agent或root活动world_leg修改；contact私有grade未变成controller/public cue或新许可。
