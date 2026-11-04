# V4失效后的单因素METHOD草案——只提案、不实施（PH11pending）
证据仅[RESULT_MIN](<RESULT_MIN.json>)的6个去重事件与[REPORT](<REPORT.md>)；父此前一次读193control，不是本review再开trace；V4源码语义复用已完成审查，静态9poses不重算。
1. 已观测顺序：.31s进LIFT；1.23/1.55/1.83的true POST pitch=.60030/.80242/.95165rad；1.92 PRE估计1.00222触原envelope，POST=.99134。未到CAPTURE/RETURN/VERIFY/BLEND/BALANCE，非6s timeout。
2. .31的h_des=h_clip=-.44051088；1.23保存点h_des=-.62616279、h_clip=-.502536081507324，以后已存有效点同界。首次夹持的准确control未知，只能夹在(.31,1.23]，非“精确1.23开始”。
3. 这是support GOAL共移盒限：goal q4=[-.500000006,-.300000006]×2；1.23实际发布qref hip仍+.09082，实测hip+.07680。goal夹持不等同reference已到界、实际关节到限或motor/DC饱和。
4. 1.55 gamma=.731859、发布crank速度=-.999rad/s，证明当点rate limiter生效；1.92 fault当前goal/ref字段null，只有1.91 lastpub可引用，不补造fault时目标。
5. 全193bin双主轮均每20离散采样>1N，但0bin满足全20无guide/hard；guide3815/hard0。支持双轮+非主轮多点接触，非腾空或已证仅双轮平衡；哪只guide/支点/反作用矩/逐时实际扭矩本文件UNKNOWN，不能断言恰一个guide“三点支撑”。
6. root升高+.068776m、XY .076305m且wheel-rate<.63，均未阻止倾倒；request峰值约legs13/20Nm、wheels.189Nm非actual。PRE估计与POST差max .0666875含异步/窗/动态效应，不单据此认定AHRS偏置根因。
7. 既有静态end构型仅是假设姿态及共同wheel seating；不覆盖持续guide反力、腿动反作用、实际被动闭链/参考跟踪和动态到达。现象相容于“先抬腿但body-wheel回路尚未介入”的假说，也相容于legpath/多点接触主导；未证唯一原因。
8. H_W可证伪隔离草案：若父另行选择新TRAIN，仅把LIFT的wheel policy从quiet damping换成已有nominal K的pitch/rate有界pose+damping支路；不引入全GC距离/vx/yaw项，不借discarded全GC rail作输出。具体使能域须父另锁，是sensor域而非contact certificate。
9. 锁住原leg-reference规则、-estimatedPitch目标法/盒限、single-gamma/.999发布速度、support q/tau trim、2.2lift/.25dwell/1return/原verify与blend、observer、model/driver及全部旧验收；不另换leg规划/gain/DARE/参数。闭环pitch改变仍会改变realized qref，这是同参考法的wheel-policy单因素，不是逐时leg路径相等或纯直接轮力矩因果；旧V4不重跑。
10. 保留既有quiet±2与pose±3Nm分支各自cap、>12rad/s同向软制动、encoder .50m、6s、pitch1/roll.25包络及原strictsuccess；未知contact依然未知。不得以越界、速度、运动或guides持续来放宽门槛。
11. 未来若获批，事先比较最小事件：pose分支是否实际起用→pitch/rate→h夹持/跟踪→guides/主轮→阶段/终止；request与实际driver效果分开，私有接触只作离线grade，不输入控制。
12. 若原legpath下有界wheel反馈确实作用仍同样发散/更早guard，则该次条件不支持H_W足以解决；若分支未生效或实际力矩未知，则机制比较不成立。即使改善也不排除legpath作用，亦非站立/全DR/其他初姿态资格；再改legpath需另一个父决策，不在本案叠加。
本草案未选新gain或执行任何代码/proof/model/FK/PHY/solver/QA/Git/agent/Goal；[最小读取账](<LIFT_METHOD_DRAFT_MIN_READ_COUNTS_001.json>)区分父原trace读取与本次只读小摘要。旧case/gates/scores及PH10封源不改；等待父下一决定。
