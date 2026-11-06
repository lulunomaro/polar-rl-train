# R30：观测器E1单创新权重修复，新seed配对——部分改善，仍未通过

**E1是真正改变反馈输入的观测器候选，不是只读副路。** 旧控制力矩M1/M2/M3=3/3保持封存、不采用；本轮首个独立观测器模块候选E1=1/最多3，不改LQR/K、120–4差分PD/整形或原PD目标-D4-currentPD-DC-gain-DC，不开力矩/增益网格。默认共享runtime/原估计器源码仍未写。

## 唯一改动与新软件证据

[候选源码](<../estimator_cauchy_e1.py>)只把原重力创新乘子`max(0,1-r)`换为`1/(1+r*r)`，r=innovation/既有innovation_limit；复用原limit=1m/s²，不搜索系数。**原重力模长门、accel_correction=1.5、误差限幅、KF/时标保持与其它数学不变。** 模长门为0仍为0，未把confidence全开；Cauchy远端衰减，非独立噪声标定/概率/误差界。

[派生回执](<../ESTIMATOR_CAUCHY_E1_V1/SOURCE_DERIVATION.json>)记录单乘子AST替换，恢复该节点后原审计update AST完全相同；额外非finite创新/尺度guard显式记录。原R29审计hook不改行为，未将既往真值残差均值回流，也未改roll混合时标近似。

[全新check001](<../ESTIMATOR_CAUCHY_E1_V1/check001/RESULT.json>)454断言：11个数值点含极端值、范围/单调/原模长零门/disabled-scale约定/nonfinite、64理想静态包和40个新加速度扰动包。静态state14差0，同E1 witness差0；扰动下baseline–E1 state14差.0292824（混合SI分量，仅证明输入会变，不是机器人精度或性能提升）。简化geometry stub，0P0 FK/模型/forward/物理/旧QA/raw，该check已消费。

## 新配对冻结与可比性

[协议](<PROTOCOL.json>)在新抽样前冻结：**同一新seed520200、两个fresh模型/FullDR实例**，baseline和E1各12s。不是重跑旧case；是一份episode随机设置的配对复现，不是两个独立DR样本。2个单线程worker，总物理CPU≤4。

场景仍真实全29×16mCAD/P0圆柱胎/300N60mm（k2000/d3未实测）、新名义地面带；站0–2、+.3m/s2–8、停8–12，yaw0；原门槛与评分窗逐项保留。520184/185和520112–115仍暂停，未强制D3或按结果换seed。E1结果明确observer_changed/system_changed/controller_changed=true（这里包括反馈变化），另列controller_torque_policy_unchanged=true；baseline为false。同变体witness差0不代表baseline–E1等价。

[唯一小结果收集](<COLLECTION001/RESULT.json>)只读新2result+2meta、0raw/回放/FK/积分；pair checks全true：DR初始收据逐项相等、初始qpos37差0、LQR K差0、同冻结协议、每例1model/1FullDR、每例1200控制/24000物理、同变体审计各差0。实际D3均0，本pair不覆盖10ms；未单独逐噪声流对账，不假称两系统所有测量值相同（真实轨迹本来会随反馈变化）。

## 实际配对结果

| 指标 | 原版新baseline | E1 |
|---|---:|---:|
| 原case screen | **FAIL** | **FAIL** |
| 原false门 | whole0 | whole0 |
| 左/右主轮>1N支持率 |96.980/97.565%|98.030/98.560%|
| whole all-positive-normal-sum≤1N评分点 |39|25|
| guide/hard |0/0|0/0|
| 评分窗roll峰 / RMS rad |.05190329 / .02838462|.02300448 / .01408241|
| pitch峰 / RMS rad |.02599146 / .01234359|.02813919 / .01327317|
| 稳态速度RMSE m/s |.02196401|.02003093|
| 末段停车速度RMS m/s |.01526790|.01842144|
| 行程 / 最大横偏 m |1.774816 / .077475|1.820341 / .070299|
| 重力校正权重均值 |.1253064|.4061362|
| 权重恰0次数/1200 |690|8|
| 9–12s held-roll同sensor真值残差RMS rad |.03724005|.01681172|
| 9–12s pitch同command真值残差RMS rad |.00425614|.00454546|
| 墙钟耗时 s |50.1954|49.3650|

每例1200控制/24000真实物理、评分窗2–12s的20000接触点。whole点不是宏观飞行事件。两例停车门均过，E1停车数值略差、pitch也略差；不能只挑roll/25<39宣布总体通过。两例全24000原两DC改写均0，非电流/热/硬件输出扭矩/送达证明。旁路匹配参考各自变体，0差不证明两个观测器相同。

### 新暴露的适用范围缺口

**两例new_scenario_scope_valid均false**：100Hz全311几何缓存XY超出既有名义带，baseline最大.033822908m、E1最大.025536018m；姿态设计界仍true。原16性能门只有whole0失败，但这项独立场景scope也未过，不能从pair_valid推出通廊资格。缓存为末PRE/age.5ms，不是连续扫掠。原R26最坏通廊证书继续false；未扩带、放宽门或隐藏越界。

这是一项同参数配对的局部反馈效果证据：E1让重力校正更可用、roll误差/roll姿态及低支持点改善，但既未消灭whole点，也未闭合场景域，不能证明先前所有DR失败仅由创新门造成。**E1暂不切入默认runtime，不定技能通过/95%可靠性/实机资格。**

## 软件prefix/数据与后续

首次[配对准备器](<../prepare_estimator_e1_pair_v1.py>)把已知meta续行锚点写17空格而源16，失败在派生目录/模型/物理/seed抽样之前；[原log](<../prepare_estimator_e1_pair_001.log>)保留。[一次根因回执](<../ESTIMATOR_CAUCHY_E1_V1/PAIR_PREP_ATTEMPT001.json>)和[唯一AST恢复](<../prepare_estimator_e1_pair_recovery001.py>)只改一个call的两个literal，缩进取自真实语义行，不扩泛化重试、不覆盖原失败。此后两例均exit0/完整，job pwsh-5451f6e3f3c14fd7和pwsh-1801d79207134eda均已收，勿重收/重跑。

两个新case的六条大raw只producer边写收据，不读payload归档或额外归约；该collection一次预算已消费，所有旧once预算仍消费。无新代理/GPU/SSH/PPO/硬件/依赖，无额外源地形查询。累计v2为8名义+5DR仿真=13例、15600控制/312000物理，但DR独立设置仅4份，配对不充独立样本。

下一步冻结E1公式，不把partial improvement当通过、不立刻扫E2系数；把观察域越界与性能门分开，优先用已有小统计约束后续有界同协议验证/名义回归范围。旧力矩3/3不重开、暂停seed不动、整体0/36/Goal active。任何新观测器候选仍需先给明确机制/预声明比较，不借新名换名义控制网格。
