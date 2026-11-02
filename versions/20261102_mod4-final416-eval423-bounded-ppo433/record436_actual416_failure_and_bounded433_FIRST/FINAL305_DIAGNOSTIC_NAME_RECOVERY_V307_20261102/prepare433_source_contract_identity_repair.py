"""Independent433 synchronizes everyactualworkercontract;431failedpreSDKpreserved."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import re
import shutil
import time
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
O=T/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V431_20261102';OQ=T/'RL431_SINGLE_PROCESS_POSTROUND_V432_20261102';OE=T/'RL431_FINAL_INDEPENDENT_EVAL_V432_20261102'
N=T/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V433_20261102';Q=T/'RL433_SINGLE_PROCESS_POSTROUND_V434_20261102';E=T/'RL433_FINAL_INDEPENDENT_EVAL_V434_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def token(s,a,b):return re.sub(r'(?<=[A-Za-z_])'+str(a)+r'(?!\d)',str(b),s)
def rename(s):
 for a,b in((O,N),(OQ,Q),(OE,E)):s=s.replace(str(a),str(b)).replace(a.as_posix(),b.as_posix())
 return token(token(s,431,433),432,434)
snap=read(O/'reports/ROOT431_STATUS_FIRST_UPDATED.json');files={Path(x['path']).name:json.loads(x['UTF8'])for x in snap['full_selected_UTF8']}
assert files['NODE_EXIT_ACTUAL.json']['all_own_children_waited']and files['NODE_EXIT_ACTUAL.json']['private_EX_released']
assert files['OWNER_EXIT_ACTUAL.json']['original_cost_settled']
assert 'source_SHA'in files['NODE_ORIGINAL_ERROR.json']['error']or'final'in files['NODE_ORIGINAL_ERROR.json']['error']
for origin,dest in((O,N),(OQ,Q),(OE,E)):
 assert not dest.exists();dest.mkdir();(dest/'reports').mkdir()
 for path in sorted(origin.rglob('*')):
  if not path.is_file()or'__pycache__'in path.parts or'reports'in path.relative_to(origin).parts or path.name.startswith('INDEX'):continue
  target=dest/rename(str(path.relative_to(origin)));target.parent.mkdir(parents=True,exist_ok=True)
  if path.suffix=='.py':
   s=rename(path.read_text('utf8'));ast.parse(s);target.write_bytes(s.encode('utf8'))
  elif path.name.startswith('TASK'):
   def names(v):
    if isinstance(v,str):return v if re.fullmatch('[0-9a-f]{64}',v)else rename(v)
    if isinstance(v,list):return[names(x)for x in v]
    if isinstance(v,dict):return{k:names(x)for k,x in v.items()}
    return v
   put(target,names(read(path)))
  else:shutil.copyfile(path,target)
learner=O/'source/actual_transition_learner427.py'
for root in(N,E):shutil.copyfile(learner,root/'source/actual_transition_learner427.py')
shutil.copyfile(O/'reports/CPU431_REUSED428_TRUST_ADMISSION.json',N/'reports/CPU433_REUSED428_TRUST_ADMISSION.json')
contract=(N/'teacher_task433.py').read_bytes()
for path in(N/'tracking_task433.py',N/'control433/teacher_task433.py',N/'source/teacher_task433.py',N/'source/tracking_task433.py',E/'source/teacher_task433.py',E/'source/tracking_task433.py'):
 path.write_bytes(contract)
taskpath=N/'TASK433_FROZEN.json';task=read(taskpath);nonce=str(time.time_ns());job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_BOUNDED_ACTUAL_PPO433_'+nonce
task.update(run_id='ACTUAL_RESIDUAL_PPO433_'+nonce,job_root=job+'/tracker72',owner_root=job+'/owner72',worker_SHA=H(N/'source/worker433.py'),CPU433_SHA=H(N/'reports/CPU433_REUSED428_TRUST_ADMISSION.json'))
taskpath.write_bytes(json.dumps(task,indent=2,ensure_ascii=False).encode('utf8'))
for i,path in enumerate((N/'teacher_task433.py',N/'control433/teacher_task433.py',N/'source/teacher_task433.py',N/'source/tracking_task433.py')):
 spec=importlib.util.spec_from_file_location('contract433_'+str(i),path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_task(task)
 assert H(path)==H(N/'teacher_task433.py')
etaskpath=E/'TASK434_PENDING_FINAL_IDENTITY.json';etask=read(etaskpath);etask['worker_SHA']=H(E/'source/evaluate434.py');etaskpath.write_bytes(json.dumps(etask,indent=2).encode('utf8'))
for path in list(N.rglob('*.py'))+list(Q.rglob('*.py'))+list(E.rglob('*.py')):ast.parse(path.read_bytes())
assert H(N/'source/actual_transition_learner427.py')==read(N/'reports/CPU433_REUSED428_TRUST_ADMISSION.json')['learnerSHA']
for path in Q.glob('*.py'):assert N.name in path.read_text('utf8')
assert 'path!=index'in(Q/'postround434_close_actual433_eval_once.py').read_text('utf8')
normal=N/'normal433'
put(normal/'INDEX433_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in(normal/'normal433_common.py',normal/'collect433_fullclose_transfer_once.py',N/'teacher_task433.py')]))
rows=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(N/'INDEX433_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=rows))
rows=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for root in(Q,E)for p in sorted(root.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(Q/'INDEX434_POSTROUND_FOR433_FROZEN.json',dict(epoch=time.time(),files=rows))
put(R/'STATIC433_WORKER_ROOT_CONTROL_CONTRACT_IDENTICAL.json',dict(epoch=time.time(),passed=True,root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX433_SOURCE_TASK_CALLERS_FROZEN.json'),workerSHA=task['worker_SHA'],source_control_root_contract_SHA=H(N/'teacher_task433.py'),CPU428learner_exact=True,postroot=str(Q),postindexSHA=H(Q/'INDEX434_POSTROUND_FOR433_FROZEN.json'),evalroot=str(E),original431preSDKfailurepreserved=True,SDK=0,modelreads=0,network=0,START=False))
print(json.dumps(dict(passed=True,run=task['run_id'],indexSHA=H(N/'INDEX433_SOURCE_TASK_CALLERS_FROZEN.json'),postindexSHA=H(Q/'INDEX434_POSTROUND_FOR433_FROZEN.json'))))
