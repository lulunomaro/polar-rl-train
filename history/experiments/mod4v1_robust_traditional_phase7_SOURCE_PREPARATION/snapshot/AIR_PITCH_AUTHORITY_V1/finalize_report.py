"""Saved-evidence report/seal only; no MuJoCo imports or extra dynamics query."""
from pathlib import Path
from urllib.parse import unquote
import hashlib,json,math,re,struct
D=Path(__file__).resolve().parent;R=D.parent
load=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def link(path,label,frag=''):
    return '['+label+'](<'+str(path).replace('\\','/')+('#'+frag if frag else'')+'>)'
m=load(D/'METHOD.json');s=load(D/'SOURCE_LOCK.json');a=load(D/'FRAME_AMENDMENT.json');v=load(D/'RESPONSES.json');e=load(D/'FRAME_API_EVIDENCE.json')
assert sha(D/'METHOD.json')==s['method_SHA']==v['method_SHA']
assert sha(D/'SOURCE_LOCK.json')==v['source_lock_SHA'] and sha(D/'query_authority.py')==v['script_SHA']
assert sha(D/'FRAME_AMENDMENT.json')==v['frame_amendment_SHA'] and sha(D/'FRAME_API_EVIDENCE.json')==v['frame_API_evidence_SHA']
for x in s['sources']:assert sha(Path(x['path']))==x['SHA']
for x in e['sources']:assert sha(Path(x['path']))==x['SHA']
old=D/'revisions/query_attempt_01'
assert sha(old/'query_authority.py')==a['original_source_SHA'] and sha(old/'PARTIAL_ERROR.json')==a['original_failure_SHA']
for n in ['query_01.log','PARTIAL_ERROR.json','METHOD.json','SOURCE_LOCK.json']:assert sha(old/n)==sha(D/n)
failure=load(old/'PARTIAL_ERROR.json');assert failure['calls']['mj_forward']==1 and failure['rows']==[]
assert v['calls']['mj_forward']==12 and v['cumulative_mj_forward_calls']==13 and v['cumulative_model_boots']==2
assert v['first_diagnostic_frame_gate_passed']and len(v['rows'])==12 and len(v['response'])==9
assert all(v['calls'][k]==failure['calls'][k]==0 for k in m['blocked_integrators'])
assert all(r['ncon']==0 and r['time_s']==0 and r['pre_warmstart_all_zero']for r in v['rows'])
assert all(r['same_constraint_types_states']and r['nominal_contact_free_interpretation_eligible']for r in v['response'])
diags=[load(D/r['frame_diagnostic_file'])for r in v['rows']]
assert len(diags)==12
for x in diags:
    assert all(x['state_force_checks'].values()) and x['corrected_frame_error']<1e-8 and x['root_Jacobian_identity_error']<1e-14
    assert x['qacc_after_forward']==x['qacc_after_RNE']
    assert struct.pack('<'+str(len(x['qacc_after_forward']))+'d',*x['qacc_after_forward'])==struct.pack('<'+str(len(x['qacc_after_RNE']))+'d',*x['qacc_after_RNE'])
for pose in s['poses']:
    group=[r for r in v['rows']if r['pose']==pose['name']];assert len(group)==4 and len({r['qpos_SHA']for r in group})==1
    base=group[0]
    for rr in [r for r in v['response']if r['pose']==pose['name']]:
        row=next(r for r in group if r['query']==rr['channel'])
        assert rr['delta_root_pitch_qacc_rad_s2']==row['root_pitch_qacc_rad_s2']-base['root_pitch_qacc_rad_s2']
