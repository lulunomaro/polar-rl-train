# 六档成熟后首次八档短物理拒绝

固定最新paired成熟19975/6white_v2，原控制器自动仅把cap6→8（auto0073记录）后执行auto0074：22env、seed20261002、white_v2、300steps3秒冻结预检。22/22存活、nonfinite=false、closure0.210644mm/mimic0.001691rad；physical_smoke_pass=false。没有启动后续20k物理、128PPO或正式8档PPO，奖励/DR/硬件/物理保持。

此次拒绝有独立真实物理依据，不是已取消的0.15滑移硬否决。纯+8 env7/18的peaktilt14.926383/17.101288deg，其中17.101288超过短物理原15deg门槛；控制采样gap44.759311/42.719461mm、高差43.843/36.379mm，动作delta0.516604/0.434986与d20.521671/0.443787，双轮低载22/17ms、平均XY速度0.415983/0.339347m/s，轮速峰55.351/55.278rad/s且出现实际硬件rating clip。启停反向+8 env9/20也有13.653–14.213deg、gap29.012–39.535mm、delta0.277323–0.297362、双轮低载16.5–22ms及漂移。纯-8较稳但平均XY速度0.163704–0.168462m/s仍高于15秒原地漂移门槛；3秒只是短诊断，不能当15秒成熟失败统计。

新loaded015/mesh/legacy失败继续影子记录，正确COM/link参考点和.15数值取消原样。3秒报告不满足15秒接触验收完整时长，不能把新长验收的complete_evidence=false说成此短预检缺失接触数据；physical_smoke本身独立拒绝。短窗口看到状态失稳，不证明8不可学习、硬件不可能或具体单项奖励因果。低力不等于腾空，gap是输入网格控制采样代理；不把空载轮速峰当稳定负载能力。

父按规则回实际paired成熟19975/6white_v2并repair_hold，所有权重保留，旧父/guardian已经计划退出，无trainer/evaluator/active段。此hold保存余预算，不是finished，不盲--resume叠6或重复8探针、不删监控。AUTONOMY_STATE.rate_rejected仍实际历史[6,5]，不编造已写入8；auto0074拒绝和STATE.reason保留明确下一8失败证据。

唯一canonical总252000秒三扩展、charged225308.08865308762/余26691.911346912384秒约7h24；本次冻结全过程账本字节精确不变，没有PPO或额外记账。后续需有依据的更细课程或单项行为适应及独立物理/原能力/PPO验收，不能降低真实姿态门槛或盲恢复旧入口。当前用户优先原地小陀螺、移动/FPS/地形延期保持。

本次本机原collect_existing_v2.py假定父永远存活的断言因计划内hold触发，仅读取工具错误，不是生产故障。已使其识别repair_hold/finished且核验无trainer/active段；未改生产源或执行入口。实际原始证据及逐环境REVIEW一并保留。
