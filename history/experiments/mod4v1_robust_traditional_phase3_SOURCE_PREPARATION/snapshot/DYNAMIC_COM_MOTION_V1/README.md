# Dynamic COM Motion v1 — moving-COM全项补偿，非接触身份

**23/23合成单测、fresh PUBLIC model12次静态forward通过，0Step/0新robot episode。** 本包在PH2commit `02b5ff84b905a4e40f207a44b0491aeff2f79b7e` 完成后新建，属PH3pending；没有重record/tag，没有改旧CONTACT/FSM、H1/H2、父源或model。

## 入口与证据

- [Runtime](<com_motion.py>)：标准库＋NumPy，只读复用[已封存公共model/FK](<../CONTACT_PROXY_NOMINAL_V1/nominal_model.py>)及[31body/MCI常量](<../CONTACT_PROXY_NOMINAL_V1/PUBLIC_NOMINAL_CONSTANTS.json>)。没有SDK/contacts/rootGT/DR/top/wrench输入。
- [23单测源码](<test_com_motion.py>)、[static oracle](<static_qa.py>)、[新TRAIN传感器差分诊断](<sensor_derivative_diagnostic.py>)、[append-only检查执行器](<run_checks.py>)。
- [首次完整结果](<attempts/001/RESULT.json>)、[原样unit log](<attempts/001/unittest.log>)、[staticQA](<attempts/001/static_QA.json>)、[真实已记录传感器字段诊断](<attempts/001/sensor_diagnostic.json>)；执行前源码SHA/字节另存在该attempt下。
- [完整index](<INDEX.json>)、[validation](<VALIDATION.json>)、[nominal数学例子及wheel缺失界](<NOMINAL_VECTOR_EXAMPLES.json>)、[proposed配置](<PROPOSED_CONFIG.json>)、[建议的新sensor-only捕获schema](<PROPOSED_SENSOR_CAPTURE.json>)。
- [范围](<SCOPE.md>)、[行政/reader事件](<ADMIN_AND_READER_EVENTS.json>)：曾猜测的v5bridge文件不存在，原事件保留，随后从真实R16runner import解析实际producer；不是机器人失败。

## 方程、坐标与全运动项

输入q4顺序为 **Lhip,Lcrank_absolute,Rhip,Rcrank_absolute**，rad；qd/qdd同序。root/body/chassis坐标一致，proper reference必须为`chassis_origin`。输入proper_origin已经是该点的`a-g`向量；IMU-site原始值若尚未补lever，不冒充root；这里没有静止g加回。

```text
rCOM_B(q,wheel_phi) = Σ nominal_m_i * COM_i_B / Σ nominal_m_i
proper_COM_B = proper_origin_B
             + alpha_B × rCOM_B
             + omega_B × (omega_B × rCOM_B)
             + 2 omega_B × rDot_COM_B
             + rDDot_COM_B
```

- public31body tree/闭链FK给所有link、gas内外筒、drive/guide/wheel等的COM；不是只补一个静止torso lever。
- q/qd/qdd与可选wheel角/速/加速度构成局部二阶轨迹：`q±=q±dt*qd+.5dt²*qdd`，wheel亦同。central差分给rDot/rDDot，包含`J*qdd`、Hessian/convective、leg-wheel交叉运动；同时输出linear acceleration部分和剩余convective部分便于审核。
- `2omega×rDot`明确独立输出，不遗漏；rDDot也不假定为0。被动闭链坐标由nominal FK求出，不从runtime仿真读取。
- Root世界XYZ/四元数不是输入。proper已在B轴表达，故瞬时非惯性修正不靠world rootGT；它也没有观察terrain normal或contact点。

### 0g/guide的正确解释

合成旋转freefallfixture中，origin proper可大于2.5m/s²；只要它与alpha/omega/nominal r运动项一致，全项相加后COM proper≈0，`COM_FREEFALL_LIKE`成立。反之origin proper=0但快速旋转不意味着COM proper=0。

固定q/静止root且guide支承的合成fixture取proper_origin=[0,0,9.81]，全项后仍为g，返回`COM_NONFREEFALL_LIKE`。这说明净非重力支承，不识别是guide、轮、chassis、外力或其组合。小COM proper只是freefall-like净力cue，**不是全表面离地/接触身份/过沿成功**；尤其卸载接触仍可能几何相触。

## wheel偏心：没有假balanced

public wheelCOM有很小但非零的径向分量，代码按`c_perp=c-axis*(axis·c)`计算。wheel自转是leaf-body COM旋转修正，轴向COM偏置不会随自转绕圈；wheel角/速/加速度可从输出关节域绑定，不用rootGT补。

