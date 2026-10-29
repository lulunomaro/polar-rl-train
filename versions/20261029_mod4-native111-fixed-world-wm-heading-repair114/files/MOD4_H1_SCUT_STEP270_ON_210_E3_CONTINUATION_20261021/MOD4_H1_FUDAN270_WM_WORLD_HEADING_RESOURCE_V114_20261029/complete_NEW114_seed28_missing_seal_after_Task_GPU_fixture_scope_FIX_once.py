"""Complete unused second candidate after fixture-field scope refusal, no source/model rerun."""
from pathlib import Path
import json,ast,time,sys,copy,hashlib
N=Path(__file__).resolve().parent;R=N/'reports';B=N/'payloads_v2/seed28'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with Path(p).open('x',encoding='utf8') as f:f.write(v)
spec=json.loads((R/'NEW114_SEED28_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json').read_bytes());task=spec['task']
write(R/'SOURCE114_SEED28_ORIGINAL_Task_GPU_FIXTURE_SCOPE_REFUSAL_ACTUAL.json',json.dumps(dict(epoch=time.time(),original_entry='prepare_NEW114_seed28_exact_alias_second_candidate_SOURCE_ONLY_once.py',original_error='AssertionError: physical alias not bound GPU_UUID at line37',stage='Before proof seal/installer/remote/model action, full source candidate prepared',classification='Fixture scope error: native payloadguard binds Task.GPU_UUID; test mutated GO.GPU_UUID which is generated and bound in the separate signed controller protocol. No runtime/source guard relaxed.',old_entry_not_reexecuted=True,correction='New test mutates actual guard-consumed Task.GPU_UUID, preserves GO negative checks for fields the migration guard consumes. Future controller must separately reject bad spec.GPU_UUID.'),indent=2))
sys.path[:0]=[str(B),str(B/'source')]
from native_flat90_source_guard_v1 import validate_task_go
go=copy.deepcopy(task);go.update(payload_manifest_SHA=spec['manifest_SHA'],num_envs=4096,max_parent_seconds=3900,exit_headroom_seconds=300)
validate_task_go(task,go,spec['manifest_SHA']);neg=[]
for field in ('native_seed','native_learning_seed','logical_slot','source_SHA'):
 bad=copy.deepcopy(go);bad[field]='WRONG'
 try:validate_task_go(task,bad,spec['manifest_SHA'])
 except (ValueError,TypeError,AssertionError,KeyError):neg.append('GO.'+field)
 else:raise AssertionError('guard-consumed GO field not bound '+field)
bad=copy.deepcopy(task);bad['GPU_UUID']='WRONG'
try:validate_task_go(bad,go,spec['manifest_SHA'])
except (ValueError,TypeError,AssertionError,KeyError):neg.append('Task.GPU_UUID')
else:raise AssertionError('Task hardware alias not bound')
# Reuse only source-sealer tail AST from original preparer; no previous main/body execution.
original=N/'prepare_NEW114_seed28_exact_alias_second_candidate_SOURCE_ONLY_once.py';tree=ast.parse(original.read_text(encoding='utf8'))
start=next(i for i,x in enumerate(tree.body) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='proof' for t in x.targets))
tail=ast.Module(body=tree.body[start:],type_ignores=[])
assert not (N/'install_NEW114_seed28_WM_heading_actual_sourceSDK_fullstate_CPU_UNUSED_once.py').exists()
ns=dict(__name__='NEW114_seed28_missing_seal_only',__file__=str(original),N=N,R=R,B=B,Path=Path,json=json,copy=copy,hashlib=hashlib,ast=ast,time=time,H=H,neg=neg,spec=spec)
exec(compile(tail,str(original),'exec'),ns)
