# 新静态支撑几何：9指定counterfactual，不是起立/承载证明
实际计数1 compile / 9 total mj_forward（setup 0，public setter内部8+fixture1），0积分/显式RNE/controller/DR/旧QA。初姿pitch由saved wxyz求得0.383686828731rad。
原robot及34碰撞shape不改；compiled mesh vertex支撑/primitive解析极值，仅读同次forward缓存。public轮/guide相位0，fixture保持saved相位；不含contact shell/载荷/稳定性。
|case|假想轮底seating rootZ m|guide minZ/arg m|hard minZ/arg m|COMx−tireMid m|2s peak rad/s|limit合法|
|---|---|---|---|---|---|---|
|INITIAL_SAVED_FIXTURE|0.237139|0.000000/guide_wheel_04|0.031657/chassis_rear|0.219303|0.000000|COMPUTED_LIMITS_INVALID_NO_SILENT_PROJECTION|
|NOMINAL_Q_PITCH0|0.334394|0.156394/guide_wheel_03|0.051218/left_shin_collision|-0.000000|0.728381|COMPUTED_LIMITS_VALID|
|NOMINAL_Q_PITCH_INIT|0.302594|0.065455/guide_wheel_06|0.051691/left_shin_collision|0.072896|0.728381|COMPUTED_LIMITS_VALID|
|NOMINAL_Q_PITCH_0p60|0.268449|-0.004214/guide_wheel_06|0.023297/chassis_rear|0.109954|0.728381|COMPUTED_LIMITS_VALID|
|PUBLIC_DELTA20_Q_PITCH0|0.366144|0.188144/guide_wheel_03|0.051439/right_shin_collision|-0.000000|0.653872|COMPUTED_LIMITS_VALID|
|PUBLIC_DELTA20_Q_PITCH_INIT|0.332136|0.094997/guide_wheel_06|0.051669/left_shin_collision|0.082539|0.653872|COMPUTED_LIMITS_VALID|
|PUBLIC_DELTA20_Q_PITCH_0p60|0.295082|0.022419/guide_wheel_06|0.049930/chassis_rear|0.124499|0.653872|COMPUTED_LIMITS_VALID|
|PUBLIC_DELTA20_COMMON_PLUS_INIT_PITCH_AT_INIT_PITCH|0.258514|0.021375/guide_wheel_06|0.051325/left_shin_collision|0.161519|0.294166|COMPUTED_LIMITS_VALID|
|PUBLIC_DELTA20_COMMON_MINUS_INIT_PITCH_AT_INIT_PITCH|0.366144|0.129005/guide_wheel_06|0.051439/left_shin_collision|-0.012418|1.013579|COMPUTED_LIMITS_VALID|
最低主轮minZ的common dz只解析平移缓存，不再forward/改data；左右轮剩余gap另存，非强迫两轮同时承载。COMx相对cached tire geom-origin midpoint，另列wheel-axle参考，不是支撑多边形证书。
完整all-joint/driver边界、6对closure/mimic残差、q/phase/per-geom/2s速度在数值JSON。初姿实际软限越界原样记录，不投影测量；reference-only投影与其delta另列。速度仅端点quintic max，不证中间闭链/碰撞/driver可达。
正guide/hard间隙≠真实卸载或站稳；负值是该轮底放平假想姿态的几何干涉，不等于观测到真实接触力。不同pitch/δ/common shift仅诊断，不选V4目标/gain/时间。
[METHOD](<METHOD.json>) · [source锁](<SOURCE_PREEXEC.json>) · [9行数值](<RESULT.json>)。旧fixture/gate/模型/分数不改；当前PH10cutoff外新研究，后续controller/PHY须另批。
