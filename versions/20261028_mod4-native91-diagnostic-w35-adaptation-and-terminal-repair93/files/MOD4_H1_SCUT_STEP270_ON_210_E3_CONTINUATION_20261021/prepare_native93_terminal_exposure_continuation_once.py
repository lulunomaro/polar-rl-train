"""Prepare a new typed native91 continuation; source-only, no remote/GO."""
from pathlib import Path
import ast,copy,hashlib,json,pprint,runpy,shutil,time,traceback
T=Path(__file__).resolve().parent
O=T/'MOD4_H1_FLAT05_MASK_AWARE_MIXED72_RESOURCE_V91_20261027'
N=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028'
L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
F=L/'flat92_terminal_exposure_source_v1'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_TERMINAL_2610v93/h1'
SHA='bd36a58c6bb31471212f4329407e85113064337650e51fc3c1587995dc2e3d50'
KIND='MOD4_NATIVE91_H1_TERMINAL_EXPOSURE93_TYPED_SOURCE_CPU_V1'
PROGRESS=dict(updates=9256,world_updates=92560,policy_updates=9000)
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(s,encoding='utf8')
def put(p,v):
 with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False)
def replace_def(s,name,new):
 node=next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name==name)
 lines=s.splitlines(keepends=True);return ''.join(lines[:node.lineno-1])+new.rstrip()+'\n'+''.join(lines[node.end_lineno:])
