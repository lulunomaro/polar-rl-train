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
