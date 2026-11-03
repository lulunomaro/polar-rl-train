# V3B单次控制trace事实诊断（非起立成功）
原完整case状态complete=False, stop=controller_fault, fault=recovery encoder rotation travel exceeds0.50m; 298controls/5960PHY，originalgateFalse，未重跑。
首次eligible/对准control=2.31/2.31s；首次logged软限速替换=2.45s；BALANCE=None。
|control s/事件|phase|est pitch/rate|POST true pitch/rate|proxy m / PRE XY m|packet wheel rad/s|requested wheel Nm|q-ref max rad|support minN2 / noOther|
|---|---|---|---|---|---|---|---|---|
|0.00 / initial|OBSERVE|0.450373/-0.00108494|0.383685/0.000652095|0/0|[-0.06268584530245479, -0.0626953980155818]|[0.0, 0.0]|3.36626e-07|[36.188782926146516, 36.19765183130205] / False|
|0.31 / first_SHAPE|SHAPE_TO_STAND|0.440511/-2.84893e-06|0.38368/-6.89306e-06|0/2.07138e-05|[0.00037037626920655283, -5.202690366355227e-06]|[-0.00011111288076196585, 1.5608071099065681e-06]|3.49161e-07|[38.289970030959, 39.07234937001688] / False|
|2.30 / pre_first_eligible|SHAPE_TO_STAND|0.613992/0.00286946|0.608467/0.00337062|0.0265187/0.102028|[-0.004893514163692399, -0.00489396452422799]|[0.0014680542491077196, 0.001468189357268397]|0.0698583|[44.07773419278767, 44.16802785569435] / False|
|2.31 / first_eligible,first_alignment_latch,first_aligned_already_braking_request_not_replaced|VERIFY|0.614006/0.00318076|0.60825/-0.0397707|0.0265233/0.102008|[-0.007315539867310035, -0.007315990672702095]|[3.0, 3.0]|0.0699184|[0.0, 0.0] / False|
|2.45 / first_logged_soft_overspeed_replacement,first_proxy_ge_0p10|VERIFY|0.554294/-0.643306|0.544167/-0.394486|0.100679/0.0676364|[12.67754624409989, 12.67469092623773]|[-0.203263873229967, -0.202407277871319]|0.0250575|[0.0, 0.0] / True|
|2.65 / first_proxy_ge_0p25|VERIFY|0.608968/0.433435|0.609098/0.586988|0.251864/0.11809|[12.108045122532122, 12.103533804756513]|[-0.03241353675963658, -0.03106014142695379]|0.0534894|[0.0, 0.0] / False|
|2.96 / penultimate|VERIFY|0.604639/-0.0188436|0.59986/0.0243568|0.493591/0.346749|[12.097396236802217, 12.118066762114994]|[-0.029218871040665027, -0.0354200286344982]|0.0391806|[0.0, 0.0] / False|
|2.97 / first_proxy_gt_0p50,terminal|INHIBIT|0.604541/-0.000355428|0.601442/0.246767|0.500546/0.354421|[11.147493411242234, 11.10990605817469]|[0.0, 0.0]|UNKNOWN|[0.0, 0.0] / False|
对准起至终段POST true |pitch|min/max=0.5355244551076976/0.6298966186586855rad；<.15rad rows=0；仍未BLEND/BALANCE。末Z=0.2729324744757128m，gain=0.03579377042510551m，不等于直立。
原proxy strict>.50触发，末proxy=0.5005464977251093m，PRE true XY净位移=0.3544212729067335m，POST/max净位移=0.36250708650489405m<.5；绝对轮转代理与真XY净位移/历程非同量，epoch亦不同，不据此证明打滑或真实越界。
软限速事件来自控制日志；already-braking是请求对packet轮速反向且无soft replacement，不是实际driver力矩。只报告requested，2k实际τ/速度未读、UNKNOWN；不唯一归因摩擦/clip。
current_reference缺失的INHIBIT保留UNKNOWN；last_published_reference另标时刻，private POST joint-target error是不同量。main mean/min和noOther系原writer的20×2k采样统计，未重建contact identity；POST pitchrate仅由记录gyro/roll代数换算。
本脚本一open/298rows、事件8<=12；physics/旧Araw/rawhash/model/FK/PHY/旧QA/Git/agent0。原源码/guard/gate/score不改，计数不声称全会话别人未读。
[READ_COUNTS](<READ_COUNTS.json>) · [EVENTS](<EVENTS.json>) · [METHOD](<METHOD.json>)；V4另提最小方法，不调参、不执行。PH10pending。
