# 主优化器学习率日程整体×0.01：本轮单项试验，实际质量待测

## 来自本轮实际数据的选题依据

- [首7真实更新](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_N20000_W11_LOWSTD005_ADMISSION2_FIRST_REAL_TRAINING_EVIDENCE.json>)：配置desired_kl=0.005，实测该次20-minibatch均值KL约11.6395，实际LR已到1e-5。
- [完整25轮收口](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/reports/FDN_N20000_W11_LOWSTD005_ADMISSION2_20261105_051151/CLOSED_RESULT.json>)最后一次update均值KL约2.63307、LR1e-5；gradient finite/groups separated真。这是每次update内20个minibatch的平均诊断，不是整训练轨迹、信赖域证明或技能分数。
- 原位11,996,400低趴样本height通过约95.94%、speed约2.51%、angular约15.11%、joint_good约1.17%；29991低episode峰值全达到.23，但训练连续信用仍0。高度不是主要缺项；样本单项和峰值不替代持续联合接受。
- [同五姿MuJoCo](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOWSTD005_MUJOCO31_LOWRise_RESULT.json>)十条均完整finite：候选0/5，末态均高.210951m、速度2.264332m/s、平面位移12.554245m；本次母版.241437/.038073/.639393。降低初始STD本身未改善名义联合信用，漂移更大；这不证明native因果。
- 原独立N80初稿时仍在资源等待；随后Eval1真实零启动超时保留，新的EvalAdmission2已实际完成并通过V6_LOWSTD005父资格与collector全检查，结果0/74、normal物理0/6。见[完整质量决定](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOWSTD005_ADMISSION2_CLOSED_QUALITY_DECISION_V1.json>)。未获得严格信用改善，原1cd保持；此假设具备后续选择依据，但仍未部署/未宣称因果。

## 源码事实与局限

[固定PPO核心:374–386](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/source_fudan_seq_ppo_v1/fudan_seq_ppo.py#L374-L386>)按Gaussian KL比较后将主LR×/÷1.5，受当前[min1e-5,max1e-2]限制，随后执行原optimizer.step。没有把高KL当硬停止。source读取不证明它是漂移根因，也不修改运行中/冻结核心。

## 如果完整独立质量仍无改善，待选的一项参数因子

以本轮W11低STD0.05、无heightgate、fresh1cd配置为对照，只将**主优化器整个LR日程尺度η=0.01**：initial1e-3→1e-5、min1e-5→1e-7、max1e-2→1e-4。三边界共同按同一因子缩放，明确不是仅改一个initial数值。保留STD0.05、encoder LR1e-3、原desiredKL/entropy/5epochs×4/clip/梯度分组/两Adam算法与PPO核心源码。目标是检验warm-start策略是否能在更小实际步长下保持/改善，而非断言现有实验已确定根因。

同N20000/T48、cap25、seed20261104，原1cd actor8+critic8 MLP-only、随机fresh encoder/latent新增列0/两Adam私有generator与计数fresh，不继承坏cc41/bf824/246ac/205。原recipe、low8/400 timeout、reward、commands、action scale、PD/2c-bae/400N/fullD0D7/原接受阈值和分母保持。继续保留被动七项测量，观察实际KL与严格质量，别用小KL或更新数宣布通过。

最初仅假设；goal round4已选择并另建W12/v8实际分支，stage450/preflight0后取得原GO1793833088.400895、controller1639584/parent1639591/worker1639602。当前唯一受控顺序接续job pwsh-bd58147566b04531，原门控/计账/窗口不改，真实收口后立即调用原独立评测并重查资格；不凭source或GO声称更新/技能通过。[当前交接](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/CURRENT_PROGRESS_V23_LRSCHEDULE001_GO_HANDOFF_READY.md>)。H1/其它专家/Registryv12/1cd保持；旧cc41完整候选保留但不续该坏分支。全部新结果与本文件在下一有意义quality归档记录，main只读，不为Git重开模型/旧raw/物理。
