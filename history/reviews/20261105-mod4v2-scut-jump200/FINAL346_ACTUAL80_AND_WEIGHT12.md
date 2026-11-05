# MOD4v2 final346与起跳速度权重12接续

final239→346实际新增107次PPO、51.36M样本、2140次Adam和20544次物理回调。完整模型40,717,271B，SHA febd69f82d3b1e647d2598f660bb73a65fdc7c834bee7dc95b40bed7b972ccf4。唯一必要完整诊断确认17个Adam条目均6920、LR0.0008649755859375004、actor35/critic78、STD与7组件RNG/队列/计数器8304完整有限，新constructor nominal保留；三个未设置permission NaN仍为原哨兵，没有重复解模。

原窗口2026-11-05 22:56:12.293340 GO、23:56:12.293340保存、2026-11-06 00:01:12.293340安全退出边界没有延长。实际final23:55:24.035253、训练关闭23:55:52.971074、独立80完成23:58:17.566437、owner23:58:18.449778完整wait/结算/释放。完整503039B训练日志和15440B评测日志均0实际错误。107轮平均采样29.090860s、优化0.226402s，logger step/s均值16412.67、末16822；这些是已闭窗口实值。

独立80全部399controls/7.98s timeout，0持续接触终止、闭链/mimic/数值/outlier重置。0验证地面自主起跳、整轮腾空越沿、双轮台顶、稳定落台和成功，台顶力0。80环境353请求；rootx最大0.533890仍小于台沿0.8。102个contact-free entry中6个正vz均flightID0且轮底净高不超过1.30mm，不能当有效起跳。机械目标delta[-0.973294,0.138616]、0界限命中，motor目标MAE约0.049–0.059rad，不据此认定mapping损坏。

全部4张early/late侧顶保存姿态图，以及原v2可视mesh的env41完整7.98s视频与4关键帧已经当前模型原生查看；视频已打开Codex。早期spawn下降，随后接近台沿并在地面反复推蹬，未整轮腾空越沿或落台。媒体来自已保存PhysX wxyz姿态，MuJoCo仅mj_forward，0新NN/physics/PT/SSH。视频727413B，SHA61d77bddb9a7e537f1916026cb5d970e3b64cd82c0c6dd8379b7cde1bd13c23f。

原weight4的华南虎takeoff_vel_z已实际生效，保存动作逐control重算误差最大5.122274e-10。4038个push端点向上速度均值0.223073m/s、最大0.421753，相较final239的0.064225/0.185133明显提高，但全部push轮底仍低于1.312mm，3473个tuck端点vz均值为负0.150982。下一窗只将同一固定源码push-only clamp(world_vz,0,3)的权重4→12；原dt仅tail一次、基础字典与push height/velocity/peak2/1/2、命令/观测/动作/状态时序/物理/DR/PPO/验收保持。3项原公式CPU与6项既有v2测试通过，0生产PT/physics。旧轨迹weight12反事实push均值0.05356533/control、整体0.006776216，仅奖励核算，不能称新动作技能。

原75844本地收集器消失，原因未知；保留空日志及once，没有推断远端失败。唯一34352仅恢复尚未消费的正式读者，在原SAVE+45后完成回传，没有重训或重复评测。CIM字符串后缀、两次本地状态reader语法错误均保留。

新takeoff_velocity_weight12_final346_1h仅config叠加与PLAN/entry/owner四个小文件、92共享SHA引用。第一次准入因另一聊天E0的原canonical active而拒绝，0新生产启动；该false及全部传输关闭回执保留。E0实际00:05:09.622850结算/wait/释放，原owner1679974已dead。00:09:54.233947 fresh实际canonical activeNone、三锁free、剩余160344.73774170876秒，两4090 free24203MiB/apps空、RAM532171800576B/disk241275854848B。余额和空闲只代表这次准入。原reserve86412.86069250107不变。

仅恢复未消费的准入，使用admission_resume01追加回执，原false不覆盖；未造新实验树或预算。00:09:54.812576实际launch owner1681149/create1793894994.57。唯一local24916/create2026-11-06T00:09:47.145920+08负责原FIRST347验证后绑定唯一postround。FIRST、GO与窗口边界必须按实际回传更新，不能从launch推算。完整final346/17Adam6920/STD/RNG/队列恢复，newconstructor nominal保护后一次fresh physical reset，不恢复PhysX状态。实际运行状态见WORK_ORDER.json。

本次沿已有v2 trial追加普通Git补充，不record/retag。原失败、拒绝、回放、全部报告和共享账本授权均保留；本地其它chat控制器不阻断连接，但原远端实际计账准入与GPU锁保持。
