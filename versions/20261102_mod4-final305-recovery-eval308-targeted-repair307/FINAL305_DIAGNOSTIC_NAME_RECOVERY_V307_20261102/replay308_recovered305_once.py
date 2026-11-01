"""Replay already captured308 actualposes and render finite native reviewframes."""
from pathlib import Path
import ast,json,re,subprocess,time
N=Path(__file__).resolve().parent;T=N.parent;E=T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102';O=T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101'
full=json.loads((N/'reports/ROOT307_NEW_FINAL305_WHOLE_CPU_RETURNED_ACTUAL.json').read_bytes());result=json.loads((E/'reports/ROOT308_EVALUATION_FULL_RETURNED.json').read_bytes())['result'];assert result['passed']
s=(O/'postround306/view306_actual_final305_replay_template.py').read_text('utf8');s=re.sub(r'(?<=[A-Za-z_])306(?!\d)','308',s)
s=s.replace('policy_updates=2336','policy_updates='+str(full['Pi'])).replace('Pi2336 Critic2336','Pi'+str(full['Pi'])+' Critic'+str(full['critic']))
s=s.replace('FAILED: bad_orientation; held-out stairs0/72; ground completed0/8',f"REFERENCE TRACKER: stable{result['strict_successes']}/80 / bothcross{result['crossed_cases']}/80; planned goals")
p=E/'view308_actual_final305_replay.py';p.write_bytes(s.encode());ast.parse(s)
with(E/'reports/VIEW308_CONSOLE.log').open('xb')as f:proc=subprocess.Popen(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/pythonw.exe','-B','-X','utf8',str(p)],cwd=E,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
with(E/'reports/VIEW308_LAUNCH.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),pid=proc.pid,actualrecordedposes=True,modelreads=0,physicssteps=0),f,indent=2)
s=(T/'TRACKING300_FAILURE_DIAGNOSIS_V304_20261101/render304_recorded303_frames.py').read_text('utf8')
s=s.replace('REFERENCE_TRACKING300_POSTROUND_EVAL_V303_20261101','RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102').replace('view303_actual_final300_replay.py','view308_actual_final305_replay.py')
s=s.replace('VISIBLE_REPLAY303','VISIBLE_REPLAY308').replace('VIEW303','VIEW308').replace('FINAL300','FINAL305').replace('ACTUAL303','ACTUAL308').replace('RECORDED303','RECORDED308').replace('recorded303','recorded308').replace('final300','final305')
p=E/'render308_recorded_frames.py';p.write_bytes(s.encode());ast.parse(s)
run=subprocess.run(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',str(p)],cwd=E,capture_output=True,text=True,encoding='utf8')
with(E/'reports/NATIVE308_RENDER_RETURNED.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),returncode=run.returncode,stdout=run.stdout,stderr=run.stderr),f,indent=2)
assert run.returncode==0
print(json.dumps(dict(passed=True,eval_strict=result['strict_successes'],crossed=result['crossed_cases'],terminations=result['terminations'],image=str(E/'RECORDED308_NATIVE_FRAMES/ACTUAL308_FINAL305_BODY_POSE_SEQUENCE.png'))))