- wheel状态缺失时，nominal estimate内部使用明确的reference phase/rate，而不是声称测到0；输出记录缺失原因。
- phase全未知时position误差界为每轮`2*(m_w/M)*|c_perp|`；rate/acc还需要实测误差界或上游显式absolute bounds。没有它们则动态缺失界为未知，cue保持UNCERTAIN，public proper_COM为空。
- 有界时给出COM position/velocity/acceleration缺失半径，以及[例子](<NOMINAL_VECTOR_EXAMPLES.json>)中的specific-force合成界。只是**在declared motion bounds和nominal MCI成立条件下**的几何界，不是实机轮动平衡标定。
- motor no-load speed不是外界冲击下的硬rate/acc上界；本包没有暗用55rad/s或motor torque/I当真实wheel-acc guarantee。缺失界明确由调用者声明。

## API与不确定

```python
from DYNAMIC_COM_MOTION_V1.com_motion import MovingCOM, Config, Sample, Valid, Cue
estimator = MovingCOM(Config())
out = estimator.update(sensor_sample, now_s)
# out.proper_COM_B3 / out.nominal_corrected_estimate_B3
# out.r_COM_B3 / out.rDot_COM_B3 / out.rDDot_COM_B3 / out.terms
# out.cue / out.confidence / out.proposed_error_radius_m_s2 / out.reasons
```

Sample接收传感器q/qd、proper_origin、omega；qdd/alpha可以是显式已对齐的sensor-estimator输出，也可从新鲜qd/gyro差分。显式数据需要Valid.QDD4/ALPHA和各误差界；置信/参考点未知时不从数值看起来合理就升级。

输入timestamp必须是上游已对齐的公共采集时间；单timestamp原型不代替每路acquisition/arrival/derivative-estimate time校验。当前旧trace只有post-step row时钟的情况不应直接填写为可靠采集时钟。

- 两点差分qdd/alpha自带dt/2的midpoint lag，error包含相邻输入误差除dt和显式jerk×dt/2。没有输入误差/jerk bound则时间对齐误差未知，cue UNCERTAIN。
- 估计数值可展示为`nominal_corrected_estimate_B3`，但误差未绑定时`proper_COM_B3=None`，与“已验证可靠向量”分开。
- 默认model confidence cap=.60，自动差分额外×.5；不把unit通过或极小MCI wheel偏心强行写成.8/.9。默认校准置信为0，缺动态界进一步降conf。
- Proposed error radius采用局部Jacobian传播与声明的nominal position/velocity/acceleration model-error scale；未证明高阶曲率、柔顺、encoder零点、非uniform真实MCI误差的全局界。它是工程scale而非校准概率/严格DR保证，原因码一直保留，不把该区间当真实全球置信区间。
- cue是UNCERTAIN/COM_FREEFALL_LIKE/COM_NONFREEFALL_LIKE；没有actuation、CAN、contact_identity、airborne_truth或qualify字段。
- 不接收episode DR真参数来取消D0/D2差异；新guide μ/pair priority澄清不改变MCI/COM常量，也没有回写旧模型/CONTACT/FSM/PH2。

## 当前真实packet差分可靠性：结论为uncertain

[诊断](<attempts/001/sensor_diagnostic.json>)仅新分析R16TRAIN的long_0/101/201各900行，没用H1/H2，没新physics、没重算raw hash。regex仅提取`time`、`gyro`、`estimated14`数组，未parse/use truth/contacts/qpos/envelope/DR字段。

R16logger保存了post-control physics row time、raw packet gyro及sensor-derived est14。est14 rate4可由`[10,10+11,12,12+13]`还原，但未保存`packet.time_s`或raw4encoder采集tuple，因此这不是可完全重放的原始packet。10ms row间隔不证明相邻sensor acquisition时间也是10ms。

示例nominal long_0的arrival-grid apparent qdd绝对p95约48–54rad/s²、最大约564–677；DR101 p95约81–84、最大594–687rad/s²。rawgyro的apparent alpha也有大峰。这些混合了真实加速度、噪声、延迟/保持和时间alias，**不是测量噪声估计或可信上界**。旧estimator alpha用60ms lowpass，该时延也不自动成为当前瞬时alpha。

因此此轮没有证实当前采集条件下qdd/alpha足够可靠；没有从root qvel/qacc/contacts补齐或用gradetruth分离噪声。后续由父在新TRAIN/新logger单独验证建议[sensor-only捕获字段](<PROPOSED_SENSOR_CAPTURE.json>)，而不是改冻结H1/H2或把现有差分设高confidence。

## 静态QA与未证明的部分

fresh public model4poses×3局部轨迹点=12static forwards，wheel相位/速度/加速度参与；时间始终0，step/step1/step2被guard。

|比较|最大差|
|---|---:|
|rCOM vs fresh-public compiled MCI|5.5511e−17m|
|rDot|2.7756e−13m/s|
|rDDot|5.5511e−9m/s²|

这是公开几何/有限差分实现一致性，不是完整dynamic force/contact/RM/270mm/board/real-time资格。23unit首次全过，原source/log/SHA保留。对旧CONTACT/FSM/公共model/PH2receipt的8项保护SHA均未变。新模块不会自行集成、改变门槛或给父整体Goal“毕业”。
