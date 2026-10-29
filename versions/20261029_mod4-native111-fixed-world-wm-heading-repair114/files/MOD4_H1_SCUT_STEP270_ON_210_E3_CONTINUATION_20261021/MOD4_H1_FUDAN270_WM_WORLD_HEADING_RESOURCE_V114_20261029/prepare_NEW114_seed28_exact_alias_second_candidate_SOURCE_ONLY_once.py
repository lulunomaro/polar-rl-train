"""Second genuine physical seed candidate; no model/binary content read."""
from pathlib import Path
import json,copy,hashlib,shutil,os,ast,time,sys
N=Path(__file__).resolve().parent;R=N/'reports';A=N/'payloads_v2/seed27';B=N/'payloads_v2/seed28'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def write(p,v):Path(p).write_text(v,encoding='utf8',newline='\n')
assert not B.exists();B.mkdir(parents=True)
old=read(R/'NEW114_V2_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json');m=read(A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');rows={x['relative']:x for x in m['files']}
for row in m['files']:
 s=A/row['relative'];d=B/row['relative'];d.parent.mkdir(parents=True,exist_ok=True)
 if s.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(s,d)
 else:shutil.copy2(s,d)
task=copy.deepcopy(old['task']);task.update(id='MOD4_H1_FUDAN270_WM_HEADING114_seed28',logical_slot='h1_seed28',GPU_UUID='GPU-16828f91-2b45-b646-8dc0-9481138e2842',seed=28,native_seed=28)
g=(A/'native_flat90_source_guard_v1.py').read_text(encoding='utf8');assert g.count("task.get('logical_slot')=='h1'")==1
g=g.replace("task.get('logical_slot')=='h1'","task.get('logical_slot')=='h1_seed28'").replace("'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'","'GPU-16828f91-2b45-b646-8dc0-9481138e2842'")
ast.parse(g);write(B/'native_flat90_source_guard_v1.py',g)
c=read(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');c['approved_python']={p.relative_to(B).as_posix():H(p) for p in B.rglob('*.py')}
write(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json',json.dumps(c,indent=2));task['flat_source_contract_SHA']=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json');write(B/'job0/TASK.json',json.dumps(task,indent=2))
new=[]
for row in m['files']:
 rel=row['relative'];p=B/rel
 if p.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):r=row
 else:r=dict(relative=rel,bytes=p.stat().st_size,SHA=H(p))
 new.append(r)
m['files']=new;write(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',json.dumps(m,indent=2))
spec=copy.deepcopy(old);spec.update(epoch=time.time(),payload=str(B),task=task,job_root='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FUDAN270_WM_HEADING_2610v114/seed28',GPU_UUID=task['GPU_UUID'],logical_slot='h1_seed28',manifest_SHA=H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),source_contract_SHA=H(B/'FLAT90_SOURCE_CONTRACT_ACTUAL.json'))
write(R/'NEW114_SEED28_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json',json.dumps(spec,indent=2))
sys.path[:0]=[str(B),str(B/'source')]
from native_flat90_source_guard_v1 import validate_task_go
go=copy.deepcopy(task);go.update(payload_manifest_SHA=spec['manifest_SHA'],num_envs=4096,max_parent_seconds=3900,exit_headroom_seconds=300)
validate_task_go(task,go,spec['manifest_SHA']);neg=[]
for field in ('native_seed','native_learning_seed','logical_slot','GPU_UUID','source_SHA'):
 bad=copy.deepcopy(go);bad[field]='WRONG'
 try:validate_task_go(task,bad,spec['manifest_SHA'])
 except (ValueError,TypeError,AssertionError,KeyError):neg.append(field)
 else:raise AssertionError('physical alias not bound '+field)
proof=dict(passed=True,epoch=time.time(),physical_seed28_saved_learning_seed27_bound=True,only_guard_alias_GPU_Task_contract_inventory_manifest_metadata_changed=True,all_other_Python_identical=True,negative_fields=neg,source27_new_WM_helper_CPU_proof_SHA=H(R/'SOURCE114_V2_PREINSTALL_TASK_GO_HELPER_PRODUCER_CPU_ACTUAL.json'),model_binary_reads=0)
write(R/'SOURCE114_SEED28_PREINSTALL_ALIAS_TASK_GO_CPU_ACTUAL.json',json.dumps(proof,indent=2))
installer=(N/'install_NEW114_one_WM_heading_actual_sourceSDK_fullstate_CPU_UNUSED_once.py').read_text(encoding='utf8')
for a,b in [('NEW114_V2_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json','NEW114_SEED28_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json'),('SOURCE114_V2_PREINSTALL_TASK_GO_HELPER_PRODUCER_CPU_ACTUAL.json','SOURCE114_SEED28_PREINSTALL_ALIAS_TASK_GO_CPU_ACTUAL.json'),('FROZEN_NEW114_ONE_ACTUAL_TARGET_CPU_ENTRY_SOURCE_INDEX_V1.json','FROZEN_NEW114_SEED28_ACTUAL_TARGET_CPU_ENTRY_SOURCE_INDEX_V1.json'),('NEW114_ONE_ACTUAL_TARGET_CPU_ENTRY_CONSUMED.json','NEW114_SEED28_ACTUAL_TARGET_CPU_ENTRY_CONSUMED.json'),('NEW114_ACTUAL_PRECOPY_CURRENT_AUTHORITY_AND_CPU_RESOURCE.json','NEW114_SEED28_ACTUAL_PRECOPY_CURRENT_AUTHORITY_AND_CPU_RESOURCE.json'),('NEW114_ACTUAL_SOURCE_SDK_FULLSTATE_CPU_RETURNED_ACTUAL.json','NEW114_SEED28_ACTUAL_SOURCE_SDK_FULLSTATE_CPU_RETURNED_ACTUAL.json'),('NEW114_TARGET_CPU_ORIGINAL_ERROR_','NEW114_SEED28_TARGET_CPU_ORIGINAL_ERROR_'),("assert gpu=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'","assert gpu=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'")]:
 assert installer.count(a)==1,(a,installer.count(a));installer=installer.replace(a,b)
entry=N/'install_NEW114_seed28_WM_heading_actual_sourceSDK_fullstate_CPU_UNUSED_once.py';ast.parse(installer);write(entry,installer)
seal=dict(epoch=time.time(),status='FROZEN_UNUSED_SEED28_ACTUAL_TARGET_CPU',entry=str(entry),entry_SHA=H(entry),manifest_SHA=spec['manifest_SHA'],source_Task_GO_proof_SHA=H(R/'SOURCE114_SEED28_PREINSTALL_ALIAS_TASK_GO_CPU_ACTUAL.json'),no_GPU_GO=True)
write(R/'FROZEN_NEW114_SEED28_ACTUAL_TARGET_CPU_ENTRY_SOURCE_INDEX_V1.json',json.dumps(seal,indent=2))
print(json.dumps(dict(prepared_seed28=True,entry=str(entry),entry_SHA=H(entry),physical_seed=28,saved_learning_seed=27,PT_decodes=0)))
