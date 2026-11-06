# 官方采样对照与总训练吞吐优化

2026-11-06人类要求“怎么速度这么慢?优化采样，看看官方采样流程”，明确速度指采样和全部学习更新合计的控制样本step/s。固定查阅PoplarCrystal/basic_loco_lib commit e4181af587330d0b70ca72e0d36b49be32e12a65的MimicWM learner/replay/bridge/Warp环境，源码和SHA保留。其replay留训练设备、CUDA启用fused Adam，Warp环境合并热路径。MOD4的Fudan learned reward/context并非官方analytic mimic任务，不替换任务公式或引入人形参考。

实际本地128环境、生产网络宽度和原4WM/4aux/H32/4critic剖析，一轮记录73281次Torch CUDA kernel launch、2670次stream synchronize。闭链检查与跳跃验收占采样约30%；replay add和batch搬运合计约18ms，非当前本地主要瓶颈。此前20k完整GPU replay已真实OOM，因此保持完整CPU replay和CUDA batch，不盲目搬回2.26GB整库。小批次剖析比例不可套远端20k。

新候选融合400Hz六闭链/四mimic与验收、50Hz复旦16项；四个原Adam启用fused执行，保留权重/一二阶矩/步数和posthook；learned模型几何纯张量函数用TorchScript图执行，保持fp32/H32/梯度路径。此前状态读取融合导致fullstep慢7.5%，仍不启用。新增训练入口选项和检查点字段会自动恢复候选；日志明确给出采样/总训练窗口吞吐和含初始化、历史周期保存的worker吞吐。

逐项真实端点验证：108次闭链检查最大差1.953e-8m，原16项奖励及状态/复位对齐，270验收端点和invalidmask计数对齐。几何12组输出最大1.193e-7、梯度最大9.537e-7；完整四Adam/replay/RNG/7组件保存并通过production build恢复后新H32，0数值重置。first/BPTT有限不是技能。

最终隔离ABBA11：同一随机本地teacher学习状态、每组恢复四Adam/replay/RNG，A组恢复原eager几何。每组4轮2/3交替controls，WM/aux/BPTT/critic比率均不减。A两组2560样本/17.62785s=145.225 controlstep/s，B为2560/12.20819s=209.695，**总吞吐1.44394倍**；采样534.888→954.968，**1.78536倍**。A1/B1/B2/A2四轮耗时9.862/6.281/5.927/7.766s，笔记本实际时钟有波动，原全部round保留。这是5070Ti Laptop本地128环境，不将该绝对速度或倍率冒充4090生产20k实测。

前一只含采样/fusedAdam的ABBA07总吞吐1.10879、采样1.64092倍保留；scripted09因测试harness变量original被tuple覆盖失败，scripted10末尾A仍保留scripted几何仅探索，均不作为最终倍率。隔离ABBA11修复分组恢复。全部失败/raw不改写。

production build完整恢复测试12已通过新H32；CLI13从fixture iteration1到2仍在原32轮warmup，0新BPTT，保留且不当策略更新证据。新CLI14只调整随机fixture调度到32，所有学习张量/Adam保留，真实运行到33新增1次H32/4WM4aux4critic并完整fullsave/safeclose，0数值/约束重置。不是生产检查点或技能测试。

当前原小时冻结supermimic_first1941_reboot_periodic_1h及sole79388不改。原SAVE11:30:26.533121、soleSAVE+45开始正式回传；先fullsave/release/独立80/全4actualpose，再按证据用prepare_sampling_continuation.py从实际final接入。原400Hz重置、物理/DR/命令/复旦16、residual.25和300秒原子完整保存保持。2万环境生产总step/s待实际下一FIRST/窗口回执，不能直接把旧27315.87乘本地1.44宣称新速度。

11:41实际接入更新：原小时完整final3786/source1941+1845H32、9226万新样本、owner3648.248223s含初始化/周期保存/80，实际总25288.85step/s；最后一轮60000/2.064444=29063.52，采样47267.77，均值与快照区分。完整四Adam步数pi3754/WMaux15144/critic15016、64x20kreplay1279964valid/36invalid且streamcut/7组件RNG完整；唯一final解码完成。周期最后3766完整2328856927B有真实回执。独立80平均4.8135s、36timeout44terminated，73upward、0wholeclear/topforce/landing/success；全4earlylate实际姿态当前模型原生审阅，后退短跳/倾倒，未过200mm。原日志全文errors0，但新增612numerical/760constraint，不能说训练数值无风险。

正式supermimic_final3786_sampling_1h用9小文件/共享原件启动，sourcefull3786 SHA d260e491f820f92be587ba7fafd280df1adfaa720d925b347a1bfd514749ea12。实际FIRST3787新增1真H32并首存2328857439B SHA15fa5c7bf7e0dd2409c50187a748ff4160ef651f40cab6712766dc9bddd4daf8，四Adam/replay/RNG/teacher完整恢复且原residual.25。STARTUP确认Warp400Hz/50Hz、fused4Adam及TorchScript几何启用，0新FIRST数值/约束重置；大有限梯度和loss不当技能。原launch58916正常退出，sole78196/create11:41:03.350977负责本轮保存后正式回传。

11:41:03.493781历史LATEST3792/6新H32快照：60000/1.468956=**40845.33总训练step/s**，采样**80549.99step/s**。相对上一最后轮约1.405倍仅两个快照，非同状态ABBA或小时均值。首轮含编译5970.72、六轮含冷首轮窗口22494.00、含初始化和首存worker4304.94，均原数保留，不能用暖轮覆盖冷启动。整小时平均待本轮真正返回。

actualGO11:39:47.665763/SAVE12:39:47.665763/NOMINAL12:44:47.665763，北京时间2026-11-06；soleSAVE+45=12:40:32.665763。健康只查本地exact78196/children/reports，不二次SSH/reader/FIRST/PTdecode/hotpatch。新累计前67791.168398秒仍为原中断保守上界+已知实耗，非捏造实际GPU成本。下一小时据final/80/回放和真实吞吐再修，未进入台阶地图。
