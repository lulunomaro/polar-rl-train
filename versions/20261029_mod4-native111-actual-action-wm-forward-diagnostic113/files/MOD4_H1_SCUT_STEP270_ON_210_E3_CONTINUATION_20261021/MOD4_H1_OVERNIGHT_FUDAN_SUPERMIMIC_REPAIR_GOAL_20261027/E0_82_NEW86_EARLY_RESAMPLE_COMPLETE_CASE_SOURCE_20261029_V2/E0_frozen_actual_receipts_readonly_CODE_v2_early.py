"""Only known fresh E0 V1 output receipts/text; no GPU/model/lock/account API."""
CODE=r'''
from pathlib import Path
import hashlib,json,os,time
J=Path(v['job']);assert str(J)=='/data/robemo/polar-rl-train/evaluation_runs/E0_ADAPTED82_EARLY_RESAMPLE_20261029v2/e0' and J.resolve()==J
MODEL='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a';GPU='GPU-90a66ae2-f536-7033-79c0-487536ae36d3'
F=J/'frozen_regression';mode=v['mode'];assert mode in ('first','terminal')
def read(p):return json.loads(p.read_bytes()) if p.exists() else None
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
sup=read(J/'OWN_FINITE_FROZEN_EVAL_SUPERVISOR_IDENTITY.json');assert sup==v['supervisor'] and sup['cwd']==str(J)
def state(row):
 if row is None:return dict(original_out=True,no_worker_identity_published=True)
 if row.get('initial_spawn_already_exited'):return dict(original_out=True,expected=row,initial_identity_unavailable=True,no_PID_query_without_creation=True)
 p=Path('/proc')/str(row['pid'])
 try:
  raw=(p/'stat').read_text();a=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));created=boot+int(a[19])/os.sysconf('SC_CLK_TCK')
 except FileNotFoundError:return dict(original_out=True,expected=row,reason='original PID absent')
 if created!=row['creation']:return dict(original_out=True,expected=row,reason='PID reused; replacement exe/argv NOT read')
 if a[0]=='Z':return dict(original_out=True,expected=row,state='Z',reason='nonexecuting original zombie; parent waited receipt is separate')
 actual=dict(pid=row['pid'],creation=created,exe=os.readlink(p/'exe'),argv=[os.fsdecode(x) for x in (p/'cmdline').read_bytes().split(bytes([0])) if x],cwd=os.readlink(p/'cwd'))
 assert actual==row,'Known original identity differs'
 return dict(original_out=False,expected=row,actual=actual,known_identity_exact=True,state=a[0])
def worker_identity():
 row=read(J/'OWN_E0_FROZEN_WORKER_EXACT_IDENTITY.json')
 if row is not None:
  if row.get('initial_spawn_already_exited'):
   assert row['worker_self_identity_required'];return row
  assert row['cwd']==str(J) and str(J/'evaluate_E0_adapted82_new86_frozen1000_once_v2_early.py') in row['argv']
  assert row['argv'][-2:]==['--job-root',str(J)]
 return row
def native_valid(rr,nn):
 return bool(rr and rr.get('passed') and rr.get('source_SHA')==MODEL and rr.get('Adam_step')==641200 and rr.get('stored_RSL_iteration')==31984 and rr.get('actual_constructor_algorithm_optimizer_LR')==.00038443359375000017 and nn and nn.get('passed') and nn.get('source_SHA')==MODEL and nn.get('controls')==24 and nn.get('physics_callbacks')==192 and nn.get('feedback_samples')==48 and nn.get('legs_queue_apply')==192 and nn.get('wheels_queue_apply')==192 and nn.get('trace_controls')==list(range(1,25)) and nn.get('RewardManager_calls')==24 and nn.get('RewardManager_dt_s')==.02 and nn.get('original_Adam641200_unchanged') is True)
def input_admission():
 assert H(J/'E0_NEW86_COMPLETE_INPUT_MANIFEST_V2.json')==v['manifest_SHA']
 installed=read(J/'E0_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json');assert installed['actual_postcopy_fullSHA_verified'] and installed['job_root']==str(J) and installed['manifest_SHA']==v['manifest_SHA']
 task=read(J/'FROZEN_CASE_TASK.json');cpu=read(J/'E0_TARGET_SOURCE_SDK_METADATA_ACTUAL.json');wait=read(J/'E0_NEW86_CPU_ORIGINAL_WAIT_PROOF.json')
 if task is None:return dict(actual_GPU_task_not_yet_published=True,CPU_metadata=cpu,CPU_wait=wait)
 assert task['kind']=='MOD4_E0_ADAPTED82_NEW86_EARLY_RESAMPLE_FROZEN_PROFILE_DOMAIN_V2' and task['source_SHA']==MODEL and task['worker_SHA']==v['worker_SHA'] and task['manifest_SHA']==v['manifest_SHA']
 assert task['controls']==1000 and task['warmup_controls']==100 and task['maximum_worker_seconds']==1680 and task['no_optimizer_steps'] and task['original_Adam']==641200 and task['original_LR']==.00038443359375000017
 assert task['actual_private_GPU_EX_held_by_parent'] and task['actual_private_parent_identity']==sup
 assert task['known72_readonly_authority']['passed_readonly_original72_finite_authority'] and task['known72_readonly_authority']['generation']=='MOD4_SINGLE_WRITER72_20261026'
 assert cpu['passed'] and cpu['source_SHA']==MODEL and cpu['worker_SHA']==v['worker_SHA'] and cpu['whole_CPU_witness_reused_without_PT_decode'] and cpu['model_loads_this_metadata_admission']==0 and cpu['versions']['tensordict']=='0.14.1'
 assert wait['passed'] and wait['actual_waited'] and wait['returncode']==0 and not wait['deadline_terminated'] and wait['report_SHA']==H(J/'E0_TARGET_SOURCE_SDK_METADATA_ACTUAL.json')
 assert task['actual_CPU_report_SHA']==H(J/'E0_TARGET_SOURCE_SDK_METADATA_ACTUAL.json') and task['actual_CPU_waited_proof_SHA']==H(J/'E0_NEW86_CPU_ORIGINAL_WAIT_PROOF.json')
 assert cpu['actual_target_CommandTerm_method_AST_passed'] and cpu['actual_target_method_CPU_lifecycle']['passed']
 assert task['early_observer_SHA']==cpu['actual_target_method_CPU_lifecycle_helper_SHA']==v['early_observer_SHA']
 resource=read(J/'FRESH_PRIVATE_HELD_UUID_ONLY_BEFORE_FROZEN_WORKER.json');row=[x.strip() for x in resource['GPU_line'].split(',')];assert row[0]==GPU and row[1]=='NVIDIA GeForce RTX 4090' and int(row[2])>15669 and int(row[3])<=30
 held=read(J/'OWN_PRIVATE86_EX_ACQUIRED_FOR_FROZEN_EVAL.json');assert held['supervisor']==sup
 return dict(actual_task_and_CPU_witness_and_private_resource_bound=True,authority_at_installation_readonly_not_current_C_claim=task['known72_readonly_authority'],resource_at_worker_admission=resource,target_metadata_is_not_GPU_proof=True)
early_path=F/'ACTUAL_E0_EARLY_POSTRESTORE_RESAMPLE_BEFORE_MEAN_ACTION.json'
restore=F/'ACTUAL_E0_82_CUDA_FULLRESTORE_BEFORE_MEAN_ACTION.json';native=F/'ACTUAL_NATIVE24_E0_40050_CLOCK_QUEUE.json';terminal=J/'FROZEN_E0_ORIGINAL_WAITED_TERMINAL_ACTUAL.json'
nominal=sup['creation']+1800
if mode=='terminal':assert nominal-time.time()<=900,'original remote supervisor1800 remaining<=900 gate closed'
limit=time.monotonic()+(360 if mode=='first' else 850)
while True:
 errors=(list(F.glob('*ORIGINAL_ERROR*.json'))+list(F.glob('*EXCEPTION_BEFORE_APP_CLOSE*.json'))) if F.exists() else []
 errors+=list(J.glob('*SUPERVISOR_ORIGINAL_ERROR*.json'));tt=read(terminal);worker=worker_identity();ss=state(sup);ww=state(worker)
 if mode=='first':
  if restore.exists() and native.exists() and early_path.exists() or errors or tt is not None or time.monotonic()>=limit:break
 else:
  if tt is not None and ss['original_out'] and ww['original_out'] or time.monotonic()>=limit:break
 time.sleep(1)
early_value=read(early_path)
admission=input_admission();rr=read(restore);nn=read(native);passed_native=native_valid(rr,nn) and not errors
settled=bool(tt and ss['original_out'] and ww['original_out'] and tt.get('private_EX_released') and (worker is None or tt.get('actual_worker_waited')))
if tt and worker is not None:assert tt['worker']==worker and tt['supervisor']==sup
paths=[J/n for n in ('E0_TARGET_SOURCE_SDK_METADATA_ACTUAL.json','E0_NEW86_CPU_ORIGINAL_WAIT_PROOF.json','FROZEN_CASE_TASK.json','FRESH_PRIVATE_HELD_UUID_ONLY_BEFORE_FROZEN_WORKER.json','OWN_PRIVATE86_EX_ACQUIRED_FOR_FROZEN_EVAL.json','FROZEN_E0_WORKER_COMPLETE_STDOUT_STDERR.log','FROZEN_E0_SUPERVISOR_COMPLETE_STDOUT_STDERR.log','FROZEN_E0_ORIGINAL_WAITED_TERMINAL_ACTUAL.json','FROZEN_E0_SUPERVISOR_EXIT_ACTUAL.json')]+[restore,native,early_path]+errors
if mode=='terminal':
 paths=[p for p in J.iterdir() if p.is_file() and p.suffix in ('.json','.txt','.log') and p.name not in ('E0_NEW86_COMPLETE_INPUT_MANIFEST_V2.json','E0_INSTALLED_BINARY_DEPENDENCIES_VERIFIED.json')]
 if F.exists():paths.extend(p for p in F.rglob('*') if p.is_file() and p.suffix in ('.json','.txt','.log'))
texts=[];integrity=[]
for p in sorted(set(paths)):
 if not p.exists():continue
 assert p.resolve().is_relative_to(J) and not p.is_symlink();before=p.stat();raw=p.read_bytes();after=p.stat();stable=(before.st_size,before.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
 texts.append(dict(path=str(p),relative=p.relative_to(J).as_posix(),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'),before_bytes=before.st_size,after_bytes=after.st_size,stable=stable,after_allownout_snapshot=settled))
 if settled and not stable:
  assert p.name=='omni.processlifetime.log','Other own fulltext changed after allout: '+str(p)
  fresh_before=p.stat();fresh=p.read_bytes();fresh_after=p.stat();assert (fresh_before.st_size,fresh_before.st_mtime_ns)==(fresh_after.st_size,fresh_after.st_mtime_ns)
  texts.append(dict(path=str(p),bytes=len(fresh),SHA=hashlib.sha256(fresh).hexdigest(),UTF8=fresh.decode('utf8'),exact_own_omni_one_fresh_snapshot=True,original_mismatch_bytes_and_manifest_preserved=True));integrity.append(dict(path=str(p),classification='authorized exact own omni single fresh snapshot'))
large=[]
jsonl_indexes=[]
if mode=='terminal' and F.exists():
 for index_path in sorted(F.rglob('*.jsonl.PRODUCER_INDEX_ACTUAL.json')):
  assert index_path.resolve().is_relative_to(F) and not index_path.is_symlink();producer=read(index_path);p=Path(producer['path']);assert p.resolve().is_relative_to(F) and p.suffix=='.jsonl' and not p.is_symlink()
  assert producer['source_SHA']==MODEL and producer['producer_stream_SHA_no_reread'] and producer['collector_mode']=='producer_path_bytes_SHA_metadata_only' and not producer['content_transfer_default'] and len(producer['SHA'])==64
  actual=p.stat();assert actual.st_size==producer['bytes'];jsonl_indexes.append(producer);large.append(dict(path=str(p),bytes=actual.st_size,SHA=producer['SHA'],SHA_scope='original_producer_stream_not_reader_rehash',rows=producer['rows'],producer_index=str(index_path),contents_not_read_rehashed_or_transferred=True))

if mode=='terminal' and F.exists():
 for p in sorted(F.rglob('*')):
  if not p.is_file() or p.suffix not in ('.npz','.pt','.npy','.usd','.zip','.gz'):continue
  assert p.resolve().is_relative_to(J) and not p.is_symlink();large.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,producer_SHA_unavailable_not_recomputed=True,contents_not_read_rehashed_or_transferred=True))
def full_coverage(passed_execution,result):
 return bool(passed_execution and result and result.get('controls')==1000 and result.get('requested_controls')==1000 and result.get('warmup_controls')==100 and result.get('steady_controls')==900 and not result.get('wall_time_limited') and result.get('all17_Adam_steps')==641200 and result.get('actual_LR_unchanged')==.00038443359375000017 and result.get('core_actor_critic_STD_norm_optimizer_literal_unchanged'))
result=tt.get('result') if tt else None;passed_execution=bool(settled and tt.get('passed_frozen_execution') and passed_native and not errors);full=full_coverage(passed_execution,result)
early_pass=bool(early_value and early_value['source_SHA']==MODEL and early_value['observer_SHA']==v['early_observer_SHA'] and early_value['actual_original_postrestore_event_adopted'] and not early_value['initial_left_censored'] and early_value['observed_ids_count']==20000 and early_value['actual_phase_zero'] and early_value['actual_physics_tick']==0 and not early_value['diagnostic_errors'])
print(json.dumps(dict(early_original_resample=early_value,passed_actual_early_observation_and_adoption=early_pass,typed_JSONL_producer_indexes_metadata_only=jsonl_indexes,epoch=time.time(),purpose=mode,source_SHA=MODEL,original_supervisor1800_nominal_epoch=nominal,original_worker1680_maximum=True,passed_first_actual_E0_CUDA_fullrestore_native24_queue=passed_native,admission_readonly_evidence=admission,supervisor_state=ss,worker_state=ww,restore=rr,native24=nn,original_terminal=tt,original_errors=[dict(path=str(p),value=read(p)) for p in dict.fromkeys(errors)],original_terminal_and_allownout_proven=settled,passed_original_frozen_execution=passed_execution,requested1000_controls_100warm_900steady_complete=full,complete_original_own_stage_UTF8=texts,large_artifact_metadata_only=large,integrity=integrity,no_model_raw_NPZ_decode_download_or_rehash=True,no_actor_GPUquery_lock_or_Cwrite=True,metadata_API_synthetic_not_GPU_qualification=True,skill_graduation=False,complete_WM_dataset=False,partial_or_error_not_promoted=True)))
'''
