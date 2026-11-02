"""Validate actualRL FIRST fullsave and start only one localtimer."""
from pathlib import Path
import importlib.util,json,subprocess,time
Q=Path(__file__).resolve().parent;N=Q.parent/'MPC_COMMAND_RESIDUAL_RL_V389_20261102';R=N/'reports'
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
assert not(R/'BIND388_POSTROUND_ONCE_CONSUMED.json').exists()
snap=json.loads((R/'ROOT389_STATUS_FIRST_UPDATED.json').read_bytes());files={Path(x['path']).name:json.loads(x['UTF8'])for x in snap['full_selected_UTF8']}
assert not any(n in files for n in('ORIGINAL_ERROR.json','NODE_ORIGINAL_ERROR.json','OWNER_ORIGINAL_ERROR.json'))
task=json.loads((N/'TASK389_FROZEN.json').read_bytes());go=files['GO_PRODUCTION.json'];first=files['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT389_UPDATE.json']
spec=importlib.util.spec_from_file_location('RL389bind',N/'teacher_task389.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_first(first,task,go)
assert first['student']['residual_RL']and not first['student']['online_MPC']
put('BIND388_POSTROUND_ONCE_CONSUMED.json',dict(epoch=time.time(),run_id=task['run_id'],model_reads=0))
put('ROOT389_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json',dict(epoch=time.time(),passed=True,run_id=task['run_id'],current=files['OWNER_CURRENT.json'],canonical_None=False,files=files,first=first,source_snapshot=str(R/'ROOT389_STATUS_FIRST_UPDATED.json'),model_reads=0,exact_original_owner=json.loads((R/'ROOT389_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').read_bytes())['owner']))
path=Q/'postround396_close_RL389_eval_once.py'
with(R/'POSTROUND396_LOCAL_STDOUT.log').open('xb')as out,(R/'POSTROUND396_LOCAL_STDERR.log').open('xb')as err:
 p=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',str(path)],cwd=N,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
put('POSTROUND396_WAITER_LAUNCH.json',dict(epoch=time.time(),pid=p.pid,script=str(path),scope='solelocaltimer_thenRL389closefullCPU_actor396evaluationandactualposeframes'))
print(json.dumps(dict(passed=True,run_id=task['run_id'],postround_pid=p.pid)))
