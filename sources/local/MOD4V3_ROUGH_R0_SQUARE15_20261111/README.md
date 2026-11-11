# 接续Rough R0：保留速度平方项1.5

2026-11-11用户在Flat约18分钟时要求下个检查点保存后切换Rough。按既有40分钟轮次分配：Flat20分钟＋Rough20分钟。下一个完整Flat020m作为实际父，完整PPO恢复，新物理episode与R0level0。保留−1.5e²和完整DR，复用既有R0地形/课程/35/78/6/2.5ms/TGS32/4/2mm重置，4096环境。每5分钟完整保存、MuJoCo名义回放；结束同批PhysX Flat和Rough配对。未自动推进R1或增加40分钟。

状态：已启动，确切父Flat020m/iter22856/SHA`a5102af62938f6bf472855edba34c5f10efce061eecaeb3aebee34815fe7cf87`。实际RESTORE完整actor/critic/STD/Adam/RNG成功，首完整iter22857。
