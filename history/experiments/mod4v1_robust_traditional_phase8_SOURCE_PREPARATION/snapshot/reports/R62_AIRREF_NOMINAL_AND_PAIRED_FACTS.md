# R62空中俯仰参考：名义及固定TRAIN配对事实

名义原gate 2/2；固定TRAIN配对原gate 1/4，baseline同seed 2/4。
配对firstflight main-rear 4/4；与原local gate联合 1/4。改善[]，退化[4610]；DR receipts一致=True。
已保存物理result消耗 4800 controls / 96000 integrator steps；软件错误0，未启动0。未知软件prefix另看原ERROR，不由duration推算。

| case | 原gate | guide/hard ticks | mainfirstflight s | endstable s | maxpitch rad | 失败项 |
|---|---|---:|---:|---:|---:|---|
|r62_airref002_nominal_flat|True|0/0|None|4.5500|0.31964||
|r62_airref002_nominal_rm|True|0/0|2.379999999999962|3.9100|0.29363||
|r62_airref002_paired_RM_DR_4602|True|0/0|2.394999999999967|4.6500|0.23638||
|r62_airref002_paired_RM_DR_4605|False|4/0|2.438999999999982|4.6700|0.20914|guide0|
|r62_airref002_paired_RM_DR_4606|False|0/2|2.2109999999999057|4.3100|0.81373|hard0|
|r62_airref002_paired_RM_DR_4610|False|0/0|2.4945000000000004|3.9900|0.32545|full_collision_final_behind_bar|

配对是看过旧R60 TRAIN结局后的机制对照；不是独立holdout或可靠率证明，未重跑baseline。
保留原FullDR、传感器boxcar→D1→D3、D4/PD/gain/signedDC、闭链和所有contact；未改失败/阈值或扩大main-rear净空为整机净空。
旧H1/H2/H4/H5与Stage1不变；本结果不是270mm、完整RM、自主接触许可、目标板或实机验收。PH8pending。
[结构化逐例事实](<R62_AIRREF_NOMINAL_AND_PAIRED_FACTS.json>)
