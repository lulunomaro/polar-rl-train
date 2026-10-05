# DR接管前读者结构错误保留并修正

首次CPU准备读者错误假定平地raw带有顶层profile，发生在新runtime创建、任何worker/PPO/配置/预算变化之前。原平地格式应从mild_initial_parameters读DR profile，nominal flat没有独立参数对象的事实保留。显式修正后目标13项实际数据/故障合同通过。

首次交接读者错误使用manifest.environment；实际原trainer manifest使用env，未发生旧进程退休、账本操作或新worker。按未改的生产ctl.training使用的真实字段修正；保留两份原错误及显式retry记录。两次均非生产训练/物理故障。

额外目标7项新控制器合同验证只允许white_v2→white_v3配置变化，世界目标、奖励、cap、KEEP_STD和solver变化均拒绝，基础环境SHA封存。桌面14项实际报告和故障合同通过，包括新white_v3短回读。缺失/非有限/实际task reset/闭链/初态不配对/错误源均拒绝；有限性能质量只诊断。冻结canonical完整字节不变。