def main():
 assert not N.exists();N.mkdir();R=N/'reports';R.mkdir();B=N/'payload';B.mkdir();P=N/'controllers';P.mkdir()
 put(R/'NATIVE93_SOURCE_PREPARATION_STARTED_ACTUAL.json',dict(epoch=time.time(),no_remote_or_model_decode=True))
 closed=read(O/'reports/NATIVE91_COMPLETE_FINAL_OR_PARTIAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json')
 qual=read(O/'reports/NATIVE91_FORMAL_NATIVE_FULLSTATE_INITIAL_CPU_AND_COST_ACTUAL.json')
 assert qual['passed'] and closed['published']['SHA']==SHA and closed['canonical_None']
 evidence=read(F/'SOURCE_CPU_ACTUAL.json');assert evidence['passed'] and evidence['changed_AST_functions']==['valid_imagination_start']
 assert H(F/'native_flat_jump_adapter_v1.py')==evidence['source_candidate']['SHA']
 pub=closed['published']['original_producer'];base=runpy.run_path(str(O/'payload/source/native90B_mask91_pins_v1.py'))
 oldtask=read(O/'payload/job0/TASK.json');oldmf=read(O/'payload/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 for row in oldmf['files']:
  rel=row['relative']
  if rel=='job0/source/'+oldtask['source_filename']:continue
  src=O/'payload'/rel;dest=B/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
 nativefile='H1_native91_qualified_h1.pt';shutil.copy2(Path(closed['published']['local_path']),B/'job0/source'/nativefile)
 pins=copy.deepcopy(base['SOURCE_PINS']);pins.update(final=pub,native_contract=base['NATIVE_CONTRACT'],producer=pub['producer'],source_migration_window=pub['native88_migration_window'])
 contract=copy.deepcopy(base['NATIVE_CONTRACT'])
 exposure=dict(schema='mod4.flat93.terminal_exposure.v1',source_old_mdp_SHA=evidence['source_original']['SHA'],selected_mdp_SHA=evidence['source_candidate']['SHA'],source_CPU_proof_SHA=H(F/'SOURCE_CPU_ACTUAL.json'),actual_start_age_min=0,actual_start_age_max=499,physical_timeout_age=500,learner_BPTT_and_TD_lambda_unchanged=True)
 contract['imagination_terminal_exposure']=exposure
 text='"""Qualified91 formal metadata; native state is separate from frozen RSL."""\n'
 for name,value in [('SOURCE_PINS',pins),('NATIVE_CONTRACT',contract),('FLAT_OBJECTIVE_SHA',base['FLAT_OBJECTIVE_SHA']),('FLAT_OBJECTIVE_CONTRACT',base['FLAT_OBJECTIVE_CONTRACT'])]:text+=name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'
 write(B/'source/native91_terminal93_pins_v1.py',text)
 oldmig=(O/'payload/source/native88C_to_flat_migration_v1.py').read_text('utf8')
 write(B/'source/native91_prior_migration_validation_v1.py',oldmig)
 s=oldmig.replace('from native90B_mask91_pins_v1 import','from native91_terminal93_pins_v1 import',1)
 for a,b in [('8b0ef2b6c60f4453ebb46a9718133e54e33cad5985ddd96459e479d10fc5ef43',SHA),('MOD4_NATIVE90B_H1_MASK_AWARE_FLAT91_TYPED_SOURCE_CPU_V1',KIND),('MOD4_own_flat5cm_mask91_native400_continuation','MOD4_own_flat5cm_terminal93_native400_continuation'),('mod4.native90B_to_flat05_mask91.objective_window.v1','mod4.native91_to_flat05_terminal93.objective_window.v1')]:s=s.replace(a,b)
 # Only current validation/progress changes. Prior91 validator is retained verbatim.
 s=s.replace('updates=7841,world_updates=78410,policy_updates=7649','updates=9256,world_updates=92560,policy_updates=9000')
 s=replace_def(s,'validate_source','''def validate_source(full,expected_source_contract,expected_args,expected_progress,expected_reference_SHA):
 from native91_prior_migration_validation_v1 import verify_saved_migration as verify_prior
 require(exact_plain(expected_source_contract,SOURCE_PINS['native_contract']),'exact qualified91 source contract')
 require(exact_plain(expected_args,SOURCE_PINS['native_args']),'exact saved architecture/args')
 require(exact_plain(expected_progress,{k:SOURCES['h1'][k] for k in ('updates','world_updates','policy_updates')}),'exact91 source progress')
 require(expected_reference_SHA==SOURCE_REFERENCE_SHA,'exact source flat reference')
 pub=full['UniSuperMimic_publication'];native=full['UniSuperMimic_H1_test'];verify_prior(full,pub)
 require(exact_plain(full['UniSuperMimic_test_contract'],SOURCE_PINS['native_contract']),'qualified91 contract literal')
 require(exact_plain(pub['producer'],SOURCE_PINS['producer']),'qualified91 producer literal')
 require(exact_plain(pub['native88_migration_window'],SOURCE_PINS['source_migration_window']),'qualified91 migration literal')
 require(exact_plain(native['args'],expected_args),'config literal')
 require(native['iteration']==pub['native_iteration']==9256 and pub['world_updates']==92560 and pub['policy_updates']==9000,'exact91 global counters')
 for name,steps,count,betas in [('opt_wm',92560,14,(.9,.999)),('opt_pi',9000,20,(.9,.95)),('opt_v',180000,6,(.9,.999))]:
  opt=native[name];require(len(opt['state'])==count and {int(x['step']) for x in opt['state'].values()}=={steps},'native91 optimizer '+name)
  require(all(tuple(x['betas'])==betas for x in opt['param_groups']),'native betas '+name)
 require(len(full['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in full['optimizer_state_dict']['state'].values()}=={832460},'separate literal frozenRSL832460')
 return native,pub
''')
 s=s.replace("source=validate_role_source(key,task['source_SHA'],task['source_progress'])","source=validate_role_source(key,task['source_SHA'],task['source_progress'])\n require(task.get('imagination_terminal_exposure')==NATIVE_CONTRACT['imagination_terminal_exposure'] and go.get('imagination_terminal_exposure')==task['imagination_terminal_exposure'],'exact new terminal exposure Task-GO')",1)
 write(B/'source/native88C_to_flat_migration_v1.py',s)
 shutil.copy2(F/'native_flat_jump_adapter_v1.py',B/'source/native_flat_jump_adapter_v1.py')
 task=copy.deepcopy(oldtask);task.update(id='MOD4_H1_FLAT05_TERMINAL_V93',source_SHA=SHA,source_filename=nativefile,source_progress=PROGRESS,source_native_iteration=9256,source_native_contract=pins['native_contract'],imagination_terminal_exposure=exposure,source_qualification_kind=KIND)
 guard=(B/'native_flat90_source_guard_v1.py').read_text('utf8').replace('dict(updates=7841,world_updates=78410,policy_updates=7649)','dict(updates=9256,world_updates=92560,policy_updates=9000)').replace('mod4.native.flat05.mask91.complete_source.v1','mod4.native.flat05.terminal93.complete_source.v1');write(B/'native_flat90_source_guard_v1.py',guard)
 entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';s=entry.read_text('utf8').replace('MOD4_own_flat5cm_mask91_native400_continuation','MOD4_own_flat5cm_terminal93_native400_continuation')
 needle="goal_encoding_changed_from90B=True,goal_conditioning=task['goal_conditioning'],";assert s.count(needle)==1;s=s.replace(needle,needle+"\n        imagination_terminal_exposure=task['imagination_terminal_exposure'],",1);write(entry,s)
 cpu=B/'target_native_flat90_source_sdk_CPU_once.py';s=cpu.read_text('utf8').replace('initial_loads=dict(native90B=1,normal86=1)','initial_loads=dict(native91=1,normal86=1)')
 needle="require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')";assert s.count(needle)==1
 s=s.replace(needle,"require(mdp.valid_imagination_start(torch.tensor([468,499]),32).all() and not mdp.valid_imagination_start(torch.tensor([500]),32).any(),'new actual preterminal starts reach unchanged timeout500')\n "+needle)
 s=s.replace('mask_aware_goal_source_CPU_passed=True,','terminal_exposure_source_CPU_passed=True,imagination_terminal_exposure=task[\'imagination_terminal_exposure\'],mask_aware_goal_source_CPU_passed=True,');write(cpu,s)
 c=read(O/'payload/FLAT90_SOURCE_CONTRACT_ACTUAL.json');c.update(schema='mod4.native.flat05.terminal93.complete_source.v1',source_SHA=SHA,imagination_terminal_exposure=exposure)
 c['protected_current88C_files'].pop('source/native_flat_jump_adapter_v1.py',None)
 c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
 write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2));task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
 oldrows={r['relative']:r for r in oldmf['files']};rows=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
  rel=p.relative_to(B).as_posix()
  if p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):
   row=dict(relative=rel,bytes=closed['published']['bytes'],SHA=SHA) if rel=='job0/source/'+nativefile else oldrows[rel];assert p.stat().st_size==row['bytes']
  else:row=dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
  rows.append(row)
 mf=copy.deepcopy(oldmf);mf.update(source_SHA=SHA,files=rows);write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(mf,indent=2))
 for p in (O/'controllers').glob('*.py'):shutil.copy2(p,P/p.name)
 protocol=(P/'h1_next72_protocol.py').read_text('utf8')
 for a,b in [('MOD4_H1_FLAT05_MASK_AWARE_2610v91','MOD4_H1_FLAT05_TERMINAL_2610v93'),('8b0ef2b6c60f4453ebb46a9718133e54e33cad5985ddd96459e479d10fc5ef43',SHA),('dict(updates=7841,world_updates=78410,policy_updates=7649)','dict(updates=9256,world_updates=92560,policy_updates=9000)'),('MOD4_NATIVE90B_H1_MASK_AWARE_FLAT91_TYPED_SOURCE_CPU_V1',KIND)]:protocol=protocol.replace(a,b)
 needle="require(s.get('goal_encoding_changed_from90B') is True,'new mask-aware input encoding')";assert protocol.count(needle)==1;protocol=protocol.replace(needle,needle+"\n require(s.get('imagination_terminal_exposure')=="+repr(exposure)+",'new terminal exposure exact contract')")
 protocol=protocol.replace('flat05_objective_changed_from_native88C=True,goal_encoding_changed_from90B=True,','flat05_objective_changed_from_native88C=True,goal_encoding_changed_from90B=True,imagination_terminal_exposure=spec[\'imagination_terminal_exposure\'],')
 protocol=protocol.replace("'source_native_fullstate_finite',","'terminal_exposure_source_CPU_passed','source_native_fullstate_finite',")
 write(P/'flat90_protocol_v1.py',protocol);write(P/'h1_next72_protocol.py',protocol)
 req=copy.deepcopy(read(O/'reports/NATIVE91_SOURCE_PREPARED_ACTUAL.json')['h1_spec_pending_actual_CPU_and_controller'])
 req.update(source_SHA=SHA,source_progress=PROGRESS,source_native_iteration=9256,source_qualification_kind=KIND,job_root=JOB,CPU_path=JOB+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json',CPU_proof_path=JOB+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json',payload_manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),payload_manifest_path=JOB+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=JOB+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json',worker_SHA=H(B/'h1_native_flat90_worker_v1.py'),imagination_terminal_exposure=exposure)
 for k in ('source_CPU_SHA','CPU_waited_proof_SHA','manifest_SHA'):req.pop(k,None)
 for p in [*B.rglob('*.py'),*P.glob('*.py')]:ast.parse(p.read_bytes())
 put(R/'NATIVE93_SOURCE_PREPARED_ACTUAL.json',dict(passed=True,epoch=time.time(),task=task,h1_spec_pending_actual_CPU_and_controller=req,qualified_native91=closed['published'],source_CPU_terminal_proof=evidence,no_local_model_decode_or_rehash=True,local_copy2_did_read_model_bytes=True,source_only_not_installed_or_GO=True))
 print(json.dumps(dict(prepared=True,source_SHA=SHA,typed_native91_lineage=True,actual_source_SDK_and_resource_admission_pending=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  if (N/'reports').is_dir():put(N/'reports'/('NATIVE93_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(traceback=traceback.format_exc(),no_rerun_old_once=True))
  raise
