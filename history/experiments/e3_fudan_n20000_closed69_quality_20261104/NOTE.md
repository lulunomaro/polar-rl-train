# V11 — N20000 closed69；原范围0/74；不推广候选

- 当前 goal `goal-c490e4cc-b28b-440e-bde6-30ee956813f0` revision3，active/armed，max14；质量改善未实现，不 complete/pause/blocked。
- 本窗 N20000/T48 新增69真实PPO/双Adam1380/66,240,000已优化transitions；累计133/双2660/78,822,912。native控制3360，完整保存48个未优化控制。
- 完整候选SHA `8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78`，1204250903 bytes；source/new env/DR/history/RNG语义见 [实测总报告](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_N20000_QUALITY_RESULTS_V1.md>)。
- 原 native N80/160/seed20260928执行qualified，0/74；normal6的物理终止0；父/子/outer实际等待与资源释放均闭环。原口径未放宽。
- 31体名义MuJoCo5姿×8s各400control均finite。严格计分双方0/5；候选高度约.183m/速度.309，母本高度约.241m/速度.038，不能把两者行为说相同。未证明native因果退化。
- Decision：`KEEP_REGISTRY_V12_E3_1CD_NO_8AF4_PROMOTION`。H1/其他专家/Registryv12不变，所有完整候选保留。
- stage_v1只在本地 pinned-assets 两/三空格锚点失败，marker/connect/模型/SDK/GO前；旧源保留。新stage_v2仅修两处锚点，成功完整nonPT materialization445files。没有物理重跑旧根。
- native训练observer6639、CPUexport66529、真实MuJoCo6d4、原native评测47bb均已completed0并收集，当前无本任务 native/observer。勿复跑已消费 stage/dispatch/collector/export/benchmark。
- 14权重派生artifact见 [pi-only部署artifact](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDNN20000_PI_ONLY_EXPORT_20261104_215607_1793800567159401600/pi_export.pt>)；它明确不是完整resume。原1.2GB输入不为状态/Git重开。
- 源分析与唯一下一任务源已完成：[低趴8秒timeout源](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/source_task_runtime_v2_lowtimeout8/e3_fudan_task_runtime_v1.py>)，99行/8571B/SHA386107b02983505518e1dcfb5bbdeb6f243392d390dfd48e16a61d75cb2c51e2。仅recipe>=13、真实time_out=True、episode_length_buf达到ceil(8/step_dt)，50Hz第400完成步；新增实际全局episode配置摘要，旧fall/normal/reward/PPO/物理DR保持。一次AST/compile+静态差异PASS，无测试/SDK/模型/SSH/准入/训练。child已inactive。下一窗完整source必须重新绑定8af4/N20000/Base133；现v3硬绑定47937/N4096/Base64，勿直接复用。详情见[单一干预计划](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/NEXT_SINGLE_INTERVENTION_LOWTIMEOUT8_PLAN_V1.md>)。当前无下一训练进程。
- 最新已验证archive仍4fc5baf6c8a1df672bbb3d281475d6b370d70a4b / trial-20261104-e3-fudan-n20000-admission2-native；本次69闭环、实测、失败、选择、晚源等待下一次有意义合并archive。feature-only，main只读；模型/raw/media/geometry在stat/read/hash前跳过。


# 下一单一任务干预：低趴分支8秒 timeout（待运行）

## 为什么提出，而不是已证明的原因

[本次独立结果](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_N20000_QUALITY_RESULTS_V1.md>)表明：N20000 新增69次真实PPO后，原恢复首次episode计分仍0/74；正常6例无物理终止；候选在五个固定低姿的名义MuJoCo高度和漂移比母本差。当前决定保留1cd母本，不推广8af4完整候选。这些结果没有证明 native 因果退化，也没有完成起身质量目标。

