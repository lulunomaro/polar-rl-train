# 下一有限动作：冻结8e27，一批N80只测原根速失败的XYZ分量

## 已证实与未知
[新三seedholdout](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_RESUME55_LOW80_HOLDOUT_RESULTS_V1.md>)：8e27首episode连续25信用22/240，严格终点当前连续25为0/240，ever+末帧12/240分列；物理首episode结束0/240。末帧height/upright/wheel/chassis均未失败，根速113/240、角速15/240失败，联合121/240失败可重叠。mean根速.03188907208483822/mid.029258464463055134；max-good中位14控制=.28秒，小于25=.5秒。名义五姿终点5/5不代表原生fullDR稳健，原74仍0/74，不晋升。

现有结果只存根速范数和角速范数，没有根线速度XYZ序列。尚未证实速度失败主要来自平移XY还是接触/竖直Z、哪一DR或奖励项；旧low阶段lin_vel_z掩码、encoder参数变化较大等源事实都不是因果证明。因此本轮后不盲加25、也不先改速度阈值、物理、reward或encoderLR。

## 唯一下一诊断（源码与实际准入尚未执行）
- 只冻结完整Root8 8e27c2f35d5e1ed5ad2f71324e729bdbda9a10e1486b151ca1dd9384d3ecfe32/146251569B；seed明确20261005，一新process N80=同五合法pose×16，400控制8秒、原sole fresh reset/fullD0D7。该seed只是诊断，不再当未来独立选模holdout；候选only，未运行reference则paired差值null。
- 在原phase.update已读取的root tensor上，仅被动保留世界系root linear velocity三分量、可选angular三分量；不增加root/contact getter、不调用额外传感器、不触发RNG、不变physics/reward/commands/termination/good或原25信用。未知源字段与typed观察state原样保留。
- 在同pre-reset hook以first_episode_live mask累计小型统计：各轴v²和、各轴abs均值、原speed_fail条件样本数、其中XY_norm>=.03 /abs(Z)>=.03 /两者均小于.03但合成norm>=.03的数量；终点每env的三轴值及current_good_streak。只统计原条件、分类可重叠明确标出，不另造通过标准。可用有限几个时间点aggregate而非巨大轨迹dump，落盘仅bounded JSON。
- 整源一次物理read/hash/CPUdecode/cache，未知N20000根/raw CPU保留，仅14pi frozen mean GPU，无critic/optimizer/learner，无sourceDR/history切片或RNG应用。不为status/Git开模型。
- 原privateGPU_EX+finite_EX/原C ownerNone+reserve/fresh4090/1800preGO/SDKclose/actual innerouter wait释放完整保留，无预算增加、退款、账副本、foreign signal或清锁。此计划不意味着新GPU任务已启动；旧低80三case/first失败/Admission2/原物理once均不重放。
- 获得实际XYZ占比后才选择下一单因素学习假设：若竖直分量主导且原有效lin_vel_z确实掩码，可考虑只在low解除该原负项掩码；若XY主导，则针对实际低速tracking/估计误差另选一个因素。必须先以真实effective config和观测确认，保持Fudan PPO核心/原门限不变，不能凭source默认权重或参数delta认定原因。

H1/其它专家/Registryv12/1cd与全部候选保持。仅有诊断计划，没有新增训练或模型晋升，goal仍active。下一实际源码/准入/成功失败与结果照原feature-only唯一annotated trial归档，main只读，模型/raw/旧once/物理不为Git重跑。
