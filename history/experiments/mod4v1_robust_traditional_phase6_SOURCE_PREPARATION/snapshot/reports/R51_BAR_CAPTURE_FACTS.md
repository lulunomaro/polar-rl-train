# R51：提前定时capture的两项名义TRAIN

两项均完成800 controls / 16000 physics，总32000新物理步，原局部gate **0/2**；未改门槛。
| case | air后定时 s | guide ticks | endstable s | peak pitch rad | 原gate失败项 |
|---|---:|---:|---:|---:|---|
|r51_bar_air180|0.18|7|3.430000|0.595195|no_guide, never_reached_nextbar_envelope|
|r51_bar_air250|0.25|11|3.510000|0.593985|no_guide, never_reached_nextbar_envelope|

两案first-flight-only rear-cross均null；这是独立诊断字段，不回溯增添原成功门槛。any-later-air另列，不能称clean firstflight。
nextbar包络失败不单独证明真实力接触，本汇总没有读取R51 physics raw确认身份。
提前capture单项未消除guide。R49已观察push中先碰首bar前上棱、之后才fullair；后续可在新TRAIN研究提前离地，仍保留旧失败，不读取H5调参。
本脚本只读小batch/result，0新物理步、无大raw重hash；PH6pending。
[结构化事实](<R51_BAR_CAPTURE_FACTS.json>)
