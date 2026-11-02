# 名义yaw bias：静态fixed-chart模板，不是稳态纯转解

数据：[YAW_NOMINAL_BIAS.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/DATA_DIAGNOSTIC/YAW_NOMINAL_BIAS.json>)；脚本：[compute_yaw_nominal_bias.py](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/DATA_DIAGNOSTIC/compute_yaw_nominal_bias.py>)。

## 直接可用的数学系数

执行顺序：left_hip, left_crank, left_wheel_spin, right_hip, right_crank, right_wheel_spin。单位为输出关节Nm；XMLgear=1，勿再乘9或15.8。

`tau(omega)=tau0 + c_even*omega**2 + c_odd*omega`，由0,+1,−1rad/s计算。

- tau0=(6.591811364, -7.635446745, 2.648938846e-10, 6.572299328, -7.619720368, 2.648974373e-10) Nm。
- c_even=(0.01457097555, 0.04165719544, 0.01455244217, 0.01455377418, 0.04167105923, 0.01455244217) Nm/(rad/s)²。
- c_odd=(1.776356839e-15, -1.33226763e-15, -0.0515227646, 4.440892099e-16, -4.440892099e-16, 0.0515227646) Nm/(rad/s)。

若父已有gas/gravity FF，只加delta项，避免重复叠加tau0。系数不是新controller/硬件binding。

## 逐点残差与边界

|omega rad/s|lstsq residual x force N|其余6维残差Nm最大绝对值|混合单位残差norm（仅数诊）|FF超当前DC边界个数|
|---:|---:|---:|---:|---:|
|0|1.64144e-09|5.43095e-09|5.67358e-09|0|
|1|-0.0319882|0.105836|0.110565|0|
|-1|-0.0319882|0.105836|0.110565|0|
|0.5|-0.00799706|0.026459|0.0276411|0|
|-0.5|-0.00799706|0.026459|0.0276411|0|
|2|-0.127953|0.423344|0.442258|0|
|-2|-0.127953|0.423344|0.442258|0|
|2.6808082|-0.229891|0.760616|0.794598|0|
|-2.6808082|-0.229891|0.760616|0.794598|0|
|4|-0.511812|1.69338|1.76903|0|
|-4|-0.511812|1.69338|1.76903|0|
|12.566371|-5.05138|16.713|17.4597|0|
|-12.566371|-5.05138|16.713|17.4597|0|

±0.5/±1/±2/±2.6808/±4/±4π范围内二次＋一次拟合最大误差 8.24896e-13Nm。精确拟合的是这个固定chart，不证明真实spin等价。

## 关键限制：pivot/侧向滑动

继承full_reduced的q=[rootWorldX,yaw,pitch,Lhip,Ldelta,Rhip,Rdelta]固定名义q，v只在yaw列非零。chassis origin的worldXY固定，而wheelmid_B.x=−0.0342023945m。
静态mj_jacBody表明omega=1时左右wheel center body速度分别约(−.2188,−.0342024,0)与(+.2188,−.0342024,0)m/s；4π时共同侧向速度约−.429800m/s。因此它不是围绕wheelmid/COM的精确无侧滑纯转chart。

此外：使用0.0637圆轮支撑chart，不是姿态依赖的真实凸包接触；Gᵀ(passive−bias)不纳入实际接触constraint reaction，固定chart未展开完整moving-reference关系。每点7维Btau+f残差均已报告，未假定可精确平衡。

R01实际yaw约2.6808时，四腿even delta仅约(.105,.299,.105,.299)Nm；与R01腿间约数十Nm的观测差别相比，不支持“漏掉这个ω²项就充分导致劈叉”的强因果结论。固定零yaw gain/参考点/接触耦合失配仍是待对照假说。

## 速度和轴证据

双wheel joint轴为+bodyY；正wheel spin的底接触点相对轮心速度向−bodyX，无滑时轮心向+bodyX。正yaw需左轮负、右轮正，与R01符号一致。主惯性PCA轴不改变joint axis；这些是软件模型证据，未验证实际CAN极性。
controller wheel no-load=55.3557rad/s，metadata缩放值55.3649085074rad/s，仅差−0.0166324%；输出转子总比15.8，metadata rotor no-load≈8353.396rpm。R01尾wheel速度峰值约53.710rad/s，对应rotor≈8103.73rpm（controller no-load的97.0273%），均值约−4818/+3518rpm。
no-load为零正向电机转矩点，不是外力驱动/再生区的绝对硬限；工程转矩转速曲线、热/峰值持续时间、硬件最大rotor转速未实测。leg输出no-load160rpm×9=rotor1440rpm，XML输入仍输出关节Nm/rad/s。

## 零步与来源

RobustPlant实际构造一次，仅tmp参与403次forward；step/step1/step2均设fail guard且调用数0，tmp时间0，主plant.d与tick保持原样。没有物理rollout/DR重跑、父模块或模型改写。
所有source SHA最终复核通过；缺失的source_snapshots/r01路径检索错误保留，不假称该快照存在，计算绑定实际读取的当前源码SHA。
