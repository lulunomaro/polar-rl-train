"""Read frozen joint/actuator law and installed parameter APIs without starting GPU."""
from pathlib import Path
import sys,json,time,hashlib,base64,shlex,ast
D=Path(__file__).resolve().parent;R=D/'reports';R.mkdir(exist_ok=True)
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
sys.path.insert(0,str(D.parent/'MOD4_MOE_PLAN_EXECUTION_20261007'));from eval_remote_io import connect_eval
n=connect();w=connect_eval()
try:
 code=r'''
from pathlib import Path
import json,hashlib,zipfile,base64,time
D=Path('/home/egde/rl_candidates/MOD4_D5_FULL_CONTRACT_20261008');E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(E/'reports/PLAN_APPROVAL.json');assert a['approved'] and 'S2' in a['allowed_stages']
f=read(D/'reports/SOURCE_FREEZE.json')['sha256'];files={}
for name in ('isaac/mod4/mod4_task.py','isaac/mod4/mild_dr.py','isaac/mod4/spring_pressure_component.py','isaac/mod4/spring_pressure_training_env.py'):
 assert sha(D/name)==f[name];files[name]=dict(sha256=f[name],raw_b64=base64.b64encode((D/name).read_bytes()).decode())
pack=read(D/'reports/D5_FROZEN_BEHAVIOR_PACKAGES.json')['flat'];assert sha(Path(pack['path']))==pack['sha256']
with zipfile.ZipFile(pack['path']) as z:
 contractnames=[p for p in z.namelist() if p.endswith('import_contract.json')];assert len(contractnames)==1;raw=z.read(contractnames[0]);contract=json.loads(raw)
print(json.dumps(dict(epoch=time.time(),files=files,contract=contract,import_contract_SHA=hashlib.sha256(raw).hexdigest(),package=pack,approval=a,work_order=read(E/'reports/NEXT_D6_DAMPING_FRICTION_WORK_ORDER.json'),no_GPU_or_budget_write=True)))
'''
 _,o,e=n.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace');v=json.loads(raw)
 src=D/'reviewed_sources';src.mkdir(exist_ok=True)
 for name,row in v.pop('files').items():
  path=src/Path(name).name;path.write_bytes(base64.b64decode(row['raw_b64']));assert hashlib.sha256(path.read_bytes()).hexdigest()==row['sha256']
 sdk=[];root='D:/claude2/fangzhen/third_party/IsaacLab-3.0.0-beta2.patch1/source/'
 with w.open_sftp() as s:
  for name in ('isaaclab_physx/isaaclab_physx/assets/articulation/articulation.py','isaaclab_physx/isaaclab_physx/assets/articulation/articulation_data.py','isaaclab_physx/isaaclab_physx/assets/articulation/articulation_kernels.py','isaaclab/isaaclab/actuators/actuator_pd.py'):
   try:raw=s.open(root+name).read()
   except FileNotFoundError:
    sdk.append(dict(path=root+name,not_found=True));continue
   path=src/('installed_'+Path(name).name);path.write_bytes(raw);sdk.append(dict(path=root+name,sha256=hashlib.sha256(raw).hexdigest(),local_name=path.name))
 v['installedSDK']=sdk
 (R/'D6_ACTUAL_SOURCE_REVIEW.json').write_text(json.dumps(v,indent=2),encoding='utf8')
 joints=v['contract']['joints'];summary=dict(epoch=v['epoch'],joint_damping_SI={k:r['damping_si'] for k,r in joints.items()},gas_springs=v['contract']['gas_springs'],
  import_contract_SHA=v['import_contract_SHA'],SDK_sources=sdk,no_GPU_PPO_or_budget_write=True)
 (R/'D6_NOMINAL_SOURCE_SUMMARY.json').write_text(json.dumps(summary,indent=2),encoding='utf8');print(json.dumps(summary))
finally:w.close();n.close()
