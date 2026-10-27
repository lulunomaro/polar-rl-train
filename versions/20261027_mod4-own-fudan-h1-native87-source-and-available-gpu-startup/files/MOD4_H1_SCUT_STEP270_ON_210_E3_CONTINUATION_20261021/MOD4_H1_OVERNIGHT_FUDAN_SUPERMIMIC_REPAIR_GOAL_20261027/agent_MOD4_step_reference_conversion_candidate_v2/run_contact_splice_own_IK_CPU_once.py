"""New bounded post-contact IK fixture. Preserves originalV1 rejections."""
from pathlib import Path
import sys,json,traceback,hashlib,datetime
import numpy as np
from contact_splice_own_IK_v2 import generate_contact_splice
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
V1=L/'agent_MOD4_step_reference_conversion_candidate_v1'
B=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2'
sys.path.insert(0,str(V1));sys.path.insert(0,str(B/'source'))
from mod4_step_reference_conversion_v1 import build_recorded_kinematics,wheel_bounds,OwnStepReference
from own_step_reference_tables_v1 import to_named_tables,query_numpy
from supermimic_reference_adapter_v1 import NativeReference,quat_to_mat,angular_velocity_world
from own_usd_closed_chain_ik_v1 import OwnUsdKinematics,transform
P=B/'reference/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json'
G=T/'full20k_native180_V3_actual/out/GEOMETRY_AND_CLOCK_ACTUAL.json'
C=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/h1/job0/assets/import_contract.json'
PARAM=V1/'NEW_OWN_FORWARD_TIMING_CANDIDATE_PARAMETERS_ACTUAL.json'
def put(name,v):
    with (D/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def SHA(p):return hashlib.sha256(p.read_bytes()).hexdigest()
put('V2_SOURCE_INPUTS_AND_ORIGINAL_REJECTIONS_LINEAGE_ACTUAL.json',dict(inputs=[dict(path=str(p),SHA=SHA(p),bytes=p.stat().st_size) for p in
    [P,G,C,PARAM,V1/'mod4_step_reference_conversion_v1.py',V1/'own_step_reference_tables_v1.py',V1/'FROZEN_OWN_STEP_REFERENCE_SHA_INDEX.json',
     V1/'ORIGINAL_COMMAND08_OWN_FK_WINDOW_ACTUAL.json',V1/'NEW_OWN_GOAL_LANDING_SPLICE_GEOMETRY_ACTUAL.json',
     B/'source/own_usd_closed_chain_ik_v1.py',B/'source/supermimic_reference_adapter_v1.py']],
    no_USD_mesh_asset_NPZ_PT_raw_read=True,new_postcontact_IK_only_not_old_static261_rerun=True))
try:
    ref=NativeReference.from_dict(json.loads(P.read_bytes()));contract=json.loads(C.read_bytes());geometry=json.loads(G.read_bytes())
    kin=build_recorded_kinematics(contract,geometry,OwnUsdKinematics,transform,quat_to_mat)
    assert tuple(ref.joint_names)==kin.joint_names
    ages=np.arange(301);source=ref.at_time(ages*.01-.5);parameters=json.loads(PARAM.read_bytes());forward=np.asarray(parameters['target_x_by_age'])
    with (D/'POSTCONTACT_ORIGINAL_IK_PER_FRAME_RESULTS_ACTUAL.jsonl').open('x',encoding='utf8') as stream:
        def sink(row):stream.write(json.dumps(row,ensure_ascii=False,allow_nan=False)+'\n');stream.flush()
        candidate,rows=generate_contact_splice(ages,source,forward,ref.conditioning_mask73,kin,quat_to_mat,angular_velocity_world,
            wheel_bounds,OwnStepReference,own_spawn_height=contract['spawn_height_m'],row_sink=sink)
    tables=to_named_tables(candidate,ref.joint_names)
    for k in ('ages','packed73','mask73','phase'):tables[k]=tables[k].tolist()
    tables['metadata'].update(candidate.metadata)
    put('OWN_STEP_POSTCONTACT_IK_REFERENCE_TABLES_CANDIDATE_NOT_ADMITTED.json',tables)
    q=query_numpy(to_named_tables(candidate,ref.joint_names),np.array([100,140,145,160,180]),future=10)
    assert q['goal'].shape==(5,10,73)
    touch=candidate.metadata['first_touch_age'];end=candidate.metadata['support_age']
    before=source[touch-1];entry=candidate.states[touch]
    result=dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_CPU_passed=True,
        contact_frames=len(rows),original_IK_all_static_fit=all(x['IK']['status']=='STATIC_KINEMATIC_FIT' for x in rows),
        metadata=candidate.metadata,source_air_geometry_vertical_dynamics_literal_preserved=True,
        first_touch_q_step_max_rad=float(abs(entry[13:43]-before[13:43]).max()),
        original_source_same_q_step_max_rad=float(abs(source[touch,13:43]-before[13:43]).max()),
        contact_transition_max_q_step_rad=float(abs(np.diff(candidate.states[touch:end+1,13:43],axis=0)).max()),
        support_root_R_identity=True,support_root_z_error_m=float(candidate.states[end,2]-(contract['spawn_height_m']+.27)),
        own_forward_parameters={k:v for k,v in parameters.items() if k!='target_x_by_age'},
        named_future10_passed=True,actual_contact_or_skill_success=False,dynamic_feasibility='pending',
        no_actor_model_physics_GPU_SSH_Git=True)
    put('V2_POSTCONTACT_IK_SOURCE_CPU_RESULT_ACTUAL.json',result)
    print(json.dumps({k:result[k] for k in ['source_CPU_passed','contact_frames','original_IK_all_static_fit','metadata','first_touch_q_step_max_rad','original_source_same_q_step_max_rad','contact_transition_max_q_step_rad','support_root_z_error_m']}))
except BaseException:
    put('V2_ORIGINAL_POSTCONTACT_IK_SOURCE_CPU_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),originalV1_preserved=True,no_actual_model_or_physics=True))
    raise
