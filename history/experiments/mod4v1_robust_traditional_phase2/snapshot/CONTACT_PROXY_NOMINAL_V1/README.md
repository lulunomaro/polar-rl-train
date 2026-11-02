# Contact Proxy Nominal v1 — 公共模型虚功估计，不是足力传感器

**仅public nominal MJCF/MCI＋传感器输入。32个合成/代数单测通过，13个fresh-public-model静态forward对照通过，0Step/0新robot episode。** 本包没有读取runtime contacts、rootGT、障碍顶面、episode随机化参数，也未修改封存FSM/父源码。所有置信门槛、动态阈值与uncertainty scale均为proposed engineering，不是用户验收或实测标定。

## 已封存入口与证据

- [公共nominal常量](<PUBLIC_NOMINAL_CONSTANTS.json>)：31body、30内部joint、COM/fullinertia、轴、spring/damping/armature、闭链pins、名义q/ff；固定源MJCF SHA `0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324`。
- [导出器](<export_public_nominal.py>)只读XML/MCI/public旧公式/公开nominal gain，不导入SDK或mesh；常量文件SHA `14c38264568f8859ba86b567509318a125355bbd24fe9d35aefa6e9354ea900f`。
- [SDK-free model/FK/虚功](<nominal_model.py>)、[传感器限定observer](<contact_proxy.py>)；仅NumPy＋标准库，runtime不导入mujoco/旧kin。
- [32单测源码](<test_contact_proxy.py>)、[fresh-public静态oracle](<static_qa.py>)、[append-only执行器](<run_checks.py>)。
- [首轮32/32结果与源码SHA](<attempts/001/RESULT.json>)、[原样unit日志](<attempts/001/unittest.log>)、[静态QA](<attempts/001/STATIC_QA.json>)。
- [初始nomEq代数probe](<model_probes/001/RESULT.json>)保留执行前源码，未改写成后续版本。
- [完整index](<INDEX.json>)、[validation](<VALIDATION.json>)、[proposed阈值](<PROPOSED_THRESHOLDS.json>)、[行政/读者事件](<ADMIN_EVENTS.json>)。

## 数学与nomEq结果

四主动坐标和四motor torque顺序均为 **Lhip,Lcrank,Rhip,Rcrank**，输出侧rad/Nm，正号沿public joint轴。crank为绝对关节角，不是gain state14的crank-minus-hip delta，更不是被动knee。

闭链连续分支公式来自只读旧kin的`leg_configuration`，在此去掉SDK依赖。generic31body tree FK给出chassis-frame body/COM/wheel-center几何；central ±q有限差分得到COM/角速度/轮心/被动joint Jacobian及spring长度导数。runtime不接收world位置，也不根据episode model更新质量、惯量、spring或几何。

每腿采用拟议等效wheel-center载荷模型：

```text
Jwheel_xz.T @ [Fx_B, Fz_B] = load_effective - tauMotor - tauGas - tauOtherPassive
```

- `proper_root_B = a_root_B - g_B`，算法直接使用完整向量，**没有再加一个固定g**。
- 每body有效COM平移载荷：`proper_root + alpha×r + omega×(omega×r) + 2omega×r_dot + r_ddot`；qdd由新鲜qd差分，Jdot由离线公式方向差分。
- 包含非wheel body的nominal转动惯性/陀螺proxy和joint armature投影；不是完整测量状态RNE。
- `s_slide=|T-S|-|T0-S0|`是MJCF slide坐标，不是绝对杆长；`Fgas=k*(springref-s_slide)-d*s_dot`，`tauGas=(ds/dq).T*Fgas`。其他nominal关节阻尼另算。
- wheel spin/加速度/drive反作用/contact patch力矩未观测；wheel rotational load省略，wheelCOM的极小偏轴spin phase固定0。它们是明确遗漏，不从truth补齐。

public nomEq输入q4 `[.250328109554,.050328109554,.250328109554,.050328109554]`、tau4 `[6.591811364,-7.635446745,6.572299328,-7.619720368]`、proper_root `[0,0,9.81]`：

|结果|left|right|
|---|---:|---:|
|Fx_B model proxy (N)|−2.02e−8|−5.33e−9|
|Fz_B model proxy (N)|70.0574160121|70.1681001878|
|J.T条件数|1.363169|1.363169|

总Fz=140.2255162N，与public14.2941402886kg×9.81一致。这个值从motor/spring/J/MCI解得，代码没有强塞mg/2。gas虚功tau每腿约`[-16.2963139,+16.2963139]Nm`；有效重力load约`[2.6456183,-1.2931223]Nm`。这些是名义模型自洽，不是实机扭矩/足力标定。

### 0g与旋转飞行

若`proper_root=0,omega=alpha=qd=qdd=0`，effective load为0，不保留静止g。要得到一致的0外力，还需motor torque抵消内部gas/passive torque；不是任意把站立τff原封不动搬到0g就应得到0力。实际自由运动时gas会加速腿，缺可靠qdd/alpha时返回低置信或None。

O→IMU补到root后，绕偏置COM旋转飞行的root proper norm仍可非零；本模块使用其向量及omega/alpha/nominal COM运动项，不用“root norm≈0”替代接触判断。它不宣称已补出真实moving-COM或识别全部外部载荷。

