# R61：只检验自转减速期centering门控

动机为既存[stop诊断](<../SPIN_STOP_CAUSAL_V1/REPORT.md>)：operator yaw归零时旧centering立即off，但整形yaw继续约2.09s。没有据此断言它是唯一失效原因。

- 新[controller](<controller.py>)默认`center_through_yaw_decel=False`，直接调用冻结legacy。
- enabled时只在**已active、operator yaw恰为0、forward绝对值<.1、previous shaper.w非零**时保持旧target；不以真实yaw/contact或未来信息决策，不向底层伪造非零yaw请求。
- previous-shaper语义显式：release最多比本tick整形归零晚一个10ms周期；不是当前瞬时yaw、不是已停止判据。
- kt20/cap1.8/lead0.0083900879、旧nominal K/rolling parameter、AHRSgain0、旧phase计划不变；没有R27低spin AHRS或capture切换，没有新的C/硬件接线。

[实际零步结果](<preflight002/RESULT.json>)：24657检查/0失败，2600 synthetic frames disabled的τ/参考/里程/整形等bit相同，enabled首1000frames（首次stop前）相同；整形全2600相同。两stop各延长210ticks，10.00..12.09和22.00..24.09。**不是2600机器人测试或实际PHY prefix证明。**

首[generator v1](<../prepare_r61_spin_decel_gate_v1.py>)在假定旧代码indent时失败，0unit/0PHY，保留[ERROR](<preflight001/ERROR.json>)；新[retry02](<../prepare_r61_spin_decel_gate_retry02.py>)使用AST span导出[v2](<../prepare_r61_spin_decel_gate_v2.py>)，旧源不改，未重放已消费物理episode。

[实际runner](<../run_spin_decel_gate_v1.py>)保留旧force/DC/D4/DR/plant与transition grader，去除truth控制分支，采用每row先持久化再入内存、异常保存既有prefix的[logger](<../streamed_trace_rows_v1.py>)。原actuation调用AST相同。

[新launcher](<../launch_r61_spin_decel_gate_v1.py>)只从旧R26三份配置复制caseID与新flag；先冻结3份profile/源再PHY。计划名义0及配对TRAIN201/202，不是H2新holdout；旧baseline不重跑。名义admission只指完整26s无health/software stop，原skill composite如实另报，不假称admission即技能通过。等待独立pre-exec review ready且父read后launch。

保留原composite/各相位停止窗口/漂移判据；不得因失败延长评价窗或加gain/替seed。即使局部改善也不升级自转停启换向鲁棒性、ARM时序、Power或final-send资格。PH7pending；旧H1/H2/H4/H5与Stage1均不改。

## 实际关闭结果（上方等待review为执行前历史）

独立[review](<preflight002/PRE_EXEC_REVIEW.md>) ready后父read并launch。新3/3真实完整，7800controls/156000物理步，**composite0/3（两DR0/2）**，见[结果](<../reports/R61_SPIN_DECEL_GATE_FACTS.md>)。两DR的XY改善不等于泛化：名义最终XY反而由.053797增至.284652m。名义first-stop最长.49s仍小于原.50s；201虽然两个停止相位hold均达到要求，原wholecase严格yaw跟踪门槛仍失败；202仍漂移/最后停止失败。保持默认off，不推荐替换冻结H2。

实际第二stop请求为22.01s附近，centering保留至24.10、下一tick24.11释放；不是synthetic的22.00..24.09逐tick保证。两个stop均210个真实control ticks；数据记录source-label清楚，不冒测得停止。分析只读新trace各一次及旧小result，没有重跑旧baseline或读旧raw。
