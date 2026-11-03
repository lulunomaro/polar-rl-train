# R61：自转停止门控的单因素TRAIN结果

真实新实验3/3完整（1名义+2配对DR），7800controls/156000物理步；**原composite仍0/3（全DR0/2）**。没有把完成执行或部分相位改善当技能通过。
只保持centering至previous commanded shaper归零，旧K/observer/roll/torque cap/driver与所有评价窗不变；旧baseline未重跑，只读小result比较。

|seed|old→new最终XY m|old→new final-stop v RMS|新first/final stop s|原wholecase失败项|
|---|---:|---:|---|---|
|0|0.053797→0.284652|0.008939→0.023206|None / 2.2899999999875753|w_tracking_RMS_strict|
|201|0.347337→0.076392|0.037740→0.029648|2.2400000000040787 / 2.499999999987086|w_tracking_RMS_strict|
|202|1.503513→0.844841|0.505538→0.421364|2.0900000000038954 / None|v_tracking_RMS_lt_0p15,w_tracking_RMS_strict|

名义first_stop最长0.49s<0.50s，继续记失败；201虽然两个stop相位均取得>=0.5s hold，仍未过原wholecase screen；202最后停止未取得hold且XY>.3m。没有删除wholecase gate或放宽yaw跟踪阈值。
两DR首次stop前positive phase保存指标与旧值精确相同=True；DR receipt逐值相同=True。不是逐2k物理state位证明；旧heldout未作选择/改分。
实际centering保留区间/previous-current shaper与严格wholecase失败项详JSON；这些是command状态，不是测得已停止/触地。新trace各单pass、无旧raw/资产归档重hash、0新分析物理步。
结论：门控可改善部分停止指标，但该单因素不足完成停启换向；201/202是旧TRAIN配对，不是新的独立鲁棒性样本。新候选保持实验默认off，PH7pending。
[结构化证据](<R61_SPIN_DECEL_GATE_FACTS.json>)