## 最小API与域声明

从Task根用同一package名导入：

```python
from CONTACT_PROXY_NOMINAL_V1.contact_proxy import (
    ContactProxy, Config, SensorInput, TorqueDomain, ALL_VALID,
)
observer = ContactProxy(Config())
result = observer.step(packet, now_s)
# adapter：只传估计与置信，不传sim contact/root/world/top truth
from FSM_DETECTOR_V1.fsm_detector import ForceProxy
force_input = ForceProxy(
    packet.timestamp_s, result.normal_proxy_N2,
    result.confidence2, result.provenance,
)
```

`packet`是slots/frozen `SensorInput`，必需：q/qd/τ4、q/IMU/torque三个单调timestamp、validbits、proper_root/omega/alpha三个chassis-frame向量、torque_domain/binding_id。还有各测量/转换的confidence、torque sigma4、qd sigma4及参考点声明。

- proper参考点必须为`'chassis_origin'`；IMU-site或COM proper不默默当root使用。
- measured/current-converted **joint-output Nm**须明确`torque_sign_verified=True`、`measured_torque_calibration_confirmed=True`和非空binding_id。转换后的Kt、传动比、方向、效率、零点和时延由父绑定；本模块不猜DM电流/rotor单位，不重复乘ratio。
- `NOMINAL_DESIGN_OUTPUT_FIXTURE`不是测量标定；只有Config显式`allow_nominal_design_fixture=True`且context为simulation/synthetic_fixture才进入代数估计，输出仍带NOT_MEASURED标志。
- 默认各confidence为0/uncertainty未绑定；未知域/符号/标定/参考点/时序直接None+低置信，绝非假0N。
- qdd须至少3个新鲜、对齐样本；重复/倒序不刷新好样本，长gap重新warmup，不从旧数据赚持续窗；q与qd不一致/zero-offset jump使导数重新预热。
- 明显大或不可信legdd/omega/alpha/proper、qd噪声放大、病态J、负压缩符号、未声明torque sigma等降confidence或None；不裁成虚假的0支撑。

输出：`normal_proxy_N2`(可None)、`confidence2`、`normal_sigma_N2`、未作truth解释的`model_force_body_xz_N2`、逐腿/公共原因与provenance=`nominal_model_nottruth`。没有actuation、CAN、contact identity、airborne_truth、jump_success或qualify字段。

默认model confidence cap=.55，本身低于已封存FSM的force_min_confidence=.8。因此默认不会把本原型直接晋升为FSM可信contact；调低门槛/抬高置信应是父显式Sim研究，而不是把通过32个单测当作传感器标定。RSS uncertainty及confidence是proposed scale/heuristic，非已验证概率、误差界或D0/D5/D2保证；fractions只影响不确定性，**不改变nominal模型来取消DR**。

## 最重要的可观性界限

1. **这是leg等效wheel-center载荷假设，不是轮接触身份。** 两个joint方程解两个XZ未知量总可有极小残余；残余小不辨认外载究竟在wheel、guide、link或其他面。guide承载/摩擦/碰撞同样能映射为类似等效力。
2. **main wheel双off不等于整机器人离地**，guide/chassis/其他接触仍可能承载；proxy正值也不证明真实轮接触。本模块没有读取R16接触候选报告或任何contact truth给结果“修正”。
3. normal字段只是chassis-Z压缩投影。没有地形法向、AHRS全姿态/ground-plane或lateral反力观测；滚转/坡面/非轮接触时不是实际地面normal。
4. 四leg torque接口看不到wheel drive反作用和contact patch力矩。推进、制动、spin和飞行期间更应保留不确定，而不是声称完整RNE/真实Fz。动态tap/push/guide load路径需后续绑定与独立验证。
5. nominal质量/COM、气弹簧、摩擦、motor effort、encoder零点与alpha对齐都可能偏；D0/D5/D2误差没有通过episode真参数抹除。未知不会被计为contact或air通过。

## 静态QA证明与未证明

fresh public model13pose，`mj_forward`13次、`data.time=0`；step/step1/step2在该QA进程被拦截，调用数0。读取的body/COM/mass/gravity/passive投影仅来自新建public nominal fixture，数据不会作为observer runtime输入；没有读取contact/ncon/rootGT episode或DR。

- body位置最大误差1.3184e−16m；COM1.7347e−16m；rotation4.4409e−16。
- virtual gravity projection差7.6215e−11Nm；spring/passive projection差0。
- 这些是实现与公开参数一致性的数值检查，不是0.01m机械验收、动态RNE资格、真实足力、跳阶或完整RM通过。

```powershell
& 'C:\Users\lulu\AppData\Local\Programs\Python\Python314\python.exe' -B .\run_checks.py
```

每次执行前保存新attempt下源码/常量字节与SHA、原样log/staticQA/RESULT，后续不覆盖。此轮001全通过；行政Goal操作的top-level限制保留[原记录](<ADMIN_EVENTS.json>)，未重试扩大子权限。新模块未做Git/SSH/真实IO；父后续PHASE2归档另行操作。封存后本包/FSM均不再为归档重跑数学或物理。
