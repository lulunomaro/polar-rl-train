from pathlib import Path
import ast,copy,hashlib,json,os,shutil,time,traceback
O=Path(__file__).resolve().parent;T=O.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';N=T/'MOD4_H1_FLAT20_NATIVE_PRODUCER_FIX_RESOURCE_V101_20261028'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def read(p):return json.loads(Path(p).read_bytes())
def main():
 assert not N.exists();N.mkdir();R=N/'reports';R.mkdir();(N/'payloads').mkdir();prep=read(O/'reports/TWO100_TARGET20_EXACT_QUALIFIED99_PAYLOADS_PREPARED_V2_ACTUAL.json');actual=read(O/'reports/TWO100_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json');closed=read(O/'reports/ACTUAL100_ORIGINAL_EARLY_FAILURE_ALL_COST_ALLOUT_FULLTEXTS_RETURNED_ACTUAL.json');assert closed['canonical_None'] and closed['all_original_own_processes_out'] and closed['original_private_shared_locks_free']
 results={};wrong='b4d801a47b92a0d63378df0cea15e8c736fe489c2fd37a63399a1a2ed3d00502';correct='8050fd4a0accd8b329fedd1570a2dc525a97e96fb3a6b17a5b5f25733c2a6d0d'
 for mode,row0 in prep['payloads'].items():
  row=copy.deepcopy(row0);old=Path(row['payload']);B=N/'payloads'/mode;B.mkdir();m=read(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');prior={x['relative']:x for x in m['files']}
  for x in m['files']:
   p=old/x['relative'];dest=B/x['relative'];dest.parent.mkdir(parents=True,exist_ok=True)
   if p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(p,dest)
   else:shutil.copy2(p,dest)
  entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';before=entry.read_bytes();needle=("source_reference_artifact_SHA='"+wrong+"'").encode();replacement=("source_reference_artifact_SHA='"+correct+"'").encode();assert before.count(needle)==1;after=before.replace(needle,replacement);entry.write_bytes(after);assert after.replace(replacement,needle)==before
  (R/(mode+'_ORIGINAL100_ENTRY_BEFORE_PRODUCER_LABEL_FIX.py.txt')).write_bytes(before)
  oldcpu=actual['results'][mode];raw=json.dumps(oldcpu['value'],indent=2,allow_nan=False).encode();assert hashlib.sha256(raw).hexdigest()==oldcpu['proof']['report_SHA'];proof=json.dumps(oldcpu['proof'],indent=2,allow_nan=False).encode();assert hashlib.sha256(proof).hexdigest()==oldcpu['proof_SHA']
  (B/'source/ORIGINAL100_FULLSTATE_CPU_REPORT_ACTUAL.json').write_bytes(raw);(B/'source/ORIGINAL100_CPU_WAITED_PROOF_ACTUAL.json').write_bytes(proof)
  oldreader=(B/'target_native_flat90_source_sdk_CPU_once.py').read_bytes();(R/(mode+'_ORIGINAL100_FULLSTATE_CPU_READER_NOT_RERUN.py.txt')).write_bytes(oldreader)
  ext='''from pathlib import Path
import ast,hashlib,importlib.metadata,importlib.util,json,sys,time
B=Path(__file__).resolve().parent;J=B/'job0';sys.path[:0]=[str(B),str(B/'source')]
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 from native_flat90_source_guard_v1 import check_payload
 from native88C_to_flat_migration_v1 import SOURCE_REFERENCE_SHA,KIND
 import psutil
 p=psutil.Process()
 with (J/'FLAT90_SOURCE_CPU_STARTED_ACTUAL.json').open('x') as f:json.dump(dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),exe=p.exe(),cwd=p.cwd(),before_model_load=True,models_not_loaded_this_metadata_only_purpose=True),f,indent=2)
 checked=check_payload(B,verify_model_bytes=False);task=checked['task'];binding=json.loads((B/'source/PRODUCER_LABEL_FIX_BINDING_ACTUAL.json').read_bytes())
 raw=(B/'source/ORIGINAL100_FULLSTATE_CPU_REPORT_ACTUAL.json').read_bytes();original=json.loads(raw);proofraw=(B/'source/ORIGINAL100_CPU_WAITED_PROOF_ACTUAL.json').read_bytes();proof=json.loads(proofraw)
 assert hashlib.sha256(raw).hexdigest()==binding['original_CPU_SHA'] and hashlib.sha256(proofraw).hexdigest()==binding['original_waited_SHA'] and proof['actual_waited'] and proof['returncode']==0 and proof['report_SHA']==binding['original_CPU_SHA']
 assert original['passed'] and original['source_SHA']==task['source_SHA'] and original['source_progress']==task['source_progress'] and original['flat_jump_target_m']==task['flat_jump_target_m']==.20 and original['physical_initial_seed']==task['native_seed'] and original['kind']==KIND
 entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';new=entry.read_bytes();assert H(entry)==binding['new_entry_SHA'] and hashlib.sha256(new.replace(binding['correct_literal'].encode(),binding['original_literal'].encode())).hexdigest()==binding['original_entry_SHA']
 tree=ast.parse(new);values=[x.value.value for x in ast.walk(tree) if isinstance(x,ast.keyword) and x.arg=='source_reference_artifact_SHA' and isinstance(x.value,ast.Constant)];assert values==[SOURCE_REFERENCE_SHA]==[binding['correct_source_reference_SHA']]
 sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)));rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)));source=json.loads((B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json').read_bytes());versions={n:importlib.metadata.version(n) for n in ('isaaclab','rsl-rl-lib','torch')};assert versions==source['expected_installed_versions']
 assert H(sdk/'utils/math.py')==source['expected_actual_SDK_math_SHA']
 for row in source['expected_actual_RSL_sources']:assert H(rsl/row['relative'])==row['SHA']
 for rel,SHA in binding['unchanged_original_Python_sources'].items():assert H(B/rel)==SHA
 value=dict(original,payload_manifest_SHA=checked['manifest_SHA'],source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),worker_SHA=H(B/'h1_native_flat90_worker_v1.py'),initial_loads=dict(native99=0,normal86=0),source100_original_initial_loads=original['initial_loads'],source100_original_fullstate_CPU_SHA=binding['original_CPU_SHA'],source100_original_waited_proof_SHA=binding['original_waited_SHA'],source101_metadata_only_producer_reference_fix_passed=True,source101_no_saved_weights_or_norms_or_opts_redecoded=True,source101_actual_SDK_sources_rechecked=True,producer_source_reference_SHA=SOURCE_REFERENCE_SHA)
 with (J/'FLAT90_SOURCE_SDK_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
 print(json.dumps(dict(passed=True,kind=KIND,metadata_only_extension_no_model_read=True)))
if __name__=='__main__':main()
'''
  write(B/'target_native_flat90_source_sdk_CPU_once.py',ext)
  binding=dict(original_CPU_SHA=oldcpu['proof']['report_SHA'],original_waited_SHA=oldcpu['proof_SHA'],original_entry_SHA=hashlib.sha256(before).hexdigest(),new_entry_SHA=H(entry),correct_source_reference_SHA=correct,original_literal=needle.decode(),correct_literal=replacement.decode(),unchanged_original_Python_sources={rel:x['SHA'] for rel,x in prior.items() if rel.endswith('.py') and rel not in ('source/native_flat5cm_training_entry_candidate_v4_typed_producer.py','target_native_flat90_source_sdk_CPU_once.py')},original100_failed_before_any_control_or_new_optimizer=True)
  write(B/'source/PRODUCER_LABEL_FIX_BINDING_ACTUAL.json',json.dumps(binding,indent=2))
  c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c['source101_metadata_only_producer_fix']=binding;c['small_evidence_pins'].update({'source/ORIGINAL100_FULLSTATE_CPU_REPORT_ACTUAL.json':hashlib.sha256(raw).hexdigest(),'source/ORIGINAL100_CPU_WAITED_PROOF_ACTUAL.json':hashlib.sha256(proof).hexdigest(),'source/PRODUCER_LABEL_FIX_BINDING_ACTUAL.json':H(B/'source/PRODUCER_LABEL_FIX_BINDING_ACTUAL.json')});c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')};write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2))
  task=read(B/'job0/TASK.json');task.update(id='MOD4_H1_FLAT20_NATIVE101_PRODUCER_FIX_'+mode,flat_source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),source101_metadata_only_producer_reference_fix=True);write(B/'job0/TASK.json',json.dumps(task,indent=2))
  rows=[]
  for p in sorted(B.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(B).as_posix();x=prior[rel] if p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip') else dict(relative=rel,bytes=p.stat().st_size,SHA=H(p));rows.append(x)
  m.update(files=rows);write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2))
  for p in B.rglob('*.py'):ast.parse(p.read_bytes())
  row.update(task=task,payload=str(B),job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT20_NATIVE_2610v101/'+mode,old100_job_root=row0['job_root'],manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),source100_original_CPU_SHA=oldcpu['proof']['report_SHA'],source100_original_waited_SHA=oldcpu['proof_SHA']);results[mode]=row
 with (R/'TWO101_EXACT_PRODUCER_REFERENCE_FIX_PAYLOADS_PREPARED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,epoch=time.time(),payloads=results,original100_fee=closed['original_fee_seconds'],expected_closed_remaining=closed['closing_remaining_snapshot'],runtime_entry_only_source_reference_label_corrected=True,source100_fullstate_CPU_reused_not_reloaded=True,no_new_GPU_or_GO=True),f,indent=2)
 print(json.dumps(dict(prepared=True,namespace101=str(N),runtime_changed_only_producer_source_reference=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  if (N/'reports').is_dir():
   with (N/'reports/PREPARE101_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(error=traceback.format_exc(),no_model_read_or_remote=True),f,indent=2)
  raise
