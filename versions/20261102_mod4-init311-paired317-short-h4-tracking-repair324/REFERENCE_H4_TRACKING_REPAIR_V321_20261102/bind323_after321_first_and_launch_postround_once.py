"""After actual321FIRST, validate own binding and start its sole local postround."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess,time
N=Path(__file__).resolve().parent;R=N/'reports'
def put(n,v):
    with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
assert not(R/'BIND323_POSTROUND_ONCE_CONSUMED.json').exists()
snap=json.loads((R/'ROOT321_STATUS_FIRST_UPDATED.json').read_bytes())
files={Path(row['path']).name:json.loads(row['UTF8'])for row in snap['full_selected_UTF8']}
assert not any(name in files for name in('ORIGINAL_ERROR.json','NODE_ORIGINAL_ERROR.json','OWNER_ORIGINAL_ERROR.json'))
task=json.loads((N/'TASK321_FROZEN.json').read_bytes());go=files['GO_PRODUCTION.json'];first=files['FIRST_ACTUAL_TEACHER_DEPTH_STUDENT321_UPDATE.json']
spec=importlib.util.spec_from_file_location('bound321_protocol',N/'teacher_task321.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_first(first,task,go)
assert first['student']['policy_H']==4 and first['student']['actor_terminal_bootstrap']is False
put('BIND323_POSTROUND_ONCE_CONSUMED.json',dict(epoch=time.time(),run_id=task['run_id'],model_reads=0,no_new_GO=True))
put('ROOT321_LIVE_FIRST_VALIDATED_AND_OWNER_BINDING.json',dict(epoch=time.time(),passed=True,run_id=task['run_id'],current=files['OWNER_CURRENT.json'],canonical_None=False,files=files,first=first,source_snapshot=str(R/'ROOT321_STATUS_FIRST_UPDATED.json'),model_reads=0,exact_original_owner=json.loads((R/'ROOT321_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').read_bytes())['owner']))
path=N/'postround322_finalize321_replay_eval_once.py'
with(R/'POSTROUND322_LOCAL_STDOUT.log').open('xb')as out,(R/'POSTROUND322_LOCAL_STDERR.log').open('xb')as err:
    p=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',str(path)],cwd=N,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
put('POSTROUND322_WAITER_LAUNCH.json',dict(epoch=time.time(),pid=p.pid,script=str(path),argv=['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',str(path)],scope='localtimerthenoriginal321close/fullCPU/new322eval/nativeposeframes;noGO'))
print(json.dumps(dict(passed=True,run_id=task['run_id'],postround_pid=p.pid)))
