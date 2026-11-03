# R59：更高landing平衡profile的同8种子消融

仅替换landing gain spec为既有delta0；K/ff/eq/ref随原V3一起插值，不是纯高度单变量；其余位置触发、时长、guard和driver不变。

实际result 8/8，完整8，软件错误0，未启动0；原局部gate **7/8**。
first-flight main-rear cross **7/8**；同时原gate通过 **6/8**。三个计数不混用。
配对baseline原gate 6/8、联合5/8；改善[4505]、退化[]。同seed DR receipts一致=True。不是新的独立样本，未重跑旧baseline。

| seed | 原局部gate | guide/hard ticks | firstflight cross s | endstable s | 失败项 |
|---|---|---:|---:|---:|---|
|4501|True|0/0|2.4074999999999713|4.6000||
|4502|True|0/0|2.4619999999999895|4.8400||
|4503|True|0/0|2.310499999999939|4.6400||
|4504|False|2/0|2.4734999999999934|4.5800|no_guide|
|4505|True|0/0|2.366999999999958|4.7100||
|4506|True|0/0|None|4.0400||
|4507|True|0/0|2.396999999999968|3.6400||
|4508|True|0/0|2.4464999999999844|4.5800||

全部guide/hard失败原样保留，即使最后恢复稳定；未替换seed或改变阈值。本报告只聚合小result，raw仅producer metadata，0新物理步。
原力阈值/geometry/driver/D0–D7/100Hz sensor链不改；仍是TRAIN、手动相对里程/单bar停车，不是自动接触许可、整场地、270mm或硬件资格。旧H1/H2/H4/H5与Stage1保持。PH7pending。
[结构化事实](<R59_TALL0_PAIRED_TRAIN_FACTS.json>)
