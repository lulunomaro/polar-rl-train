"""New sidewall check/XY-only correction of existing table; never re-solves IK."""
from pathlib import Path
import sys,json,traceback,ast,hashlib,datetime
import numpy as np
from sidewall_forward_repair_v3 import wall_report,repair_delayed_approach
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent;V1=L/'agent_MOD4_step_reference_conversion_candidate_v1'
B=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2'
sys.path.insert(0,str(V1));sys.path.insert(0,str(B/'source'))
from mod4_step_reference_conversion_v1 import build_recorded_kinematics,wheel_bounds
from own_usd_closed_chain_ik_v1 import OwnUsdKinematics,transform
from supermimic_reference_adapter_v1 import quat_to_mat
def put(name,v):
    with (D/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
try:
    table=json.loads((D/'OWN_STEP_POSTCONTACT_IK_REFERENCE_TABLES_CANDIDATE_NOT_ADMITTED.json').read_bytes())
    states=np.asarray(table['packed73']);ages=np.asarray(table['ages']);mask=np.asarray(table['mask73']);metadata=table['metadata']
    kin=build_recorded_kinematics(json.loads((T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026/payloads/h1/job0/assets/import_contract.json').read_bytes()),
        json.loads((T/'full20k_native180_V3_actual/out/GEOMETRY_AND_CLOCK_ACTUAL.json').read_bytes()),OwnUsdKinematics,transform,quat_to_mat)
    original,_,_=wall_report(ages,states,kin,quat_to_mat,wheel_bounds)
    put('V2_ORIGINAL_WHOLE_PATH_SIDEWALL_CHECK_ACTUAL.json',original)
    corrected,repair=repair_delayed_approach(ages,states,kin,quat_to_mat,wheel_bounds)
    # Data correction: earlier field label incorrectly included all30 q, including unobserved spin.
    meta=dict(metadata);mislabel=meta.pop('entry_masked_motor_q_abs_max')
    touch=metadata['first_touch_age'];end=metadata['support_age']
    meta.update(entry_all_joint_abs_max=mislabel,
        entry_masked_joint_abs_max=float(abs(states[touch,13:43][mask[touch,13:43]]).max()),
        final_masked_joint_abs_max=float(abs(states[end,13:43][mask[end,13:43]]).max()),
        whole_path_sidewall_static_check=repair['repaired_report'] if repair['changed'] else original,
        delayed_approach_repair=repair,actual_contact_or_skill_success=False)
    assert np.array_equal(corrected[:,2:7],states[:,2:7])
    assert np.array_equal(corrected[:,9:73],states[:,9:73])
    assert np.array_equal(corrected[ages>=141,0],states[ages>=141,0])
    table['packed73']=corrected.tolist();table['metadata']=meta
    put('OWN_STEP_REFERENCE_TABLES_V3_SIDEWALL_REPAIRED_CANDIDATE_NOT_ADMITTED.json',table)
    # Only metadata expression in the IK module changed after the successful IK run.
    trees=[]
    for file in ('contact_splice_own_IK_v2_before_metadata_review.py','contact_splice_own_IK_v2.py'):
        tree=ast.parse((D/file).read_text('utf8'))
        for node in ast.walk(tree):
            if isinstance(node,ast.FunctionDef) and node.name=='generate_contact_splice':
                node.body=[s for s in node.body if not (isinstance(s,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='metadata' for t in s.targets))]
        trees.append(ast.dump(tree,include_attributes=False))
    assert trees[0]==trees[1]
    put('V3_EXISTING_TABLE_SIDEWALL_REPAIR_AND_METADATA_ERRATUM_CPU_ACTUAL.json',dict(UTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        passed=True,originalV2_sidewall_passed=original['passed'],repair=repair,
        metadata_erratum=dict(original_field='entry_masked_motor_q_abs_max',original_value=mislabel,meaning='all30 joint absolute max includes unobserved wheelspin',
            corrected_entry_masked_joint_abs_max=meta['entry_masked_joint_abs_max'],corrected_final_masked_joint_abs_max=meta['final_masked_joint_abs_max'],original_table_and_report_preserved=True),
        IK_source_AST_identical_except_metadata_assignment=True,no_IK_rerun=True,
        Z_R_q_Vz_omega_qd_tables_literal_unchanged=True,postarrival_X_literal_unchanged=True,
        actual_SDK_or_dynamic_contact_admitted=False))
    print(json.dumps(dict(original=original,repair=repair,metadata_masked_entry=meta['entry_masked_joint_abs_max'],metadata_masked_end=meta['final_masked_joint_abs_max'])))
except BaseException:
    put('V3_ORIGINAL_SIDEWALL_REPAIR_CPU_ERROR_ACTUAL.json',dict(error=traceback.format_exc(),V2_originals_preserved=True,no_IK_or_physics=True))
    raise
