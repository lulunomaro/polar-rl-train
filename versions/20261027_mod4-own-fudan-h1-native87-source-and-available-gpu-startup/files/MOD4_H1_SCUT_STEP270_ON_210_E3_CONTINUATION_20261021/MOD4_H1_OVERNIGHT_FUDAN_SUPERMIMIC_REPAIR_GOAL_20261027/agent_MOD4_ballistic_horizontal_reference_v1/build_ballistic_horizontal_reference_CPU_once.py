"""Existing table/FK and source contact JSON only; no IK/model/physics/raw."""
from pathlib import Path
import json,hashlib,traceback,sys,datetime
import numpy as np
from ballistic_horizontal_reference_v1 import choose_profile
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
V1=L/'agent_MOD4_step_reference_conversion_candidate_v1'
B=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2'
sys.path[:0]=[str(V1),str(B/'source')]
from mod4_step_reference_conversion_v1 import build_recorded_kinematics,wheel_bounds
from own_usd_closed_chain_ik_v1 import OwnUsdKinematics,transform
from supermimic_reference_adapter_v1 import quat_to_mat
P=L/'root_native_bridge_integration_candidate/MOD4_OWN_CONVERTED_FUDAN_JUMP_REFERENCE_V1_NOT_ADMITTED.json'
R=B/'reference/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json'
C=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/h1/job0/assets/import_contract.json'
G=T/'full20k_native180_V3_actual/out/GEOMETRY_AND_CLOCK_ACTUAL.json'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,v):
    with (D/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
put('BALLISTIC_SOURCE_LINEAGE_ACTUAL.json',dict(inputs=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in [P,R,C,G,V1/'mod4_step_reference_conversion_v1.py',B/'source/own_usd_closed_chain_ik_v1.py']],no_IK_USD_mesh_asset_raw_NPZ_PT_or_model=True))
try:
    table=json.loads(P.read_bytes());old=np.asarray(table['packed73']);ages=np.asarray(table['ages'])
    kin=build_recorded_kinematics(json.loads(C.read_bytes()),json.loads(G.read_bytes()),OwnUsdKinematics,transform,quat_to_mat)
    low,high,closure=wheel_bounds(old,kin,quat_to_mat)
    source=json.loads(R.read_bytes())['metadata']['source_contact_reference']
    times=np.asarray(source['time_s']);query=np.clip(ages*.01-.5,times[0],times[-1]);idx=np.searchsorted(times,query+1e-10,side='right')-1
    contacts=np.asarray(source['left_right_contact'],bool)[idx]
    def first(mask):
        found=np.where(mask&(ages>=100)&(ages<145))[0]
        return int(ages[found[0]]) if len(found) else None
    marker=dict(source_either_wheel_contact_false_first_age=first(~contacts.all(-1)),
        source_both_wheels_contact_false_first_age=first(~contacts.any(-1)),
        own_both_wheel_bottom_over005_first_age=first((low[:,:,2]>.005).all(-1)),
        source_contacts_are_foreign_phase_markers_not_actual_own_contact=True)
    # Earliest warning is deliberately conservative, including one-wheel loss.
    flight_start=min(v for k,v in marker.items() if k.endswith('_age') and v is not None)
    marker.update(selected_conservative_flight_start_age=flight_start,
        selection='earliest of either/both source contact loss and own both-bottom>.005; not a measured own takeoff')
    put('BALLISTIC_FLIGHT_MARKERS_AND_OWN_FK_BOUNDS_ACTUAL.json',dict(markers=marker,ages=ages.tolist(),
        wheel_low=low.tolist(),wheel_high=high.tolist(),source_left_right_contact=contacts.tolist(),closure_max_m=float(closure.max())))
    x,vx,profile=choose_profile(ages,old,low,high,flight_start)
    updated=old.copy();updated[:,0]=x;updated[:,7]=vx
    # Only the two explicitly authorized channels change.
    keep=[i for i in range(73) if i not in (0,7)]
    assert np.array_equal(updated[:,keep],old[:,keep])
    assert x[0]==0. and (abs(vx[ages<100])<=.18).all()
    air=(ages>=flight_start)&(ages<=145)
    assert np.array_equal(vx[air],np.full(air.sum(),profile['flight_vx_m_s']))
    assert (np.diff(vx[air])==0).all()
    stop=profile['stop_age'];assert (vx[ages>=stop]==0).all() and (x[ages>=stop]==x[ages>=stop][0]).all()
    lo=low.copy();hi=high.copy();lo[:,:,0]+=x[:,None]-old[:,None,0];hi[:,:,0]+=x[:,None]-old[:,None,0]
    wheels=[]
    for k,name in enumerate(kin.wheel_names):
        crossed=hi[:,k,0]>=.35;straddle=crossed&(lo[:,k,0]<.35);bad=straddle&(lo[:,k,2]<.27-1e-9)
        wheels.append(dict(name=name,first_front_cross_age=int(ages[np.where(crossed)[0][0]]),
            straddling_ages=ages[straddle].tolist(),violating_ages=ages[bad].tolist(),
            min_bottom_during_straddle_m=float(lo[straddle,k,2].min()),
            first_touch_rear_x_m=float(lo[145,k,0]),max_posttouch_front_x_m=float(hi[145:,k,0].max())))
    assert all(not r['violating_ages'] for r in wheels)
    assert (lo[145:,:,0]>=.35).all() and (hi[145:,:,0]<=1.15).all()
    table['packed73']=updated.tolist();meta=dict(table['metadata'])
    meta.update(horizontal_reference_profile=profile,horizontal_flight_markers=marker,
        horizontal_reference_source_SHA=H(P),horizontal_only_channels_changed=['root_X','root_VX'],
        source_air_Z_R_q_Vz_omega_qd_literal_unchanged=True,flight_horizontal_acceleration_m_s2=0.,
        physical_command_and_request_unchanged=True,actual_own_contact_or_dynamic_qualification=False,
        whole_path_sidewall_static_check=dict(passed=True,wheels=wheels))
    table['metadata']=meta
    final=D/'MOD4_OWN_BALLISTIC_HORIZONTAL_REFERENCE_V1_NOT_ADMITTED.json'
    put(final.name,table)
    result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_CPU_passed=True,
        final=dict(path=str(final),bytes=final.stat().st_size,SHA=H(final)),profile=profile,flight_markers=marker,
        ready_speed_component_only=dict(max_pre_request_abs_vx_m_s=float(abs(vx[ages<100]).max()),original_threshold_m_s=.2,
            planned_limit_m_s=.18,original80callbacks_ready_rule_unchanged=True,actual_ready_not_measured=True),
        flight_VX_literal_constant=True,flight_AX_exact_zero=True,only_X_VX_modified=True,
        posttouch_stop_age=stop,standing_endpoint_through300=True,sidewall=dict(passed=True,wheels=wheels),
        min_posttouch_bottom_m=float(lo[145:,:,2].min()),max_posttouch_front_x_m=float(hi[145:,:,0].max()),
        full_body_collision_and_actuation_and_actual_contacts='pending',no_IK_or_actor_physics_GPU_SSH_Git=True)
    put('BALLISTIC_HORIZONTAL_REFERENCE_CPU_RESULT_ACTUAL.json',result)
    print(json.dumps(dict(final=result['final'],flight_markers=marker,profile={k:v for k,v in profile.items() if k!='attempts'},sidewall=wheels)))
except BaseException:
    put('BALLISTIC_HORIZONTAL_ORIGINAL_CPU_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),old_tables_untouched=True,no_IK_model_or_physics=True))
    raise
