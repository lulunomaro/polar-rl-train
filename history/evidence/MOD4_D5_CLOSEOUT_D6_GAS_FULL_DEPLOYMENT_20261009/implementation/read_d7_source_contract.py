"""Read immutable D7 nominal/SDK source only; no setters, scene, CUDA or training."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
    code=r'''
from pathlib import Path
import json,hashlib,time
D=Path('/home/egde/rl_candidates/MOD4_D6_FULL_CONTRACT_20261009');f=json.loads((D/'reports/SOURCE_FREEZE.json').read_text())['sha256'];matches={}
for n,h in f.items():
 if Path(n).name in ('mild_dr.py','nominal_parameter_audit.py','mod4_task.py','sensor_resume_contract.py'):
  raw=(D/n).read_bytes();assert hashlib.sha256(raw).hexdigest()==h;t=raw.decode();lines=t.splitlines()
  selected=[]
  for i,line in enumerate(lines):
   if any(p in line.lower() for p in ('com','derivative','write_joint_damping','kp','kd','motor_pd','nominal')):
    selected.append(dict(line=i+1,text='\n'.join(lines[max(0,i-2):min(len(lines),i+3)])))
  matches[n]=dict(sha256=h,selected=selected)
sdk=Path('/home/egde/fangzhen_linux/third_party/IsaacLab-3.0.0-beta2.patch1/source/isaaclab/isaaclab/assets/articulation/articulation.py')
if sdk.exists():
 t=sdk.read_text();lines=t.splitlines();snippets=[]
 for i,line in enumerate(lines):
  if 'def write_com' in line or 'def write_joint_stiffness' in line or 'def write_joint_damping' in line:snippets.append(dict(line=i+1,text='\n'.join(lines[i:i+48])))
 matches['installed_articulation.py']=dict(path=str(sdk),sha256=hashlib.sha256(sdk.read_bytes()).hexdigest(),selected=snippets)
print(json.dumps(dict(epoch=time.time(),actual_frozen_source=True,matches=matches,no_GPU_or_mutation=True)))
'''
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=45);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
    (R/'D7_FROZEN_SOURCE_READ_ONLY.json').write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(files=list(v['matches']),no_GPU_or_mutation=True)))
finally:c.close()
