from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
proof=json.loads((R/'SOURCE198_E0_FULLSTATE_LITERAL_JUMP_GO_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['negative_cases']==9
for p in N.glob('*.py'):ast.parse(p.read_bytes())
ast.parse((N/'remote198_CPU_and_native64_admission.txt').read_bytes())
rows=[]
for name in ('e0_jump198_task_protocol.py','prepare198_E0_72_source_once.py','test198_source_metadata_and_GO_CPU_once.py','run198_E0_JUMP72_400N50_worker.py','install198_E0_72_source_CPU_native64_admission_once.py','remote198_CPU_and_native64_admission.txt','PACKAGE198_MANIFEST.json'):
 p=N/name;rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)))
with (R/'SOURCE198_EARLIER_LOCAL_RG_OPTION_ERROR_RETAINED.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),original_error='rg: error parsing flag -E: grep config error: unknown encoding: rrorAction',cause='PowerShell -ErrorAction was mistakenly passed as an rg executable argument during bounded source-only NPZ caller lookup',source_only=True,model_raw_GPU_SDK_or_remote_calls=0,corrected_source_lookup_completed=True),f,indent=2)
request=dict(epoch=time.time(),status='FROZEN198_READY_FOR_ROOT_EXCLUSIVE_ADMISSION_LEASE_NOT_EXECUTED',files=rows,
 role='e0_72',job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_82_FUDAN_JUMP72_400N50_20261031v198/e0_72',
 worker_script='run198_E0_JUMP72_400N50_worker.py',python='/home/lc01/Zonglin Li/zonglin2/run-python.sh',
 selected_GPU='Fresh query in admission:168 preferred,c27 fallback; privateEX required; no PID query',
 private_lock_pattern='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_<selected_GPU_UUID>.lock',
 shared_validation_lock='/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock',
 original_E0_source='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89d/e0/adaptation/final_valid_update82.pt',
 original_E0_SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a',
 source_CPU_groups=4,GO_negative_cases=9,model_checkpoint_reads=0,remote_GPU_or_GO_calls=0,
 next_exclusive_entry=str(N/'install198_E0_72_source_CPU_native64_admission_once.py'),entry_SHA=H(N/'install198_E0_72_source_CPU_native64_admission_once.py'),
 required_argv='--root-lease-label ROOT197_EXCLUSIVE_ADMIT198_<explicit_root_id>',maximum_local_seconds=1300,
 target_native64_wait_seconds=900,new_source_JSON_AST_passed=True,actual_target72_admission_pending=True,
 produced_admission_file='ADMISSION198_ACTUAL.json',produced_actual_local_report='reports/ACTUAL198_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json',
 actual_train_start_requires_root_unified197_GO=True,no_child_owner_or_canonical_write=True)
with (R/'FROZEN198_COMPLETE_SOURCE_ROOT_LEASE_REQUEST.json').open('x',encoding='utf8') as f:json.dump(request,f,indent=2,ensure_ascii=False)
print(json.dumps(dict(frozen=True,entry_SHA=request['entry_SHA'],manifest_SHA=H(N/'PACKAGE198_MANIFEST.json'),max_seconds=1300,files=len(rows))))
