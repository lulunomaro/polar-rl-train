# MOD4v1 模型一致性审计与源级 MJCF 派生（SRC_ONLY）

## 1. 结论与主入口

**主输入为 [mod4v1_usd_source_aligned.xml](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mod4v1_usd_source_aligned.xml>)，状态 `PASS_COMPILE_ONLY_WITH_DECLARED_SEMANTIC_CHOICES`。** 全31刚体实际USD的质量/COM/完整惯量已映射；实际轮胎凸包与导轮几何已带入，原闭环、弹簧、驱动顺序、达妙转矩限值与传统MuJoCo时钟保留。它是可用于新实验的源级候选，尚未取得本轮 full-DR、PhysX 动态或实车通过证据。

- 主MJCF SHA256：`0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324`。
- 最新USD SHA256：`2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3`；contract SHA256：`bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755`。
- 主模型质量 **14.294140288606286 kg**，与实USD 31体总和相同；`nq=37,nv=36,nu=6`。
- 31机器人body＋world；30标量关节＋freejoint；6connect＋4mimic equality；311机器人geom＋ground；279mesh（277原视觉＋2实USD轮碰撞）。
- 仅使用既有 Python 3.14.3 / MuJoCo 3.15.0 / usd-core 26.8 / NumPy 2.4.5；编译未创建MjData，forward/step均0，时间推进0。

**版本防混用：** [mod4v1_fullaligned_candidate.xml](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mod4v1_fullaligned_candidate.xml>)（SHA `6bbc56fdc6ae7b1447b8452d18ec37507ca95b0b0d6eb29ea1d14c6f2cc780bf`）是发现轮胎实际Mesh之前的被取代preliminary；[mod4v1_three_mci_diagnostic.xml](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mod4v1_three_mci_diagnostic.xml>)仅三MCI诊断，质量14.354140334301 kg，保留旧导轮与旧关节限位，非最新物理基线。两份原样保留以追踪尝试。

## 2. 来源边界及确切旧/新身份

先读 [TASK_SCOPE.md](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/TASK_SCOPE.md>)。技能目录仅Office/ACL；无匹配控制、USD或MuJoCo skill，未虚构专用skill。使用read/glob/grep及现有CLI；无SSH、硬件SDK、训练/仿真、PT、代理派生、安装或Git。全部新增产物只写本审计目录。

在权威v1资产与来源元数据、旧传统控制工程，以及provenance直接关联的9个XML候选内核验SHA。没有发现预先存在且带此v1修正的确切MJCF；这不是对整盘的全局不存在声明。[SOURCE_COLLECTION_SUMMARY.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/SOURCE_COLLECTION_SUMMARY.json>)列出每个检查过的XML，[SOURCE_AUDIT_DATA.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/SOURCE_AUDIT_DATA.json>)保留完整原始快照。

|角色|文件|SHA256|
|---|---|---|
|最新USD|[robot.usd](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets/robot.usd>)|`2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3`|
|最新contract|[import_contract.json](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/assets/import_contract.json>)|`bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755`|
|旧400N派生|[mod4_400N.xml](<F:/RMPOLAR-RL/traditional_control_20261101/model/mod4_400N.xml>)|`5d52284a618c95ac49c97666b00f9e4567d20abb4728e322dc8651f07f4ba0ee`|
|旧完整原XML|[source_rolling_model_original.xml](<F:/RMPOLAR-RL/traditional_control_20261101/model/source_rolling_model_original.xml>)|`f936e5cf6580299e5f89ac843b4ebc3c72f9d40d9131dbcb4fa1fa7779dc87d9`|

contract的`source_mjcf_sha256=fbb039...`、`source_usd_path=incoming/...`和若干几何/自由度字段是历史沿袭字段，不是本新MJCF的生成回执。当前实际源XML为f936e5...、旧400N为5d5228...；原[MODEL_PROVENANCE.json](<F:/RMPOLAR-RL/traditional_control_20261101/MODEL_PROVENANCE.json>)与[RESULTS_20261101.md](<F:/RMPOLAR-RL/traditional_control_20261101/RESULTS_20261101.md>)未改写。

## 3. Frame、COM、主轴和单位核定

