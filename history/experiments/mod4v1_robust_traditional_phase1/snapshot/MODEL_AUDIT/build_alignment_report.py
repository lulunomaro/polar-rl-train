"""Build final Markdown + strict JSON index from preserved SRC_ONLY evidence.
No simulator or robot SDK imports; no source edits.
"""
from pathlib import Path
import csv, datetime, hashlib, json, math, xml.etree.ElementTree as ET
HERE=Path(__file__).resolve().parent
V1=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1')
OLD=Path(r'F:\RMPOLAR-RL\traditional_control_20261101')

def js(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def link(p,label=None):
    p=Path(p);return '['+(label or p.name)+'](<'+p.as_posix()+'>)'
def vec(v,n=9):return '('+', '.join(f'{float(x):.{n}g}' for x in v)+')'
def clean(x):
    if isinstance(x,float) and not math.isfinite(x):return str(x)
    if isinstance(x,dict):return {k:clean(v) for k,v in x.items()}
    if isinstance(x,list):return [clean(v) for v in x]
    return x

def main():
    md=HERE/'MODEL_ALIGNMENT.md';idxpath=HERE/'MODEL_ALIGNMENT_INDEX.json';assert not md.exists() and not idxpath.exists()
    s=js(HERE/'SOURCE_AUDIT_DATA.json');m=js(HERE/'ALIGNMENT_MEASUREMENTS.json');d=js(HERE/'DERIVATION_RECEIPT.json');r=js(HERE/'USD_SOURCE_DERIVATION_RECEIPT.json');g=js(HERE/'GEOMETRY_EQUIVALENCE_SUMMARY.json');c=js(V1/'assets/import_contract.json');changes=js(V1/'body_mass_changes.json')
    comp=r['compile'];old=s['old_compile'];by={x['usd_body']:x for x in m['frame_mapping']};mcis={x['usd_body']:x for x in d['mci_changes']}
    assert sha(r['primary']['path'])==r['primary']['sha256']
    source_unchanged=all(not x['exists'] or sha(x['path'])==x['sha256'] for x in s['source_files']);assert source_unchanged
    # Final RFC8259-safe static snapshot; originals retain their initial serialization/errors.
    (HERE/'USD_STATIC_RFC8259.json').write_text(json.dumps(clean(s['usd']),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    joints=[]
    for new in comp['joint_table']:
        if new['name']=='floating_base':prev=old['joints']['floating_base']
        else:
            match=next(x for x in m['joint_mapping'] if x['usd_joint']==new['name']);prev=old['joints'][match['old_mjcf_joint']]
        joints.append({'new':new,'old':prev})
    with (HERE/'JOINT_TABLE.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['new_name','old_name','body','type','qposadr','dofadr','axis','old_limited','old_range','new_limited','new_range','old_armature','new_armature','old_damping_si','new_damping_si','stiffness','springref'])
        for v in joints:
            n=v['new'];o=v['old'];w.writerow([n['name'],next(k for k,x in old['joints'].items() if x['id']==o['id']),n['body'],n['type'],n['qposadr'],n['dofadr'],n['axis'],o['limited'],o['range'],n['limited'],n['range'],o['armature'],n['armature'],o['damping_si'],n['damping_si'],n['stiffness'],n['springref']])
    with (HERE/'ACTUATOR_TABLE.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(['index','name','joint','gear','ctrlrange','forcerange'])
        for v in comp['actuator_table']:w.writerow([v[k] for k in ['index','name','joint','gear','ctrlrange','forcerange']])
    errors=js(HERE/'READER_ERRORS.json')
    errors['preserved_script_attempts']=[
        {'log':str(HERE/'MEASUREMENT_001.log'),'failure':'TypeError: float - NoneType when reading absent authored guide armature','resolution':'Retained absent authored value as unknown and explicit contract-zero selection; preserved log; retry 002 succeeded'},
        {'log':str(HERE/'GEOMETRY_VERIFY_001.log'),'error_file':str(HERE/'GEOMETRY_EQUIVALENCE_FAILURE_001.txt'),'failure':'KeyError: None when old cylinder was encountered as real USD Mesh','resolution':'This revealed actual tire geometry mismatch; generated separate revision with extracted actual USD convexHull mesh'},
        {'log':str(HERE/'USD_SOURCE_DERIVATION_001.log'),'error_file':str(HERE/'USD_SOURCE_DERIVATION_FAILURE_001.txt'),'failure':'AssertionError: tire polygon faces are not all triangles','resolution':'Fan triangulation of authored polygon faces; points/convex hull retained; retry 002 succeeded'}]
    (HERE/'ATTEMPTS_AND_ERRORS.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf-8')
    motor={'leg_motor':c['leg_motor'],'wheel_motor':c['wheel_motor'],'actual_gas_springs':c['gas_springs'],'legacy_motor_metadata':meta(OLD/'model_parameters.json'),
           'sources':{'leg_confirmation':'Contract reports historical user confirmation DM8009P 24V ×4, 2026-09-10; latest official_model DM-J8009P-2EC. This turn did not independently inspect a physical nameplate or OEM PDF.',
                      'wheel_confirmation':'Contract reports user-confirmed DM3519 + replacement total rotor-to-wheel 15.8. CAD parent paths include DM-S3519-1EC_3d-250509; leaf filenames contain older 3510 naming and are not motor identity evidence by themselves.'},
           'physical_bindings_unknown':['CAN IDs and bus mapping','hardware revisions and actual controller board','encoder signs/zero offsets','IMU exact mounting orientation and calibration','measured rotor/gear inertia','measured torque-speed efficiency/thermal/current/power envelope'],
           'motor_passive_damping_source':'Actual SHA-pinned USD static drive, matching old MJCF .2 leg/.015 wheel; no runtime-zero override applied',
           'nominal_wheel_rolling_radius_m':0.0625,'actual_USD_tire_convex_hull_max_radius_m':0.06369999796152115,'nominal_radius_is_not_exact_collision_support':True}
    (HERE/'MOTOR_PARAMETERS_AUDIT.json').write_text(json.dumps(motor,ensure_ascii=False,indent=2),encoding='utf-8')
    L=[];a=L.append
    a('# MOD4v1 模型一致性审计与源级 MJCF 派生（SRC_ONLY）\n')
    a('## 1. 结论与主入口\n')
    a('**主输入为 '+link(r['primary']['path'])+'，状态 `PASS_COMPILE_ONLY_WITH_DECLARED_SEMANTIC_CHOICES`。** 全31刚体实际USD的质量/COM/完整惯量已映射；实际轮胎凸包与导轮几何已带入，原闭环、弹簧、驱动顺序、达妙转矩限值与传统MuJoCo时钟保留。它是可用于新实验的源级候选，尚未取得本轮 full-DR、PhysX 动态或实车通过证据。\n')
    a('- 主MJCF SHA256：`'+r['primary']['sha256']+'`。')
    a('- 最新USD SHA256：`'+r['source_usd']['sha256']+'`；contract SHA256：`'+r['source_contract']['sha256']+'`。')
    a('- 主模型质量 **'+f"{comp['mass_sum_kg']:.15f}"+' kg**，与实USD 31体总和相同；`nq=37,nv=36,nu=6`。')
    a('- 31机器人body＋world；30标量关节＋freejoint；6connect＋4mimic equality；311机器人geom＋ground；279mesh（277原视觉＋2实USD轮碰撞）。')
    a('- 仅使用既有 Python '+s['python_version'].split()[0]+' / MuJoCo '+comp['mujoco']+' / usd-core '+s['versions']['usd-core']+' / NumPy '+s['versions']['numpy']+'；编译未创建MjData，forward/step均0，时间推进0。\n')
    a('**版本防混用：** '+link(d['primary']['path'])+'（SHA `'+d['primary']['sha256']+'`）是发现轮胎实际Mesh之前的被取代preliminary；'+link(d['diagnostic']['path'])+'仅三MCI诊断，质量'+f"{d['diagnostic_compile']['mass_sum_kg']:.12f}"+' kg，保留旧导轮与旧关节限位，非最新物理基线。两份原样保留以追踪尝试。\n')
    a('## 2. 来源边界及确切旧/新身份\n')
    a('先读 '+link(HERE.parent/'TASK_SCOPE.md')+'。技能目录仅Office/ACL；无匹配控制、USD或MuJoCo skill，未虚构专用skill。使用read/glob/grep及现有CLI；无SSH、硬件SDK、训练/仿真、PT、代理派生、安装或Git。全部新增产物只写本审计目录。\n')
    a('在权威v1资产与来源元数据、旧传统控制工程，以及provenance直接关联的9个XML候选内核验SHA。没有发现预先存在且带此v1修正的确切MJCF；这不是对整盘的全局不存在声明。'+link(HERE/'SOURCE_COLLECTION_SUMMARY.json')+'列出每个检查过的XML，'+link(HERE/'SOURCE_AUDIT_DATA.json')+'保留完整原始快照。\n')
    a('|角色|文件|SHA256|\n|---|---|---|')
    for label,key in [('最新USD','source_usd'),('最新contract','source_contract')]:
        v=r[key];a('|'+label+'|'+link(v['path'])+'|`'+v['sha256']+'`|')
    for label,p in [('旧400N派生',OLD/'model/mod4_400N.xml'),('旧完整原XML',OLD/'model/source_rolling_model_original.xml')]:a('|'+label+'|'+link(p)+'|`'+sha(p)+'`|')
    a('\ncontract的`source_mjcf_sha256=fbb039...`、`source_usd_path=incoming/...`和若干几何/自由度字段是历史沿袭字段，不是本新MJCF的生成回执。当前实际源XML为f936e5...、旧400N为5d5228...；原'+link(OLD/'MODEL_PROVENANCE.json')+'与'+link(OLD/'RESULTS_20261101.md')+'未改写。\n')
    a('## 3. Frame、COM、主轴和单位核定\n')
    a('- 最新USD实际声明 `metersPerUnit=1,kilogramsPerUnit=1,upAxis=Z`。旧400N MJCF为rad、m、kg、kg·m²；CAD原输入mm已在导出阶段转m。未按旧薄层默认0.01m/Y-up再次缩放几何或惯量。')
    a('- USD links在平铺树内，MJCF有嵌套body；先递推MJCF中性body→base刚体变换，再与实际USD XformCache比较。**31体按位置＋姿态唯一匹配，中性位置误差0，轴向矩阵误差0**；再核父子拓扑、关节锚点与几何。并非仅同名套矩阵。')
    a('- 22非导轮关节锚点最大误差 '+f"{m['nonroller_joint_max_errors']['parent_anchor_max_error_m']:.4g}"+' m，axis最大误差 '+f"{m['nonroller_joint_max_errors']['axis_vector_max_error']:.4g}"+'。此次匹配的三修正体 `R_USD→MJCF=I,t=0`；脚本仍使用一般旋转/平移公式。')
    a('- USD/Gf quaternion与MJCF均取 **w,x,y,z**；主轴quaternion先归一化。主惯量是COM处在主轴系的diag，转回body采用 `I_B=R(q) diag(d) R(q)^T`。MJCF写`fullinertia=Ixx Iyy Izz Ixy Ixz Iyz`，没有把惯性积再反号。')
    a('- 主轴排序/符号改变会使diag和quaternion看似大变，判断以完整tensor为准。三体before vs旧XML完整tensor误差≤3.017e-9 kg·m²、COM完全相同；chassis质量差3.889e-7 kg是USD float32沿袭精度。')
    a('- 通用映射：`c_M=t_MU+R_MU c_U`，`I_M=R_MU I_U R_MU^T`；此处两者都是COM惯量，不额外引入原点平行轴项。全31体MCI详见 '+link(HERE/'BODY_MCI_TABLE.csv')+' 与最终索引。\n')
    a('### 三安装刚体的真实修正\n')
    a('|body|旧MJCF质量 kg|新实USD质量 kg|旧COM m|新COM m|\n|---|---:|---:|---|---|')
    for n in ['chassis','left_shin','right_shin']:
        b=by[n];a('|'+n+'|'+f"{b['old_mass_kg']:.12f}"+'|'+f"{b['usd_mass_kg']:.12f}"+'|'+vec(b['old_com_m'])+'|'+vec(b['usd_com_m'])+'|')
    a('\n|body|新完整惯量 (Ixx,Iyy,Izz,Ixy,Ixz,Iyz) kg·m²|新主惯量|新主轴 wxyz|\n|---|---|---|---|')
    for n in ['chassis','left_shin','right_shin']:
        u=s['usd']['bodies'][n];I=u['full_inertia_kg_m2'];a('|'+n+'|'+vec([I[0][0],I[1][1],I[2][2],I[0][1],I[0][2],I[1][2]])+'|'+vec(u['diagonal_inertia_kg_m2'])+'|'+vec(u['principal_axes_wxyz'])+'|')
    a('\n修正依据：4台腿电机0.930→0.963kg，归chassis，共+0.132kg；2台拆原减速段后的裸轮电机0.160→0.131kg，归左右shin，共-0.058kg。质量差的位置近似为父关节锚点，不是新CAD实测COM。保持未知质量差本征惯量为0假设；通过一阶矩＋平行轴一致更新：\n')
    a('```text\nP(r)=||r||²I-rrᵀ\nI_O=I_C+mP(c); h=mc\nm′=m+ΣΔm; h′=h+ΣΔm r; c′=h′/m′\nI_C′=I_O+ΣΔm P(r)-m′P(c′)\n```\n')
    a('主模型读取实USD浮点落地后的结果，而非在旧double质量上盲加0.074。'+link(V1/'body_mass_changes.json')+'与'+link(V1/'BUILD_RECEIPT.json')+'保留每个安装点。当前14.29414kg不是重新标定全部SolidWorks body，不等同此前SolidWorks可见口径16.240934kg，也非整车实称；未乱加payload。\n')
    a('### 质量总和与导轮身份\n')
    a('旧XML14.280140711829919kg → 原USD导轮口径约14.220140287652612kg → v1加电机差额约0.074kg → 实USD/主MJCF14.294140288606286kg。旧导轮8×0.01kg，USD为8×0.0025kg，另有 **-0.060kg**。故旧模型与新模型净差约+0.014kg，不是+0.074kg。\n')
    a('|旧body|新USD/MJCF body|base中性位置 m|\n|---|---|---|')
    for n,b in by.items():
        if n.startswith('guide_roller'):a('|'+b['old_mjcf_body']+'|'+n+'|'+vec(s['usd']['bodies'][n]['base_relative_position_m'])+'|')
    a('\n重命名按空间唯一映射，原XML/DOF排列保留；6电机顺序保持不变。\n')
    a('## 4. 实几何核查，及陈旧contract字段\n')
    a('- 277原STL均存在且SHA符合旧provenance。实际USD视觉顶点转body后与STL双向最近点最大距离 **'+f"{g['max_STL_to_USD_vertex_distance_m']:.6g}"+'m**；277/277未定向三角拓扑一致。不同MuJoCo版本的mesh PCA pos/quat/size会改变，实际三角几何未随之改变；初始metadata差异保留但不当作几何形变。')
    a('- 其余24非导轮primitive中心误差0、尺寸最大差'+f"{g['nonroller_primitive_max_errors']['size_max_error_m']:.4g}"+'m，旋转/轴投影差'+f"{g['nonroller_primitive_max_errors']['axis_or_rotation_max_error']:.4g}"+'（float quaternion）。')
    a('- 8导轮半径0.015m保持；实际USD全宽0.016m，旧XML全宽0.009m。contract的guide geometry位置仍是旧chassis局部坐标，而实际USD已reparent至各roller、局部center=0。主模型采用实USD局部0与0.008m半宽，未重复平移。')
    a('- **两驱动轮实际USD是convexHull Mesh，不是contract/旧XML的r=0.0625圆柱。** 各48个顶点，源多边形扇形三角化为92三角；轮mesh局部外包络x/z±0.0636999979615m、y±0.00999999977648m。主输入已使用 '+link(HERE/'usd_meshes/left_tire.stl','左轮提取网格')+' 与 '+link(HERE/'usd_meshes/right_tire.stl','右轮提取网格')+'。两个文件SHA相同，均为`befafaf4b731dc707ac7e38444f4c5c2fac3f1a66dc1dbf65a6d8c2590867015`。')
    a('- 旧controller nominal rolling radius0.0625m仍是历史运动学参数，**不是新Mesh每个姿态的精确支撑高度**。按旧圆轮半径重置可能造成约1.2mm支撑差；新初始化/接触包络/落台评价应读实际凸包，不能用旧圆柱证明最新几何性能。\n')
    a('证据：'+link(HERE/'GEOMETRY_EQUIVALENCE.json')+'、'+link(HERE/'USD_TIRE_MESHES.json')+'。USD为单层、无外部依赖；新MJCF依赖279个mesh。277文件只读引用旧资产，2个本目录新提取文件；'+link(HERE/'USD_SOURCE_DERIVATION_RECEIPT.json')+'列出全部实际依赖路径/SHA。移走旧mesh目录前应显式打包，不把当前相对引用误称自包含。\n')
    a('## 5. 关节、闭环、气弹簧与跨引擎选择\n')
    a('主输入读取实际USD关节limit，不沿袭旧contract/旧XML缺失或更窄的值。下表显示实质差异（弧度）；完整含axis/qposadr/dofadr/armature/damping的表为 '+link(HERE/'JOINT_TABLE.csv')+'。表内范围采用实际USD的float落地值换rad，不额外设计新限位。\n')
    a('|关节|旧limited/range|主输入limited/range|\n|---|---|---|')
    for v in joints:
        n=v['new'];o=v['old']
        if n['name'].startswith('guide_roller') or n['name']=='floating_base':continue
        changed=n['limited']!=o['limited'] or any(abs(x-y)>1e-6 for x,y in zip(n['range'],o['range']))
        if changed:a('|'+n['name']+'|'+(vec(o['range']) if o['limited'] else 'unlimited')+'|'+(vec(n['range']) if n['limited'] else 'unlimited')+'|')
    a('\n- 6个connect closure和4个joint mimic，以及actuator、contact exclude、sensor、default、option段，与旧400N输入保持字节同义；闭环锚点与实USD再核对到float精度。未删闭环/导轮或把系统换成质点。')
    a('- 左右gas_slide均保k=2000N/m、damping=3Ns/m、springref=0.22063944109012937/0.2206394410901294m；行程读实USD，约[-0.0267046844,0.0206394402]m。400N指上限行程静态力，q=0约441.28N。旧 '+link(OLD/'model_parameters.json')+' 的700N/3500N/m标签不是当前XML的力学依据。')
    a('- 原 '+link(OLD/'README.md')+' 提到较新PhysX运行任务有motor damping=0覆盖；本次SHA实USD本身按导出器角驱动换算后仍为腿0.2、轮0.015N·m·s/rad。主模型保留实资产值；未猜测/热植入未提供的运行覆盖。')
    a('- **导轮阻尼有真实单位冲突：** 实USD raw angular Drive damping=9.999999747e-5；按原 '+link(Path(r'C:\Users\lulu\Desktop\claude\mjcf\chassis_mod4\tools\export_usd.py'))+' 的per-degree约定，SI=raw×180/π=0.005729577806566919。contract同时把raw标作SI≈1e-4，二者相差57.3倍。主模型明确选择实际USD字面值换算；manifest逐joint列明该选择，未冒称已知作者意图或实测阻力。')
    a('- 导轮armature实际USD未显式authored，contract声明0；主模型显式0并flag，而不是凭空把缺省解释成已经测得0。MuJoCo额外torsional/rolling friction保旧0.001/0.0001，sliding μ用实USD≈0.02。轮μ≈0.9保留。USD contactOffset≈1mm与MuJoCo软接触参数无逐项动力等价保证。')
    a('- contract `independent_velocity_dofs=12` 与 `mjcf_equality_rank_at_neutral=16`为历史字段；本轮仅compile得到nv36，没有执行forward来重测rank。若rank16仍成立，36−16=20而非12（8新被动导轮）；该历史12不作为新模型实际自由度证据。\n')
    a('## 6. 达妙电机、执行顺序与转矩转速证据\n')
    a('来源优先级：历史用户确认由最新contract记载 → CAD装配路径佐证 → OEM链接仅作来源指针。本轮未读取实体铭牌或重新核验厂家PDF。CAD叶子名DM8116/3510不覆盖父装配/用户确认；不将电机换成M3508。'+link(HERE/'MOTOR_PARAMETERS_AUDIT.json')+'保留原完整额定/峰值/包络状态。\n')
    a('|参数|腿×4|轮×2|\n|---|---:|---:|\n|型号|DM8009P / DM-J8009P-2EC|DM3519 / DM-S3519-1EC裸机＋自制总比15.8|\n|母线 V|24|24|\n|当前质量口径 kg/台|0.963|0.131裸机，减速箱CAD单计|\n|连续/峰值 Nm|20 / 40|2.591754385964913 / 5.775909774436091|\n|额定/空载 rpm|100 / 160|480.08021390374324 / 528.6959317674135|\n|总机械减速|内部9×外部1|总转子到轮15.8，替代原厂减速|\n|输出armature kg·m²|0.025暂估|0.00099856（转子估计4e-6×15.8²）|\n|包络intercept Nm / slope Nm·s/rad|53.333333333333336 / 3.183098861837907|28.18532894736838 / 0.5090829138384437|\n')
    a('转矩转速曲线、效率0.9、转子惯量、热/电流/峰值持续时间均未实测。MJCF电机gear=1已经是输出关节力矩映射，不再次乘内部9或15.8。XML只表达静态ctrl/force限；速度包络/PD/队列来自控制代码，不是compile自动认证的功能。\n')
    a('|index|motor / joint|gear[0]|ctrlrange Nm|forcerange Nm|\n|---:|---|---:|---|---|')
    for v in comp['actuator_table']:a('|'+str(v['index'])+'|'+v['name']+' / '+v['joint']+'|'+str(v['gear'][0])+'|'+vec(v['ctrlrange'])+'|'+vec(v['forcerange'])+'|')
    a('\n实际CAN IDs、符号/零点、控制板revision、IMU安装/标定、实测惯量与功率边界仍未知；源文件中存在imu site/仿真framequat不代表硬件已绑定或真值反馈已剔除。\n')
    a('## 7. 时钟、可编译性与证据等级\n')
    a('|栈|物理与求解器|反馈/控制或策略|本轮证据|\n|---|---|---|---|\n|新MJCF传统栈|0.0005s；implicitfast/Newton/100；gravity(0,0,-9.81)|100Hz为旧传统代码约定，20substeps；需父新控制链落实|MuJoCo3.15.0 CPU compile-only|\n|最新USD配套Isaac要求|0.0025s；TGS；32/4 iterations|SDK反馈100Hz，RL policy50Hz|静态声明；未在PhysX运行|\n')
    a('不把TGS称作MuJoCo求解器，不把RL50Hz移作通用硬件周期。closure0.01m/mimic0.01rad为每回合健康条件，由新仿真控制/验收程序执行，非XML自动整批stop或本轮新增准入门槛。旧64seed结果属于旧模型，不作为该新SHA的full-DR资格。\n')
    a('## 8. 精确diff、复现、错误保留与交接\n')
    a('主输入相对旧400N的完整字面diff：'+link(HERE/'mod4v1_usd_source_aligned.xml.diff')+'。全31体MCI、实际关节limit、导轮命名/参数/宽度、两轮真实凸包和mesh resolver变化均可逐行审计；未改旧物理文件或父控制代码。\n')
    a('脚本顺序（原输出存在时保护退出；复现应复制脚本到相同目录深度的新空审计目录，保持已固定权威源路径）：\n')
    for n in ['inspect_sources.py','analyze_alignment.py','generate_mjcf.py','finalize_geometry_candidate.py','verify_geometry.py','build_alignment_report.py']:a('- '+link(HERE/n))
    a('\n'+link(HERE/'ATTEMPTS_AND_ERRORS.json')+'和原始日志保留：二进制USD被read识别、历史incoming路径缺失、缺省armature的None误差、旧轮圆柱对应实际USD Mesh、USD多边形需三角化三次代码尝试。后两次错误带来了轮几何缺口修复，未抹掉失败记录。\n')
    a('父可用主输入开展独立新实验，但应记录source SHA、上述导轮单位决策、真实轮支撑包络与实际engine版本；若另做contract-SI guide damping或runtime damping0实验，应产新配置/新SHA并保留本分支。**本轮结论止于来源/几何/MCI/表格/依赖与compile，full-DR实跑数=0。** 原源hash最终复核均未变。\n')
    md.write_text('\n'.join(L),encoding='utf-8')
    mci_table=[]
    for n,b in by.items():
        mci_table.append({'USD_body':n,'old_MJCF_body':b['old_mjcf_body'],'old_mass_kg':b['old_mass_kg'],'new_mass_kg':b['usd_mass_kg'],'old_COM_m':b['old_com_m'],'new_COM_m':b['usd_com_m'],'old_inertia_body_kg_m2':b['old_full_inertia_kg_m2'],'new_inertia_body_kg_m2':b['usd_full_inertia_kg_m2'],'new_principal_diag_kg_m2':s['usd']['bodies'][n]['diagonal_inertia_kg_m2'],'new_principal_axes_wxyz':s['usd']['bodies'][n]['principal_axes_wxyz'],'frame_rotation_USD_to_MJCF_col':mcis[n]['rotation_USD_to_MJCF_col'],'frame_translation_USD_to_MJCF_m':mcis[n]['translation_USD_to_MJCF_m']})
    index={'schema_version':1,'mode':'SRC_ONLY','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'PASS_COMPILE_ONLY_WITH_DECLARED_SEMANTIC_CHOICES','primary':r['primary'],'report':meta(md),'source_usd':r['source_usd'],'source_contract':r['source_contract'],'all_original_sources_unchanged':source_unchanged,'preexisting_exact_v1_MJCF_found_in_checked_scope':False,'source_scope':s['source_scope'],'checked_source_files':s['source_files'],
           'versions':s['versions'],'python':s['python'],'compile':{k:v for k,v in comp.items() if k not in ['body_com_inertia_max_errors','joint_table','actuator_table']},'compiled_MCI_max_errors':{k:max(abs(v[k]) for v in comp['body_com_inertia_max_errors'].values()) for k in ['mass_kg','com_m','inertia_kg_m2']},
           'full_DR_episodes_this_agent':0,'physics_time_advanced_s':0,'MjData_created':False,'robot_SDK_imports':0,'installation_attempts':0,'critical_flags':r['critical_flags'],'guide_damping_decision':r['damping_decision'],'MCI_table':mci_table,'joint_table_old_new':joints,'actuator_table':comp['actuator_table'],'motor_evidence':motor,'geometry_summary':g,'tire_meshes':r['tire_meshes'],'mesh_dependency_manifest':meta(HERE/'USD_SOURCE_DERIVATION_RECEIPT.json'),'mesh_dependency_count':r['mesh_dependencies']['count'],
           'timing':{'MuJoCo_physics_dt_s':0.0005,'traditional_control_hz_from_old_code':100,'USD_PhysX_physics_dt_s':0.0025,'USD_solver':'TGS32/4','USD_policy_hz':50,'USD_feedback_hz':100,'timing_physically_tested_this_turn':False},'superseded_preliminary':r['superseded_preliminary_candidate'],'three_MCI_diagnostic':d['diagnostic'],'errors_manifest':meta(HERE/'ATTEMPTS_AND_ERRORS.json')}
    artifact_names=['inspect_sources.py','analyze_alignment.py','generate_mjcf.py','finalize_geometry_candidate.py','verify_geometry.py','build_alignment_report.py','READER_ERRORS.json','ATTEMPTS_AND_ERRORS.json','SOURCE_AUDIT_DATA.json','USD_STATIC_DATA.json','USD_STATIC_RFC8259.json','SOURCE_COLLECTION_SUMMARY.json','ALIGNMENT_MEASUREMENTS.json','MEASUREMENT_SUMMARY.json','DERIVATION_RECEIPT.json','USD_SOURCE_DERIVATION_RECEIPT.json','USD_TIRE_MESHES.json','GEOMETRY_EQUIVALENCE.json','GEOMETRY_EQUIVALENCE_SUMMARY.json','MESH_DEPENDENCIES.json','BODY_MCI_TABLE.csv','JOINT_TABLE.csv','ACTUATOR_TABLE.csv','MOTOR_PARAMETERS_AUDIT.json','mod4v1_fullaligned_candidate.xml','mod4v1_fullaligned_candidate.xml.diff','mod4v1_three_mci_diagnostic.xml','mod4v1_three_mci_diagnostic.xml.diff','mod4v1_usd_source_aligned.xml','mod4v1_usd_source_aligned.xml.diff','usd_meshes/left_tire.stl','usd_meshes/right_tire.stl','SOURCE_COLLECTION_001.log','MEASUREMENT_001.log','MEASUREMENT_002.log','DERIVATION_001.log','GEOMETRY_VERIFY_001.log','GEOMETRY_EQUIVALENCE_FAILURE_001.txt','USD_SOURCE_DERIVATION_001.log','USD_SOURCE_DERIVATION_FAILURE_001.txt','USD_SOURCE_DERIVATION_002.log','GEOMETRY_VERIFY_002.log']
    index['artifacts']=[meta(HERE/n) for n in artifact_names]
    idxpath.write_text(json.dumps(clean(index),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({'report':meta(md),'index':meta(idxpath),'primary':r['primary'],'compiled_MCI_max_errors':index['compiled_MCI_max_errors'],'source_unchanged':source_unchanged,'status':index['status']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
