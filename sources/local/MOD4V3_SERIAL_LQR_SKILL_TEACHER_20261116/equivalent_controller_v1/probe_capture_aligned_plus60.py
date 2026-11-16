from pathlib import Path
import subprocess, os, json, sys, hashlib
from datetime import datetime
P=Path(__file__).resolve().parent
case=dict(name='step200_capture_aligned_plus60',kind='stair',height=.2,start_x=.06,length=.3466,speed=.47,duration=10.)
out=P/'tests'/case['name'];out.mkdir(parents=True,exist_ok=False)
files=['run_teacher.py','native_runtime.py','native_contacts.py','native_actuation.py','native_geometry.py','sim/controller.py','sim/step_climb.py','sim/lqr_governor.py','data/lqr_gain_fit.py','native_full_mjcf_gains.npz']
provenance=dict(timestamp=datetime.now().astimezone().isoformat(),files={f:hashlib.sha256((P/f).read_bytes()).hexdigest() for f in files},teacher_only=True,actor_calls=0,optimizer_steps=0)
(out/'CODE_PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf8')
with (out/'process.log').open('w',encoding='utf8') as log:
 code=subprocess.call([sys.executable,'-X','utf8','-u','-B',str(P/'run_teacher.py'),'--case',json.dumps(case),'--out',str(out)],stdout=log,stderr=subprocess.STDOUT,env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
print(case['name'],code,flush=True)
if (out/'RESULT.json').exists():
 r=json.loads((out/'RESULT.json').read_text(encoding='utf8'));print(json.dumps({k:r[k] for k in ['pass_teacher_stair','entry','max_continuous_top_hold_s','pitch_peak_deg','yaw_peak_deg','phase_transitions','error']},indent=2),flush=True)
