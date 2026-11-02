# CONTROL_CHAIN_SEAM_AUDIT_V1 — 有界静态接口审查

## 1. 结论与边界

- **当前有可拼接的无执行数学候选 API，没有已合格的“C3→FSM→MPC→driver→Power→唯一发送”总接口。** 以下是源接口审查，不是集成、编译、数值或实机证明。
- 仅审4个公共头及必要 enqueue/clock/final-commit 实现，共7个文件；catalog仅Office/ACL，无robotics匹配，使用文件/CLI。无fixture/physics/GPU/Git/newagent/goal/blockedIO行为，无全旧树重hash。
- 旧核均只读；所有建议接口尚未实现。硬件driver-rate、CAN、实际校准、双板BSP与时钟同步继续unbound。

## 2. 实际符号与源证据

| 核 | 实际入口/数据 | 证据 |
|---|---|---|
| C3数学 | `pc3_estimator_update/view`, `pc3_p25_step`, `pc3_original_dc_clip` | [C3-H:71–96](<../SPR_AUDIT/portable_control_v3_current/pc3_control.h#L71-L96>) |
| C3 dispatch | `pc3_cycle`, `pc3_enqueue_one`, `pc3_disable_and_invalidate`, `pc3_clock_us` | [C3-H:98–115](<../SPR_AUDIT/portable_control_v3_current/pc3_control.h#L98-L115>) |
| FSM | `fd1_step`, typed optional sources, `fd1_output` | [FSM-H:44–69](<../SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.h#L44-L69>), [79–88](<../SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.h#L79-L88>) |
| nativeMPC | `nm1_select`, `nm1_input/output`, available ns callback | [MPC-H:15–51](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.h#L15-L51>) |
| Power | `pa1_allocate`, live-domain input, external cycle clock | [Power-H:59–87](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.h#L59-L87>), [97–129](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.h#L97-L129>) |

## 3. C3已有发送；capture仅能改变backend，不能继承最终资格

- `pc3_cycle`在L30–33依次估计、P25、point-DC clip、row重排；L40已调用一次`enqueue_one`，L41才检查post-clock；任一abort通过L11调用disable/invalidate。[dispatch:10–11](<../SPR_AUDIT/portable_control_v3_current/pc3_dispatch.c#L10-L11>)、[30–42](<../SPR_AUDIT/portable_control_v3_current/pc3_dispatch.c#L30-L42>)。
- **若此backend已连接真实发送，外层再mux/Power/send就是第二次发送，第一帧也不会被后处理追溯修正。** 后验时钟只能撤销仍pending队列，不能撤销已在硬件执行的帧；源注释明确是queue-copy，不是immediate emission。
- 合同允许新增纯capture backend：同步按值copy到私有pending槽，禁止硬件/下游转发；disable清槽；仅在`pc3_cycle==PC3_OK`及其post-check完成后发布候选。不能保留指向局部`frame`的指针。[binding合同](<../SPR_AUDIT/portable_control_v3_current/pc3_control.h#L100-L110>)。
- capture必须有独立存储/clock fault side-channel；`declared_bindings=0x1ff`只是caller声明，不证明硬件。内部`have_sent`在capture场景只表示私有candidate被copy，不是最终driver ack。
- capture得到的`pc3_actuation`仅有guarded τ、重排τ、序号/expiry，**不包含MPC所需REF/MATH/SHAPER全bundle**；L15的`control`为局部变量。单换backend并没有解决候选数据出口。[C3-H:80–100](<../SPR_AUDIT/portable_control_v3_current/pc3_control.h#L80-L100>)、[dispatch:15](<../SPR_AUDIT/portable_control_v3_current/pc3_dispatch.c#L15>)。
- `cmd.enable=0`在当前cycle走abort/latch，并非无副作用的“监测但不发送”模式；不得为了拿candidate而把operator/FSM disable伪装为enable。[dispatch:22–25](<../SPR_AUDIT/portable_control_v3_current/pc3_dispatch.c#L22-L25>)。

## 4. 当前最小非驱动seam

- **首选新增薄候选adapter调用现有数学入口，不调用`pc3_cycle`**：估计输出→P25 result→在独立数组上`pc3_original_dc_clip`，产生`STATE14/REF14/MATH_TAU/GUARDED_TAU`，保留独立fallback副本后才调用`nm1_select`；结果只进入日志/私有候选槽，无真实enqueue。
- P25 result给出pre-DC `tau_row6/reference14`；MPC另需`shaper_v`。C3同时公开context的`shaper_v`与result的`shaped_v`，新bundle须明确内部/有效shaper语义，不能凭近似同名互换。[C3-H:80–92](<../SPR_AUDIT/portable_control_v3_current/pc3_control.h#L80-L92>)、[MPC-H:19–23](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.h#L19-L23>)。
- 此路径绕开了cycle自带command/bindings/drive-age/sequence/pre-post-clock gate；外层必须新增并审定相应guard，不能称已等价复用dispatch资格。[dispatch:21–36](<../SPR_AUDIT/portable_control_v3_current/pc3_dispatch.c#L21-L36>)。
- row6仍为LH,LC,LW,RH,RC,RW；wheel-first仅数学重排，不绑定物理front/rear、CAN ID、符号或reducer。[C3-H:93–96](<../SPR_AUDIT/portable_control_v3_current/pc3_control.h#L93-L96>)。
- 本次不修改estimator/FSM/MPC/Power，也不把数学候选设为driver-enabled；这就是当前能做到的最小非驱动seam，而非合格执行链。

## 5. 状态/许可与epoch不可偷换

- FSM输出是state/profile/phase/诊断，头部明确**无actuation permission**；`hard_inhibit`是上层必须尊重的否决，不是其反值自动成为发送许可。[FSM-H:3–6](<../SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.h#L3-L6>)、[65–88](<../SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.h#L65-L88>)。
- 保留`UNCERTAIN`/wheel未知值、可选字段present/valid bits与默认jump/recovery/auto-obstacle disabled；不增cue cap，不用C3 contact-consistency proxy冒充N单位force，也不用Power包络冒充实测motor power。[FSM-H:19–38](<../SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.h#L19-L38>)、[44–64](<../SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.h#L44-L64>)。
- FSM公开execution_context注释仅定义0unbound/1simulation/2synthetic_fixture；没有已声明hardware绑定。不能在板上填simulation来冒充硬件资格。[FSM-H:57–63](<../SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.h#L57-L63>)。
- nativeMPC的`abs(yaw_rate)>2`或`abs(pitch)>.25`只是模型domain fallback，既没有ground/contact字段，也不能排除小pitch飞行；MPC enabled必须另由已绑定normal/contact/operator许可给出，unknown/unbound时保持disabled。跳跃、预测flight、非normal不因角度小而启用。[MPC-H:19–23](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.h#L19-L23>)、[MPC-C:41–48](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c#L41-L48>)。
- C3 state14的4/6/11/13是crank-minus-hip delta/rate；FSM q4是absolute LH/LC/RH/RC，不能直接把delta当knee或absolute crank。新adapter应绑定原始encoder q4及其epoch。[C3-H:23–35](<../SPR_AUDIT/portable_control_v3_current/pc3_control.h#L23-L35>)、[FSM-H:3–6](<../SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.h#L3-L6>)。
- C3 estimate同时有sampled/estimated/age/aperture；aged view只预测x[0:7]，raw gyro/proxy/roll没有自动换到新body frame。FSM core仅一个timestamp：必须新增raw快照/多epoch对齐合同，不能把所有量统标为estimated-now。[C3-H:48–78](<../SPR_AUDIT/portable_control_v3_current/pc3_control.h#L48-L78>)、[FSM-H:48–54](<../SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.h#L48-L54>)。
- C3 packet有source/arrival/mean-end语义，drive只有sampled_us；dispatch检查各自age但未在L28–34要求drive与packet epoch相等。MPC显式要求`base_epoch_us==drive_epoch_us`；adapter须保留原source stamp与snapshot/frame身份，不把arrival或aged estimated_us伪装为base source epoch。[C3-H:31–38](<../SPR_AUDIT/portable_control_v3_current/pc3_control.h#L31-L38>)、[dispatch:28–34](<../SPR_AUDIT/portable_control_v3_current/pc3_dispatch.c#L28-L34>)、[MPC-C:42](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c#L42>)。

## 6. driver-rate与Power的真实断点

- `GUARDED_TAU`是同packet速度下的C3 point-DC数学fallback；它独立于QP并不等于稳定性/接触/热/电池/功率证书。MPC只在自身路径保留这份输入，不证明其在之后时刻仍合格。[MPC-C:43–65](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c#L43-L65>)。
- 必须在实际driver-rate、所有inversePD/D4/gain/其他torque-changing处理**之后**，用同一driver snapshot独立preview reserve与request；状态型PD/D4不能串行共用同一可变状态评估两次而污染reserve。当前四核没有该preview接口或实际电机链绑定。
- Power要求reachable speed interval、live Vlo/Vhi、温度域、电流/四象限/坐标证据、fresh signed box及reserve qualification；C3单点drive6和旧DC clip不自动提供这些数据。缺失保持unbound，禁止硬件数值猜测。[Power-H:11–38](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.h#L11-L38>)、[59–81](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.h#L59-L81>)。
- Power的最终证书绑定binary64实际输出表示；之后F64→F32、CAN lattice/符号/齿比换算、电流跟踪误差可能改变τ及box/功率。MPC此前inward f32 common-wheel box也不为后续变换提供电气证书。[MPC-C:45–57](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c#L45-L57>)、[Power-C:235–242](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.c#L235-L242>)。
- 当前Power公共API没有“对最终encoded payload+tracking torque enclosure纯再认证”的入口；不能靠cast、一般clamp、假冒新reserve或反复allocate声称补证。需新增不改变旧核的certified quantizer/enclosure verifier及对应电气证据。
- `PA1_RESERVE_INFEASIBLE/UNCERTIFIED`必须invalid，不能绕过Power直接下发同一未认证reserve。invalid的零τ在必需非零制动signed box中不是合格fallback；独立紧急hold/disable/watchdog策略仍待硬件绑定。[Power-H:117–129](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.h#L117-L129>)、[Power-C:210–220](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.c#L210-L220>)。

## 7. 统一时钟、全caller deadline与真实fallback gate

- 采用一个available monotonic u64 ns时基/clock epoch，外部cycle_start早于C3候选阶段；总期限包含snapshot/adapter/FSM/C3/MPC/driver-preview/Power/encode/final queue-copy，不在kernel START或各模块入口重新起算。[MPC-H:18–23](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.h#L18-L23>)、[Power-H:82–87](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.h#L82-L87>)。
- C3是us裸返回值；MPC/Power是int availability+ns。新增checked adapter：ns→us取整不抹掉source/arrival，us→ns检查overflow；外层ns gate主导真实expiry/age，us rounding不得延长截止。C3缺availability位，须out-of-band fault latch，不能把unavailable当0。[C3-H:101–109](<../SPR_AUDIT/portable_control_v3_current/pc3_control.h#L101-L109>)、[MPC-H:15–18](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.h#L15-L18>)、[Power-H:55–57](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.h#L55-L57>)。
- FSM relative double seconds使用同一固定session epoch、明确减法/转换精度；frame/command/motor/force/front/now保持同域。不能直接把大绝对ns转double，不能每模块自行置零、用arrival刷新旧source或用单一age替代mean aperture。[FSM-H:44–54](<../SPR_AUDIT/portable_fsm_detector_v1/fd1_detector.h#L44-L54>)。
- MPC PRE_QP余量向下取整为kernel us预算，kernel clock桥有显式diagnostic poison；这不是新硬件时间，kernel budget也不是完整callerdeadline。[MPC-C:20–28](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c#L20-L28>)、[51–54](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c#L51-L54>)。
- **重要实际返回路径：NM1 final clock fault或deadline后仍可`valid=1`返回C3数学fallback，`clock_valid=0`或`deadline_missed=1`同时存在。** 不能按L26局部注释或仅valid推断发送许可；必须检查所有clock/domain/outer permission/完整deadline/源新鲜度。[MPC-C:61–65](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c#L61-L65>)。
- Power重查source valid-until/age、校准域与总elapsed，final poll通过后才写valid，但仍不覆盖返回到driver。[Power-C:134–150](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.c#L134-L150>)、[235–242](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.c#L235-L242>)。
- 仅当统一时钟健康、完整cycle未过期、permission/source/box/证书仍有效时，QP数学失败可选独立fallback继续资格链。时钟失效/全cycle超时不因NM1 fallback valid而发新normal帧；invalidate pending与硬件deadman策略另行绑定，不假装零τ总是安全。

## 8. 状态提交与唯一发送所有权

- NM1在自己的final poll后就提交warm/accepted与last_u；此时Power尚未运行。后续缩放、量化、拒绝或send失败会造成“内部accepted/last_u”和实际held request不同；现有API无external commit/abort/delivered-feedback参数。[MPC-H:24–28](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.h#L24-L28>)、[MPC-C:63–65](<../SPR_AUDIT/NATIVE_C_MPC_SUPERVISOR_V1/nm1_supervisor.c#L63-L65>)。
- context shadow可隔离一次尝试，但不是完整事务/反馈资格。必须分开sensor/health/FSM fault推进与control/MPC动作提交：不能回滚健康/故障来隐藏坏消息，也不能在Power改变动作后直接把MPC shadow当作实际held状态；需明确reconcile/reset/antiwindup/period策略，不直接改library-owned字段假装已有API。
- 真实normal enqueue只归新final owner：绑定最终encoded bytes/坐标/校准和permission generation、frame/session ID、source epochs与expiry；原子copy+deadline/generation再查，失效清所有pending。C3 capture槽与真实queue分别拥有；当前四核没有这层总仲裁。
- C3 uint32 command sequence与Power u64 frame/drive IDs需显式session/rollover合同，不截断后当同一身份。callback“一次”也不证明六轴CAN/双板同步原子应用或单CAN frame。[C3-H:98–111](<../SPR_AUDIT/portable_control_v3_current/pc3_control.h#L98-L111>)、[Power-H:69–72](<../SPR_AUDIT/PORTABLE_POWER_ALLOCATOR_V1/pa1_allocator.h#L69-L72>)。
- enqueue前后及driver实际消费时的deadline/取消/ack/hold语义必须新绑定；任何旧mock enqueue合格结论都不自动覆盖mux最终输出、量化器、两板链路或driver执行。

## 9. 必须新增的合同/接口（均未实现）

| 建议新增层 | 必须解决的当前缺口 |
|---|---|
| candidate snapshot adapter / 可选capture backend | 完整STATE/REF/MATH/GUARDED/内部shaper bundle；同packet drive；source/arrival/estimate/aperture及只读pending生命周期 |
| permission + clock adapter | FSM否决/unknown/default-disable保持；真实normal/contact/operator许可；单ns时基、relative-s/us精度、全cycle deadline、availability与frame generation |
| driver actual-torque preview pair | reserve/request同一snapshot、无双重state污染；实际driver-rate所有PD/D4/gain之后的τ及signed box/reachable speed域 |
| emitted-enclosure certifier / quantizer | 最终F32/CAN bytes及current-tracking load-torque enclosure；无隐藏后clamp；证书绑定真实请求/有效期 |
| proposal commit/abort + held feedback | Power/最终发送之后的实际held command与MPC last_u/warm、P25/driver状态一致；健康fault不回滚 |
| final enqueue owner / board binding | 唯一normal提交、原子expiry/generation/cancel/dedup/ack、两板clock/CAN/driver watchdog与fallback合同 |

**本轮成果仅静态断点与建议合同；未实现上述层，未新增接触许可/校准或完整C3最终enqueue资格。** 读过文件SHA、精确范围与报告行数见[小receipt](<RECEIPT.json>)。
