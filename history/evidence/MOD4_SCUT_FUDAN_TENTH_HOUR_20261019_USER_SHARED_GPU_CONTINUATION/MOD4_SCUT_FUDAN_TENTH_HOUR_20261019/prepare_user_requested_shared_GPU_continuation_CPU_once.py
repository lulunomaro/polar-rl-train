"""Apply the user's explicit GPU-sharing instruction to unused admission code only."""
from pathlib import Path
import ast,copy,hashlib,json,time
B=Path(__file__).resolve().parent;R=B/'reports'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as stream:json.dump(value,stream,ensure_ascii=False,indent=2)
assert not (R/'THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json').exists()
assert not (R/'USER_SHARED_GPU_CONTINUATION_CPU_PREPARED_ACTUAL.json').exists()
prior=R/'THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json';p=json.loads(prior.read_bytes());assert p['passed']
put('LATEST_USER_IGNORE_OCCUPANT_START_TRAINING_INSTRUCTION_ACTUAL.json',dict(epoch=time.time(),user_text='不用管占用的进程，你直接开始训练就行',scope='Permit H1 to share its assigned GPU with the observed occupant; do not signal, inspect identity again, stop, modify or delete anything belonging to that process. Retain original resource memory, disk, locks, source, save and accounting guards.',unused_next_namespace='T3sf10_1910v15',no_recipe_PPO_reward_LR_STD_physics_or_budget_change=True))
guard="assert not any(spec['GPU_UUID'] in x for x in compute.splitlines())"
newguard="assert (spec['key']=='h1' and spec.get('human_explicit_GPU_sharing') is True) or not any(spec['GPU_UUID'] in x for x in compute.splitlines())"
root=Path(p['payloads']['h1']);q=root/'three_real_gpu_resource_v1.py';old=q.read_text('utf8');oldSHA=H(q);assert old.count(guard)==1
new=old.replace(guard,newguard).replace('compute_snapshot=compute,GPU_line=line','compute_snapshot=compute,human_explicit_GPU_sharing=bool(spec.get(\'human_explicit_GPU_sharing\')),other_processes_untouched=True,GPU_line=line')
normalized=new.replace(newguard,guard).replace("compute_snapshot=compute,human_explicit_GPU_sharing=bool(spec.get('human_explicit_GPU_sharing')),other_processes_untouched=True,GPU_line=line",'compute_snapshot=compute,GPU_line=line')
assert ast.dump(ast.parse(normalized))==ast.dump(ast.parse(old))
for key in ('actual_private_GPU_fcntl_acquired','LOCK_EX|fcntl.LOCK_NB',"int(line.split(',')[-1])>7000",'available>8*1024**3','free>25*1024**3'):assert key in new
q.write_text(new,'utf8')
mf=root/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';m=json.loads(mf.read_bytes());row=next(x for x in m['files'] if x['relative']=='three_real_gpu_resource_v1.py');assert row['SHA']==oldSHA;row.update(bytes=q.stat().st_size,SHA=H(q));mf.write_text(json.dumps(m,indent=2),'utf8')
p['specs']['h1'].update(human_explicit_GPU_sharing=True,manifest_SHA=H(mf));p.update(epoch=time.time(),human_explicit_shared_H1_GPU_admission_only=True,original_prepared_report_SHA=H(prior),original_three_expert_one_writer_contract_unchanged=True)
put('THREE_NEXT_CLOSED_SOURCES_USER_SHARED_GPU_CPU_PREPARED_ACTUAL.json',p)
src=B/'deploy_three_next_closed_source_hours_once.py';s=src.read_text('utf8');assert s.count(guard)==1
s=s.replace(guard,newguard)
s=s.replace(";assert psutil.virtual_memory().available>8*1024**3", ";GPU_line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode().splitlines() if spec['GPU_UUID'] in x);assert int(GPU_line.split(',')[-1])>7000;assert psutil.virtual_memory().available>8*1024**3")
s=s.replace('compute_snapshot=compute,immutable_same_manifest_files_copied','compute_snapshot=compute,GPU_line=GPU_line,human_explicit_GPU_sharing=bool(spec.get(\'human_explicit_GPU_sharing\')),other_processes_untouched=True,immutable_same_manifest_files_copied')
s=s.replace('THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json','THREE_NEXT_CLOSED_SOURCES_USER_SHARED_GPU_CPU_PREPARED_ACTUAL.json')
ast.parse(s)
dest=B/'deploy_three_next_closed_source_hours_user_shared_H1_GPU_V2_once.py'
with dest.open('x',encoding='utf8',newline='\n') as stream:stream.write(s)
put('USER_SHARED_GPU_CONTINUATION_CPU_PREPARED_ACTUAL.json',dict(epoch=time.time(),passed=True,source_preparer_not_replayed=True,previous_resource_source_SHA=oldSHA,new_resource_source_SHA=H(q),admission_change_only_H1_explicit_sharing=True,all_other_resource_source_AST_exact=True,original_free_GPU_MiB_guard=7000,original_RAM_GiB_guard=8,original_disk_GiB_guard=25,original_private_shared_and_account_locks_retained=True,source_PPO_runtime_reward_assets_and_accounting_unchanged=True,source_full_CPU_and33negative_cases_retained=True,new_deployer=dict(path=str(dest),SHA=H(dest)),old_prepared_and_original_deployer_retained=True,no_remote_GPU_Task_native_or_account_write=True))
print(json.dumps(dict(shared_H1_GPU_prepared=True,Adam={k:v['source_Adamstep'] for k,v in p['specs'].items()},original_memory_locks_save_and_account_guards=True)))
