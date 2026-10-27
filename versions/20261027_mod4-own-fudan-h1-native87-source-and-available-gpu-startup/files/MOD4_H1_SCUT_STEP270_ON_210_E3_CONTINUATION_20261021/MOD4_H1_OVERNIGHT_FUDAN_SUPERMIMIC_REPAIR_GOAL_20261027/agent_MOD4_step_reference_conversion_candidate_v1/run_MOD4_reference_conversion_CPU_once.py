"""Own FK/reference JSON only; no IK rerun, USD, mesh asset, NPZ or model IO."""
from pathlib import Path
import sys,json,hashlib,traceback,datetime
import numpy as np
import mod4_step_reference_conversion_v1 as c
D=Path(__file__).resolve().parent;T=D.parent.parent;W=T.parent
B=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2'
J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026'
sys.path.insert(0,str(B/'source'))
from supermimic_reference_adapter_v1 import NativeReference,quat_to_mat
from own_usd_closed_chain_ik_v1 import OwnUsdKinematics,transform
P=B/'reference/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json'
G=T/'full20k_native180_V3_actual/out/GEOMETRY_AND_CLOCK_ACTUAL.json'
C=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/h1/job0/assets/import_contract.json'
DRAW=J/'agent_reference_retarget_cpu/ACTUAL_FUDAN_CONSTRAINED_RETARGET_V2_1793005471832546700/STATIC_KINEMATIC_DRAW_DATA.json'
EXPORT=W/'polar-rl-train/sources/remote/incoming/rm2025_fixed/tools/export_usd.py'
def put(name,value):
    with (D/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs=[P,G,C,DRAW,EXPORT,B/'source/own_usd_closed_chain_ik_v1.py',B/'source/supermimic_reference_adapter_v1.py']
put('SOURCE_INPUT_LINEAGE_ACTUAL.json',dict(inputs=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in inputs],
    no_USD_mesh_asset_NPZ_PT_or_actual_trace_read=True))
try:
    reference=NativeReference.from_dict(json.loads(P.read_bytes()))
    geometry=json.loads(G.read_bytes());contract=json.loads(C.read_bytes())
    require_axis='CreateAxisAttr(\'X\')' in EXPORT.read_text('utf8')
    assert require_axis,'Recorded exporter axisX convention missing'
    kin=c.build_recorded_kinematics(contract,geometry,OwnUsdKinematics,transform,quat_to_mat)
    assert tuple(reference.joint_names)==kin.joint_names,'reference/FK order mismatch'
    selected=json.loads(DRAW.read_bytes())['frames'];wheel_error=[]
    for row in selected:
        age=round(row['reference_time_s']/.01)+50
        state=reference.at_time(np.asarray(age*.01-.5))
        poses=kin.forward(np.asarray(row['joint_pos30']),enforce_transmission=False)
        for wheel in kin.wheel_names:
            world=quat_to_mat(state[3:7])@poses[wheel][:3,3]+state[:3]
            wheel_error.append(float(np.max(abs(world-np.asarray(row['body_world_m'][wheel])))))
    assert max(wheel_error)<1e-6,('recorded contract wheel FK differs from prior USD-derived selected poses',max(wheel_error))
    ages=np.arange(0,301);states=reference.at_time(ages*.01-.5)
    strict,report=c.generate_candidate(ages,states,reference.conditioning_mask73,kin,quat_to_mat)
    put('ORIGINAL_COMMAND08_OWN_FK_WINDOW_ACTUAL.json',report)
    x,parameters=c.bounded_own_forward_timing(ages,states,kin,quat_to_mat)
    put('NEW_OWN_FORWARD_TIMING_CANDIDATE_PARAMETERS_ACTUAL.json',parameters)
    candidate,newreport=c.generate_candidate(ages,states,reference.conditioning_mask73,kin,quat_to_mat,root_x_path=x)
    put('NEW_OWN_GOAL_LANDING_SPLICE_GEOMETRY_ACTUAL.json',newreport)
    if candidate is not None:
        put('OWN_STEP_REFERENCE_GEOMETRIC_CANDIDATE_NOT_ADMITTED.json',dict(ages=candidate.ages.tolist(),states=candidate.states.tolist(),
             masks=candidate.masks.tolist(),phases=candidate.phases.tolist(),metadata=candidate.metadata))
    # Pure named-goal API consistency, independent of whether conversion is admitted.
    tiny=c.OwnStepReference(np.arange(12),np.zeros((12,73)),np.ones((12,73),bool),np.array(['fixture']*12),dict(fixture=True))
    goal=tiny.future10_goal(np.array([0,1]))
    assert goal['goal'].shape==(2,10,73)
    assert np.array_equal(tiny.objective_error(tiny.target_bundle(np.array([0,1]))['packed73'],np.array([0,1])),np.zeros(2))
    rejected=False
    try:tiny.future10_goal(np.array([3]))
    except ValueError:rejected=True
    assert rejected,'future10 beyond explicit clip must reject, not silently flatten phase'
    put('OWN_CONVERSION_SOURCE_CPU_RESULT_ACTUAL.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source_CPU_passed=True,geometric_candidate_exported=candidate is not None,
        original_command_status=report['status'],original_command_rejections=report['rejection_reasons'],
        new_goal_status=newreport['status'],new_goal_rejections=newreport['rejection_reasons'],
        recorded_wheel_FK_max_error_m=max(wheel_error),recorded_wheel_checks=len(wheel_error),
        named_future10_goal_objective_target_consistency=True,future_goal_out_of_clip_rejected=True,
        source_contacts_not_own_contacts=True,dynamic_feasibility='pending',actual_SDK_admitted=False,
        no_actor_WM_physics_GPU_SSH_training_or_Git=True))
    print(json.dumps(dict(strict_status=report['status'],strict_rejections=report['rejection_reasons'],
        window=report['descending_clear_age_ranges'],inside=report['descending_clear_and_complete_inside_age_ranges'],
        required_vx=report['required_constant_vx_from_age100_min_m_s'],new_goal_status=newreport['status'],
        new_goal_rejections=newreport['rejection_reasons'],parameters={k:v for k,v in parameters.items() if k!='target_x_by_age'},
        wheel_FK_error=max(wheel_error))))
except BaseException:
    put('ORIGINAL_CONVERSION_SOURCE_CPU_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),old_files_untouched=True,no_model_or_physics_execution=True))
    raise
