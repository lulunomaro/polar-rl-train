# R62 AIRREF response：两组TRAIN只读请求级诊断

**结论：早期h效应确有部分被请求级±40Nm裁剪遮蔽；不是“全部无效”，也不是实际DC/硬件饱和或失败唯一因果证明。** 4606首hard为负pitch下chassis_front触第一bar顶面；4610退化是原保守final-bounds gate，不按翻倒/真实shape碰撞解释。

## 范围与时间
- [方法](<METHOD.json>)与[26小源锁/58实际manifest匹配](<SOURCE_LOCK.json>)先于raw；仅旧/新4606、4610四条800行控制trace及**新4606一条16000行physics**，各一次，共19200行，无raw重hash/拷贝或其他TRAIN/H5。完整flight行与七点hard小窗见[EXTRACTED](<EXTRACTED.json>)，精简事实见[FACTS](<FACTS.json>)，审计见[RECEIPT](<RECEIPT.json>)。
- [实际entry:63–80](<../MINIHOP_AIR_PITCH_REF_V1/attempt002/run_manual_air_pitch_ref_v1.py#L63-L80>)：表中t是command_time_s，row.time/grade_after晚10ms；encoder是同packet的D1/D2/D3位置/速度观测，非实际2k关节位置；不把窗端位置与带窗速率当成同步瞬时状态。pitch是command时刻age-view，pitchrate仍source-window Euler率，见[sensor:126–133](<../sensor_core_jump_v1.py#L126-L133>)。4606首flight sensor=2.000/age10ms；4610=2.160/age0，仍非瞬时率。
- firstflight前201/216个公共100Hz snapshot、22字段，共9174字段值二进制比较0差异；**不是2k轨迹/接触相同证明**。两pair的DR小metadata相同；看过旧结局的TRAIN机制对照非holdout。

## Flight首tick至capture anchor：实际输入与参考
角度rad、率rad/s；q表示左hip/crank、右侧参考相同。Flight用target_q4，capture用**landing_position_ref4**；generic target_q4在capture恢复原q_start，不是实际ground参考。旧h字段不存在，表记“—”而非伪造日志零。
| case/时刻 | t | estimated pitch/rate | goal h / 实际h或anchor | 实际参考(hip,crank) |
|---|---:|---:|---:|---:|
|R60/4606 firstflight|2.010|-.112425 / -3.108681|—|(.454174,-.041510)|
|R62/4606 firstflight|2.010|-.112425 / -3.108681|-.100000 / -.010000|(.444174,-.051510)|
|R60/4606 firstcapture|2.260|-.714293 / -2.129359|—|(.454174,-.041510)|
|R62/4606 firstcapture|2.260|-.675825 / -2.140417|held -.100000 / anchor -.100000|(.354174,-.141510)|
|R60/4610 firstflight|2.160|+.003359 / +.104158|—|(.454174,-.041510)|
|R62/4610 firstflight|2.160|+.003359 / +.104158|+.005006083 / +.005006083|(.459180,-.036504)|
|R60/4610 firstcapture|2.410|-.073908 / -.012907|—|(.454174,-.041510)|
|R62/4610 firstcapture|2.410|-.068614 / -.033236|held -.012266898 / anchor -.012266898|(.441907,-.053777)|
- 各25 flight tick。[新源:78–98](<../MINIHOP_AIR_PITCH_REF_V1/attempt002/controller.py#L78-L98>)的goal/h/target重建最大误差0；首capture实际参考与末flight参考连续误差≤2.776e-17rad，**不冒称τ连续证明**。capture goal为末flight保持值，不能再当此时重新计算的goal。
- 4606 raw goal25/25低于-.10，h速率限制active9tick、h到-.10共16tick；4610 goal未碰两端，速率限制active10tick、h未碰域两端。原002参数/default-off未改，不增第三h。

## 请求裁剪：直接重建及其局限
- 预声明[原flight式:85–99](<../MINIHOP_V1/controller.py#L85-L99>)：leg_pre=140*(logged target_q4-encoder_q4)-3*encoder_qd4，外裁剪±40；wheel用原25*pitch+4*pitchrate及原yaw差动/峰值。100 flight rows×6输出对actual requested最大误差**0Nm**，门1e-9；未调用任何旧controller/replay/QA。
- “去h”只把同一recorded packet的target换成冻结public crouch，其余输入不动。它是**同packet请求代数敏感性**，不是旧case反事实trajectory。每新case100个leg-axis-ticks的全遮蔽/部分/传递分别**22/2/76**、**16/0/84**，全部非零h效应。
| case | flight腿request到±40次数 [LH,LC,RH,RC] | wheel到峰值[L,R] | flight wheel均值[L,R] Nm | capture首.2s wheel均值[L,R] Nm |
|---|---:|---:|---:|---:|
|R60/4606|[5,6,4,7]|[25,25]|[-5.77591,-5.77591]|[-3.11905,-3.18267]|
|R62/4606|[5,7,4,8]|[25,25]|[-5.77591,-5.77591]|[-2.62878,-2.41128]|
|R60/4610|[5,4,5,2]|[3,3]|[-2.48066,-2.31469]|[+.69637,+.69549]|
|R62/4610|[5,4,5,2]|[2,2]|[-2.34480,-2.19296]|[+.59300,+.61832]|
- 新4606首tick未clip腿=[85.412902,-78.512831,83.119553,-79.860061]Nm，h已变而四腿请求仍[40,-40,40,-40]；2.01–2.04四tick全四腿h效应完全遮蔽。新4610的2.16–2.17两tick同样如此。
- 配对首leg请求数值分歧：4606=2.05、4610=2.18；estimated pitch/rate分歧2.07/2.19，4610 wheel也2.19分歧，4606 flight wheel全程仍在负峰值。**这些相邻100Hz差值不是D4延迟测量。** 状态分歧后两条轨迹不再是同输入比较。
- capture进入旧[V3 K/FF/eq/ref schedule](<../MINIHOP_LANDING_V3/controller.py#L25-L47>)及[ground LQR/PD/yaw/roll](<../ground_controller_v4.py#L21-L36>)路径，wheel可随参考/状态改变；不把synthetic同输入flight wheel不变外推成capture wheel不变。完整capture preclip、I/混合内部状态未重建。

## 新4606首hard：真实私有PRE-stage小窗
[private capture/grade源](<../MINIHOP_AUDIT_V2/contact_grade_v2.py#L43-L110>)将drive/contact/regular-root-R标PRE，root_post另晚.5ms。firsthard **2.3335s：chassis_front(id17)→rm_bar_011(id11) TOP**，点(1.835758630,.137575306,.059094460)m、环境向robot法向(0,0,1)，fn35379.105N；距top .906mm、距bar-back1.264mm。不是因“靠近back”就命名背面；面判定阈值先锁于方法。
| PRE stage s | body pitch rad | hard normal N | capture weight | observer |
|---:|---:|---:|---:|---|
|2.3235|-.800208|0|.21600|isolated|
|2.3285|-.810627|0|.21600|isolated|
|2.3330|-.819915|0|.28175|isolated|
|2.3335|-.820942|35379.105|.28175|isolated|
|2.3340|-.818905|4814.556|.28175|isolated|
|2.3385|-.796462|0|.28175|isolated|
|2.3435|-.772154|0|.35200|isolated|
- firsthard在capture2.26后73.5ms，anchor=-.10；roll=-.058164。2.33 command estimated pitch=-.830324、source pitchrate=-2.159329。observer直到2.50才恢复；此窗两hard tick、guide0与原result一致。前10ms已负pitch -.800208且总normal=0，故该碰撞不是全部先行旋转的原因；不由此指定唯一失效机制。
- 同PRE-stage actual_tau确有记录：首hard model bounded τ6=[14.366285,-15.414176,-.798005,12.665932,-13.515530,-.787674]Nm；2.33的请求leg4=[13.192290,-16.323340,9.567350,-13.452012]、wheel=[-5.775910,-5.775910]，request age3.5ms。[原driver链:8–16](<../MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py#L8-L16>)含inversePD/D4/current PD/两次signedDC/gain；actual_tau是末端d.ctrl模型命令，非独立测力。
- 其余三例此窗口同stage actual τ **UNKNOWN**；即使新4606有boundedτ和dq，也无各内部clipmask/raw-PD，**actual DC clip次数UNKNOWN**。push ±32 pre-roll/target限幅等不可由最终request到峰值唯一反推；所有case的实际2k q仍UNKNOWN，不积分dq或套名义递推。

## 4610：停止位置与保守gate，非翻倒/碰撞归因
- 仅用这两small result：root final X 2.264746806→2.226867745m（-37.879061mm），sphere-envelope minX 1.866383093→1.828106760m，bar back1.837022445，margin **+29.360648→-8.915685mm**。final pitch .010267→.009616、roll小、vx近0、guide/hard均0。
- [bounds:45–58](<../MANUAL_FIRST_BAR_V1/grade_rows.py#L45-L58>)是compiled-rbound球包络；本FAIL保持原conservative gate，既非真实shape碰撞证据，也不证明真实shape已过。h改变后的闭环/捕获位置参考与状态耦合，当前证据不把-37.879mm唯一分摊给某个PD/anchor/clip阶段。

## 冻结边界
原[父R62 2/2 nominal、1/4 vs同seed旧2/4事实](<../reports/R62_AIRREF_NOMINAL_AND_PAIRED_FACTS.md>)及所有原gate不改；只分析两个已选TRAIN机制，不拟合参数/增gain/第三h，不改002 sealed/default-off。0新PHY/旧QA/compile/Git/newagent，PH8 pending；详见[receipt](<RECEIPT.json>)。
