# 下一项假设：仅从55afa完整learner有限续25，不改奖励/STD/LR/物理

## 来自本轮真实失败反馈，而不是更新数配额

[独立三seed fullDR确认](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LOW80_THREESEED_CONFIRMATION_RESULTS_V1.md>)：首episode连续25控制联合信用21/240=8.75%；此前获过信用且第400控制单帧joint_good为7/240=2.92%，严格末段连续25计数未序列化、保持null。三seed 8/80、8/80、5/80；240个首episode物理终止0，但这不是起身接受。末帧高度/姿态/双wheel/chassis各240/240过其条件，根速124/240失败、角速12/240失败、joint129/240失败（可重叠），最长good streak中位15控制=.3秒，不足所需25控制=.5秒；根速均值.034450m/s、中位.030714m/s，与原严格.03门限分列。

这定位的是**本轮观测到的连续低速稳定性不足**，不证明具体reward/某一DR项/优化器的因果根。根速XYZ成分没有在本scope序列化，不猜测是Z振动、XY漂移或传感lag；不凭默认reward权重做诊断。原74仍上一真实0/74，母版native配对参考未运行，paired差值null。旧名义5/5不能推广成native fullDR90%。

## 唯一学习干预：延续已存在的正向局部候选，不重启或叠加超参

- 相对本轮冻结55afa，下一新purpose/window最多新增25次真实PPO。使用实际已保存**完整55afa**，不是重新1cd MLP-only开始、不是派生pi_export/CPU预演，也不续坏cc41/bf824/246ac/3e64。保留全部旧candidate/mother与原false/null。
- 输入只来自 `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_FRESH1CD25_LRSCHEDULE001_W12_20261105_065201_1793832721176405000/roles/E3/production/fudan_seq_full_u000025_c00001200_s0002.pt`，146247985B，SHA55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7；Root/schema7、fresh原1cd lineage25/两Adam各500/24m，完整close/actual wait/cost/release已资格。
- 必须真正还原该learner的actor/critic/encoder/logSTD、mutable LR、两Adam全部state和私有generator/未知根，原core.load_state_dict clone语义复用，输入whole CPU一次physical/hash/decode并保持immutable。不是只拷14pi或把config初始LR覆盖实际LR。源末实际LR2.562890625e-6与config initial1e-5/min1e-7/max1e-4分列；encoderLR.001、initial STD.05及其实际learned logSTD原样续接。
- 计数base25/两Adam500/24m保留，新window单独0→≤25；累计base+window，每新update960000转移、各20Adam，不把旧source_iter43090或旧4096/205计数拼来。源环境20000、controls1200、pending0只是CPU保留的历史，不当新controls。
- 新N20000/T48环境/DR/history/queues/环境全局RNG经原sole fresh reset重新生成，source这些内容不应用、不切片到新env；显式stream cut，不声称PhysX整环境位级resume。新returned noisy raw35重复5帧起history，不额外采样。
- 训练仍混合原falls0..11/normal12/low13..25、五合法pose、8s/400 timeout、原a848 overlay/PPO5×4/奖励/commands/PD/400N/k2000/d3/fullD0D7/2c-bae资产不改。**只改变从已验证learner续学的训练量，不叠加reward、KL门控、STD或LR因子。**这是根据低速稳定性不足选择的有限学习验证，仍不保证改善、25不是通过。
- 可在原已读取root/phase数据上添加只读诊断（不改变行为）：root速度XYZ平方统计、每个终点当前good streak controls，不能增加额外传感采样或修改信用。它们只是解决本轮读者解释与未观测分量缺口，不成为毕业规则或CPU审计农场。

## 必须的质量反馈与资源/交接

- 运行前一次最小metadata适配要接受实际Root7输入，旧retained helper只接受8af4/Root2不能直接套；旧源冻结不热改，不为修格式反复打开55afa或重跑旧once。不另造seal/CPU回归农场；已有完整core resume测试复用，实际native input/clone/更新/完整保存才证明本次真实续接。
- 原canonical/charge_values/authority2EX/privateGPU_EX/train finiteSH-eval finiteEX/reserve86412.86069250107、3900/3600/300与1800preGO全不改。实际GO至SDKclose/save/innerouterwait结清释放；不清外国锁/发signal/退款/扩预算/复制账。提前准备评测与受控原父接续，实际释放后立即重新fresh门控，不传递外部租约。
- 保存/实际closewait/原成本释放后：原E3 N80/160/20260928/74+6保持验证 + 同名义五姿8秒 + low80/fullDR多seed。新scope读者必须另列『首次连续25信用』『曾获信用且末帧good』『终点当前streak≥25』，末项若未记录仍null。原74分母、3秒request与所有门限不动，normal物理0/6不当normal通过。
- 本轮20260929/30/20261001作为诊断集；下一确认预先另留seed20261002/20261003/20261004，不把同seed当完整DR/噪声/lag配对。没有实测baseline配对时差值仍null，不把不同seed或nominal对照宣传因果。任何新低姿结果均不合并原74、不自动晋升Registryv12。
- 全部真实成功失败/源码/报告按下一有意义feature-only unique annotated trial记录并远端核验，main只读；不为Git重开模型/旧raw/物理。当前这只是下一有限验证文字计划，尚无新续接worker/准入/模型输入/SDK/训练实例，goal继续active。
