# COM Sensor Capture Audit v1 — sensor-only shadow applicability

**4400projection rows完整核验，14/14边界/allowlist/数学单测首次通过；0physics/Git/newagent/真实IO。严格分支与条件分支的可信cue均为0，保留UNCERTAIN，没有为通过FSM门槛删掉边界或抬高置信。**

## 逐case结果

“有界”只表示显式synthetic/window/model误差假设下可算局部工程radius，不是硬件可用率或准确率。

|case|rows|重复epoch|条件数值/有界行（全row分母）|radius p50 / p95 m/s²|可信cue|
|---|---:|---:|---:|---:|---:|
|r29_C_MATH_TAU_stand_0|800|0|798/800 (99.750%)|12.165994 / 12.169260|0|
|r29_C_MATH_TAU_forward_0|1200|0|1198/1200 (99.833%)|12.171430 / 12.237361|0|
|r31_C_MATH_TAU_forward_101|1200|1|1197/1200 (99.750%)|12.296155 / 12.384910|0|
|r31_C_MATH_TAU_forward_102|1200|1|1197/1200 (99.750%)|12.338946 / 12.429660|0|

严格unbound分支：4400/4400 UNCERTAIN，usable vector/cue0。条件分支共4390/4400数值/有界行（99.773%），但radius约12.16–12.53m/s²；冻结threshold不改、声明input confidence最多.50低于COM默认.60。即使忽略置信门，也没有把这些宽区间叫成可靠freefall/nonfreefall。被排除10行是4boot instant、4首次mean边界及2重复首包；不是删掉“不好看”的运动样本。

## 证据与入口

- [Scope](<SCOPE.md>)；[实现](<shadow_audit.py>)；[14单测](<test_shadow.py>)；[append-only runner](<run_audit.py>)。
- [本次RESULT/sourceSHA](<attempts/001/RESULT.json>)、[原样unit log](<attempts/001/unittest.log>)、[完整逐case summary](<attempts/001/audit/SUMMARY.json>)。
- [逐row derived输出manifest/producerSHA](<DERIVED_OUTPUT_MANIFEST.json>)、[冻结V4 baseline对照](<FROZEN_BASELINE_COMPARISON.json>)。
- [显式假设](<ASSUMPTIONS.json>)、[最小真实采集绑定](<MINIMUM_CAPTURE_BINDINGS.json>)、[validation](<VALIDATION.json>)、[完整index](<INDEX.json>)。

只读父SENSOR_CAPTURE_CLOOP_V1 manifest及四个*_sensor_only projections，原case仅引用sourceSHA。验证每个projection producerSHA/bytes/rowcount、top+nested严格allowlist；drive6速度逐项等于4joint dq＋2wheel spin拼接。没有打开完整原trace、episode DRreceipt、root/contact/真姿态/envelope。源码/依赖HASH保护均未变，旧DYNAMIC_COM/CONTACT/FSM/PH2保持封存。

## 真实时钟/窗口结论

- epoch t时gyro/proper/qd是20×.5ms窗口[t−.010,t−.0005]均值，支撑span9.5ms、center=t−5.25ms；q4仍是endepoch值。coherent/sharedqueueepoch仅是队列声明，**不证明瞬时同步**。
- 无queue年龄的nominal case：mean center已比arrival旧5.25ms，相邻mean差分名义center旧10.25ms；DR101/102观察到queue年龄10ms，则分别15.25/20.25ms。没有把观测队列年龄反解为episode参数。
- frozenV4纯sensor-math replay给sampleomega/alphaLP/properRoot作baseline，alpha60ms LP稳态effective age约70.25ms（nominal）/80.25ms（上述队列延迟），不是当前瞬时alpha。boot初始alpha0先验及instant→mean过渡另标，不赚新可靠样本。
- instant→mean直接重置新分支差分历史；重复首包不更新alpha/qdd或持续窗。全部逐row输出保留。

## 条件分支具体做了什么

目标选current window center，不冒epoch瞬时。用二阶模型`q_center=q_end-v_mean*5.25ms-.5*a_fd*(5.25ms)^2`对齐q；qdd/alpha从相邻mean-center采集时差求差分，但名义导数时间仍比targetcenter早5ms。20point均值＋差分kernel对current center的E|lag|=5.415625ms，只有显式jerk假设才可传播时间误差。

相同PUBLIC D1半宽用于全部4cases：gyro.125rad/s、q.005rad、qd.25rad/s、wheelqd.5rad/s；gravity3.025dimensionless映射proper乘9.81只是明示benchmark假设。D1是100Hz每feedback量加噪再D3排队，**没有将噪声÷20或÷sqrt20**。不按case的nominal/DR标签推回真实噪声开关、不读取D0–D7receipt。

示例声明jerk q1000rad/s³、angular200rad/s³时，每轴qdd error约55.415625rad/s²、alpha约26.083125rad/s²；另有proper curvature/lever误差、未验证零点allowance与冻结COM model-error scale。它们是可见的工程假设，不是硬件校准，也不是保证涵盖所有模型/高阶曲率/柔顺变化的全局区间。

proper atIMU先按origin→IMU lever(.03,0,.04)做`properRoot=properIMU-alpha×lever-omega×(omega×lever)`；lever与alpha误差也进预算，再调用未改的movingCOM全项补偿。wheel无phase按冻结模块完整圆周几何缺项界，rate/acc只用projection纯encoder及明示差分误差，不假balancedwheel。

## 适用性结论与最小补齐

新projection修好了旧R16“没有采集stamp/raw q tuple”的缺口；现在能检查采集/到达/epoch/重复与窗口。**它仍未建立可靠当前qdd/alpha和COM-cue绑定**：均值aperture、q异时、差分中点和60ms LP都仍存在，PUBLIC模拟噪声范围更不等于实机标定。数值可算率99.8%不等于可信cue可用率。

最小下一步是绑定每路真实aperture/采集/到达及滤波延迟，encoder零点/速估计噪声，IMUlever/方向与alpha有效时间；要么提供同时间的instant传感器和校准导数，要么保留同window语义并提供有依据的运动/协方差/jerk界。旧冻结H1/H2不改，真值grading仍由父独立进行，不用真值来补这个shadow。

本目录及所有derived reports均PH3pending；没有重record PH2或执行新物理。整体Goal继续active。
