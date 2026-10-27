"""Midpoint horizontal goal design, original q/Z/R unchanged; interpolation is not physics."""
from pathlib import Path
import json,hashlib,sys,traceback,datetime
import numpy as np
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
V1=L/'agent_MOD4_ballistic_horizontal_reference_v1';GEO=L/'agent_MOD4_step_reference_conversion_candidate_v1'
IK=L/'agent_MOD4_step_reference_conversion_candidate_v2'
B=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2'
sys.path[:0]=[str(V1),str(GEO),str(IK),str(B/'source')]
from ballistic_horizontal_reference_v1 import profile
from mod4_step_reference_conversion_v1 import build_recorded_kinematics,wheel_bounds
from contact_splice_own_IK_v2 import slerp
from own_usd_closed_chain_ik_v1 import OwnUsdKinematics,transform
from supermimic_reference_adapter_v1 import quat_to_mat
P=V1/'MOD4_OWN_BALLISTIC_HORIZONTAL_REFERENCE_V1_NOT_ADMITTED.json'
C=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/h1/job0/assets/import_contract.json'
G=T/'full20k_native180_V3_actual/out/GEOMETRY_AND_CLOCK_ACTUAL.json'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
    with (D/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
put('SOURCE_LINEAGE_ACTUAL.json',dict(inputs=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in
    [P,C,G,V1/'ballistic_horizontal_reference_v1.py',GEO/'mod4_step_reference_conversion_v1.py',IK/'contact_splice_own_IK_v2.py']],
    no_IK_model_or_asset_read=True))
