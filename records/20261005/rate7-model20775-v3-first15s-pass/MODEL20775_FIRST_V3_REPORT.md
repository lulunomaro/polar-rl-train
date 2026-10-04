# 20775新版本第一份真实15秒验收

精确正式model20775 SHA 0d0477bb311524f1e55fbfd79b44ff79df3958186d08ed4f467a90165f1e0cad，CPU actor/critic/optimizer/std/iter共68浮点完整有限。auto0087真实flat80env及spin88env各1500步15秒已经完成，新验收v3两者通过。原文件名仍含scut_style_v2，decision实际acceptance_version是v3。flat64已训练环境全部原非滑移准入通过；spin88/88存活、physical true、11组各8/8，严重个体否决为空，实际参数/完整接触数据通过。

纯+7平均实测yaw 6.981622、纯-7 -7.016723rad/s；两组每环境平均世界XY速范围分别 [0.11908619850873947, 0.1252574473619461]、[0.11432851105928421, 0.11930785328149796]m/s，只诊断。纯±7最坏peaktilt 3.286106deg，gap 1.194075mm，双轮低载 11.500ms。按交错group_ids逐环境检查，均值不冒充瞬时峰或世界净漂移。

原v2技能 False、mesh False、legacy False、loaded015 False布尔与原raw完整保留。新通过来自已授权验收语义变更，不能说原.12/.15规则毕业或滑移已修好。flat与spin不同seed协议并非配对；后续同20775两个seed nominal/white各flat/spin八份精确初态/参数配对继续，全部通过才7成熟并尝试8。此次只读取既有报告，没有额外probe/PPO或新预算。