- 最新USD实际声明 `metersPerUnit=1,kilogramsPerUnit=1,upAxis=Z`。旧400N MJCF为rad、m、kg、kg·m²；CAD原输入mm已在导出阶段转m。未按旧薄层默认0.01m/Y-up再次缩放几何或惯量。
- USD links在平铺树内，MJCF有嵌套body；先递推MJCF中性body→base刚体变换，再与实际USD XformCache比较。**31体按位置＋姿态唯一匹配，中性位置误差0，轴向矩阵误差0**；再核父子拓扑、关节锚点与几何。并非仅同名套矩阵。
- 22非导轮关节锚点最大误差 6.542e-09 m，axis最大误差 1.634e-08。此次匹配的三修正体 `R_USD→MJCF=I,t=0`；脚本仍使用一般旋转/平移公式。
- USD/Gf quaternion与MJCF均取 **w,x,y,z**；主轴quaternion先归一化。主惯量是COM处在主轴系的diag，转回body采用 `I_B=R(q) diag(d) R(q)^T`。MJCF写`fullinertia=Ixx Iyy Izz Ixy Ixz Iyz`，没有把惯性积再反号。
- 主轴排序/符号改变会使diag和quaternion看似大变，判断以完整tensor为准。三体before vs旧XML完整tensor误差≤3.017e-9 kg·m²、COM完全相同；chassis质量差3.889e-7 kg是USD float32沿袭精度。
- 通用映射：`c_M=t_MU+R_MU c_U`，`I_M=R_MU I_U R_MU^T`；此处两者都是COM惯量，不额外引入原点平行轴项。全31体MCI详见 [BODY_MCI_TABLE.csv](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/BODY_MCI_TABLE.csv>) 与最终索引。

### 三安装刚体的真实修正

|body|旧MJCF质量 kg|新实USD质量 kg|旧COM m|新COM m|
|---|---:|---:|---|---|
|chassis|10.232698829400|10.364698410034|(-0.0210162625, -0.000241252023, -0.0496609429)|(-0.0207486097, -0.000238179549, -0.049028486)|
|left_shin|0.853956455770|0.824956476688|(0.130623702, 0.00466320422, -0.118586646)|(0.128513888, 0.00410648761, -0.116644338)|
|right_shin|0.853956455770|0.824956476688|(0.130623705, -0.00466322463, -0.118586645)|(0.128513888, -0.00410650857, -0.116644338)|

|body|新完整惯量 (Ixx,Iyy,Izz,Ixy,Ixz,Iyz) kg·m²|新主惯量|新主轴 wxyz|
|---|---|---|---|
|chassis|(0.176105009, 0.199650782, 0.331118773, -0.00035021852, 0.0038509466, 0.000142388005)|(0.176004112, 0.199655935, 0.331214517)|(0.999894857, -0.000415097369, 0.0124130724, 0.00748282345)|
|left_shin|(0.00539732099, 0.0113089576, 0.00623240713, -0.000466059519, 0.00537721857, 0.000427227532)|(0.000384867424, 0.0112082055, 0.0113456128)|(0.658522785, -0.657817543, 0.235749483, 0.279367149)|
|right_shin|(0.00539732004, 0.0113089575, 0.00623240677, 0.000466059774, 0.00537721825, -0.000427228153)|(0.000384866988, 0.0112082046, 0.0113456128)|(0.65852356, 0.657816768, 0.235749781, -0.279366881)|

修正依据：4台腿电机0.930→0.963kg，归chassis，共+0.132kg；2台拆原减速段后的裸轮电机0.160→0.131kg，归左右shin，共-0.058kg。质量差的位置近似为父关节锚点，不是新CAD实测COM。保持未知质量差本征惯量为0假设；通过一阶矩＋平行轴一致更新：

```text
P(r)=||r||²I-rrᵀ
I_O=I_C+mP(c); h=mc
m′=m+ΣΔm; h′=h+ΣΔm r; c′=h′/m′
I_C′=I_O+ΣΔm P(r)-m′P(c′)
```

