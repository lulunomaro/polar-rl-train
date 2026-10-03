# 5rad/s中间档全量物理预检拒绝

从最新正式16450完整源进行auto0028原80env15s站跑和88env15s cap4自转验收，原flat准入、原spin_skill、修正参考点spin技能均通过。white_v2、物理、奖励、PPO、硬件、闭链reset不变，只有登记的yaw命令上限4→5。22env3秒短检查physical_smoke=true、nonfinite=false，但短spin_skill=false仍保留，没有称15秒毕业。

auto0029的20k×120步1.2秒冻结物理检查，无PPO。20000样本无终止、无NaN；闭链0.2661mm、mimic0.001827rad，两个reset实际质量/惯量/摩擦/输出参数读回通过，非轮材料、局部COM、PD、弹簧和关节参数误差为0；四采样环境承重地面法向+Z。

但最大倾角15.265189deg超过原物理guard的15deg，physical_smoke_pass=false；原combined pass=false和最大高差72.8026mm警告保留。没有忽略最坏环境、降低阈值或把无终止等同全部通过。原短技能和旧strict窗口统计不改。全量报告缺少最坏环境ID，所以不能直接把这次异常归为纯±5组或断定与6档滑移同因。

监督器如实拒绝并恢复4rad/s/white_v2，保留源和所有报告，追加5拒绝记录而保留6旧拒绝，进入targeted_repair_hold。128env PPO及5档45min正式试训均未启动，charged165433.3585538864秒和总252000秒保持，冻结评测未另加时间。

接续已安排同源16450、同seed20260927、同white_v2的cap4/cap5全量只读诊断，保存完整root/q数组哈希、逐环境峰倾角/高度及最坏环境时序。必须完整初始root/q严格相同、原cap5物理结果复现，才能讨论命令上限的差异；当前基线未完成，不预先声称是旧复位瞬态或提速造成。正式修复/续训须依据实际证据，不能重跑已有one-shot或删除拒绝记录。
