# D5 分部位接触材质适应（2026-11-11）

当前状态：40 分钟训练及9模型1440env同源配对评测完成。选010m作为D10续训候选；40m后半程掉速不晋升。具体结果见 FINAL_REPORT.md。D10本轮同样40分钟已授权，原生推扰探针中。

父模型为 Step7 冻结质量轮 final，SHA256 `23c112b16e9629215c7265124925daaf0f9b6bbbb62be61689c714ba1fc7a772`，iteration 21754。保留独立输出倍率及已有 Step7 DR，奖励和 PPO 配方与上一轮一致。原冻结目录不修改。

轮/机身/导向件的范围、64/64/8 buckets、dynamic≤static 与每 env/碰撞形状 startup 抽样见 PLAN.json。选中形状跨 reset 固定；未选中形状保持已有 Step7 轻量材质 reset。78D critic 的六个材质槽报告实际左右轮三元组；机身/导向件无额外专属槽。35D actor 和 6D action 不变。

探针实际结果：numerical=0，reset=0，最大闭链 0.63753 mm；8 次 reset 后三组选中材质变化 0，critic 材质编码误差 0。质量/惯量回读及输出倍率/原电机包络验证通过。

证据在 evidence/；训练中的动态统计不代表固定任务毕业结果。最终配对 PhysX 将比较同一随机属性与初态下的父模型和所有 5 分钟检查点；MuJoCo 名义结果单列。

D10 源码语义修正：目标机安装的 `push_by_setting_velocity` 实际以 `vel_w += uniform_delta` 对世界 XY 速度添加增量，z/角速度不变，不能仅凭函数名称解释为覆盖当前速度。原 README 描述已更正。
