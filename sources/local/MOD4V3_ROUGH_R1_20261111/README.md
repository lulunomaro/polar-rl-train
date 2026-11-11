# R1首轮40分钟

2026-11-11用户授权“开始推进r1 40分钟”。父Flat1.5_020m，iter22856，SHA`a5102af62938f6bf472855edba34c5f10efce061eecaeb3aebee34815fe7cf87`，完整PPO/globalRNG恢复，新物理episode、本地课程level0。

只推进R1地形及其低到高指令课程；速度平方项保持−1.5e²、指数1.2，fullDR/PPO/35/78/6/2.5-10-20ms/TGS32/4/2mm单env重置保留。4096env，名义平地164/名义Rough655/DR平地655/DRRough2622。

新增中级正反阶梯25–40mm；原栅格10–30mm、坡度.05–.15、浅阶梯5–15mm、随机起伏0–30mm。四难度行70列9m；低难度level0起，按能力升降。Rough行进上限按level为1.0/1.25/1.5/2.2m/s，采样60%直行/20%缓转/20%低速旋转，平地任务仍保留原采样。初始ground恢复指令沿用。

40min/5min完整保存检查；首前64env200step与4096env48step无优化探针；每点MuJoCo名义回放。最终同批PhysXFlat与R1地形、正反方向、实际跨阶和偏速后恢复评测。原冻结不覆盖，不自动R2或追加训练。全部PT实体Git，7897代理。

状态：已启动；40min结果待评测。

启动2026-11-11 18:28:35 Asia/Shanghai，PID1247876；首完整PPO iter22857，SHA`1c318faf8f9cca8a7884333603b9a98855dc96e05bb738b9b28fee5e4c68e4c5`，完整actor/critic/STD/Adam/RNG恢复。训练开始约106s累计numerical1，继续原单env重置统计，无整批失败。探针64env200步、4096env48步numerical均0，后者闭链峰7.0766mm及速度峰331.59rad/s如实保留。


2026-11-11偏速处理切段：用户要求加强速度平方惩罚。010m完整检查点iter22925/SHA959dc6a5a0ce1b221f8f7c489437b81da3149a712a96d2b8c319a1b3c496e022已核验保存，旧训练SIGINT退出，无FINAL/SAFE_CLOSED，不能写成正常40分钟完成。原段总消耗756.803s（010m后未保存更新也计入），接续−2.0e²用1643s，仍为同一轮40min；新目录MOD4V3_ROUGH_R1_SQUARE2_20261111。保存R1等级、地形分组、偏移和累计计数，重新物理episode。

本轮最终状态：三段合计2400.031s，名义/fullDR平地与R1两难度配对评测完成；三次项未解决fullDR偏速，未晋升；最终选择见../MOD4V3_ROUGH_R1_ABSCUBIC_20261111/DECISION.md。
