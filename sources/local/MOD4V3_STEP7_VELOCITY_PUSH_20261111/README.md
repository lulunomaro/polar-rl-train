# D10 速度推扰适应（2026-11-11）

第二轮已授权；父权重已选 D5 010m，iteration21882，SHA49a2bb7b...；原生 interval 探针通过，4096环境40分钟训练已启动。累计保留 Step7、质量、输出比例与三组材质 DR。直接调用目标机原生 push_by_setting_velocity，通过 EventManager post-step interval 触发，timer 按参考 episode reset 重采样。世界 XY 加性速度增量每轴 ±0.25 m/s、每 env 5–10s；z/角速度保持。评测安排推扰前/恢复/恢复后稳定窗口。

训练记录另存实际推扰总次数、触发过的环境数和最新世界 XY 增量最大值。原父类摘要中的轻量 wheel_friction_range 不是 D5 后的真实轮材质；本轮摘要报告真实左右轮静摩擦范围，详细三组属性以 contact_material.groups 回读为准。未选中形状仍保留已有 Step7 all-shape 轻量材质 reset。

D5 010m 是下一轮训练候选，原 Step7 主冻结基线保持。D5 实际 DR 两前进项通过10/10、8/10；原父为9/10、9/10，不能宣称此候选全面优于原父。后半程40m掉速，保留所有失败证据并不接用该末权重。

原生探针64env×80steps：numerical=0、最大闭链0.478094mm，强制选择32env的interval触发32次；世界XY增量回读、z/角速度保持、未选env保持、episode reset计时器语义全部通过。
