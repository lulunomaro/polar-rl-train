from pathlib import Path
import ast,copy,hashlib,json,os,pprint,runpy,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
A=T/'MOD4_H1_FLAT20_NATIVE_PRODUCER_FIX_RESOURCE_V101_20261028/payloads/seed27'
F=L/'H1_FUDAN_COMBINED_REWARD_ADAPTATION_SOURCE_V102_20261028'
helpers=runpy.run_path(str(T/'MOD4_H1_FLAT20_NATIVE_RESOURCE_V100_20261028/prepare_target20_two_saved99_native_payloads_once.py'),run_name='definitions_only')
rep=helpers['rep'];assign=helpers['assign'];replace_def=helpers['replace_def']
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def main():
 assert not (N/'payloads_v3').exists();(N/'payloads_v3').mkdir()
 closed=read(T/'MOD4_H1_FLAT20_NATIVE_PRODUCER_FIX_RESOURCE_V101_20261028/reports/CURRENT_CLOSED101_TWO_QUALIFIED_NATIVE20_FORMALS_FULL_EVENT_SCOPE_AND_COST_ACTUAL.json')
 assert closed['fully_closed'] and closed['strict_fullstate_method_qualification_passed'] and not closed['skill_graduation']
 row=closed['rows']['h1'];source=row['published'];pub=source['original_producer'];assert source['SHA']=='35e1657815fc972ed954d258fe62326074ebeb862e5bcfce7150b3ef58dc2b9f'
 progress=dict(updates=14784,world_updates=147840,policy_updates=14272)
 assert pub['updates']==progress['updates'] and pub['world_updates']==progress['world_updates'] and pub['policy_updates']==progress['policy_updates']
 source_local=L/'TWO101_CORRECT_NORMAL900_TWO_NATIVE20_COLLECTOR_SOURCE_V1/current_closed101_models/h1/formal/model_final.pt'
 oldtask=read(A/'job0/TASK.json');manifest=read(A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');previous={x['relative']:x for x in manifest['files']}
 base=runpy.run_path(str(A/'source/native100_target20_pins_v1.py'),run_name='literal100_pins_only')
 assert read(F/'reports/FUDAN102_NATIVE127_OWN_GEOMETRY_TERMINAL_GOAL_AND_GRADIENT_CPU_V3_ACTUAL.json')['passed_source_CPU_only']
 REF=H(F/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json');results={}
 for seed,slot,GPU in [(27,'h1','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'),(28,'h1_seed28','GPU-16828f91-2b45-b646-8dc0-9481138e2842')]:
  mode='seed'+str(seed);B=N/'payloads_v3'/mode;B.mkdir();nativefile='H1_native103_qualified101_input.pt'
  for r in manifest['files']:
   rel=r['relative']
   if rel=='job0/source/'+oldtask['source_filename']:continue
   src=A/rel;dst=B/rel;dst.parent.mkdir(parents=True,exist_ok=True)
   if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dst)
   else:shutil.copy2(src,dst)
  os.link(source_local,B/'job0/source'/nativefile)
  for name in ('native_fudan_step_adapter_candidate_v2.py','mod4_fudan_contact_phase_reward_candidate_v2.py','OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json'):
   shutil.copy2(F/name,B/'source'/name)
  for name in ('FUDAN102_INSTANTANEOUS_FORMULAS_MODES_AND_SYNTHETIC_GRADIENT_CPU_ACTUAL.json','FUDAN102_NATIVE127_OWN_GEOMETRY_TERMINAL_GOAL_AND_GRADIENT_CPU_V3_ACTUAL.json'):
   shutil.copy2(F/'reports'/name,B/'source'/name)
  shutil.copy2(N/'source_templates/native_fudan_step_bridge_v1.py',B/'source/native_fudan_step_bridge_v1.py')
  adapter=B/'source/native_fudan_step_adapter_candidate_v2.py';s=adapter.read_text('utf8')
  # Cache only the just-computed true native reward components. No extra FK,
  # actor call or RNG draw is introduced for logging.
  needle='    def soft_termination(self,state,frames):'
  s=rep(s,needle,"    def reward(self,state,frames,action,previous_action):\n        result=self.objective_terms(state,frames,action,previous_action)\n        if torch.is_inference_mode_enabled():self.last_reward_components=result\n        return result['total']\n"+needle)
  write(adapter,s)
  focus=B/'source/flat95_task_focused_starts_v1.py';s=focus.read_text('utf8')
  s=replace_def(s,'focused_mask',"""def focused_mask(frames):
    info=decode(frames);age=info['public_age']
    return info['valid_actual'] & (age>=180) & (age<500)
""")
  tree=ast.parse(s);x=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONTRACT' for t in x.targets));s=''.join(s.splitlines(keepends=True)[:x.lineno-1])+"CONTRACT=dict(schema='mod4.fudan103.actual_replay_prestep_to_recovery.v1',numerator=1,denominator=2,maximum_original_sampler_calls=8,actual_age_start=180,actual_age_end_exclusive=500,policy_hz=100,unchanged_physical_timeout_ticks=500,insufficient_focus='fill_with_original_valid_starts',generated_or_modified_transitions=False,original_sampler_RNG_draw_count_unchanged=False)\n"+''.join(s.splitlines(keepends=True)[x.end_lineno:]);write(focus,s)
  focus_assignment=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CONTRACT' for t in x.targets))
  focused=dict({kw.arg:ast.literal_eval(kw.value) for kw in focus_assignment.value.keywords},source_SHA=H(focus))
  modekind='continue_qualified101_fudan270';kind='MOD4_NATIVE101_FUDAN270_TARGET103_TYPED_SOURCE_CPU_V1';schema='mod4.native101_to_fudan270.target103.objective_window.v1';method='MOD4_fudan103_actual270_from_qualified101'
  taskdomain=dict(schema='mod4.fudan103.own270.jump_and_recovery.v1',upstream_commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c',request_age_ticks=200,request_end_exclusive=500,approach_speed_m_s=.5,terminal_root_x_m=.75,step_edge_x_m=.35,step_top_z_m=.27,landing_callbacks=12,stable_callbacks=200,stable_seconds=.5,contact_modes_refreshed_each_predicted_state=True,no_scripted_action_or_force_or_airborne_reset=True,original_exact270_physical_criterion_retained=True,flat20_course_superseded=True)
  contract=copy.deepcopy(base['NATIVE_CONTRACT'])
  for k in ('native_flat05_objective','target_both_wheel_clearance_m','stationary_horizontal_command','stance_reference_revision','flat_jump_target_m','source_flat_jump_target_m','user_authorized_height_change_5_to20'):contract.pop(k,None)
  contract.update(input_start_mode=modekind,reference_artifact_SHA=REF,source_reference_artifact_SHA=pub['producer']['reference_artifact_SHA'],native_fudan270_objective=True,fudan_step_task=taskdomain,task_focused_real_replay=focused,original_public_request_clock_unchanged=False,public_request_100_180_changed_to_200_500=True,original_physical_reset_RNG_unchanged=True)
  pins=copy.deepcopy(base['SOURCE_PINS']);pins.update(final=pub,native_contract=base['NATIVE_CONTRACT'],producer=pub['producer'],source_migration_window=pub['native88_migration_window'])
  flatcontract=dict(private_phase_frame_source_SHA=H(B/'source/private_phase_frame_v1.py'),real_callback_counter_source_SHA=H(B/'h1_step270_sdk_runtime_candidate.py'),source_MDP_contract=dict(fudan_step_task=taskdomain))
  text='"""Exact qualified101 complete state -> Fudan-inspired real270mm task. No model I/O."""\n'
  for name,value in [('SOURCE_PINS',pins),('NATIVE_CONTRACT',contract),('FLAT_OBJECTIVE_SHA',REF),('FLAT_OBJECTIVE_CONTRACT',flatcontract),('OUTPUT_GAS400_PARAMETER_CONTRACT_SHA',oldtask['gas400_parameter_source_contract_SHA']),('SOURCE_MODE',modekind)]:text+=name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'
  write(B/'source/native103_fudan270_pins_v1.py',text)
  mig=B/'source/native88C_to_flat_migration_v1.py';s=mig.read_text('utf8');write(B/'source/native101_prior_migration_validation_v1.py',s)
  s=rep(s,'from native100_target20_pins_v1 import','from native103_fudan270_pins_v1 import')
  for name,value in [('SOURCE_SHA',source['SHA']),('SOURCE_REFERENCE_SHA',pub['producer']['reference_artifact_SHA']),('METHOD',method),('KIND',kind),('SOURCES',{'h1':dict(SHA=source['SHA'],**progress,seed=27)})]:s=assign(s,name,value)
  s=s.replace('mod4.native99_to_flat20.target100.objective_window.v1',schema)
  s=rep(s,'from native99_prior_migration_validation_v1 import verify_saved_migration','from native101_prior_migration_validation_v1 import verify_saved_migration')
  s=replace_def(s,'assert_declared_admission',(N/'source_templates/assert_declared_admission.txt').read_text('utf8'))
  s=replace_def(s,'verify_saved_migration',(N/'source_templates/verify_saved_migration.txt').read_text('utf8'))
  write(mig,s)
  entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';s=entry.read_text('utf8')
  s=rep(s,'from native_flat_jump_bridge_v2_original_support import FlatWheelLegBridge as NativeWheelLegBridge, install_flat_real_counter, install_stationary_flat_command','from native_fudan_step_bridge_v1 import FudanStepBridge as NativeWheelLegBridge, install_fudan_step_request_and_command')
  s=rep(s,'from native_flat_jump_adapter_v1 import OwnFlatJumpReference,OwnFlatJumpMdp','from native_fudan_step_adapter_candidate_v2 import OwnFudanStepReference as OwnFlatJumpReference,OwnFudanStepMdp as OwnFlatJumpMdp')
  s=rep(s,'flat_command_admission=install_stationary_flat_command(env)\n    flat_counter,flat_floor_basis=install_flat_real_counter(env,height_m=provider.phase.height_m)','flat_command_admission=install_fudan_step_request_and_command(env)')
  s=s.replace('flat_real_physics_events=flat_counter.snapshot(),flat_floor_support_basis=flat_floor_basis,','fudan_real_reward_tracking=bridge.reward_tracking_snapshot(),')
  s=s.replace('flat_real_physics_events=flat_counter.snapshot(),','fudan_real_reward_tracking=bridge.reward_tracking_snapshot(),')
  s=s.replace("actual_flat_command=flat_command_admission,actual_flat_floor_basis=flat_floor_basis,","actual_fudan_step_command=flat_command_admission,")
  s=rep(s,'actual_flat_counter_height_m=flat_counter.height_m,flat_goal_height_m=provider.phase.height_m,flat_counter_installed_before_first_control=True,private_flat_frame_encoded_in_bridge=True,','actual_step_top_z_m=.27,original_exact270_counter_preserved=True,private_task_age_encoded_in_bridge=True,')
  s=s.replace('own_MOD4_native_flat20cm_same_nominal400','own_MOD4_native_fudan270_same_nominal400').replace('original_Isaac_MOD4_own_flat20cm_native_v1','original_Isaac_MOD4_own_fudan270_native_v1')
  s=rep(s,"method='MOD4_flat100_target20_from_qualified99'",'method='+repr(method))
  s=rep(s,"source_reference_artifact_SHA='8050fd4a0accd8b329fedd1570a2dc525a97e96fb3a6b17a5b5f25733c2a6d0d'",'source_reference_artifact_SHA='+repr(pub['producer']['reference_artifact_SHA']))
  s=rep(s,"input_start_mode=task['input_start_mode'],stance_reference_revision=task['stance_reference_revision'],flat_jump_target_m=task['flat_jump_target_m'],","input_start_mode=task['input_start_mode'],fudan_step_task=task['fudan_step_task'],")
  s=rep(s,"real_callback_counter_source_SHA='51db83fb9e75427bd0f28f7c5d7d2a31700fdb030eb672b002223d95068cbb8a'",'real_callback_counter_source_SHA='+repr(flatcontract['real_callback_counter_source_SHA']))
  s=rep(s,',flat_floor_support_basis=flat_floor_basis','')
  # Old phase-coverage helper decodes the obsolete parabolic20cm phase.
  s=rep(s,"    from flat_policy_phase_coverage_v1 import attach_optional_policy_phase_coverage\n    bridge.phase_sampling_diagnostic=attach_optional_policy_phase_coverage(learner,out/'NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json')\n",'')
  assert 'flat_counter' not in s and 'provider.phase' not in s;write(entry,s)
  guard=B/'native_flat90_source_guard_v1.py';s=guard.read_text('utf8')
  s=rep(s,'mod4.native.flat20.target100.complete_source.v1','mod4.native.fudan270.target103.complete_source.v1')
  s=rep(s,"require(task['flat_jump_target_m']==.20 and task['user_authorized_height_change_5_to20'],'explicit user20cm target')","require(task['fudan_step_task']==c['fudan_step_task'] and task['fudan_step_task']['step_top_z_m']==.27,'explicit Fudan-inspired actual270 task')")
  s=rep(s,repr(dict(updates=13429,world_updates=134290,policy_updates=12981)),repr(progress));s=rep(s,"task.get('logical_slot')=='h1'","task.get('logical_slot')=="+repr(slot));s=s.replace('GPU-c27eecbd-6838-7290-1cd2-37e34522213d',GPU);write(guard,s)
  task=copy.deepcopy(oldtask)
  for k in ('stance_reference_revision','flat_jump_target_m','user_authorized_height_change_5_to20','source101_metadata_only_producer_reference_fix'):task.pop(k,None)
  task.update(id='MOD4_H1_FUDAN270_NATIVE103_'+mode,logical_slot=slot,GPU_UUID=GPU,source_SHA=source['SHA'],source_filename=nativefile,source_progress=progress,source_native_iteration=progress['updates'],source_native_contract=pins['native_contract'],source_qualification_kind=kind,native_reference_relative='source/OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json',native_reference_SHA=REF,native_seed=seed,native_learning_seed=27,input_start_mode=modekind,fudan_step_task=taskdomain,task_focused_real_replay=focused)
  cpu=(T/'MOD4_H1_FLAT20_NATIVE_RESOURCE_V100_20261028/payloads/seed27/target_native_flat90_source_sdk_CPU_once.py').read_text('utf8')
  start=cpu.index(' from native_flat_jump_adapter_v1 import');end=cpu.index(" require(not torch.cuda.is_initialized()",start)
  cpu=cpu[:start]+(N/'source_templates/target_fudan_CPU_body.txt').read_text('utf8')+cpu[end:]
  cpu=rep(cpu,"flat_objective=True,","fudan270_objective=True,")
  start=cpu.index("  flat_jump_target_m=task['flat_jump_target_m']");end=cpu.index("source_model_environment_RNG_not_restored=True",start)
  cpu=cpu[:start]+"  physical_initial_seed=task['native_seed'],fudan_step_task=task['fudan_step_task'],own_FK_reward_and_goal_source_CPU_passed=True,task_focused_replay_source_CPU_passed=True,task_focused_real_replay=task['task_focused_real_replay'],native_learning_seed=27,source_native_args_exact=True,initial_loads=dict(selected101source=1,normal86=1),"+cpu[end:]
  write(B/'target_native_flat90_source_sdk_CPU_once.py',cpu)
  c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c.update(schema='mod4.native.fudan270.target103.complete_source.v1',source_SHA=source['SHA'],input_start_mode=modekind,fudan_step_task=taskdomain,task_focused_real_replay=focused)
  for k in ('stance_reference_revision','flat_jump_target_m','user_authorized_height_change_5_to20','source101_metadata_only_producer_fix'):c.pop(k,None)
  for rel in ('source/OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json',):c['small_evidence_pins'][rel]=H(B/rel)
  c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
  for rel,SHA in c['protected_current88C_files'].items():assert H(B/rel)==SHA,rel
  write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2));task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
  rows=[]
  for p in sorted(B.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(B).as_posix()
   if rel=='job0/source/'+nativefile:r=dict(relative=rel,bytes=source['bytes'],SHA=source['SHA'])
   elif p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):r=previous[rel]
   else:r=dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
   assert p.stat().st_size==r['bytes'];rows.append(r)
  m=copy.deepcopy(manifest);m.update(source_SHA=source['SHA'],files=rows);write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2))
  for p in B.rglob('*.py'):ast.parse(p.read_bytes())
  results[mode]=dict(task=task,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FUDAN270_NATIVE_2610v103/'+mode,GPU_UUID=GPU,logical_slot=slot,source=dict(source,local_path=str(source_local)),source_progress=progress,source_kind=kind,payload=str(B),manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),reference_SHA=REF,source_CPU_pending=True,not_GO=True)
 with (R/'TWO103_FUDAN270_PAYLOADS_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,epoch=time.time(),payloads=results,no_models_decoded_or_rehashed=True,actual_training=False),f,indent=2)
 print(json.dumps(dict(prepared=True,new_actual270_task=True,no_GPU_or_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/('SOURCE103_PREPARER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_GPU_or_remote=True),f,indent=2)
  raise
