"""One saved-only scalar algebra pass. Never imports or calls project code."""
from pathlib import Path
import json,ast,math,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=Path(__file__).resolve().parent;OLD=ROOT.parent/'traditional_control_20261101';TOL=1e-9
PRE=ROOT/'R62_AIRREF_RESPONSE_CAUSAL_V1'
def rec(p):
    b=p.read_bytes();return dict(path=str(p.resolve()),bytes=len(b),SHA=hashlib.sha256(b).hexdigest())
def load(p):return json.loads(p.read_bytes())
def put(name,v):
    with(OUT/name).open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,allow_nan=False,separators=(',',':'));f.write('\n')
def vec(x):
    assert isinstance(x,list)and len(x)==6
    assert all(type(v)in(int,float)and math.isfinite(v)for v in x)
    return list(map(float,x))
def clip(x,l,h):return min(h,max(l,x))
def main():
    runtime=[ROOT/'physics_bridge_rm_grid_v1.py',ROOT/'physics_bridge_rm_buffer_v1.py',ROOT/'physics_bridge_rm_grade_v1.py',ROOT/'MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py',ROOT/'MINIHOP_AUDIT_V2/contact_grade_v2.py',OLD/'control_core.py',OLD/'full_lqr.py',OLD/'dr_components.py']
    reference=[ROOT/'physics_bridge.py',ROOT/'rm_grid_terrain_v1.py']
    inputs=[PRE/'EXTRACTED.json',PRE/'FACTS.json',PRE/'RECEIPT.json',PRE/'REPORT.md',ROOT/'results/r62_airref002_paired_RM_DR_4606/SOURCE_MANIFEST.json']
    refs=[rec(p)for p in runtime+reference+inputs];by={r['path']:r for r in refs}
    oldreceipt=load(PRE/'RECEIPT.json')
    oldarts={r['path']:r['SHA']for r in oldreceipt['artifacts']}
    for p in [PRE/'EXTRACTED.json',PRE/'FACTS.json',PRE/'REPORT.md']:assert by[str(p.resolve())]['SHA']==oldarts[str(p.resolve())]
    manifest=load(inputs[-1]);producer={str(Path(r['path']).resolve()):r['SHA']for r in manifest['files']}
    for p in runtime:assert producer[str(p.resolve())]==by[str(p.resolve())]['SHA'],('producer drift',p)
    trees={p:ast.parse(p.read_text(encoding='utf-8'))for p in runtime}
    ct=trees[OLD/'control_core.py'];order=None
    for n in ct.body:
        if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='ORDER'for t in n.targets):order=ast.literal_eval(n.value)
    assert order==('left_hip','left_crank','left_wheel_spin','right_hip','right_crank','right_wheel_spin')
    constants={}
    for n in ast.walk(trees[runtime[0]]):
        if not isinstance(n,ast.Assign):continue
        for target in n.targets:
            if isinstance(target,ast.Attribute)and isinstance(target.value,ast.Name)and target.value.id=='self'and target.attr in ['max_tau','stall','no_load']:
                v=n.value.args[0];assert isinstance(v,ast.BinOp)and isinstance(v.op,ast.Mult)and ast.literal_eval(v.right)==2
                constants[target.attr]=[float(x)for x in ast.literal_eval(v.left)]*2
    assert set(constants)=={'max_tau','stall','no_load'}
    assert all(len(v)==6 and all(math.isfinite(x)and x>0 for x in v)for v in constants.values())
    # Inherited clip is not overridden in these small bridge/mixin classes.
    for p in runtime[:5]+[OLD/'full_lqr.py']:
        assert not any(isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))and n.name=='clip'for n in ast.walk(trees[p]))
    # DR.sample receives plant, but its only direct plant-attribute assignment is mass.
    drwrites=[]
    for n in ast.walk(trees[OLD/'dr_components.py']):
        if isinstance(n,ast.Assign):
            for t in n.targets:
                if isinstance(t,ast.Attribute)and isinstance(t.value,ast.Name)and t.value.id=='plant':drwrites.append(t.attr)
    assert set(drwrites)<= {'mass'}
    E=load(PRE/'EXTRACTED.json');F=load(PRE/'FACTS.json');ph=E['new4606_physics'];win=ph['first_hard_window'];hard=F['new4606_physics']['hard_events']
    assert len(win)==7 and len(hard)==2
    byindex={r['sample_index']:r for r in win}
    for r in hard:
        w=byindex[r['sample_index']]
        assert r['stage_s']==w['stage_s']and r['actual_velocity6_rad_s']==w['actual_velocity6_rad_s']and r['actual_bounded_tau6_Nm']==w['actual_bounded_tau6_Nm']
        vec(r['actual_velocity6_rad_s']);vec(r['actual_bounded_tau6_Nm'])
    put('SOURCE_LOCK.json',dict(status='LOCKED_BEFORE_ALGEBRA',method=rec(OUT/'METHOD.json'),sources=refs,producer_runtime_SHA_matches=len(runtime),order=order,constants=constants,DR_direct_plant_assignments=drwrites,saved_stage_identity_valid=True,raw_content_reads=0))
    rows=[]
    for r in hard:
        for j in[2,5]:
            w=float(r['actual_velocity6_rad_s'][j]);a=float(r['actual_bounded_tau6_Nm'][j]);P=constants['max_tau'][j];S=constants['stall'][j];N=constants['no_load'][j]
            guard=N*(1+P/S);v=clip(w,-guard,guard);lo=max(-P,S*(-1-v/N));hi=min(P,S*(1-v/N))
            lo2=max(-P,-S-(S/N)*v);hi2=min(P,S-(S/N)*v)
            algebra=max(abs(lo-lo2),abs(hi-hi2));projection=abs(a-clip(a,lo,hi))
            assert lo<=hi and algebra<=TOL and projection<=TOL
            rows.append(dict(sample_index=r['sample_index'],PRE_s=r['stage_s'],axis=order[j],axis_index=j,omega_rad_s=w,omega_over_no_load=w/N,guard_rad_s=guard,guard_active=(v!=w),velocity_used_rad_s=v,no_load_rad_s=N,stall_Nm=S,peak_Nm=P,lo_Nm=lo,hi_Nm=hi,recorded_model_applied_Nm=a,margin_above_lo_Nm=a-lo,margin_below_hi_Nm=hi-a,on_lo=abs(a-lo)<=TOL,on_hi=abs(a-hi)<=TOL,within_box=True,above_no_load_abs=abs(w)>N,mandatory_brake=(lo>0 and w<0)or(hi<0 and w>0),algebra_rearrangement_error_Nm=algebra,recorded_applied_projection_residual_Nm=projection))
    first=[q for q in rows if q['sample_index']==hard[0]['sample_index']];second=[q for q in rows if q['sample_index']==hard[1]['sample_index']]
    cross=all(abs(a['omega_rad_s'])<=a['no_load_rad_s'] and b['omega_rad_s'] < -b['no_load_rad_s'] for a,b in zip(first,second))
    first_zero=all(q['lo_Nm']<=0<=q['hi_Nm']for q in first);second_brake=all(q['mandatory_brake']for q in second)
    headline='两轮保存的同stage速度在相邻hard tick均跨负向no-load，box由含零转成只许正τ的mandatory-brake'if cross and first_zero and second_brake else'未由这些保存值确认所提跨no-load/mandatory-brake组合假说；仅按下表报告已算box'
    result=dict(status='PASS_SAVED_STAGE_SIGNED_MODEL_BOX_ONLY',algebra_tolerance_Nm=TOL,rows=rows,saved_pre_window_rows=7,hard_rows=2,signed_wheel_mapping=list(order),source_constants=constants,raw_content_reads=0,original_project_execution_calls=0,proof_limit='Allowed same-stage model box and output headroom only; no raw-PD/clipmask/which-limiter-stage/hardware-feedback/electrical-power or unique-closed-loop-cause claim.',R62_original_gate='1/4 unchanged',PH8_pending=True)
    put('RESULTS.json',result)
    report=['# R62 driver headroom：仅saved两hard tick','',
      '**结论：'+headline+'；这是模型允许box/输出一致性，不是clip事件归因。**','',
      '- Catalog仅Office/ACL，无robotics匹配；仅saved [EXTRACTED](<../R62_AIRREF_RESPONSE_CAUSAL_V1/EXTRACTED.json>)/[FACTS](<../R62_AIRREF_RESPONSE_CAUSAL_V1/FACTS.json>)七PRE小窗及必要原driver小源/producer metadata，0原raw reopen/driver调用/controller/model/PHY/QA/Git/agent。',
      '- [capture:43–60](<../MINIHOP_AUDIT_V2/contact_grade_v2.py#L43-L60>)直接存actual_dq和bounded；[实际driver:12–15](<../MINIHOP_AUDIT_V2/physics_bridge_minihop_rm_v2.py#L12-L15>)的actual_dq=d.qvel[self.vids]。不是packet速度，更未从τ反解ω。',
      '- [RM构造:26](<../physics_bridge_rm_grid_v1.py#L26>)按[ORDER:14](<../../traditional_control_20261101/control_core.py#L14>)映射signed6=LH LC LW RH RC RW；wheel索引2/5。常量来自此实际RM构造、匹配producer SHA；DR未重设该box三常量。',
      '- [原clip:127–130](<../../traditional_control_20261101/control_core.py#L127-L130>)：v=clip(ω,±N(1+P/S)); lo=max(-P,S(-1-v/N)); hi=min(P,S(1-v/N))。N=55.3557rad/s，S=28.18532894736838Nm，P=5.775909774436091Nm。',
      '- 预声明[代数门](<METHOD.json>)1e-9Nm：直接源表达式与重排仿射式比较，并检查已保存输出对box的重投影残差；没有执行原函数或改任何物理gate。','',
      '|PRE s|wheel|ω rad/s|ω/N|lo / hi Nm|saved applied Nm|applied-lo Nm|hi-applied Nm|mandatory brake|','|---:|---|---:|---:|---:|---:|---:|---:|---|']
    for q in rows:report.append(f"|{q['PRE_s']:.4f}|{'L'if q['axis_index']==2 else'R'}|{q['omega_rad_s']:.9f}|{q['omega_over_no_load']:.9f}|{q['lo_Nm']:.9f} / {q['hi_Nm']:.9f}|{q['recorded_model_applied_Nm']:.9f}|{q['margin_above_lo_Nm']:.9f}|{q['margin_below_hi_Nm']:.9f}|{q['mandatory_brake']}|")
    report+=['',f"- 全4条scalar algebra最大差{max(q['algebra_rearrangement_error_Nm']for q in rows):.3g}Nm，输出重投影残差最大{max(q['recorded_applied_projection_residual_Nm']for q in rows):.3g}Nm；速度guard active条数={sum(q['guard_active']for q in rows)}。",
      f'- 首tick各box含零={first_zero}；两轮跨负向no-load={cross}；次tick两轮mandatory-brake={second_brake}。这些是直接signed ω/box判断，不证明某个单独clip stage触发或该机制是闭环失败唯一原因。',
      '- 表中余量/on-bound是相对于同PRE允许box；actual_tau为最终bounded d.ctrl模型命令，非独立测得电机力矩。原链仍有D4/PD/inner clip/gain/outer clip，raw-PD和clipmask未记录，不补值；电流/母线再生/实机资格不在本证明中。',
      '- 原R62 1/4、002 sealed/default-off、所有旧报告/源保持不变，不拟合gain/第三h。PH8 pending；[RESULTS](<RESULTS.json>)保留全精度，[SOURCE_LOCK](<SOURCE_LOCK.json>)与[receipt](<RECEIPT.json>)保留选定小源SHA。']
    assert len(report)<=45
    with(OUT/'REPORT.md').open('x',encoding='utf-8',newline='\n')as f:f.write('\n'.join(report)+'\n')
    for z in refs:assert rec(Path(z['path']))['SHA']==z['SHA']
    receipt=dict(status='SEALED_SAVED_ONLY_MODEL_DRIVER_BOX_NOT_LIMITER_OR_HARDWARE_QUALIFICATION',report_lines=len(report),algebra_runs=1,source_count=len(refs),producer_runtime_SHA_matches=len(runtime),sources=refs,outputs=[rec(OUT/n)for n in['REPORT.md','RESULTS.json','SOURCE_LOCK.json','METHOD.json','saved_box.py']],raw_content_reads=0,original_driver_controller_model_PHY_QA_calls=0,unchanged_old_seal=True,R62_original_gate='1/4 unchanged',PH8_pending=True)
    put('RECEIPT.json',receipt)
    print(json.dumps(dict(status=receipt['status'],rows=rows,report=rec(OUT/'REPORT.md'),result=rec(OUT/'RESULTS.json'),receipt=rec(OUT/'RECEIPT.json')),indent=2))
if __name__=='__main__':
    try:main()
    except BaseException as e:
        put('UNKNOWN.json',dict(status='UNKNOWN_STOPPED_NO_RAW_REOPEN',reason=type(e).__name__+': '+str(e),raw_content_reads=0));raise
