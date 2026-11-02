"""Independent355 fixes actual354 SDK scale Tensor JSON failure before first control."""
from pathlib import Path
import ast,hashlib,json,re,shutil,subprocess,sys,time
P=Path(__file__).resolve().parent;T=P.parent
S=T/'MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V354_20261102'
D=T/'MPC_CURRENT_STATE_EVENT_PHYSX_COMPARISON_V355_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(p,v):
    with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
actual=read(S/'reports/ROOT354_EVALUATION_FULL_RETURNED.json');assert actual['result']is None
errors=[r for r in actual['full_UTF8']if r['path'].endswith('/ORIGINAL354_ERROR.json')];assert len(errors)==1 and'Tensor is not JSON serializable'in errors[0]['UTF8']
released=next(json.loads(r['UTF8'])for r in actual['full_UTF8']if r['path'].endswith('ACTUAL354_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json'));assert released['all_own_children_waited']and released['all_owned_locks_released']
put(P/'reports/ACTUAL354_SCALE_TENSOR_FAILURE_PRESERVED.json',dict(epoch=time.time(),source=str(S/'reports/ROOT354_EVALUATION_FULL_RETURNED.json'),SHA=H(S/'reports/ROOT354_EVALUATION_FULL_RETURNED.json'),first_control_completed=False,NN=0,account=0,SDK_constructed=True,error=errors[0],originalfalse_preserved=True,originalconsumed_not_replayed=True,ownclosed=True,repair='Independent355 converts actualSDK term scale tensor to plain perwidth list, validated for serialization and channel unscale; no physics/PD/reward/sourcecontroller change.'))
D.mkdir(exist_ok=False);(D/'reports').mkdir()
def rename(s):return re.sub(r'(?<=[A-Za-z_])354(?!\d)','355',s)
for path in sorted(S.rglob('*')):
    if not path.is_file()or'__pycache__'in path.parts or'reports'in path.relative_to(S).parts or path.name.startswith('INDEX354'):continue
    dest=D/rename(str(path.relative_to(S)));dest.parent.mkdir(parents=True,exist_ok=True)
    if path.suffix in('.py','.json'):dest.write_text(rename(path.read_text('utf8')),encoding='utf8')
    elif path.suffix=='.npz':shutil.copyfile(path,dest)
worker=(D/'source/evaluate355.py').read_text('utf8')
old="  width=int(dims[0]);policy_slices[name]=(offset,offset+width,1. if termcfg.scale is None else termcfg.scale);offset+=width"
new="""  width=int(dims[0]);scale=termcfg.scale
  if scale is None:scale=np.ones(width,dtype=np.float32)
  elif torch.is_tensor(scale):scale=scale.detach().cpu().numpy()
  else:scale=np.asarray(scale,dtype=np.float32)
  if scale.ndim==0:scale=np.full(width,float(scale),dtype=np.float32)
  elif scale.shape==(80,width):scale=scale[0]
  else:scale=scale.reshape(-1)
  assert scale.shape==(width,)and np.isfinite(scale).all()and (scale!=0).all()
  policy_slices[name]=(offset,offset+width,scale.tolist());offset+=width"""
assert old in worker;worker=worker.replace(old,new)
(D/'source/evaluate355.py').write_text(worker,encoding='utf8')
task=read(D/'TASK355_FROZEN.json');task['worker_SHA']=H(D/'source/evaluate355.py');task['planned_motor_control']['SHA']=H(D/'planned_mpc_motor355.json');task['planned_motor_control']['bytes']=(D/'planned_mpc_motor355.json').stat().st_size
(D/'TASK355_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
for path in D.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
ns={};exec(compile((D/'contract355.py').read_text('utf8'),str(D/'contract355.py'),'exec'),ns);assert ns['validate_task'](task)
# Actual failure's Tensor case verified without SDK/physics; no extra checkpoint read.
test="import json,torch,numpy as np\nfor shape in ((),(3,),(80,3)):\n scale=torch.full(shape,.5).cpu().numpy();scale=np.full(3,float(scale),dtype=np.float32)if scale.ndim==0 else scale[0]if scale.shape==(80,3)else scale.reshape(-1);assert scale.shape==(3,);value=scale.tolist();assert np.allclose(np.array([.1,.2,.3])/np.array(value),[.2,.4,.6]);json.dumps(value)\nprint('PASS')"
cpu=subprocess.run(['C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe','-B','-X','utf8','-c',test],capture_output=True,text=True,encoding='utf8',check=True);assert cpu.stdout.strip()=='PASS'
files=[path for path in sorted(D.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]
put(D/'INDEX355_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]))
put(P/'reports/STATIC355_SCALE_TENSOR_REPAIR.json',dict(epoch=time.time(),passed=True,root=str(D),INDEX_SHA=H(D/'INDEX355_SOURCE_TASK_CALLERS_FROZEN.json'),CPU_tensor_serialize_unscale_passed=True,SDK=0,NN=0,network=0,GO=0))
print(json.dumps(dict(passed=True,root=str(D),INDEX_SHA=H(D/'INDEX355_SOURCE_TASK_CALLERS_FROZEN.json'),NN=0,SDK=0)))
