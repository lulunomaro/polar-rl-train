# MOD4 R0 shallow terrain: authorized first 40-minute round

2026-11-11 用户授权按 R0 推进。父为 square1_030m / iter22618 / SHA d5e176401c20dd1b88a74003f7d4993aadc9a9cda301f042953de08fb6108851。

保留完整 DR、名义819/DR3277、35/78/6接口、2.5/10/20ms、TGS32/4与−1.0e²奖励。新增浅地形与最低等级出生、交叉20%平地分配、reset边界能力课程。完整PT每5分钟保存；本轮40分钟，不自动开R1。

R0去掉中级台阶，地形4等级覆盖difficulty[0,.35]，70列让出生分散；随机起伏显式按难度调幅，因为IsaacLab原函数忽略difficulty。地形边界按timeout单列。

当前为实现/探针阶段，真实启动与结果随证据更新。
