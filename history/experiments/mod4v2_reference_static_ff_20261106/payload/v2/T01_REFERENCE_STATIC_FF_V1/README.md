# M2：参考姿态名义静力差分前馈——唯一新名义例，未通过/未采用

## 设计与接线

- [独立静力设计](<../REFERENCE_STATIC_FF_DESIGN_V1/RESULT.json>)复用封存SDK-free 31-body MCI/气簧/Jacobian。F0从已有trim自然反解，约70.057416/70.168100N，不是在线Fn或mg/2硬填；两目标构型/内部18次纯FK/0 MuJoCo compile、forward、积分。原解析草稿未执行。
- [控制器](<../controller_reference_static_ff_v1.py>)在C1平滑reference q处计算 `tau_static=load-tauGas-J.T F0` 的相对trim变化，**只加左右相反关节力矩分量**，原共同LQR、120/4差分PD、shaper、K、yaw及原PD→D4→当前PD→signedDC→gain→同DC不变。按已有effort余量整体同一scale收缩；不是Cartesian力零和/完整逆动力学保证。
- [独立runtime](<../runtime_reference_static_ff_v1.py>)和[唯一协议](<PROTOCOL.json>)不接默认runtime/UI/BSP。固定静态proper=(0,0,9.81)、零rate/acceleration只是公开名义设计假设，不是把未知传感alpha/qdd改成已测零；无force proxy/接触真值/DR样本回流，300N/60mm、原碰撞与门不变。
- [几何耦合计算](<../VMC_DIAGONAL_DESIGN_V1/FORMULAS.md>)给出归一化rho=9.507%；单纯虚拟对角化会令关节刚度一向-8.68%、另一向+10.51%，并非巨大串扰证据，**未选/未跑该候选**。实际bridge API附加核对因zero-SDK约束跳过，明确未核。

## 唯一实际新case

[结果](<runs/v2_t01_reference_static_ff_nominal_slow_520141_001/result.json>)、[配置](<runs/v2_t01_reference_static_ff_nominal_slow_520141_001/config.json>)、[日志](<reference_static_ff_001.log>)。

- 新seed520141名义、实际全CAD、公开flat_run原起点(-9,-1)，正向+.3m/s在2–8s，0–2站立/8–12停止；不是旧case重放。与原正向名义profile相同，单例不作可靠性/唯一根因结论。
- 12s，1200控制/24000真实MuJoCo步，fresh simulation model/FullDR各1，65.8383s墙钟，完成rc0；**case_screen_pass=false**。

| 指标 | 原正向名义520111（冻结历史） | 本M2 |
|---|---:|---:|
| 左主轮>1N支持占比 | 91.570% | 92.210% |
| 右主轮>1N支持占比 | 98.035% | 98.715% |
| 全机正法向和≤1N的.5ms点数 | 92 | 43 |
| roll峰值/rms(rad) | .0298455/.00941665 | .0332899/.0210572 |
| pitch峰值(rad) | .0170887 | .0180326 |
| 速度RMSE(m/s) | .0406789 | .0420189 |
| 行程/最大横偏(m) | 1.622586/.0410681 | 1.626089/.0379770 |
| 停车vx RMS(m/s) | .0193254 | .0164248 |

非接触检查全true，guide/hard=0；**每轮≥95%与全机低支持点=0两项仍false**。支持计数有改善，roll RMS反而上升；不得写成M2成功/全T01通过。低力点不等于宏观腾空。暂停该候选，不改默认控制器，不自动新seed/DR/延长case或扫FF系数。

## 实际观测与代价

- 本新12s全24000实际子步，原两级DC六轴改写计数全0、第二级到held变化0；`d.ctrl`是仿真保持命令，不是测得的电机输出，不把本结果回填旧正向/M1饱和占比。
- 前馈1200调用，投影后关节额外峰值约1.9572/2.0121Nm、轮端0；余量缩放1次/min0；被去掉共同项峰.5753/.7311Nm，额外关节共同和残差0，不保证物理轮端力/机身矩零和。
- 本实际运行SDK-free terms共1201(含初始化1)，内部FK10809，不是1201物理case。前馈求值总17.0882s/最大35.9062ms，平均约14.24ms；整个command墙钟21.9431s。**未取得100Hz墙钟实时性/ARM WCET资格**，simulation100Hz时钟仍为原.01s。
- 公共1198插值观测，缺alpha/标定/误差预算、force=false；旁路不回流。3ms/.55/.8门未改。
- 三个raw行数/bytes/SHA已在producer写流时记录于结果；归档只用该既有回执，不重读/重hashpayload。当前新raw尚未额外归约；旧正向/M1/逆向一次归约预算均已消费。

## 准备错误与边界

[原准备脚本](<../prepare_reference_static_ff_v1.py>)首次3空格锚点与实际2空格不符，**在派生runtime/目录/model/物理之前失败**，不是机器人失败；[原log](<../prepare_reference_static_ff_v1_001.log>)保留。[唯一恢复](<../prepare_reference_static_ff_retry001.py>)只按实际语义行改一个AST call的两个字符串，成功后才跑上述唯一case；[回执](<../REFERENCE_STATIC_FF_PREP_ATTEMPT001.json>)。不重跑任一生成器/check/设计研究/case。

全36仍0/36，T01进行中；v2失败驱动机制已消费M1与M2共2/3，diag研究不算实际机制。气簧k2000/d3仍未实测，P0主胎为原圆柱而非v1全胎mesh；没有硬件发送、闪写、GPU/RL或自然摊卧起立资格。
