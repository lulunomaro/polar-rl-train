# R57：手动里程next-tick触发，paired TRAIN

实际物理result 8/8，完整 8，软件错误 0，未启动 0。原局部gate配对baseline 6/8 → 新候选 6/8。
同8个TRAIN种子，不是16个独立样本、不是新holdout，也没有重跑旧baseline。
DR receipt逐值一致：True；仅用作事后配对核验，未把参数输入控制或消除扰动。

| seed | baseline/new gate | guide旧→新 | decision→push s | firstflight cross s | 失败项 |
|---|---|---:|---|---:|---|
|4501|True/True|0→0|1.96→1.97|2.4074999999999713||
|4502|True/True|0→0|2.0100000000000002→2.02|2.4619999999999895||
|4503|False/True|33→0|1.8900000000000001→1.9000000000000001|2.310499999999939||
|4504|True/False|0→4|2.02→2.0300000000000002|2.4734999999999934|no_guide|
|4505|False/False|3→3|1.92→1.93|2.366999999999958|no_guide|
|4506|True/True|0→0|1.96→1.97|None||
|4507|True/True|0→0|1.97→1.98|2.396999999999968||
|4508|True/True|0→0|1.97→1.98|2.4464999999999844||

首次operational-air内main-rear cross 7/8；同时原局部gate通过 5/8。三个计数不混用。
改善seed=[4503]，退化seed=[4504]；全部原失败保留，不挑最好片段或改阈值。
当前只是手动相对估计里程调度；不是真位置/障碍/接触许可，无新增RAW2K输入。实际float-grid phase以日志为准。
尚非全9m/其他地形/270mm/2mps越障/C跳跃/Power/实机或WCET资格。所有旧H1/H2/H4/H5冻结。PH7pending。
[结构化事实](<R57_POSITION_PAIRED_TRAIN_FACTS.json>)
