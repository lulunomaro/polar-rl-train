# MOD4v2：一次新的逆向低速实际执行链/源时刻观测

## 本次真正执行的内容

- [冻结协议](<PROTOCOL.json>)、[生成器](<../prepare_observability_v1.py>)、[新runner](<run_reverse_observe.py>)。
- 唯一新case `v2_t01_reverse_observe_nominal_520130_001`：公开flat_run从另一端x=-5.5m/y=-1m/yaw=0初始化，2–8s给-.3m/s、其余停车，总12s。公开原路线两端为-9和-5.5m，避免从-9m继续倒向未声明延长段；这是公开初始化，不是运行中移根，也不是趴地自然起身或行驶换向。
- [实际结果](<runs/v2_t01_reverse_observe_nominal_520130_001/result.json>)：fresh model/FullDR各1，1200控制/24000真实MuJoCo积分步，49.1461555s墙钟；不是stub、旧case回放或实时WCET。
- 原P0全机构/300N60mm/圆柱胎、最新版48k CAD、.5ms/Newton100、100Hz、新v2 K/trim及原PD→机械投影→D4→当前PD→DC→gain→DC均保留。仅新诊断Plant显式启用旁路；[默认runtime](<../runtime_v2.py>)未接入。旧正向和M1失败均未重跑。

## 筛选原样保留，整体仍失败

| 项 | 本次结果 |
|---|---:|
| pitch峰/RMS(rad) | .0162915787 / .0076134100 |
| roll峰/RMS(rad) | .0322384804 / .0104968428 |
| 低速vx RMSE(m/s) | .0202962811 |
| 沿反向计划进度(m) | 1.8234572234 |
| 最大横漂(m) | .0454769702 |
| 最后停车vx RMS(m/s) | .0287206321 |
| 左/右主轮正法向>1N占比 | 93.640% / 98.540% |
| 所有环境正法向总和≤1N | 76个.5ms点，最长连续.5ms |
| guide/hard | 0 / 0 |

非接触检查全true；左主轮仍未达95%、整车低正法向点仍非0，因此case_screen_pass=false。孤立低力点不直接等同宏观飞行。机身中心x范围[-7.323457,-5.494143]m；初始平衡有约5.86mm向前微漂。附加±.25m路径诊断不是原T01门，也不构成全车足迹/全路线资格。方向和初始位置与旧正向不同，不作为等条件改善证据；T01/全36项/DR/可靠性均未收口。

## 原执行链的2kHz私有记录

[可选组合Plant](<../observed_bridge_v1.py>)使用既有[记录mixin](<../actuation_telemetry_v1.py>)，每个原apply/clip/contact hook只调用原路径一次；[流式记录](<../diagnostic_stream_v1.py>)在写入时生成SHA，无归档payload重读。

- 1200个窗口×20步，24000行，两个原DC阶段六轴changed计数**全部0**；功率阶段后held值与第二级输出差异也为0。20000评分步及左/右低支持1272/292点、整车76点均同样无当步DC改写。
- 左主轮最大法向1796.740N发生于PRE 8.513s，实际同一子步held负载侧Nm为[2.909443,-3.453945,.010661,1.794364,-3.150215,.185670]；这是模拟驱动保持值，不是硬件测得输出扭矩。
- [新控制trace一次归约](<REDUCTION001/RESULT.json>)核对1200窗口与物理计数，目标改写/共同分支抬升累计1次，仅control_index=1。此粗计数未区分微小抬升和物理域clamp，不是机械撞限位或完全没有目标改写的证据。
- 结论只覆盖本新12s例：两级DC输入/输出未发生改写。不是额定电流/热保护/功率/通讯交付证明，不是唯一因果解释；**旧正向/M1的2kHz实际限幅占比仍未知**，不回填。

## 公共信号归一化：已实接Plant，但只是观测

[public_signal_adapter_v1.py](<../public_signal_adapter_v1.py>)明确将publisher的endpoint/held_command规范成已知点窗、sampled_boxcar规范成真实sampled_mean；值来自原公共Packet，角色逐项核对。未知时刻/边界保留None，不以packet epoch冒充同步。

- 1200次提交，起始2帧分别缺时间历史/无插值括号；1198帧实际凸插值，无外推/Schema错误/锁存fault。
- 共同评价时刻比packet epoch早5.25ms；查询在原tick物理结束后，所以真实诊断到达age约15.25ms，未把额外10ms运输时间擦掉。
- 例如control2以.01475s评价：编码器q由.01和.02s以.525/.475权重插值；gyro仍是[.01,.0195]20点均值；模拟驱动保持量来源为.0095/.0195s。它们不是同一原始瞬间，均值窗口偏差未消失。
- 所有帧numeric_bounds_complete/force_input_ready/hardware_sync_proven均false，alpha未知；时钟/噪声/曲率界和真实输出扭矩标定未提供。proper_imu_B仍不是已完成角加速度杆臂补偿的chassis_origin量。不得给[力代理](<../CONTACT_PROXY_V2/contact_proxy.py>)、FSM或控制器使用，原3ms/.55/.8门不改。

## 原始数据/预算

三份新raw都只以producer receipt索引；控制trace约14.17MB/1200行，仅[reduce_control_once.py](<reduce_control_once.py>)新问题一次顺序读已消费；接触约10.85MB/20000行、执行链约36.61MB/24000行未为事后分析或归档重读。旧raw读0、新归约物理0、不作档案hash重读。原case、生成器、REDUCTION001及两份log均保留，不重跑。

全局累计4个v2名义物理例4800控制/96000物理；观察诊断不是M2，仍仅M1/最多3已消费且未采用。停止同类只读探针；后续第二机制须从公开轮腿几何/实际证据给出可解释推导，最多先1个新名义例，不以未知力信号闭环或参数网格替代它。Goal继续，整体0/36不变。
