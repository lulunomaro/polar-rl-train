# R63气弹簧反补偿：两条既有nominal flat机械功（只读）

**只分析R58 baseline flat与R63 release nominal flat；原门两案均pass照旧。不触碰正在运行的paired波次，不新增PHY/单位测试/模型/FK/driver执行、gain或第三假说。**

## 1. 方法与阶段核对
- [METHOD](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/R63_SPRING_MECHANICAL_WORK_V1/METHOD.json>)和[SOURCE锁](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/R63_SPRING_MECHANICAL_WORK_V1/SOURCE_LOCK.json>)先于raw；4个精确allowlist raw各open一次，总33600行（2×800控制+2×16000物理）。10小文件SHA/10producer代码SHA关联核对，raw只复用producer SHA与size/mtime，不算大hash、不归档raw。
- [PRE记录:43–60](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/contact_grade_v2.py#L43-L60>)在同一captured PRE保存velocity6_rad_s与actual_tau6_Nm；[active apply:11–16](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MINIHOP_AUDIT_V2/physics_bridge_minihop_flat_v2.py#L11-L16>)显示它在限幅/增益后、ctrl赋值/step之前，root POST另列。它是模型driver-point命令，不是独立电机反馈。
- 瞬时机械P_i=τ_PRE·dq_PRE（W），功W_i≈ΣP_i×0.0005（J），采用left-Riemann；正/负先逐轴每sample分开，再聚合leg[0,1,3,4]/wheel[2,5]。不是精确离散能量，也不是电气母线功率/回充。
- 验sample_index/drive tick/drive timestamp/PRE→POST/20:1与control command/post时间，最大钟差 1.71418435002e-12s（预锁1e−8s）。没有混入rootPOST速度或重建q。
- 实际两案phase均195 approach、15 push、25 predicted-flight、565 capture：push [1.95,2.10)为300cells/0.15s，虽cfg名义push=.14s也不强裁14帧；flight [2.10,2.35)，capture [2.35,8)。
- 包含最后index15999的[7.999499999998286,7.999999999998286)；16000个完整500us权重合8s，无丢尾/半格补点。whole还含approach，不等于只加下表三个动作段。

## 2. 100Hz prepush公共前缀（不是2k bit证明/资格门）
- 实际首push控制index195；比较此前195行（command0..1.94s）的13公共sensor/estimate/request字段共8190标量，maxdiff=0.0，binary64解析值bit差0，phase差0。
- 字段为time/command/forward/sensor time与age、estimated14/roll、raw gyro/proper、encoder q/dq、wheel mean rate、requested_tau6；不是物理2k全状态逐bit对照，未拿名义FF差替代actual τ差。

## 3. 实际clip后机械功：每格“净/正/负”，单位J
|实际控制段(时长)|R58腿4|R63腿4|R58轮2|R63轮2|
|---|---:|---:|---:|---:|
|push (0.15s)|+2.695748/+16.744320/-14.048572|+1.490828/+16.898606/-15.407778|+3.498119/+3.843545/-0.345426|+3.688964/+3.878773/-0.189809|
|predicted flight (0.25s)|+25.474726/+28.555201/-3.080475|+30.004897/+32.479795/-2.474899|+11.447669/+12.168617/-0.720948|+15.248652/+15.819632/-0.570980|
|capture (5.65s)|-19.790081/+12.962719/-32.752800|-21.833659/+12.253638/-34.087297|+27.092745/+45.977196/-18.884452|+24.171531/+40.726944/-16.555413|
|whole8s (8s)|+7.747727/+59.994299/-52.246572|+9.029399/+63.364098/-54.334699|+74.196835/+94.204136/-20.007301|+75.267450/+92.640126/-17.372677|
- 负功按带负号记；同时有轴做正功/轴做负功时不先抵消。[小SUMMARY](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/R63_SPRING_MECHANICAL_WORK_V1/SUMMARY.json>)保留6轴与分组full precision、net_mean_power_W、各段PRE/POST边界和source域。
- push腿净功反而减少1.204919J：正功仅增加0.154286J，负功多1.359205J；push轮净功增加0.190845J。不宜以“加回FF→push腿净正功必然更多”解释高度变化。
- predicted-flight腿净功增加4.530170J、轮增加3.800983J；capture腿更负2.043579J、轮少2.921213J。即使这些阶段方程未改，push后的状态/速度与真实限幅轨迹已不同，机械作用被重分配。
- whole腿净+1.281672J、轮净+1.070614J；whole四腿均功率0.968466→1.128675W，两轮9.274604→9.408431W。它们是机械平均功率，不作转换为电池省电/耗电/再生结论。

## 4. 已记录事件与峰值，保持原grade解释
|case|air区间开始PRE(s)|20ms确认POST(s)|main-mesh峰高(m)/cache PRE(s)|首landing PRE/POST(s)|身份|
|---|---:|---:|---|---|---|
|R58|2.0705|2.0905|0.181228926 / 2.2180|2.4115 / 2.4120|right_tire→ground|
|R63|2.0695|2.0895|0.191686051 / 2.2120|2.4090 / 2.4095|left_tire→ground|
- main-mesh qualified-air峰高增加10.457124mm，不是COM势能或单独根高度。air条件来自既有全world法向合计定义，不新增评分/接触许可。
- 实际air区间在push内开始、确认也仍属push；首landing在capture内。表中predicted-flight只是控制phase，capture积分5.65s也不是只取撞击瞬间。
- 记录到的六轴正机械瞬时峰544.963243→603.332973W，均出现在predicted-flight；与原result一致到舍入误差，不是母线峰功率/过流证据。

## 5. 结论与unknown
同prepush公共记录下，反补偿改变了后续实际driver-point机械功分布与几何air峰；这两条nominal轨迹只支持上述机制观察，不推出唯一因果/DR泛化。实际gas做功、弹簧势能变化、重力/接触/阻尼完整能量账与电气损耗未从该记录分解；不重建q或用nominal tauGas冒充实测。原分数/源/阈值保持，完成即停止，不设计第三假说。
