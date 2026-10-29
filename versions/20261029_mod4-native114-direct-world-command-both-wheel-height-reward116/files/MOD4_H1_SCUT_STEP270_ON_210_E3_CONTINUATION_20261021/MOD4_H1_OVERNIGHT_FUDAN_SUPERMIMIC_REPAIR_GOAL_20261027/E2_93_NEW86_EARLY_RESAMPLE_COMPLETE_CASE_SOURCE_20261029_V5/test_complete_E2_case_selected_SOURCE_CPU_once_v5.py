"""Fresh source/constructor/lifetime/producer tests. No old binary/SDK/remote."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,time,traceback
B=Path(__file__).resolve().parent;L=B.parent
OLD=L/'E2_93_NEW86_ORIGINAL_FLAT_HEIGHT_PROVIDER_REPAIR_SOURCE_20261029_V4';REF=L/'E2_93_EARLY_ORIGINAL_RESAMPLE_LIFECYCLE_SOURCE_20261029_V1'
def H(b):return hashlib.sha256(b).hexdigest()
def put(n,v):
 with (B/n).open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,indent=2,allow_nan=False)
def load(name):
 p=B/(name+'.py');s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 sys.path.insert(0,str(B))
 for p in B.glob('*.py'):ast.parse(p.read_bytes(),str(p))
 m=json.loads((B/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());rows={r['relative']:r for r in m['files']};old=json.loads((OLD/'E2_NEW86_COMPLETE_INPUT_MANIFEST_V1.json').read_bytes());oldrows={r['relative']:r for r in old['files']}
 protected=[r for r in oldrows if r.startswith(('runtime/','source/'))];assert all(rows[r]==oldrows[r] for r in protected)
 worker=(B/'evaluate_E2_adapted93_new86_frozen900_once_v1.py').read_bytes();base=(OLD/'evaluate_E2_adapted93_new86_frozen900_once_v1.py').read_bytes();d=json.loads((B/'SELECTED_E2_V5_SOURCE_DERIVATION_AND_ORIGINAL_WORKER_INVERSE_OPERATIONS.json').read_bytes());row=next(r for r in d['files'] if r['name']=='evaluate_E2_adapted93_new86_frozen900_once_v1.py');inverse=worker.decode()
 for op in reversed(row['operations']):assert inverse.count(op['new'])==op['count'];inverse=inverse.replace(op['new'],op['old'])
 assert inverse.encode()==base
 def loop(raw):return next(n for f in ast.walk(ast.parse(raw)) if isinstance(f,ast.FunctionDef) and f.name=='work' for n in ast.walk(f) if isinstance(n,ast.For) and isinstance(n.iter,ast.Call) and isinstance(n.iter.func,ast.Name) and n.iter.func.id=='range')
 assert ast.dump(loop(worker),include_attributes=False)==ast.dump(loop(base),include_attributes=False)
 source=load('e2_complete_case_source_contract_v5');timing=source.validate_worker_timing(worker);negative=[]
 for label,a,b in [('missing_early_install','early.install(DirectionalSpinCommand,sensor_resume_contract,e2_command_checkpoint_v1)','early_not_installed()'),('wrong900_window','for i in range(900):','for i in range(901):'),('extra_step','vec.step(action)','vec.step(vec.step(action))')]:
  assert worker.decode().count(a)==1
  try:source.validate_worker_timing(worker.decode().replace(a,b).encode())
  except (AssertionError,StopIteration):negative.append(label)
  else:raise AssertionError('Invalid source accepted '+label)
 entry=load('e2_declared_entry_receipt_cli_contract_v5');cli=entry.validate_entry_cli_learn_hook(Path(rows[entry.ENTRY]['local_path']).read_bytes(),worker);graph=entry.selected_receipt_graph(worker,(B/entry.SUP).read_bytes(),(B/entry.CODE).read_bytes());closure=entry.declared_import_closure(m,lambda rel:Path(rows[rel]['local_path']).read_bytes());guard=load('e2_frozen_worker_call_guard_v3').validate_frozen_worker_calls(ast.parse(worker))
 for text in ('runner.alg.update()','runner.alg.optimizer.step()','runner.alg.actor.train()'):
  try:load('e2_frozen_worker_call_guard_v3').validate_frozen_worker_calls(ast.parse(worker+b'\n'+text.encode()))
  except AssertionError:negative.append(text)
  else:raise AssertionError('Learner operation accepted')
 import torch as t
 # Actual original E2 sampler/method lifecycle with fresh CPU buffers, old values not decoded.
 lifecycle=load('E2_actual_target_early_method_CPU_fixture_v5').run_actual_target_lifecycle(B,(REF/'REFERENCE_SAVED_SDK_command_manager.py.txt').read_bytes(),(REF/'REFERENCE_SAVED_SDK_velocity_command.py.txt').read_bytes(),actual_target=False)
 api=load('selected_telemetry_constructor_API_fixture_v1').run_selected_constructor_fixture(B,'E2',t,source_path=Path(rows['runtime/isaac/mod4/mod4_task.py']['local_path']))
 catalog=load('e2_original_profile_catalog_candidate_v1');inst=load('e2_observed_command_instances_v1');prod=load('e2_early_original_resample_observer_v2_complete');n=5;book=inst.CommandInstances(t,n,'cpu');ids=t.arange(n);key=t.tensor([0,6,7,8,9]);uid=t.zeros(n,dtype=t.long);episode=uid.clone();cmd=t.zeros(n,3);cmd[3:,0]=1.;yaw=t.tensor([0.,-2.,2.,-4.,4.])
 def context(control):return dict(key=key,episode=episode,command_uid=uid,command=cmd,direction=t.zeros(n),signed_yaw=yaw,written_phase=t.full((n,),max(0,control-1)*.02),written_phase_valid=t.ones(n,dtype=t.bool))
 book.control=0;book.open(ids,context(0),True)
 for control in range(1,601):book.control=control;book.observe(context(control),dict(errors=[t.full((n,),.01),t.full((n,),.02),t.full((n,),.003)]))
 book.close(ids,'resample');uid+=1;book.open(ids,context(600),True)
 for control in range(601,604):book.control=control;book.observe(context(control),dict(errors=[t.full((n,),.01),t.full((n,),.02),t.full((n,),.003)]))
 reset_ids=ids[:3];book.close(reset_ids,'reset');episode[reset_ids]+=1;uid[reset_ids]+=1;book.open(reset_ids,context(603),True)
 book.close(ids[:2],'resample');uid[:2]+=1;book.open(ids[:2],context(603),True)
 out=B/'CPU_E2_FRESH_INSTANCE_PRODUCER';out.mkdir();summary=book.finish(out,prod.MODEL)
 total=lambda k:sum(r[k] for r in summary['profiles'])
 assert total('closed_instance_events')==15 and total('acted_instance_events')==10 and total('zero_control_instance_events')==5 and total('fully_observed_resample_to_resample_instance_events')==5 and total('acted_reset_ended_events')==3 and total('acted_window_end_events')==2
 assert total('complete_transition_instances_with_all_pre12_bins')==2 and total('complete_instance_population_controls')==3000
 for reason,cols in book.records:
  for count,first,last in zip(cols['population_controls'].tolist(),cols['first_acted_control'].tolist(),cols['last_acted_control'].tolist()):
   assert (first==last==-1) if count==0 else last>=first>=1
 prod.produce_typed_instance_JSONL_with_stream_SHA(out/'early_original_resample' if (out/'early_original_resample').exists() else (out/'early_original_resample'), 'E2_REAL_INITIAL_SAMPLED_COMMANDS_ACTUAL.jsonl',[]) if False else None
 initial=out/'early_original_resample';initial.mkdir();prod.produce_typed_instance_JSONL_with_stream_SHA(initial,'E2_REAL_INITIAL_SAMPLED_COMMANDS_ACTUAL.jsonl',({'env_id':i,'phase':0,'signed_yaw':float(yaw[i])} for i in range(n)))
 # Block all JSONL content reads while running the actual selected normalreader helper.
 pm=load('e2_producer_metadata_only_read_contract_v5');original_open=Path.open
 def no_content_read(path,mode='r',*a,**kw):
  if str(path).endswith('.jsonl') and 'r' in mode:raise AssertionError('JSONL content must not be read')
  return original_open(path,mode,*a,**kw)
 Path.open=no_content_read
 try:metadata=pm.metadata_indexes(B,out,prod.MODEL)
 finally:Path.open=original_open
 assert metadata['both_expected_producer_indexes_present'] and len(metadata['indexes'])==2 and not metadata['raw_JSONL_content_read']
 assert all(x['contents_not_read_rehashed_or_transferred'] for x in metadata['indexes'])
 code=ast.literal_eval(next(n.value for n in ast.parse((B/'E2_frozen_actual_receipts_readonly_CODE_v4.py').read_bytes()).body if isinstance(n,ast.Assign)));assert "360 if mode=='first' else 850" in code and 'nominal-time.time()<=900' in code and 'early_path.exists()' in code and "pm.metadata_indexes(J,F,MODEL)" in code
 put('ACTUAL_E2_V5_COMPLETE_SELECTED_SOURCE_CPU_AND_PRODUCER_CONTRACT_PROOF.json',dict(passed=True,scope='LOCAL fresh CPU/source only, target SDK/GPU/model still pending',local_torch=t.__version__,protected_original_runtime_model_asset_rows=len(protected),worker_inverse_SHA=H(base),original900_numerical_mean_loop_AST_equal=True,selected_hook_timing=timing,real_entry_CLI_learnhook=cli,worker_sup_first_normal_receipt_graph=graph,declared_import_closure=closure,no_learning_source_call_guard=guard,rejected=negative,actual_original_E2_method_lifecycle_fresh_CPU=lifecycle,actual_selected_constructor_API=api,command_instance_fresh_counts=dict(closed15=True,acted10=True,zero5=True,complete5=True,acted_reset3=True,acted_window2=True,complete_transition_all_pre12bins2=True),boundary_vs_first_actual_action_fields_tested=True,actual_JSONL_reader_metadata_only_under_content_read_block=metadata,no_old_PT_NPZ_raw_gz_or_SDK_host_GPU=True))
 print(json.dumps(dict(passed=True,protected_rows=len(protected),negative=len(negative),fresh_instance_counts=[15,10,5,5,3,2],target_GPU_pending=True)))
if __name__=='__main__':
 try:main()
 except BaseException:put('LOCAL_E2_V5_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_remote_or_old_model=True));raise
