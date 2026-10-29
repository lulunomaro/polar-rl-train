from pathlib import Path
import json,ast,time,sys,copy,hashlib
N=Path(__file__).resolve().parent;R=N/'reports';B=N/'payloads_v2/seed28'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 with Path(p).open('x',encoding='utf8') as f:f.write(v)
write(R/'SOURCE114_SEED28_V2_MISSING_WRITER_NAMESPACE_AND_PREEXEC_MISSING_ENTRY_ACTUAL.json',json.dumps(dict(epoch=time.time(),original_error='V2 sealer AST tail NameError write not defined before proof/installer; following attempted newinstaller path absent before interpreter/marker/network',model_or_network_actions=0,old_sources_and_errors_retained=True,correction='NEW V3 explicit write function provided to the extracted source-sealer tail; old main not executed.'),indent=2))
spec=json.loads((R/'NEW114_SEED28_ONE_SOURCE111_TYPED_PAYLOAD_PREPARED_NOT_ADMITTED_ACTUAL.json').read_bytes());task=spec['task'];sys.path[:0]=[str(B),str(B/'source')]
from native_flat90_source_guard_v1 import validate_task_go
go=copy.deepcopy(task);go.update(payload_manifest_SHA=spec['manifest_SHA'],num_envs=4096,max_parent_seconds=3900,exit_headroom_seconds=300)
validate_task_go(task,go,spec['manifest_SHA']);neg=[]
for field in ('native_seed','native_learning_seed','logical_slot','source_SHA'):
 bad=copy.deepcopy(go);bad[field]='WRONG'
 try:validate_task_go(task,bad,spec['manifest_SHA'])
 except (ValueError,TypeError,AssertionError,KeyError):neg.append('GO.'+field)
 else:raise AssertionError(field)
bad=copy.deepcopy(task);bad['GPU_UUID']='WRONG'
try:validate_task_go(bad,go,spec['manifest_SHA'])
except (ValueError,TypeError,AssertionError,KeyError):neg.append('Task.GPU_UUID')
else:raise AssertionError('Task.GPU_UUID')
original=N/'prepare_NEW114_seed28_exact_alias_second_candidate_SOURCE_ONLY_once.py';tree=ast.parse(original.read_text(encoding='utf8'))
start=next(i for i,x in enumerate(tree.body) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='proof' for t in x.targets))
assert not (N/'install_NEW114_seed28_WM_heading_actual_sourceSDK_fullstate_CPU_UNUSED_once.py').exists()
ns=dict(N=N,R=R,B=B,Path=Path,json=json,copy=copy,hashlib=hashlib,ast=ast,time=time,H=H,neg=neg,spec=spec,write=write)
exec(compile(ast.Module(body=tree.body[start:],type_ignores=[]),str(original),'exec'),ns)
