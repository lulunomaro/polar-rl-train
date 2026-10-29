"""Seal NEW target111 CPU candidates from qualified107 without model content I/O."""
from pathlib import Path
import ast,copy,hashlib,json,os,pprint,runpy,shutil,time,traceback
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
N=T/'MOD4_H1_FUDAN270_REWARD_COHERENCE_RESOURCE_V111_20261029';R=N/'reports'
A=T/'MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029/payloads_v2/seed27'
Q=L/'TWO107_FUDAN270_20S_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1';F=L/'native111_coherent_world_task_reward_source_v2'
helper=runpy.run_path(str(T/'MOD4_H1_FLAT20_NATIVE_RESOURCE_V100_20261028/prepare_target20_two_saved99_native_payloads_once.py'),run_name='definitions_only')
assign,rep=helper['assign'],helper['rep']
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,s):Path(p).write_text(s,encoding='utf8',newline='\n')
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False)
def main():
 assert not N.exists();R.mkdir(parents=True)
 assert read(F/'reports/NEW111_REWARD_GEOMETRY_HEADING_AND_SURVIVAL_CPU_ACTUAL_V1.json')['passed']
 prior=read(Q/'reports/NATIVE106_seed27_NEW_FORMAL_INITIAL_WHOLE_CPU_QUALIFIED_ACTUAL.json');assert prior['passed']
 assert read(Q/'reports/TWO107_INITIAL_TWO_FORMAL_CPU_QUALIFIED_ACTUAL.json')['passed']
 source=prior['model'];pub=source['original_producer'];progress=dict(updates=17272,world_updates=172720,policy_updates=16632)
 assert source['SHA']=='36059cd11b17097e82feb58fc48b259613bcf378376c4d219e20e2000baa21ef' and all(pub[k]==v for k,v in progress.items())
 local=Path(source['local_path']);assert local.stat().st_size==256234249 and source['twohost_complete_SHA'] and source['NEW_formal_transfer_count']==1
 base=runpy.run_path(str(A/'source/native106_fudan20s_pins_v1.py'),run_name='prior107_literal_pins')
 oldtask=read(A/'job0/TASK.json');manifest=read(A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');oldrows={r['relative']:r for r in manifest['files']}
 REF=H(F/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json');assert REF==pub['producer']['reference_artifact_SHA']
 modekind='continue_qualified107_coherent_world_task_reward111';kind='MOD4_NATIVE107_FUDAN270_TARGET111_COHERENT_REWARD_TYPED_SOURCE_CPU_V1';schema='mod4.native107_to_fudan270.target111.coherent_reward.v1';method='MOD4_fudan111_coherent_world_task_reward_from_qualified107'
 coherence=read(F/'SOURCE_DELTA_AND_BEFORE_USE_CONTRACT_111_V2.json')
 taskdomain=copy.deepcopy(oldtask['fudan_step_task']);taskdomain.update(schema='mod4.fudan111.own270.coherent_world_reward.v1',reward_coherence=dict(source_CPU_SHA=H(F/'reports/NEW111_REWARD_GEOMETRY_HEADING_AND_SURVIVAL_CPU_ACTUAL_V1.json'),reward_SHA=H(F/'mod4_fudan_contact_phase_reward_candidate_v2.py'),adapter_SHA=H(F/'native_fudan_step_adapter_candidate_v2.py'),reference_SHA=REF,heading_slot=3,heading_scale=.01,platform_XY=[[.35,-.6],[1.15,.6]],surface_height_reward='mixture_of_two_authored_plane_errors_not_an_interpolated_plane',max_step_reward=.16,soft_tilt_risk_horizon32=True,actual_physical_acceptance_unchanged=True))
 results={}
 for seed,slot,gpu in [(27,'h1','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'),(28,'h1_seed28','GPU-16828f91-2b45-b646-8dc0-9481138e2842')]:
  mode='seed'+str(seed);B=N/'payloads'/mode;B.mkdir(parents=True);nativefile='H1_native111_qualified107_input.pt'
  for row in manifest['files']:
   rel=row['relative']
   if rel=='job0/source/'+oldtask['source_filename']:continue
   s=A/rel;d=B/rel;d.parent.mkdir(parents=True,exist_ok=True)
   if s.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(s,d)
   else:shutil.copy2(s,d)
  os.link(local,B/'job0/source'/nativefile)
  for name in ('mod4_fudan_contact_phase_reward_candidate_v2.py','native_fudan_step_adapter_candidate_v2.py','OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json','reward111_installed_readback_cpu_v1.py'):shutil.copy2(F/name,B/'source'/name)
  shutil.copy2(F/'reports/NEW111_REWARD_GEOMETRY_HEADING_AND_SURVIVAL_CPU_ACTUAL_V1.json',B/'source/REWARD111_SOURCE_CPU_PROOF_ACTUAL.json')
  exposure=copy.deepcopy(oldtask['imagination_terminal_exposure']);exposure.update(schema='mod4.fudan111.terminal_exposure20s.coherent_risk.v1',selected_mdp_SHA=H(B/'source/native_fudan_step_adapter_candidate_v2.py'),soft_tilt_risk_controls=32,soft_height_012_removed_physical_lowbase_disabled=True)
  contract=copy.deepcopy(base['NATIVE_CONTRACT']);contract.update(input_start_mode=modekind,source_reference_artifact_SHA=pub['producer']['reference_artifact_SHA'],fudan_step_task=taskdomain,imagination_terminal_exposure=exposure)
  pins=copy.deepcopy(base['SOURCE_PINS']);pins.update(final=pub,native_contract=base['NATIVE_CONTRACT'],producer=pub['producer'],source_migration_window=pub['native88_migration_window'])
  flat=copy.deepcopy(base['FLAT_OBJECTIVE_CONTRACT']);flat.update(source_MDP_contract=dict(fudan_step_task=taskdomain))
  text='"""Qualified107 complete state into bounded task-coherence repair111; literals."""\n'
  for k,v in [('SOURCE_PINS',pins),('NATIVE_CONTRACT',contract),('FLAT_OBJECTIVE_SHA',REF),('FLAT_OBJECTIVE_CONTRACT',flat),('OUTPUT_GAS400_PARAMETER_CONTRACT_SHA',base['OUTPUT_GAS400_PARAMETER_CONTRACT_SHA']),('SOURCE_MODE',modekind)]:text+=k+'='+pprint.pformat(v,width=120,sort_dicts=False)+'\n'
  write(B/'source/native111_coherent_reward_pins_v1.py',text)
  shutil.copy2(A/'source/native88C_to_flat_migration_v1.py',B/'source/native107_prior_migration_validation_v1.py')
  mig=(A/'source/native88C_to_flat_migration_v1.py').read_text(encoding='utf8').replace('from native106_fudan20s_pins_v1 import','from native111_coherent_reward_pins_v1 import')
  mig=mig.replace('from native104_prior_migration_validation_v1 import verify_saved_migration','from native107_prior_migration_validation_v1 import verify_saved_migration')
  for k,v in [('SOURCE_SHA',source['SHA']),('SOURCE_REFERENCE_SHA',pub['producer']['reference_artifact_SHA']),('METHOD',method),('KIND',kind),('SOURCES',{'h1':dict(SHA=source['SHA'],**progress,seed=27)})]:mig=assign(mig,k,v)
  mig=mig.replace('mod4.native104_to_fudan270.target106.episode20.v1',schema);write(B/'source/native88C_to_flat_migration_v1.py',mig)
  entry=(A/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py').read_text(encoding='utf8')
  entry=rep(entry,"method='MOD4_fudan106_actual270_20s_from_qualified104'",'method='+repr(method))
  entry=rep(entry,"source_reference_artifact_SHA='6c251beda43dc36431df80f00e67bbbfd05c54e66f614e5db5650551a65d4274'",'source_reference_artifact_SHA='+repr(pub['producer']['reference_artifact_SHA']))
  write(B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py',entry)
  task=copy.deepcopy(oldtask);task.update(id='MOD4_H1_FUDAN270_REWARD_COHERENCE111_'+mode,logical_slot=slot,GPU_UUID=gpu,native_seed=seed,seed=seed,source_SHA=source['SHA'],source_filename=nativefile,source_progress=progress,source_native_iteration=progress['updates'],source_native_contract=pins['native_contract'],source_qualification_kind=kind,native_reference_SHA=REF,input_start_mode=modekind,fudan_step_task=taskdomain,imagination_terminal_exposure=exposure,own_step_objective_qualification_SHA=H(B/'source/REWARD111_SOURCE_CPU_PROOF_ACTUAL.json'))
  guard=(A/'native_flat90_source_guard_v1.py').read_text(encoding='utf8');guard=rep(guard,repr(oldtask['source_progress']),repr(progress));guard=rep(guard,"task.get('logical_slot')=='h1'","task.get('logical_slot')=="+repr(slot))
  if seed==28:guard=rep(guard,repr(oldtask['GPU_UUID']),repr(gpu))
  guard=guard.replace('mod4.native.fudan270.target106.episode20.complete_source.v1','mod4.native.fudan270.target111.coherent_reward.complete_source.v1')
  guard=rep(guard," value.update(source_native88C400_environment_not_restored=True,",''' tilt=env.termination_manager.get_term_cfg('bad_orientation');low=env.termination_manager.get_term_cfg('low_base')
 require(tilt.params['limit_angle']==.75 and low.params['minimum_height']==-1.,'actual physical guards for new source111 analytic head')
 value['actual111_termination_readback']=dict(bad_orientation_limit=.75,low_base_minimum=-1.,physical_cfg_unchanged=True)
 value.update(source_native88C400_environment_not_restored=True,''')
  write(B/'native_flat90_source_guard_v1.py',guard)
  cpu=(T/'MOD4_H1_FUDAN270_EPISODE20_RESOURCE_V106_20261029/payloads/seed27/target_native_flat90_source_sdk_CPU_once.py').read_text(encoding='utf8')
  cpu=cpu.replace('from native106_fudan20s_pins_v1 import','from native111_coherent_reward_pins_v1 import').replace('selected104source=1','selected107source=1')
  needle=" require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')"
  cpu=rep(cpu,needle," from reward111_installed_readback_cpu_v1 import check as reward111_check\n reward111=reward111_check(mdp,pi,critic,bank_state)\n put(J/'REWARD111_ACTUAL_INSTALLED_OWN_FK_INPUT_NORM_READBACK_CPU.json',reward111)\n"+needle)
  cpu=rep(cpu,'own_FK_reward_and_goal_source_CPU_passed=True,','reward111_actual_installed_readback=reward111,own_FK_reward_and_goal_source_CPU_passed=True,')
  write(B/'target_native_flat90_source_sdk_CPU_once.py',cpu)
  c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c.update(schema='mod4.native.fudan270.target111.coherent_reward.complete_source.v1',source_SHA=source['SHA'],input_start_mode=modekind,fudan_step_task=taskdomain)
  c['small_evidence_pins']['source/REWARD111_SOURCE_CPU_PROOF_ACTUAL.json']=H(B/'source/REWARD111_SOURCE_CPU_PROOF_ACTUAL.json')
  c['small_evidence_pins'][oldtask['native_reference_relative']]=REF
  c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
  write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2));task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
  rows=[]
  for p in sorted(B.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(B).as_posix()
   if rel=='job0/source/'+nativefile:r=dict(relative=rel,bytes=source['bytes'],SHA=source['SHA'])
   elif p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):r=oldrows[rel]
   else:r=dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
   assert p.stat().st_size==r['bytes'];rows.append(r)
  m=copy.deepcopy(manifest);m.update(source_SHA=source['SHA'],files=rows);write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2))
  for p in B.rglob('*.py'):ast.parse(p.read_bytes())
  results[mode]=dict(payload=str(B),task=task,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FUDAN270_REWARD_COHERENCE_2610v111/'+mode,GPU_UUID=gpu,logical_slot=slot,source=source,source_progress=progress,source_kind=kind,manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),reference_SHA=REF,source_CPU_pending=True,not_GO=True)
 put(R/'TWO111_SOURCE_PAYLOADS_PREPARED_NO_GO_ACTUAL.json',dict(passed=True,epoch=time.time(),payloads=results,models_decoded_or_rehashed=0,binary_hardlinks_only=True,actual_training=False,human_before_use_gate_still_pending_actual_target=True))
 print(json.dumps(dict(prepared=True,source107=source['SHA'],new_target111=True,no_model_decode_or_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(parents=True,exist_ok=True);put(R/('PREPARE111_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(traceback=traceback.format_exc(),no_remote_GPU_or_GO=True));raise
