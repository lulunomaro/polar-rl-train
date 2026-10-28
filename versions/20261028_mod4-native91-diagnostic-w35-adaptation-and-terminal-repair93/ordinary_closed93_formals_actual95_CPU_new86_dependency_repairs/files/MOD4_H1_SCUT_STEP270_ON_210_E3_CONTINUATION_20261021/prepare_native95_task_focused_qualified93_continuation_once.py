"""Prepare NEW native93->95 source; no remote/model decode, not a GO."""
from pathlib import Path
import ast,copy,hashlib,json,pprint,runpy,shutil,time
T=Path(__file__).resolve().parent; L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
O=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028'
N=T/'MOD4_H1_FLAT05_TASK_FOCUSED_RESOURCE_V95_20261028'
F=L/'flat95_task_focused_real_replay_source_v1'
JOB='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_TASK_FOCUSED_2610v95/h1'
KIND='MOD4_NATIVE93_H1_TASK_FOCUSED95_TYPED_SOURCE_CPU_V1'
PROGRESS=dict(updates=10692,world_updates=106920,policy_updates=10372)

def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b,1)
def replace_def(s,name,new):
 x=next(x for x in ast.parse(s).body if isinstance(x,ast.FunctionDef) and x.name==name)
 lines=s.splitlines(keepends=True);return ''.join(lines[:x.lineno-1])+new.rstrip()+'\n'+''.join(lines[x.end_lineno:])

