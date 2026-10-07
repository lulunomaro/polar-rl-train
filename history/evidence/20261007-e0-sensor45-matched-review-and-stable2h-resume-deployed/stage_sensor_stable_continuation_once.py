"""Stage one isolated continuation; no GPU/PPO/production or budget authority."""
from pathlib import Path
import sys,json,hashlib,shlex,ast
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
ROOT='/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007'
names={'sensor_resume_contract.py':'isaac/mod4/sensor_resume_contract.py','test_sensor_resume_actual_cpu.py':'isaac/mod4/test_sensor_resume_actual_cpu.py','train_sensor_resume_ppo.py':'isaac/mod4/train_sensor_resume_ppo.py','supervise_sensor_stable_continuation.py':'supervise_sensor_stable_continuation.py'}
for n in names:ast.parse((D/'continuation_source'/n).read_text())
c=connect()
try:
 code='''
from pathlib import Path
import json,shutil,hashlib,time
S=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DEPENDENCY_REVIEW_20261007');D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007')
assert not D.exists();D.mkdir();(D/'reports').mkdir()
f=json.loads((S/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(f)==202
for n,h in f.items():
 p=S/n;assert hashlib.sha256(p.read_bytes()).hexdigest()==h,n
 out=D/n;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
shutil.copy2(S/'reports/SENSOR_CPU_CONTRACT.json',D/'reports/SENSOR_CPU_CONTRACT.json')
print(json.dumps(dict(old202_byte_exact=True,newroot=str(D))))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=30);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();print(raw.decode())
 with c.open_sftp() as s:
  for n,target in names.items():s.put(str(D/'continuation_source'/n),ROOT+'/'+target)
  s.put(str(R/'SENSOR_MODEL24061_FIRST_MATCHED_REVIEW.json'),ROOT+'/reports/SENSOR_MODEL24061_FIRST_MATCHED_REVIEW.json')
 code='''
from pathlib import Path
import json,hashlib,subprocess,time,ast
D=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_STABLE_CONTINUATION_20261007');S=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DEPENDENCY_REVIEW_20261007');f=json.loads((S/'reports/SOURCE_FREEZE.json').read_text())['sha256']
new=('isaac/mod4/sensor_resume_contract.py','isaac/mod4/test_sensor_resume_actual_cpu.py','isaac/mod4/train_sensor_resume_ppo.py','supervise_sensor_stable_continuation.py')
for n in new:ast.parse((D/n).read_text());f[n]=hashlib.sha256((D/n).read_bytes()).hexdigest()
assert len(f)==206
(D/'reports/SOURCE_FREEZE.json').write_text(json.dumps(dict(sha256=f,original202_byte_exact=True,only_four_new_continuation_files=True),indent=2))
source=json.loads((D/'reports/SENSOR_MODEL24061_FIRST_MATCHED_REVIEW.json').read_text())['formal']['checkpoint']
assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256']
proc=subprocess.run(['/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python',str(D/'isaac/mod4/test_sensor_resume_actual_cpu.py'),source['path']],capture_output=True,text=True,cwd=D/'isaac/mod4',timeout=60)
assert proc.returncode==0,proc.stdout+proc.stderr
v=json.loads(proc.stdout);assert v['passed'] and v['no_CUDA_initialized']
(D/'reports/SENSOR_RESUME_CPU_CONTRACT.json').write_text(json.dumps(v,indent=2))
print(json.dumps(dict(source_count=len(f),CPU=v)))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=80);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'SENSOR_STABLE_STAGING_CPU_PASSED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
finally:c.close()