try:
    table=json.loads(P.read_bytes());states=np.asarray(table['packed73']);ages=np.asarray(table['ages']);meta=table['metadata']
    old_profile=meta['horizontal_reference_profile'];flight_start=122;touch=145;v=.9;brake=.4
    kin=build_recorded_kinematics(json.loads(C.read_bytes()),json.loads(G.read_bytes()),OwnUsdKinematics,transform,quat_to_mat)
    # Zero-X geometry decouples every horizontal inequality from the unchanged poses.
    base=states.copy();base[:,0]=0
    control_lo,control_hi,closure=wheel_bounds(base,kin,quat_to_mat)
    fractional=np.arange(120,145.0001,.25);quarter=[]
    for age in fractional:
        i=int(np.floor(age));u=age-i;j=min(i+1,len(states)-1)
        row=(1-u)*base[i]+u*base[j];row[3:7]=slerp(base[i,3:7],base[j,3:7],u)
        quarter.append(row)
    quarter=np.asarray(quarter);qlo,qhi,qclosure=wheel_bounds(quarter,kin,quat_to_mat)
    sample_ages=np.concatenate((ages,fractional));lo=np.concatenate((control_lo,qlo));hi=np.concatenate((control_hi,qhi))
    edge=.35;top=.27;end=1.15
    # X(vpre) is affine. Evaluate two explicit basis profiles, not a physics fit.
    x0,_,_=profile(sample_ages,0.,v,flight_start,touch,brake)
    x1,_,_=profile(sample_ages,1e-3,v,flight_start,touch,brake)
    coeff=(x1-x0)/1e-3
    upper=[];lower=[]
    for i,age in enumerate(sample_ages):
        for wheel in range(2):
            if age<touch and lo[i,wheel,2]<top-1e-9:
                upper.append((float((edge-hi[i,wheel,0]-x0[i])/coeff[i]) if coeff[i]>0 else np.inf,float(age),wheel,'pretop_front'))
            if age>=touch:
                lower.append((float((edge-lo[i,wheel,0]-x0[i])/coeff[i]),float(age),wheel,'posttouch_rear'))
                upper.append((float((end-hi[i,wheel,0]-x0[i])/coeff[i]),float(age),wheel,'posttouch_front'))
    lower_bound=max(0.,max(x[0] for x in lower));upper_bound=min(.18,min(x[0] for x in upper))
    if lower_bound>upper_bound:raise ValueError(dict(reason='NO_POSITIVE_BALLISTIC_INTERVAL',lower=lower_bound,upper=upper_bound))
    chosen=(lower_bound+upper_bound)/2
    old_v=old_profile['pre_request_speed_m_s']
    def report_for(pre):
        x,vx,p=profile(sample_ages,pre,v,flight_start,touch,brake)
        world_lo=lo[:,:,0]+x[:,None];world_hi=hi[:,:,0]+x[:,None]
        straddle=(world_hi>=edge)&(world_lo<edge);violations=straddle&(lo[:,:,2]<top-1e-9)
        pretop=(sample_ages[:,None]<touch)&(lo[:,:,2]<top-1e-9)
        pre_gap=float((edge-world_hi)[pretop].min())
        after=sample_ages>=touch
        rear_gap=float((world_lo[after]-edge).min());far_gap=float((end-world_hi[after]).min())
        return dict(passed=not bool(violations.any()) and rear_gap>=-1e-9 and far_gap>=-1e-9,
            violating_samples=[dict(age=float(sample_ages[i]),wheel=int(k),bottom_m=float(lo[i,k,2]),front_x_m=float(world_hi[i,k])) for i,k in np.argwhere(violations)],
            min_pretop_front_X_gap_m=pre_gap,min_posttouch_rear_X_gap_m=rear_gap,min_posttouch_far_edge_X_gap_m=far_gap,
            maxmin_X_margin_m=min(pre_gap,rear_gap,far_gap),
            min_bottom_during_front_rear_straddle_m=float(lo[:,:,2][straddle].min()),
            quarter_control_only_violations=[float(sample_ages[i]) for i,k in np.argwhere(violations) if i>=len(ages)])
    original=report_for(old_v);repaired=report_for(chosen)
    put('ORIGINAL_V1_CONTROL_AND_QUARTER_GRID_CHECK_ACTUAL.json',original)
    if not repaired['passed']:raise ValueError(dict(reason='MIDPOINT_GRID_CHECK_FAILED',report=repaired))
    x,vx,p=profile(ages,chosen,v,flight_start,touch,brake)
    updated=states.copy();updated[:,0]=x;updated[:,7]=vx
    keep=[i for i in range(73) if i not in (0,7)];assert np.array_equal(updated[:,keep],states[:,keep])
    assert (abs(vx[ages<100])<=.18).all() and (vx[(ages>=122)&(ages<=145)]==v).all()
    assert (vx[ages>=185]==0).all()
    # Best max-min score on a tiny affine parameter scan; target5mm is a design objective.
    maxmin=max((report_for(float(pre))['maxmin_X_margin_m'],float(pre)) for pre in np.linspace(lower_bound,upper_bound,1001))
    p.update(reference_only=True,physical_command_vx_m_s=.8,physical_public_request=[100,179],
        vpre_feasible_interval=[lower_bound,upper_bound],X_air_feasible_interval=[profile(np.array([122]),pre,v,122)[2]['X_air_m'] for pre in (lower_bound,upper_bound)],
        selection='midpoint_of_feasible_X_air_interval_not_upper_boundary',quarter_control_geometry_check_passed=True,
        design_margin_goal_m=.005,actual_midpoint_min_X_margin_m=repaired['maxmin_X_margin_m'],
        approximate_best_maxmin_X_margin_m=maxmin[0],approximate_best_maxmin_vpre=maxmin[1],
        actual_tracking_or_dynamics_qualified=False)
    newtable=dict(table);newtable['packed73']=updated.tolist();newmeta=dict(meta)
    newmeta.update(horizontal_reference_profile=p,horizontal_reference_source_SHA=H(P),
        horizontal_reference_original_V1_quarter_check=original,
        horizontal_reference_quarter_check=repaired,
        interpolation_check_scope='120..145 every.25control; shortest quaternion slerp+linearq/Z for FK only, no IK/physics',
        interpolation_closure_max_m=float(qclosure.max()),source_air_geometry_unchanged=True,
        actual_tracking_or_contact_qualification=False)
    newtable['metadata']=newmeta
    destination=D/'MOD4_OWN_BALLISTIC_HORIZONTAL_REFERENCE_V2_NOT_ADMITTED.json'
    put(destination.name,newtable)
    result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=True,
        reference=dict(path=str(destination),bytes=destination.stat().st_size,SHA=H(destination)),
        old_V1_quarter_check=original,midpoint_check=repaired,profile=p,
        binding_constraints=dict(lower=max(lower,key=lambda x:x[0]),upper=min(upper,key=lambda x:x[0])),
        quarter_sample_count=len(fractional),interpolation_closure_max_m=float(qclosure.max()),
        unchanged_columns=keep,no_IK_or_model_or_physics_GPU_SSH_Git=True)
    put('BALLISTIC_V2_MIDPOINT_QUARTER_CPU_RESULT_ACTUAL.json',result)
    print(json.dumps(dict(reference=result['reference'],old_V1=original,new=repaired,profile=p,interpolation_closure_max_m=float(qclosure.max()))))
except BaseException:
    put('ORIGINAL_BALLISTIC_V2_CPU_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),old_tables_unchanged=True,no_IK_or_physics=True))
    raise
