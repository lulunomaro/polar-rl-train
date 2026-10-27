"""Derive UNUSED C/400N N1 code; no old entry/model/physics/fixture execution."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent;OLD=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027/code'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,text):
 ast.parse(text)
 with (D/name).open('x',encoding='utf8',newline='\n') as f:f.write(text)
def change(text,old,new):
 assert text.count(old)==1,old;return text.replace(old,new)
for name in ('native87R5_eval_environment_v1.py','native87R5_own_pid_out_guard_v1.py'):
 write(name.replace('native87R5','native88C'),(OLD/name).read_text('utf8').replace('native87R5','native88C'))
guard=(L/'native87R5_frozen_step_acceptance_preparation_v1/native87R5_readonly_authority72_guard_v1.py').read_text('utf8').replace('native87R5','native88C')
write('native88C_readonly_authority72_guard_v1.py',guard)
driver=(OLD/'native87R5_frozen_acceptance_driver_v1.py').read_text('utf8').replace('native87R5','native88C')
start=driver.index('CONTRACT=dict(');end=driver.index('\ndef literal(',start);driver=driver[:start]+driver[end+1:]
driver=change(driver,'def make_frozen_policy(checkpoint,policy_class,device):','def make_frozen_policy(checkpoint,policy_class,device,*,expected_native_contract):')
driver=change(driver,"literal(checkpoint['UniSuperMimic_test_contract'],CONTRACT)","literal(checkpoint['UniSuperMimic_test_contract'],expected_native_contract)")
driver=change(driver,"native=checkpoint['UniSuperMimic_H1_test'];cfg=native['args']","require(expected_native_contract['changed_plant700_to_nominal400'] is True and expected_native_contract['native_objective_changed'] is True and expected_native_contract['nominal_gas_stiffness_N_m']==2000.,'native88C/400N output recipe required')\n native=checkpoint['UniSuperMimic_H1_test'];cfg=native['args']")
driver=change(driver,"'only three predeclared seeds'","'only fixed single seed20260928'")
# Add metrics from the already captured original caches, without new queries.
driver=change(driver,' def state(self):',' def state(self):')
driver=change(driver,"  return dict(root13_sdk_xyzw=", "  caches={k:v[0].clone() for k,v in p.last_measured.items() if k in ('step_wheel_min','step_wheel_max','step_query_height','step_query_face','step_platform_contact','step_footprint_inside','step_first_cross_clear','step_stable_ticks','step_goal_success')}\n  root=t(r.data.root_state_w)[0];gravity=t(r.data.projected_gravity_b)[0].clone();metrics=dict(root_vx_world=root[7].clone(),tilt_rad=__import__('torch').acos((-gravity[2]).clamp(-1,1)),wheel_cache_available='step_wheel_min' in caches)\n  if 'step_wheel_min' in caches:\n   lo,hi=caches['step_wheel_min'],caches['step_wheel_max'];origin=e.scene.env_origins[0];edge=origin[0]+.35\n   metrics.update(wheel_bottom_above_floor_m=lo[:,2]-origin[2],wheel_front_edge_gap_m=edge-hi[:,0],wheel_rear_edge_gap_m=edge-lo[:,0],wheel_bottom_minus_platform_m=lo[:,2]-(origin[2]+.27))\n  return dict(metrics=metrics,projected_gravity_b=gravity,root13_sdk_xyzw=")
driver=change(driver,"actual_original_success_caches={k:v[0].clone() for k,v in p.last_measured.items() if k in ('step_wheel_min','step_wheel_max','step_query_height','step_query_face','step_platform_contact','step_footprint_inside','step_first_cross_clear','step_stable_ticks','step_goal_success')}","actual_original_success_caches=caches")
driver=change(driver,"     terminal=capture.last;last=terminal['state']", "     terminal=capture.last;last=terminal['state']\n     from static_dynamic_delay_contract_v1 import pack_dynamic_aux\n     aux=pack_dynamic_aux(last['contact_history18'][None],last['applied_torque30'][None],last['physical_applied_processed6'][None])\n     s1=bridge.pack(last['root13_sdk_xyzw'][None],last['q30'][None],last['qd30'][None],aux)\n     objective=bridge.mdp.objective_terms(unflatten_state(s1),age+1,last['executed6'][None],previous)\n     require(all(torch.isfinite(v).all() for v in objective.values()),'finite existing own-wheel V2 objective required')")
driver=change(driver,"terminal_pre_reset=terminal,actual_original_done=", "terminal_pre_reset=terminal,terminal_packed127_same_point=s1[0],actual_ownwheel_V2_objective=objective,actual_original_done=")
write('native88C_frozen_acceptance_driver_v1.py',driver)
entry=(OLD/'native87R5_frozen_single_sdk_entry_unused_once.py').read_text('utf8').replace('native87R5','native88C').replace('NATIVE87_SOURCE_CONTRACT_ACTUAL.json','NATIVE88_SOURCE_CONTRACT_ACTUAL.json')
entry=entry.replace('three predeclared fresh N1 frozen R5 native attempts','one fixed fresh N1 frozen qualified88C/400N attempt').replace('qualified R5','qualified88C').replace('OWN_E2_H1_KIND=\'FROZEN_NATIVE87R5_THREE_SEED_ACCEPTANCE\'','OWN_E2_H1_KIND=\'FROZEN_NATIVE88C_SINGLE_ATTEMPT\'')
entry=change(entry,'import argparse,hashlib,io,json,os,sys,time,traceback','import argparse,hashlib,io,json,os,sys,time,traceback,ast,importlib.util,importlib.metadata')
entry=change(entry," if q['execution_backend']=='target72':", " if q['execution_backend']=='target72':")
entry=change(entry,"['nvidia-smi','--query-compute-apps=gpu_uuid'", "['nvidia-smi','-i',q['GPU_UUID'],'--query-compute-apps=gpu_uuid'")
entry=change(entry," require(read(B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json')==q['runtime_source_contract'],'original R5 source contract changed')", " require(read(B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json')==q['runtime_source_contract'],'exact C training source contract changed')\n tree=ast.parse((B/'source/native88_gas400_migration_v1.py').read_bytes());node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='NATIVE_CONTRACT' for t in n.targets));scope={}\n exec(compile(ast.Module(body=[node],type_ignores=[]),'pinned_native_output_contract','exec'),scope)\n require(scope['NATIVE_CONTRACT']==q['native_output_contract'],'new native88 output contract source differs')")
entry=change(entry,"final=selected['source']['final'];require(final['SHA']==q['source_model']['SHA'] and final['bytes']==q['source_model']['bytes'],'formal qualified native model differs')", "final=selected['source']['final'];require(final['SHA']==q['source_model']['SHA'] and final['bytes']==q['source_model']['bytes'],'formal qualified native model differs')\n producer=final['producer']\n require(producer['initial_native_source']==q['native_parent_source'] and producer['bootstrap_task_source_SHA']=='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394','native R5 parent and normal86 witness distinct')\n require(producer['runtime_objective_contract_SHA']==q['objective_contract_SHA'] and producer['gas400_parameter_source_contract_SHA']==q['gas400_parameter_source_contract_SHA'] and producer['actual_gas400_asset_composition_report_SHA']==q['actual_gas400_asset_composition_report_SHA'],'typed native88C objective/gas recipe pins')")
entry=change(entry,"  from converted_MOD4_jump_mdp_v4 import ConvertedMOD4Reference,ConvertedMOD4JumpMdp", "  from own_step_differentiable_objective_v2 import build_own_step_mdp,OwnStepDifferentiableMdpV2\n  from gas400_sdk_admission_candidate_v1 import check_actual_new_gas\n  from gas400_reset_bank_exact_compatibility_v1 import check_runtime_source")
entry=change(entry,"  provider=ConvertedMOD4Reference(read(ref),env.device).bind_named_order(names,scope='actual_SDK_readback')\n  encoder=actual_encoder_joint_names(env,names);mdp=ConvertedMOD4JumpMdp(provider,encoder)", "  encoder=actual_encoder_joint_names(env,names);geo=contained(B,q['own_geometry_relative']);require(H(geo)==q['own_geometry_SHA'],'own C wheel geometry source')\n  mdp=build_own_step_mdp(read(J/'assets/import_contract.json'),read(geo),read(ref),names,encoder,device=env.device,order_scope='actual_SDK_readback')\n  require(type(mdp) is OwnStepDifferentiableMdpV2 and json.loads(json.dumps(mdp.contract_manifest()))==q['objective_contract'],'actual C own-wheel V2 semantics/order')\n  require(hashlib.sha256(json.dumps(mdp.contract_manifest(),indent=2).encode()).hexdigest()==q['objective_contract_SHA'],'actual unchanged objective contract SHA')\n  capture=env._integrated_contact;require(list(capture.sensor.body_names)==['left_wheel','right_wheel'] and tuple(capture.history.shape)==(1,3,2,3),'original named contact history18')\n  bank_source=check_runtime_source(J/'runtime/isaac/mod4');gas_actual=check_actual_new_gas(env,expected_joint_names=list(names),tensor=tensor,require_active_preload=False)\n  require(env._rescue_reset_bank[0].shape==(74,30) and env._rescue_reset_q.shape==(1,30),'actual original400N first reset cache/write path')")
entry=change(entry,"source4096_or20k_environment_state_not_restored=True))", "source4096_or20k_environment_state_not_restored=True,original_first_reset_completed=True,reset_bank_exact_compatibility_source_CPU=bank_source,actual_new400N_gas_readback=gas_actual,ownwheel_V2_objective=q['objective_contract']))")
entry=change(entry,"  require(publication['producer']['bootstrap_task_source_SHA']==q['runtime_source_contract']['source_SHA'] and publication['producer']['reference_artifact_SHA']==q['reference_SHA'],'formal native method/source/reference binding')", "  producer=publication['producer'];require(producer['bootstrap_task_source_SHA']=='0c1edb9603c1cb84fbb894d242dae1b6a7c87fe3237d658dbc486ccbbad3d394' and producer['initial_native_source']==q['native_parent_source'] and producer['reference_artifact_SHA']==q['reference_SHA'],'C model/native R5 parent/normal86 witness/reference binding')\n  require(producer['runtime_objective_contract_SHA']==q['objective_contract_SHA'] and producer['gas400_parameter_source_contract_SHA']==q['gas400_parameter_source_contract_SHA'] and producer['actual_gas400_asset_composition_report_SHA']==q['actual_gas400_asset_composition_report_SHA'],'C actual objective/400N source recipe')")
entry=change(entry,"  pi=make_frozen_policy(saved,Policy,env.device);del saved", "  pi=make_frozen_policy(saved,Policy,env.device,expected_native_contract=q['native_output_contract']);del saved")
entry=change(entry,"all_three_seed_aggregate_not_yet_claimed=True", "one_fixed_episode_only=True,not_skill_graduation=True")
# Fresh installed versions and math/RSL sources without model or scene creation.
anchor='class Authority:'
fresh='''def validate_installed_sources(q):
 c=q['runtime_source_contract'];sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)));rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)))
 versions={}
 for name in ('isaaclab','rsl-rl-lib','torch'):
  try:versions[name]=importlib.metadata.version(name)
  except importlib.metadata.PackageNotFoundError:versions[name]='not_registered_distribution'
 require(versions==c['expected_installed_versions'],'fresh installed SDK/RSL/torch versions')
 require(H(sdk/'utils/math.py')==c['expected_actual_SDK_math_SHA'],'fresh actual SDK math source')
 for row in c['expected_actual_RSL_sources']:
  path=contained(rsl,row['relative']);require(path.stat().st_size==row['bytes'] and H(path)==row['SHA'],'fresh actual RSL source')
 return dict(passed=True,versions=versions,no_scene_or_model_created=True)

'''
entry=change(entry,anchor,fresh+anchor)
entry=change(entry,"  import runpy\n  entry=", "  put(out,'FRESH_INSTALLED_SOURCE_BEFORE_APP_ACTUAL.json',validate_installed_sources(q))\n  import runpy\n  entry=")
write('native88C_frozen_single_sdk_entry_unused_once.py',entry)
rows=[dict(path=str(p),SHA=H(p),bytes=p.stat().st_size) for p in OLD.glob('*.py')]
checks=dict(environment_function_AST_exact=ast.dump(next(n for n in ast.parse((OLD/'native87R5_eval_environment_v1.py').read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='environment'))==ast.dump(next(n for n in ast.parse((D/'native88C_eval_environment_v1.py').read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='environment')),
 own_PID_guard_source_byteexact=(OLD/'native87R5_own_pid_out_guard_v1.py').read_bytes()==(D/'native88C_own_pid_out_guard_v1.py').read_bytes())
assert all(checks.values())
with (D/'SOURCE_DERIVATION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,source_files=rows,checks=checks,old_R2_entry_not_executed=True,
 typed_differences=['fixed h1 qualified88C model/seed20260928/one episode','new native88 output recipe and separate R5 parent/normal86 witness','actual400N/resetbank and own-wheel V2 MDP','metrics and same pre-reset terminal127 objective recording','selected UUID-only compute query','fresh SDK/math/RSL source/version check'],
 actual_model_SDK_GPU_or_physics_run=False),f,indent=2)
print(json.dumps(dict(passed=True,derived_unused_entry=True,checks=checks)))
