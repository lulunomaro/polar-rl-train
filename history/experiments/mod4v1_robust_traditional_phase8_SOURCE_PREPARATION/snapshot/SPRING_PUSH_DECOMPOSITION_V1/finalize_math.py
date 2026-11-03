"""Saved-evidence-only report/receipt; no NumPy/model imports or queries."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent;R=O.parent
S=json.loads((O/'SOURCE.json').read_bytes());M=json.loads((O/'METHOD.json').read_bytes());X=json.loads((O/'RESULT.json').read_bytes());D=json.loads((O/'ENDPOINTS.json').read_bytes())
def rec(p):
    b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
assert X['status']=='PASS_NEW_NOMINAL_STATIC_DECOMPOSITION_ONLY'and X['checks']==168 and X['error']is None
assert X['counts']==dict(models=1,FK_attempted=27,FK_completed=27,terms_calls=3)and not X['MuJoCo_imported']and X['physics_steps']==0
old=[]
for r in S['files']:
    a=rec(R/r['relative']);assert a['SHA']==r['SHA']and a['bytes']==r['bytes'];old.append(a)
for n in('SOURCE.json','METHOD.json','spring_push.py','run_once.py'):assert rec(O/n)['SHA']==rec(O/'attempt_001'/n)['SHA']
fd=max(g['max_abs_error']for g in X['gates']if g['kind']=='torque_Nm'and 'gradient'in g['label'])
powerr=max(g['abs_error']for g in X['gates']if g['kind']=='virtual_power_W')
def fmt(v):return '['+', '.join(f'{x:.10g}'for x in v)+']'
def link(label,path,anchor=''):return '['+label+'](<'+str(path.resolve()).replace('\\','/')+anchor+'>)'
lines=['# 气弹簧静态FF反补偿：名义端点分解（零步）','',
'**结论：固定其他支持项时，静态motor抵消项为 −tauGas；撤抵消应 `FF_new = FF_old + tauGas6`。只加四个leg行，不删除gravity/整条trim，也不改变物理气弹簧。等待父独立review，不自动PHY。**','',
'## 1. 来源、符号与单位',
'- '+link('旧NominalModel:107–148',R/'CONTACT_PROXY_NOMINAL_V1/nominal_model.py','#L107-L148')+'给出gas_scalar=k*(ref−s)−d*sdot，G=Dgas.T*gas_scalar，rhs=L−tauMotor−G−otherPassive。',
'- 固定B=L−otherPassive−J.T*Fsupport，则tauMotor_old=B−G；去掉抵消C=−G：tauMotor_new=tauMotor_old−C=tauMotor_old+G。实际gas保留，因此固定pose下净motor+gas相对原值增加G；不是删除模型spring。',
'- 静态sdot=0，仅弹性G进入静态FF反补偿；阻尼不是本helper要撤掉的项。s为MJCF slide位移(m)，不是气杆绝对长度；Dgas单位m/rad，scalar单位N，motor tau单位Nm。',
'- 输出四轴是绝对Lhip,Lcrank,Rhip,Rcrank；六轴为LH,LC,LW,RH,RC,RW。state14的4/6是crank-minus-hip，qabs=[s3,s3+s4,s5,s5+s6]，不是被动knee。',
'- 诊断delta广义力须A.T*tau_abs=[tauLH+tauLC,tauLC,tauRH+tauRC,tauRC]；这不是motor行的扭矩映射，勿直接塞入执行器FF。','',
'## 2. 锁定预算与实际执行',
'- '+link('METHOD',O/'METHOD.json')+'与'+link('SOURCE',O/'SOURCE.json')+'在helper/model执行前锁定：3既有public poses、eps=1e−5rad、1对象、每pose base+8 central FK；共27上限。',
'- 实际一次新执行：168 checks/0，17预声明typed错误，1 NominalModel、3静态terms、27/27 FK。复用内部FK缓存计算独立U=.5Σk(s−ref)^2，没有额外FK/potential查询。',
f'- 原门1e−6Nm abs+1e−8rel未改；−gradU与tauGas最大差 {fd:.12g} Nm。固定mixed qdot=[.13,−.21,−.17,.09]rad/s，弹性/阻尼/总气杆及delta协向量虚功均过门，最大功率差 {powerr:.12g} W。',
'- 功率门由torque门乘固定|qdot|逐项导出，属SI/FD/数值自洽，不是硬件置信、动态稳定或弹簧辨识。混合qd只在缓存D上代数计算，未触发nonzero-qd terms的额外FK。',
'- 0 MuJoCo/import/boot/forward/RNE/step/旧QA/DR样本/真值/raw/H5/Git/newagent；旧5小source末次SHA不变。','',
'## 3. 三个公开端点（高精度/完整D与scalar见数据）',
'|pose|s_slide L/R (m)|elastic scalar L/R (N)|tauGas4 (Nm)|old leg FF4 (Nm)|new leg FF4=old+Gas (Nm)|',
'|---|---|---|---|---|---|']
for row in D['endpoints']:
    ix=(0,1,3,4);lines.append('|'+row['name']+'|'+fmt(row['gas_slide2_m'])+'|'+fmt(row['elastic_scalar2_N'])+'|'+fmt(row['tauGas4_Nm'])+'|'+fmt([row['original_trim6_Nm'][i]for i in ix])+'|'+fmt([row['new_static_FF6_Nm'][i]for i in ix])+'|')
lines+=['', '每pose的Dgas (m/rad)，两行分别left/right slide：']
for row in D['endpoints']:lines.append('- '+row['name']+': '+fmt(row['Dgas_m_per_rad_2x4'][0])+' ; '+fmt(row['Dgas_m_per_rad_2x4'][1]))
lines+=['- wheel2/5的gas增量严格为0；原gain微小wheel trim约1e−10Nm逐bit保留，而不是把轮FF硬清零。',
'- 上表newFF含原trim的其余所有项；没有证明它是“纯重力”，也没有证明旧trim中存在一个可唯一辨识/单独存储的spring项。这里只定义并验证公共名义模型下的反补偿操作。','',
'## 4. 小helper API与绑定',
'- '+link('spring_push.py',O/'spring_push.py')+'只读加载缓存与5个旧public/gain小source一次、验SHA，不import NominalModel、不跑在线FK/辨识。'+link('ENDPOINTS.json',O/'ENDPOINTS.json')+'是父可绑定的实际数据文件。',
'- `book=load_precomputed(); start=book.endpoint("crouch").tauGas6_Nm; end=book.endpoint("pushend").tauGas6_Nm`，正号就是物理joint-output的G，可给父ctor(start_gas_tau6=...,end_gas_tau6=...)，不是−G。',
'- `book.timed_push_ff6(name, old_ff6, reference_absolute_q4, phase=..., enabled=False)` 默认原样独立copy；仅enabled=True且phase="timed_push"会在匹配的冻结端点reference/trim上加G；其他phase不改FF。',
'- finite/real/shape/overflow/错delta语义/原trim错绑均检查；输出immutable tuple/frozen endpoint，无mutable array alias；源数组不变、默认off/非push不变、wheel bit不变均为新单测事实。',
'- 不对任意中间pose/线性混合提供“精确去弹簧”证书；父若混合两端点FF，应显式标明名义端点近似，不当作tauGas(q(t))在线精确估计。','',
'## 5. 仍未知/不做的事',
'实际DR/安装/真实spring/ref/damping与公共名义模型的差异未知且未读取；没有抹掉DR。未改gain/模型/控制器、air h/轮策略/事件策略或物理gas。没有动力学/驱动/峰值/270/接触许可提升；表通过只允许父独立审查下一timed_push FF单变量实验。']
report='\n'.join(lines)+'\n';assert len(report.splitlines())<=70
with(O/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write(report)
receipt=dict(status='SEALED_NOMINAL_STATIC_SPRING_SIGN_FD_AND_PURE_HELPER_ONLY_NOT_PHYSICS',checks=168,typed_expected_errors=17,counts=X['counts'],torque_FD_max_abs_error_Nm=fd,virtual_power_max_abs_error_W=powerr,old_sources_unchanged=old,source=rec(O/'SOURCE.json'),method=rec(O/'METHOD.json'),report=rec(O/'REPORT.md'),report_lines=len(report.splitlines()),data=rec(O/'ENDPOINTS.json'),helper=rec(O/'spring_push.py'),result=rec(O/'RESULT.json'),run_log=rec(O/'run_001.log'),API='book=load_precomputed(); book.endpoint(crouch/pushend).tauGas6_Nm. FFnew=old+G, physical absolute motor row order; not delta covector.',runtime_FK=0,MuJoCo_imports=0,PHY=0,independent_parent_review_required=True,automatic_physics=False)
with(O/'RECEIPT.json').open('x',encoding='utf-8',newline='\n')as f:json.dump(receipt,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
