# R55：6cm首bar，新全DR TRAIN

固定R54唯一名义局部门槛通过的1.95s方案后，再执行8个未用TRAIN种子4501–4508。原D0–D7、100Hz传感链、2kHz物理与力/几何门槛均保留。

**结果：8/8完整运行，原局部gate 6/8。** 不是独立holdout，也不是全场鲁棒毕业。

| seed | 原局部gate | guide/hard ticks | first-flight主轮rear-cross s | endstable s | 失败项 |
|---|---|---:|---:|---:|---|
|4501|True|0/0|2.4074999999999713|4.3100||
|4502|True|0/0|None|4.4500||
|4503|False|33/0|None|3.6600|no_guide|
|4504|True|0/0|None|4.3700||
|4505|False|3/0|2.367499999999958|3.7300|no_guide|
|4506|True|0/0|None|3.5100||
|4507|True|0/0|2.3779999999999615|4.3200||
|4508|True|0/0|2.46299999999999|4.4600||

## 必须分开的三个计数

- 原首bar局部gate：**6/8**。4503和4505分别有33、3个guide>1N物理采样，仍严格失败；3个采样也未舍入忽略。
- 首次qualified operational-air内主轮mesh后沿越过bar后沿：**4/8**。不是把landing后rebound充首次飞越。
- 同时原gate通过且有上述first-flight cross：**3/8**（4501、4507、4508）。因此6/8不能写成6/8 clean first-flight。

全部8案hard>1N采样0、endstable≥2s、最终全collision包络在首bar后且没有到下bar保守包络。最高mesh离地范围约0.1916–0.2464m，仍非270mm。100Hz endstable不等于每个2k采样连续主轮支撑。

指令接近速度0.9m/s、手动定时起跳、已知局部首bar后停车；不是2m/s越障、自动接触FSM、全9m格栅/其他10类地形或硬件资格。控制为Python V3，不称C跳跃或已接入Power。

原H1/H2/H4/H5及Stage1 V1保持原样；本次8个TRAIN失败均保留，无替换种子或放宽门槛。6400controls/128000新物理步；分析只读小结果，0新步/无大raw重hash。PH7pending。

[结构化事实](<R55_FULLDR_FIRST_BAR_TRAIN_FACTS.json>) · [名义首次飞越事实](<R54_FIRST_FLIGHT_6CM_FACTS.md>)
