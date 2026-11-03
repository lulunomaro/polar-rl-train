# 手动相对里程触发候选 V1 — 默认关闭、尚非技能毕业

[控制器](<controller.py>)明确继承原[Landing V3](<../MINIHOP_LANDING_V3/controller.py>)，不是加入AirRetract V4，不改已冻结H5或任何旧源码。新增的是触发调度，不是接触检测、独立世界定位或自动地形识别。

## 研究动机与参数边界

旧R55 TRAIN固定1.95s触发时，4503估计distance约1.2573m，而名义约1.1940m；这提示固定时间不固定接近位置，但不证明唯一失败机理。4505另有主轮清杆后guide碰杆顶问题，预期本单因素未必解决两类故障。

新目标1.18m取自**名义TRAIN传感里程**，达到后在当前command中仅锁下一个100Hz tick。名义旧轨迹的调度检查为decision1.94→push1.95；没有读DR抽样值或世界root位置来修正运行输入。相对origin仅取第一个有效estimate，估计里程的漂移、滑移与噪声仍存在。

- `position_trigger_enable`默认False；operator默认亦False。任一未启用即保留旧V3控制路径。
- 开启后，最早decision1s，截止2.6s；等待时旧timer被未来哨兵覆盖，未达距离先INHIBIT超时，而不是回退到1.95s或哨兵处偷偷跳。
- 锁存只改变**未来tick**的trigger；该tick仍按原runner顺序prepare_estimator→packet→estimate→command。当前tick的估计通道不被回改。
- 原pitch/roll .15、speed1.2触发guard不变，且在实际push首tick检查。
- 原push .14、predAir .25、landing参考/K/ff .2s插值、capture blend .1、observer quarantine .5、driver/DR/力与几何成功gate不变。
- 原来push期仍可能用wheel观测；新增触发不把这点改写成提前全隔离。相对phase时长未变，绝对触发时刻可变。

## 当前证据

[零步入场记录](<preflight001/RESULT.json>)为1809 checks/0、0integrator：disabled与旧V3的600组合成command逐bit相同；enabled在同样合成latch时序下600组亦相同，且prepared estimator flags相同。名义TRAIN只作里程调度读取，不重放扭矩或物理，不由日志重建未保存四元数。

[新entry](<../run_manual_position_v4.py>)保留旧main控制loop AST，变更import与诚实的source/result metadata。载入原实际gain loader；物理前[源锁](<preflight001/SOURCE_PREEXEC.json>)记录实际小源SHA。

[计划](<preflight001/PROTOCOL.json>)是新名义flat通过原gate后才准同profile RM。尚无该候选的真实PHY结果，本文件不预称通过；实际以case receipt为准。后续paired TRAIN需新ID，旧R55/H1/H2/H4/H5不重写。

纯Python仿真候选，无C跳跃/最终发送/实板校准/WCET资格。默认contact/flight trusted、world-position trusted和contact-permission均不提升；PH7pending。
