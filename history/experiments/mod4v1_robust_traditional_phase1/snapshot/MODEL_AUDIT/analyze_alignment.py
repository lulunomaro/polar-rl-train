"""Compare already collected static facts; no model or physics calls."""
from pathlib import Path
import json, hashlib
import numpy as np
from inspect_sources import rot, tensor
OUT=Path(__file__).resolve().parent
V1=Path(r'F:\RMPOLAR-RL\mod4_usd_scut_fudan_20261101\candidates\v1')

def main():
    out=OUT/'ALIGNMENT_MEASUREMENTS.json'
    d=json.loads((OUT/'SOURCE_AUDIT_DATA.json').read_text(encoding='utf-8'));o=d['old_compile'];u=d['usd'];c=json.loads((V1/'assets/import_contract.json').read_text(encoding='utf-8'))
    change={x['body']:x for x in json.loads((V1/'body_mass_changes.json').read_text(encoding='utf-8'))}
    frames={}
    def frame(n):
        if n in frames:return frames[n]
        b=o['bodies'][n];R=rot(b['parent_relative_quat_wxyz']);p=np.asarray(b['parent_relative_position_m'])
        if b['parent']=='world':value=(p,R)
        else:
            pp,pr=frame(b['parent']);value=(pp+pr@p,pr@R)
        frames[n]=value;return value
    frame('chassis');baseP,baseR=frames['chassis']
    body_mapping=[]
    for un,ub in u['bodies'].items():
        p=np.asarray(ub['base_relative_position_m']);R=np.asarray(ub['base_relative_rotation_col'])
        candidates=[]
        for on in o['bodies']:
            op,oR=frame(on);op=baseR.T@(op-baseP);oR=baseR.T@oR
            err=float(np.max(np.abs(op-p)));rerr=float(np.max(np.abs(oR-R)))
            if err<1e-7 and rerr<1e-7:candidates.append((on,err,rerr))
        assert len(candidates)==1,(un,candidates)
        on,err,rerr=candidates[0];ob=o['bodies'][on];oldI=np.asarray(ob['full_inertia_kg_m2'])
        baseline=change[un]['before'] if un in change else c['bodies'][un]
        beforeI=tensor(baseline['diagonal_inertia_kg_m2'],baseline['principal_axes_wxyz'])
        body_mapping.append({'usd_body':un,'old_mjcf_body':on,'evidence':'unique neutral position+orientation match, then topology/joint/geometry comparisons; not body-name-only',
             'position_error_m':err,'rotation_matrix_max_error':rerr,'old_mass_kg':ob['mass_kg'],'usd_mass_kg':ub['mass_kg'],'mass_delta_kg':ub['mass_kg']-ob['mass_kg'],
             'old_com_m':ob['com_m'],'usd_com_m':ub['com_m'],'old_full_inertia_kg_m2':ob['full_inertia_kg_m2'],'usd_full_inertia_kg_m2':ub['full_inertia_kg_m2'],
             'usd_contract_mass_error_kg':ub['mass_kg']-c['bodies'][un]['mass_kg'],
             'usd_contract_com_max_error_m':float(np.max(np.abs(np.asarray(ub['com_m'])-c['bodies'][un]['com_m']))),
             'usd_contract_inertia_max_error':float(np.max(np.abs(np.asarray(ub['full_inertia_kg_m2'])-tensor(c['bodies'][un]['diagonal_inertia_kg_m2'],c['bodies'][un]['principal_axes_wxyz'])))),
             'baseline_mass_error_kg':ob['mass_kg']-baseline['mass_kg'],
             'baseline_com_max_error_m':float(np.max(np.abs(np.asarray(ob['com_m'])-baseline['com_m']))),
             'baseline_tensor_max_error':float(np.max(np.abs(oldI-beforeI)))})
    bm={r['usd_body']:r['old_mjcf_body'] for r in body_mapping}
    invbm={v:k for k,v in bm.items()}
    joints=[]
    for un,uj in c['joints'].items():
        # Match physical child (and parent); names of eight idlers differ.
        child=bm[uj['child']];parent=bm[uj['parent']]
        matches=[(n,j) for n,j in o['joints'].items() if j['body']==child and o['bodies'][child]['parent']==parent]
        assert len(matches)==1,(un,matches)
        on,oj=matches[0];sp=u['joints'][un];sa=sp['attrs']
        oldpos=np.asarray(o['bodies'][child]['parent_relative_position_m'])+rot(o['bodies'][child]['parent_relative_quat_wxyz'])@np.asarray(oj['pos_m'])
        sjaxis={'X':np.array([1.,0,0]),'Y':np.array([0.,1,0]),'Z':np.array([0.,0,1])}[sa.get('physics:axis','X')]
        axis=rot(sa['physics:localRot0'])@sjaxis
        stage_limits=None
        lo=sa.get('physics:lowerLimit');hi=sa.get('physics:upperLimit')
        if lo is not None and hi is not None and np.isfinite(lo) and np.isfinite(hi):stage_limits=np.array([lo,hi])*(1 if uj['type']=='slide' else np.pi/180)
        legname='linear' if uj['type']=='slide' else 'angular'
        usd_damp=sa.get('drive:'+legname+':physics:damping',0)*(1 if uj['type']=='slide' else 180/np.pi)
        limits_error=None if stage_limits is None and not oj['limited'] else (float(np.max(np.abs(np.array(oj['range'])-stage_limits))) if stage_limits is not None and oj['limited'] else 'limited mismatch')
        joints.append({'usd_joint':un,'old_mjcf_joint':on,'usd_parent':uj['parent'],'usd_child':uj['child'],'old_parent':parent,'old_child':child,
             'parent_anchor_max_error_m':float(np.max(np.abs(oldpos-sa['physics:localPos0']))),'child_anchor_max_error_m':float(np.max(np.abs(np.asarray(oj['pos_m'])-sa['physics:localPos1']))),
             'axis_vector_max_error':float(np.max(np.abs(axis-oj['axis']))),'limits_error_si':limits_error,'old':oj,
             'usd_limits_si':None if stage_limits is None else stage_limits.tolist(),'usd_armature':sa.get('physxJoint:armature'), 'usd_damping_si':usd_damp,
             'contract_damping_si':uj['damping_si'],'usd_gas_stiffness':sa.get('drive:linear:physics:stiffness') if uj['type']=='slide' else None,
             'usd_gas_target_m':sa.get('drive:linear:physics:targetPosition') if uj['type']=='slide' else None})
    geom=[]
    for un,ug in c['geometry'].items():
        if ug['body'].startswith('guide_roller'):
            on=next(n for n,g in o['geometry'].items() if g['body']==bm[ug['body']])
        else:on=un
        og=o['geometry'][on]
        # Symmetry of cylindrical/capsule axes means q and -q are equivalent.
        a=rot(og['quat_wxyz']);b=rot(ug['quat_wxyz']);typ=og['type']
        rerr=float(np.max(np.abs(np.outer(a[:,2],a[:,2])-np.outer(b[:,2],b[:,2])))) if typ in [3,5] else float(np.max(np.abs(a-b)))
        sg=u['geometry'][un];mat=u['materials'].get(sg['physics_material'],{})
        geom.append({'usd_geometry':un,'old_mjcf_geometry':on,'usd_body':ug['body'],'old_mjcf_body':og['body'],'visual':ug['visual'],'type_matches':og['type']==ug['type'],
            'position_max_error_m':float(np.max(np.abs(np.asarray(og['position_m'])-ug['position_m']))),'size_max_error_m':float(np.max(np.abs(np.asarray(og['size'])-ug['size']))),
            'rotation_or_axis_projector_max_error':rerr, 'old_size':og['size'],'usd_contract_size':ug['size'],'old_friction':og['friction'],'usd_static_friction':mat.get('physics:staticFriction'),
            'usd_dynamic_friction':mat.get('physics:dynamicFriction'),'old_condim':og['condim']})
    closures=[]
    for n,spec in c['closures'].items():
        j=u['joints'][n];a=j['attrs']
        # Compare their semantic anchor evidence against original XML sites.
        closures.append({'name':n,'usd_type':j['type'],'usd_excluded_from_articulation':a.get('physics:excludeFromArticulation'), 'contract':spec,
                         'usd_local_pos0':a['physics:localPos0'],'usd_local_pos1':a['physics:localPos1']})
    data={'frame_mapping':body_mapping,'joint_mapping':joints,'geometry_mapping':geom,'closures':closures,'mimics':c['mimics'],
          'old_mass_kg':o['mass_sum_kg'],'usd_mass_kg':sum(b['mass_kg'] for b in u['bodies'].values()),
          'frame_mapping_max_error_m':max(x['position_error_m'] for x in body_mapping),
          'common_geometry_max_errors':{k:max(x[k] for x in geom if not x['usd_body'].startswith('guide_roller')) for k in ['position_max_error_m','size_max_error_m','rotation_or_axis_projector_max_error']},
          'nonroller_joint_max_errors':{k:max(x[k] for x in joints if not x['usd_child'].startswith('guide_roller')) for k in ['parent_anchor_max_error_m','child_anchor_max_error_m','axis_vector_max_error']}}
    if out.exists():
        assert json.loads(out.read_text(encoding='utf-8')) == data, 'Do not replace changed prior measurements'
    else:
        out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    summary={'frame_max':data['frame_mapping_max_error_m'],'mass_old_usd': [data['old_mass_kg'],data['usd_mass_kg']],
             'geometry_max':data['common_geometry_max_errors'],'nonroller_joints_max':data['nonroller_joint_max_errors'],
             'joint_differences':[{k:r[k] for k in ['usd_joint','old_mjcf_joint','limits_error_si','usd_armature','usd_damping_si','contract_damping_si']} for r in joints if r['limits_error_si']=='limited mismatch' or (r['limits_error_si'] is not None and r['limits_error_si']>1e-7) or (r['usd_armature'] is None or abs(r['old']['armature']-r['usd_armature'])>1e-7) or abs(r['old']['damping_si']-r['usd_damping_si'])>1e-7],
             'roller_geometry':[g for g in geom if g['usd_body'].startswith('guide_roller')],
             'before_mass_com_tensor_three':[{k:r[k] for k in ['usd_body','position_error_m','baseline_mass_error_kg','baseline_com_max_error_m','baseline_tensor_max_error']} for r in body_mapping if r['usd_body'] in change]}
    (OUT/'MEASUREMENT_SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='roller_geometry'},indent=2))
if __name__=='__main__': main()
