"""Render and review newly recorded311 physics; no checkpoint or physics replay."""
from pathlib import Path
import ast,json,subprocess,time
N=Path(__file__).resolve().parent;T=N.parent;E=T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102';O=T/'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102'
R=E/'reports'
assert not(R/'REPLAY311_RENDER_ONCE_CONSUMED.json').exists()
result=json.loads((R/'ROOT311_EVALUATION_FULL_RETURNED.json').read_bytes())['result'];assert result['passed']
with(R/'REPLAY311_RENDER_ONCE_CONSUMED.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),purpose='Display new actual311default/referenceinitialization physicalprobe',model_reads=0,physics_steps=0),f,indent=2)
source=(O/'view308_actual_final305_replay.py').read_text('utf8').replace('308','311')
source=source.replace('Final305','Plannedreference physicalprobe').replace('final305','referenceqtargetprobe').replace('FINAL305','REFERENCE q/dq TARGETS').replace('Pi2724 Critic2724','NO POLICY / NO OPTIMIZER').replace('policy_updates=2724','policy_updates=0')
source=source.replace("r['result']['kind']=='reference270'","r['result']['kind']in('defaultzero_init','reference_init')")
source=source.replace('1 env1 | 2 env0 | 3 env10 | 4 env20','1 default env0 | 2 default env1 | 3 ref env40 | 4 ref env41')
source=source.replace('Closure10mm /mimic.01rad / reference tracking BPTT / matching tracking critic','Closure10mm /mimic.01rad / direct planned q/dq targets / no inference')
path=E/'view311_actual_probe_replay.py';ast.parse(source);path.write_bytes(source.encode())
renderer=(O/'render308_recorded_frames.py').read_text('utf8').replace(O.name,E.name).replace('view308_actual_final305_replay.py',path.name).replace('308','311').replace('final305','referenceqtargetprobe').replace('FINAL305','REFERENCE_TARGET')
renderer=renderer.replace('ACTUAL311 referenceqtargetprobe env', 'ACTUAL311 planned q/dq env')
path2=E/'render311_recorded_frames.py';ast.parse(renderer);path2.write_bytes(renderer.encode())
# Finite native rendering is sufficient for visual review; it reads recorded
# trajectories only and never creates a training or physics controller.
run=subprocess.run(['C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe','-B','-X','utf8',str(path2)],cwd=E,capture_output=True,text=True,encoding='utf8')
with(R/'NATIVE311_RENDER_RETURNED.json').open('x',encoding='utf8')as f:json.dump(dict(epoch=time.time(),returncode=run.returncode,stdout=run.stdout,stderr=run.stderr),f,indent=2)
assert run.returncode==0
print(json.dumps(dict(passed=True,comparison=result['comparison'],image=str(E/'RECORDED311_NATIVE_FRAMES/ACTUAL311_REFERENCE_TARGET_BODY_POSE_SEQUENCE.png'))))
