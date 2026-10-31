"""Preserve original228 failure; new scalar-reader source and namespace only."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;OLD=N/'source';S=N/'source_V2_FLOAT_FIRST';S.mkdir(exist_ok=False);R=N/'reports'
def put(p,v):
 with Path(p).open('x',encoding='utf8')as f:json.dump(v,f,indent=2)
actual=json.loads((R/'ROOT228_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json').read_bytes());assert not actual['passed_execution']and actual['original_parent']['wait']['returncode']==0
assert json.loads((R/'ROOT228_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json').read_bytes())['global_serial_control_client_lease']=='FREE'
for p in OLD.iterdir():
 if p.is_file()and p.name!='PACKAGE228_SOURCE_AND_TASK.json':(S/p.name).write_bytes(p.read_bytes())
p=S/'evaluate228_action_optimizer_metadata_UNUSED_once.py';s=p.read_text('utf8')
old="x=torch.as_tensor(tensor(value),device='cpu',dtype=torch.float32).reshape(-1)"
new="x=torch.as_tensor(value if isinstance(value,(int,float)) else tensor(value),device='cpu',dtype=torch.float32).reshape(-1)"
assert old in s;s=s.replace(old,new,1);p.write_text(s,encoding='utf8');tree=ast.parse(s)
put(R/'ROOT228V2_NEW_FLOAT_FIRST_ADAPTER_CPU_PURPOSE_ONCE.json',dict(epoch=time.time(),original228_consumed_failure_preserved=True,new_namespace=True,actual_model_raw_SDK_GPU_remote_calls=0,synthetic_adapter_cases=3))
import torch
assert not torch.cuda.is_initialized();rng=torch.random.get_rng_state().clone()
node=next(x for x in ast.walk(tree)if isinstance(x,ast.FunctionDef)and x.name=='vector')
module=ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[]));calls=[]
def convert(x):calls.append(type(x).__name__);return x
scope={'torch':torch,'tensor':convert};exec(compile(module,'actual228V2_vector','exec'),scope)
assert scope['vector'](.5,4)==[.5]*4 and not calls
assert scope['vector'](torch.zeros(1,4),4)==[0.]*4 and calls==['Tensor']
try:scope['vector'](torch.zeros(1,3),4)
except AssertionError:pass
else:raise AssertionError('Bad metadata width accepted')
assert torch.equal(rng,torch.random.get_rng_state())and not torch.cuda.is_initialized()
put(R/'ROOT228V2_NEW_FLOAT_FIRST_ADAPTER_CPU_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,synthetic_cases=3,global_RNG_unchanged=True,CUDA_initialized=False,original_model_or_physics_failure=False))
t=json.loads((S/'TASK228.json').read_bytes());t.update(worker_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),reader_adapter='V2_FLOAT_FIRST',prior228_failure='Scalar0.5 incorrectly sent to Warp tensor adapter before values captured;original false retained')
(S/'TASK228.json').write_text(json.dumps(t,indent=2),encoding='utf8')
caller=(N/'run_ROOT228_action_optimizer_metadata_once.py').read_text('utf8').replace("S=N/'source'","S=N/'source_V2_FLOAT_FIRST'")
caller=caller.replace('META228_CNONE_20261101/case','META228V2_CNONE_20261101/case').replace("'ROOT228_","'ROOT228V2_")
caller=caller.replace("run_ROOT228_action_optimizer_metadata_once|","run_ROOT228V2_action_optimizer_metadata_once|run_ROOT228_action_optimizer_metadata_once|")
ast.parse(caller);(N/'run_ROOT228V2_action_optimizer_metadata_once.py').write_text(caller,encoding='utf8')
rows=[dict(relative=p.name,bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest())for p in sorted(S.iterdir())if p.is_file()]
put(S/'PACKAGE228_SOURCE_AND_TASK.json',dict(epoch=time.time(),files=rows,model_or_asset_copy=0))
put(R/'ROOT228V2_BEFORE_USE_REPAIR_FROZEN.json',dict(epoch=time.time(),changes='Only scalar-before-Warp metadata adapter/Task worker hash/new namespace and CIM/report prefix. Original228 source/error/receipts retained.',worker_SHA=t['worker_SHA'],original228_reexecution=False,model_reads=0,source_AST_CPU_passed=True))
print(json.dumps(dict(passed=True,model_reads=0,source_files=len(rows))))
