# C2：新case接触开断的有界定位
- 三源各一次完整流读：control=1200,contact=20000,diagnostic=1200；旧raw、model/FK/physics/QA/hash/Git/newagent均0。
- 左off=2029、右off=897、wholeoff=165；最长分别0.001/0.0005/0.0005s。1tick episode分别1869/1949、897/897、165/165。
- 每轮总normal均值/峰：L=67.2997052/511.130769N；R=77.4054524/419.401044N；guide/hard=0/0。
- 10个1s计数覆盖2–12s，12个半秒细窗覆盖6–12s；7关键事件保留同control-bin腿qd/请求/末子步actual矩和包时间。接触PRE、packet平均窗及控制快照不冒充同一2k时刻。
- **归约器缺口，非数据缺失：** 本次时钟查找只检查顶层，漏了已存在的嵌套raw_packet.time_s；raw_packet.wheel_vel2也在原日志中。故diagnostic对应、ref/shaped/park/分解及24facet实际轮速关联尚未完成，原false字段不是经检验的时钟不匹配。所需诊断数值未被本次最小输出保留；父已明确停止，不再读diagnostic或补24facet关联。
- 24阶相位/IAT关联未执行；只存了20子步controller-phase开断直方图和0.3m/s、名义r=.0625m的理论约54.54ms facet周期。后者不是实际周期测量，更不是因果证明。
- 未从端点矩推断2k饱和；未用source age≈0断言没有boxcar/filter延迟。数据不足部分明确UNKNOWN，不挑选或编写C3。
