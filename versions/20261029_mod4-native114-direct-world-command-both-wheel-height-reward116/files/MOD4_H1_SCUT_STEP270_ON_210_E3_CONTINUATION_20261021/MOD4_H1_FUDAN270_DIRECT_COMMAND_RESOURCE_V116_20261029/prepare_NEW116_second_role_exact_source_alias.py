"""Second genuine4096 physical role; same qualified114 fullstate, savedlearning27."""
from pathlib import Path
import ast,copy,hashlib,json,os,shutil,sys,time
N=Path(__file__).resolve().parent;R=N/'reports';A=N/'payloads/seed27';B=N/'payloads/seed28'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_text(v,encoding='utf8',newline='\n')
def put(p,v):
    with Path(p).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
assert not B.exists();B.mkdir(parents=True)
prep=read(R/'NEW116_ONE_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json');m=read(A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
for row in m['files']:
    src=A/row['relative'];dst=B/row['relative'];dst.parent.mkdir(parents=True,exist_ok=True)
    if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dst)
    else:shutil.copy2(src,dst)
task=copy.deepcopy(prep['task']);task.update(id='MOD4_H1_DIRECT_COMMAND116_seed28',logical_slot='h1_seed28',GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',seed=28,native_seed=28)
g=(A/'native_flat90_source_guard_v1.py').read_text(encoding='utf8');assert g.count("task.get('logical_slot')=='h1'")==1
g=g.replace("task.get('logical_slot')=='h1'","task.get('logical_slot')=='h1_seed28'").replace("'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'","'GPU-16828f91-2b45-b646-8dc0-9481138e2842'")
write(B/'native_flat90_source_guard_v1.py',g)
c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')};write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2))
task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
new=[]
for row in m['files']:
    p=B/row['relative']
    new.append(row if p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip') else dict(relative=row['relative'],bytes=p.stat().st_size,SHA=H(p)))
m['files']=new;write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2))
spec=copy.deepcopy(prep);spec.update(epoch=time.time(),payload=str(B),task=task,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_DIRECT_COMMAND_2610v116/seed28',GPU_UUID=task['GPU_UUID'],logical_slot='h1_seed28',manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'))
put(R/'NEW116_SEED28_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json',spec)
sys.path[:0]=[str(B),str(B/'source')]
from native_flat90_source_guard_v1 import validate_task_go
go=copy.deepcopy(task);go.update(payload_manifest_SHA=spec['manifest_SHA'],num_envs=4096,max_parent_seconds=3900,exit_headroom_seconds=300)
validate_task_go(task,go,spec['manifest_SHA']);neg=[]
for field in ('native_seed','native_learning_seed','logical_slot','source_SHA'):
    bad=copy.deepcopy(go);bad[field]='WRONG'
    try:validate_task_go(task,bad,spec['manifest_SHA'])
    except (ValueError,AssertionError,TypeError,KeyError):neg.append(field)
    else:raise AssertionError('unbound physical role '+field)
bad=copy.deepcopy(task);bad['GPU_UUID']='WRONG'
try:validate_task_go(bad,go,spec['manifest_SHA'])
except (ValueError,AssertionError,TypeError,KeyError):neg.append('Task.GPU_UUID')
else:raise AssertionError('unbound actual consumed Task.GPU_UUID')
proof=R/'SOURCE116_SEED28_ALIAS_TASK_GO_CPU_ACTUAL.json';put(proof,dict(passed=True,epoch=time.time(),negative_fields=neg,physical28_savedlearning27=True,all_own_reward_and_WM_sources_identical_to_role27=True,no_models_or_binary_reads=True,role27_math_ownFK_proof_SHA=H(R/'SOURCE116_PREINSTALL_TASK_GO_OWN_FK_COUNTEREXAMPLE_CPU_ACTUAL.json')))
installer=(N/'install_NEW116_one_actual_target_sourceSDK_fullstate_CPU_UNUSED_once_v2.py').read_text(encoding='utf8')
mapping=[('NEW116_ONE_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json','NEW116_SEED28_TYPED_REWARD_PAYLOAD_PREPARED_SOURCE_ONLY.json'),('SOURCE116_PREINSTALL_TASK_GO_OWN_FK_COUNTEREXAMPLE_CPU_ACTUAL.json','SOURCE116_SEED28_ALIAS_TASK_GO_CPU_ACTUAL.json'),('FROZEN_NEW116_ONE_TARGET_CPU_ENTRY_SOURCE_INDEX_V2.json','FROZEN_NEW116_SEED28_TARGET_CPU_ENTRY_SOURCE_INDEX.json'),('NEW116_ONE_ACTUAL_TARGET_CPU_ENTRY_CONSUMED.json','NEW116_SEED28_ACTUAL_TARGET_CPU_ENTRY_CONSUMED.json'),('NEW116_ACTUAL_AUTHORITY_RESOURCE_BEFORE_COPY.json','NEW116_SEED28_ACTUAL_AUTHORITY_RESOURCE_BEFORE_COPY.json'),('NEW116_ACTUAL_SOURCE_SDK_FULLSTATE_REWARD_CPU_RETURNED_ACTUAL.json','NEW116_SEED28_ACTUAL_SOURCE_SDK_FULLSTATE_REWARD_CPU_RETURNED_ACTUAL.json'),('NEW116_TARGET_CPU_ORIGINAL_ERROR_','NEW116_SEED28_TARGET_CPU_ORIGINAL_ERROR_'),("assert gpu=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'","assert gpu=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'")]
for a,b in mapping:assert installer.count(a)==1,(a,installer.count(a));installer=installer.replace(a,b)
entry=N/'install_NEW116_seed28_actual_target_sourceSDK_fullstate_CPU_UNUSED_once.py';ast.parse(installer);write(entry,installer)
put(R/'FROZEN_NEW116_SEED28_TARGET_CPU_ENTRY_SOURCE_INDEX.json',dict(epoch=time.time(),entry=str(entry),entry_SHA=H(entry),manifest_SHA=spec['manifest_SHA'],source_CPU_SHA=H(proof),source_only=True,no_GO=True))
print(json.dumps(dict(prepared=True,role='h1_seed28',physical28_savedlearning27=True,entry=str(entry),negative_checks=len(neg))))
