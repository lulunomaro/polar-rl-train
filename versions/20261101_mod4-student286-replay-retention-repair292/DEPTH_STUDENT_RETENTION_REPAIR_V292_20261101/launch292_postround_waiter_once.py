from pathlib import Path
import ast,hashlib,json,subprocess,time
N=Path(__file__).resolve().parent;R=N/'reports';script=N/'postround292_finish_replay_eval_once.py'
for p in (script,*list((N/'postround292').rglob('*.py'))):ast.parse(p.read_text('utf8'))
assert not (R/'POSTROUND292_WAITER_LAUNCH.json').exists()
args=['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',str(script)]
with (R/'POSTROUND292_WAITER_CONSOLE.log').open('xb')as f:child=subprocess.Popen(args,cwd=N,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
with (R/'POSTROUND292_WAITER_LAUNCH.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),pid=child.pid,args=args,source_SHA=hashlib.sha256(script.read_bytes()).hexdigest(),local_wait_then_original_close_and_new_eval=True),f,indent=2)
print(json.dumps(dict(passed_launch=True,pid=child.pid)))
