"""Integrate frozen native continuation + V2 own-wheel head; source only, no payload."""
from pathlib import Path
import ast,hashlib,json,time,traceback,shutil
S=Path(__file__).resolve().parent;L=S.parent;R=S/'reports'
M=L/'native88_gas400_typed_native_migration_bridge_source_v1'
O=L/'native88_own_step_differentiable_objective_source_v1'
P=L/'native88_two_available_H1_runtime_protocol_source_v1'
def H(raw):return hashlib.sha256(raw).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def replace(text,a,b):
 assert text.count(a)==1,(a,text.count(a));return text.replace(a,b,1)
def write(name,raw):
 if name.endswith('.py'):ast.parse(raw)
 with (S/name).open('xb') as f:f.write(raw)
 return dict(path=name,bytes=len(raw),SHA=H(raw))
def funcs(raw):
 return {x.name:ast.dump(x,include_attributes=False) for x in ast.parse(raw).body if isinstance(x,(ast.FunctionDef,ast.ClassDef))}
def main():
 R.mkdir(exist_ok=True);put('SOURCE_INTEGRATION_CONSUMED_BEFORE_WRITE_ACTUAL.json',dict(epoch=time.time(),source_only=True))
 assert H((O/'SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_FINAL_ACTUAL.json').read_bytes())=='dc5a6f147309310acdb812848f509b03c41b0c44781c9c9281585cbf4edb5c89'
 raw=(M/'native_own_fudan88_gas400_training_v2.py').read_bytes();text=raw.decode('utf8')
 text=replace(text,'from converted_MOD4_jump_mdp_v4 import ConvertedMOD4Reference,ConvertedMOD4JumpMdp','from own_step_differentiable_objective_v2 import build_own_step_mdp,OwnStepDifferentiableMdpV2')
 text=replace(text,"    provider=ConvertedMOD4Reference(document,env.device).bind_named_order(names,scope='actual_SDK_readback')\n    encoder_names=actual_encoder_joint_names(env,names)\n    mdp=ConvertedMOD4JumpMdp(provider,encoder_names)",
 """    encoder_names=actual_encoder_joint_names(env,names)
    geometry_path=B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json'
    if H(geometry_path)!=task['own_step_geometry_SHA']:raise ValueError('own authored wheel geometry source pin differs')
    geometry=json.loads(geometry_path.read_bytes())
    if list(body)!=geometry['body_names']:raise ValueError('actual body-name mapping differs from own-wheel source geometry')
    capture=env._integrated_contact
    if list(capture.sensor.body_names)!=['left_wheel','right_wheel'] or tuple(capture.history.shape)!=(env.num_envs,3,2,3):
        raise ValueError('original contact18 named order/history layout differs')
    mdp=build_own_step_mdp(json.loads((J/'assets/import_contract.json').read_bytes()),geometry,document,names,encoder_names,device=env.device,order_scope='actual_SDK_readback')
    if type(mdp) is not OwnStepDifferentiableMdpV2:raise ValueError('selected bounded-positive own-wheel head V2 required')""")
 text=replace(text,"        actual_reference_SHA=task['native_reference_SHA'],","        actual_reference_SHA=task['native_reference_SHA'],\n        actual_selected_own_step_objective_class=type(mdp).__name__,actual_own_geometry_SHA=task['own_step_geometry_SHA'],\n        actual_contact_history_shape=list(capture.history.shape),actual_contact_wheel_order=list(capture.sensor.body_names),\n        contact_force_used_as_soft_magnitude_not_platform_face_truth=True,")
 text=replace(text,"        own_step_objective_qualification_SHA=task['own_step_objective_qualification_SHA'],","        own_step_objective_qualification_SHA=task['own_step_objective_qualification_SHA'],\n        own_step_geometry_SHA=task['own_step_geometry_SHA'],native_task_objective_changed_from_R5=True,")
 rows=[write('native_own_fudan88_gas400_training_v2.py',text.encode('utf8'))]
 # All top-level functions except the explicitly integrated run function remain AST exact.
 a=funcs(raw);b=funcs(text);assert {k for k in a if a[k]!=b[k]}=={'run'}
 rows.append(write('native_wheel_leg_bridge_v4.py',(M/'native_wheel_leg_bridge_v4.py').read_bytes()))
 migration=(M/'native88_gas400_migration_v1.py').read_text('utf8')
 migration=replace(migration,'original_clock_solver_geometry_reward_command_success_unchanged=True,','original_clock_solver_geometry_physical_V8_command_success_unchanged=True,native_task_objective_changed=True,')
 rows.append(write('native88_gas400_migration_v1.py',migration.encode('utf8')))
 # Preserve finalization lifecycle/error/atomic/fullsave functions exactly.
 for name in ('native_finalization_own88_gas400.py','same_architecture_native_continuation_candidate_v1.py','native88_typed_window_reviewer_v1.py','gas400_source_patcher_v1.py'):
  rows.append(write(name,(M/name).read_bytes()))
 rows.append(write('gas400_sdk_admission_candidate_v1.py',(P/'gas400_sdk_admission_candidate_v2.py').read_bytes()))
 for name in ('own_step_differentiable_geometry_v1.py','own_step_differentiable_objective_v1.py','own_step_differentiable_objective_v2.py'):
  rows.append(write(name,(O/name).read_bytes()))
 # Vendor directory is an explicit one-file replacement, not a whole new install.
 target=S/'vendor_candidate/supermimic_wheel_leg_v3/learner.py';target.parent.mkdir(parents=True)
 raw=(M/'vendor_candidate/supermimic_wheel_leg_v3/learner.py').read_bytes()
 with target.open('xb') as f:f.write(raw)
 rows.append(dict(path=target.relative_to(S).as_posix(),bytes=len(raw),SHA=H(raw)))
 put('FROZEN_OWN_STEP_V2_AND_NOMINAL400_NATIVE_INTEGRATION_SOURCE_ACTUAL.json',dict(epoch=time.time(),source_only=True,files=rows,only_entry_run_AST_changed=True,finalization_and_native_physical_bridge_bytes_exact=True,old_source_contract_separately_used_for_input_restore=True,new_output_native_contract_names_physical_V8_unchanged_and_native_task_changed=True,old_Warp_backend_assumption_replaced_by_original_parameter_tensor_view=True,actualUSD_CPU_report_SHA='9ee4e319f2b21d71d660ed061e1539ce41a580c40f1a412589c39926621d7569',own_objective_qualification_SHA='dc5a6f147309310acdb812848f509b03c41b0c44781c9c9281585cbf4edb5c89',actual_SDK_PhysX_resource_admission_and_training_pending=True,no_model_or_asset_or_remote_or_actor=True))
 print(json.dumps(dict(source_integrated=True,files=len(rows),actual_installed_or_GO=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(exist_ok=True);put('SOURCE_INTEGRATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_model_or_remote_or_Go=True));raise
