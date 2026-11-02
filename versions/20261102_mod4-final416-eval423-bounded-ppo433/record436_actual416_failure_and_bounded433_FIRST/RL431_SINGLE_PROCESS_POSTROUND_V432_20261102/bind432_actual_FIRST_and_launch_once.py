"""BindactualFIRST431 and launch sole432timer; no network/modelreads."""
from pathlib import Path
import importlib.util,json,subprocess,time
Q=Path(__file__).resolve().parent;N=Q.parent/'RL_BOUNDED_ACTUAL_PPO_PRODUCTION_V431_20261102';R=N/'reports'
def put(name,value):
 with(R/name).open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
assert not(R/'BIND432_POSTROUND_ONCE_CONSUMED.json').exists()
snap=json.loads((R/'ROOT431_STATUS_FIRST_UPDATED.json').read_bytes());files={Path(row['path']).name:json.loads(row['UTF8'])for row in snap['full_selected_UTF8']}
assert not any(name in files for name in('ORIGINAL_ERROR.json','NODE_ORIGINAL_ERROR.json','OWNER_ORIGINAL_ERROR.json'))
task=json.loads((N/'TASK431_FROZEN.json').read_bytes());spec=importlib.util.spec_from_file_location('bind431',N/'teacher_task431.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.validate_first(files['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT431_UPDATE.json'],task,files['GO_PRODUCTION.json'])
put('BIND432_POSTROUND_ONCE_CONSUMED.json',dict(epoch=time.time(),run_id=task['run_id'],modelreads=0))
put('ROOT431_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json',dict(epoch=time.time(),passed=True,run_id=task['run_id'],current=files['OWNER_CURRENT.json'],canonical_None=False,files=files,exact_original_owner=json.loads((R/'ROOT431_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').read_bytes())['owner']))
path=Q/'postround432_close_actual431_eval_once.py'
with(R/'POSTROUND432_STDOUT.log').open('xb')as out,(R/'POSTROUND432_STDERR.log').open('xb')as err:
 process=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',str(path)],cwd=N,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
put('POSTROUND432_WAITER_LAUNCH.json',dict(epoch=time.time(),PID=process.pid,script=str(path),sameprocessserialdispatcher=True))
print(json.dumps(dict(passed=True,PID=process.pid)))
