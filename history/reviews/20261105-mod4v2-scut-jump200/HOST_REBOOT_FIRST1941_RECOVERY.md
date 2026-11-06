# 服务器重启中断与FIRST1941恢复

2026-11-06 10:13有限原服务器检查确认启动时间09:41:05，原owner1697594与worker1697604完整PID/creation均不存活，原GPU私有锁可取；没有终止任何其它chat。取回原生产完整日志与目录后，未见FINAL、interrupted checkpoint、TRAIN_CLOSED、OWNER_EXIT或80评测。原日志末尾含NUL，原因未进一步确证，不冒称正常退出或特定硬件故障。

最后完整进度iteration2842、902新增验证H32、总143.38M转移，对源1940新增45.10M；lastownerelapsed1696.757秒。唯一持久完整检查点是FIRST1941（2328856927B，SHA0070897dbf618063b2f243d6ffdf7120bb914b8d52e5d555f435ab28445802e7），较latest少901次更新。完整恢复必须使用该原件，不能把LATEST_PROGRESS当权重。原失败窗与所有旧once/error/partial不覆盖。

SSH已能真实读取；原57448读者在09:57的90次有限读取后因缺OWNER_EXIT返回pending并退出，finally已关闭SESSION恢复FREE，不再让它等待一个已消失owner。10:15只补缺失FIRST1941独立80，私有GPU EX、seed9137/新DR/400Hz/0优化器，产物在原窗的recovery_first1941_eval80；结果不冒称final2842评测。

下一新段仅增加每300秒完成更新后的原子完整保存（相同完整四Adam、WM/aux/policy/critic、replay、7组件DR/RNG/queues），保留首次与最终完整保存，固定原3600+300窗口不延长。真实本地4环境周期保存与恢复第二次H32已通过，报告PERIODIC_FULL_CHECKPOINT_RESTORE_TEST.json；不改复旦16项、物理或策略尺度0.25。新段需先完成本次80及实际回放，保留失败后再按证据选择。

原owner没有actualelapsed回执，不能捏造已结算成本。记录1696.757秒已观察活跃下界，以及从GO到下次boot的11851.925803秒保守上界；上界仅用于累计100h安全核算，不写canonical也不作真实GPU耗时声明。原窗未延长，网络等待不产生续训授权之外的时间补偿。补评测真实耗时另据回执。

10:27补评测与文件传输已完整完成，原receiver自行退出，未终止它或补传。源FIRST1941唯一完整诊断通过：四Adam步数WM/aux7764、pi1909、critic7636；64×20000replay1279999有效/1无效及streamcut、7组件/RNG/queues有限完整。独立80平均246.4875controls=4.92975s，28timeout、52terminated，0数值/约束，44无重置upward flag、0越沿/落台/成功，rootx最大.548766小于.8；16奖励/commands/电机和perbody真实字段保留。NPZ仍缺400Hzphysicalvalid列，50Hzcurve真实physicalvalid全部有效，两种范围明确并列。全部4earlylate侧顶实际wxyz图当前模型原生审阅：接近台沿前短跳/摆动，未越沿；没有通过200mm。

10:30准备并启动supermimic_first1941_reboot_periodic_1h，仅5小文件overlay与共享引用、源完整1941不复制，target residual.25和周期300秒保存。初始总额采用64142.92017507553秒保守上界（含补评测实测415.579145s），明确非原owner实际成本；不写账本。FIRST与唯一collector待实际回执，不提前宣称更新成功。

10:32新段实际VALID FIRST1942/source1941+1H32：3controls60000新样本、4WM/4aux/4critic，跨时37.2394/WM路径26.0141、裁剪前paramgrad2374.43、paramdelta.000793651，全部有限但不是技能。首存2328856927B SHAad81f7a1f10f54a7826966babcb690cd42e873d65bbfc45db5d86f64db2da645；restore四Adam/64×20kreplayptr52/RNG7组件完整，source/target residual.25、freshphysicalepisode。首轮numerical361/constraint778为继承累计、0新重置。完整首轮WORKER21954B SHA5b5bd64197b4c4a30ed2828af82a9525fba709ed3cdf67a2b1edd0393821b431，错误0。周期保存300秒STARTUP已回读，尚未到首个实际周期。

实际GO10:30:26.533121、SAVE11:30:26.533121、NOMINAL11:35:26.533121（北京时间）；唯一collector79388/parent37408/create10:31:43.158333，只有自身conhost29876，stdoutstderr0。原owner6227/create1793932225.45、worker6237/create1793932225.83，以实际receipt优先。soleSAVE+45=11:31:11.533121有限回传；健康仅本地exact，不第二SSH/reader/PTdecode/重launch/hotpatch。FIRST不是跳跃毕业，下一完整小时后核新80和实际回放，不能原样无限失败小时。
