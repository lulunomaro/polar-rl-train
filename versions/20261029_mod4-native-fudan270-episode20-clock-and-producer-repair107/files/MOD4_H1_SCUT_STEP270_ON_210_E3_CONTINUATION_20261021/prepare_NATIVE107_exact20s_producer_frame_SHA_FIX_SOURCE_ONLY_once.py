from pathlib import Path
import ast,copy,hashlib,json,os,runpy,shutil,time,traceback
T=Path(__file__).resolve().parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';A=T/'MOD4_H1_FUDAN270_EPISODE20_RESOURCE_V106_20261029';N=T/'MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029';R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def rep(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def assign(s,name,value):
 x=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in x.targets));lines=s.splitlines(keepends=True);return ''.join(lines[:x.lineno-1])+name+'='+repr(value)+'\n'+''.join(lines[x.end_lineno:])
CPU='''from pathlib import Path
import ast,hashlib,importlib.metadata,importlib.util,json,sys,time,psutil
B=Path(__file__).resolve().parent;J=B/'job0';sys.path[:0]=[str(B),str(B/'source')]
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 from native_flat90_source_guard_v1 import check_payload
 from native88C_to_flat_migration_v1 import KIND,FLAT_OBJECTIVE_CONTRACT
 p=psutil.Process()
 with (J/'FLAT90_SOURCE_CPU_STARTED_ACTUAL.json').open('x') as f:json.dump(dict(pid=p.pid,creation=p.create_time(),argv=p.cmdline(),exe=p.exe(),cwd=p.cwd(),before_model_load=True,models_not_loaded_this_metadata_only_purpose=True),f,indent=2)
 checked=check_payload(B,verify_model_bytes=False);task=checked['task'];binding=json.loads((B/'source/PRODUCER_FRAME_SHA_FIX_BINDING_ACTUAL.json').read_bytes())
 raw=(B/'source/ORIGINAL106_FULLSTATE_CPU_REPORT_ACTUAL.json').read_bytes();original=json.loads(raw);pr=(B/'source/ORIGINAL106_CPU_WAITED_PROOF_ACTUAL.json').read_bytes();proof=json.loads(pr)
 assert hashlib.sha256(raw).hexdigest()==binding['original_CPU_SHA'] and hashlib.sha256(pr).hexdigest()==binding['original_waited_SHA'] and proof['actual_waited'] and proof['returncode']==0 and proof['report_SHA']==binding['original_CPU_SHA']
 assert original['passed'] and original['source_SHA']==task['source_SHA'] and original['source_progress']==task['source_progress'] and original['fudan_step_task']==task['fudan_step_task'] and original['episode_clock']==task['episode_clock'] and original['physical_initial_seed']==task['native_seed'] and original['kind']==KIND
 entry=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';new=entry.read_bytes();assert H(entry)==binding['new_entry_SHA'] and hashlib.sha256(new.replace(binding['correct_literal'].encode(),binding['original_literal'].encode())).hexdigest()==binding['original_entry_SHA']
 values={x.arg:x.value.value for x in ast.walk(ast.parse(new)) if isinstance(x,ast.keyword) and x.arg in ('private_phase_frame_source_SHA','real_callback_counter_source_SHA','source_reference_artifact_SHA') and isinstance(x.value,ast.Constant)}
 assert values['private_phase_frame_source_SHA']==FLAT_OBJECTIVE_CONTRACT['private_phase_frame_source_SHA']==H(B/'source/private_phase_frame_v1.py')
 assert values['real_callback_counter_source_SHA']==FLAT_OBJECTIVE_CONTRACT['real_callback_counter_source_SHA']==H(B/'h1_step270_sdk_runtime_candidate.py')
 from native88C_to_flat_migration_v1 import SOURCE_REFERENCE_SHA
 assert values['source_reference_artifact_SHA']==SOURCE_REFERENCE_SHA
 sdk=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)));rsl=Path(next(iter(importlib.util.find_spec('rsl_rl').submodule_search_locations)));source=json.loads((B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json').read_bytes());versions={n:importlib.metadata.version(n) for n in ('isaaclab','rsl-rl-lib','torch')};assert versions==source['expected_installed_versions'] and H(sdk/'utils/math.py')==source['expected_actual_SDK_math_SHA']
 for row in source['expected_actual_RSL_sources']:assert H(rsl/row['relative'])==row['SHA']
 for rel,SHA in binding['unchanged_original_Python_sources'].items():assert H(B/rel)==SHA
 value=dict(original,payload_manifest_SHA=checked['manifest_SHA'],source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),worker_SHA=H(B/'h1_native_flat90_worker_v1.py'),initial_loads=dict(selected104source=0,normal86=0),original106_initial_loads=original['initial_loads'],original106_fullstate_CPU_SHA=binding['original_CPU_SHA'],original106_waited_proof_SHA=binding['original_waited_SHA'],source107_metadata_only_producer_frame_SHA_fix_passed=True,source107_no_saved_weights_norms_opts_redecoded=True,source107_actual_SDK_sources_rechecked=True,producer_three_source_literals_bound=True)
 with (J/'FLAT90_SOURCE_SDK_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
 print(json.dumps(dict(passed=True,kind=KIND,metadata_only_extension_no_model_read=True)))
if __name__=='__main__':main()
'''
def main():
 assert not N.exists();R.mkdir(parents=True);closed=read(A/'reports/ACTUAL106_ORIGINAL_EARLY_FAILURE_ALL_COST_ALLOUT_FULLTEXTS_RETURNED_ACTUAL.json');assert closed['canonical_None'] and closed['all_original_own_processes_out'] and closed['original_private_shared_locks_free']
 prep=read(A/'reports/TWO106_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json');actual=read(A/'reports/TWO106_V3_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json')
 for mode,spec in prep['payloads'].items():
  old=Path(spec['payload']);B=N/'payloads'/mode;B.mkdir(parents=True);manifest=read(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  for row in manifest['files']:
   src=old/row['relative'];dst=B/row['relative'];dst.parent.mkdir(parents=True,exist_ok=True)
   if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dst)
   else:shutil.copy2(src,dst)
  p=B/'source/native_flat5cm_training_entry_candidate_v4_typed_producer.py';oldbytes=p.read_bytes();oldliteral="private_phase_frame_source_SHA='196063b60aa4fd956b97bd4db427aa44aa7a9ea0a8b060e68de57b849796be70'";newliteral='private_phase_frame_source_SHA='+repr(H(B/'source/private_phase_frame_v1.py'));s=rep(p.read_text('utf8'),oldliteral,newliteral);assert s.replace(newliteral,oldliteral)==oldbytes.decode();write(p,s)
  proof=actual['results'][mode];raw=json.dumps(proof['value'],indent=2,allow_nan=False);wait=json.dumps(proof['proof'],indent=2,allow_nan=False);assert hashlib.sha256(raw.encode()).hexdigest()==proof['proof']['report_SHA'] and hashlib.sha256(wait.encode()).hexdigest()==proof['proof_SHA']
  write(B/'source/ORIGINAL106_FULLSTATE_CPU_REPORT_ACTUAL.json',raw);write(B/'source/ORIGINAL106_CPU_WAITED_PROOF_ACTUAL.json',wait)
  unchanged={r['relative']:r['SHA'] for r in manifest['files'] if r['relative'].endswith('.py') and r['relative'] not in ('source/native_flat5cm_training_entry_candidate_v4_typed_producer.py','target_native_flat90_source_sdk_CPU_once.py')}
  put(B/'source/PRODUCER_FRAME_SHA_FIX_BINDING_ACTUAL.json',dict(original_CPU_SHA=proof['proof']['report_SHA'],original_waited_SHA=proof['proof_SHA'],original_entry_SHA=hashlib.sha256(oldbytes).hexdigest(),new_entry_SHA=H(p),original_literal=oldliteral,correct_literal=newliteral,unchanged_original_Python_sources=unchanged))
  write(B/'target_native_flat90_source_sdk_CPU_once.py',CPU);ast.parse(CPU)
  c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')};c['source107_metadata_only_frame_producer_fix']=True;write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2))
  task=spec['task'];task['id']=task['id'].replace('106','107');task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
  oldrows={r['relative']:r for r in manifest['files']};rows=[]
  for p in sorted(B.rglob('*')):
   if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
   rel=p.relative_to(B).as_posix();row=oldrows[rel] if p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip') else dict(relative=rel,bytes=p.stat().st_size,SHA=H(p));rows.append(row)
  manifest['files']=rows;write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(manifest,indent=2));spec.update(payload=str(B),job_root=spec['job_root'].replace('2610v106','2610v107'),old100_job_root=spec['job_root'],manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'),source106_original_CPU_SHA=proof['proof']['report_SHA'])
 put(R/'TWO107_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json',prep)
 # New exact metadata-only extension installer with original failed106 closure.
 p=T/'MOD4_H1_FLAT20_NATIVE_PRODUCER_FIX_RESOURCE_V101_20261028/install_two101_previous_owner_path_corrected_metadata_CPU_v2_once.py';s=p.read_text('utf8');tree=ast.parse(s);pre=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PRE' for t in x.targets))
 for a,b in [('524081.4115035534',repr(closed['closing_remaining_snapshot'])),('609931','629927'),('1793190660.79','1793213048.42'),('216.67591309547424',repr(closed['original_fee_seconds'])),('106.82035231590271',repr(closed['original_fee_by_slot']['h1'])),('109.85556077957153',repr(closed['original_fee_by_slot']['h1_seed28']))]:pre=pre.replace(a,b)
 pre=pre.replace("--query-gpu=uuid,name,memory.free'","--query-gpu=uuid,name,memory.free,utilization.gpu'").replace(' and gpu not in apps',' and int(line[3])<=30')
 s=assign(s,'PRE',pre);s=s.replace('TWO100_TARGET20_TWO_NATIVE_ORIGINAL_OWNER_SOURCE_V1/reports/TWO100_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json','TWO106_FUDAN270_20S_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1/reports/TWO106_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json').replace('TWO101_EXACT_PRODUCER_REFERENCE_FIX_PAYLOADS_PREPARED_ACTUAL.json','TWO107_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json').replace('TWO101_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json','TWO107_V3_ACTUAL_TWO_SOURCE_SDK_CPU_RETURNED_ACTUAL.json').replace('NATIVE101_','NATIVE107_V3_').replace('TWO101_','TWO107_');ast.parse(s);write(N/'install_TWO107_exact_producer_frame_metadata_extension_CPU_UNUSED_once.py',s)
 # Source CPU/controller generator uses the same validated method106 contracts.
 s=(A/'prepare_TWO106_actual20s_CPU_bound_original_writer_and_readers_SOURCE_ONLY_once.py').read_text('utf8').replace('TWO106','TWO107').replace('NATIVE106_V3','NATIVE107_V3').replace('MOD4_H1_FUDAN270_EPISODE20_RESOURCE_V106_20261029',N.name).replace('MOD4_TWO106_FUDAN270_EPISODE20_2610v106','MOD4_TWO107_FUDAN270_EPISODE20_2610v107').replace('expected_closed_remaining=509633.3206150532','expected_closed_remaining='+repr(closed['closing_remaining_snapshot']))
 # Its owner source is unchanged104, so the activation derivation must also
 # route the original104 report names to NEW107.
 s=s.replace(".replace('TWO104','TWO106')",".replace('TWO104','TWO107')")
 # Reference task/CPU kind stay106: the sole learning-code delta is its literal.
 ast.parse(s);write(N/'prepare_TWO107_actual_CPU_original_writer_and_readers_SOURCE_ONLY_once.py',s)
 put(R/'FROZEN_UNUSED_TWO107_EXACT_PRODUCER_FIX_AND_EXTENSION_INDEX.json',dict(frozen=True,unused=True,epoch=time.time(),only_runtime_entry_change='producer.private_phase_frame_source_SHA updated to actual4096stride20s source SHA',physical_reward_learner_model_normalizer_optimizer_and20s_clock_unchanged=True,source106_original_fullCPU_and_original_false_preserved=True,no_CPU_weight_reload_or_GO_yet=True,entries=[dict(path=str(p),SHA=H(p),bytes=p.stat().st_size) for p in N.glob('*.py')]))
 print(json.dumps(dict(prepared107=True,exact_runtime_entry_literal_fix=True,fullstate_model_loads=0,no_GO=True)))
if __name__=='__main__':
 try:main()
 except BaseException:
  R.mkdir(parents=True,exist_ok=True);put(R/('PREPARE107_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_remote=True));raise
