from pathlib import Path
import ast,copy,hashlib,json,os,pprint,runpy,shutil,time,traceback,math
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';O=T/'MOD4_H1_FLAT05_STANCE_START_COMPARE_RESOURCE_V99_20261028';A=O/'payloads/continue97';R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def rep(s,a,b,count=1):
 assert s.count(a)==count,(a,s.count(a),count);return s.replace(a,b)
def replace_def(s,name,new):
 x=next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name==name);lines=s.splitlines(keepends=True);return ''.join(lines[:x.lineno-1])+new.rstrip()+'\n'+''.join(lines[x.end_lineno:])
def assign(s,name,value):
 x=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets));lines=s.splitlines(keepends=True);return ''.join(lines[:x.lineno-1])+name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'+''.join(lines[x.end_lineno:])
def main():
 assert not (N/'payloads').exists();(N/'payloads').mkdir();(N/'source_reference').mkdir()
 closed=read(O/'reports/CURRENT_CLOSED99_TWO_QUALIFIED_FORMALS_REAL_TAKEOFF_COMPARISON_ACTUAL.json');assert closed['passed_initial_two_native_formal_CPU'] and closed['allout_CNone_original_locks_and_raw_cost_passed']
 source=closed['results']['h1']['model'];progress=dict(updates=13429,world_updates=134290,policy_updates=12981);assert source['SHA']=='da60dd1e671e27476dc6f239b6b7aa5d647f8862edc3426fb4d4681e5ebad36c'
 oldtask=read(A/'job0/TASK.json');manifest=read(A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');previous={x['relative']:x for x in manifest['files']};base=runpy.run_path(str(A/'source/native99_stance_pins_v1.py'),run_name='old99_pins_definitions_only')
 doc=read(A/oldtask['native_reference_relative']);assert doc['metadata']['height_m']==.05 and doc['neutral_packed73'][2]==.3824462629854679
 doc['metadata'].update(height_m=.20,wheel_lowest_point_actual_acceptance_m=.20,user_authorized_target_change='2026-10-28 explicit20cm trial; old5cm not graduated',nominal_ballistic_flight_s=2*math.sqrt(2*9.81*.20)/9.81)
 reference=N/'source_reference/OWN_FLAT20_FROM_99_GROUNDED_STANCE_REFERENCE_SOURCE.json';write(reference,json.dumps(doc,indent=2));REF=H(reference);results={}
 for seed,slot,GPU in [(27,'h1','GPU-c27eecbd-6838-7290-1cd2-37e34522213d'),(28,'h1_seed28','GPU-16828f91-2b45-b646-8dc0-9481138e2842')]:
  mode='seed'+str(seed);B=N/'payloads'/mode;B.mkdir();nativefile='H1_native100_qualified99_warm_input.pt';job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT20_NATIVE_2610v100/'+mode
  for row in manifest['files']:
   rel=row['relative']
   if rel=='job0/source/'+oldtask['source_filename']:continue
   src=A/rel;dest=B/rel;dest.parent.mkdir(parents=True,exist_ok=True)
   if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dest)
   else:shutil.copy2(src,dest)
  os.link(source['local_path'],B/'job0/source'/nativefile);shutil.copy2(reference,B/oldtask['native_reference_relative'])
  focus=B/'source/flat95_task_focused_starts_v1.py';s=focus.read_text();s=rep(s,'preparation_ticks=20, height_m=.05','preparation_ticks=20, height_m=.20');s=rep(s,'math.sqrt(2 * 9.81 * .05)','math.sqrt(2 * 9.81 * .20)');write(focus,s)
  focused=copy.deepcopy(base['NATIVE_CONTRACT']['task_focused_real_replay']);focused.update(height_m=.20,source_SHA=H(focus));focused.pop('source_CPU_proof_SHA',None)
  stance=copy.deepcopy(oldtask['stance_reference_revision']);stance.update(schema='mod4.flat100.grounded_stance_target20.v1',reference_SHA=REF,target_wheel_clearance_m=.20,source_height_m=.05,user_authorized_height_change=True);stance.pop('source_CPU_SHA',None)
  modekind='continue_warm99_height20';kind='MOD4_NATIVE99_WARM_FLAT20_TARGET100_TYPED_SOURCE_CPU_V1';schema='mod4.native99_to_flat20.target100.objective_window.v1';method='MOD4_flat100_target20_from_qualified99'
  contract=copy.deepcopy(base['NATIVE_CONTRACT']);contract.update(input_start_mode=modekind,stance_reference_revision=stance,flat_jump_target_m=.20,source_flat_jump_target_m=.05,user_authorized_height_change_5_to20=True,task_focused_real_replay=focused)
  pins=copy.deepcopy(base['SOURCE_PINS']);pub=source['original_producer'];pins.update(final=pub,native_contract=base['NATIVE_CONTRACT'],producer=pub['producer'],source_migration_window=pub['native88_migration_window'])
  flatcontract=copy.deepcopy(base['FLAT_OBJECTIVE_CONTRACT']);flatcontract.update(stance_reference_revision=stance,flat_jump_target_m=.20,source_flat_jump_target_m=.05);flatcontract['source_MDP_contract']['reference_metadata']=copy.deepcopy(doc['metadata']);flatcontract['source_MDP_contract']['target']='both own wheel lowest points20cm then real floor support stable.5s'
  text='"""Exact100 source99 warm -> user-authorized20cm target; no physical mutation."""\n'
  for name,value in [('SOURCE_PINS',pins),('NATIVE_CONTRACT',contract),('FLAT_OBJECTIVE_SHA',REF),('FLAT_OBJECTIVE_CONTRACT',flatcontract),('OUTPUT_GAS400_PARAMETER_CONTRACT_SHA',oldtask['gas400_parameter_source_contract_SHA']),('SOURCE_MODE',modekind)]:text+=name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'
  write(B/'source/native100_target20_pins_v1.py',text)
  mig=B/'source/native88C_to_flat_migration_v1.py';s=mig.read_text();write(B/'source/native99_prior_migration_validation_v1.py',s);s=rep(s,'from native99_stance_pins_v1 import','from native100_target20_pins_v1 import')
  for name,value in [('SOURCE_SHA',source['SHA']),('SOURCE_REFERENCE_SHA',pub['producer']['reference_artifact_SHA']),('METHOD',method),('KIND',kind),('SOURCES',{'h1':dict(SHA=source['SHA'],**progress,seed=27)})]:s=assign(s,name,value)
  s=s.replace('mod4.native99.stance_continue97.objective_window.v1',schema)
  validator='''def validate_source(full,expected_source_contract,expected_args,expected_progress,expected_reference_SHA):
 require(exact_plain(expected_source_contract,SOURCE_PINS['native_contract']) and exact_plain(expected_args,SOURCE_PINS['native_args']),'qualified99 source contract/args')
 require(exact_plain(expected_progress,{k:SOURCES['h1'][k] for k in ('updates','world_updates','policy_updates')}) and expected_reference_SHA==SOURCE_REFERENCE_SHA,'qualified99 counters/reference')
 native=full['UniSuperMimic_H1_test'];pub=full['UniSuperMimic_publication']
 require(exact_plain(full['UniSuperMimic_test_contract'],SOURCE_PINS['native_contract']) and exact_plain(pub['producer'],SOURCE_PINS['producer']) and exact_plain(native['args'],expected_args),'qualified99 fullliteral source')
 require(native['iteration']==pub['native_iteration']==SOURCES['h1']['updates'] and pub['world_updates']==SOURCES['h1']['world_updates'] and pub['policy_updates']==SOURCES['h1']['policy_updates'],'qualified99 progress')
 from native99_prior_migration_validation_v1 import verify_saved_migration
 verify_saved_migration(full,pub)
 require(exact_plain(pub['native88_migration_window'],SOURCE_PINS['source_migration_window']),'qualified99 completed migration')
 for name,steps,count,betas in [('opt_wm',SOURCES['h1']['world_updates'],14,(.9,.999)),('opt_pi',SOURCES['h1']['policy_updates'],20,(.9,.95)),('opt_v',20*SOURCES['h1']['policy_updates'],6,(.9,.999))]:
  opt=native[name];require(len(opt['param_groups'])==1 and all(tuple(x['betas'])==betas for x in opt['param_groups']) and len(opt['state'])==count and {int(x['step']) for x in opt['state'].values()}=={steps},'qualified99 complete native optimizer '+name)
 require(len(full['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in full['optimizer_state_dict']['state'].values()}=={832460},'unchanged separate frozenRSL')
 return native,pub
'''
  s=replace_def(s,'validate_source',validator);write(mig,s)
  bridge=B/'source/native_flat_jump_bridge_v2_original_support.py';s=bridge.read_text();s=rep(s,'def install_flat_real_counter(env):','def install_flat_real_counter(env,*,height_m):');s=rep(s,'FlatJumpPhase(height_m=.05)','FlatJumpPhase(height_m=height_m)');s=rep(s,'provider, height_m=.05','provider, height_m=height_m');write(bridge,s)
  adapter=B/'source/native_flat_jump_adapter_v1.py';s=adapter.read_text();s=rep(s,'both own wheel lowest points5cm then real floor support stable.5s','both own wheel lowest points20cm then real floor support stable.5s');write(adapter,s)
  entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';s=entry.read_text();s=rep(s,'install_flat_real_counter(env)','install_flat_real_counter(env,height_m=provider.phase.height_m)');s=rep(s,"input_start_mode=task['input_start_mode'],stance_reference_revision=task['stance_reference_revision'],","input_start_mode=task['input_start_mode'],stance_reference_revision=task['stance_reference_revision'],flat_jump_target_m=task['flat_jump_target_m'],")
  s=s.replace('MOD4_flat99_grounded_stance_continue97',method).replace('own_MOD4_native_flat5cm_same_nominal400','own_MOD4_native_flat20cm_same_nominal400').replace('original_Isaac_MOD4_own_flat5cm_native_v1','original_Isaac_MOD4_own_flat20cm_native_v1');write(entry,s)
  guard=B/'native_flat90_source_guard_v1.py';s=guard.read_text();s=rep(s,'mod4.native.flat05.stance99.continue97.complete_source.v1','mod4.native.flat20.target100.complete_source.v1');s=rep(s,repr(dict(updates=12066,world_updates=120660,policy_updates=11682)),repr(progress));s=rep(s,"task.get('logical_slot')=='h1'","task.get('logical_slot')=="+repr(slot));s=s.replace('GPU-c27eecbd-6838-7290-1cd2-37e34522213d',GPU)
  s=rep(s,"require(task['flat05_objective_changed_from_native88C']", "require(task['flat_jump_target_m']==.20 and task['user_authorized_height_change_5_to20'],'explicit user20cm target')\n require(task['flat05_objective_changed_from_native88C']");write(guard,s)
  task=copy.deepcopy(oldtask);task.update(id='MOD4_H1_FLAT20_NATIVE100_'+mode,logical_slot=slot,GPU_UUID=GPU,source_SHA=source['SHA'],source_filename=nativefile,source_progress=progress,source_native_iteration=progress['updates'],source_native_contract=pins['native_contract'],source_qualification_kind=kind,native_reference_SHA=REF,native_seed=seed,native_learning_seed=27,input_start_mode=modekind,stance_reference_revision=stance,flat_jump_target_m=.20,user_authorized_height_change_5_to20=True,task_focused_real_replay=focused)
  cpu=B/'target_native_flat90_source_sdk_CPU_once.py';s=cpu.read_text();s=rep(s,'from native99_stance_pins_v1 import','from native100_target20_pins_v1 import');s=rep(s,"doc['metadata']['height_m']==.05","doc['metadata']['height_m']==.20");s=rep(s,'focused_mask(torch.tensor([180,200,220])).all() and not focused_mask(torch.tensor([179,221,500])).any()','focused_mask(torch.tensor([180,200,240])).all() and not focused_mask(torch.tensor([179,241,500])).any()')
  s=rep(s,"stance_reference_source_CPU_passed=True,input_start_mode", "flat_jump_target_m=task['flat_jump_target_m'],physical_initial_seed=task['native_seed'],real_counter_target20_source_CPU_passed=True,stance_reference_source_CPU_passed=True,input_start_mode")
  s=rep(s,"require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')", "from flat_real_physics_events_v3_original_support import FlatRealPhysicsEvents\n require(FlatRealPhysicsEvents(1,height_m=.20).height_m==task['flat_jump_target_m']==provider.phase.height_m==.20,'goal and actual diagnostic same20cm target')\n require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')");write(cpu,s)
  c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c.update(schema='mod4.native.flat20.target100.complete_source.v1',source_SHA=source['SHA'],input_start_mode=modekind,stance_reference_revision=stance,flat_jump_target_m=.20,user_authorized_height_change_5_to20=True)
  c['small_evidence_pins'][oldtask['native_reference_relative']]=REF;c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
  write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2));task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
  rows=[]
  for p in sorted(B.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(B).as_posix()
   if rel=='job0/source/'+nativefile:row=dict(relative=rel,bytes=source['bytes'],SHA=source['SHA'])
   elif p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):row=previous[rel]
   else:row=dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
   assert p.stat().st_size==row['bytes'];rows.append(row)
  m=copy.deepcopy(manifest);m.update(source_SHA=source['SHA'],files=rows);write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2))
  for p in B.rglob('*.py'):ast.parse(p.read_bytes())
  results[mode]=dict(task=task,job_root=job,GPU_UUID=GPU,logical_slot=slot,source=source,source_progress=progress,source_kind=kind,payload=str(B),manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),reference_SHA=REF,source_CPU_pending=True,not_GO=True)
 with (R/'TWO100_TARGET20_EXACT_QUALIFIED99_PAYLOADS_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,epoch=time.time(),payloads=results,active_height_m=.20,saved_native_learning_seed=27,physical_initial_seeds=[27,28],whole_source_models_norms_threeoptimizers_preserved=True,no_saved_model_decode_or_extra_binary_hash_or_remote=True),f,indent=2,allow_nan=False)
 print(json.dumps(dict(prepared=True,target_m=.20,reference_SHA=REF,actual20cm_GO=False)))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (R/'SOURCE100_PREPARER_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_GPU_or_remote=True),f,indent=2)
  raise
