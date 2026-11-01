from pathlib import Path
import ast,hashlib,json,subprocess,time
N=Path(__file__).resolve().parent;T=N.parent;O=T/'DEPTH_STUDENT_RETENTION_REPAIR_V292_20261101';E=T/'RETENTION292_DEPENDENCY_REPLAY_EVAL_V299_20261101'
result=json.loads((E/'reports/ROOT299_EVALUATION_FULL_RETURNED.json').read_bytes())['result'];full=json.loads((O/'reports/ROOT292_NEW_FINAL_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes())
assert result['passed']and result['strict_successes']==0 and full['passed']
text=(O/'postround292/view293_actual_final292_replay_template.py').read_text('utf8').replace('293','299')
text=text.replace('policy_updates=2336','policy_updates=211').replace('Pi2336 Critic2336','Pi211 Critic211').replace('FAILED: bad_orientation; held-out stairs0/72; ground completed0/8','292 repair result: stairs0/72; ground completed6/8; mixed objective retired')
viewer=E/'view299_actual_final292_replay.py';viewer.write_bytes(text.encode());ast.parse(text)
with(E/'reports/VIEW299_CONSOLE.log').open('xb')as f:p=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/pythonw.exe','-B','-X','utf8',str(viewer)],cwd=E,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
with(E/'reports/VIEW299_LAUNCH.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),pid=p.pid,actual_recorded_replay=True,modelreads=0,physicalsteps=0),f,indent=2)
with(O/'reports/POSTROUND292_REPLAY_EVAL_DECISION.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),status='COMPLETE_SAVE_REPLAY_EVAL_DECISION',model_SHA=full['SHA'],eval_root=str(E),strict_successes=0,crossed_cases=0,ground_complete=6,terminations=result['terminations'],decision='Ground retention improved to6/8 but no270cross. Old mixed objective retired. Human explicitly authorized new reference tracking; launch independent297afterfreshCNone/privateEX.',original293_failure_preserved=True,new299_only_evaluation_repair=True),f,indent=2)
script=N/'launch297_reference_tracking_once.py';old=script.read_bytes()
with(N/'launch297_reference_tracking_v1_UNEXECUTED.py').open('xb')as f:f.write(old)
text=old.decode().replace("pattern='run293_eval|", "pattern='run299_eval|run293_eval|")
text=text.replace("    cpu=read(T/", "    phasecheck=read(R/'CPU297_POSITIVE_RETURN_PHASE_SOURCE_TEST.json');assert phasecheck['passed']\n    cpu=read(T/",1)
script.write_bytes(text.encode());ast.parse(text)
oldindex=N/'INDEX297_SOURCE_TASK_CALLERS_FROZEN.json'
files=[p for p in sorted(N.rglob('*'))if p.is_file()and'__pycache__'not in p.parts and p.suffix in('.py','.json','.npz')and p!=oldindex]
index=N/'INDEX297V2_SOURCE_TASK_CALLERS_FROZEN.json'
# Keep previous index bytes untouched. Update launch to select new independent index.
text=script.read_text('utf8').replace("index=N/'INDEX297_SOURCE_TASK_CALLERS_FROZEN.json'", "index=N/'INDEX297V2_SOURCE_TASK_CALLERS_FROZEN.json'")
script.write_bytes(text.encode());ast.parse(text)
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with index.open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),kind='TRACKING297V2_ACTUAL299_CLOSED_CALLER_BINDING',files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))for p in files]),f,indent=2)
print(json.dumps(dict(passed=True,index_SHA=H(index),replayPID=p.pid if False else 'seeVIEW299_LAUNCH',old292ground=6)))