closure=max(r['eq_geometry_closure_max_m']for r in v['rows']);mimic=max(r['eq_mimic_position_max_rad']for r in v['rows'])
eqacc=max(r['eq_acceleration_residual_max_mixed_units']for r in v['rows'])
f=diags[0]
short={'crouch':'crouch','pushend_delta_plus_0p2':'pushend δ+.2','landing_delta0':'landing δ0'}
channel={'hip_pair_plus1':'双hip +1','crank_pair_plus1':'双crank +1','wheel_common_plus1':'双wheel +1'}
table=['| pose | 各选中轴+1Nm | Δroot pitch | ΔLH | ΔLC | ΔLW | ΔRH | ΔRC | ΔRW |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
for r in v['response']:
    nums=[r['delta_root_pitch_qacc_rad_s2']]+r['delta_hinge_qacc6_rad_s2']
    table.append('| '+short[r['pose']]+' | '+channel[r['channel']]+' | '+' | '.join(f'{z:+.6f}'for z in nums)+' |')
base='；'.join(short[r['pose']]+f"={r['root_pitch_qacc_rad_s2']:+.9f}"for r in v['rows']if r['query']=='zero')
api=Path(e['sources'][0]['path'])
lines=[
'# AIR_PITCH_AUTHORITY_V1 — 名义无接触瞬时输入响应，不是控制器',
'',
'## 范围与计数',
'- 三existing pose：'+link(R/'JUMP270_V1/GAIN_BANK.json','crouch','L7-L16')+'、'+link(R/'TALL_ROUGH_BANK_V1/gain_delta20.json','pushend δ+.2','L2-L11')+'、'+link(R/'TALL_ROUGH_BANK_V1/gain_delta0.json','landing δ0','L2-L11')+'；rootZ=1m、roll/pitch/yaw0、qvel0、canonical wheelphase0。',
'- '+link(D/'METHOD.json','原预锁方法')+' / '+link(D/'SOURCE_LOCK.json','8小来源SHA')+' / '+link(D/'FRAME_AMENDMENT.json','明确批准的一次frame修订/13上限')+' / '+link(D/'RESPONSES.json','完整12有效query与9差分，小JSON')+'。',
'- **累计13次mj_forward=原失败1+有效12，累计2次模型boot；6个integrator入口均0、所有有效query time=0。** 不是无说明地重跑：新crouch/0完整诊断先落盘，原阈值gate通过后才继续其余11。',
'- 所有有效12 query实际ncon=0；每次新MjData+resetData、同pose qpos字节一致，warmstart/qvel/act/applied forces先全0，没有前一ctrl记忆。原ground/所有geoms/闭链/solver/PD/DR未改；不构造Plant/controller/DR。',
'- 正常boot加载原279mesh；没有资产重hash或逐query遍历279mesh，没有raw/H5/DR样值/大pitch事件分析、新episode、编译、Git或新agent。',
'',
'## Actuator、pitch与gyro frame核对',
'- 原'+link(R/'MODEL_AUDIT/mod4v1_usd_source_aligned.xml','XML actuator','L776-L783')+'与compiled model核实row6=[LH,LC,LW,RH,RC,RW]，joint transmission、gear=[1,0,0,0,0,0]、fixed gain1/bias0/dynamics-none；实际actuator_force恰等于0/1 ctrl，广义力落在对应编译dof。**+1Nm EACH，一对合计+2Nm，不是总共+1Nm。**',
'- freejoint dofadr=0；在本identity/零速查询中，root pitch ddot取qacc[4]，与chassis角Jacobian Y及regular-frame angular acceleration相符。root Jacobian误差0，12点角加速度交叉核最大差'+f"{v['frame']['max_qacc_vs_object_angular_acceleration_error']:.3g}"+'；gyro为固连imu的site-local量，compiled site/body R均I。零gyro本身并非独立的非零姿态frame实验。',
'- **关键修正：mjOBJ_BODY/local是惯性主轴i-frame，mjOBJ_XBODY/local才是regular chassis frame。** 安装'+link(api,'API枚举:299–300','L299-L300')+'有明确语义，'+link(D/'FRAME_API_EVIDENCE.json','API证据')+'保留摘录和SHA。不能把BODY local Y当gyro/chassis Y。',
'- 新crouch/0诊断：regular XBODY Y='+f"{f['XBODY_regular_local_accel6'][1]:+.9f}"+'，BODY inertia-local Y='+f"{f['BODY_inertia_local_accel6'][1]:+.9f}"+' rad/s²；未变换的差'+f"{f['wrong_untransformed_BODY_local_vs_qacc_error']:.6f}"+'，经ximat旋回world后吻合。'+link(D/v['rows'][0]['frame_diagnostic_file'],'完整首新诊断')+'含全部qacc/Jacobians/body与site实际R、两种object/local-world值和调用阶段。',
'- 首脚本在1次forward后错误frame断言失败；其数值在断言后才计划写，故**原失败数字仍unknown，不用新基线retrofill**。'+link(old/'query_authority.py','原source')+'、'+link(old/'query_01.log','原失败log')+'、'+link(old/'PARTIAL_ERROR.json','原错误receipt')+'均保留。修订只改frame语义与先落盘后assert，1e−8/1e−14阈值、模型和solver未放宽；RNE前后qacc字节值不变。',
'',
'## 相对同pose ctrl0的加速度差',
'下表全部角加速度单位rad/s²；每列输入标量u=各选中motor共同增加1Nm。LH/LC等是实际hip/crank/wheel hinge，不是把passive knee或crank-minus-hip混作编码器角。',
]+table+[
'',
'- ctrl0绝对root pitch qacc：'+base+' rad/s²。未去掉原重力、气弹簧/被动项、armature或soft equalities，所以零ctrl不等于零加速度；crouch的单个+1通道也不保证抵消其全部baseline。',
'- **符号结论仅在这些模型torque坐标与姿态下：** 三pose的双hip、双crank和双wheel系数均负。若正pitch误差e需要恢复性负Δpitchddot，且u=k·e，则需a·k<0，故这里**k应为正号**；直接套u=−k·e(k>0)会给同向正Δpitchddot，即局部正反馈。没有选择k幅值、没有实现控制，也未证明position-target/D4链可直接沿用此符号。',
'- wheel common同样有负root反作用，但每轮自身瞬时Δqacc约573rad/s²/每轴1Nm，且伴随leg耦合；**这不是持续速度/动量/电压/电流/四象限DC权威**。本模型unit ctrl没有完整inverse-PD、processed-target、D4队列及实际motor tracking，不由本表推持续可用torque/速度时长。',
'',
'## 动力学解释边界与资格',
'- 位置闭链site残差最大'+f'{closure:.3g}'+'m，mimic joint残差'+str(mimic)+'rad；12点都是22条equality、相同type/state，Newton各1 iteration。原soft-equality加速度残差最大'+f'{eqacc:.6g}'+'（混合m/s²与rad/s²的诊断max，不是统一物理误差限），未调solref/solver或把qacc重新投影成理想刚性FK导数。',
'- 全模型动力学广义力方程残差max '+f"{v['max_dynamics_force_residual']:.3g}"+'（平动/转动混合单位诊断）。这些是固定nominal q/v的+1-vs0局部瞬时前向差；未验证负方向、其他幅度、非零姿态/速度、持续air过程或大pitch事件。objectAcceleration的线性后三项仅原始诊断，不命名完整trueCOMproper。',
'- 父提供的R60 fresh16仅10/16 local；本12名义query不扩大它，旧8seed7/8也不作为强鲁棒资格。没有新runtime、gain选择、动态稳定/概率证书、operating limit或contact confidence/permission提升。**PH7 pending。**',
]
text='\n'.join(lines)+'\n';assert len(lines)<=m['report_max_lines']
with (D/'REPORT.md').open('x',encoding='utf-8',newline='\n')as out:out.write(text)
links=re.findall(r'\]\(<([^>]+)>\)',text)
for t in links:
    name,_,frag=unquote(t).partition('#');p=Path(name);assert p.is_file(),name
    if frag:
        z=re.fullmatch(r'L(\d+)(?:-L(\d+))?',frag);assert z
        lo=int(z[1]);hi=int(z[2]or z[1]);assert 1<=lo<=hi<=len(p.read_text(encoding='utf-8').splitlines())
primary=['REPORT.md','RESPONSES.json','METHOD.json','SOURCE_LOCK.json','FRAME_AMENDMENT.json','FRAME_API_EVIDENCE.json',
    'query_authority.py','query_01.log','query_02.log','PARTIAL_ERROR.json','finalize_report.py']
receipt=dict(status='SEALED_NOMINAL_INSTANTANEOUS_AIR_RESPONSE_WITH_EXPLICIT_FRAME_FIX_NOT_RUNTIME_OR_ROBUSTNESS',
    report_lines=len(lines),verified_report_links=len(links),old_model_pose_source_SHAs_unchanged=len(s['sources']),installed_API_source_SHAs_unchanged=len(e['sources']),
    cumulative_model_boots=2,cumulative_forward_calls=13,effective_queries=12,original_failed_queries=1,original_failed_numeric_values='UNKNOWN_NOT_SAVED_NOT_RETROFILLED',
    cumulative_RNE_postconstraint_calls=13,integrator_entry_counts={k:0 for k in m['blocked_integrators']},
    first_new_baseline_full_diagnostic_saved_before_gate=True,first_new_frame_gate_passed=True,thresholds_unchanged=[1e-8,1e-14],
    all_effective_ncon_zero=True,all_effective_time_zero=True,same_pose_qpos_byte_identical=True,pre_warmstart_zero=True,
    frame=v['frame'],max_position_closure_residual_m=closure,max_mimic_position_residual_rad=mimic,
    original_soft_eq_acceleration_diagnostic_max_mixed_units=eqacc,authority=v['response'],
    PD_solver_model_modified=False,raw_H5_DR_samples_read=0,asset_archival_hashes=0,new_episodes=0,C_compiles=0,agents_started=0,Git_actions=0,
    controller_implemented=False,gain_selected=False,actual_large_pitch_event_cause_claim=False,stability_or_robustness_certificate=False,
    operating_limit=False,contact_confidence_increased=False,PH7_pending=True,
    files=[dict(path=n,bytes=(D/n).stat().st_size,SHA=sha(D/n))for n in primary],
    diagnostics=[dict(path=r['frame_diagnostic_file'],SHA=sha(D/r['frame_diagnostic_file']))for r in v['rows']],
    preserved_first_attempt=[dict(path='revisions/query_attempt_01/'+n,SHA=sha(old/n))for n in ['query_authority.py','query_01.log','PARTIAL_ERROR.json','METHOD.json','SOURCE_LOCK.json']])
with (D/'RECEIPT.json').open('x',encoding='utf-8')as out:json.dump(receipt,out,separators=(',',':'),allow_nan=False);out.write('\n')
print(json.dumps(dict(status=receipt['status'],report_lines=len(lines),sources_unchanged=8,API_headers_unchanged=3,effective_queries=12,cumulative_forward=13,
    cumulative_integrators=0,report_SHA=sha(D/'REPORT.md'),response_bytes=(D/'RESPONSES.json').stat().st_size,response_SHA=sha(D/'RESPONSES.json'),
    receipt_SHA=sha(D/'RECEIPT.json'),root_pitch_response=[dict(pose=x['pose'],channel=x['channel'],delta=x['delta_root_pitch_qacc_rad_s2'])for x in v['response']]),indent=2))
