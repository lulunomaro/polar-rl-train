# 已保存回放一致性诊断：真实CPU结果 V1

这是**POSTHOC / REPLAY RESUBSTITUTION**：回放可能已参与训练，以下不是heldout、原技能通过率、泛化或因果结论。两角色各1次真实own checkpoint bytes/SHA/CPU decode；无mother重开、无optimizer/SDK/GPU/训练；全root/live值与版本、全局RNG保持。

沿记录action（bridge clip6 raw manager command输入，不是延迟后物理torque）比较。H16使用完整无done/cut/invalid的survivor窗口；CONDITIONAL每步true xi，FULL只起点true xi后aux+savedmask+legacy projector，无oracle重锚；两个都不是actor新动作反事实。

|角色|样本/actor/H16|1步位置MAE m|1步旋转MAE rad|1步关节q MAE rad|原reward样本std|真s1奖励头MAE|WM s1串联奖励MAE|
|---|---:|---:|---:|---:|---:|---:|---:|
|E3|64/64/32|0.000464182|0.00211593|0.0447666|0.136134|0.0061548|0.00546448|
|W35|64/64/32|0.000249724|0.00146179|0.00638273|0.00969654|0.0028826|0.00320529|

## E3
- 原reward mean=-0.0152127、mean_abs=0.0907045；真s1奖励头MAE/样本std=0.0452115，MAE/saved reward_norm.std=0.0370375。
- one-step done正例 1/64；串联Brier=8.94494e-07、ECE10=0.000320677。若正例0，未验证终止检测，不能凭均值低宣称calibration良好。
- 合法actor池121954、合法H16池108479；全部排除数与selected chronological keys在机器件。

|模式|h|位置MAE m|旋转MAE rad|线速度MAE m/s|关节q MAE rad|原sensor16 MAE（缩放观测单位）|奖励MAE|
|---|---:|---:|---:|---:|---:|---:|---:|
|conditional|1|0.000531709|0.00200293|0.0181609|0.0275796|0.038128|0.00342858|
|conditional|8|0.00160982|0.00563029|0.0188787|0.0881506|0.0319937|0.00926184|
|conditional|16|0.00377271|0.00824619|0.0219295|0.134548|0.0325883|0.00574179|

CONDITIONAL_STATE_OPENLOOP：H16累计原reward误差 MAE=0.049552 / RMSE=0.0808569。

|模式|h|位置MAE m|旋转MAE rad|线速度MAE m/s|关节q MAE rad|原sensor16 MAE（缩放观测单位）|奖励MAE|
|---|---:|---:|---:|---:|---:|---:|---:|
|FULL|1|0.000531709|0.00200293|0.0181609|0.0275796|0.038128|0.00342858|
|FULL|8|0.00273695|0.0116743|0.0284133|0.0923775|0.0543486|0.0134642|
|FULL|16|0.00559255|0.0262374|0.0341759|0.167317|0.066328|0.00747932|

FULL_STATE_AND_CONTEXT_OPENLOOP_ALONG_RECORDED_ACTIONS：H16累计原reward误差 MAE=0.0807109 / RMSE=0.164676。

- 当前deterministic mean在合法原raw35 history10上的六分量scaled residual RMS（非记录探索action误差）：`[0.9871909769481682, 6.9595325222340065, 11.48827919824793, 1.837501827599395, 3.670981895215906, 0.7206867322773153]`。
- actor−clipped teacher六分量max_abs：`[0.0, 4.842964172363281, 7.387494087219238, 4.934680938720703, 3.8115482330322266, 2.5255537033081055]`；actor clip saturation：`[1.0, 0.5625, 0.984375, 0.015625, 0.515625, 0.078125]`。

## W35
- 原reward mean=0.0474191、mean_abs=0.047804；真s1奖励头MAE/样本std=0.297281，MAE/saved reward_norm.std=0.0615076。
- one-step done正例 0/64；串联Brier=3.9566e-06、ECE10=0.00166445。若正例0，未验证终止检测，不能凭均值低宣称calibration良好。
- 合法actor池121942、合法H16池112027；全部排除数与selected chronological keys在机器件。

|模式|h|位置MAE m|旋转MAE rad|线速度MAE m/s|关节q MAE rad|原sensor16 MAE（缩放观测单位）|奖励MAE|
|---|---:|---:|---:|---:|---:|---:|---:|
|conditional|1|0.000295422|0.00167871|0.0157192|0.0187235|0.0312749|0.00306261|
|conditional|8|0.000992339|0.00340292|0.0145084|0.0454371|0.0304189|0.00231322|
|conditional|16|0.00198309|0.00517479|0.018844|0.0685096|0.0312125|0.00263922|

CONDITIONAL_STATE_OPENLOOP：H16累计原reward误差 MAE=0.0309945 / RMSE=0.0514047。

|模式|h|位置MAE m|旋转MAE rad|线速度MAE m/s|关节q MAE rad|原sensor16 MAE（缩放观测单位）|奖励MAE|
|---|---:|---:|---:|---:|---:|---:|---:|
|FULL|1|0.000295422|0.00167871|0.0157192|0.0187235|0.0312749|0.00306261|
|FULL|8|0.00224759|0.0105184|0.0215923|0.0500523|0.0436126|0.00248429|
|FULL|16|0.00381902|0.0238579|0.0263641|0.0838976|0.0561137|0.00395535|

FULL_STATE_AND_CONTEXT_OPENLOOP_ALONG_RECORDED_ACTIONS：H16累计原reward误差 MAE=0.0393607 / RMSE=0.0533177。

- 当前deterministic mean在合法原raw35 history10上的六分量scaled residual RMS（非记录探索action误差）：`[0.08308653329147013, 0.17515369913204057, 0.2718686634648422, 0.2501220162698164, 0.1405241118255836, 0.07838403907719137]`。
- actor−clipped teacher六分量max_abs：`[0.0, 0.26691651344299316, 0.7127044200897217, 0.6452332139015198, 0.24066364765167236, 0.19533175230026245]`；actor clip saturation：`[1.0, 0.0, 0.0, 0.0, 0.0, 0.0]`。

## 决策边界

不把本表误差直接变成原技能分数或真实失败根因。继续保持Registry_v12母本/H1/原物理fullDR/原接受阈值，尚未因本诊断启用任何新训练/奖励/动作映射。下一个因素须依据这些真实一致性事实设计并独立冻结复测，不为更新数量盲目续训。

[完整压缩机器事实](<reports/ACTUAL_REPLAY_CONSISTENCY_COMPACT_FACTS_V1.json>)含source/provenance、自然done分布、全部sample/exclusion、h=1/8/16面板及不变性。原两角色完整诊断保留所有h=1..16结果。
