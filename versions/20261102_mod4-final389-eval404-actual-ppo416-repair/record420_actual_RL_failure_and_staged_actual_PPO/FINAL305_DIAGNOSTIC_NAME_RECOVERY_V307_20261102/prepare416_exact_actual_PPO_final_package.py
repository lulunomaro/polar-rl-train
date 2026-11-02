"""Final416 package retains CPU409 learner bytes exactly, plus independent417 postround."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import re
import shutil
import time

P=Path(__file__).resolve().parent;T=P.parent
C=T/'RL_ACTUAL_TRANSITION_PPO_REPAIR_V409_20261102'
O=T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V414_20261102'
OQ=T/'RL414_SINGLE_PROCESS_POSTROUND_V415_20261102'
OE=T/'RL414_FINAL_INDEPENDENT_EVAL_V415_20261102'
N=T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102'
Q=T/'RL416_SINGLE_PROCESS_POSTROUND_V417_20261102'
E=T/'RL416_FINAL_INDEPENDENT_EVAL_V417_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_bytes())
def put(path,value):
 with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
assert not N.exists()and not Q.exists()and not E.exists()
assert not(O/'reports/ROOT414_START_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
cpu=read(C/'reports/CPU409_REAL_TRANSITION_RL_NO_STEP_ADMISSION.json')
put(P/'reports/STATIC416_UNUSED414_LINE_ENDING_IDENTITY_REJECTION.json',dict(epoch=time.time(),passed=False,
 original414_unused=True,original_learnerSHA=cpu['learnerSHA'],prepared414learnerSHA=H(O/'source/actual_transition_learner409.py'),
 reason='Windowsread_text/write_text normalizedlineendings; ASTmatchesbutlauncherbyteSHAcheckwouldfail',
 repair='Independent416 copies exactCPU409 learnerbytesaftertokenrename; no new PTread',network=0,SDK=0,modelreads=0))
def rename(text):
 for old,new in((O,N),(OQ,Q),(OE,E)):
  text=text.replace(str(old),str(new)).replace(old.as_posix(),new.as_posix())
 for old,new in((414,416),(415,417)):
  text=re.sub(r'(?<=[A-Za-z_])'+str(old)+r'(?!\d)',str(new),text)
 return text
for origin,dest in((O,N),(OQ,Q),(OE,E)):
 dest.mkdir();(dest/'reports').mkdir()
 for path in sorted(origin.rglob('*')):
  if not path.is_file()or'__pycache__'in path.parts or path.name.startswith('INDEX')or 'reports'in path.relative_to(origin).parts:continue
  target=dest/rename(str(path.relative_to(origin)));target.parent.mkdir(parents=True,exist_ok=True)
  if path.suffix=='.py':target.write_text(rename(path.read_text('utf8')),encoding='utf8')
  elif path.name.startswith('TASK'):
   value=read(path)
   def names(value):
    if isinstance(value,str):
     if re.fullmatch(r'[0-9a-f]{64}',value)or value.startswith('GPU-'):return value
     return rename(value)
    if isinstance(value,list):return[names(item)for item in value]
    if isinstance(value,dict):return{key:names(item)for key,item in value.items()}
    return value
   target.write_text(json.dumps(names(value),indent=2),encoding='utf8')
  else:shutil.copyfile(path,target)
for root in(N,E):
 shutil.copyfile(C/'source/actual_transition_learner409.py',root/'source/actual_transition_learner409.py')
shutil.copyfile(C/'reports/CPU409_REAL_TRANSITION_RL_NO_STEP_ADMISSION.json',N/'reports/CPU416_REUSED409_NO_STEP_ADMISSION.json')
taskpath=N/'TASK416_FROZEN.json';task=read(taskpath)
nonce=str(time.time_ns());job='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_ACTUAL_RESIDUAL_PPO416_'+nonce
task.update(kind='ACTUAL_ONPOLICY_RESIDUAL_PPO_400N50_V416',run_id='ACTUAL_RESIDUAL_PPO416_'+nonce,
 job_root=job+'/tracker72',owner_root=job+'/owner72',worker_SHA=H(N/'source/worker416.py'),
 CPU416_SHA=H(N/'reports/CPU416_REUSED409_NO_STEP_ADMISSION.json'))
taskpath.write_text(json.dumps(task,indent=2),encoding='utf8')
etaskpath=E/'TASK417_PENDING_FINAL_IDENTITY.json';etask=read(etaskpath)
etask.update(kind='FROZEN416_ACTUAL_RESIDUAL_PPO_EVAL417',worker_SHA=H(E/'source/evaluate417.py'))
etaskpath.write_text(json.dumps(etask,indent=2),encoding='utf8')

for path in list(N.rglob('*.py'))+list(Q.rglob('*.py'))+list(E.rglob('*.py')):ast.parse(path.read_text('utf8'),filename=str(path))
assert H(N/'source/actual_transition_learner409.py')==cpu['learnerSHA']==H(E/'source/actual_transition_learner409.py')
assert task['worker_SHA']==H(N/'source/worker416.py')
assert task['GPU_UUID']=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
assert H(N/'feedforward389.json')==task['fixed_command_feedforward']['SHA']==H(E/'feedforward389.json')
assert H(N/'reference389.npz')==task['reference']['SHA']==H(E/'reference389.npz')
spec=importlib.util.spec_from_file_location('static416contract',N/'teacher_task416.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_task(task)
normal=N/'normal416'
put(normal/'INDEX416_NORMAL_SOURCE_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in(normal/'normal416_common.py',normal/'collect416_fullclose_transfer_once.py',N/'teacher_task416.py')]))
put(N/'INDEX416_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(N.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]))
put(Q/'INDEX417_POSTROUND_FOR416_FROZEN.json',dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for root in(Q,E)for path in sorted(root.rglob('*'))if path.is_file()and'__pycache__'not in path.parts]))
put(P/'reports/STATIC416_COMPLETE_ACTUAL_PPO417_POSTROUND_PACKAGE.json',dict(epoch=time.time(),passed=True,
 root=str(N),run=task['run_id'],indexSHA=H(N/'INDEX416_SOURCE_TASK_CALLERS_FROZEN.json'),workerSHA=task['worker_SHA'],
 CPU409learnerbyteexact=True,no_new_PTread=True,actualPPO_update=True,
 sourceAdam=[56144,13204,20419],postroot=str(Q),postindexSHA=H(Q/'INDEX417_POSTROUND_FOR416_FROZEN.json'),
 evalroot=str(E),sameprocessserialpostround=True,allAST=True,START=False,network=0,SDK=0,physics=0))
print(json.dumps(dict(passed=True,run=task['run_id'],indexSHA=H(N/'INDEX416_SOURCE_TASK_CALLERS_FROZEN.json'),workerSHA=task['worker_SHA'],postindexSHA=H(Q/'INDEX417_POSTROUND_FOR416_FROZEN.json'))))
