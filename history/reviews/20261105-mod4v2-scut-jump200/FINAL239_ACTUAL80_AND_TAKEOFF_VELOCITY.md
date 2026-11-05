# MOD4v2 final239与华南虎起跳速度奖励

上轮从完整final148接续至final239，新增91PPO、43.68M样本、1820Adam、17472物理回调。完整模型40,556,635B SHA74dcd1b80f57da5e8bd04554b28231279459eb1e6c0bf019b214b8776cc34838。唯一必要完整CPU诊断确认17Adam4780/LR0.0008649755859375004、actor35critic78/STD与7组件RNG队列计数器5736完整有限，新constructor nominal保留，三个未设permission NaN仍为原哨兵。

实际final22:22:39.832939，训练安全关闭22:23:17.242869，独立80完成22:25:44.229613，原owner22:25:45.036096完整wait/结算/释放，完整419747B训练与15437B评测日志均0错误。正式回传已完成、旧29056退出不重放。窗口仍原21:24:16.946090至22:24:16.946090保存、22:29:16.946090安全退出，不延长退款。91轮平均采样33.141341s/学习0.229231s；日志step/s均值14822.16、末15484，均为上一闭窗实值。

实际80中79timeout399controls7.98s，env69在246controls因持续chassis接触终止，0closure/mimic/numerical/outlier。全部0验证地面自主起跳/整轮腾空越沿/台顶落地/成功、0台顶力。70环境295请求，rootx最高0.533632小于台沿0.8。99contactfreeentries中2个positivevz均env28在0.2725/0.305s早期spawn落地反弹、flightID0，不是验证起跳，更没有越沿。全部4early/late侧顶图已当前模型原生查看；选例1/40/41在台前接地停住，env0结束x0.323。7.98s env41原v2mesh保存姿态视频与4关键帧已生成/查看并打开Codex，0NN/physics/PT/SSH。

反复失败实测：3311个push端点worldvz均值0.064225m/s、最大0.185133；2857个tuck端点均值vz负0.040826，原peak项仅约1.99e-8/control。当前机械delta在CAD界内且0边界命中，目标跟踪MAE约0.03–0.04rad，不将其误判为mapping损坏。只修改奖励配置：启用固定华南虎源码已有takeoff_vel_z公式，push期clamp(rootworldvz,0,3)，weight4，dt仍原tail一次；idle/tuck新增项0。原基础字典与pushheight/velocity/peak2/1/2保持，0新奖励公式、0物理助推，不带回v1projection/bilateral/tuckgate。3项新增源码CPU测试＋6项既有v2检查通过；旧保存动作反事实push新增均值0.005171826/control，整体0.000539047，仅旧动作奖励核算不称新运动。

下一任务takeoff_velocity_final239_1h仅config.py叠加＋PLAN/entry/owner，92共享SHA引用，sdk继续引用原已修overlay，无模型/资产/整树复制。从完整final239恢复17Adam4780/STD/RNG队列计数器，20k和华南虎PPO、硬件、DR、动作、观测、验收保持。实际owner1677968于22:56:12.293340 GO，SAVE2026-11-05T23:56:12.293340/NOMINAL2026-11-06T00:01:12.293340。23:03:26.721080已验证FIRST240：source239+1，480000新样本/192physics/20Adam，actorgrad0.9999998808/critic1.0，完整首存40,717,271B SHAda204dacabdee35ebabd85a54ffc83b7aad2be0747786c472817f34aeb703926；完整首轮18057B SHA16e28d4b448fb47135ee7543051b90b83d1dc9ccbd5a1040f9e1c22007934162，errors0。恢复239/17Adam4780/LR/组件RNG队列计数器完整且新nominal保留。首轮17077step/s（collection27.798s/learn0.308s/总28.11s），不是技能证据。55964正常退出后唯一75844收集器已绑定，SAVE+45=23:56:57.293340有限正式返回。最新共享账本指令仍适用，本地其它controller不做总串行门槛；原余额reserve/GPU锁和计账准入不改。

本次沿已有v2trial追加普通Git补充，不record/retag。原失败、读者文件名错误及全部报告保留。
