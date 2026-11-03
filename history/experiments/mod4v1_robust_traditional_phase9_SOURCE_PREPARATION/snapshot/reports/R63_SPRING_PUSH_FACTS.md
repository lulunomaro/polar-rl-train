# R63：仅push阶段撤名义弹簧抵消的实际结果

新物理结果 6，完整 6；已知实际消耗 4800 controls / 96000 physics steps。软件prefix未知项：[]。

|case|原门|旧baseline|轮mesh空中峰值 m|guide/hard ticks|终态稳定 s|失败项|
|---|---|---|---:|---:|---:|---|
|r63_spring_release_nominal_flat|True|True|0.19168605065374866|0/0|4.629999999999946||
|r63_spring_release_nominal_rm|True|True|0.1921001504367721|0/0|4.629999999999946||
|r63_spring_release_DR4602|True|True|0.27482476802717515|0/0|4.869999999999941||
|r63_spring_release_DR4605|False|False|0.2045356890938418|2/0|4.509999999999948|no_guide|
|r63_spring_release_DR4606|False|False|0.2441071228037885|0/2|3.889999999999961|no_hard,lane|
|r63_spring_release_DR4610|False|True|0.21794249682027161|3/0|4.559999999999947|no_guide|

所选机制TRAIN：1/4；同一已执行seed旧baseline 2/4。
只改变名义弹性端点FF加回，机械spring/PD/driver/原接触及所有原门保持。端点混合不是任意q(t)精确模型。
原标准逐项重算一致；main轮rear-cross不等整机空中净跨，保守包络失败不自动等实际碰撞。
队列是已按旧TRAIN结果选择的机制对照，不是独立holdout。空中mesh峰值、6cm局部跨障不构成270mm台阶/全RM/硬件或母线功率资格。
本统计只读小result/config；大raw只引用producer SHA/size，没有物理/旧QA重放或为归档重hash。