def main():
 assert not N.exists();N.mkdir();R=N/'reports';R.mkdir();B=N/'payload';B.mkdir();C=N/'controllers';C.mkdir()
 closed=read(O/'reports/THREE93_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL_V1.json')
 qualified=read(O/'reports/NATIVE93_FORMAL_NATIVE_FULLSTATE_INITIAL_CPU_AND_COST_ACTUAL.json')
 evidence=read(F/'SOURCE_CPU_ACTUAL.json');assert qualified['passed'] and evidence['passed'] and closed['canonical_None']
 source=closed['published']['h1'];SHA=source['SHA'];pub=source['original_producer']
 assert SHA=='b008fc03d5de3e39217101523c7e8fc0ddebf5cd6e63699582b61053171d165e'
 base=runpy.run_path(str(O/'payloads/h1/source/native91_terminal93_pins_v1.py'))
 oldtask=read(O/'payloads/h1/job0/TASK.json');mf=read(O/'payloads/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 for row in mf['files']:
  rel=row['relative']
  if rel=='job0/source/'+oldtask['source_filename']:continue
  dest=B/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(O/'payloads/h1'/rel,dest)
 nativefile='H1_native93_qualified_h1.pt';shutil.copy2(source['local_path'],B/'job0/source'/nativefile)
 pins=copy.deepcopy(base['SOURCE_PINS']);pins.update(final=pub,native_contract=base['NATIVE_CONTRACT'],producer=pub['producer'],source_migration_window=pub['native88_migration_window'])
 contract=copy.deepcopy(base['NATIVE_CONTRACT']);focus=copy.deepcopy(evidence['source_contract'])
 focus.update(source_SHA=evidence['source_SHA'],source_CPU_proof_SHA=H(F/'SOURCE_CPU_ACTUAL.json'))
 contract['task_focused_real_replay']=focus;contract['native_learning_seed']=27
 text='"""Qualified93 formal pins; not a physical-success certificate."""\n'
 for name,value in [('SOURCE_PINS',pins),('NATIVE_CONTRACT',contract),('FLAT_OBJECTIVE_SHA',base['FLAT_OBJECTIVE_SHA']),('FLAT_OBJECTIVE_CONTRACT',base['FLAT_OBJECTIVE_CONTRACT'])]:text+=name+'='+pprint.pformat(value,width=120,sort_dicts=False)+'\n'
 write(B/'source/native93_focused95_pins_v1.py',text)
 oldmig=(B/'source/native88C_to_flat_migration_v1.py').read_text('utf8')
 write(B/'source/native93_prior_migration_validation_v1.py',oldmig)
 s=rep(oldmig,'from native91_terminal93_pins_v1 import','from native93_focused95_pins_v1 import')
 s=s.replace('bd36a58c6bb31471212f4329407e85113064337650e51fc3c1587995dc2e3d50',SHA)
 s=s.replace('MOD4_NATIVE91_H1_TERMINAL_EXPOSURE93_TYPED_SOURCE_CPU_V1',KIND).replace('MOD4_own_flat5cm_terminal93_native400_continuation','MOD4_own_flat5cm_task_focused95_native400_continuation')
 s=s.replace('mod4.native91_to_flat05_terminal93.objective_window.v1','mod4.native93_to_flat05_focused95.objective_window.v1').replace('updates=9256,world_updates=92560,policy_updates=9000','updates=10692,world_updates=106920,policy_updates=10372')
 s=replace_def(s,'validate_source','''def validate_source(full,expected_source_contract,expected_args,expected_progress,expected_reference_SHA):
 from native93_prior_migration_validation_v1 import verify_saved_migration as verify_prior
 require(exact_plain(expected_source_contract,SOURCE_PINS['native_contract']),'exact qualified93 source contract')
 require(exact_plain(expected_args,SOURCE_PINS['native_args']),'exact saved architecture and learning seed27')
 require(exact_plain(expected_progress,{k:SOURCES['h1'][k] for k in ('updates','world_updates','policy_updates')}),'exact93 source progress')
 require(expected_reference_SHA==SOURCE_REFERENCE_SHA,'same own flat reference')
 pub=full['UniSuperMimic_publication'];native=full['UniSuperMimic_H1_test'];verify_prior(full,pub)
 require(exact_plain(full['UniSuperMimic_test_contract'],SOURCE_PINS['native_contract']),'qualified93 contract literal')
 require(exact_plain(pub['producer'],SOURCE_PINS['producer']),'qualified93 producer literal')
 require(exact_plain(pub['native88_migration_window'],SOURCE_PINS['source_migration_window']),'qualified93 migration literal')
 require(exact_plain(native['args'],expected_args),'config literal')
 require(native['iteration']==pub['native_iteration']==10692 and pub['world_updates']==106920 and pub['policy_updates']==10372,'exact93 counters')
 for name,steps,count,betas in [('opt_wm',106920,14,(.9,.999)),('opt_pi',10372,20,(.9,.95)),('opt_v',207440,6,(.9,.999))]:
  opt=native[name];require(len(opt['state'])==count and {int(x['step']) for x in opt['state'].values()}=={steps},'native93 optimizer '+name)
  require(all(tuple(x['betas'])==betas for x in opt['param_groups']),'native betas '+name)
 require(len(full['optimizer_state_dict']['state'])==17 and {int(x['step']) for x in full['optimizer_state_dict']['state'].values()}=={832460},'separate frozen normal86')
 return native,pub
''')
 s=rep(s,"require(task['native_seed']==27 and go['source_SHA']==SOURCE_SHA", "require(task['native_learning_seed']==go['native_learning_seed']==NATIVE_CONTRACT['native_learning_seed']==27 and task['native_seed']==go['native_seed'] and task['native_seed'] in (27,28) and go['source_SHA']==SOURCE_SHA")
 s=rep(s,"source=validate_role_source(key,task['source_SHA'],task['source_progress'])", "source=validate_role_source(key,task['source_SHA'],task['source_progress'])\n require(task['task_focused_real_replay']==go['task_focused_real_replay']==NATIVE_CONTRACT['task_focused_real_replay'],'exact focused sampling Task GO')")
 s=rep(s,"p=expected['producer'];require", "p=expected['producer'];require(p['task_focused_real_replay']==NATIVE_CONTRACT['task_focused_real_replay'] and p['native_learning_seed']==27,'new sampler producer and saved learning seed')\n require")
 write(B/'source/native88C_to_flat_migration_v1.py',s)
 shutil.copy2(F/'flat95_task_focused_starts_v1.py',B/'source/flat95_task_focused_starts_v1.py')
 task=copy.deepcopy(oldtask);task.update(id='MOD4_H1_FLAT05_TASK_FOCUSED_V95',source_SHA=SHA,source_filename=nativefile,source_progress=PROGRESS,source_native_iteration=10692,source_native_contract=pins['native_contract'],source_qualification_kind=KIND,native_learning_seed=27,task_focused_real_replay=focus)
 entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';s=entry.read_text('utf8').replace('MOD4_own_flat5cm_terminal93_native400_continuation','MOD4_own_flat5cm_task_focused95_native400_continuation')
 assert s.count("config_for(int(task['native_seed']))")==2;s=s.replace("config_for(int(task['native_seed']))","config_for(int(task['native_learning_seed']))")
 s=rep(s,"imagination_terminal_exposure=task['imagination_terminal_exposure'],", "imagination_terminal_exposure=task['imagination_terminal_exposure'],\n        task_focused_real_replay=task['task_focused_real_replay'],native_learning_seed=task['native_learning_seed'],physical_initial_seed=task['native_seed'],")
 s=rep(s,'    from flat_policy_phase_coverage_v1 import attach_optional_policy_phase_coverage',"    from flat95_task_focused_starts_v1 import attach_task_focused_starts\n    bridge.task_focus_diagnostic=attach_task_focused_starts(learner,diagnostic=lambda value:atomic_json(out/'NATIVE_TASK_FOCUS_SAMPLE_COUNTS_ACTUAL.json',value))\n    from flat_policy_phase_coverage_v1 import attach_optional_policy_phase_coverage")
 write(entry,s)
 g=B/'native_flat90_source_guard_v1.py';s=g.read_text('utf8').replace('dict(updates=9256,world_updates=92560,policy_updates=9000)','dict(updates=10692,world_updates=106920,policy_updates=10372)').replace('mod4.native.flat05.terminal93.complete_source.v1','mod4.native.flat05.focused95.complete_source.v1');write(g,s)
 cpu=B/'target_native_flat90_source_sdk_CPU_once.py';s=cpu.read_text('utf8').replace('initial_loads=dict(native91=1,normal86=1)','initial_loads=dict(native93=1,normal86=1)')
 s=rep(s,"require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')", "from flat95_task_focused_starts_v1 import focused_mask,CONTRACT\n require(focused_mask(torch.tensor([180,200,220])).all() and not focused_mask(torch.tensor([179,221,500])).any(),'new actual installed focused-phase source')\n require(task['native_learning_seed']==27 and all(task['task_focused_real_replay'][k]==v for k,v in CONTRACT.items()),'selected exact sampling contract')\n require(not torch.cuda.is_initialized(),'CPU admission unexpectedly initialized CUDA')")
 s=rep(s,'terminal_exposure_source_CPU_passed=True,',"task_focused_replay_source_CPU_passed=True,task_focused_real_replay=task['task_focused_real_replay'],native_learning_seed=27,terminal_exposure_source_CPU_passed=True,")
 write(cpu,s)
 c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c.update(schema='mod4.native.flat05.focused95.complete_source.v1',source_SHA=SHA,task_focused_real_replay=focus,native_learning_seed=27)
 c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
 write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2));task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
 previous={r['relative']:r for r in mf['files']};rows=[]
 for p in sorted(B.rglob('*')):
  if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
  rel=p.relative_to(B).as_posix()
  if p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):
   row=dict(relative=rel,bytes=source['bytes'],SHA=SHA) if rel=='job0/source/'+nativefile else previous[rel];assert p.stat().st_size==row['bytes']
  else:row=dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
  rows.append(row)
 mf.update(source_SHA=SHA,files=rows);write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(mf,indent=2))
 protocol=(O/'controllers/h1_next72_protocol.py').read_text('utf8')
 for a,b in [('MOD4_H1_FLAT05_TERMINAL_2610v93','MOD4_H1_FLAT05_TASK_FOCUSED_2610v95'),('bd36a58c6bb31471212f4329407e85113064337650e51fc3c1587995dc2e3d50',SHA),('dict(updates=9256,world_updates=92560,policy_updates=9000)','dict(updates=10692,world_updates=106920,policy_updates=10372)'),('MOD4_NATIVE91_H1_TERMINAL_EXPOSURE93_TYPED_SOURCE_CPU_V1',KIND)]:protocol=protocol.replace(a,b)
 protocol=rep(protocol,"require(s.get('goal_encoding_changed_from90B') is True,'new mask-aware input encoding')", "require(s.get('goal_encoding_changed_from90B') is True,'new mask-aware input encoding')\n require(s.get('native_learning_seed')==27 and s.get('task_focused_real_replay')=="+repr(focus)+",'saved learner seed and exact real replay mixture')")
 protocol=rep(protocol,"'terminal_exposure_source_CPU_passed',","'task_focused_replay_source_CPU_passed','terminal_exposure_source_CPU_passed',")
 protocol=rep(protocol,"fields=('source_progress','native_seed',","fields=('task_focused_real_replay','native_learning_seed','source_progress','native_seed',")
 protocol=rep(protocol,"for k in ('source_SHA','worker_SHA','source_CPU_SHA',","for k in ('task_focused_real_replay','native_learning_seed','source_SHA','worker_SHA','source_CPU_SHA',")
 write(C/'h1_next72_protocol.py',protocol)
 req=copy.deepcopy(read(O/'reports/NATIVE93_SOURCE_PREPARED_ACTUAL.json')['h1_spec_pending_actual_CPU_and_controller'])
 req.update(source_SHA=SHA,source_progress=PROGRESS,source_native_iteration=10692,source_qualification_kind=KIND,native_learning_seed=27,task_focused_real_replay=focus,job_root=JOB,CPU_path=JOB+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json',CPU_proof_path=JOB+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json',payload_manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),payload_manifest_path=JOB+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json',source_contract_path=JOB+'/FLAT90_SOURCE_CONTRACT_ACTUAL.json',worker_SHA=H(B/'h1_native_flat90_worker_v1.py'))
 for k in ('source_CPU_SHA','CPU_waited_proof_SHA','manifest_SHA'):req.pop(k,None)
 for p in [*B.rglob('*.py'),*C.glob('*.py')]:ast.parse(p.read_bytes())
 put(R/'NATIVE95_SOURCE_PREPARED_ACTUAL.json',dict(passed=True,epoch=time.time(),task=task,h1_spec_pending_actual_CPU_and_controller=req,qualified_native93=source,source_only_not_installed_or_GO=True,source_sampler_CPU=evidence,no_local_model_decode_or_rehash=True,copy2_reads_qualified_model_bytes_for_new_payload=True,normalizer_and_three_optimizer_restore_unchanged=True))
 put(R/'LOCAL_PREPARATION_READER_PATH_ERROR_RETAINED_ACTUAL.json',dict(error='Get-Content attempted controller_three93_sealed_v4/h1_next72_protocol.py; that controller contains h1_native93_protocol.py. Correct source found with rg at N93/controllers/h1_next72_protocol.py.',no_remote_model_or_training_effect=True))
 print(json.dumps(dict(prepared=True,source_SHA=SHA,target=JOB,source_SDK_and_runtime_pending=True)))

if __name__=='__main__':main()