主模型读取实USD浮点落地后的结果，而非在旧double质量上盲加0.074。[body_mass_changes.json](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/body_mass_changes.json>)与[BUILD_RECEIPT.json](<F:/RMPOLAR-RL/mod4_usd_scut_fudan_20261101/candidates/v1/BUILD_RECEIPT.json>)保留每个安装点。当前14.29414kg不是重新标定全部SolidWorks body，不等同此前SolidWorks可见口径16.240934kg，也非整车实称；未乱加payload。

### 质量总和与导轮身份

旧XML14.280140711829919kg → 原USD导轮口径约14.220140287652612kg → v1加电机差额约0.074kg → 实USD/主MJCF14.294140288606286kg。旧导轮8×0.01kg，USD为8×0.0025kg，另有 **-0.060kg**。故旧模型与新模型净差约+0.014kg，不是+0.074kg。

|旧body|新USD/MJCF body|base中性位置 m|
|---|---|---|
|guide_roller_3|guide_roller_00|(0.048, 0.1005, -0.163)|
|guide_roller_1|guide_roller_01|(-0.048, 0.1005, -0.163)|
|guide_roller_2|guide_roller_02|(0.048, -0.1005, -0.163)|
|guide_roller_0|guide_roller_03|(-0.048, -0.1005, -0.163)|
|guide_roller_7|guide_roller_04|(0.259, 0.131, -0.135)|
|guide_roller_5|guide_roller_05|(-0.259, 0.131, -0.135)|
|guide_roller_6|guide_roller_06|(0.259, -0.131, -0.135)|
|guide_roller_4|guide_roller_07|(-0.259, -0.131, -0.135)|

重命名按空间唯一映射，原XML/DOF排列保留；6电机顺序保持不变。

## 4. 实几何核查，及陈旧contract字段

- 277原STL均存在且SHA符合旧provenance。实际USD视觉顶点转body后与STL双向最近点最大距离 **2.48492e-08m**；277/277未定向三角拓扑一致。不同MuJoCo版本的mesh PCA pos/quat/size会改变，实际三角几何未随之改变；初始metadata差异保留但不当作几何形变。
- 其余24非导轮primitive中心误差0、尺寸最大差7.391e-09m，旋转/轴投影差1.445e-07（float quaternion）。
- 8导轮半径0.015m保持；实际USD全宽0.016m，旧XML全宽0.009m。contract的guide geometry位置仍是旧chassis局部坐标，而实际USD已reparent至各roller、局部center=0。主模型采用实USD局部0与0.008m半宽，未重复平移。
- **两驱动轮实际USD是convexHull Mesh，不是contract/旧XML的r=0.0625圆柱。** 各48个顶点，源多边形扇形三角化为92三角；轮mesh局部外包络x/z±0.0636999979615m、y±0.00999999977648m。主输入已使用 [左轮提取网格](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/usd_meshes/left_tire.stl>) 与 [右轮提取网格](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/usd_meshes/right_tire.stl>)。两个文件SHA相同，均为`befafaf4b731dc707ac7e38444f4c5c2fac3f1a66dc1dbf65a6d8c2590867015`。
- 旧controller nominal rolling radius0.0625m仍是历史运动学参数，**不是新Mesh每个姿态的精确支撑高度**。按旧圆轮半径重置可能造成约1.2mm支撑差；新初始化/接触包络/落台评价应读实际凸包，不能用旧圆柱证明最新几何性能。

证据：[GEOMETRY_EQUIVALENCE.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/GEOMETRY_EQUIVALENCE.json>)、[USD_TIRE_MESHES.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/USD_TIRE_MESHES.json>)。USD为单层、无外部依赖；新MJCF依赖279个mesh。277文件只读引用旧资产，2个本目录新提取文件；[USD_SOURCE_DERIVATION_RECEIPT.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/USD_SOURCE_DERIVATION_RECEIPT.json>)列出全部实际依赖路径/SHA。移走旧mesh目录前应显式打包，不把当前相对引用误称自包含。

## 5. 关节、闭环、气弹簧与跨引擎选择

主输入读取实际USD关节limit，不沿袭旧contract/旧XML缺失或更窄的值。下表显示实质差异（弧度）；完整含axis/qposadr/dofadr/armature/damping的表为 [JOINT_TABLE.csv](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/JOINT_TABLE.csv>)。表内范围采用实际USD的float落地值换rad，不额外设计新限位。

