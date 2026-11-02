"""BindactualFIRST429 and launch sole430timer; no network/modelreads."""
from pathlib import Path
import importlib.util,json,subprocess,time
Q=Path(__file__).resolve().parent;N=Q.parent/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V429_20261102';R=N/'reports'
def put(name,value):
 with(R/name).open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
assert not(R/'BIND430_POSTROUND_ONCE_CONSUMED.json').exists()
snap=json.loads((R/'ROOT429_STATUS_FIRST_UPDATED.json').read_bytes());files={Path(row['path']).name:json.loads(row['UTF8'])for row in snap['full_selected_UTF8']}
assert not any(name in files for name in('ORIGINAL_ERROR.json','NODE_ORIGINAL_ERROR.json','OWNER_ORIGINAL_ERROR.json'))
task=json.loads((N/'TASK429_FROZEN.json').read_bytes());spec=importlib.util.spec_from_file_location('bind429',N/'teacher_task429.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.validate_first(files['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT429_UPDATE.json'],task,files['GO_PRODUCTION.json'])
put('BIND430_POSTROUND_ONCE_CONSUMED.json',dict(epoch=time.time(),run_id=task['run_id'],modelreads=0))
put('ROOT429_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json',dict(epoch=time.time(),passed=True,run_id=task['run_id'],current=files['OWNER_CURRENT.json'],canonical_None=False,files=files,exact_original_owner=json.loads((R/'ROOT429_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').read_bytes())['owner']))
path=Q/'postround430_close_actual429_eval_once.py'
with(R/'POSTROUND430_STDOUT.log').open('xb')as out,(R/'POSTROUND430_STDERR.log').open('xb')as err:
 process=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',str(path)],cwd=N,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
put('POSTROUND430_WAITER_LAUNCH.json',dict(epoch=time.time(),PID=process.pid,script=str(path),sameprocessserialdispatcher=True))
print(json.dumps(dict(passed=True,PID=process.pid)))
