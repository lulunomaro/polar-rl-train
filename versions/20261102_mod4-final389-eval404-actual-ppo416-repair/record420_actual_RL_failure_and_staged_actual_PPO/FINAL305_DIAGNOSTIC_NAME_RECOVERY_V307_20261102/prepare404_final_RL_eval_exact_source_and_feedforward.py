"""Independent404 packages exact389 inputs and dependencies without global replacements."""
from pathlib import Path
import ast
import hashlib
import json
import re
import shutil
import time

P=Path(__file__).resolve().parent;T=P.parent
N=T/'MPC_COMMAND_RESIDUAL_RL_V389_20261102'
O=T/'RL389_RECOVERED_FINAL_INDEPENDENT_EVAL_V400_20261102'
B=T/'RL389_FINAL_EVAL_DEPENDENCY_REPAIR_V403_20261102'
E=T/'RL389_EXACT_FINAL_INDEPENDENT_EVAL_V404_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
def put(path,value):
 with path.open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)

assert not E.exists()
assert not(B/'reports/ROOT403_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
assert not(O/'reports/ROOT400_SELECTED_REPLAY_TRANSFERS.json').exists()
sourcehash=H(N/'feedforward389.json')
assert sourcehash=='2c7e2c67c6e2fc764b2f3e9ffe2cdd943604fbb23c8c004464c5ef19a42c262c'
put(P/'reports/DIAG404_EVAL400_403_FEEDFORWARD_CORRUPTION_PRESERVED.json',dict(
 epoch=time.time(),passed=False,
 issue='Earlier globalversionreplacement rewrote numeric substrings in feedforward JSON; checkpoint protocol hashes would disagree',
 sourcefeedforwardSHA=sourcehash,eval400SHA=H(O/'feedforward389.json'),eval403SHA=H(B/'feedforward389.json'),
 eval400_stopped_before_PT=True,eval403_localCIMrefused_before_network=True,
 originals_preserved=True,training389_unchanged=True,
 repair='New404 source copied byteexact from frozen389; only versioned evalentry/caller tokens renamed; data always binarycopy'))
E.mkdir();(E/'reports').mkdir()
shutil.copytree(N/'source',E/'source',ignore=shutil.ignore_patterns('__pycache__'))
for name in('feedforward389.json','reference389.npz'):shutil.copyfile(N/name,E/name)
helper=T/'MPC_MATCHED_INITIAL_IMU_AIR_REQUEST_V377_20261102/source/wheel_geometry220.py'
shutil.copyfile(helper,E/'source/wheel_geometry220.py')

def rename(text):
 text=text.replace(str(O),str(E)).replace(O.as_posix(),E.as_posix())
 # Version tokens are names only. Numeric400/400Hz/400N and pinned values remain exact.
 return re.sub(r'(?<=[A-Za-z_])400(?!\d)','404',text)
for old,new in(('contract400.py','contract404.py'),('target400_parent.py','target404_parent.py'),
 ('run400_eval_once.py','run404_eval_once.py'),('view400_actual_RL_replay.py','view404_actual_RL_replay.py'),
 ('render400_recorded_frames.py','render404_recorded_frames.py'),('source/evaluate400.py','source/evaluate404.py')):
 text=rename((O/old).read_text('utf8'))
 if old.startswith('target'):text=text.replace('NN_actor_only=False','NN_actor_only=True')
 if old.startswith('view'):
  text=text.replace('policy_updates=4379','policy_updates=3508')
  text=text.replace('Planned MPC target comparison','Learned RL389 recorded motion').replace('final324','final389')
 (E/new).write_text(text,encoding='utf8')
task=json.loads((O/'TASK400_FROZEN.json').read_bytes())
task.update(kind='FROZEN389_RESIDUAL_RL_EVAL404',worker_SHA=H(E/'source/evaluate404.py'),
 distinct_evaluation_purpose='First RL389final skillmeasurement after400missinghelper/noPT and403localCIMrefusal; exact389sourceandfeedforward',
 fixed_feedforward=dict(path='feedforward389.json',bytes=(E/'feedforward389.json').stat().st_size,SHA=sourcehash))
put(E/'TASK404_FROZEN.json',task)
for source in(N/'source').rglob('*'):
 if source.is_file()and'__pycache__'not in source.parts:
  dest=E/'source'/source.relative_to(N/'source');assert H(source)==H(dest)
assert H(E/'feedforward389.json')==sourcehash
assert H(E/'reference389.npz')==task['reference']['SHA']
assert H(E/'source/wheel_geometry220.py')==H(helper)
assert task['max_controls']==400 and task['physics_dt']==.0025
assert task['GPU_UUID']=='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'
assert task['model_SHA']=='c760f8c2e3441756e1d4f6912d019c6bcdaafa456bdf6e48a9ce152395776f99'
assert task['expected_Pi_updates']==3508
for path in E.rglob('*.py'):ast.parse(path.read_text('utf8'),filename=str(path))
entry=(E/'source/evaluate404.py').read_text('utf8')
assert 'controls==400'in entry and 'physics_hz=400'in entry
assert "t['max_controls']==400"in(E/'contract404.py').read_text('utf8')
assert 'controls_max=400'in(E/'target404_parent.py').read_text('utf8')
put(E/'INDEX404_SOURCE_TASK_CALLERS_FROZEN.json',dict(epoch=time.time(),files=[
 dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in sorted(E.rglob('*'))
 if path.is_file()and'__pycache__'not in path.parts]))
put(P/'reports/STATIC404_EXACT_FROZEN389_INPUTS_DEPENDENCIES.json',dict(epoch=time.time(),passed=True,
 root=str(E),indexSHA=H(E/'INDEX404_SOURCE_TASK_CALLERS_FROZEN.json'),
 exact389_source_tree=True,feedforwardSHA=sourcehash,referenceSHA=H(E/'reference389.npz'),
 originalwheelhelperSHA=H(helper),SDK=0,network=0,model_reads=0,physics=0,
 original400_403_preserved=True,unused404=True))
print(json.dumps(dict(passed=True,root=str(E),indexSHA=H(E/'INDEX404_SOURCE_TASK_CALLERS_FROZEN.json'))))
