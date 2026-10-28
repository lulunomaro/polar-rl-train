"""Two concrete source99 payloads, no model decode or remote execution."""
from pathlib import Path
import ast,copy,hashlib,json,os,pprint,runpy,shutil,time
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';O=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V97_20261028';F=L/'H1_99_STANCE_GOAL_AND_CLEAN_START_SOURCE_V1';N=T/'MOD4_H1_FLAT05_STANCE_START_COMPARE_RESOURCE_V99_20261028'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def put(p,x):
 with p.open('x',encoding='utf8') as f:json.dump(x,f,indent=2,allow_nan=False)
def rep(s,a,b,count=1):
 assert s.count(a)==count,(a,s.count(a),count);return s.replace(a,b)
def replace_def(s,name,new):
 node=next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name==name);lines=s.splitlines(keepends=True);return ''.join(lines[:node.lineno-1])+new.rstrip()+'\n'+''.join(lines[node.end_lineno:])
def typed_like(value,template):
 if isinstance(template,tuple):return tuple(typed_like(x,t) for x,t in zip(value,template))
 if isinstance(template,dict):return {k:typed_like(value[k],t) for k,t in template.items()}
 return value
def main():
 assert not N.exists();N.mkdir();R=N/'reports';R.mkdir();(N/'payloads').mkdir()
 evidence=read(F/'reference_candidate_v1/STANCE99_REFERENCE_SOURCE_CPU_ACTUAL.json');early=read(F/'reports/EARLIEST_NATIVE0_TYPED_INITIAL_RESTART_SOURCE_CPU_ACTUAL.json');closed=read(L/'TWO97_correct_normal900_dual_native_PPO_collector_source_v1/reports/TWO97_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json');assert evidence['passed'] and early['passed'] and closed['canonical_None']
 base=runpy.run_path(str(O/'payload/source/native93_focused95_pins_v1.py'),run_name='pins_definitions_only');oldtask=read(O/'payload/job0/TASK.json');manifest=read(O/'payload/THREE_SLOT_COMPLETE_MANIFEST_V1.json');previous={r['relative']:r for r in manifest['files']};current=closed['published']['h1'];earlyproof=early['model'];reference=F/'reference_candidate_v1/OWN_FLAT5CM_STANCE99_REFERENCE_SOURCE.json';REF=H(reference);parameter=oldtask['gas400_parameter_source_contract_SHA'];results={}
 for mode,slot,GPU,source,progress in [
  ('continue97','h1','GPU-c27eecbd-6838-7290-1cd2-37e34522213d',current,dict(updates=12066,world_updates=120660,policy_updates=11682)),
  ('restart0','restart','GPU-16828f91-2b45-b646-8dc0-9481138e2842',dict(path=earlyproof['original_producer']['path'],local_path=earlyproof['local_path'],bytes=earlyproof['bytes'],SHA=earlyproof['SHA']),dict(updates=0,world_updates=0,policy_updates=0))]:
  B=N/'payloads'/mode;B.mkdir();SHA=source['SHA'];plant_changed=mode=='restart0';kind='MOD4_NATIVE99_'+mode.upper()+'_GROUNDED_STANCE_SOURCE_CPU_V1';method='MOD4_flat99_grounded_stance_'+mode;schema='mod4.native99.stance_'+mode+'.objective_window.v1';nativefile='H1_native99_'+mode+'_input.pt';job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_STANCE_START_COMPARE_2610v99/'+mode
  for row in manifest['files']:
   rel=row['relative']
   if rel=='job0/source/'+oldtask['source_filename']:continue
   src=O/'payload'/rel;dest=B/rel;dest.parent.mkdir(parents=True,exist_ok=True)
   if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dest)
   else:shutil.copy2(src,dest)
  os.link(source['local_path'],B/'job0/source'/nativefile);shutil.copy2(reference,B/'source/OWN_FLAT5CM_TASK_REFERENCE_SOURCE.json')
  pins=copy.deepcopy(base['SOURCE_PINS'])
  if mode=='continue97':
   pub=current['original_producer'];source_contract=copy.deepcopy(base['NATIVE_CONTRACT']);pins.update(final=pub,native_contract=source_contract,producer=pub['producer'],source_migration_window=pub['native88_migration_window'])
  else:
   observed=early['source_pins'];pub=observed['publication'];pub['producer']=observed['producer'];source_contract=observed['native_contract'];pins.update(final=pub,native_contract=source_contract,producer=observed['producer'],source_migration_window=None,native_args=typed_like(observed['native_args'],base['SOURCE_PINS']['native_args']))
  source_ref=pins['producer']['reference_artifact_SHA'];stance=dict(schema='mod4.flat99.stance_reference.v1',reference_SHA=REF,source_CPU_SHA=H(F/'reference_candidate_v1/STANCE99_REFERENCE_SOURCE_CPU_ACTUAL.json'),standing_body_height_m=evidence['new_body_cue_range_m'][0],target_wheel_clearance_m=.05,unmeasured_joint_trajectory_still_masked=True)
  contract=copy.deepcopy(base['NATIVE_CONTRACT']);contract.update(stance_reference_revision=stance,input_start_mode=mode,source_checkpoint_before_any_native_update=plant_changed,changed_plant700_to_nominal400=plant_changed,plant_nominal400_unchanged=not plant_changed)
  flatcontract=copy.deepcopy(base['FLAT_OBJECTIVE_CONTRACT']);flatcontract['stance_reference_revision']=stance
  text='"""Exact99 source pins; two start modes remain distinct typed payloads."""\n'
  for name,value in [('SOURCE_PINS',pins),('NATIVE_CONTRACT',contract),('FLAT_OBJECTIVE_SHA',REF),('FLAT_OBJECTIVE_CONTRACT',flatcontract),('OUTPUT_GAS400_PARAMETER_CONTRACT_SHA',parameter),('SOURCE_MODE',mode)]:text+=name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'
  write(B/'source/native99_stance_pins_v1.py',text)
  oldmig=(B/'source/native88C_to_flat_migration_v1.py').read_text('utf8');write(B/'source/native97_prior_migration_validation_v1.py',oldmig)
  s=rep(oldmig,'SOURCE_PINS,NATIVE_CONTRACT,FLAT_OBJECTIVE_SHA,FLAT_OBJECTIVE_CONTRACT)','SOURCE_PINS,NATIVE_CONTRACT,FLAT_OBJECTIVE_SHA,FLAT_OBJECTIVE_CONTRACT,OUTPUT_GAS400_PARAMETER_CONTRACT_SHA,SOURCE_MODE)')
  s=rep(s,'from native93_focused95_pins_v1 import','from native99_stance_pins_v1 import');s=s.replace('b008fc03d5de3e39217101523c7e8fc0ddebf5cd6e63699582b61053171d165e',SHA).replace("SOURCE_REFERENCE_SHA='b4d801a47b92a0d63378df0cea15e8c736fe489c2fd37a63399a1a2ed3d00502'","SOURCE_REFERENCE_SHA="+repr(source_ref)).replace('MOD4_own_flat5cm_task_focused95_native400_continuation',method).replace('MOD4_NATIVE93_H1_TASK_FOCUSED95_TYPED_SOURCE_CPU_V1',kind).replace('mod4.native93_to_flat05_focused95.objective_window.v1',schema).replace('updates=10692,world_updates=106920,policy_updates=10372','updates='+str(progress['updates'])+',world_updates='+str(progress['world_updates'])+',policy_updates='+str(progress['policy_updates']))
  s=s.replace("SOURCE_PINS['producer']['gas400_parameter_source_contract_SHA']",'OUTPUT_GAS400_PARAMETER_CONTRACT_SHA')
  validator='''def validate_source(full,expected_source_contract,expected_args,expected_progress,expected_reference_SHA):
 require(exact_plain(expected_source_contract,SOURCE_PINS['native_contract']),'exact selected99 input native contract')
 require(exact_plain(expected_args,SOURCE_PINS['native_args']),'exact selected99 input architecture/config')
 require(exact_plain(expected_progress,{k:SOURCES['h1'][k] for k in ('updates','world_updates','policy_updates')}),'exact selected99 source progress')
 require(expected_reference_SHA==SOURCE_REFERENCE_SHA,'selected99 source reference')
 native=full['UniSuperMimic_H1_test'];pub=full['UniSuperMimic_publication']
 require(exact_plain(full['UniSuperMimic_test_contract'],SOURCE_PINS['native_contract']) and exact_plain(pub['producer'],SOURCE_PINS['producer']),'selected99 source contract/producer literal')
 require(exact_plain(native['args'],expected_args),'selected99 saved arguments literal')
 require(native['iteration']==pub['native_iteration']==SOURCES['h1']['updates'] and pub['world_updates']==SOURCES['h1']['world_updates'] and pub['policy_updates']==SOURCES['h1']['policy_updates'],'selected99 source counters')
 if SOURCE_MODE=='continue97':
  from native97_prior_migration_validation_v1 import verify_saved_migration as verify_prior
  verify_prior(full,pub)
  require(exact_plain(pub['native88_migration_window'],SOURCE_PINS['source_migration_window']),'qualified97 source window literal')
 for name,steps,count,betas in [('opt_wm',SOURCES['h1']['world_updates'],14,(.9,.999)),('opt_pi',SOURCES['h1']['policy_updates'],20,(.9,.95)),('opt_v',20*SOURCES['h1']['policy_updates'],6,(.9,.999))]:
  opt=native[name];require(len(opt['param_groups'])==1 and all(tuple(x['betas'])==betas for x in opt['param_groups']),'selected99 optimizer groups/betas '+name)
  if SOURCE_MODE=='restart0':require(steps==0 and opt['state']=={},'only protected0 source admits empty native optimizer '+name)
  else:require(len(opt['state'])==count and {int(x['step']) for x in opt['state'].values()}=={steps},'qualified97 native optimizer '+name)
 require(len(full['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in full['optimizer_state_dict']['state'].values()}=={832460},'separate literal frozen normal86 witness')
 return native,pub
'''
  s=replace_def(s,'validate_source',validator)
  s=rep(s,"source=validate_role_source(key,task['source_SHA'],task['source_progress'])","source=validate_role_source(key,task['source_SHA'],task['source_progress'])\n require(task['input_start_mode']==go['input_start_mode']==SOURCE_MODE and task['stance_reference_revision']==go['stance_reference_revision']==NATIVE_CONTRACT['stance_reference_revision'],'exact source99 mode/stance Task GO')")
  s=rep(s,"p=expected['producer'];require", "p=expected['producer'];require(p['input_start_mode']==SOURCE_MODE and p['stance_reference_revision']==NATIVE_CONTRACT['stance_reference_revision'],'source99 producer start mode and stance')\n require")
  if plant_changed:
   s=rep(s,"task['changed_plant700_to_nominal400'] is False and go['changed_plant700_to_nominal400'] is False","task['changed_plant700_to_nominal400'] is True and go['changed_plant700_to_nominal400'] is True")
   s=s.replace('plant_nominal400_unchanged=True','plant_nominal400_unchanged=False').replace('new_700_to400_migration=False','new_700_to400_migration=True').replace('changed_plant=False','changed_plant=True').replace('changed_plant700_to_nominal400=False','changed_plant700_to_nominal400=True')
   s=rep(s,"w['plant_nominal400_unchanged'] is True and w['changed_plant700_to_nominal400'] is False","w['plant_nominal400_unchanged'] is False and w['changed_plant700_to_nominal400'] is True")
   s=rep(s,"p['plant_nominal400_unchanged'] is True","p['plant_nominal400_unchanged'] is False")
  write(B/'source/native88C_to_flat_migration_v1.py',s)
  task=copy.deepcopy(oldtask);task.update(id='MOD4_H1_STANCE99_'+mode,key='h1',logical_slot=slot,canonical_worker_key='h1',GPU_UUID=GPU,source_SHA=SHA,source_filename=nativefile,source_progress=progress,source_native_iteration=progress['updates'],source_native_contract=source_contract,source_qualification_kind=kind,native_reference_SHA=REF,input_start_mode=mode,stance_reference_revision=stance,changed_plant700_to_nominal400=plant_changed,native_seed=27,native_learning_seed=27)
  entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';s=entry.read_text('utf8').replace('MOD4_own_flat5cm_task_focused95_native400_continuation',method).replace("source_reference_artifact_SHA='b4d801a47b92a0d63378df0cea15e8c736fe489c2fd37a63399a1a2ed3d00502'","source_reference_artifact_SHA="+repr(source_ref))
  s=rep(s,"plant_nominal400_unchanged=True,","plant_nominal400_unchanged="+repr(not plant_changed)+",\n        input_start_mode=task['input_start_mode'],stance_reference_revision=task['stance_reference_revision'],")
  write(entry,s)
  g=B/'native_flat90_source_guard_v1.py';s=g.read_text('utf8').replace('dict(updates=10692,world_updates=106920,policy_updates=10372)',repr(progress)).replace('mod4.native.flat05.focused95.complete_source.v1','mod4.native.flat05.stance99.'+mode+'.complete_source.v1').replace('GPU-c27eecbd-6838-7290-1cd2-37e34522213d',GPU)
  s=rep(s,"task.get('logical_slot')=='h1'","task.get('logical_slot')=="+repr(slot))
  s=rep(s,"task['changed_plant700_to_nominal400'] is False","task['changed_plant700_to_nominal400'] is "+repr(plant_changed))
  write(g,s)
  cpu=B/'target_native_flat90_source_sdk_CPU_once.py';s=cpu.read_text('utf8').replace('initial_loads=dict(native93=1,normal86=1)','initial_loads=dict(selected99source=1,normal86=1)')
  proof="""from native99_stance_pins_v1 import NATIVE_CONTRACT,SOURCE_MODE
 require(task['input_start_mode']==SOURCE_MODE and task['stance_reference_revision']==NATIVE_CONTRACT['stance_reference_revision'],'exact99 stance/mode source')
 require(doc['neutral_packed73'][2]==task['stance_reference_revision']['standing_body_height_m'],'new grounded stance body cue')
 require(doc['metadata']['height_m']==.05 and doc['metadata']['joint_trajectory_unmeasured_and_masked'],'same real5cm task/no invented joint path')
 """
  s=rep(s,"require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')",proof+"require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')")
  s=rep(s,'diagnostic_receipt_IO_source_CPU_passed=True,',"stance_reference_source_CPU_passed=True,input_start_mode=task['input_start_mode'],stance_reference_revision=task['stance_reference_revision'],diagnostic_receipt_IO_source_CPU_passed=True,")
  if plant_changed:
   helper='''from native88_installed_cpu_helpers_v1 import validate_native_optimizer as old_validate
def validate(module,state,betas):
 from native99_stance_pins_v1 import SOURCE_MODE
 assert SOURCE_MODE=='restart0' and state['state']=={} and len(state['param_groups'])==1
 g=state['param_groups'][0];assert tuple(g['betas'])==tuple(betas) and g['params']==list(range(len(list(module.parameters()))))
 return dict(min_step=0,max_step=0,initial_empty_native_optimizer=True,parameter_count=len(list(module.parameters())))
''';write(B/'source/native99_protected0_optimizer_CPU_v1.py',helper)
   s=rep(s,"modules[name]=validate_native_optimizer(module,native[opt],betas)","from native99_protected0_optimizer_CPU_v1 import validate\n  modules[name]=validate(module,native[opt],betas)")
  write(cpu,s)
  c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c.update(schema='mod4.native.flat05.stance99.'+mode+'.complete_source.v1',source_SHA=SHA,input_start_mode=mode,stance_reference_revision=stance)
  for key,value in list(c['small_evidence_pins'].items()):
   if key==oldtask['native_reference_relative']:c['small_evidence_pins'][key]=REF
  c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
  write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2));task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
  rows=[]
  for p in sorted(B.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(B).as_posix()
   if rel=='job0/source/'+nativefile:row=dict(relative=rel,bytes=source['bytes'],SHA=SHA)
   elif p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):row=previous[rel]
   else:row=dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
   assert p.stat().st_size==row['bytes'];rows.append(row)
  m=copy.deepcopy(manifest);m.update(source_SHA=SHA,files=rows);write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2))
  for p in B.rglob('*.py'):ast.parse(p.read_bytes())
  results[mode]=dict(task=task,job_root=job,GPU_UUID=GPU,logical_slot=slot,source=source,source_progress=progress,source_kind=kind,payload=str(B),manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),reference_SHA=REF,source_CPU_pending=True,not_GO=True)
 put(R/'TWO99_EXACT_START_PAYLOADS_PREPARED_ACTUAL.json',dict(passed=True,epoch=time.time(),payloads=results,reference_proof=evidence,same_goal_reward_plant_clock_actions_and_physical_seed=True,checkpoint_optimizer_normalizer_and_global_scheduler_history_intentionally_differ=True,not_an_actor_only_causal_memory_test=True,no_saved_model_decode_rehash_GPU_SDK_or_remote=True,actual_source_CPU_controller_firstupdate_and_final_pending=True))
 print(json.dumps(dict(prepared=True,reference_SHA=REF,source_modes={k:v['source_progress'] for k,v in results.items()},actual_CPU_pending=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  p=N/'reports/SOURCE99_PREPARER_ORIGINAL_ERROR_ACTUAL.json'
  if p.parent.is_dir():put(p,dict(epoch=time.time(),error=__import__('traceback').format_exc(),no_remote_or_model_decode=True))
  raise
