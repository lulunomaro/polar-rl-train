# 接续Rough R0：保留速度平方项1.5

2026-11-11用户在Flat约18分钟时要求下个检查点保存后切换Rough。按既有40分钟轮次分配：Flat20分钟＋Rough20分钟。下一个完整Flat020m作为实际父，完整PPO恢复，新物理episode与R0level0。保留−1.5e²和完整DR，复用既有R0地形/课程/35/78/6/2.5ms/TGS32/4/2mm重置，4096环境。每5分钟完整保存、MuJoCo名义回放；结束同批PhysX Flat和Rough配对。未自动推进R1或增加40分钟。

状态：已启动，确切父Flat020m/iter22856/SHA`a5102af62938f6bf472855edba34c5f10efce061eecaeb3aebee34815fe7cf87`。实际RESTORE完整actor/critic/STD/Adam/RNG成功，首完整iter22857。

Rough005m：完整PPO含terrain_curriculum_state已保存；MuJoCo名义前进2.280636/2.563200偏超速，其他四项10/10，回放reset0。训练numerical0；完整DR/地形实际能力待同批PhysX验证，原指标不回写pass。

Rough010m名义回放2.259898/2.541289偏超，其他四项10/10、回放reset0；随后约654s训练numerical累计1。现有numeric条件为非有限状态或joint_vel>500rad/s、root_ang>200rad/s、root_lin>100m/s。当前周期只保存峰值和累计，没有该瞬间逐env状态，不能指定是哪项触发或冒称根因。按原单env重置保留，无整批失败，未改任何门槛。一次本地读取不存在LATEST_PROGRESS路径失败，使用monitor已有实际周期记录；训练未受影响。
