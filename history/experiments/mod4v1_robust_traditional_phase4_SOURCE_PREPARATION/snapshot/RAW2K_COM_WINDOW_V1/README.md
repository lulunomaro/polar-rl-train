# RAW2K COM Window v1 — 可观察离散functional，不冒continuous真值

**13/13新synthetic/SO3/analytic-bin/prefix/时序/allowlist单测首轮通过；6条sensor-onlyprojection全部SHA/bytes/frames核验。3200frames、63848samples，sourceSeq去重63846，另排除6instantboot后63840steady2k points。0新physics/Git/GPU/newagent/真实IO，PH4pending。**

## 先给正确结论

2k path现在确实可见，用真实同时间raw q/qd/gyro/proper端点得到有限窗口离散functional；它与100Hzmean constantbin近似在动态段有可见差别。**差值不是连续trueCOM误差，不是新branch比旧benchmark真实更准的证明。** R38无独立2kworldCOM/contacttruth，sub-.5ms motion/covariance/quadrature仍无保证，continuous radius=None，所有trusted cue UNKNOWN，cap.50/冻结.60门槛不改。

## 每case/窗口

paired delta=两个noisy-sensor离散近似的vector差norm；radius仅对新discrete functional在声明noise/model假设下计算。不是硬件误差/概率。

|case|T ms|数值窗口|平均量age p50 ms|paired delta p95 m/s²|max delta|discrete radius p50|可信cue|
|---|---:|---:|---:|---:|---:|---:|---:|
|C0|50|194|25.5|0.000160|0.004032|3.720439|0|
|C0|100|189|50.5|0.000110|0.002069|2.152572|0|
|C0|150|184|75.5|0.000084|0.001382|1.665362|0|
|C1|50|594|25.5|0.270889|0.419123|4.355770|0|
|C1|100|589|50.5|0.136046|0.209159|2.473717|0|
|C1|150|584|75.5|0.090964|0.136958|1.891231|0|
|C2|50|594|25.5|0.266818|0.497142|4.435346|0|
|C2|100|589|50.5|0.133804|0.240283|2.517423|0|
|C2|150|584|75.5|0.091110|0.166444|1.919852|0|
|C3|50|594|25.5|0.269540|0.779472|4.431814|0|
|C3|100|589|50.5|0.133224|0.393174|2.524907|0|
|C3|150|584|75.5|0.088619|0.260174|1.919951|0|
|C4|50|593|35.5|0.285142|0.472129|4.474753|0|
|C4|100|588|60.5|0.147618|0.251321|2.540693|0|
|C4|150|583|85.5|0.098815|0.166711|1.932331|0|
|C5|50|593|35.5|0.304463|0.480664|4.472341|0|
|C5|100|588|60.5|0.149854|0.236906|2.539054|0|
|C5|150|583|85.5|0.100823|0.162523|1.939106|0|

[完整表](<CASE_WINDOW_TABLE.json>)及[六案summary](<attempts/001/shadow/SUMMARY.json>)保留mean/raw mean roundoff、boot/duplicate/clock和区间细节。高度重叠窗口不是独立case，也不是qualify次数。

## 定义：同时间raw边界，不混旧epoch点

在500us pre-step采样点上，q/qd/gyro/proper相同timestamp。估计器用末条raw时间`sourceEpoch−500us`作为window_end，起点恰早50/100/150ms，端点u只用该两个raw sample：

```text
u = omega×(rCOM(q)−sIMU) + J(q)*qd + nominalWheelPhaseTerm
R_(i+1)=R_i exp([gyro_i]h)
I_(i+1)=I_i + R_i [integral_0^h exp([gyro_i]t)dt] fIMU_i
window_specific_force = I_window/T + (Rrel_end*u_end-u_start)/T
```

每sample constant-bin transport用解析SO3指数积分；prefix只为O(1)取任意窗口，relativewindow-start R=I，不用worldyaw/姿态。没有alpha/qdd差分、没有加g。此定义是**piecewise-held noisy sampled functional**，不是“sampled值等于连续实际trajectory”的断言。

原packet的endpoint_joint_pos4在sourceEpoch，比末raw晚.5ms，不会和旧mean qd/gyro拼成伪同步端点。window average年龄=T/2+arrival−lastRaw，所以nominal25.5/50.5/75.5ms；观测到10msqueue时35.5/60.5/85.5ms。重复sourceSeq不重积分、不赚持续窗，bootinstant单独丢弃；gap不插值凑窗口。

## 旧mean近似如何公平比较

使用原authoritative100Hzmean gyro/proper，在其原窗口support内作constant-bin model；但截取与rawfunctional**完全相同的t0/t1和同一rawu端点**。首/尾mean bin可能仅部分overlap，避免把错时端点误差混入transport比较。它不是旧epoch-endpoint策略的byte-replay，也没读取旧controller输出/原trace。比较的不同来自noisyraw intrawindow信息与mean模型差，不能拿它当连续物理精度。

## 保留的误差与未获得的资格

- 新原始资料同window共用D1offset，是information-enhancement/correlated-noise新branch，不是IID2k；噪声预算不除sqrt20或窗口N，gyro drift/model端点界不凭空相消。
- 仅因raw端点确有同时间采集，取消旧mean endpoint5.25ms错时项；PUBLICnoise/encoderzero allowance、nominalMCI/J/lever、missingwheelphase界都保留，不把少一个时间误差项当校准。
- 新窗口radius是**discrete functional**条件budget。未知sub-.5ms变化/gyro-proper关联/真实模型误差的continuous quadrature不能伪造成严格硬件球；因此continuous radius始终unknown，不集成FSM/actuation。
- authoritative均值与旧packet一致是producer声明；本consumer不读完整packettrace去重验。只核投影内部raw重算mean，roundoff最大约2.13e−14，非bitidentical；不把数值微差/均值同值叫同难度benchmark。
- 真COM/netforce可能不同：所有model及D0相关误差保持unbound/条件标签，未读DRreceipt逆算取消它们。净力窗口cue也不识别接触身份/全表面air。

## 证据/后续

[scope/functional](<SCOPE_AND_FUNCTIONAL.md>)、[runtime](<raw_functional.py>)、[shadow](<shadow_cases.py>)、[新tests](<test_raw_functional.py>)、[run RESULT/sourceSHA](<attempts/001/RESULT.json>)、[原unit log](<attempts/001/unittest.log>)、[frame时钟审计](<FRAME_CLOCK_AUDIT.json>)、[source/result/derivedproducer索引](<SOURCE_RESULT_INDEX.json>)、[validation](<VALIDATION.json>)、[INDEX](<INDEX.json>)。

[未来动态验证要求](<FUTURE_VALIDATION_REQUIREMENTS.md>)只列独立spin/jump/movingleg/guide支承及私有highrate truthgrade的需求，未新physics/改父publisher。原100Hz controller没使用这些raw作actuation，旧rough/COM/CONTACT和封存source保护SHA均不变。全部新结果PH4pending，整体Goal继续active。
