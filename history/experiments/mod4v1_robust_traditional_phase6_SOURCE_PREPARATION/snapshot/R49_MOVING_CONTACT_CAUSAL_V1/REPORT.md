# R49 moving-contact causal diagnostic (singleTRAINcase, PH6pending)

可选2k activehinge推导验证：800个100Hz同sensor epoch ×4轴，maxerror=0rad，预声明1e-9，accepted=True。负对照前一stage速度积分error=0.0044799797rad。
仅条件NEWderived-grade，非原始2kq测量；nominalTrue无D1/D2，source implicitfast/无runtime hinge写；旧R45unknown与所有旧分数不变。

实际trace phase switches见DETAILS；gravity首恢复control=2.6s，wheel/ground首恢复=2.74s。
|event|stage s|pitch deg|rootPRE z m|FK BODYdrop m|FK worlddrop m|guide N|
|---|---:|---:|---:|---:|---:|---:|
|first_main_firstbar|2.130999999999879|0.23885985491216957|0.2552343400255184|0.19169209853520078|0.1915471182282556|0.0|
|first_landing|2.4955000000000007|33.63565262920356|0.29270842326399815|0.22482337838575622|0.16248522253960296|0.0|
|first_guide|2.5070000000000046|34.633714556916594|0.2763194151873079|0.21556390676357637|0.1527017457958122|11693.220396572167|
|last_guide|2.5100000000000056|34.08618679507332|0.2747248758079063|0.2116683421155499|0.15052571630464648|17.89276996796454|
|rear_cross_in_later_air|2.604500000000037|24.621816476145522|0.2602125603219563|0.21320789483591304|0.1771301308709765|0.0|
|first_nextbar|3.762500000000424|-13.394260398177773|0.30331531037985177|0.23832835520058596|0.23975267646801007|0.0|

guide共7个physics rows（不是point数），nextbar总法向>1N 137rows。guide6→ground，firstlanding右轮→firstbar上表面，而非同一个接触/主轮支撑。
首次guide早于capture/gravity与observer恢复；因此该初次guide不由这些重启触发。仍是观察到的时序，不证明唯一机理。
rear-cross=2.604500000000037s在firstlanding=2.4955000000000007s后，rebound而非firstflight：{'air_qualified': True, 'all_world_normal_N': 0.0, 'air_run_s': 0.025500000000000002, 'after_first_landing_s': 0.1090000000000364}。
phase/target与实际stageq区分；姿态R与rootPRE同stage，postroot另有time不混用。FK passive约束是public名义闭链，不是全部实际2k关节测量，几何不能取代实测contactforce。
原localgate=False，不改分数、不以guide支持充主轮支持，不以rebound rear-cross冒cleanfirstflight。

仅3个关键时间窗口，无279mesh重建/无新gain/无H5数据/无新physics/Git/agent/真实IO；producerSHA引用，无为归档raw重hash。
[DETAILS](<DETAILS.json>) / [预声明](<METHOD_PREDECLARED.md>) / [收据](<RECEIPT.json>)。