[任务源](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/source_task_runtime_v1/e3_fudan_task_runtime_v1.py#L20-L70>)规定低趴请求8秒，默认episode则为20秒；后者来自[基础配置](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/original_runtime_refs/mod4_task.py#L1862>)且允许环境变量覆写，现有独立报告未证明该默认就是本次生效值。若20秒且没有提前终止，低趴episode的后12秒已没有恢复请求。N20000 的固定recipe分配为9997低趴、9234旧跌倒、769正常。

高度目标原始值是0.25m，[观测项才乘5](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/original_runtime_refs/mod4_task.py#L418-L424>)；没有把0.25误当缩放后的1.25输入。恢复potential项已经是delta/step_dt，不再重复指称它少除dt。低趴高度项已解mask，竖速罚在请求中仍mask。奖励默认权重不等于已核实的本次生效权重。

## 只改变这一项任务行为

在新的、尚未准入的任务源中增加带 `time_out=True` 的终止项：只对 `recipe >= 13`，在episode达到8秒时timeout；50Hz为400个策略步。使用框架episode_length_buf和step_dt，确认计数顺序，不用可能落后一拍的phase age；不是physical failure。保留既有timeout bootstrap语义。

旧跌倒、normal、原74评测、奖励函数和权重、Fudan PPO/encoder、动作、观测、所有物理/DR/关节范围均不变。新摘要应记录实际基础episode配置与低趴8秒上限，区分源默认和运行值。该项只是待验证的目标/采样匹配假说，不能从源代码直接宣布改善。

## 下一窗完整承接边界

拟用实际完整N20000候选 `8af4e04c3a2b7dff8e805eb28a47caee442ae2f9c9ac25d08369e25d4aa6ca78`（1,204,250,903 bytes）承接整个learner：模型/critic/STD/LR、两套Adam、私有generator及累计133/双2660/78,822,912个已优化transitions。输入有3360个native控制，69×48已优化，48个控制的完整pending未优化；新流不补算这些pending。

现有retained-source v3只接收旧4096/64步/47937输入，不能拿它直接接8af4。下一unused版本必须按实际version2/N20000根校验并完整加载learner；新环境/DR/历史/全局环境RNG仍明确fresh reset，不称PhysX bitwise resume、不切片、不把pi-only部署产物当完整resume。新的本窗counter从0开始，累计以133为base，跨窗transitions按实际人口累计，不回填133×20000。

所有完整源和候选保留。新source/manifest/owner准入仍走原single-writer canonical、私有GPU与finite锁、原计费、3900/3600/300和1800preGO；不复制账本、不退款、不延长旧窗、不重放任何已消费once。当前这里只准备源码，没有发出下一训练窗。

## 评测与选择

仍使用原N80/160/seed20260928的74个恢复首次episode及6个normal；不得在原评测中安装新低趴timeout。保留相同五个合法姿态的8秒MuJoCo名义对照，并继续注明clean观测/非fullDR/非native接受标准。未经独立质量改善与技能保留证据，不推广新候选。H1、其他专家、Registry v12和生产E3母本均不变。


## Archive boundary
Actual N20000 window ended with 69 new PPO updates, 1380 steps for each Adam, 66240000 optimized transitions, and a fully saved 48-control unoptimized pending rollout. Complete candidate 8af4 is preserved; source4096, full N20000 continuation, and derived pi-only deployment are separate artifacts and purposes. Qualified original N80 reports 0/74 first-episode recovery credits and 0/6 normal physical terminations. Ten actual nominal MuJoCo runs remain separate from native/fullDR acceptance; both engineering scores are 0/5 but the mother raises its body while the candidate stays low and drifts. Keep Registryv12/1cd and H1; no candidate promotion. Preserve the pre-connect materializer indentation failure and new-source correction. Next low-only timeout8 intervention is a source-level hypothesis, not a proven cause or already-run training. Original physics, DR, resources, canonical accounting and actual closure remain unchanged. This script is consumed after record; never repeat record/tag/physical tasks for sync.
