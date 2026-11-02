"""Independent403 adds omitted wheel geometry helper; original400 is immutable."""
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import time

P=Path(__file__).resolve().parent;T=P.parent
O=T/'RL389_RECOVERED_FINAL_INDEPENDENT_EVAL_V400_20261102'
E=T/'RL389_FINAL_EVAL_DEPENDENCY_REPAIR_V403_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
 with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)

assert not E.exists()
returned=json.loads((O/'reports/ROOT400_EVALUATION_FULL_RETURNED.json').read_bytes())
texts={Path(row['path']).name:json.loads(row['UTF8'])for row in returned['full_UTF8']if row['path'].endswith('.json')}
assert 'ModuleNotFoundError' in texts['ORIGINAL400_ERROR.json']['error']
assert "wheel_geometry220" in texts['ORIGINAL400_ERROR.json']['error']
assert texts['ACTUAL400_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json']['all_own_children_waited']
assert texts['ACTUAL400_ALL_WAITED_PRIVATE_SHARED_EX_RELEASED.json']['private_shared_EX_released']
assert texts['ENV400_CLOSE_RETURNED.json']['closed']
assert not any('ACTUAL400_RL_ACTOR_ONE_READ' in row['path']for row in returned['full_UTF8'])
put(P/'reports/DIAG403_ACTUAL400_MISSING_HELPER_FAILURE_PRESERVED.json',dict(epoch=time.time(),
    passed=False,original400_consumed=True,worker_waited_rc=0,SDK_started=True,
    model_reads=0,controls=0,physics_controls=0,result=None,
    actual_error=texts['ORIGINAL400_ERROR.json'],
    original400_files_unchanged=True,all_own_children_waited=True,private_shared_released=True,
    repair='New403 packages exact historical wheel_geometry220 helper; no model or protocol changes'))
def rename(text):
 protected={}
 def hold(match):
  key=f'PINNEDVALUE{len(protected)}PLACEHOLDER';protected[key]=match.group(0);return key
 text=re.sub(r'GPU-[0-9a-f-]{36}|\b[0-9a-f]{64}\b',hold,text)
 text=text.replace(str(O),str(E)).replace(O.as_posix(),E.as_posix()).replace('400','403')
 for key,value in protected.items():text=text.replace(key,value)
 return text
E.mkdir();(E/'reports').mkdir()
for path in sorted(O.rglob('*')):
 if not path.is_file()or '__pycache__'in path.parts:continue
 relative=path.relative_to(O)
 if relative.parts[0]in('reports','replay')or path.name.startswith('INDEX')or path.name.startswith('TASK400_PENDING')or path.name.startswith('bind400_'):continue
 dest=E/rename(str(relative));dest.parent.mkdir(parents=True,exist_ok=True)
 if path.suffix in('.py','.json'):dest.write_text(rename(path.read_text('utf8')),encoding='utf8')
 else:shutil.copyfile(path,dest)
helper=T/'MPC_MATCHED_INITIAL_IMU_AIR_REQUEST_V377_20261102/source/wheel_geometry220.py'
shutil.copyfile(helper,E/'source/wheel_geometry220.py')
taskpath=E/'TASK403_FROZEN.json';task=json.loads(taskpath.read_bytes())
# Preserve physical400Hz in metadata: version rename above changes all literal400 tokens.
task.update(physics_dt=.0025,policy_hz=50,feedback_hz=100,max_controls=400,
    kind='FROZEN389_RESIDUAL_RL_EVAL403',
    distinct_evaluation_purpose='First final389RL physicalevaluation after400missingwheelhelper failed before checkpointread or firstcontrol',
    worker_SHA=H(E/'source/evaluate403.py'))
taskpath.write_text(json.dumps(task,indent=2),encoding='utf8')
# Preserve original unversioned numerical constants and400Hz/window strings in all copied code.
for source in sorted(O.rglob('*.py')):
 relative=source.relative_to(O)
 if relative.parts[0]=='reports'or source.name.startswith('bind400_'):continue
 dest=E/rename(str(relative))
 text=dest.read_text('utf8')
 text=re.sub(r'(?<![A-Za-z_0-9])403(?![A-Za-z_0-9])','400',text)
 text=text.replace('PhysX403','PhysX400').replace('403Hz','400Hz')
 if dest.name=='target403_parent.py':text=text.replace('NN_actor_only=False','NN_actor_only=True')
 if dest.name=='view403_actual_RL_replay.py':
  text=text.replace('policy_updates=4379','policy_updates='+str(task['expected_Pi_updates']))
  text=text.replace('Planned MPC target comparison','Learned RL389 recorded motion').replace('final324','final389')
 dest.write_text(text,encoding='utf8')
task['worker_SHA']=H(E/'source/evaluate403.py')
taskpath.write_text(json.dumps(task,indent=2),encoding='utf8')
assert task['max_controls']==400 and task['model_SHA']=='c760f8c2e3441756e1d4f6912d019c6bcdaafa456bdf6e48a9ce152395776f99'
assert task['GPU_UUID']=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
assert H(helper)==H(E/'source/wheel_geometry220.py')
for path in E.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
assert "range(1,TASK['max_controls']+1)" in(E/'source/evaluate403.py').read_text('utf8')
assert 'controls==400'in(E/'source/evaluate403.py').read_text('utf8')
assert "t['max_controls']==400"in(E/'contract403.py').read_text('utf8')
assert 'controls_max=400' in(E/'target403_parent.py').read_text('utf8')
put(E/'INDEX403_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=[
 dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(E.rglob('*'))
 if path.is_file()and'__pycache__'not in path.parts]))
put(P/'reports/STATIC403_EVAL_DEPENDENCY_REPAIR.json',dict(epoch=time.time(),passed=True,
 root=str(E),indexSHA=H(E/'INDEX403_SOURCE_TASK_CALLERS_FROZEN.json'),
 exact_original_helper=dict(path=str(helper),SHA=H(helper)),
 original400_consumed_preserved=True,SDK=0,model_reads=0,physics=0,
 sourcefinalSHA=task['model_SHA'],same80firstepisodes400controls=True))
print(json.dumps(dict(passed=True,root=str(E),indexSHA=H(E/'INDEX403_SOURCE_TASK_CALLERS_FROZEN.json'))))
