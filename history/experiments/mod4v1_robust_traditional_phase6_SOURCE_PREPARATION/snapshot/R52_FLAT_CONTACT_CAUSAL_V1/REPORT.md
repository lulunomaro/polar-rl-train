# R52 flat contact causal audit — offline TRAIN only

原complete800/16000，flat gate=False；guide=7,hard=0；peakmesh=0.18203666098315546m,endstable=4.159999999999956s。未改score/gate。

|event|same-stage time s|rootPRE z m|stage pitch deg|phase|V3 captureweight|guide N|
|---|---:|---:|---:|---|---:|---:|
|first_landing|2.46399999999999|0.2928270791484726|-3.381621917793525|predicted_flight_retract|0.0|0.0|
|first_guide|2.5370000000000146|0.21352558591778945|14.667222195110321|timed_capture|0.10400000000000018|7059.476610012508|
|peak_guide|2.5370000000000146|0.21352558591778945|14.667222195110321|timed_capture|0.10400000000000018|7059.476610012508|
|last_guide|2.5400000000000156|0.21344354285376366|14.629230775224462|timed_capture|0.156249999999999|11.19497675007162|
|capture_control|2.489999999999999|0.25113399055587904|0.22556957173832326|timed_capture|0.0|0.0|
|first_K_ff_ref_weight_positive|2.500000000000002|0.24056976607990205|3.4734150003242767|timed_capture|0.007249999999999697|0.0|
|observer_restore_control|2.640000000000049|0.2572971426031498|-0.0021571328240988447|timed_capture|0.8437499999999994|0.0|

Guide>1N原7个physicsrows，episode=[{'start': 2.5370000000000146, 'ticks': 7, 'peak_N': 7059.476610012508, 'last_post': 2.5405000000000157}]。实际接触面/point/normal见DETAILS的first_guide.contacts，不从target姿态推断。
capture首control=2.49，K/ff/ref插值weight首次>0=2.5；gravity按锁定旧source schedule映射到control=2.49（该flag未独立逐row记录）；observer实际日志首恢复=2.64。
在capture中legacy phase.target_q4可能保留flight target；正确位置参考是landing_position_ref4，变化weight同时对应K/nominalff/ref，本文不把legacy字段当真实currentref。
2kactual单腿q未知：本次不做可选重建。100Hzencoder仅bracket，rootPRE与cachedR/force同stage；rootPOST另time，不能混搭成同瞬间姿态。
只有一个TRAINflat观察，不选predAir/gain、不过拟合、不推断反事实一定成功；RM准入未通过，与其未启动的父decision一致。
读取仅该case smallresult/trace；physics pose仅[2.30,2.75]，外侧仅原guide/hard计数；不读其他case/H5/资产，无279mesh/新physics/Git/agent/真实IO/rawhash。
[DETAILS](<DETAILS.json>) / [receipt](<RECEIPT.json>)。
