# CONTACT_PROXY_V2 — HW300N60公开名义模型，未接控制器
- 本轮仅写此目录。`PUBLIC_NOMINAL_CONSTANTS.json`绑定实际P0 scene.xml SHA `c19c72d2690dce90fdef56bebd3b36e4c319d47b8ac7152cf42b2d01f6dfd125`；constants SHA `d394608bc662ce5c2b21dd9176668eaa68ebfca7eedac682b218c0a086abc546`。31 body/30 joint/6 connect+4 mimic；质量14.294140288606286kg；胎是P0 cylinder半径.0625/半宽.01m，8 guides半径.015m，不是v1胎网格。
- [export_public_nominal.py](<export_public_nominal.py>)只读P0小XML/参数/manifest/实际kinematics_v2与父已有nominal_gain_v2；未求LQR或重求静力trim。principal diaginertia与inertial quaternion显式转为BODY完整惯量，不照搬v1 fullinertia或400N参数。
- [nominal_model.py](<nominal_model.py>)、[contact_proxy.py](<contact_proxy.py>)的runtime仅stdlib+NumPy；不导入MuJoCo/SDK/DR/kinematics_v2，不读root/world/contact或随机化参数。原分支公式已SDK-free移植：q4为连续绝对[Lhip,Lcrank,Rhip,Rcrank]；保留active/follower整圈，仅5类被动角作局部wrap；delta在[-1.0863195404360622,+.49192233306644084]，没有旧active硬窗。
- gas slide是相对中性眼长.1793605589098706m的位移s，绝非眼长本身：F=2000*(.1706394410901294-s)-3*sdot。eye140–200mm/stroke60mm，完全伸展名义300N；k/d及力曲线未实测。名义姿态s=-.00757798586835m、Fgas=356.434853917N。
- 核心平衡Jwheel_xz.T*F_xz = load(proper_root,omega,alpha,q,qd,qdd) − tauMotor − tauGas − tauOtherPassive；不额外加g。proper_root必须是chassis原点BODY specific acceleration，非未经杆臂/坐标处理的IMU值或姿态重力向量。
- Fn(Z)是chassis-Z轮心压缩等效，非地形法向。新增leg_axial_compression_proxy_N2与leg_Tp_y_proxy_Nm2仅为同一Fxz的坐标重表达，不增加观测维度；r为hip→wheel的xz向量，Fcomp=−F·r/|r|，Tp_y=r_z*F_x−r_x*F_z；J_Ltheta.T@[-Fcomp,Tp_y] = Jwheel_xz.T@F_xz。不能将其称为独立测得的接触力矩。
- SensorInput仍须声明output-joint-Nm domain/binding/sign/calibration及每轴confidence/sigma；默认全部unbound。design tau只在显式synthetic_fixture/simulation opt-in下可用，不成为硬件校准。3通道时间戳、age<=.03s、skew<=.003s、dt .001–.04s及至少3样本导数warmup保留；连续active增量直接一致性校验，不以整圈wrap隐藏跳变。
- 默认confidence cap=.55且Config禁止上调超过.55；不是经验概率或全DR误差上界，更不提升到FSM .8。缺标定/未知时间/坏差分/奇异映射/负压缩/低confidence → None，绝非伪造0N。仅同leg正常发布时才同时公布axial/Tp；debug/raw模型力也不授予动作权限。
## 本轮实际零步结果
- [RESULT.json](<RESULT.json>)：一次新public P0编译，恰3次mj_forward；mj_step/step1/step2及公开积分入口守卫尝试0，data.time始终0。3姿态为已有名义、共同+2π、非对称；没有动态case、old QA/holdout/父raw读取。
- 纯名义FK45次（包含中央差分及同姿态zero-proper/静态传感器fixture），实际P0 leg_configuration54调用；3次静态SensorInput调用前两次warmup None，第三次出值。这些不是物理episode或硬件执行。
- 全部3姿态最大误差：BODY位置9.72e−17m，COM1.71e−16m，rotation3.34e−16，完整惯量5.56e−17kgm²；COM J4.41e−12、angular J2.61e−11、wheel J3.35e−12，joint J0；gravity投影5.26e−11Nm，passive投影0；已知力逆代数1.47e−14N，轴向/Tp虚功3.56e−15Nm。校验数值及每姿态prefix均保留，未追加forward/姿态。
- 已有nominal trim得到F_xz=[[-4.10e−9,70.0574159960],[-2.26e−9,70.1681002673]]N（未硬编码mg/2）；axial=[69.3482152023,69.4577790018]N，Tp_y=[2.3961313931,2.3999170597]Nm，condition约1.36317。扰动姿态仍用原trim只作数学fixture，非新静力平衡。
- 一致的zero-proper/静态/抵消gas motor fixture得到零模型力，不把固定g补回飞行。名义fixture第三样本confidence约[.4900145,.4900883]，仍显式fixture、非测力标定；.56 cap配置被阻止。保护输入及所测源码前后SHA相同。
## 未覆盖与停止边界
- 未覆盖实际wheel/guide spin相位及加速度、轮驱反作用/接触力矩、实际转子映射、soft closure误差、gas滞回/摩擦/温度、传感器/电流换算标定、alpha/qdd差分可靠性、DR参数。guide支持无法由主轮proxy认定为整机腾空；2×2零残差不识别负载来自何种接触。
- FK/MCI/gravity/Jacobian/static inverse通过只证明公开参数数学/静态一致；不是完整RNE、动态力传感器、T01/T24任务毕业或硬件资格。尚未接父runtime/控制器；下一步输入时钟与可观测性由父单独决定。P0/v1封存源均未改，无Git/Goal/硬件/新代理。
