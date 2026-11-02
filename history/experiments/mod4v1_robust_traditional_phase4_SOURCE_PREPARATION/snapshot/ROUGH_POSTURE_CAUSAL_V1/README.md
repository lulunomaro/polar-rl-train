# Rough Posture Causal v1 — R22existing TRAIN, no new physics

**主要观察：delta0/.2/.4确实抬高nominal几何，但首非轮bin前已出现显著pitch。此时BODY腿竖直drop并未缩短，而旋转到world的竖直投影损失约7–12cm，压过增加高度收益。更高固定腿姿四案后来因upright<.45结束；不是闭链先坏。**

## 精简因果表

shape loss定义target BODYdrop−observed encoderFK BODYdrop，负值代表观察姿态在BODY反而更长。projection loss定义BODYdrop−post-truth旋转后的world竖直drop。sensorq与postroot姿态相差一个控制interval，数值为近似分解，不是瞬时完整truth姿态。

|case|target level rootZ m|first非轮bin s|rootZ m|pitch deg|shape loss mm|projection loss mm|progress m|stop|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|r22_height0bar40|0.334876|4.750–4.760|0.284417|38.481|-18.401|86.259|6.121980|complete|
|r22_height0bar60|0.334876|2.680–2.690|0.275384|35.556|-12.757|72.201|2.816321|complete|
|r22_height20bar40|0.366405|4.580–4.590|0.283297|39.405|-9.541|94.103|4.483151|health|
|r22_height20bar60|0.366405|2.680–2.690|0.285015|40.021|-10.236|96.895|2.626646|health|
|r22_height40bar40|0.396124|4.660–4.670|0.290096|42.415|-5.465|111.938|4.488685|health|
|r22_height40bar60|0.396124|2.700–2.710|0.290373|42.863|-8.791|115.536|2.624288|health|

[CASE表](<CASE_CAUSAL_TABLE.json>)与[完整analysis](<analysis_attempts/001/output/RESULT.json>)给角度、腿几何、wheel速度/τ、health及每个关键时刻8root-body box包络。

## 几何与事件顺序

nominal delta0/.2/.4：leg planar长度.273242/.304462/.333924m，upright root高.334876/.366405/.396124m。所有8个rootbodyrigidbox中最低belly对6cm顶面净距107.876/139.405/169.124mm，故不能声称uprightnominal也必然chassis碰6cm。此几何并未保证guide/link/tire或动态转移可通过。

首nonwheel20stepbin之前：pitch已达35–43deg；wheel endstep曾达5.7759Nm峰限；腿绝对角误差曾超过.05rad。但“角误差”不等于“腿回缩”，数据反而显示BODYdrop增大。控制器固定4输出角，没直接控制worldrootZ。

较高四案terminal upright_cos=.423–.448<.45，closure约3e−7m/mimic约1e−6rad，未触原.01门槛。低姿两案complete但rough未过；停住/尾速小/完成不能变成通过。

wheel mean约53.8–53.9rad/s与endstepτ约.77–.79Nm，对55.3557nominal no-load的同向DC motoring limit下降一致。原clip是SIGNED，逆向制动力矩不等于同向motor能力；这里mean速度与最后stepτ不同时间，2k峰值/饱和占比未保存，不能精确重建。

## R30证据与身份边界

另四个R30existing小报告保留在analysis里：6cm原模型tire/bar0112.564s→chassis_core/bar0112.680s、force12780.99N，随后guideground。它说明实际动态bodyblocker机制，但不能倒填成R22每案的第一身份。R22只有aggregate非轮pair/point ticks每20step，不是去重physicsstep。

稀疏解析SAT只表示指定postrootpose下某rootbox与已存barbox几何候选；没重跑collision/force、没279mesh逐tick、没2k事件。postframe无overlap不证明bin内无接触；全部命名未知照留。真实fullassetCAD/所有11family或PhysX equivalence仍不在该tiny_step数据中。

## 下一最小可检验动作（未执行）

[策略假设](<STRATEGY_HYPOTHESES.json>)建议先在同6cm/model/contact/gainbank下比较：在bar加载/轮motorheadroom耗尽前，用真实IMU/encoder允许的pitch/foreaft参考轨迹保住world投影与动态reserve；不是继续只抬delta，也不是笼统更慢或删碰撞。固定target完全竖直/零pitch也可能消掉必要爬阶lean，必须同时看progress/轮bar转移/非轮与health顺序。高度改变同时重算DAREgain是confounder，不冒纯几何因果试验。

所有GT只用于离线grading；不输出在线truth控制、rootassist或新物理。旧trace仅为本次授权因果分析流读，producerSHA沿用，不为归档重hash大raw。H1/H2/H4未读作选择。[初步表](<INTERIM.json>)此前已交父，最终证据更正必须以本表为准。

## Source/验证

[scope](<SCOPE.md>)、[执行源码](<causal_analysis.py>)、[执行前sourceSHA/保护旧源](<analysis_attempts/001/VALIDATION.json>)、[reader事件](<READER_EVENTS.json>)、[边界](<EVIDENCE_BOUNDARIES.json>)、[INDEX](<INDEX.json>)。0physics/SDK/Git/GPU/newagent/真实IO，全部PH4pending。RAW2K任务只在此rough交付后另新目录做。
