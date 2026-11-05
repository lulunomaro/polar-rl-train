# Final60实评、实际回放及续训

人类最新：“为什么只有60次ppo更新？不是20000env吗？怎么一个小时才60次ppo？继续训和回放”。20,000是并行环境宽度，每轮24控制步收480,000条样本；60轮=28.8M条，5epoch×4minibatch=1200Adam更新。完整60轮真实日志平均采样50.5706s、优化0.2272s；总采样3034.234s，优化13.633s。初始化448.633s，STARTUP到final3054.059s。采样主导已实测；更具体CPU/GPU/solver瓶颈尚未分段测量，不凭此改变20k或增强物理。

final60完整学习诊断只解码1次，17Adam均1200、LR0.0008779149519890263、6STD及7组件/RNG/队列/globalcommon_step_counter1440完整。actor/critic/Adam均有限；3个SCUTpermission未设置NaN是既有哨兵。没有为Git解模或重复解模。

另一任务V36于19:23:47实际释放后，本聊天精确退掉仅本地睡眠的8572，保留其原once和记录；新准入读原canonical/三锁/freeGPU后独立eval_mesh01实际启动。19:31:06评测完成、19:31:07 ownwait释放，80/seed9137/399最大controls/400Hz/0optimizer，正式回传完整400Hz+actualpose+all80+curves，原失败网格导出eval并列保留。

实评0/80success、0ground-upwardflight/flightID/wholeclear/toplanding/topforce。16terminated/64timeout，0closure/mimic/numerical/rawoutlier；80局共374请求。rootx最大.531899m，未到.8m台沿。4选例0/1/40/41晚期finalx.509-.523m。全部4early/late侧视与顶视图已当前模型原生view_image审完：early是spawn下降，late接近台阶后轮子支撑、没有真实腾空越沿/落台。148contactfree entries及其中8positive-vz无已验证groundtakeoff，不能当跳跃。

按人类本次再次明确“继续训”接续当前随机起步v2的完整final60，华南虎base+source2/1/2奖励保持；这不是把失败结果认定毕业或无条件循环。新continuation_final60_1h仅1sdk模块修复导出MESH，91共享SHA引用，资产权重不复制；原owner/entry适配完整--resume、17Adam1200及FIRST61检查，0CPU新physics。实际owner1669926已启动；FIRST61/fullrestore及原actualGO时钟以唯一controller回传覆盖，不能从launch猜时限。下一小时仍完整保存退出后立即80与全部实际回放，依据实测再决定。

完整日志补读两次在LOCAL门因另一任务离线renderer/prepare出现被拒，0SSH/0once消费，原false都保留；第三次freshLOCAL后唯一有限读成功，完整WORKER272665B SHAee943dccad372f7aac6603d3a827d9f2170f473e71a342b086c7a24e66c2487e，实际训练错误0。所有报告、失败、返回和准备归同v2阶段ordinarysupplement，不重record/retag。
