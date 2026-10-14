# 同完整20k来源的左均值中点初始化：CPU数学准备

真实来源为 `MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_formal_final_actual/0_model_32635.pt`，SHA `2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971`。再次直接CPU核验19044152字节、107个floating字段finite、99项20k perenv字段；原文件SHA及加载后完整状态树fingerprint前后相同，CPU RNG状态不变、无CUDA。

本计划仅量化：初始left最终mean row0的W复制本来源实际hip row1的W，bias复制hip bias再减0.2343。实际hip bias为0.33378705382347107，计划left bias为0.0994870513677597。其它五mean头、shared trunk、critic和全部std不变。实际left std为0.6773233413696289，本计划保持该值；不存在“再把std归1”的操作。若后续采用，只清Adam参数7/8的mean row0 exp_avg/exp_avg_sq，保留std参数0 moments及全部17个step计数。

原6action、clip±6、腿scale0.5及CAD区间 `crank−hip∈[−1.0843,0.85]` 完全原样。候选的同hidden输入数学均值差为−0.11715rad，即该区间中点。已用真实80×1500个保存hip raw mean做CPU反事实均值数学映射，未使用可能已在vec.step后更新的policy_obs来伪作同control actor输入，也未重放actor或物理路径。映射后的均值差为 `[−0.11715000868,−0.11714994907]`，每个样本均严格在区间内，到上下边界各约0.96715rad。

对任意实数hip raw也有解析界：clip单调且1-Lipschitz，`clip(h−0.2343)−clip(h)∈[−0.2343,0]`。乘0.5后差在 `[−0.11715,0]`，全域最小lower margin约0.96715rad、upper margin0.85rad。边界例使用确定性数值，不生成随机fixture。这里证明的是CPU数学均值合法性；实际CUDA线性层舍入、完整恢复和物理动作仍须自己新scope实证。

保持真实std0=.677323、把hip固定在原保存mean时，数学左Normal落入原联合输入合法区间的条件概率如下：

| 环境 | 当前2b mean的15s平均条件概率 | 中点计划的条件概率 |
|---|---:|---:|
| 6 | 1.234e−6 | 0.99570714547 |
| 15 | 1.138e−6 | 0.99570714547 |
| 21 | 8.334e−7 | 0.99570714547 |
| 69 | 2.398e−4 | 0.99570714547 |
| 72 | 6.618e−5 | 0.99570714547 |
| 67 倒向 | 9.515e−4 | 0.99570714547 |
| 70 倒向 | 8.941e−6 | 0.99570714547 |

这不是完整hip/crank联合随机采样概率、实际机械动作实现概率、通过率或课程晋级线。没有创建任何候选权重；不能凭上述数字选用生产策略。

独立新身份准备为profile `left_initial_joint_interval_center_keep_saved_std_v1`、KEY `LINUX20K_LEFT_JOINT_CENTER_KEEP_SAVED_STD_INITIALIZATION_V1`。先用完整2b来源恢复原13项状态，旧left initializer的历史KEY保持原样且不重复；再显式一次新mean初始化，保存独立新KEY、追加第14项own CPU/CUDA磁盘roundtrip和episode+1证明。未来同新身份恢复必须全exact且不再次初始化。所有准备字段都不是已执行的GPU合同。

旧17b512的同中点mean-only因素实际仅1/7、ordinary20，已拒绝；旧margin014 mean-only仅0/7、ordinary3。其来源、std和学习历史与完整20k2b不同，既不能拿这些旧失败涂成通过，也不能由新CPU数学推断它们的机构效果会自动改善。更内域均值可能损伤原平地、转圈、世界方向和起伏技能；当前三项skill行为仍待实际完成。正常PPO也可能再次把均值移出联合输入域。

下一只有在完整行为和scope决策合理后，才能独立新fullstate/native/PPO/fresh及原完整四case评测选择。最多第二学习块、随后完整审查，无盲第三/70。没有live耦合、teacher、heading correction、真值gate、DR/reward/clock/hardware变更，也没有SSH、GPU、PPO、预算或Gitcommit操作。本目录CPU源码和报告待根代理统一Git归档。
