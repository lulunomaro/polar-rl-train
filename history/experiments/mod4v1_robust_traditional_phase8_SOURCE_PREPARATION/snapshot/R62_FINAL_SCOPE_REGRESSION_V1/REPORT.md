# R62 seed4610 final-scope regression：仅small result/offline

| 指标 | R60 baseline | R62 AIRref |
|---|---:|---:|
|原main/local gate|False/True|False/False|
|guide/hard ticks|0/0|0/0|
|endstable s|4.009999999999959|3.989999999999959|
|mainfirstflightrear s|2.4945000000000004|2.4945000000000004|
|root POST x/y/z m|[2.264746806334247, 0.07138709116334307, 0.33072299378611986]|[2.2268677453554955, 0.056139515567338046, 0.3307500843155355]|
|root POST yaw/pitch/roll rad|[-0.05900911532058635, 0.010266668689624532, 0.001006043646567763]|[-0.01824745369039767, 0.009616457688125227, 0.0015065008945757388]|
|body velocity POST B m/s|[-0.0019399159566892267, 0.009363735763826658, -0.005899018521797607]|[-0.001843770153583599, 0.00806709912812929, -0.0057922424789236355]|
|compiled-sphere minX m|1.8663830929796186|1.828106759617952|
|minX−firstbarback m|0.02936064826260454|-0.008915685099061932|
|exact main-rear−barback m|0.3164770752726098|0.287863580588549|

相同firstbar011 backX=1.837022444717014m。新root实际progress=2.0268677453554953m，而root POST x=2.2268677453554955，不要混用progress与全机器人minX。原local唯一新增失败是final-full-collision-bound-behind；nextbar未到达仍True。

新bound minX比旧少38.276333mm，root POST x少37.879061mm；rootPOST−boundminX offset只多0.397272mm。这是保存数值的算术分解，不是相同tick的真实后伸长度或导致停止的控制机制；source bounds时钟=7.999499999998286，rootPOST=7.999999999998286，相差约.5ms。

**保守证书失败≠实测bar接触或真实mesh重叠。** source只对34个collision geom的compiledrbound+1e−8球求union AABB，非碰撞shape或方向精确全mesh。旧margin+29.360648mm，新−8.915685mm，只证明原保守whole-robot-behind门槛未通过；并不能证明真实shape已过/未过。argmin geom未存，不猜是chassis/guide，不把近似界解释为实际姿态故障。finalpitch约.01rad，两案rootZ差仅2.7090529415629838e-05m，但这也不证明相同完整关节/mesh姿态。

保留原localFalse与全部gate，不放宽/改分、不选gain或新目标。未读任何raw/trace/H5/mesh/模型/QA/新PHY/Git/newagent；仅两个result、新report和grade_rows源。其他agent独立trace解释不在本任务。细值/时钟/sourceSHA见[FACTS](<FACTS.json>)、[receipt](<RECEIPT.json>)。PH8pending。
