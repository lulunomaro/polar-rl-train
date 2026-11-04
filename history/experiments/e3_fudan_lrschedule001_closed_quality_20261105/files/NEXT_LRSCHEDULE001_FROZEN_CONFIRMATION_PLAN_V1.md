# 下一项：冻结55afa独立确认，不继续加训练更新

## 选题来自实际新证据

本轮[完整质量结果](<F:/RMPOLAR-RL/e3_fudan_recovery_alignment_20261104/FDN_LRSCHEDULE001_CLOSED_QUALITY_RESULTS_V1.md>)：N20000/T48真实25/两Adam各500/24m、完整收口；候选55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7、146247985B保留。原N80/160/seed20260928严格首episode信用仍0/74，normal首episode物理终止0/6，不是normal接受率。

同原五个合法低姿、每条8s/400控制、clean nominal31体MuJoCo：候选5/5曾连续.5秒满足原低趴全部工程联合门限，母版0/5。候选末态5/5速度均略高于.03，因此credited_and_stable_at_end为0/5；5/5不是8秒持续到终点接受，不是原E3毕业。候选末态均高.241784/根速.032465/XY.596205；本次母版.241437/.038073/.639393。相对W11候选2.264m/s和12.554m漂移有明确名义量化变化，但单seed/五姿态不是matched native因果。原位训练低组连续信用4/29991与joint_good样本20.3217%分列；不替代独立验收。

实际第25次update内20minibatch均KL.0050813306、LR2.562890625e-6，首1次KL22.888443、LR1e-7；不以诊断量决定晋升。原1cd/Registryv12/H1/其它专家保持。下一步优先确认，不叠加新的reward/STD/LR/epoch或盲续55afa。

## 下一独立scope的最小实施目标（当前仅计划，未创建/运行新worker）

1. 将当前完整候选冻结作pi-only，使用同模型缓存边界：每个真实新确认purpose整份N20000根一次CPU read/hash/decode、未知根保留、只14pi上线，不恢复训练/两Adam/环境DRhistory、不切片投影20k到80。母版参考按自己的真实输入cache一次，不混用母版与candidate身份。
2. 明确新增 **N80合法低趴8秒/fullD0D7** 作用域，不冒称沿用原74评分。五个原合法pose各16个first-episode环境，不扩大关节/改姿态阈值、不带原fall/normal混合分母。记录首次连续25控制联合credit、首次时间、最大连续good、终点全部条件与credited_and_stable_at_end；原height≥.23/gz<−.984807753/v<.03/omega<.2/双wheel>1N/chassis<1N、8s400控制、50/100/.0025保持，无reset拼信用。
3. 先安排三个明确独立seed 20260929/20260930/20261001，逐seed/逐pose分母及错误分列；episode物理终止/timeout/partial不能当接受，未实际执行或采样缺口记null，不把训练29991分母迁到评测。
4. 参考与候选须记录相同pose/seed/初始DR采样键、实际传感噪声与lag协议；只在真实可核对的配对边界内做差。仅seed相同不声称完整配对/PhysX位级复现；若配对证据不全，仍分别完整报告，不编造因果。无需为配对重开已消费旧窗口的权重或raw。
5. 原E3 74+6评分保留本轮0/74，不修改duration/阈值/分母或把新增low80分数合成原skill90%。若新low确认成立，仅是该独立scope的候选保留依据，后续另选原倒地训练/保持策略；Registry不自动晋升。
6. 继续原privateEX/finiteEX/CownerNone/reserve检查、原SDK/actual inner+outer wait/cleanup release，原唯一canonical/训练预算不扩展、不清外国锁/发signal。源适配只满足新scope的真实运行所需，不另开seal/CPU/审计农场；原已验证pi math/缓存/close不重写。已有受控接续器只顺序调用原父，不递交锁或篡改账本。

这是由本轮正向局部证据选择的下一项确认计划；当前无新scope源码、准入、模型输入、SDK或GPU运行。质量goal仍active；本轮全量成功失败/代码/报告按有意义阶段入既有feature-only唯一annotated trial，main只读，模型/raw/JSONL/geometry在stat/read/hash前跳过，不为Git重跑物理或旧once。