|关节|旧limited/range|主输入limited/range|
|---|---|---|
|left_rocker_pin|(-0.782827918, 0.336793828)|(-0.782777746, 0.70574175)|
|left_distal_pin|unlimited|(-0.73305806, 0.815233024)|
|left_knee|(-0.761378703, 0.339258885)|(-0.761328713, 0.720233075)|
|left_gas_pin|unlimited|(-0.0123684213, 0.155949637)|
|left_coupler_pin|unlimited|(-0.880052035, 0.902728519)|
|right_rocker_pin|(-0.782827918, 0.336793828)|(-0.782777746, 0.70574175)|
|right_distal_pin|unlimited|(-0.73305806, 0.815233024)|
|right_knee|(-0.761378703, 0.339258885)|(-0.761328713, 0.720233075)|
|right_gas_pin|unlimited|(-0.0123684213, 0.155949637)|
|right_coupler_pin|unlimited|(-0.880052035, 0.902728519)|

- 6个connect closure和4个joint mimic，以及actuator、contact exclude、sensor、default、option段，与旧400N输入保持字节同义；闭环锚点与实USD再核对到float精度。未删闭环/导轮或把系统换成质点。
- 左右gas_slide均保k=2000N/m、damping=3Ns/m、springref=0.22063944109012937/0.2206394410901294m；行程读实USD，约[-0.0267046844,0.0206394402]m。400N指上限行程静态力，q=0约441.28N。旧 [model_parameters.json](<F:/RMPOLAR-RL/traditional_control_20261101/model_parameters.json>) 的700N/3500N/m标签不是当前XML的力学依据。
- 原 [README.md](<F:/RMPOLAR-RL/traditional_control_20261101/README.md>) 提到较新PhysX运行任务有motor damping=0覆盖；本次SHA实USD本身按导出器角驱动换算后仍为腿0.2、轮0.015N·m·s/rad。主模型保留实资产值；未猜测/热植入未提供的运行覆盖。
- **导轮阻尼有真实单位冲突：** 实USD raw angular Drive damping=9.999999747e-5；按原 [export_usd.py](<C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4/tools/export_usd.py>) 的per-degree约定，SI=raw×180/π=0.005729577806566919。contract同时把raw标作SI≈1e-4，二者相差57.3倍。主模型明确选择实际USD字面值换算；manifest逐joint列明该选择，未冒称已知作者意图或实测阻力。
- 导轮armature实际USD未显式authored，contract声明0；主模型显式0并flag，而不是凭空把缺省解释成已经测得0。MuJoCo额外torsional/rolling friction保旧0.001/0.0001，sliding μ用实USD≈0.02。轮μ≈0.9保留。USD contactOffset≈1mm与MuJoCo软接触参数无逐项动力等价保证。
- contract `independent_velocity_dofs=12` 与 `mjcf_equality_rank_at_neutral=16`为历史字段；本轮仅compile得到nv36，没有执行forward来重测rank。若rank16仍成立，36−16=20而非12（8新被动导轮）；该历史12不作为新模型实际自由度证据。

## 6. 达妙电机、执行顺序与转矩转速证据

来源优先级：历史用户确认由最新contract记载 → CAD装配路径佐证 → OEM链接仅作来源指针。本轮未读取实体铭牌或重新核验厂家PDF。CAD叶子名DM8116/3510不覆盖父装配/用户确认；不将电机换成M3508。[MOTOR_PARAMETERS_AUDIT.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/MOTOR_PARAMETERS_AUDIT.json>)保留原完整额定/峰值/包络状态。

|参数|腿×4|轮×2|
|---|---:|---:|
|型号|DM8009P / DM-J8009P-2EC|DM3519 / DM-S3519-1EC裸机＋自制总比15.8|
|母线 V|24|24|
|当前质量口径 kg/台|0.963|0.131裸机，减速箱CAD单计|
|连续/峰值 Nm|20 / 40|2.591754385964913 / 5.775909774436091|
|额定/空载 rpm|100 / 160|480.08021390374324 / 528.6959317674135|
|总机械减速|内部9×外部1|总转子到轮15.8，替代原厂减速|
|输出armature kg·m²|0.025暂估|0.00099856（转子估计4e-6×15.8²）|
|包络intercept Nm / slope Nm·s/rad|53.333333333333336 / 3.183098861837907|28.18532894736838 / 0.5090829138384437|

