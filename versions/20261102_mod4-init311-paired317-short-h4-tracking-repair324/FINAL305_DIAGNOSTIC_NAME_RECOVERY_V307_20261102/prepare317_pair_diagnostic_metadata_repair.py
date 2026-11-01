"""Reject316's missing metadata locally and freeze an independent317 package."""
from pathlib import Path
import ast,hashlib,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;S=T/'FINAL305_ACTUAL_PAIRED_WM_DIAGNOSTIC_V316_20261102';D=T/'FINAL305_ACTUAL_PAIRED_WM_DIAGNOSTIC_V317_20261102'
task=json.loads((S/'TASK316_FROZEN.json').read_bytes());tree=ast.parse((S/'source/evaluate316.py').read_text('utf8'))
keys=sorted({node.slice.value for node in ast.walk(tree)if isinstance(node,ast.Subscript)and isinstance(node.value,ast.Name)and node.value.id=='TASK'and isinstance(node.slice,ast.Constant)and isinstance(node.slice.value,str)})
derived={'run_id','generation','actual_resource_admission_SHA'}
missing=sorted(set(keys)-task.keys()-derived)
assert missing==['teacher_SHA','teacher_whole_CPU_receipt_SHA']and not(S/'reports/ROOT316_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
with(S/'reports/LOCAL316_STATIC_TASK_KEYS_REJECTED.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),passed=False,missing_keys=missing,model_reads=0,network=0,SDK=0,physics_steps=0,original316_source_task_preserved=True,next='independent317fromexactoriginal305metadata'),f,indent=2)
assert not D.exists();D.mkdir();(D/'reports').mkdir();shutil.copytree(S/'source',D/'source',ignore=shutil.ignore_patterns('__pycache__'));shutil.copyfile(S/'reference305.npz',D/'reference305.npz')
for path in(D/'source/evaluate316.py',D/'source/contract316.py'):
    text=path.read_text('utf8').replace('316','317');new=path.with_name(path.name.replace('316','317'));ast.parse(text);new.write_bytes(text.encode());path.unlink()
for name in('contract316.py','run316_diagnostic_once.py'):
    text=(S/name).read_text('utf8').replace('316','317');ast.parse(text);(D/name.replace('316','317')).write_bytes(text.encode())
original=json.loads((T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101/TASK305_FROZEN.json').read_bytes())
for key in missing:task[key]=original[key]
task.update(kind='FROZEN_FINAL305_ACTUAL_PAIRED_WM_DIAGNOSTIC317',worker_SHA=hashlib.sha256((D/'source/evaluate317.py').read_bytes()).hexdigest(),first_episode_only=False,actual_continuous_episode_collection=True)
assert not(set(keys)-task.keys()-derived)
(D/'TASK317_FROZEN.json').write_text(json.dumps(task,indent=2),encoding='utf8')
with(D/'reports/SOURCE317_METADATA_REPAIR_READY.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),passed=True,missing316=missing,original305_teacher_metadata_copied=True,all_literal_taskkeys_present=True,worker_SHA=task['worker_SHA'],newpurpose='frozenfinal305actualpairedpredictiondiagnostic,notduplicate308skilltest',model_reads_max=1,controls_max=64,optimizer_steps=0,network_so_far=0,normalizer_updates=0,account_writes=0,first_episode_only=False,continuous_fresh_episodes=True),f,indent=2)
print(json.dumps(dict(passed=True,root=str(D),rejected316_before_network=True)))
