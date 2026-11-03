# R54：首次取得名义6cm首bar的first-flight通过

全几何与原力阈值/guard/gate保留。4项新名义试验均800controls/16000steps，总64000新物理步；flat **2/2**，RM局部 **1/2**。不是全DR成功率。
| case | gate | guide/hard ticks | first-flight rear-cross s | endstable s | 失败项 |
|---|---|---:|---:|---:|---|
|r54_t190_flat|True|0/0|None|3.6600||
|r54_t195_flat|True|0/0|None|3.6900||
|r54_t190_rm|False|0/0|None|3.5800|never_nextbar_envelope|
|r54_t195_rm|True|0/0|2.382499999999963|3.6700||

1.95s方案：主轮mesh后沿在2.3825s的qualified operational-air中越过首bar后沿，早于firstlanding；最终全collision保守包络在bar之后，且全程未到下bar包络。guide/hard均0，endstable3.67s。
1.90s方案虽guide/hard0且最终过bar，但nextbar保守包络失败，仍记失败；未仅凭保守包络推断实际nextbar力接触。
这里的clean first-flight限定为上述主轮mesh＋原operational-air定义，非全机瞬间包络、真实零力或硬件冲击认证。峰mesh离地约0.183m，不是270mm。
仅新TRAIN、Python控制路径、手动定时首bar局部；H1/H2/H4/H5和Stage1 V1未改。后续新全DR TRAIN独立保存，不据名义宣称鲁棒毕业。
PH6严格截止R53，R54属于PH7pending；保留执行时旧provisional字段原样。
[结构化事实](<R54_FIRST_FLIGHT_6CM_FACTS.json>)