转矩转速曲线、效率0.9、转子惯量、热/电流/峰值持续时间均未实测。MJCF电机gear=1已经是输出关节力矩映射，不再次乘内部9或15.8。XML只表达静态ctrl/force限；速度包络/PD/队列来自控制代码，不是compile自动认证的功能。

|index|motor / joint|gear[0]|ctrlrange Nm|forcerange Nm|
|---:|---|---:|---|---|
|0|left_hip_motor / left_hip|1.0|(-40, 40)|(-40, 40)|
|1|left_crank_motor / left_crank|1.0|(-40, 40)|(-40, 40)|
|2|left_wheel_spin_motor / left_wheel_spin|1.0|(-5.77590977, 5.77590977)|(-5.77590977, 5.77590977)|
|3|right_hip_motor / right_hip|1.0|(-40, 40)|(-40, 40)|
|4|right_crank_motor / right_crank|1.0|(-40, 40)|(-40, 40)|
|5|right_wheel_spin_motor / right_wheel_spin|1.0|(-5.77590977, 5.77590977)|(-5.77590977, 5.77590977)|

实际CAN IDs、符号/零点、控制板revision、IMU安装/标定、实测惯量与功率边界仍未知；源文件中存在imu site/仿真framequat不代表硬件已绑定或真值反馈已剔除。

## 7. 时钟、可编译性与证据等级

|栈|物理与求解器|反馈/控制或策略|本轮证据|
|---|---|---|---|
|新MJCF传统栈|0.0005s；implicitfast/Newton/100；gravity(0,0,-9.81)|100Hz为旧传统代码约定，20substeps；需父新控制链落实|MuJoCo3.15.0 CPU compile-only|
|最新USD配套Isaac要求|0.0025s；TGS；32/4 iterations|SDK反馈100Hz，RL policy50Hz|静态声明；未在PhysX运行|

不把TGS称作MuJoCo求解器，不把RL50Hz移作通用硬件周期。closure0.01m/mimic0.01rad为每回合健康条件，由新仿真控制/验收程序执行，非XML自动整批stop或本轮新增准入门槛。旧64seed结果属于旧模型，不作为该新SHA的full-DR资格。

## 8. 精确diff、复现、错误保留与交接

主输入相对旧400N的完整字面diff：[mod4v1_usd_source_aligned.xml.diff](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/mod4v1_usd_source_aligned.xml.diff>)。全31体MCI、实际关节limit、导轮命名/参数/宽度、两轮真实凸包和mesh resolver变化均可逐行审计；未改旧物理文件或父控制代码。

脚本顺序（原输出存在时保护退出；复现应复制脚本到相同目录深度的新空审计目录，保持已固定权威源路径）：

- [inspect_sources.py](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/inspect_sources.py>)
- [analyze_alignment.py](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/analyze_alignment.py>)
- [generate_mjcf.py](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/generate_mjcf.py>)
- [finalize_geometry_candidate.py](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/finalize_geometry_candidate.py>)
- [verify_geometry.py](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/verify_geometry.py>)
- [build_alignment_report.py](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/build_alignment_report.py>)

[ATTEMPTS_AND_ERRORS.json](<F:/RMPOLAR-RL/mod4v1_lqr_mpc_robust_20261102/MODEL_AUDIT/ATTEMPTS_AND_ERRORS.json>)和原始日志保留：二进制USD被read识别、历史incoming路径缺失、缺省armature的None误差、旧轮圆柱对应实际USD Mesh、USD多边形需三角化三次代码尝试。后两次错误带来了轮几何缺口修复，未抹掉失败记录。

父可用主输入开展独立新实验，但应记录source SHA、上述导轮单位决策、真实轮支撑包络与实际engine版本；若另做contract-SI guide damping或runtime damping0实验，应产新配置/新SHA并保留本分支。**本轮结论止于来源/几何/MCI/表格/依赖与compile，full-DR实跑数=0。** 原源hash最终复核均未变。
