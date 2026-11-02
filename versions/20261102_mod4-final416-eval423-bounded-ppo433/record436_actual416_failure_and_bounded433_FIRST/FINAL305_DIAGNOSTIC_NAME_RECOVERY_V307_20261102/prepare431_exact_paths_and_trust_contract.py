"""Independent431 fixes unused429postroundrelativepath and validates actualtrustreceipt."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import re
import shutil
import time
P=Path(__file__).resolve().parent;T=P.parent;R=P/'reports'
O=T/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V429_20261102'
OQ=T/'RL429_SINGLE_PROCESS_POSTROUND_V430_20261102'
OE=T/'RL429_FINAL_INDEPENDENT_EVAL_V430_20261102'
N=T/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V431_20261102'
Q=T/'RL431_SINGLE_PROCESS_POSTROUND_V432_20261102'
E=T/'RL431_FINAL_INDEPENDENT_EVAL_V432_20261102'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_bytes())
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
def token(s,a,b):return re.sub(r'(?<=[A-Za-z_])'+str(a)+r'(?!\d)',str(b),s)
def rename(s):
 for a,b in((O,N),(OQ,Q),(OE,E)):
  s=s.replace(str(a),str(b)).replace(a.as_posix(),b.as_posix())
 s=s.replace('RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V429_20261102',N.name)
 return token(token(s,429,431),430,432)
assert not(O/'reports/ROOT429_START_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
put(R/'STATIC431_UNUSED429_POSTROUND_PATH_REJECTION.json',dict(epoch=time.time(),passed=False,unused429=True,
 oldpostround=str(OQ),defect='RelativeN assignment uses RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V429 but actualroot RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V429; oldbinderandtimerwouldfailbeforeIO',
 repair='Independent431/432 correctspaths and explicitlyvalidatesactortrustreceipt; CPU428learnerbyteexactunchanged',network=0,SDK=0,modelreads=0))
for origin,dest in((O,N),(OQ,Q),(OE,E)):
 assert not dest.exists();dest.mkdir();(dest/'reports').mkdir()
 for path in sorted(origin.rglob('*')):
  if not path.is_file()or'__pycache__'in path.parts or'reports'in path.relative_to(origin).parts or path.name.startswith('INDEX'):continue
  target=dest/rename(str(path.relative_to(origin)));target.parent.mkdir(parents=True,exist_ok=True)
  if path.suffix=='.py':
   data=rename(path.read_text('utf8'));ast.parse(data);target.write_bytes(data.encode('utf8'))
  elif path.name.startswith('TASK'):
   def strings(v):
    if isinstance(v,str):return v if re.fullmatch(r'[0-9a-f]{64}',v)else rename(v)
    if isinstance(v,list):return[strings(x)for x in v]
    if isinstance(v,dict):return{k:strings(x)for k,x in v.items()}
    return v
   put(target,strings(read(path)))
  else:shutil.copyfile(path,target)
# ExactCPUlearnerbyteidentity, unaffectedbyproductionversion.
learner=O/'source/actual_transition_learner427.py'
for root in(N,E):shutil.copyfile(learner,root/'source/actual_transition_learner427.py')
shutil.copyfile(O/'reports/CPU429_REUSED428_TRUST_ADMISSION.json',N/'reports/CPU431_REUSED428_TRUST_ADMISSION.json')
contract=(N/'teacher_task431.py').read_text('utf8')
needle=" assert d['actor_grad_norm']>0 and math.isfinite(d['actor_grad_norm'])and d['terminal_bootstrap']==0.\n"
assert contract.count(needle)==1
contract=contract.replace(needle,needle+" trust=d['actor_trust_step'];assert trust['applied']and trust['actual_KL']<=.01 and trust['actual_max_action_delta']<=.05 and trust['one_committed_Adam_step']\n")
for path in(N/'teacher_task431.py',N/'tracking_task431.py',N/'control431/teacher_task431.py'):
 ast.parse(contract);path.write_bytes(contract.encode('utf8'))
taskpath=N/'TASK431_FROZEN.json';task=read(taskpath)
nonce=str(time.time_ns());job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_BOUNDED_ACTUAL_PPO431_'+nonce
task.update(run_id='ACTUAL_RESIDUAL_PPO431_'+nonce,job_root=job+'/tracker72',owner_root=job+'/owner72',worker_SHA=H(N/'source/worker431.py'),CPU431_SHA=H(N/'reports/CPU431_REUSED428_TRUST_ADMISSION.json'))
taskpath.write_bytes(json.dumps(task,indent=2,ensure_ascii=False).encode('utf8'))
etaskpath=E/'TASK432_PENDING_FINAL_IDENTITY.json';etask=read(etaskpath);etask['worker_SHA']=H(E/'source/evaluate432.py');etaskpath.write_bytes(json.dumps(etask,indent=2).encode('utf8'))
for path in list(N.rglob('*.py'))+list(Q.rglob('*.py'))+list(E.rglob('*.py')):ast.parse(path.read_bytes())
assert H(N/'source/actual_transition_learner427.py')==read(N/'reports/CPU431_REUSED428_TRUST_ADMISSION.json')['learnerSHA']
assert H(E/'source/actual_transition_learner427.py')==H(learner)
for path in Q.glob('*.py'):
 text=path.read_text('utf8');assert N.name in text and 'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V431'not in text
post=Q/'postround432_close_actual431_eval_once.py';posttext=post.read_text('utf8')
assert 'path!=index' in posttext and E.name in posttext
spec=importlib.util.spec_from_file_location('static431contract',N/'teacher_task431.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_task(task)
for root in(N,E):
 assert H(root/'feedforward389.json')==task['fixed_command_feedforward']['SHA']
 assert H(root/'reference389.npz')==task['reference']['SHA']
normal=N/'normal431'
put(normal/'INDEX431_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in(normal/'normal431_common.py',normal/'collect431_fullclose_transfer_once.py',N/'teacher_task431.py')]))
files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(N/'INDEX431_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=files))
files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for root in(Q,E)for p in sorted(root.rglob('*'))if p.is_file()and'__pycache__'not in p.parts]
put(Q/'INDEX432_POSTROUND_FOR431_FROZEN.json',dict(epoch=time.time(),files=files))
put(R/'STATIC431_EXACT_PATH_CPU428_TRUST_CONTRACT_PRODUCTION.json',dict(epoch=time.time(),passed=True,
 root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX431_SOURCE_TASK_CALLERS_FROZEN.json'),
 workerSHA=task['worker_SHA'],learnerSHA=H(learner),CPU428byteexact=True,source_offsets=[56304,13364,25556],
 postroot=str(Q),postindexSHA=H(Q/'INDEX432_POSTROUND_FOR431_FROZEN.json'),evalroot=str(E),
 actualtrustreceipt_required=True,exact_relative_paths=True,selfindexexcluded=True,allAST=True,START=False,SDK=0,physics=0,modelreads=0,network=0))
print(json.dumps(dict(passed=True,root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX431_SOURCE_TASK_CALLERS_FROZEN.json'),postindexSHA=H(Q/'INDEX432_POSTROUND_FOR431_FROZEN.json'))))
