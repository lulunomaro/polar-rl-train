# E1命令保留修复：实际保存边界与下一审查

E1连续训练后的旧能力下降是真实行为问题。全旧actor/critic/std/optimizer、D1–D7及随机流恢复已有实际验证；gate未训练。当前证据不支持把退化归因于漏恢复或MoE路由。窄范围新课缺少旧命令练习是待验证解释。

华南虎公开源码使用持续、受地形条件限制的旧直行/旋转等命令采样。已审V14运行的是ActorCritic/PPO；CLI支持MoE/CMoE不能作为永久抗遗忘证明。我们借鉴持续旧命令练习：保持原35mm和五族比例，只在实际plane网格支撑、净空核验环境加入signed直行和低速world命令，其他地形保持gentle yaw0，额外私有随机流明确保存与恢复。没有改reward、学习率、硬件、时钟或训练地形配额。

首300s source364的完整129四case审查，对选定32058来源：world62/64→63/64，负4π5/8→7/8，正4π仍8/8；35mm完整后支撑前23/27→24/27，倒仍27/27。三个前进有效前缀未完成后支撑，原false/残差保留。这只证明一次短窗的行为改善。

随后唯一900s同范围source365已自然完整保存。own32104 SHA `f5b1623e71fc5d6f3682ca19594bdf43db5a391ce9fc046ec48f8ce90dde234a`，CPU102/source365/72snapshot，42updates、20.16M环境策略步、4032实际回调，ordinary/integrity/unknown0、nonfinitefalse；原父实际920.4243905544281s仅一次结清，剩318850.0927927494s为退出后的idle快照，新增预算0。完整sameG3地形与新增command-private状态恢复通过。父、guardian、trainer均实际退出；这是合法审查边界。

新130冻结四case已自动发布，当前已完成 `clk2500-closure-episode-d3-130-e1-g3-command-retention-matched-retention-flat`；其余3份结果尚未生成，attention为空。需完整跨机字节、NPZ、ground/contact/参数/root30q和signedcircle审查，再直接与129来源比较。该900s的旧能力保持尚未宣告通过，不能自动第三块或升50mm。

RewardManager签名、SDK选格、额外私有RNG归属、savedepisode+1断言的四次拒绝与独立修复均保留；没有用失败预检权重继续正式训练，没有热改活跃源码。全部新报告和monitor回执纳入该阶段普通Git补充，最终remote/tracked以工具输出为准。
